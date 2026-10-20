"""T-16 prototype: is it the same photograph (another scan, crop, print or retouch) or a different one?

Layer (b) of the proposal, feature matching: SIFT keypoints, ratio test, then RANSAC on a similarity
transform. Copies of one photograph share many geometrically consistent points; different photographs
share almost none. Mirrored prints are caught by also matching the mirror image.

Run: python prototype/same_photo.py -> prints inlier counts and writes out/same-photo.json
Limits: the "different" pairs here are different people. Different sittings of the same person, the
hard case, need real pairs; the coverage survey (SRC-14) collects them before thresholds are fixed.
"""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from common import *

def gray8(rgb):
    return (np.clip(to_gray(rgb), 0, 1) * 255).astype(np.uint8)

def variants(g, rng):
    h, w = g.shape
    out = {}
    out["crop 80%"] = g[int(h * .08):int(h * .88), int(w * .1):int(w * .9)]
    out["half size"] = cv2.resize(g, (w // 2, h // 2), interpolation=cv2.INTER_AREA)
    out["double size"] = cv2.resize(g, (w * 2, h * 2), interpolation=cv2.INTER_CUBIC)
    M = cv2.getRotationMatrix2D((w / 2, h / 2), 4, 1.0)
    out["rotated 4°"] = cv2.warpAffine(g, M, (w, h), borderMode=cv2.BORDER_REPLICATE)
    ok, enc = cv2.imencode(".jpg", g, [cv2.IMWRITE_JPEG_QUALITY, 25]); out["jpeg q25"] = cv2.imdecode(enc, 0)
    out["blurred"] = cv2.GaussianBlur(g, (0, 0), 1.5)
    out["darker, flatter"] = np.clip((g.astype(np.float32) / 255) ** 1.6 * 200 + 20, 0, 255).astype(np.uint8)
    yy, xx = np.mgrid[0:h, 0:w]
    screen = (np.sin((xx + yy) * 0.9) * np.sin((xx - yy) * 0.9) * 0.5 + 0.5)
    out["reprinted (dot screen)"] = np.clip(g * (0.75 + 0.5 * screen) - 30, 0, 255).astype(np.uint8)
    out["mirrored"] = g[:, ::-1]
    noisy = g.astype(np.float32) + rng.normal(0, 12, g.shape)
    out["noisy rescan"] = np.clip(noisy, 0, 255).astype(np.uint8)
    return out

sift = cv2.SIFT_create(nfeatures=2000)
def feats(g):
    g = cv2.resize(g, None, fx=600 / max(g.shape), fy=600 / max(g.shape), interpolation=cv2.INTER_AREA) if max(g.shape) > 600 else \
        cv2.resize(g, None, fx=600 / max(g.shape), fy=600 / max(g.shape), interpolation=cv2.INTER_CUBIC)
    return sift.detectAndCompute(g, None)

def inliers(a, b):
    best = 0
    ka, da = feats(a)
    for bb in (b, b[:, ::-1]):                      # also try the mirror image
        kb, db = feats(bb)
        if da is None or db is None or len(ka) < 3 or len(kb) < 3:
            continue
        m = cv2.BFMatcher(cv2.NORM_L2).knnMatch(da, db, k=2)
        good = [p[0] for p in m if len(p) == 2 and p[0].distance < 0.75 * p[1].distance]
        if len(good) < 4:
            continue
        src = np.float32([ka[x.queryIdx].pt for x in good]); dst = np.float32([kb[x.trainIdx].pt for x in good])
        M, mask = cv2.estimateAffinePartial2D(src, dst, method=cv2.RANSAC, ransacReprojThreshold=4.0)
        best = max(best, int(mask.sum()) if mask is not None else 0)
    return best

rng = np.random.default_rng(1)
G = {t: gray8(load_rgb(original_path(t))) for t in EXAMPLES}
same, diff = {}, {}
for t, g in G.items():
    for name, v in variants(g, rng).items():
        same[f"{t} / {name}"] = inliers(g, v)
ts = list(G)
for i in range(len(ts)):
    for j in range(i + 1, len(ts)):
        diff[f"{ts[i]} vs {ts[j]}"] = inliers(G[ts[i]], G[ts[j]])
        for name, v in variants(G[ts[j]], rng).items():
            diff[f"{ts[i]} vs {ts[j]} ({name})"] = inliers(G[ts[i]], v)
res = dict(same_min=min(same.values()), same_median=float(np.median(list(same.values()))),
           diff_max=max(diff.values()), diff_median=float(np.median(list(diff.values()))), same=same, diff=diff)
json.dump(res, open(ROOT / "prototype/out/same-photo.json", "w"), indent=1)
print({k: v for k, v in res.items() if not isinstance(v, dict)})
print("weakest same-photo pairs:", sorted(same.items(), key=lambda kv: kv[1])[:4])
print("strongest different pairs:", sorted(diff.items(), key=lambda kv: -kv[1])[:3])
