"""Check the PIP-13 mechanics with synthetic 'AI-enhanced' copies (no AI here): each copy is the original,
upscaled 2.8x, sharpened, rescaled by 2% and shifted, with the background replaced by flat green.
Measures: alignment, ghosting (edge agreement with the plain result) and the keyed cut-out vs the stand-in."""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from common import *
from recipe import make_master, SETTINGS
from run_examples import filled

res = {}
for tid in EXAMPLES:
    rgb = load_rgb(original_path(tid)); h, w = rgb.shape[:2]
    fx = json.load(open(ROOT / f"prototype/fixtures/{tid}.json"))
    mask = np.asarray(Image.open(ROOT / f"prototype/fixtures/{tid}.cutout.png")).astype(np.float32) / 255
    face = dict(box=fx["face"]["box"], kps=np.array(fx["face"]["kps"]))
    g = to_gray(rgb)
    up = cv2.resize(g, (int(w * 2.8), int(h * 2.8)), interpolation=cv2.INTER_CUBIC)
    up = np.clip(up + 0.6 * (up - cv2.GaussianBlur(up, (0, 0), 3)), 0, 1)
    mu = cv2.resize(mask, (up.shape[1], up.shape[0]))
    E = np.dstack([up, up, up])
    E = E * mu[..., None] + np.array([0, 1, 0], np.float32) * (1 - mu[..., None])
    Mx = np.array([[1.02, 0, 9], [0, 1.02, -7]], np.float32)
    E = cv2.warpAffine(E, Mx, (E.shape[1], E.shape[0]), borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 1, 0))
    # a copy where the AI has moved the eyes and mouth a little (a local change no overall alignment can fix)
    yy, xx = np.mgrid[:E.shape[0], :E.shape[1]].astype(np.float32)
    k = np.array(face["kps"]) * 2.8 * 1.02 + np.array([9, -7])
    bump = np.zeros_like(xx)
    for (px, py) in k[[0, 1, 3, 4]]:
        bump += np.exp(-(((xx - px) ** 2 + (yy - py) ** 2) / (2 * (0.06 * E.shape[1]) ** 2)))
    cell_e = 2.8 * (1000 / 110) / (0.237 * 1000 / np.linalg.norm((np.array(face["kps"][3]) + face["kps"][4]) / 2 - (np.array(face["kps"][0]) + face["kps"][1]) / 2))
    E_moved = cv2.remap(E.astype(np.float32), (xx - bump * 1.2 * cell_e).astype(np.float32), yy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    _, info_moved = make_master(rgb, mask, face, enhanced=E_moved)
    plain, _ = make_master(rgb, mask, face)
    blended, info = make_master(rgb, mask, face, enhanced=E)
    keyed, info2 = make_master(rgb, None, face, enhanced=E)
    a = lambda im: cv2.GaussianBlur(im[..., 3].astype(np.float32) / 255, (0, 0), 6)
    edge = lambda x: cv2.Sobel(x, cv2.CV_32F, 1, 0)
    agree = float(np.corrcoef(edge(a(plain)).ravel(), edge(a(blended)).ravel())[0, 1])
    fp, fk = filled(cv2.resize(plain[..., 3], (500, 500)).astype(np.float32) / 255), filled(cv2.resize(keyed[..., 3], (500, 500)).astype(np.float32) / 255)
    iou = float((fp & fk).sum() / (fp | fk).sum())
    res[tid] = dict(align_corr=info["enhance_blend"]["align_corr"], used=info["enhance_blend"]["used"],
                    face_drift_cells=info["enhance_blend"]["face_drift_cells"],
                    moved_features_drift_cells=info_moved["enhance_blend"].get("face_drift_cells"),
                    moved_features_used=info_moved["enhance_blend"]["used"],
                    edge_agreement_with_plain=round(agree, 3), keyed_cutout_iou_vs_standin=round(iou, 3))
    print(tid, res[tid])
json.dump(res, open(ROOT / "prototype/out/enhance-mechanics.json", "w"), indent=1)
