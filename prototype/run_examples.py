"""Run the prototype recipe on the owner's three examples; write masters, a comparison board and measures."""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from common import *
from register import target_tone
from recipe import make_master, check_master, SETTINGS, RECIPE_VERSION
from measure_dots import measure as measure_pitch

OUT = ROOT / "prototype/out"


def filled(alpha500):
    """Figure region: everything not connected to the image border through transparent pixels."""
    B = (alpha500 > 0.3).astype(np.uint8)
    B = cv2.morphologyEx(B, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
    n, lab = cv2.connectedComponents((B == 0).astype(np.uint8), connectivity=4)
    border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    ext = np.isin(lab, list(border)) & (B == 0)
    return ~ext


def measures(ours500, target500):
    a, t = ours500.astype(np.float32) / 255, target500
    fa, ft = filled(a), filled(t)
    iou = (fa & ft).sum() / max((fa | ft).sum(), 1)
    inside = cv2.erode((fa & ft).astype(np.uint8), np.ones((15, 15), np.uint8)).astype(bool)
    ta, tt = target_tone(a), target_tone(t)
    tone_mae = float(np.abs(ta - tt)[inside].mean())
    tone_corr = float(np.corrcoef(ta[inside], tt[inside])[0, 1])
    return dict(figure_iou=round(float(iou), 3), tone_mae=round(tone_mae, 3), tone_corr=round(tone_corr, 3),
                coverage_ours=round(float(a.mean()), 3), coverage_target=round(float(t.mean()), 3))


def add_header(img, labels, col_w, h=44):
    from PIL import ImageDraw, ImageFont
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
    except OSError:
        font = ImageFont.load_default()
    head = Image.new("RGB", (img.shape[1], h), (50, 52, 60))
    d = ImageDraw.Draw(head)
    for i, lab in enumerate(labels):
        d.text((i * col_w + 12, 11), lab, fill=(235, 235, 235), font=font)
    return np.vstack([np.asarray(head), img])


def tile(rgba_or_rgb, size=420):
    im = rgba_or_rgb
    if im.shape[-1] == 4:
        im = on_page(im)
    return cv2.resize(im, (size, size), interpolation=cv2.INTER_AREA)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    report = {"recipe_version": RECIPE_VERSION, "settings": SETTINGS, "examples": {}}
    rows, zooms = [], []
    for tid in EXAMPLES:
        rgb = load_rgb(original_path(tid))
        fx = json.load(open(ROOT / f"prototype/fixtures/{tid}.json"))
        mask = np.asarray(Image.open(ROOT / f"prototype/fixtures/{tid}.cutout.png")).astype(np.float32) / 255
        face = dict(box=fx["face"]["box"], kps=np.array(fx["face"]["kps"]))
        warp1000 = (np.array(fx["target_warp_500"], np.float32) * 2)
        ours_owner, info_o = make_master(rgb, mask, face, warp=warp1000)
        ours_auto, info_a = make_master(rgb, mask, face)
        for name, im in [("owner-framing", ours_owner), ("auto-crop", ours_auto)]:
            Image.fromarray(im, "RGBA").save(OUT / f"{tid}.{name}.png")
        tgt_rgba = np.asarray(Image.open(target_path(tid)).convert("RGBA"))[:500, :500]
        tgt_a = tgt_rgba[..., 3].astype(np.float32) / 255
        ours500 = cv2.resize(ours_owner[..., 3], (500, 500), interpolation=cv2.INTER_AREA)
        m = measures(ours500, tgt_a)
        pitch_auto = measure_pitch(str(OUT / f"{tid}.auto-crop.png"))[1][0][0]
        m["dots_across_ours"] = round(1000 / pitch_auto, 1)
        m["sty06_problems"] = check_master(ours_auto)
        m["levels"] = info_a["levels"]
        report["examples"][tid] = m
        print(tid, json.dumps(m))
        # board row: original | owner's portrait | ours at owner's framing | ours, automatic crop
        orig = (rgb * 255).astype(np.uint8)
        h, w = orig.shape[:2]
        sq = np.zeros((max(h, w), max(h, w), 3), np.uint8); sq[:] = PAGE
        sq[(sq.shape[0] - h) // 2:(sq.shape[0] - h) // 2 + h, (sq.shape[1] - w) // 2:(sq.shape[1] - w) // 2 + w] = orig
        rows.append(np.hstack([tile(sq), np.full((420, 8, 3), 70, np.uint8), tile(tgt_rgba),
                               np.full((420, 8, 3), 70, np.uint8), tile(ours_owner), np.full((420, 8, 3), 70, np.uint8), tile(ours_auto)]))
        # zoom: same region of owner's and ours (owner framing), 3x
        zt = on_page(cv2.resize(tgt_rgba, (1000, 1000), interpolation=cv2.INTER_NEAREST))[100:400, 150:450]
        zo = on_page(ours_owner)[100:400, 150:450]
        zooms.append(np.hstack([cv2.resize(zt, (420, 420), interpolation=cv2.INTER_NEAREST), np.full((420, 8, 3), 70, np.uint8),
                                cv2.resize(zo, (420, 420), interpolation=cv2.INTER_NEAREST)]))
    sep = np.full((8, rows[0].shape[1], 3), 70, np.uint8)
    board = np.vstack(sum([[r, sep] for r in rows], [])[:-1])
    board = add_header(board, ["Original", "Your portrait", "Prototype (your framing)", "Prototype (automatic crop)"], 428)
    Image.fromarray(board).save(OUT / "board.png")
    sepz = np.full((8, zooms[0].shape[1], 3), 70, np.uint8)
    Image.fromarray(np.vstack(sum([[z, sepz] for z in zooms], [])[:-1])).save(OUT / "zoom.png")
    json.dump(report, open(OUT / "measures.json", "w"), indent=1)


if __name__ == "__main__":
    main()
