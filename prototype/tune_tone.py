"""Grid-search the tone settings against the owner's targets (coverage maps only; fast)."""
import sys, itertools, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from common import *
from register import register, target_tone
from recipe import SETTINGS, tone_to_coverage, smooth_mask

N = 1000
cases = []
for tid in EXAMPLES:
    rgb = load_rgb(original_path(tid)); L = to_gray(rgb)
    mask = proto_cutout(tid); face = detect_face(rgb)
    w500, *_ = register(tid, verbose=False)
    W = w500 * 2
    Lc = cv2.warpAffine(L, W, (N, N), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    Mc = cv2.warpAffine(mask, W, (N, N), borderValue=0)
    bx = np.hstack([np.array(face["box"]).reshape(2, 2), np.ones((2, 1))]) @ W.T
    A = load_alpha(target_path(tid))[:500, :500]
    T = cv2.resize(target_tone(A), (N, N))
    inside = cv2.erode((smooth_mask(Mc) > 0).astype(np.uint8), np.ones((31, 31), np.uint8)).astype(bool)
    cases.append((tid, Lc, Mc, bx.ravel(), T, inside))

pitch = N / 110
grid = dict(gamma=[1.4, 1.8, 2.2, 2.6, 3.0], black_k=[0.2, 0.4, 0.6, 0.8], white_from_face_p98=[-0.02, 0.0, 0.02, 0.04],
            sharpen_amount=[0.0, 0.6, 1.2])
results = []
for vals in itertools.product(*grid.values()):
    s = dict(SETTINGS); s.update(dict(zip(grid.keys(), vals)))
    errs = []
    for tid, Lc, Mc, bx, T, inside in cases:
        cov, _ = tone_to_coverage(Lc, Mc, bx, pitch, s)
        cb = cv2.GaussianBlur(cov, (0, 0), 0.9 * pitch * 2 / 2)  # same scale as target_tone at 1000 px
        cb = cv2.GaussianBlur(cov, (0, 0), 4.5 * 0.9 * 2)
        errs.append(float(np.abs(cb - T)[inside].mean()))
    results.append((float(np.mean(errs)), max(errs), vals, errs))
results.sort()
for r in results[:8]:
    print(f"mean {r[0]:.4f} worst {r[1]:.4f}  " + " ".join(f"{k}={v}" for k, v in zip(grid, r[2])) + "  per-example " + " ".join(f"{e:.3f}" for e in r[3]))
cur = [x for x in results if x[2] == (SETTINGS['gamma'], SETTINGS['black_k'], SETTINGS['white_from_face_p98'], SETTINGS['sharpen_amount'])]
