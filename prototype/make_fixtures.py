"""Save the prototype's model-dependent inputs as fixtures, so the recipe can be re-run from the repo alone.

Needs the stand-in models in the scratch folder (see README). Writes prototype/fixtures/:
  <tid>.cutout.png    8-bit cut-out mask (union of u2net_human_seg and isnet-general-use; stand-in for Bria)
  <tid>.json          face box + 5 landmarks (YuNet, models/, since recipe 0.5.0; SCRFD-500M before) and the
                      registration onto the owner's target (2x3, original px -> 500 px target frame)

  python prototype/make_fixtures.py --faces-only   re-detects only the faces (needs nothing outside the repo)
"""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from common import *
from register import register

FIX = ROOT / "prototype/fixtures"
FIX.mkdir(parents=True, exist_ok=True)
def face_record(rgb):
    face = detect_face(rgb)
    return dict(box=[round(v, 2) for v in face["box"]], kps=np.round(face["kps"], 2).tolist(), score=round(face["score"], 3),
                detector="yunet-2023mar")

if "--faces-only" in sys.argv:
    for tid in EXAMPLES:
        p = FIX / f"{tid}.json"
        d = json.load(open(p))
        d["face"] = face_record(load_rgb(original_path(tid)))
        json.dump(d, open(p, "w"), indent=1)
        print(tid, "face updated")
    sys.exit(0)

for tid in EXAMPLES:
    rgb = load_rgb(original_path(tid))
    Image.fromarray((proto_cutout(tid) * 255).round().astype(np.uint8)).save(FIX / f"{tid}.cutout.png")
    warp, *_, res = register(tid, verbose=False)
    json.dump(dict(face=face_record(rgb),
                   target_warp_500=np.round(warp, 6).tolist(), registration=res), open(FIX / f"{tid}.json", "w"), indent=1)
    print(tid, "saved")
