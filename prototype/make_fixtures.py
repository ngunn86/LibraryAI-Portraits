"""Save the prototype's model-dependent inputs as fixtures, so the recipe can be re-run from the repo alone.

Needs the stand-in models in the scratch folder (see README). Writes prototype/fixtures/:
  <tid>.cutout.png    8-bit cut-out mask (union of u2net_human_seg and isnet-general-use; stand-in for Bria)
  <tid>.json          face box + 5 landmarks (SCRFD-500M, research use only) and the registration onto the
                      owner's target (2x3, original px -> 500 px target frame)
"""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from common import *
from register import register

FIX = ROOT / "prototype/fixtures"
FIX.mkdir(parents=True, exist_ok=True)
for tid in EXAMPLES:
    rgb = load_rgb(original_path(tid))
    Image.fromarray((proto_cutout(tid) * 255).round().astype(np.uint8)).save(FIX / f"{tid}.cutout.png")
    face = detect_face(rgb)
    warp, *_, res = register(tid, verbose=False)
    json.dump(dict(face=dict(box=[round(v, 2) for v in face["box"]], kps=np.round(face["kps"], 2).tolist(), score=round(face["score"], 3)),
                   target_warp_500=np.round(warp, 6).tolist(), registration=res), open(FIX / f"{tid}.json", "w"), indent=1)
    print(tid, "saved")
