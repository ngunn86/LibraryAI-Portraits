"""The portrait recipe, prototype version (P0-3). Reference code for the harness, not the product.

Steps (code only; the cut-out and the face landmarks are inputs):
  descreen (find and remove a printed dot pattern; edge-preserving blur) -> [optional: blend with an
  AI-enhanced copy, PIP-13] -> crop -> tone (levels from the face) -> halftone (45° round dots, white on
  transparency) -> smoothed figure mask -> code-drawn outline -> composite -> 1000 x 1000 RGBA master.
"""
import numpy as np, cv2

RECIPE_VERSION = "0.2.0"

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


def blend_enhanced(L, enhanced, s=SETTINGS):
    """PIP-13 (proposed, owner's method): blend an AI-enhanced copy of the original with it, after aligning.

    Image models often shift or rescale what they redraw, so the enhanced copy is first aligned to the
    original (affine, by image correlation). If alignment is poor, the enhanced copy is not used.
    """
    E = enhanced @ np.array([0.299, 0.587, 0.114], np.float32) if enhanced.ndim == 3 else enhanced
    h, w = L.shape
    E = cv2.resize(E.astype(np.float32), (w, h), interpolation=cv2.INTER_AREA)
    warp = np.eye(2, 3, dtype=np.float32)
    crit = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 200, 1e-6)
    try:
        cc, warp = cv2.findTransformECC(cv2.GaussianBlur(L, (0, 0), 2), cv2.GaussianBlur(E, (0, 0), 2), warp,
                                        cv2.MOTION_AFFINE, crit, None, 1)
    except cv2.error:
        cc = 0.0
    if cc < s["enhance_min_align"]:
        return L, dict(used=False, align_corr=round(float(cc), 3))
    Ea = cv2.warpAffine(E, warp, (w, h), flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP, borderMode=cv2.BORDER_REPLICATE)
    k = s["enhance_blend"]
    return (1 - k) * L + k * Ea, dict(used=True, align_corr=round(float(cc), 3), blend=k)


def make_master(rgb, cutout_mask, face, s=SETTINGS, warp=None, enhanced=None):
    """Return (RGBA uint8 N x N master, info dict). `warp` overrides the crop (used to compare at the owner's framing)."""
    N, ss = s["size_px"], s["supersample"]
    W = crop_transform(face, s) if warp is None else warp
    L = rgb @ np.array([0.299, 0.587, 0.114], np.float32) if rgb.ndim == 3 else rgb
    pitch = N / s["dots_across"]
    scale = float(np.sqrt(abs(np.linalg.det(W[:, :2]))))
    L, ds = descreen(L.astype(np.float32), pitch / scale, s)
    if enhanced is not None:
        L, bl = blend_enhanced(L, enhanced, s)
    else:
        bl = None
    Lc = cv2.warpAffine(L.astype(np.float32), W, (N, N), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    Mc = cv2.warpAffine(cutout_mask.astype(np.float32), W, (N, N), flags=cv2.INTER_LINEAR, borderValue=0)
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
