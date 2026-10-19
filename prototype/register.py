"""Register each original onto its hand-made target, to measure crop geometry and the tone curve."""
import sys, json
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from common import *

def target_tone(alpha, pitch=4.5):
    return cv2.GaussianBlur(alpha, (0, 0), pitch * 0.9)

def register(tid, verbose=True):
    rgb = load_rgb(original_path(tid)); L = to_gray(rgb)
    A = load_alpha(target_path(tid))[:500, :500]
    T = target_tone(A)
    fo = detect_face(rgb)
    ft = detect_face(np.dstack([T, T, T]))
    if ft is None:
        raise SystemExit(f"{tid}: no face found on target tone map")
    W = similarity_from_eyes(fo["eyes"], ft["eyes"])
    # refine with ECC on blurred images, figure region only
    Lw0 = cv2.warpAffine(L, W, (500, 500), flags=cv2.INTER_LINEAR)
    fig = (cv2.GaussianBlur(A, (0, 0), 6) > 0.15).astype(np.uint8)
    fig = cv2.erode(fig, np.ones((15, 15), np.uint8))
    Lb = cv2.GaussianBlur(L, (0, 0), 4.5 * 0.9 / W[0, 0] ** 0.5 if W[0,0] > 0 else 2)
    warp = W.copy()
    crit = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 300, 1e-6)
    Lw0b = cv2.GaussianBlur(Lw0, (0, 0), 4.5 * 0.9)
    try:
        # template = original warped by the eye fit; input = target tone. R maps template -> target.
        R = np.eye(2, 3, dtype=np.float32)
        cc, R = cv2.findTransformECC(Lw0b.astype(np.float32), T.astype(np.float32), R, cv2.MOTION_AFFINE, crit, fig, 1)
        R3 = np.vstack([R, [0, 0, 1]]); W3 = np.vstack([W, [0, 0, 1]])
        warp = (R3 @ W3)[:2].astype(np.float32)
    except cv2.error as e:
        cc = None
    Lw = cv2.warpAffine(L, warp, (500, 500), flags=cv2.INTER_LINEAR, borderValue=0)
    eyes_t = [warp @ np.array([*e, 1]) for e in fo["eyes"]]
    box = fo["box"]
    corners = np.array([[box[0], box[1], 1], [box[2], box[3], 1]]) @ warp.T
    res = dict(
        tid=tid, ecc=None if cc is None else round(float(cc), 3),
        scale=round(float(np.sqrt(abs(np.linalg.det(warp[:, :2])))), 3),
        eye_mid=[round(float(v) / 500, 3) for v in (eyes_t[0] + eyes_t[1]) / 2],
        eye_dist=round(float(np.linalg.norm(eyes_t[1] - eyes_t[0])) / 500, 3),
        face_box=[round(float(v) / 500, 3) for v in corners.ravel()],
        face_w=round(float(corners[1, 0] - corners[0, 0]) / 500, 3),
    )
    if verbose:
        print(json.dumps(res))
    return warp, Lw, T, A, fig, res

if __name__ == "__main__":
    out = {}
    tiles = []
    for tid in EXAMPLES:
        warp, Lw, T, A, fig, res = register(tid)
        out[tid] = res
        # overlay check: original (red/green) vs target tone (blue)
        ov = np.dstack([Lw, Lw, T]) * 255
        tiles.append(ov.clip(0, 255).astype(np.uint8))
    Image.fromarray(np.hstack(tiles)).save(SCRATCH / "register_overlay.png")
    json.dump(out, open(SCRATCH / "register.json", "w"), indent=1)
