# Style prototype (P0-3): results, 2026-10-19 (recipe 0.3.0)

This folder answers one question before the harness builds anything: can code reproduce the owner's three hand-made portraits? It holds reference code and reference outputs, **not the product**. The harness builds the real modules (F-12..F-16) from what's learned here.

**Result:** recipe **0.3.0** reproduces the style closely on all three examples. The halftone, tone, line and crop are done entirely by code. The only model inputs are a cut-out and the face landmarks. See `out/board.png`, which is waiting for the owner's look.

## What was measured on the owner's portraits

| What | How | Result |
|---|---|---|
| Dot grid | FFT of the alpha channel | **45°**, cell pitch 4.55 px at 500 px, i.e. **110 cells across** (Fillmore 109, Holmes 111). Cady is finer (127), which looks like a different setting on that one |
| Dot shape | Close-up | Round white dots in shadows, merging into white with round dark holes in highlights (a classic round "Euclidean" dot). Dark tones are fully transparent |
| Framing | Each original registered onto its target (eye landmarks, refined by image alignment; correlation 0.91–0.99) | Eye-to-mouth distance **0.237 of the side** (0.223–0.246; this measure doesn't change when the head turns). Eye line at **0.443** of the height (0.40–0.51). Face centred (0.46–0.56). Fillmore and Cady are exactly 2× their originals, so their framing mostly came from the originals |
| Tone | Dot coverage vs. original brightness, over the registered figure | A levels-and-gamma curve. The white point sits at the face's own brightest tones (p98), and shadows drop out to transparent well above black |
| Line | Coverage profile inward from the figure's edge | About **3 px wide with a ~1 px gap** at 500 px, i.e. **6 px and 2 px** on the 1,000 px master (Fillmore, Holmes). Cady's is thicker (about 4.5 px at 500). The dots are clipped to a smoothed silhouette, and the line follows that same silhouette |

## Changes in 0.3.0 (owner's decisions D-18 to D-20, 2026-10-19)

- **The AI-enhanced blend is adopted (D-18).**
  - One image call per original, through OpenRouter (D-19), returns the original subtly restored, in black and white, on a flat pure-green background (`prompts/enhance_keyed.md`).
  - Code aligns the copy to the original, over the figure only, then blends it 50/50 **in the portrait's frame**. That keeps the copy's extra resolution, which matters for small originals.
- **The cut-out comes from the same image.** The green background gives the mask (`key_mask`), so the copy and its cut-out always line up. If that mask looks wrong, a fallback "background to green, change nothing else" call is made (`prompts/cutout_keyed.md`). OpenRouter has no dedicated background-removal model.
- **Mechanics test** (`test_enhance_mechanics.py`, no AI). Synthetic keyed copies were made at 2.8× the size, sharpened, rescaled by 2%, shifted and put on green:
  - aligned at a correlation of 0.997–0.999;
  - blended without double edges (edge agreement with the unblended result 0.98–1.00);
  - keyed cut-out matching the stand-in's (overlap 0.94–0.99).

  Real AI copies are first tried in the live smoke test and the trial.
- **Proposed prompts for every model step** are in `prompts/` (D-20).
- With no enhanced copy supplied, 0.3.0 gives the same output as 0.2.0, so `out/` is unchanged.

## Changes in 0.2.0 (owner's feedback, 2026-10-19)

- **Descreen (D-17).** Fillmore and Cady come from books and already carry a printed dot pattern. That made the new halftone's texture look strange: broken dots and a herringbone pattern around Cady's eyes.
  - Every original now gets an edge-preserving (bilateral) blur, sized in dot cells.
  - When a printed screen is found, its peaks are also notch-filtered and the blur is stronger.
  - Detection finds a screen in Fillmore and Cady but not in Holmes, which matches what the owner said. See `out/descreen-compare.png`.
- **The AI-enhanced blend (PIP-13): the owner's method.** A first version blended an aligned copy at the original's size. Unaligned blends showed double edges: edge agreement 0.58–0.72, against 0.99 aligned. This was superseded in 0.3.0.
- **The cut-out.** The owner's AI cut-out did better than the stand-in here, which was expected (see below).

## The recipe (0.2.0)

These are the settings in `recipe.py`. They become the `[recipe]` block of `settings.toml`.

```
descreen: edge-preserving blur on every original, 0.30 cell (0.6 with a screen) · colour sigma 0.08
          screen = compact spectral peaks ≥ 1.6 log units above surroundings in ≥ 2 directions, notch-filtered
enhance:  (when a copy is supplied) align by image correlation over the figure (≥ 0.90), blend 0.5 in the frame;
          cut-out from the copy's green background (greenness 0.15–0.45 soft edge)
size_px 1000 · dots_across 110 (side ÷ cell pitch along the 45° grid) · grid_angle_deg 45 · supersample 4
crop:    eye_mouth_frac 0.237 · eye_y_frac 0.443 · face_centre_x_frac 0.50 · min_face_px 90
tone:    white = face p98 + 0.02 · black = face p5 − 0.2 × (p98 − p5) · gamma 1.8
         sharpen 0.6 at 1 cell · tone blur 0.05 cell  (face tones read at one-cell scale, inside the face box)
outline: mask_smooth_px 9 (head) · body_smooth_px 28 below the chin, blended over 120 px
         outline_gap_px 2 · outline_width_px 6 · dots clipped to the same smoothed silhouette
```

### The steps

0. **Descreen.** In the original's own pixels: notch-filter any printed screen, then an edge-preserving blur.
0b. **Enhanced copy.** Align it to the original. Its green background gives the cut-out.
1. **Crop.** A similarity transform from the face landmarks: scale from the eye-to-mouth distance, the eye line at a fixed height, and the face box centred horizontally.
1b. **Blend.** 50% original, 50% aligned enhanced copy, in the frame.
2. **Tone.** Levels from the face's own tones, plus a gamma and an unsharp mask.
3. **Halftone.** A round-dot screen at 45°, rendered at 4× and averaged down for smooth dot edges.
4. **Figure mask.** The cut-out, smoothed: gently for the head (hair keeps its overall shape) and harder below the chin (clean shoulder curves). Holes are filled and only the largest piece is kept.
5. **Line.** A band 2–8 px outside the smoothed figure, from a distance transform, anti-aliased.
6. **Composite.** White with alpha only. Passes the STY-06 check on all three examples.

## How close it is (`out/measures.json`, at the owner's own framing, compared at 500 px)

| Example | Figure overlap (IoU) | Tone error (mean abs, 0–1) | Tone correlation | Dots across |
|---|---|---|---|---|
| Charles Fillmore | 0.97 | 0.071 | 0.987 | 110.5 |
| Emilie Cady | 0.90 | 0.053 | 0.967 | 110.5 |
| Ernest Holmes | 0.92 | 0.058 | 0.979 | 110.5 |

**Proposed thresholds for F-16 and TRI-08** (the code measures):

- figure overlap ≥ 0.85;
- tone error ≤ 0.08;
- dots across 110 ± 2;
- no STY-06 problems.

F-16 also checks that the recipe re-creates `out/*.png` from `fixtures/` within a small pixel tolerance.

## What's still different, and why

- **The cut-out decides the line.** Holmes's left shoulder and Cady's right side bulge, because the prototype's stand-in cut-out is two small public models merged. It struggles with a dark suit on a dark background. The production cut-out (Bria RMBG 2.0 or similar) should do better, and the draft check's "cut-out clean" criterion exists to catch it. **Risk for the trial:** include dark-on-dark originals.
- **The owner's portraits were each adjusted by hand** (different levels per image, finer dots and a heavier line on Cady). One recipe for every teacher (STY-05) can't match all three exactly. It matches Fillmore and Holmes most closely.

## Evidence for open questions

- **Q-05 (code-drawn line):** the owner's line is what code produces naturally: a thin band hugging a smoothed silhouette, with the dots clipped to it. The code line reproduces it at no cost and is the same every run. Recommendation: make the code line the default, and keep the image-model lines as trial contenders.
- **PIP-02 (minimum face size):** the owner's originals have face boxes 108–183 px wide, so `min_face_px` = 90.
- **PIP-04 (crop):** crop from 5 face landmarks. Eye-to-mouth distance is the scale because it holds steady when the head turns, unlike the distance between the eyes.

## Files

| Path | What |
|---|---|
| `recipe.py` | The recipe and its settings (reference implementation) |
| `common.py` | Loaders, the stand-in cut-out, the face detector used for measuring |
| `register.py`, `measure_dots.py`, `tune_tone.py` | How the owner's portraits were measured and the tone fitted |
| `make_fixtures.py` | Saves the model-dependent inputs (cut-outs, landmarks, registrations) to `fixtures/` |
| `run_examples.py` | Re-runs the recipe from `fixtures/` alone and writes `out/` |
| `test_enhance_mechanics.py` | Checks alignment, blending and the keyed cut-out with synthetic copies; writes `out/enhance-mechanics.json` |
| `prompts/` | Proposed prompts for every model step (D-20) |
| `out/board.png` | Original · owner's portrait · prototype at the owner's framing · prototype with automatic crop |
| `out/zoom.png` | Close-ups: owner's (left) vs prototype (right) |
| `out/descreen-compare.png` | Texture close-ups: owner's · 0.1.0 (no descreen) · 0.2.0 (descreen) |
| `out/*.png` | 1,000 × 1,000 masters (reference outputs for F-16) |

## Re-running

From the repo root, with Python 3.12+, NumPy, OpenCV and Pillow, run `python3 prototype/run_examples.py`. It needs only `fixtures/`.

`make_fixtures.py`, `register.py` and `tune_tone.py` also need the stand-in models. Those are kept out of the repo:

- `u2net_human_seg` and `isnet-general-use` from the rembg releases;
- SCRFD-500M from insightface's `buffalo_sc`, which is for research use only and is used here just to measure the examples.

The product uses its own cut-out provider and a permissively licensed face detector (YuNet).
