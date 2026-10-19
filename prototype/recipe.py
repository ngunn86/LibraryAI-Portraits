"""The portrait recipe, prototype version (P0-3). Reference code for the harness, not the product.

Steps (code only; the cut-out and the face landmarks are inputs):
  descreen (find and remove a printed dot pattern; edge-preserving blur) -> crop -> [blend in the aligned
  AI-enhanced copy at 50%, whose keyed background can also give the cut-out; PIP-13] -> tone (levels from the face) -> halftone (45° round dots, white on
  transparency) -> smoothed figure mask -> code-drawn outline -> composite -> 1000 x 1000 RGBA master.
The other versions (D-39) come from the master's layers: the black-and-white version (bw_version: the dots on
black, with a black edge where the white line was, clipped at the line's outer edge; STY-08) and the 500 px
copies of both (small; STY-09).
"""
import numpy as np, cv2

RECIPE_VERSION = "0.4.0"

SETTINGS = {
    "size_px": 1000,
    # crop (measured on the owner's three examples; see prototype/RESULTS.md)
    "eye_mouth_frac": 0.237,      # eye-midpoint to mouth-midpoint distance / side
    "eye_y_frac": 0.443,          # eye midpoint height / side
    "face_centre_x_frac": 0.50,   # face box centre / side
    "min_face_px": 90,            # pre-check: smallest face-box width accepted in the original (the owner's own are 108-183)
    # descreen (PIP-05): blur sizes are in dot cells, converted to original pixels, so they suit any original size
    "edge_blur_cells": 0.30,      # edge-preserving (bilateral) blur on every original, spatial sigma
    "edge_blur_color": 0.08,      # bilateral colour sigma (tones 0..1): edges stronger than this survive
    "screen_peak_log": 1.6,       # a spectral peak this far (log units) above its surroundings counts
    "screen_min_cyc_px": 0.08,    # ignore frequencies below this (image content, not a print screen)
    "screen_min_peaks": 2,        # at least two independent peak directions = a printed dot screen
    "notch_sigma_bins": 2.0,      # width of each notch in the frequency domain
    "descreen_blur_cells": 0.6,   # stronger edge-preserving blur when a screen was found
    # tone: levels taken from the face's own tones, then a gamma
    "white_from_face_p98": 0.02,  # white point = face p98 + this
    "black_k": 0.2,               # black point = face p5 - k * (face p98 - face p5)
    "gamma": 1.8,                 # coverage = ramp ** gamma (lifts contrast, keeps shadows transparent)
    "tone_blur_cells": 0.05,      # blur of the tone map before screening, in dot cells
    "sharpen_amount": 0.6,        # unsharp mask before screening (0 = off)
    "sharpen_radius_cells": 1.0,
    # AI-enhanced blend (PIP-13, proposed; owner's method): applied only when an enhanced copy is supplied
    "enhance_blend": 0.5,         # share of the aligned enhanced copy in the blend
    "enhance_min_align": 0.90,    # minimum alignment correlation, else the enhanced copy is not used
    "enhance_max_drift_cells": 0.7,  # after alignment, face details may sit at most this far apart (95th pct)
    "key_lo": 0.15,               # keyed background: greenness below this is the person...
    "key_hi": 0.45,               # ...and above this is background (soft edge in between)
    # halftone
    "dots_across": 110,           # side / dot-cell pitch, measured along the 45° grid
    "grid_angle_deg": 45,
    "supersample": 4,
    # figure mask and outline
    "mask_smooth_px": 9,          # Gaussian sigma that rounds off stray hair before the line follows it
    "body_smooth_px": 28,         # stronger smoothing below the chin: shoulders become clean curves
    "body_blend_px": 120,         # height over which head smoothing blends into body smoothing
    "outline_gap_px": 2,          # transparent gap between the figure and the line
    "outline_width_px": 6,        # line width
    # the other versions (D-39, T-02)
    "bw_edge": "black",           # black-and-white version: gap and line drawn black (option C); clipped at the line's outer edge
    "small_px": 500,              # side of the small copies of the white and black-and-white versions
}


