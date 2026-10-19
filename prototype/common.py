"""Shared helpers for the style prototype (Phase 0, P0-3). Reference code, not the product."""
from pathlib import Path
import numpy as np, cv2
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ["charles-fillmore", "emilie-cady", "ernest-holmes"]
PAGE = (28, 30, 38)  # stand-in for the library's dark page colour

def original_path(tid):
    d = ROOT / "design/portraits/originals"
    return next(d.glob(f"{tid}.*"))

def target_path(tid):
    return ROOT / f"design/portraits/targets/{tid}.png"

def load_rgb(path):
    return np.asarray(Image.open(path).convert("RGB")).astype(np.float32) / 255

def to_gray(rgb):
    return (rgb @ np.array([0.299, 0.587, 0.114], np.float32)).astype(np.float32)

def load_alpha(path):
    return np.asarray(Image.open(path).convert("RGBA"))[..., 3].astype(np.float32) / 255

def on_page(rgba_u8):
    """Composite an RGBA uint8 array on the page colour; returns RGB uint8."""
    a = rgba_u8[..., 3:4].astype(np.float32) / 255
    bg = np.array(PAGE, np.float32)
    out = rgba_u8[..., :3].astype(np.float32) * a + bg * (1 - a)
    return out.clip(0, 255).astype(np.uint8)

# ---------- cut-out (stand-in for the production background-removal model) ----------
_sess = {}
def cutout(rgb, model_path, size=320):
    """Run a rembg-style ONNX segmentation model (u2net family / isnet / birefnet). Returns mask 0..1 at input size."""
    import onnxruntime as ort
    if model_path not in _sess:
        _sess[model_path] = ort.InferenceSession(str(model_path), providers=["CPUExecutionProvider"])
    s = _sess[model_path]
    inp = s.get_inputs()[0]
    shp = inp.shape
    size = shp[2] if isinstance(shp[2], int) else size
    h, w = rgb.shape[:2]
    x = cv2.resize(rgb, (size, size), interpolation=cv2.INTER_AREA)
    if "isnet" in str(model_path):
        x = (x - 0.5) / 1.0
    else:
        x = (x / max(x.max(), 1e-6) - np.array([0.485, 0.456, 0.406])) / np.array([0.229, 0.224, 0.225])
    x = x.transpose(2, 0, 1)[None].astype(np.float32)
    out = s.run(None, {inp.name: x})[0][0, 0]
    if "birefnet" in str(model_path).lower():
        out = 1 / (1 + np.exp(-out))
    out = (out - out.min()) / max(out.max() - out.min(), 1e-6)
    return cv2.resize(out.astype(np.float32), (w, h), interpolation=cv2.INTER_LINEAR)

# ---------- face box and eyes ----------
# Prototype: SCRFD-500M (insightface "buffalo_sc", research licence) used ONLY to measure the examples here.
# Production proposal: OpenCV YuNet (MIT), which gives the same box + 5 landmarks. The model file stays outside the repo.
FACE_MODEL = "/tmp/claude-0/-home-claude/27dc5434-a5bc-5b9d-b2a3-302381507a91/scratchpad/models/buffalo_sc/det_500m.onnx"

def detect_face(rgb, model_path=FACE_MODEL, thresh=0.4):
    """Return dict(box=(x0,y0,x1,y1), eyes=((lx,ly),(rx,ry)), kps=5x2, score) for the largest face, or None."""
    import onnxruntime as ort
    if model_path not in _sess:
        _sess[model_path] = ort.InferenceSession(str(model_path), providers=["CPUExecutionProvider"])
    s = _sess[model_path]
    h, w = rgb.shape[:2]
    S = 640
    sc = S / max(h, w)
    img = np.zeros((S, S, 3), np.float32)
    img[: int(round(h * sc)), : int(round(w * sc))] = cv2.resize(rgb, (int(round(w * sc)), int(round(h * sc))))
    x = ((img * 255 - 127.5) / 128).transpose(2, 0, 1)[None].astype(np.float32)
    outs = s.run(None, {s.get_inputs()[0].name: x})
    boxes, kpss, scores = [], [], []
    for i, st in enumerate((8, 16, 32)):
        sco, bb, kp = outs[i][:, 0], outs[i + 3] * st, outs[i + 6] * st
        f = S // st
        cy, cx = np.mgrid[:f, :f]
        centers = np.stack([cx, cy], -1).reshape(-1, 2).astype(np.float32) * st
        centers = np.repeat(centers, 2, axis=0)
        keep = sco >= thresh
        c = centers[keep]
        b = np.stack([c[:, 0] - bb[keep, 0], c[:, 1] - bb[keep, 1], c[:, 0] + bb[keep, 2], c[:, 1] + bb[keep, 3]], 1)
        k = (kp[keep].reshape(-1, 5, 2) + c[:, None, :])
        boxes.append(b); kpss.append(k); scores.append(sco[keep])
    boxes, kpss, scores = np.concatenate(boxes), np.concatenate(kpss), np.concatenate(scores)
    if len(scores) == 0:
        return None
    i = int(np.argmax((boxes[:, 2] - boxes[:, 0]) * (boxes[:, 3] - boxes[:, 1]) * (scores > thresh)))
    b, k = boxes[i] / sc, kpss[i] / sc
    return dict(box=tuple(float(v) for v in b), kps=k, eyes=(tuple(k[0]), tuple(k[1])), score=float(scores[i]))

# ---------- prototype cut-out: union of two small public models (stand-in for Bria RMBG 2.0) ----------
SCRATCH = Path("/tmp/claude-0/-home-claude/27dc5434-a5bc-5b9d-b2a3-302381507a91/scratchpad")

def proto_cutout(tid):
    """Union of the u2net_human_seg and isnet-general-use masks, holes filled. Cached as .npy in scratch."""
    ms = [np.load(SCRATCH / f"mask_{m}_{tid}.npy") for m in ("u2net_human_seg", "isnet-general-use")]
    m = np.maximum(*ms)
    b = (m > 0.5).astype(np.uint8)
    # fill holes: flood from the border
    h, w = b.shape
    ff = b.copy(); mask = np.zeros((h + 2, w + 2), np.uint8)
    cv2.floodFill(ff, mask, (0, 0), 1)
    holes = (ff == 0)
    m = np.where(holes, 1.0, m)
    return m.astype(np.float32)

def similarity_from_eyes(src_eyes, dst_eyes):
    """2x3 similarity transform mapping src eye points to dst eye points."""
    (a, b), (c, d) = src_eyes, dst_eyes
    a, b, c, d = map(np.asarray, (a, b, c, d))
    vs, vd = b - a, d - c
    s = np.linalg.norm(vd) / np.linalg.norm(vs)
    ang = np.arctan2(vd[1], vd[0]) - np.arctan2(vs[1], vs[0])
    R = s * np.array([[np.cos(ang), -np.sin(ang)], [np.sin(ang), np.cos(ang)]])
    t = c - R @ a
    return np.hstack([R, t[:, None]]).astype(np.float32)
