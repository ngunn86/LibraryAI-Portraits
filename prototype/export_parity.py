"""Reference outputs for the TypeScript porting spike (F-39) and the imaging cards (F-12..F-14, F-30, F-42).

Each OpenCV, NumPy or SciPy operation the recipe uses is run here on small, fixed inputs, and its result is
saved, so the TypeScript port can be compared operation by operation, offline. Writes prototype/parity/:

  inputs/<tid>.rgb.png      the original exactly as Pillow decoded it (8-bit RGB). The port reads this, not the
                            JPEG or WebP, so a different decoder can't cause a mismatch
  <case>/<op>.f32           an array as raw little-endian float32, row-major, channels last
  <case>/<op>.json          its sidecar: shape, the exact call and parameters, and the tolerance to test with
  results.json              results that aren't images: screen peaks, YuNet faces, ECC, SIFT, components, ...
  index.json                every file, with what it checks and which card uses it

Cases are 96 x 96 grey crops (values 0..1) of two originals: Fillmore (printed dot screen) and Holmes (clean).
Run from the repo root:  python3 prototype/export_parity.py
Needs NumPy, SciPy, OpenCV (4.10+ or 5.x, with SIFT and FaceDetectorYN) and Pillow.
"""
import sys, json, platform
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from common import *
from recipe import (SETTINGS, RECIPE_VERSION, detect_screen, descreen, _threshold_map, landmarks_from_box,
                    crop_transform, key_mask)
from scipy import __version__ as scipy_version
from scipy.ndimage import median_filter, maximum_filter

OUT = ROOT / "prototype/parity"
CROP = 96
index = {"recipe_version": RECIPE_VERSION, "made_with": dict(python=platform.python_version(), numpy=np.__version__,
         scipy=scipy_version, opencv=cv2.__version__), "format": "raw little-endian float32, row-major, channels last",
         "files": []}
results = {}


def save(case, op, arr, call, tolerance, card, note=None):
    a = np.ascontiguousarray(np.asarray(arr, dtype="<f4"))
    d = OUT / case
    d.mkdir(parents=True, exist_ok=True)
    a.tofile(d / f"{op}.f32")
    side = dict(op=op, shape=list(a.shape), call=call, tolerance=tolerance, card=card,
                stats=dict(min=float(a.min()), max=float(a.max()), mean=float(a.mean())))
    if note:
        side["note"] = note
    json.dump(side, open(d / f"{op}.json", "w"), indent=1)
    index["files"].append(dict(file=f"{case}/{op}.f32", card=card, call=call))