def detect_screen(L, s=SETTINGS):
    """Find a printed dot screen: compact spectral peaks standing well above their surroundings.

    Returns a list of (fy, fx) peak frequencies in cycles/px (one of each symmetric pair).
    """
    from scipy.ndimage import median_filter, maximum_filter
    h, w = L.shape
    hp = L - cv2.GaussianBlur(L, (0, 0), 3)
    win = np.outer(np.hanning(h), np.hanning(w)).astype(np.float32)
    M = np.log1p(np.abs(np.fft.fftshift(np.fft.fft2(hp * win))))
    D = M - median_filter(M, size=15)
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
    # a screen needs at least two directions (a lattice), not just one line pattern
    dirs = []
    for f in peaks:
        a = np.degrees(np.arctan2(f[0], f[1])) % 180
        if all(min(abs(a - d), 180 - abs(a - d)) > 20 for d in dirs):
            dirs.append(a)
    return peaks if len(dirs) >= s["screen_min_peaks"] else []


def descreen(L, cell_px_in_original, s=SETTINGS):
    """Remove a printed dot pattern (notch filter) and smooth grain with an edge-preserving blur.

    `cell_px_in_original`: the size of one output dot cell, in original pixels.
    """
    h, w = L.shape
    peaks = detect_screen(L, s)
    out = L.astype(np.float32)
    if peaks:
        F = np.fft.fftshift(np.fft.fft2(out))
        fy = (np.arange(h) - h // 2)[:, None] / h
        fx = (np.arange(w) - w // 2)[None, :] / w
        notch = np.ones((h, w), np.float32)
        sig_y, sig_x = s["notch_sigma_bins"] / h, s["notch_sigma_bins"] / w
        for py, px in peaks:
            for k in (1, 2):                       # the peak and its first harmonic
                for sy, sx in ((py, px), (-py, -px)):
                    cy, cx = k * sy, k * sx
                    if abs(cy) < 0.5 and abs(cx) < 0.5:
                        notch *= 1 - np.exp(-(((fy - cy) / sig_y) ** 2 + ((fx - cx) / sig_x) ** 2) / 2)
        out = np.real(np.fft.ifft2(np.fft.ifftshift(F * notch))).astype(np.float32)
    blur_cells = s["descreen_blur_cells"] if peaks else s["edge_blur_cells"]
    sigma_space = max(blur_cells * cell_px_in_original, 0.5)
    out = cv2.bilateralFilter(np.clip(out, 0, 1), -1, s["edge_blur_color"], sigma_space)
    return out, dict(screen_found=bool(peaks), screen_peaks=[[round(a, 4), round(b, 4)] for a, b in peaks],
                     edge_blur_sigma_px=round(float(sigma_space), 2))


def crop_transform(face, s=SETTINGS):
    """Similarity transform (2x3) from original pixels to the square frame, from the face landmarks."""
    N = s["size_px"]
    k = np.asarray(face["kps"], np.float64)
    eye = (k[0] + k[1]) / 2
    mouth = (k[3] + k[4]) / 2
    em = np.linalg.norm(mouth - eye)
    scale = s["eye_mouth_frac"] * N / em
    bx = face["box"]
    cx = (bx[0] + bx[2]) / 2
    tx = s["face_centre_x_frac"] * N - scale * cx
    ty = s["eye_y_frac"] * N - scale * eye[1]
    return np.array([[scale, 0, tx], [0, scale, ty]], np.float32)


def tone_to_coverage(L, mask, face_box_frame, pitch, s=SETTINGS):
    """Map luminance (0..1) to white-dot coverage (0..1) using levels taken from the face.

    The face's tones are read at the scale of one dot cell (blurred), inside the face box and well
    inside the figure, so single dark pixels (pupils, nostrils) don't move the levels.
    """
    N = L.shape[0]
    Lb = cv2.GaussianBlur(L, (0, 0), 0.9 * pitch)
    inner = cv2.erode((mask > 0.5).astype(np.uint8), np.ones((int(3.3 * pitch) | 1,) * 2, np.uint8)) > 0
    x0, y0, x1, y1 = [int(round(v)) for v in face_box_frame]
    x0, y0, x1, y1 = max(x0, 0), max(y0, 0), min(x1, N), min(y1, N)
    sel = np.zeros_like(inner); sel[y0:y1, x0:x1] = True
    fv = Lb[sel & inner]
    if fv.size < 100:
        fv = Lb[mask > 0.5]
    p5, p98 = np.percentile(fv, [5, 98])
    white = p98 + s["white_from_face_p98"]
    black = p5 - s["black_k"] * (p98 - p5)
    src = L
    if s.get("sharpen_amount", 0) > 0:
        blur = cv2.GaussianBlur(L, (0, 0), s["sharpen_radius_cells"] * pitch)
        src = L + s["sharpen_amount"] * (L - blur)
    ramp = np.clip((src - black) / max(white - black, 1e-3), 0, 1)
    return ramp ** s["gamma"], dict(black=float(black), white=float(white), face_p5=float(p5), face_p98=float(p98))


def _threshold_map(N, ss, pitch, angle_deg):
    """Euclidean round-dot screen: per (super)pixel threshold in 0..1 (low = turns white first)."""
    M = N * ss
    y, x = np.mgrid[:M, :M].astype(np.float32)
    x = (x + 0.5) / ss; y = (y + 0.5) / ss
    a = np.radians(angle_deg)
    u = (x * np.cos(a) + y * np.sin(a)) / pitch
    v = (-x * np.sin(a) + y * np.cos(a)) / pitch
    u = 2 * (u - np.floor(u)) - 1          # -1..1 within the cell
    v = 2 * (v - np.floor(v)) - 1
    au, av = np.abs(u), np.abs(v)
    centre = (au + av) <= 1
    key = np.where(centre, 2 - (au ** 2 + av ** 2), (1 - au) ** 2 + (1 - av) ** 2)
    # rank-normalise the key over one cell so coverage maps to area exactly
    g = np.linspace(-1, 1, 401, dtype=np.float32)
    gu, gv = np.meshgrid(g, g)
    gau, gav = np.abs(gu), np.abs(gv)
    gk = np.sort(np.where(gau + gav <= 1, 2 - (gau ** 2 + gav ** 2), (1 - gau) ** 2 + (1 - gav) ** 2).ravel())
    rank = np.searchsorted(gk, key.ravel()).reshape(key.shape) / gk.size
    return (1 - rank).astype(np.float32)


def smooth_mask(mask, s=SETTINGS, chin_y=None):
    """Binary figure mask with stray hair and small bumps rounded off; holes filled; largest piece only.

    The head keeps more of its shape (hair) than the shoulders: below the chin the mask is smoothed
    harder, so the line runs down the shoulders as a clean curve even when the cut-out is ragged there.
    """
    b = (mask > 0.5).astype(np.uint8)
    n, lab, stats, _ = cv2.connectedComponentsWithStats(b, 8)
    if n > 1:
        keep = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
        b = (lab == keep).astype(np.uint8)
    bf = b.astype(np.float32)
    head = cv2.GaussianBlur(bf, (0, 0), s["mask_smooth_px"])
    if chin_y is not None and s.get("body_smooth_px", 0) > s["mask_smooth_px"]:
        body = cv2.GaussianBlur(bf, (0, 0), s["body_smooth_px"])
        H = b.shape[0]
        ramp = np.clip((np.arange(H) - chin_y) / max(s["body_blend_px"], 1), 0, 1).astype(np.float32)[:, None]
        sm = head * (1 - ramp) + body * ramp
    else:
        sm = head
    out = (sm > 0.5).astype(np.uint8)
    # fill holes: anything not connected to the border through background
    n, lab = cv2.connectedComponents((out == 0).astype(np.uint8), connectivity=4)
    border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    out = np.where((out == 0) & ~np.isin(lab, list(border)), 1, out).astype(np.uint8)
    return out


def key_mask(rgb, s=SETTINGS):
    """Cut-out mask from an image whose background was replaced with flat pure green (the enhance prompt asks
    for this). The portraits are black-and-white, so 'how much greener than grey' separates them cleanly."""
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    greenness = g - np.maximum(r, b)                  # ~0 for grey/sepia, ~1 for pure green
    lo, hi = s["key_lo"], s["key_hi"]
    m = 1 - np.clip((greenness - lo) / (hi - lo), 0, 1)
    return m.astype(np.float32)


def align_enhanced(L, enhanced_rgb, s=SETTINGS):
    """Find the affine map from the original's pixels to the enhanced copy's pixels (PIP-13).

    Image models re-render at their own size and often shift or rescale slightly, so the copy is first
    scaled to the original's size, then aligned by image correlation over the figure only (the keyed
    background is ignored). Returns (3x3 map original->enhanced, correlation, enhanced grey, key mask).
    """
    E = enhanced_rgb.astype(np.float32)
    Eg = E @ np.array([0.299, 0.587, 0.114], np.float32)
    Em = key_mask(E, s)
    h, w = L.shape
    He, We = Eg.shape
    D = np.diag([w / We, h / He, 1.0]).astype(np.float64)        # enhanced -> original-sized
    Er = cv2.resize(Eg, (w, h), interpolation=cv2.INTER_AREA)
    Emr = (cv2.resize(Em, (w, h), interpolation=cv2.INTER_AREA) > 0.5).astype(np.uint8)
    Emr = cv2.erode(Emr, np.ones((5, 5), np.uint8))
    M = np.eye(2, 3, dtype=np.float32)
    crit = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 300, 1e-6)
    try:
        cc, M = cv2.findTransformECC(cv2.GaussianBlur(L, (0, 0), 1.5), cv2.GaussianBlur(Er, (0, 0), 1.5), M,
                                     cv2.MOTION_AFFINE, crit, Emr if Emr.any() else None, 1)
    except cv2.error:
        return None, 0.0, Eg, Em
    M3 = np.vstack([M, [0, 0, 1]]).astype(np.float64)            # original -> original-sized enhanced
    return np.linalg.inv(D) @ M3, float(cc), Eg, Em             # original -> enhanced


def local_drift(L, Eg, A, face_box, cell_px, s=SETTINGS):
    """After the overall alignment, how far do details inside the face still sit apart? (PIP-13)

    An image model can move an eye or a mouth a little without shifting the whole picture. Overall
    alignment can't fix that, and a 50% blend would show it as a soft double image. Dense optical flow
    between the original and the aligned copy measures it; the result is in dot cells.
    """
    h, w = L.shape
    Ea = cv2.warpAffine(Eg, A[:2].astype(np.float32), (w, h), flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP,
                        borderMode=cv2.BORDER_REPLICATE)
    x0, y0, x1, y1 = [int(round(v)) for v in face_box]
    x0, y0, x1, y1 = max(x0, 0), max(y0, 0), min(x1, w), min(y1, h)
    def norm(a):
        r = a[y0:y1, x0:x1]
        return np.clip(((a - r.mean()) / (r.std() + 1e-6)) * 40 + 128, 0, 255).astype(np.uint8)
    g0 = cv2.GaussianBlur(norm(L), (0, 0), 1.0)
    g1 = cv2.GaussianBlur(norm(Ea), (0, 0), 1.0)
    flow = cv2.calcOpticalFlowFarneback(g0, g1, None, 0.5, 3, 9, 5, 5, 1.1, 0)
    mag = np.hypot(flow[..., 0], flow[..., 1])[y0:y1, x0:x1]
    return float(np.percentile(mag, 95)) / max(cell_px, 1e-6)


def make_master(rgb, cutout_mask, face, s=SETTINGS, warp=None, enhanced=None, layers=False):
    """Return (RGBA uint8 N x N master, info dict). `warp` overrides the crop (used to compare at the owner's framing).
    With layers=True, info["layers"] holds the pieces the other versions are built from (versions.py, T-02):
    dots, figure, ring (all N x N, 0..1) and dist (distance outside the figure, px)."""
    N, ss = s["size_px"], s["supersample"]
    W = crop_transform(face, s) if warp is None else warp
    L = rgb @ np.array([0.299, 0.587, 0.114], np.float32) if rgb.ndim == 3 else rgb
    pitch = N / s["dots_across"]
    scale = float(np.sqrt(abs(np.linalg.det(W[:, :2]))))
    L, ds = descreen(L.astype(np.float32), pitch / scale, s)
    Lc = cv2.warpAffine(L.astype(np.float32), W, (N, N), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    bl = None
    if enhanced is not None:
        # PIP-13: blend in the frame, so the copy's extra resolution survives (it is usually 2-4x the original)
        A, cc, Eg, Em = align_enhanced(L, enhanced, s)
        bl = dict(used=False, align_corr=round(cc, 3))
        drift = local_drift(L, Eg, A, face["box"], pitch / scale, s) if A is not None else None
        if drift is not None:
            bl["face_drift_cells"] = round(drift, 3)
        if A is not None and cc >= s["enhance_min_align"] and drift <= s["enhance_max_drift_cells"]:
            W3 = np.vstack([W, [0, 0, 1]]).astype(np.float64)
            T = (A @ np.linalg.inv(W3))[:2].astype(np.float32)      # frame -> enhanced (inverse map)
            Ec = cv2.warpAffine(Eg, T, (N, N), flags=cv2.INTER_CUBIC + cv2.WARP_INVERSE_MAP, borderMode=cv2.BORDER_REPLICATE)
            # the same edge-preserving blur as the original got, so the copy's own fine texture can't beat with the dots
            Ec = cv2.bilateralFilter(np.clip(Ec, 0, 1).astype(np.float32), -1, s["edge_blur_color"], s["edge_blur_cells"] * pitch)
            k = s["enhance_blend"]
            Lc = (1 - k) * Lc + k * Ec
            bl.update(used=True, blend=k)
            if cutout_mask is None:                                  # the keyed background is the cut-out
                cutout_mask_frame = cv2.warpAffine(Em, T, (N, N), flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP, borderValue=0)
                bl["cutout"] = "from enhanced copy"
    if cutout_mask is None and not (bl and bl.get("cutout")):
        raise ValueError("no cut-out: give a cut-out mask, or an enhanced copy with a keyed background")
    if cutout_mask is not None:
        Mc = cv2.warpAffine(cutout_mask.astype(np.float32), W, (N, N), flags=cv2.INTER_LINEAR, borderValue=0)
    else:
        Mc = cutout_mask_frame
    bx = np.array(face["box"], np.float64).reshape(2, 2)
    bxf = np.hstack([bx, np.ones((2, 1))]) @ W.T
    cov, levels = tone_to_coverage(Lc, Mc, bxf.ravel(), pitch, s)
    cov = cv2.GaussianBlur(cov, (0, 0), max(pitch * s["tone_blur_cells"], 0.1))
    kf = np.hstack([np.asarray(face["kps"], np.float64), np.ones((5, 1))]) @ W.T
    eye_y, mouth_y = (kf[0, 1] + kf[1, 1]) / 2, (kf[3, 1] + kf[4, 1]) / 2
    chin_y = mouth_y + 0.8 * (mouth_y - eye_y)
    fig = smooth_mask(Mc, s, chin_y=chin_y)
    # halftone at supersampled resolution
    thr = _threshold_map(N, ss, pitch, s["grid_angle_deg"])
    cov_ss = cv2.resize(cov, (N * ss, N * ss), interpolation=cv2.INTER_LINEAR)
    dots_ss = (cov_ss > thr).astype(np.float32)
    dots = cv2.resize(dots_ss, (N, N), interpolation=cv2.INTER_AREA)
    # clip dots to the figure (soft edge from the supersampled mask)
    fig_ss = cv2.resize(fig.astype(np.float32), (N * ss, N * ss), interpolation=cv2.INTER_LINEAR)
    fig_soft = cv2.resize((fig_ss > 0.5).astype(np.float32), (N, N), interpolation=cv2.INTER_AREA)
    dots *= fig_soft
    # outline: band at distance (gap, gap + width] outside the figure, anti-aliased, from the supersampled mask
    outside_ss = (fig_ss <= 0.5).astype(np.uint8)
    d_ss = cv2.distanceTransform(outside_ss, cv2.DIST_L2, 5) / ss
    g, w = s["outline_gap_px"], s["outline_width_px"]
    ring_ss = ((d_ss > g) & (d_ss <= g + w)).astype(np.float32)
    ring = cv2.resize(ring_ss, (N, N), interpolation=cv2.INTER_AREA)
    alpha = np.clip(np.maximum(dots, ring), 0, 1)
    out = np.zeros((N, N, 4), np.uint8)
    out[..., :3] = 255
    out[..., 3] = np.round(alpha * 255).astype(np.uint8)
    out[out[..., 3] == 0, :3] = 0  # fully transparent pixels carry no colour
    info = dict(recipe_version=RECIPE_VERSION, levels=levels, crop_scale=scale, descreen=ds, enhance_blend=bl)
    if layers:
        dist = cv2.resize(d_ss.astype(np.float32), (N, N), interpolation=cv2.INTER_AREA)
        info["layers"] = dict(dots=dots, figure=fig_soft, ring=ring, dist=dist)
    return out, info


def check_master(rgba, N=1000):
    """STY-06: N x N, RGBA, every visible pixel pure white, corners transparent."""
    problems = []
    if rgba.shape != (N, N, 4):
        problems.append(f"size {rgba.shape}")
    vis = rgba[..., 3] > 0
    if (rgba[..., :3][vis] != 255).any():
        problems.append("non-white visible pixels")
    if any(rgba[y, x, 3] for y, x in [(0, 0), (0, N - 1)]):
        problems.append("top corners not transparent")
    return problems


def bw_version(layers, s=SETTINGS):
    """STY-08: the black-and-white version (option C, D-39). Inside the outline: white where the master has dots,
    black elsewhere; the gap and the line are black; transparent outside the line's outer edge. Same size and
    footprint as the master."""
    g, w = s["outline_gap_px"], s["outline_width_px"]
    dots, fig, ring, dist = layers["dots"], layers["figure"], layers["ring"], layers["dist"]
    outer = np.maximum(np.clip((g + w + 0.5) - dist, 0, 1), fig)        # soft outer edge of the line
    value = dots * fig + (ring if s["bw_edge"] == "white" else 0)
    out = np.zeros(dots.shape + (4,), np.uint8)
    out[..., :3] = np.round(np.clip(value, 0, 1) * 255)[..., None].astype(np.uint8)
    out[..., 3] = np.round(np.clip(outer, 0, 1) * 255).astype(np.uint8)
    out[out[..., 3] == 0, :3] = 0
    return out


def small(rgba, s=SETTINGS):
    """STY-09: the small copy of a version: area-averaged with premultiplied alpha, so edges stay clean."""
    n = s["small_px"]
    a = rgba[..., 3:4].astype(np.float32) / 255
    pm = cv2.resize(np.concatenate([rgba[..., :3].astype(np.float32) * a, a], axis=2), (n, n), interpolation=cv2.INTER_AREA)
    a2 = pm[..., 3:4]
    out = np.zeros((n, n, 4), np.uint8)
    out[..., :3] = np.round(np.clip(pm[..., :3] / np.maximum(a2, 1e-6), 0, 255)).astype(np.uint8)
    out[..., 3] = np.round(a2[..., 0] * 255).astype(np.uint8)
    out[out[..., 3] == 0, :3] = 0
    return out


def check_bw(rgba, master=None):
    """STY-08: square RGBA; every visible pixel grey (R = G = B); top corners transparent; the inside of the
    figure fully opaque; and, given the master, the same footprint (opaque wherever the master shows)."""
    problems = []
    N = rgba.shape[0]
    if rgba.ndim != 3 or rgba.shape != (N, N, 4):
        problems.append(f"size {rgba.shape}")
        return problems
    vis = rgba[..., 3] > 0
    c = rgba[..., :3][vis].astype(int)
    if (c[:, 0] != c[:, 1]).any() or (c[:, 1] != c[:, 2]).any():
        problems.append("visible pixels that aren't grey")
    if any(rgba[y, x, 3] for y, x in [(0, 0), (0, N - 1)]):
        problems.append("top corners not transparent")
    if master is not None:
        shows = cv2.erode((master[..., 3] > 0).astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
        if (rgba[..., 3][shows] < 255).mean() > 0.001:
            problems.append("not opaque everywhere the master shows")
    return problems

