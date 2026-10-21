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
# YuNet (MIT, committed in models/), the production detector (PIP-04, F-12). Recipe 0.4.0 and earlier
# measured the examples with SCRFD-500M (insightface, research licence, never in the repo); 0.5.0 re-measured
# the crop with YuNet, because the two detectors place the mouth corners differently (prototype/README.md).
FACE_MODEL = ROOT / "models/face_detection_yunet_2023mar.onnx"

def detect_face(rgb, model_path=FACE_MODEL, thresh=0.6):
    """Return dict(box=(x0,y0,x1,y1), eyes=((lx,ly),(rx,ry)), kps=5x2, score) for the largest face, or None.

    YuNet returns [x, y, w, h] boxes; they are turned into corners here. It finds faces of about 10-300 px,
    so an image whose long side is over 640 px is searched on a copy reduced to 640 px, then scaled back.
    """
    h, w = rgb.shape[:2]
    sc = min(1.0, 640 / max(h, w))
    img = (np.clip(rgb, 0, 1) * 255).astype(np.uint8)
    img = img if img.ndim == 3 else np.repeat(img[..., None], 3, -1)
    if sc < 1:
        img = cv2.resize(img, (int(round(w * sc)), int(round(h * sc))), interpolation=cv2.INTER_AREA)
    det = cv2.FaceDetectorYN.create(str(model_path), "", (img.shape[1], img.shape[0]), thresh, 0.3, 5000)
    _, faces = det.detect(img[..., ::-1].copy())          # OpenCV expects BGR
    if faces is None or len(faces) == 0:
        return None
    f = faces[int(np.argmax(faces[:, 2] * faces[:, 3]))].astype(np.float64)
    x, y, bw, bh = f[:4] / sc
    k = f[4:14].reshape(5, 2) / sc
    return dict(box=(float(x), float(y), float(x + bw), float(y + bh)), kps=k, eyes=(tuple(k[0]), tuple(k[1])),
                score=float(f[14]))

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