def face_crop(L, face, n=CROP):
    """An n x n crop centred on the face box (inside the image)."""
    x0, y0, x1, y1 = face["box"]
    cx, cy = int(round((x0 + x1) / 2)), int(round((y0 + y1) / 2))
    h, w = L.shape
    sx, sy = min(max(cx - n // 2, 0), w - n), min(max(cy - n // 2, 0), h - n)
    return np.ascontiguousarray(L[sy:sy + n, sx:sx + n]), [sx, sy, n, n]


def log_spectrum(L):
    """detect_screen's spectrum: high-pass, Hann window, centred FFT magnitude, log1p."""
    h, w = L.shape
    hp = L - cv2.GaussianBlur(L, (0, 0), 3)
    win = np.outer(np.hanning(h), np.hanning(w)).astype(np.float32)
    return np.log1p(np.abs(np.fft.fftshift(np.fft.fft2(hp * win)))).astype(np.float32)


def median15_8bit(M):
    """The port's fallback for the 15 x 15 median on floats: scale to 8 bits, cv2.medianBlur, scale back.
    Padded by reflection first, so the border matches scipy's mode='reflect' (medianBlur replicates)."""
    lo, hi = float(M.min()), float(M.max())
    u8 = np.round((M - lo) / max(hi - lo, 1e-12) * 255).astype(np.uint8)
    p = cv2.copyMakeBorder(u8, 7, 7, 7, 7, cv2.BORDER_REFLECT)
    med = cv2.medianBlur(p, 15)[7:-7, 7:-7]
    return med.astype(np.float32) / 255 * (hi - lo) + lo


def median15_quantised(bits):
    """A 15 x 15 median of values quantised to `bits` (what a sliding-histogram median in TypeScript computes)."""
    def f(M):
        lo, hi = float(M.min()), float(M.max())
        q = 2 ** bits - 1
        u = np.round((M - lo) / max(hi - lo, 1e-12) * q)
        return (median_filter(u, size=15) / q * (hi - lo) + lo).astype(np.float32)
    return f


def detect_screen_with(L, median, s=SETTINGS):
    """detect_screen with a swappable median, to show which medians find the same peaks."""
    h, w = L.shape
    M = log_spectrum(L)
    D = M - median(M)
    fy = (np.arange(h) - h // 2)[:, None] / h
    fx = (np.arange(w) - w // 2)[None, :] / w
    fr = np.hypot(fy, fx)
    cand = (D > s["screen_peak_log"]) & (fr > s["screen_min_cyc_px"]) & (D == maximum_filter(D, size=5)) & (fy >= 0)
    ys, xs = np.nonzero(cand)
    order = np.argsort(-D[ys, xs])
    peaks = []
    for i in order[:12]:
        f = (float(fy[ys[i], 0]), float(fx[0, xs[i]]))
        if all(np.hypot(f[0] - p[0], f[1] - p[1]) > 0.02 for p in peaks):
            peaks.append(f)
    dirs = []
    for f in peaks:
        a = np.degrees(np.arctan2(f[0], f[1])) % 180
        if all(min(abs(a - d), 180 - abs(a - d)) > 20 for d in dirs):
            dirs.append(a)
    return peaks if len(dirs) >= s["screen_min_peaks"] else []


def yunet_raw(rgb):
    """YuNet's own output rows: x, y, w, h, 10 landmark coordinates, score (OpenCV's format)."""
    img = (np.clip(rgb, 0, 1) * 255).astype(np.uint8)
    det = cv2.FaceDetectorYN.create(str(FACE_MODEL), "", (img.shape[1], img.shape[0]), 0.6, 0.3, 5000)
    _, faces = det.detect(img[..., ::-1].copy())
    return [] if faces is None else faces.astype(np.float64).tolist()


def main():
    (OUT / "inputs").mkdir(parents=True, exist_ok=True)
    rgbs, faces = {}, {}
    for tid in EXAMPLES:
        rgb = load_rgb(original_path(tid))
        rgbs[tid] = rgb
        Image.fromarray((rgb * 255).round().astype(np.uint8), "RGB").save(OUT / "inputs" / f"{tid}.rgb.png")
        index["files"].append(dict(file=f"inputs/{tid}.rgb.png", card="F-39, F-12, F-13", call="Pillow decode, RGB"))
        f = json.load(open(ROOT / f"prototype/fixtures/{tid}.json"))["face"]
        faces[tid] = dict(box=f["box"], kps=np.array(f["kps"]))

    # ---- full-image results (JSON) ----
    results["grey"] = "L = 0.299 R + 0.587 G + 0.114 B, in float32, from inputs/<tid>.rgb.png / 255"
    results["yunet"] = {}
    for tid, rgb in rgbs.items():
        raw = yunet_raw(rgb)
        big = max(raw, key=lambda r: r[2] * r[3])
        x, y, w, h = big[:4]
        results["yunet"][tid] = dict(
            raw_xywh_kps_score=[round(v, 3) for v in big], box_corners=[round(v, 3) for v in (x, y, x + w, y + h)],
            kps=[[round(big[4 + 2 * i], 3), round(big[5 + 2 * i], 3)] for i in range(5)], score=round(big[14], 4),
            model="models/face_detection_yunet_2023mar.onnx", input_size=[rgb.shape[1], rgb.shape[0]],
            params=dict(score_threshold=0.6, nms_threshold=0.3, top_k=5000),
            tolerance=dict(box_px=1.0, kps_px=1.0, score=0.01), card="F-39, F-12")
    results["landmarks_from_box"] = {
        tid: dict(box=[round(v, 3) for v in faces[tid]["box"]], kps=np.round(landmarks_from_box(faces[tid]["box"]), 3).tolist(),
                  crop_from_real=np.round(crop_transform(faces[tid]), 5).tolist(),
                  crop_from_estimate=np.round(crop_transform(dict(box=faces[tid]["box"], kps=landmarks_from_box(faces[tid]["box"]))), 5).tolist(),
                  tolerance=dict(kps_px=1e-3), card="F-12") for tid in EXAMPLES}
    results["detect_screen"] = {}
    for tid, rgb in rgbs.items():
        L = to_gray(rgb)
        p_ref = detect_screen(L)
        r = lambda ps: [[round(a, 5), round(b, 5)] for a, b in ps]
        results["detect_screen"][tid] = dict(peaks=r(p_ref), screen_found=bool(p_ref),
                                             same_peaks_with_opencv_8bit_median=r(detect_screen_with(L, median15_8bit)) == r(p_ref),
                                             same_peaks_with_12bit_median=r(detect_screen_with(L, median15_quantised(12))) == r(p_ref),
                                             card="F-13")
    results["descreen_full"] = {}
    for tid, rgb in rgbs.items():
        L = to_gray(rgb)
        W = crop_transform(faces[tid])
        scale = float(np.sqrt(abs(np.linalg.det(W[:, :2]))))
        cell = (SETTINGS["size_px"] / SETTINGS["dots_across"]) / scale
        out, info = descreen(L.astype(np.float32), cell)
        results["descreen_full"][tid] = dict(cell_px_in_original=round(cell, 5), info=info,
                                             mean_abs_change=round(float(np.abs(out - L).mean()), 6),
                                             out_mean=round(float(out.mean()), 6),
                                             tolerance=dict(mean_abs_change=0.002, out_mean=0.001), card="F-13")

    # ---- SIFT + RANSAC (same_photo.py's layer 2), on whole pictures ----
    def gray8(rgb):
        return (np.clip(to_gray(rgb), 0, 1) * 255).astype(np.uint8)
    sift = cv2.SIFT_create(nfeatures=2000)
    def feats(g):
        f = 600 / max(g.shape)
        g = cv2.resize(g, None, fx=f, fy=f, interpolation=cv2.INTER_AREA if f < 1 else cv2.INTER_CUBIC)
        return sift.detectAndCompute(g, None)
    def inliers(a, b):
        ka, da = feats(a); kb, db = feats(b)
        m = cv2.BFMatcher(cv2.NORM_L2).knnMatch(da, db, k=2)
        good = [p[0] for p in m if len(p) == 2 and p[0].distance < 0.75 * p[1].distance]
        if len(good) < 4:
            return 0
        src = np.float32([ka[x.queryIdx].pt for x in good]); dst = np.float32([kb[x.trainIdx].pt for x in good])
        M, mask = cv2.estimateAffinePartial2D(src, dst, method=cv2.RANSAC, ransacReprojThreshold=4.0)
        return int(mask.sum()) if mask is not None else 0
    G = {t: gray8(r) for t, r in rgbs.items()}
    sp = {}
    for t, g in G.items():
        h, w = g.shape
        R = cv2.getRotationMatrix2D((w / 2, h / 2), 4, 1.0)
        sp[f"{t} / rotated 4 degrees"] = inliers(g, cv2.warpAffine(g, R, (w, h), borderMode=cv2.BORDER_REPLICATE))
        sp[f"{t} / half size"] = inliers(g, cv2.resize(g, (w // 2, h // 2), interpolation=cv2.INTER_AREA))
    ts = list(G)
    for i in range(len(ts)):
        for j in range(i + 1, len(ts)):
            sp[f"{ts[i]} vs {ts[j]}"] = inliers(G[ts[i]], G[ts[j]])
    results["sift_ransac_inliers"] = dict(pairs=sp, method="SIFT 2000 features at 600 px, ratio 0.75, estimateAffinePartial2D RANSAC 4 px",
                                          tolerance="within 25%, or, if the port uses AKAZE or ORB, same/different on the same side of the thresholds",
                                          card="F-39, F-42")

    # ---- dHash fingerprint (PIP-20 layer 1) ----
    def dhash(g):
        s = cv2.resize(g, (9, 8), interpolation=cv2.INTER_AREA).astype(np.int16)
        bits = (s[:, 1:] > s[:, :-1]).ravel()
        return "".join("1" if b else "0" for b in bits)
    dh = {}
    for t, g in G.items():
        h, w = g.shape
        a, b = dhash(g), dhash(cv2.resize(g, (w // 2, h // 2), interpolation=cv2.INTER_AREA))
        ok, enc = cv2.imencode(".jpg", g, [cv2.IMWRITE_JPEG_QUALITY, 60]); c = dhash(cv2.imdecode(enc, 0))
        dh[t] = dict(hash=a, bits_differing_half_size=sum(x != y for x, y in zip(a, b)),
                     bits_differing_jpeg60=sum(x != y for x, y in zip(a, c)))
    dh["between examples"] = {f"{ts[i]} vs {ts[j]}": sum(x != y for x, y in zip(dh[ts[i]]["hash"], dh[ts[j]]["hash"]))
                              for i in range(len(ts)) for j in range(i + 1, len(ts))}
    results["dhash"] = dict(method="grey, INTER_AREA to 9 x 8, bit = right pixel brighter than left, 64 bits row by row",
                            values=dh, card="F-42")

    # ---- per-operation arrays, on 96 x 96 crops ----
    for tid, case in (("charles-fillmore", "fillmore"), ("ernest-holmes", "holmes")):
        L = to_gray(rgbs[tid])
        C, rect = face_crop(L, faces[tid])
        results.setdefault("crops", {})[case] = dict(source=f"inputs/{tid}.rgb.png", rect_xywh=rect)
        save(case, "input", C, f"grey crop {rect} of inputs/{tid}.rgb.png", "exact", "F-39")
        save(case, "gaussian_s3", cv2.GaussianBlur(C, (0, 0), 3), "GaussianBlur(src, ksize=(0,0), sigma=3), default border (REFLECT_101)",
             dict(max_abs=1e-4), "F-39")
        for sg in (1.8, 6.0):
            save(case, f"bilateral_s{sg}", cv2.bilateralFilter(C, -1, SETTINGS["edge_blur_color"], sg),
                 f"bilateralFilter(src, d=-1, sigmaColor={SETTINGS['edge_blur_color']}, sigmaSpace={sg})", dict(max_abs=2e-3), "F-39, F-13")
        M = log_spectrum(C)
        save(case, "logspec", M, "log1p(|fftshift(fft2((L - GaussianBlur(L, sigma 3)) * hann(h) x hann(w)))|); numpy.hanning",
             dict(max_abs=1e-3), "F-39, F-13")
        med = median_filter(M, size=15)
        m8, m12 = median15_8bit(M), median15_quantised(12)(M)
        save(case, "median15", med, "scipy.ndimage.median_filter(logspec, size=15, mode='reflect')",
             dict(max_abs=float(M.max() - M.min()) / 4095 * 1.01, why="a 12-bit sliding-histogram median is within one 12-bit step"),
             "F-39, F-13", note=f"cv2.medianBlur accepts floats only for sizes 3 and 5, and its 8-bit route isn't precise enough: "
                                f"on Cady it moves one screen peak by a frequency bin (results.json, detect_screen). Here the 8-bit route "
                                f"differs by up to {float(np.abs(m8 - med).max()):.4f}, a 12-bit median by up to {float(np.abs(m12 - med).max()):.5f}. "
                                f"Note the border: scipy reflects (mode='reflect'); medianBlur replicates.")
        D = M - med
        save(case, "max5", maximum_filter(D, size=5), "scipy.ndimage.maximum_filter(logspec - median15, size=5); = cv2.dilate with a 5 x 5 rectangle",
             dict(max_abs=1e-6), "F-39, F-13")
        F = cv2.dft(C.astype(np.float32), flags=cv2.DFT_COMPLEX_OUTPUT)
        back = cv2.idft(F, flags=cv2.DFT_SCALE | cv2.DFT_REAL_OUTPUT)
        save(case, "idft_roundtrip", back, "idft(dft(input, DFT_COMPLEX_OUTPUT), DFT_SCALE | DFT_REAL_OUTPUT); equals input",
             dict(max_abs=1e-5), "F-39")
        A = np.array([[1.02, 0.03, 1.5], [-0.03, 1.02, -2.0]], np.float32)
        save(case, "warp_linear", cv2.warpAffine(C, A, (CROP, CROP), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE),
             f"warpAffine(src, M={A.tolist()}, INTER_LINEAR, BORDER_REPLICATE)", dict(max_abs=2e-3), "F-39")
        save(case, "warp_cubic", cv2.warpAffine(C, A, (CROP, CROP), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE),
             f"warpAffine(src, M={A.tolist()}, INTER_CUBIC, BORDER_REPLICATE)", dict(max_abs=2e-3), "F-39")
        # ECC: recover A from the input and its warp
        crit = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 300, 1e-6)
        Wd = cv2.warpAffine(C, A, (CROP, CROP), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        cc, Mf = cv2.findTransformECC(cv2.GaussianBlur(C, (0, 0), 1.5), cv2.GaussianBlur(Wd, (0, 0), 1.5),
                                      np.eye(2, 3, dtype=np.float32), cv2.MOTION_AFFINE, crit, None, 1)
        results.setdefault("ecc", {})[case] = dict(template="GaussianBlur(input, 1.5)", input="GaussianBlur(warp_linear, 1.5)",
                                                   call="findTransformECC(template, input, eye(2,3), MOTION_AFFINE, (EPS|COUNT, 300, 1e-6), mask=None, gaussFiltSize=1)",
                                                   warp=np.round(Mf, 5).tolist(), cc=round(float(cc), 5),
                                                   tolerance=dict(warp_abs=0.01, cc=0.005), card="F-39, F-30")
        # Farneback flow on 8-bit images, as local_drift calls it
        def norm8(a):
            return np.clip(((a - a.mean()) / (a.std() + 1e-6)) * 40 + 128, 0, 255).astype(np.uint8)
        g0, g1 = cv2.GaussianBlur(norm8(C), (0, 0), 1.0), cv2.GaussianBlur(norm8(Wd), (0, 0), 1.0)
        save(case, "flow_in0", g0, "8-bit: GaussianBlur(norm(input), 1.0), norm = clip((a - mean) / std * 40 + 128)", "exact", "F-39")
        save(case, "flow_in1", g1, "8-bit: GaussianBlur(norm(warp_linear), 1.0)", "exact", "F-39")
        fl = cv2.calcOpticalFlowFarneback(g0, g1, None, 0.5, 3, 9, 5, 5, 1.1, 0)
        save(case, "flow", fl, "calcOpticalFlowFarneback(flow_in0, flow_in1, None, 0.5, 3, 9, 5, 5, 1.1, 0); channels dx, dy",
             dict(p95_abs_px=0.05, why="the drift check uses the 95th percentile of the magnitude"), "F-39, F-30")
        # masks: distance transform and connected components
        cut = np.asarray(Image.open(ROOT / f"prototype/fixtures/{tid}.cutout.png")).astype(np.float32) / 255
        x, y, w, h = rect
        mk = (cut[y:y + h, x:x + w] > 0.5).astype(np.uint8)
        save(case, "mask", mk, f"cut-out fixture > 0.5, crop {rect}", "exact", "F-39")
        save(case, "dist_outside", cv2.distanceTransform((mk == 0).astype(np.uint8), cv2.DIST_L2, 5),
             "distanceTransform(mask == 0, DIST_L2, maskSize 5)", dict(max_abs=1e-3), "F-39, F-15")
    syn = np.zeros((60, 80), np.uint8)
    cv2.circle(syn, (20, 20), 10, 1, -1); cv2.rectangle(syn, (45, 10), (70, 30), 1, -1); syn[50:53, 5:9] = 1; syn[40, 60] = 1
    n, lab, stats, cent = cv2.connectedComponentsWithStats(syn, 8)
    save("synthetic", "blobs", syn, "circle (20,20) r10; rectangle (45,10)-(70,30); 3 x 4 block at (5,50); one pixel at (60,40)", "exact", "F-39, F-15")
    results["connected_components"] = dict(input="synthetic/blobs.f32", connectivity=8, count_with_background=int(n),
                                           areas_sorted=sorted(int(a) for a in stats[1:, cv2.CC_STAT_AREA]),
                                           largest_share=round(float(stats[1:, cv2.CC_STAT_AREA].max() / stats[1:, cv2.CC_STAT_AREA].sum()), 5),
                                           tolerance="exact (label numbering may differ; compare sorted areas)", card="F-39, F-15")
    # the halftone threshold map, small
    tm = _threshold_map(64, 2, 64 / 11, 45)
    save("synthetic", "threshold_map", tm, "_threshold_map(N=64, ss=2, pitch=64/11, angle_deg=45)",
         dict(max_abs=1e-5, or_share_off_by_one_rank=0.001), "F-14")
    # the key mask on a synthetic green-screen strip
    strip = np.zeros((8, 64, 3), np.float32)
    t = np.linspace(0, 1, 64, dtype=np.float32)
    strip[..., 0] = strip[..., 2] = 0.4 * (1 - t); strip[..., 1] = 0.4 * (1 - t) + t
    save("synthetic", "key_strip", strip, "grey 0.4 blending into pure green, left to right (RGB 0..1)", "exact", "F-30")
    save("synthetic", "key_mask", key_mask(strip), f"key_mask(key_strip), key_lo {SETTINGS['key_lo']}, key_hi {SETTINGS['key_hi']}",
         dict(max_abs=1e-6), "F-30")
    json.dump(results, open(OUT / "results.json", "w"), indent=1)
    json.dump(index, open(OUT / "index.json", "w"), indent=1)
    print("wrote", len(index["files"]), "files to", OUT)
    print("same peaks with OpenCV's 8-bit median:", {t: v["same_peaks_with_opencv_8bit_median"] for t, v in results["detect_screen"].items()})
    print("same peaks with a 12-bit median:", {t: v["same_peaks_with_12bit_median"] for t, v in results["detect_screen"].items()})
    print("screen found:", {t: v["screen_found"] for t, v in results["detect_screen"].items()})
    print("sift:", results["sift_ransac_inliers"]["pairs"])
    print("dhash:", {t: (v["bits_differing_half_size"], v["bits_differing_jpeg60"]) for t, v in dh.items() if t in EXAMPLES}, dh["between examples"])


if __name__ == "__main__":
    main()
