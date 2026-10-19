"""T-02 mock-ups: the three versions of a portrait, and the options for the black-and-white one.

Run: python prototype/versions.py  ->  prototype/out/versions-board.png, versions-zoom.png

Inside the outline, the black-and-white version has only one possible picture: white where the
white version has dots, black elsewhere. "White dots on black" and "black dots on white" are the
same pixels with a round-dot screen. So the options differ only at the edge:
  A  white line kept: black gap and white line, as in the white version; clipped at the line's outer edge
  B  no line: clipped at the figure's own edge
  C  black edge: the gap and line are black, so the figure sits on a thin black margin (8 px)
"""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from common import *
from recipe import make_master, SETTINGS
from PIL import ImageDraw, ImageFont

OUT = ROOT / "prototype/out"
PAGES = {"light page": (244, 241, 234), "dark page": (28, 30, 38), "coloured page": (62, 92, 120)}


def rgba(value, alpha):
    out = np.zeros(value.shape + (4,), np.uint8)
    out[..., :3] = np.round(np.clip(value, 0, 1) * 255)[..., None].astype(np.uint8)
    out[..., 3] = np.round(np.clip(alpha, 0, 1) * 255).astype(np.uint8)
    out[out[..., 3] == 0, :3] = 0
    return out


def bw_versions(L, s=SETTINGS):
    g, w = s["outline_gap_px"], s["outline_width_px"]
    dots, fig, ring, dist = L["dots"], L["figure"], L["ring"], L["dist"]
    # soft outer edge of the line, from the supersampled distance (area-averaged)
    outer = np.clip((g + w + 0.5) - dist, 0, 1)
    outer = np.maximum(outer, fig)
    return {
        "A": rgba(dots * fig + ring, outer),        # white line kept
        "B": rgba(dots, fig),                       # no line
        "C": rgba(dots * fig, outer),               # black edge
    }


def on(rgba_u8, page):
    a = rgba_u8[..., 3:4].astype(np.float32) / 255
    return (rgba_u8[..., :3] * a + np.array(page, np.float32) * (1 - a)).clip(0, 255).astype(np.uint8)


def font(n):
    try:
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", n)
    except OSError:
        return ImageFont.load_default()


def main():
    tiles, zooms, sizes = {}, [], {}
    for tid in EXAMPLES:
        rgb = load_rgb(original_path(tid))
        fx = json.load(open(ROOT / f"prototype/fixtures/{tid}.json"))
        mask = np.asarray(Image.open(ROOT / f"prototype/fixtures/{tid}.cutout.png")).astype(np.float32) / 255
        face = dict(box=fx["face"]["box"], kps=np.array(fx["face"]["kps"]))
        white, info = make_master(rgb, mask, face, layers=True)
        bw = bw_versions(info["layers"])
        tiles[tid] = {"W": white, **bw}
        for k, im in [("white", white)] + [(f"bw-{k}", v) for k, v in bw.items()]:
            p = OUT / f"{tid}.version-{k}.png"
            Image.fromarray(im, "RGBA").save(p, optimize=True)
            sizes[f"{tid}.{k}"] = p.stat().st_size
    # board: one block per page colour; rows = teachers, columns = white version, A, B, C
    cols = [("W", "White version (today)"), ("A", "B&W  A: white line"), ("B", "B&W  B: no line"), ("C", "B&W  C: black edge")]
    T, gap = 300, 10
    blocks = []
    for pname, page in PAGES.items():
        rows = []
        for tid in EXAMPLES:
            row = [cv2.resize(on(tiles[tid][k], page), (T, T), interpolation=cv2.INTER_AREA) for k, _ in cols]
            rows.append(np.hstack(sum([[r, np.full((T, gap, 3), page, np.uint8)] for r in row], [])[:-1]))
        blk = np.vstack(sum([[r, np.full((gap, rows[0].shape[1], 3), page, np.uint8)] for r in rows], [])[:-1])
        head = Image.new("RGB", (blk.shape[1], 40), (50, 52, 60)); d = ImageDraw.Draw(head)
        d.text((12, 9), pname.capitalize(), fill=(235, 235, 235), font=font(20))
        edge = np.full((gap, blk.shape[1], 3), page, np.uint8)
        blocks.append(np.vstack([np.asarray(head), edge, blk, edge]))
    head = Image.new("RGB", (blocks[0].shape[1], 44), (36, 38, 46)); d = ImageDraw.Draw(head)
    for i, (_, lab) in enumerate(cols):
        d.text((i * (T + gap) + 8, 11), lab, fill=(235, 235, 235), font=font(19))
    board = np.vstack([np.asarray(head)] + blocks)
    Image.fromarray(board).save(OUT / "versions-board.png", optimize=True)
    # zoom: where Fillmore's head meets the background at eye level (left side), 1.8x, on light and dark
    tid = "charles-fillmore"
    fig = tiles[tid]["B"][..., 3] > 127
    y = int(SETTINGS["eye_y_frac"] * SETTINGS["size_px"]) - 60
    x = int(np.argmax(fig[y]))
    y0, x0 = max(y - 100, 0), max(x - 70, 0)
    zs = []
    for page in [PAGES["light page"], PAGES["dark page"]]:
        r = [cv2.resize(on(tiles[tid][k], page)[y0:y0 + 200, x0:x0 + 200], (360, 360), interpolation=cv2.INTER_NEAREST) for k in "ABC"]
        zs.append(np.hstack([r[0], np.full((360, 8, 3), 90, np.uint8), r[1], np.full((360, 8, 3), 90, np.uint8), r[2]]))
    z = np.vstack([zs[0], np.full((8, zs[0].shape[1], 3), 90, np.uint8), zs[1]])
    head = Image.new("RGB", (z.shape[1], 40), (36, 38, 46)); d = ImageDraw.Draw(head)
    for i, lab in enumerate(["A: white line", "B: no line", "C: black edge"]):
        d.text((i * 368 + 8, 9), lab, fill=(235, 235, 235), font=font(18))
    Image.fromarray(np.vstack([np.asarray(head), z])).save(OUT / "versions-zoom.png", optimize=True)
    json.dump(sizes, open(OUT / "versions-sizes.json", "w"), indent=1)
    print(json.dumps(sizes, indent=1))


if __name__ == "__main__":
    main()
