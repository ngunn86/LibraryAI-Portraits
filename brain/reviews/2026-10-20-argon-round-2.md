# Argon Notes: Plan & Autonomous Harness Readiness Review

**Reviewer:** Gemini 4 Argon (High)
**Date:** 2026-10-20
**Repo state reviewed:** `origin/main` at `08cb528` (consolidated requirements, architecture v2 for TypeScript/Railway, OpenAPI contract draft 4, 45 feature cards draft 2, and Python prototype 0.4.0)

---

## Executive Summary

Overall, the planning in `brain/` is exceptionally well-organized for an autonomous coding harness:
- **Strong foundations:** Retiring the model-drawn outline in favour of the deterministic code outline (`D-49`), proving the halftone/descreen/alignment mechanics in `prototype/` (`D-16`), isolating external network and model calls behind record/replay and stub clients (`F-06`, `F-17`), and proving the Railway deployment pipeline with a throwaway test first (`HT-01..HT-29`) eliminate the largest open-ended risks.
- **What will trip up an autonomous build harness right now:** Because the harness builds one feature card at a time (`F-01`..`F-48`) and grades each card strictly against its machine-checkable tests, **any contradiction between a feature card, the normative spec (`requirements.md`), the OpenAPI contract/samples, and the Python reference code (`prototype/`) will cause the harness to stall, fail a test, or bake in a bug.**

I found **19 concrete issues** across the plan and prototype (**6 blockers**, **8 major**, **5 minor**):
1. **6 Blockers (`argon-1` to `argon-6`):** Direct contradictions or impossibilities that will cause a feature card's tests or runtime pipeline to fail immediately (e.g., `F-11` / `architecture.md` running visual deduplication and pre-check damage ranking *before* downloading images or running the pre-check; sending 40+ MB raw LoC TIFFs to OpenRouter vision/image endpoints; reversed image order between `draftcheck.md` and `PIP-09`/`F-21`; `smooth_mask` deleting floating fragments before `PIP-19`/`F-15` checks for them; `F-02` ignoring `wikidata_qid`/`lcnaf_id` added to `authors.csv`; and `F-08` requiring existing birth/death years when searching Wikidata, which blocks `F-35` from enriching the ~110 undated teachers).
2. **8 Major Issues (`argon-7` to `argon-14`):** Bugs in the OpenCV.js port, API state transitions, and production trial workflow that will cause OOMs/timeouts on real LoC scans, WASM exceptions in OpenCV.js, broken `try_again` requests, or cache invalidation after the trial.
3. **5 Minor Issues (`argon-15` to `argon-19`):** Edge cases in `authors.csv` rename matching, `CC BY-SA 1.0` handling, face-hash collisions, OpenAPI/Zod parity in `F-03`, and card ordering.

Each point below follows the format in `brain/reviews/README.md` (`argon-1`..`argon-19`) with exact file/ID references and concrete replacement rules so Claude can merge them directly.

---

## Detailed Findings

### `argon-1` · Candidate pipeline ordering has a three-way chicken-and-egg impossibility
- **Refers to:** `architecture.md` ("Data flow for one teacher", lines 91–96), `SRC-07`, `PIP-01`, `PIP-02`, `PIP-15`, `PIP-16`, `PIP-18`, `PIP-20`, `F-11`, `F-23`
- **Severity:** `blocker`
- **Problem:**
  Look at the pipeline order in `architecture.md` (lines 92–96) and the boundary between `F-11` and `F-23`:
  ```text
  candidates by R1, R2, R3 (+ library try_link) → licence filter (SRC-02)
    → group copies of one photograph (PIP-20) → best copy per photograph (SRC-07)
    → choose for open slots: best-known first, then spread across life (PIP-16)
    → download original (SHA-256, rights log)
    → PRE-CHECK (Haiku)
  ```
  Three steps in this sequence depend on outputs produced by later steps:
  1. **`PIP-20` before download:** `PIP-20` (`F-42`, `F-43`) requires the image pixels (cropped face fingerprint, 600 px SIFT feature matching, and Sonnet vision tie-break). You cannot run `PIP-20` in `F-11` *before* downloading candidate image bytes.
  2. **`SRC-07` before `PRE-CHECK`:** `SRC-07` (`requirements.md` line 260) and `F-11` (`features.md` line 684) rank copies of one photograph by `(1) licence tier, (2) pixel count, (3) the pre-check's damage rating`. Yet `PRE-CHECK (Haiku)` runs *after* `F-11`, and `F-11` does not even list `F-18` (Pre-check) in its `Depends on`!
  3. **`PIP-16` before `PRE-CHECK`:** `PIP-16` chooses which 3 photographs fill the teacher's open slots using `PIP-18`'s approximate date (`source date`, or else `pre-check's age estimate + birth year`). If a candidate has no source date, its approximate date is unknown until `PRE-CHECK` runs; and if a chosen photograph fails `PRE-CHECK` (e.g., group photo, tiny face, heavy damage), slot selection must pick again.
- **Suggestion:**
  Define a single, non-circular step order in `architecture.md`, `SRC-07`, `PIP-01`, `F-11`, and `F-23`:
  1. **Gather & licence filter (`F-11`):** Query adopted sources (`R1`, `R2`, `R3`), classify licences (`SRC-02`), record refused rows in `candidates`, and merge exact `source + source_id` or file-URL duplicates.
  2. **Fetch candidate images & group copies (`F-11`):** Download candidate image bytes (up to a per-teacher candidate cap, e.g. 24, ordered by rule and pixel size; keep bytes in memory/temp cache and record `sha256` and dimensions in `candidates`, storing `original.<ext>` to the bucket only for kept portraits per `OUT-12`). Run `PIP-20` (`F-42` + `F-43`) to group candidates into `photographs`.
  3. **Order copies within each photograph (`SRC-07`, `F-11`):** Order copies by `(1) licence_tier ASC, (2) pixel_count DESC` (and `damage` if already pre-checked). The top copy is the photograph's primary candidate; if it later fails `PRE-CHECK` due to `heavy` damage, the next copy in the group may be tried.
  4. **Pre-check & choose for open slots (`F-23`):** In `F-23`, pre-check the best copy of candidate photographs (up to 12 pre-checks per teacher per run, `PIP-11`), getting `verdict`, `damage`, `medium`, `face_box`, and `estimated_age` (`PIP-18`). From the photographs that pass `PRE-CHECK`, `PIP-16` picks the open slots (`P18` first, then spread across life by `approx_date` and quality) and drafts them (up to 6 drafts per teacher per run).

---

### `argon-2` · Sending raw `original.<ext>` (40+ MB LoC TIFFs) to OpenRouter will fail
- **Refers to:** `PIP-02`, `PIP-03`, `PIP-09`, `PIP-13`, `OUT-05`, `OUT-11`, `F-18`, `F-19`, `F-21`, `prototype/prompts/precheck.md`, `enhance_keyed.md`, `cutout_keyed.md`, `draftcheck.md`
- **Severity:** `blocker`
- **Problem:**
  `F-10` chooses the largest available image link on the Library of Congress, which is frequently an uncompressed master TIFF of 30–150 MB (e.g., `portraits-api.sample.json` line 145 shows a 39.4 MB, `3200×4100` `tiff` as `original`).
  The prompts (`precheck.md`, `enhance_keyed.md`, `cutout_keyed.md`, `draftcheck.md`) and cards (`F-18`, `F-19`, `F-21`) instruct sending "the original" (or "the descreened original") to OpenRouter. OpenRouter vision and image-editing endpoints (Anthropic, Google, OpenAI) do **not** accept `image/tiff` and reject base64 payloads above provider size limits (5–20 MB).
- **Suggestion:**
  Specify in `architecture.md`, `PIP-02`, `PIP-13`, `F-18`, `F-19`, and `F-21` that:
  1. `original.<ext>` is stored byte-for-byte in the bucket (`OUT-11`), but immediately decoded by `sharp` to sRGB (`src/imaging/io.ts`).
  2. Every OpenRouter call that takes the original image (`precheck`, `cutout_keyed`, `draftCheck`) sends the downscaled PNG viewing copy (`original-view.png`, $\le 1600$ px on the long side, 8-bit sRGB PNG), and `enhance_keyed` sends the descreened image encoded as 8-bit sRGB PNG at $\le 1600$ px on the long side (and `same_photo` sends 800 px PNG/JPEG as already noted in `same_photo.md`).

---

### `argon-3` · Image order in `PIP-09` and `F-21` is reversed relative to `draftcheck.md`, and dark page RGB is missing from settings
- **Refers to:** `PIP-09` (`requirements.md` line 494), `F-21` (`features.md` line 646), `prototype/prompts/draftcheck.md` (lines 3, 7), `prototype/prompts/compare.md` (line 3), `prototype/common.py` (line 8)
- **Severity:** `blocker`
- **Problem:**
  1. **Reversed image order:** `prototype/prompts/draftcheck.md` explicitly states:
     > `Send, in this order: (1) the original photograph; (2) the draft portrait on the library's dark page colour; (3)–(5) the owner's three example portraits on the same page colour.`
     > `Image 1 is a historical photograph. Image 2 is a white dot (halftone) portrait made from it. Images 3–5 show the house style...`
     However, `PIP-09` (`requirements.md` line 494) and `F-21` (`features.md` line 646) state:
     > `The request carries the draft on a dark page, the original and the three examples.`
     If the harness builds `F-21` following `F-21`'s check text (`[draft, original, ex1, ex2, ex3]`), Sonnet will evaluate the original photograph as "Image 2" and fail every draft.
  2. **Missing dark page RGB setting:** Both `draftcheck.md` and `compare.md` require compositing transparent PNG portraits onto `"the library's dark page colour"` before sending them to the vision model. In `prototype/common.py` (line 8), this is `PAGE = (28, 30, 38)`, which is not in `prototype/recipe.py`'s `SETTINGS` and is not mentioned in `F-01` or `F-21`.
- **Suggestion:**
  - In `PIP-09` and `F-21`, change the order to match `draftcheck.md`: `(1) the original (viewing copy), (2) the draft on the dark page colour, and (3)–(5) the three example targets on the same dark page colour`.
  - Add `checkPageRgb: [28, 30, 38]` (from `prototype/common.py`'s `PAGE`) to `src/config/settings.ts` and cite it in `F-21`.

---

### `argon-4` · `PIP-19` / `F-15` "floating fragment" check can never trigger if run after `smooth_mask`
- **Refers to:** `PIP-19` (`requirements.md` lines 592–600), `F-15` (`features.md` lines 485–494), `prototype/recipe.py` (`smooth_mask`, lines 188–191)
- **Severity:** `blocker`
- **Problem:**
  `PIP-19` states:
  > `Before the draft check, code refuses a draft whose figure (inside the outline, at 1,000 px) breaks any of these: ... the largest connected piece holds at least 98% of it`
  And `F-15`'s check states:
  > `Fixtures with a floating fragment, a figure cut off above the shoulders, and a full square are each refused, naming the limit.`
  However, in `prototype/recipe.py` (lines 188–191), `smooth_mask` **already deletes all connected components except the single largest piece**:
  ```python
  n, lab, stats, _ = cv2.connectedComponentsWithStats(b, 8)
  if n > 1:
      keep = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
      b = (lab == keep).astype(np.uint8)
  ```
  If the harness ports `smooth_mask` faithfully from `recipe.py` and then runs `PIP-19` on the resulting smoothed figure mask (`fig`), any floating fragment in the fixture has already been silently removed by `smooth_mask`, so the largest connected piece of `fig` is 100% and the `F-15` floating-fragment test will fail! Conversely, if the agent removes the largest-component filter from `smooth_mask` to make `F-15` pass, it changes the recipe behavior.
- **Suggestion:**
  Specify in `PIP-19` and `F-15` that the connected-piece check (`largest_piece_area / total_foreground_area >= 0.98`) is measured on the cropped binary cut-out mask `(Mc > 0.5)` **at the start of `smooth_mask`, before `smooth_mask` discards non-maximal components** (while the 35–80% area share, face-box containment, and $\ge 40\%$ bottom-edge contact are measured on the smoothed figure mask `fig`).

---

### `argon-5` · `authors.csv` reader (`F-02`, `IN-12`) does not read `wikidata_qid` or `lcnaf_id` added by the owner
- **Refers to:** `IN-01`, `IN-02`, `IN-04`, `IN-12`, `IN-13`, `D-45`, `F-02`, `F-31`, `F-35`
- **Severity:** `blocker`
- **Problem:**
  `D-45`, `IN-04`, `IN-13`, and `F-35` establish the workflow for unidentified teachers: `F-35` exports a CSV of suggested additions (`wikidata_qid`, `lcnaf_id`, `dates`) for `authors.csv`, and skipped teachers wait `"until the owner adds an id or dates to authors.csv"` (`D-45`, `portraits-api.sample.json` line 52). Furthermore, `Teacher.ids_from` in `portraits-api.openapi.json` (line 986) has `"enum": ["list", "resolved_by_tool", "none"]` (`"where wikidata_qid and lcnaf_id came from: the authors list, or found by the tool"`).
  However, `IN-12` (`requirements.md` lines 150–154) and `F-02` (`features.md` lines 202–217) only map `name`, `aliases`, `dates`, `status`, `stream`, and `tier` from `authors.csv`—they never mention reading optional `wikidata_qid` and `lcnaf_id` columns from `authors.csv` or validating their patterns (`^Q[1-9][0-9]*$`, `^n[a-z]?[0-9]+$`).
- **Suggestion:**
  Update `IN-02`, `IN-12`, `F-02`, and `F-31` so that:
  - `src/teachers/authors.ts` (`F-02`) reads optional `wikidata_qid` and `lcnaf_id` columns from `authors.csv` when present (setting `ids_from = "list"` when either is provided on the row).
  - `IN-02` / `F-02` refuses a row with a malformed `wikidata_qid` (not matching `^Q[1-9][0-9]*$`) or malformed `lcnaf_id` (not matching `^n[a-z]?[0-9]+$`), naming the row and reason.

---

### `argon-6` · `F-08` and `SRC-06b` require teachers to already have years before searching Wikidata, blocking `F-35` for the ~110 undated teachers
- **Refers to:** `IN-13`, `SRC-06` (`requirements.md` line 251), `D-45`, `F-08` (`features.md` line 307), `F-35`
- **Severity:** `blocker`
- **Problem:**
  In `collection/authors.csv`, ~110 of the 182 active authors have no `dates` and no `wikidata_qid`. `D-45` and `IN-13` solve this by looking up the teacher in both Wikidata and the LoC Name Authority (`id.loc.gov`) and filling both their IDs and their life dates when both sources agree on the person and both years.
  However, `SRC-06b` (`requirements.md` line 251) and `F-08` (`features.md` line 307) still carry the earlier `Q-01` wording:
  > `F-08: Search: one unique human with the name or an alias and both years is returned as a candidate; two matches, none, or a year mismatch return nothing.`
  If `F-08`'s search function requires the teacher to *already* have `born` and `died` to match on Wikidata, then for the ~110 teachers with `born = null, died = null`, `F-08` will return nothing and `F-35` will never be able to compare Wikidata's years against `id.loc.gov`'s years!
- **Suggestion:**
  Update `SRC-06b`, `F-08`, and `F-35`:
  - In `F-08`, searching Wikidata by a teacher's `name` and `aliases` filters to humans (`P31 = Q5`) whose label/alias matches (normalised) and whose birth/death years (`P569`, `P570`) are both present on Wikidata and compatible with any year(s) the teacher already has (`born` and/or `died`, if known). If **one unique human** on Wikidata matches, `F-08` returns that candidate with its `qid`, `born`, `died`, and `P244` (`lcnaf_id`).
  - In `F-35`, `enrich.ts` compares that Wikidata candidate with the `id.loc.gov` authority match for the teacher: if both independent sources identify one person and agree on **both birth and death years** (and agree with any year given in `authors.csv`), store `wikidata_qid`, `lcnaf_id`, `born`, and `died` (`ids_from = "resolved_by_tool"`, `dates_from = "wikidata_and_loc"` if dates were missing); otherwise list as a suggestion for the owner.

---

### `argon-7` · Full-resolution `descreen` (`DFT` + `d=-1` bilateral filter) and un-cached `_threshold_map` will stall or OOM on large LoC originals in WebAssembly
- **Refers to:** `PIP-05`, `F-13`, `F-14`, `F-39`, `architecture.md` ("Porting risks", line 183), `prototype/recipe.py` (lines 59–115, 159–179, 277)
- **Severity:** `major`
- **Problem:**
  1. **Bilateral filter & DFT scaling with image resolution:** In `prototype/recipe.py` (lines 112–113), `descreen` runs on the full-resolution original `L`:
     ```python
     sigma_space = max(blur_cells * cell_px_in_original, 0.5)
     out = cv2.bilateralFilter(np.clip(out, 0, 1), -1, s["edge_blur_color"], sigma_space)
     ```
     On the owner's 300 px wide examples, `cell_px_in_original` is ~3 px (`sigma_space ≈ 1.8`, kernel diameter `d = 11`), which takes milliseconds.
     On a $3200 \times 4100$ LoC scan (`portraits-api.sample.json`), `cell_px_in_original` is ~36.4 px. With `descreen_blur_cells = 0.6`, `sigma_space = 21.8` px. Passing `d = -1` to OpenCV's `bilateralFilter` sets the kernel diameter to $2 \cdot \text{round}(3 \cdot \sigma_{\text{space}}) + 1 = 131$ px! A $131 \times 131$ bilateral filter on a 13.1-megapixel image requires $3200 \times 4100 \times 131^2 \approx 2.25 \times 10^{11}$ operations—taking **several minutes per portrait** in single-threaded WebAssembly, while a 2D complex FFT at $3200 \times 4100$ requires hundreds of MB of contiguous WASM heap.
  2. **Recomputing `_threshold_map` at $4000 \times 4000$:** In `recipe.py` (lines 159–178), `_threshold_map(1000, 4, pitch, 45)` allocates nine $4000 \times 4000$ `float32` arrays (~64 MB each = ~576 MB total) on every `make_master` call, even though the output depends *only* on `(size_px, supersample, dots_across, grid_angle_deg)` and is identical for every portrait under the same recipe.
- **Suggestion:**
  1. **Cap working resolution before `descreen`:** In `PIP-05`, `F-13`, and `architecture.md`, specify that if the original's long side exceeds `maxWorkingPx` (e.g., `2000` px, which is still $2\times$ the $1000$ px master frame), `L` (and the working RGB image/landmarks) is downscaled with `INTER_AREA` to `2000` px on the long side before `descreen`, while `original.<ext>` is kept at full size in the bucket. (The owner's 3 examples are 250–340 px, so `F-16` parity is completely unaffected.)
  2. **Cache `_threshold_map`:** Specify in `F-14` that `halftone.ts` computes the $4000 \times 4000$ `Float32Array` threshold map **once** per `(sizePx, supersample, dotsAcross, gridAngleDeg)` in a single loop (without allocating 9 full-size intermediate arrays) and caches it in memory across portraits.

---

### `argon-8` · OpenCV.js porting traps in `detect_screen`, `descreen`, `YuNet`, and offline fixture availability
- **Refers to:** `architecture.md` ("Stack" and "Porting risks"), `F-39`, `F-12`, `F-13`, `prototype/recipe.py` (lines 64–73, 110), `prototype/common.py` (lines 60–92)
- **Severity:** `major`
- **Problem:**
  Four concrete traps will hit the harness in `F-39`, `F-12`, and `F-13`:
  1. **`cv.medianBlur` throws on `float32` for `ksize = 15`:** `detect_screen` (`recipe.py` line 69) calls `scipy.ndimage.median_filter(M, size=15)` on a `float32` log-spectrum array `M`, and `maximum_filter(D, size=5)` on `float32` `D`. In OpenCV C++ / OpenCV.js, `cv.medianBlur` **only supports `CV_32F` for `ksize` 3 or 5**; calling `cv.medianBlur(M, dst, 15)` on a `CV_32F` Mat throws an OpenCV assertion exception!
  2. **`cv.idft` scaling:** Unlike `np.fft.ifft2`, OpenCV's `cv.idft` does not divide by $W \times H$ unless `cv.DFT_SCALE` is passed (`cv.idft(src, dst, cv.DFT_SCALE | cv.DFT_REAL_OUTPUT)`).
  3. **YuNet bounding-box format & ONNX decoding:**
     - `prototype/common.py` and `recipe.py` expect `face.box` as `[x0, y0, x1, y1]` (`x_min, y_min, x_max, y_max`). YuNet outputs `[x, y, w, h]` (`x_min, y_min, width, height`). Passing `[x, y, w, h]` into `crop_transform` (`cx = (bx[0] + bx[2]) / 2`) or `tone_to_coverage` (`x0:x1`) without converting `x1 = x + w, y1 = y + h` silently corrupts horizontal centering and tone levels.
     - Standard `@techstark/opencv-js` does not include `cv.FaceDetectorYN`. When falling back to `onnxruntime-node` (`F-39`), note that `face_detection_yunet_2023mar.onnx` outputs 12 anchor-free stride tensors (`cls_8/16/32`, `obj_8/16/32`, `bbox_8/16/32`, `kps_8/16/32`), whereas `prototype/common.py` (lines 62–92) has the tensor decoder for SCRFD (`det_500m.onnx`), not YuNet.
  4. **Offline files needed in `F-39` and `F-12`:** Both `F-39` and `F-12` have `Live calls: none` (offline tests refuse all network access), yet `F-12` requires the committed YuNet `.onnx` model file and `F-39` requires `prototype/export_parity.py`'s reference outputs. Neither exists in the repo yet, and `prototype/common.py` line 60 points to an ephemeral `/tmp/claude-0/...` path for its face model.
- **Suggestion:**
  - Before freezing `plan-v1` (in Phase 0), commit the YuNet ONNX file (`face_detection_yunet_2023mar.onnx`, ~230 KB, MIT) and a small Python YuNet runner + `prototype/export_parity.py` reference outputs directly into the repo so the harness has both the working Python YuNet tensor decoder to port and the committed reference files while offline.
  - Document in `architecture.md` / `F-39` / `F-13`:
    - For `median_filter(M, size=15)` on `float32`: either linearly scale `M` to `CV_8U` (`0..255` between `M.min()` and `M.max()`), run `cv.medianBlur(M_u8, dst_u8, 15)`, and scale back to `float32`, or compute the $15 \times 15$ median directly in a typed-array sliding window (since the FFT spectrum is small or downsampled).
    - For `maximum_filter(D, size=5)` on `float32`: use `cv.dilate` with `cv.getStructuringElement(cv.MORPH_RECT, new cv.Size(5, 5))`.
    - For `cv.idft`: always pass `cv.DFT_SCALE | cv.DFT_REAL_OUTPUT`.
    - In `F-12`: explicitly state that `face.ts` converts YuNet's `[x, y, w, h]` to `box: [x, y, x + w, y + h]`.

---

### `argon-9` · Undefined fallback crop equations when YuNet finds no face, plus normalized vs pixel `face_box` mismatch
- **Refers to:** `PIP-02`, `PIP-04`, `F-12` (`features.md` line 443), `F-18`, `prototype/prompts/precheck.md` (line 12), `prototype/recipe.py` (lines 118–130, 309–312)
- **Severity:** `major`
- **Problem:**
  1. **Coordinate units (`0..1` vs pixels):** `precheck.md` (line 12) returns `"face_box": [x0, y0, x1, y1]` as **fractions `0..1` of image width and height**, whereas `PIP-02` (`minFacePx = 90` source pixels wide) and `recipe.py` (`crop_transform`, `tone_to_coverage`, `local_drift`) use **source pixel coordinates**.
  2. **Missing landmark estimation formula from `face_box`:** `PIP-04` and `F-12` say:
     > `With no face found, the pre-check's box is used and the eye line is estimated from it (synthetic case).`
     However, `crop_transform` and `make_master` in `recipe.py` require 5 landmarks `kps` (`left_eye`, `right_eye`, `nose`, `left_mouth`, `right_mouth`) to compute `eye`, `mouth`, `em = ||mouth - eye||` (which sets the zoom scale!), and `chin_y`. Neither `recipe.py` nor `requirements.md` specifies how to derive `kps` (or `eye_y`, `mouth_y`, and `chin_y`) from a bounding box `[x0, y0, x1, y1]` when YuNet returns `None`.
- **Suggestion:**
  - In `PIP-02` / `F-18`: state that `precheck.ts` multiplies the normalized `face_box` `[fx0, fy0, fx1, fy1]` by `[width, height, width, height]` to obtain pixel coordinates `[x0, y0, x1, y1]`, and checks `(x1 - x0) >= settings.minFacePx` (`90`) in code (since `precheck.md` itself does not know `minFacePx` or image pixel dimensions!).
  - In `PIP-04` / `F-12`: define the exact synthetic 5-landmark fallback from a pixel `face_box` `[x0, y0, x1, y1]` with width $w = x_1 - x_0$, height $h = y_1 - y_0$, center $c_x = (x_0 + x_1)/2$ (measured on the 3 example fixtures where `eye_y ≈ y0 + 0.38*h` and `mouth_y ≈ y0 + 0.78*h`, so `em = 0.40*h`):
    - `left_eye = [cx - 0.18 * w, y0 + 0.38 * h]`
    - `right_eye = [cx + 0.18 * w, y0 + 0.38 * h]`
    - `nose = [cx, y0 + 0.58 * h]`
    - `left_mouth = [cx - 0.15 * w, y0 + 0.78 * h]`
    - `right_mouth = [cx + 0.15 * w, y0 + 0.78 * h]`
    With those 5 synthetic landmarks, `crop_transform` and `make_master` work unchanged without a separate code path.

---

### `argon-10` · `mask.png` coordinate space and `cutout_keyed` fallback alignment
- **Refers to:** `PIP-03`, `PIP-13`, `OUT-11` (`requirements.md` lines 702–705), `F-19`, `F-24`, `F-30`, `prototype/recipe.py` (lines 282–304)
- **Severity:** `major`
- **Problem:**
  1. **`mask.png` size and position:** `OUT-11` requires `mask.png` to be `"8-bit grey, white is the person, at the original's size and position"` (and `portraits-api.sample.json` lines 146, 218, 230 shows `original` at `3200×4100`, `enhanced` at `2048×2624`, and `mask` at `3200×4100`). However, in `recipe.py` (lines 228, 297), `Em = key_mask(E)` is at `enhanced.png`'s size and shifted position (`He × We`), and is warped directly to the $1000 \times 1000$ portrait frame (`T`), never to the original's `(w, h)` frame.
  2. **Fallback `cutout_keyed` alignment:** When `PIP-03` falls back to `cutout_keyed.md` (an OpenRouter image-editing call), the image model may also return an image at its own resolution (`1024×1024` or `2048×2624`) or with a slight shift/scale.
  3. **When the `enhance` call itself fails:** `OUT-11` (line 705) and `F-24` (line 707) require that when the `enhance` call fails completely, the portrait still publishes with the other 7 files (`enhanced.png` omitted, `enhanced_used: false`). That requires `PIP-03` / `F-19` to invoke the `cutout_keyed` fallback whenever the `enhance` call errors out, not only when the mask fails `PIP-19` or safeguards refuse the copy.
- **Suggestion:**
  - In `F-30` (`align.ts`): when extracting a mask `Em` from any green-screen model image (whether from `enhance_keyed` or `cutout_keyed`), warp `Em` into the original's `(w, h)` coordinate space using the aligned transform `A` (`cv.warpAffine(Em, A, (w, h), INTER_LINEAR | WARP_INVERSE_MAP, BORDER_CONSTANT, 0)`), and save that `(w, h)` 8-bit greyscale image as `mask.png`.
  - In `PIP-03` and `F-19`: explicitly state that `cutout_keyed` is called as the fallback when (a) the `enhance` call fails/errors, (b) `enhance` is refused by alignment/drift safeguards, or (c) `enhance`'s mask fails `PIP-19`; and that `cutout_keyed`'s output is aligned to the original via `align_enhanced` to produce `mask.png`.

---

### `argon-11` · Outbound allowlist is missing media/CDN hosts, redirect validation, and human `try_link` URL mapping
- **Refers to:** `SRC-01`, `SRC-04`, `IN-06`, `F-06`, `F-45`
- **Severity:** `major`
- **Problem:**
  1. **Media/CDN subdomains:** `SRC-01` and `F-06` enforce an strict hostname allowlist before any request leaves the process. Searching uses `www.wikidata.org`, `commons.wikimedia.org`, `www.loc.gov`, `id.loc.gov`, and `api.wellcomecollection.org`, **but downloading image files and following redirects hits additional hosts**:
     - Commons files live on `upload.wikimedia.org`;
     - LoC image files live on `tile.loc.gov` (and `loc.gov` redirects to `www.loc.gov`);
     - Wellcome IIIF images live on `iiif.wellcomecollection.org`.
     If any of these media hosts is missing from `settings.ts`, `F-06` will block every image download in `F-11`/`F-27`!
  2. **Redirect bypass in `fetch` (`undici`):** By default, Node's `fetch` (`redirect: "follow"`) follows HTTP 301/302 redirects internally without re-running wrapper checks. A redirect to an unallowed host would bypass `F-06` unless `fetch` uses `redirect: "manual"` and validates each `Location` target against the allowlist.
  3. **Human-pasted `try_link` URLs (`SRC-04`, `F-45`):** When an admin pastes a Wellcome link from a browser, the URL is `https://wellcomecollection.org/works/<id>` (on `wellcomecollection.org`, not `api.wellcomecollection.org`). Similarly, Commons links may be `https://commons.wikimedia.org/wiki/File:...` or `https://upload.wikimedia.org/...`, and LoC links may be `https://www.loc.gov/item/<id>/` or `https://www.loc.gov/pictures/item/<id>/`.
- **Suggestion:**
  - In `SRC-01` and `F-06`: list the exact allowed hostnames in `settings.ts`:
    `www.wikidata.org`, `commons.wikimedia.org`, `upload.wikimedia.org`, `www.loc.gov`, `loc.gov`, `tile.loc.gov`, `id.loc.gov`, `api.wellcomecollection.org`, `iiif.wellcomecollection.org`, `openrouter.ai`, `api.github.com`, plus the environment's bucket hostname from `process.env`.
  - In `F-06`: require `src/net/client.ts` to use `redirect: "manual"` and check every redirect target's hostname against the allowlist before following it.
  - In `SRC-04` and `F-45`: specify that `try_link` parses the pasted URL without fetching the HTML page, accepting:
    - Commons: `commons.wikimedia.org/wiki/File:<title>` or `upload.wikimedia.org/...` $\rightarrow$ Commons `File:<title>`;
    - LoC: `(www.)loc.gov/(pictures/)?item/<id>` or `loc.gov/resource/<id>` $\rightarrow$ LoC item `<id>`;
    - Wellcome: `(api.)?wellcomecollection.org/(catalogue/v2/)?works/<id>` $\rightarrow$ Wellcome work `<id>`.

---

### `argon-12` · Contradictions in `try_again` sample payload, `note_kind.md` prompt, and `web` vs `worker` boundary
- **Refers to:** `IN-06`, `OUT-07`, `OUT-11`, `F-45`, `brain/contracts/portraits-api.sample.json` (lines 388–419), `prototype/prompts/note_kind.md`
- **Severity:** `major`
- **Problem:**
  1. **`portraits-api.sample.json` violates `OUT-07` and `OUT-11`:** In `portraits-api.sample.json` (lines 406–419), the completed `try_again` request has `"portrait_id": "charles-fillmore-2"`, `"status": "done"`, and `"result_portrait_id": "charles-fillmore-2"`.
     Per `OUT-07` (`requirements.md` lines 674–676) and `OUT-11` (`requirements.md` line 693), a remake on a library `try_again` creates a **new** portrait ID (e.g., `"charles-fillmore-3"`) and marks `"charles-fillmore-2"` as `status: "replaced", replaced_by: "charles-fillmore-3"`. Having `result_portrait_id` equal the input `portrait_id` in the sample file will mislead the harness into overwriting `charles-fillmore-2` in place.
  2. **`note_kind.md` misclassifies cut-out errors as `"crop"` or `"outline"`:** In `portraits-api.sample.json` (line 393), the sample `try_again` note is `"The line cuts off the left ear."` In the pipeline, a cut-off ear or shoulder is a **cut-out mask defect** from the AI green-screen copy (`PIP-03`), which a fresh AI copy *can* fix! However, `prototype/prompts/note_kind.md` tells Haiku:
     > `"crop" covers framing, zoom, position, head size, cutting off part of the head or shoulders. "outline" covers the white line around the figure.`
     With that prompt, Haiku will classify `"The line cuts off the left ear"` (or any mask/cut-out complaint) as `"outline"` or `"crop"`, causing the tool to **refuse** the request instead of re-running the AI cut-out/enhancement!
  3. **Where `noteKind.ts` runs (`F-45` vs `F-23`/`F-25`):** `portraits-api.openapi.json` (line 1754) and `IN-06` say `POST /api/v1/requests` accepts a `try_again` with `202` (`queued`), and the worker classifies the note with Haiku (`note_kind.md`) and transitions the request to `status: "refused"` if it asks to change the recipe's crop/outline. Yet `F-45` (the API card) includes `src/models/noteKind.ts` and checks the `refused` outcome without mentioning the worker/request runner.
  4. **Worker failure outcome on requests:** Neither `IN-06` nor `F-45` specifies what `Request.status` becomes when a valid `try_link`, `try_again`, or `another_original` is processed by the worker, **and the candidate/remake fails** the licence check, pre-check, or draft check (or no more candidates exist).
- **Suggestion:**
  - In `portraits-api.sample.json` (line 416): change `"result_portrait_id"` on `request` from `"charles-fillmore-2"` to `"charles-fillmore-3"`.
  - In `prototype/prompts/note_kind.md` and `IN-06`: clarify that **cut-out / silhouette errors** (an ear, hair, or shoulder cut off by the mask/line, or background left inside the outline) count as `"restoration"` because a fresh AI keyed copy produces a new cut-out mask; `"crop"` is only for requests to change zoom, centering, or framing scale, and `"outline"` is only for requests to change the line's style, thickness, or colour.
  - In `IN-06` and `F-45`: state that `POST /api/v1/requests` validates the request schema and source host (404 / 422), writes the `requests` row (`status: "queued"`), queues a high-priority job, and returns `202`; the worker then runs `noteKind` / the pipeline and sets `status: "done"` (with `result_portrait_id`) if a portrait was published, or `status: "refused"` (with `refused_reason` explaining why—e.g. crop/outline note, refused licence, failed pre-check/draft-check, or no remaining candidates—and `result_portrait_id: null`), emitting a `request` entry in the change feed.

---

### `argon-13` · Contradiction on `replaced` status (`PIP-17`/`F-48` vs `OUT-07`), missing `main` transfer rules, and undefined `PIP-16` spread formula
- **Refers to:** `PIP-16`, `PIP-17` (`requirements.md` line 572), `OUT-07` (`requirements.md` line 676), `IN-07`, `F-23`, `F-45`, `F-48`, `brain/contracts/portraits-api.openapi.json` (line 1089)
- **Severity:** `major`
- **Problem:**
  1. **Contradiction on what `replaced` means:**
     - `OUT-07` (`requirements.md` line 676), `portraits-api.openapi.json` (line 1089), and `handoffs/library-api.md` (line 35) all state:
       > `replaced always means "superseded by another portrait of the same photograph".`
     - Yet a proposed bullet in `PIP-17` (`requirements.md` line 572) and `F-48` (`features.md` line 821) states:
       > `when all slots are full, a new photograph that ranks above one of them is offered as a draft with replaces set.`
       When the library approves a portrait with `replaces` set, `IN-07` sets the old portrait's status to `replaced`—which would mark a portrait of Photograph A as `replaced` by a portrait of a *different* Photograph B, violating `OUT-07` and the API contract!
  2. **What happens to `main` (`main_portrait_id`) on swap or turn-down (`IN-07`, `F-45`, `F-48`):**
     - If portrait `charles-fillmore-1` is `approved` and `main: true`, and the library approves a better copy `charles-fillmore-4` (`replaces: "charles-fillmore-1"`), `charles-fillmore-1` becomes `replaced`. Does `charles-fillmore-4` inherit `main: true` (and `teacher.main_portrait_id = "charles-fillmore-4"`) while `charles-fillmore-1.main` becomes `false`? If not specified, either a `replaced` portrait stays `main: true` or the teacher loses their main portrait on a quality upgrade.
     - Similarly, if an `approved` portrait with `main: true` is turned down (`turn_down` is allowed on `waiting` or `approved` portraits per OpenAPI line 1614), `main` must be set to `false` and `teacher.main_portrait_id` set to `null`.
  3. **Deterministic algorithm for `PIP-16` ("spread across the teacher's life"):**
     `PIP-16` says: `(1) P18 first, (2) then the best quality, spread across the teacher's life, by approximate date (PIP-18)`. Without a concrete tie-breaking/selection rule, the harness has to invent how date distance trades off against licence tier and pixel count.
- **Suggestion:**
  1. **Resolve the `replaced` contradiction:** Either drop the proposed "different photograph when all slots are full" bullet from `PIP-17` and `F-48` (so monthly re-search of full teachers per `D-59` only looks for *clearly better copies of their existing photographs*, keeping `replaces` and `replaced` strictly for the same photograph as `D-40` and `OUT-07` state; if an admin wants a different photograph when 3 are full, they send `another_original` or `try_link`), **or** update `OUT-07` and `portraits-api.openapi.json` line 1089 so `replaced` means "superseded by a replacement portrait (`replaces`)". Dropping the proposed bullet in `PIP-17`/`F-48` is simpler and matches `D-40`, `D-59`, and `OUT-07`.
  2. **Specify `main` invariants in `IN-07` and `F-45`:** Only an `approved` portrait may have `main = true`. When a portrait with `replaces` is approved and the portrait it replaces had `main = true`, `main = true` transfers to the new portrait (`main = false` on the old one, `teacher.main_portrait_id` updated). When a portrait with `main = true` is turned down, `main` becomes `false` and `teacher.main_portrait_id` becomes `null`.
  3. **Give `PIP-16` an explicit greedy rule:** Quality order of photographs is `(licence_tier ASC, damage_rank ASC, pixel_count DESC)`. Slot 1 takes `best_known` (`P18`) if present, else the highest-quality photograph. Each remaining slot takes the highest-quality dated photograph whose `approx_date` is at least `minSpreadYears` (`10` years) away from every already-chosen dated photograph for that teacher; if none is $\ge 10$ years away, take the dated photograph with the largest minimum year distance (ties broken by quality); if no dated photographs remain, take the highest-quality undated photograph.

---

### `argon-14` · Production trial isolation (`F-28`), `step_cache` invalidation on `recipeVersion` bump (`TRI-06`), `railway run` networking, and `first_pass` spend tracking (`RUN-04`)
- **Refers to:** `RUN-03`, `RUN-04`, `TRI-05`, `TRI-06`, `IN-09`, `F-04`, `F-17`, `F-25`, `F-28`, `F-29`, `F-47`
- **Severity:** `major`
- **Problem:**
  1. **Where trial contenders live in production (`F-04`, `F-28`, `TRI-05`, `IN-09`):** `TRI-06` and `F-28` run the trial in **production** before the release so `step_cache` in production's database is warm for `F-29` and `F-47`. However:
     - The trial includes the owner's 3 unknown-source examples (`D-13` / `IN-09`: never published), plus ~20 survey originals × 3 enhance models × 2 (with and without blend).
     - `TRI-05` requires all of them to be viewable on `/admin/trial` ("Trial drafts are never shown to the library").
     - Yet `F-04` (`src/db/schema.ts`) has **no `trial_runs` or `trial_items` table**! If `F-28` writes trial contenders into `portraits` and `candidates`, it will either expose them in `/api/v1/portraits` and `/api/v1/changes`, consume `<teacher_id>-<n>` portrait IDs, or pollute the permanent `candidates` rights log with the 3 unknown-source examples.
  2. **`step_cache` invalidation when `F-28` bumps `recipeVersion` (`RUN-03`, `TRI-06`, `F-04`):** `F-04` (line 149) says the `step_cache` key is `(original_sha256, step, model, settings_hash)`. `F-28` (line 953) writes the trial winner into `src/config/settings.ts` **with a new `recipeVersion`** before `F-29` and `F-47` run. If `settings_hash` in `step_cache` hashes `recipeVersion` or the whole settings block rather than *only that step's prompt version*, then bumping `recipeVersion` at the end of `F-28` will invalidate 100% of the trial's cached calls, causing `F-29` and `F-47` to miss the cache and pay twice!
  3. **`railway run` vs internal Railway Postgres hostname:** `F-38`, `F-27`, `F-28`, and `architecture.md` use `railway run portraits ...` from the harness (WSL). `railway run` runs the process **locally on WSL** while injecting the Railway environment's variables. On Railway, `DATABASE_URL` uses the private network hostname (`postgres.railway.internal`), which does not resolve outside Railway's network unless `DATABASE_PUBLIC_URL` is used. Conversely, if a command runs inside the Railway container via `railway ssh`, it cannot edit and git-commit `src/config/settings.ts` in the local WSL checkout (`F-28`).
  4. **Tracking the multi-night `$100` first-pass cap (`RUN-04`, `D-59`, `F-17`, `F-25`):** `RUN-04` states that the first full run is capped at `$100` across as many nights as it takes until the queue first empties (or `$100` is reached), with no `$10` night cap during it and its spend excluded from the `$30` monthly cap. Without an explicit schema field in `F-04`, `F-17` (Phase 4) and `F-25` (Phase 5) will not agree on how to query whether the first pass is active or which `spend` rows belong to the first pass vs the monthly cap vs the `$27`/`$3` trial sub-budgets.
- **Suggestion:**
  1. **Add `trial_items` to `F-04`:** Add a `trial_items` table in `F-04` (storing `trial_run_id`, `label`, `is_example`, `model`, `blend_used`, `scores_json`, `cost_usd`, and bucket keys under `trial/<trial_run_id>/...`). `F-28` writes only to `step_cache`, `spend`, `runs`, and `trial_items`—never touching `portraits`, `candidates`, or `changes`.
  2. **Scope `step_cache`'s `settings_hash` per step (`F-04`, `F-17`):** Specify in `F-04` that `settings_hash` in `step_cache` hashes **only the step's own prompt text/version** (plus `note` if a `try_again` note was included), never `recipeVersion` or unrelated settings.
  3. **`DATABASE_PUBLIC_URL` fallback for CLI (`F-01`, `F-36`):** In `src/config/env.ts`, have CLI commands (`src/cli.ts`) connect using `DATABASE_PUBLIC_URL ?? DATABASE_URL` so `railway run portraits ...` works seamlessly from WSL (including when `F-28` runs `railway run portraits trial`, updates local `src/config/settings.ts`, and commits it).
  4. **Explicit `spend.budget` and `first_pass_state` (`F-04`, `F-17`, `F-25`):**
     - Give `spend` a `budget` column: `'trial' | 'trial_examples' | 'first_pass' | 'regular'`.
     - Store `first_pass_state: 'not_started' | 'active' | 'done'` in `app_settings`. `F-47` sets it to `'active'` when enabling the production schedule; when the worker sees the queue empty while `'active'` (or when total `'first_pass'` spend reaches `$100`), it sets `first_pass_state = 'done'`. Monthly `$30` cap queries sum only `budget = 'regular'`.

---

### `argon-15` · Author rename matching rule in `F-31` is unspecified
- **Refers to:** `IN-12` (`requirements.md` line 156), `F-31` (`features.md` line 250)
- **Severity:** `minor`
- **Problem:**
  `IN-12` and `F-31` require that `"Renaming an author keeps the teacher_id."` Because `library-pipeline`'s `collection/authors.csv` has no `author_id` column (only `name`, `aliases`, `dates`, `status`, `stream`, `tier`), the sync module needs a deterministic rule to distinguish a renamed author from one author leaving the list and another joining (and must not match by CSV row number, which breaks if rows are inserted or reordered).
- **Suggestion:**
  Specify in `IN-12` and `F-31` that `sync.ts` matches incoming active rows to existing `teachers` rows in this order:
  1. exact `wikidata_qid` or `lcnaf_id` (when present on both);
  2. exact normalised `name`;
  3. normalised `name` or `aliases` of the incoming row matching the existing teacher's `name` or `aliases` (with compatible `born`/`died` years where present).

---

### `argon-16` · `CC BY-SA 1.0` originals and `OUT-04` unpublished portraits need explicit status and loop prevention
- **Refers to:** `SRC-02`, `SRC-11` (`requirements.md` lines 308, 318), `OUT-04`, `T-07`, `F-07`, `F-24`
- **Severity:** `minor`
- **Problem:**
  1. `SRC-02` allows `"CC BY and CC BY-SA, any version"` as Tier 2, while `SRC-11` says `CC BY-SA 1.0` adaptations are `"Held for the owner, never published automatically"` (checked in `F-24`). If `CC BY-SA 1.0` isn't stopped until `F-24` (publishing), the pipeline will pay for `precheck`, `enhance`, and `draftCheck` on an original it cannot publish, and `T-07` has no `held` status on `portraits`.
  2. Similarly, if a portrait is stopped at `F-24` by `OUT-04` (missing required field/licence/schema error) or `CC BY-SA 1.0`, what prevents the next run from picking the same candidate and failing again?
- **Suggestion:**
  - Either refuse `CC BY-SA 1.0` in `SRC-02` / `F-07` with verdict `refused` (`reason: "cc_by_sa_1_0_held"`) before any AI calls are made, **or** if tested in `F-24`, store `portraits.status = "failed"` (recorded in `portrait_events` as `"held_for_owner"` / `"invalid_record"`) and mark the candidate `set_aside` so later runs do not retry it.

---

### `argon-17` · Face-only perceptual hash in `PIP-20` Layer 1 risks merging two different frontal sittings of the same teacher
- **Refers to:** `PIP-20` (`requirements.md` lines 605–610), `F-42` (`features.md` lines 538–548), `prototype/same_photo.py`
- **Severity:** `minor`
- **Problem:**
  `PIP-20` Layer 1 says: `"Fingerprint: a perceptual hash of the cropped face catches exact and near-exact duplicates."`
  Because `crop.ts` (`F-12`) aligns every frontal face so the eyes sit at $y = 0.443$ and the mouth at $0.680$, two *different* frontal studio photographs of the same person have nearly identical low-frequency face layouts. If the harness implements Layer 1 with a standard 64-bit `dHash`/`pHash` on the cropped face and a typical Hamming threshold (e.g. $\le 8$), Layer 1 will short-circuit and judge two different sittings as `"same"` before SIFT (`Layer 2`) ever runs!
  Also, `prototype/same_photo.py` (line 45) recomputes `sift.detectAndCompute` inside the pairwise loop (`inliers(a, b)`), which is $O(N^2)$ SIFT extractions when a teacher has many candidates.
- **Suggestion:**
  - In `PIP-20` and `F-42`: specify that Layer 1 (`fingerprint`) is a 64-bit `dHash` (9×8 greyscale gradient hash) with a tight Hamming distance threshold of **$\le 2$ bits** (or exact SHA-256), which catches only exact/re-encoded/resized duplicates and leaves crops, retouches, and different sittings to Layer 2 (SIFT + RANSAC).
  - Specify that `samePhoto.ts` caches SIFT keypoints/descriptors per candidate image and compares each new candidate against one canonical representative per existing `photograph` group.

---

### `argon-18` · OpenAPI `Decision.value` schema and `ChangeFeed` empty-state details for `F-03` and `F-44`
- **Refers to:** `F-03` (`features.md` lines 126–128), `F-44` (`features.md` lines 770–773), `brain/contracts/portraits-api.openapi.json` (`Decision` lines 1626–1689, `ChangeFeed` lines 1555–1587)
- **Severity:** `minor`
- **Problem:**
  1. In `portraits-api.openapi.json` (lines 1634–1688), `Decision.value` has no type constraint in JSON Schema (`"description": "For correct: a year (integer) or null for approx_date; a boolean for best_known"`), and `Decision` does not forbid `reason` on `approve`/`set_main`/`correct` or `field`/`value` on non-`correct` decisions. In `F-03`, the check `"zod and ajv agree on 10 good and 10 bad generated payloads per request body"` will fail if the agent writes a discriminated union in Zod (`field: "approx_date" => value: z.number().int().nullable()`, `field: "best_known" => value: z.boolean()`) that rejects payloads `ajv` accepts!
  2. In `ChangeFeed` (`portraits-api.openapi.json` lines 1555–1586), `since`, `until`, and `next_cursor` (`type: "string"`, non-null) are all required. When the caller passes `?after=c_1241` (omitting `since`) or when the database has 0 changes (`changes: []`), what values should `F-44` return for `since` and `next_cursor`?
- **Suggestion:**
  - In `portraits-api.openapi.json` (`Decision`): add conditional schema constraints under `allOf` so `field == "approx_date"` requires `value` to be `{"oneOf": [{"type": "integer"}, {"type": "null"}]}` and `field == "best_known"` requires `value` to be `{"type": "boolean"}` (and add a negative test case in `check_api.py`).
  - In `F-44`: specify that when `after` is passed to `/api/v1/changes`, `since` in the answer is the timestamp of the cursor's sequence entry (or the service start time for `"c_0"`), and when `changes` is empty, `next_cursor` echoes the input `after` cursor (or `"c_0"` if none exist yet) with `more: false`. Also specify that passing neither `since` nor `after` (or both) returns `422 invalid`.

---

### `argon-19` · Harness card dependencies and OpenRouter live-check polish
- **Refers to:** `F-01`, `F-36`, `F-39`, `F-07`..`F-38`, `F-17`, `F-46`, `HT-18`
- **Severity:** `nit`
- **Problem:**
  1. **`F-36` vs `F-39` build order:** `F-36` (Card #5, Phase 1) builds `GET /api/v1/health`, which must return `opencv: true` and `sharp: true` (`portraits-api.openapi.json` line 1986). However, `@techstark/opencv-js` and `sharp` are only introduced in `F-39` (Card #17, Phase 3).
  2. **`O-10` (User-Agent contact) on Phase 2 cards:** `F-07`, `F-08`, `F-09`, `F-10`, `F-34`, and `F-35` have `Live calls: network (free; to record)` and `Owner input: none`, while `O-10` (the required User-Agent contact email for Wikimedia's 2026 limits) is only listed on `F-38`.
  3. **OpenRouter inline cost & model IDs (`F-17`, `F-27`, `HT-18`):** `F-27` checks that `"the spend ledger shows each call's actual cost"`. OpenRouter only includes `usage.cost` reliably in `/api/v1/chat/completions` responses when `"usage": { "include": true }` is sent in the request body. Also, `HT-18` (the throwaway test) should verify the exact OpenRouter model slugs (`D-52`, `PIP-13`) and image-edit response format so any slug difference is caught before Phase 1 rather than in Phase 6 (`F-27`).
  4. **`F-46` (`/admin/trial` placeholder):** `OUT-13` lists the trial board on the admin site (`F-46`, Phase 5), while `F-28` (Phase 6) builds the trial board.
- **Suggestion:**
  1. Include `@techstark/opencv-js` and `sharp` in `package.json` in `F-01` (or `F-36`) so `F-36`'s `/api/v1/health` can verify they load on Railway.
  2. Note `O-10` on `F-06` / `F-07` (or provide the app contact email in `settings.ts` before the build starts).
  3. Specify in `F-17` that `openrouter.ts` sends `"usage": { "include": true }` on every request, and add a check to `HT-18` to confirm the five model IDs in `GET https://openrouter.ai/api/v1/models` and one keyed image-edit call.
  4. Note in `F-46` that `/admin/trial` renders an empty state (`"No trial run yet"`) in Phase 5 until `F-28` populates `trial_items` in Phase 6.

---

## Summary Table for Quick Triage

| ID | Severity | Area | Short Summary |
|---|---|---|---|
| `argon-1` | `blocker` | Pipeline (`F-11`, `F-23`) | `PIP-20`, `SRC-07` damage rank, and `PIP-16` date spread are ordered before image download and `PRE-CHECK` |
| `argon-2` | `blocker` | Models (`F-18`, `F-19`, `F-21`) | Raw LoC TIFFs (30–150 MB) sent to OpenRouter will fail; must send downscaled sRGB PNG viewing copy |
| `argon-3` | `blocker` | Draft check (`PIP-09`, `F-21`) | Image order in `PIP-09`/`F-21` (`[draft, original]`) is reversed vs `draftcheck.md` (`[original, draft]`); missing `checkPageRgb` |
| `argon-4` | `blocker` | Cut-out limits (`PIP-19`, `F-15`) | `smooth_mask` deletes floating fragments before `PIP-19` checks `>= 98%` largest connected component |
| `argon-5` | `blocker` | Teachers (`F-02`, `IN-12`) | `authors.csv` reader ignores optional `wikidata_qid` and `lcnaf_id` columns added by the owner |
| `argon-6` | `blocker` | Enrichment (`F-08`, `F-35`) | `F-08` requires existing teacher years to search Wikidata, blocking `F-35` on the ~110 undated teachers |
| `argon-7` | `major` | Imaging perf (`F-13`, `F-14`) | Full-res `d=-1` bilateral filter ($131\times 131$) + FFT on 13 MP LoC scans will stall/OOM WASM; cache `_threshold_map` |
| `argon-8` | `major` | OpenCV.js (`F-39`, `F-12`, `F-13`) | `cv.medianBlur` throws on `float32` for `ksize=15`; `cv.idft` needs `DFT_SCALE`; YuNet `[x,y,w,h]` vs `[x0,y0,x1,y1]` & offline `.onnx` |
| `argon-9` | `major` | Crop fallback (`PIP-04`, `F-12`) | Normalized `0..1` vs pixel `face_box` from `precheck.md`, and missing 5-landmark estimation equations when YuNet finds no face |
| `argon-10` | `major` | Mask & fallback (`PIP-03`, `F-19`, `F-30`) | `mask.png` must be warped to original's `(w, h)` via `A` inverse; `cutout_keyed` needs alignment and triggers when `enhance` errors |
| `argon-11` | `major` | Network (`SRC-01`, `SRC-04`, `F-06`) | Allowlist missing `upload.wikimedia.org`, `tile.loc.gov`, `iiif.wellcomecollection.org`; manual redirect check; `try_link` URL patterns |
| `argon-12` | `major` | Requests (`IN-06`, `F-45`) | `portraits-api.sample.json` reuses `charles-fillmore-2` on remake; `note_kind.md` refuses cut-out ear/shoulder fixes as crop/outline |
| `argon-13` | `major` | Decisions & slots (`PIP-16/17`, `F-48`) | `PIP-17`/`F-48` `replaces` for different photo contradicts `OUT-07`; missing `main` transfer on swap/turn-down; `PIP-16` spread rule |
| `argon-14` | `major` | Trial & caps (`F-04`, `F-17`, `F-28`) | Missing `trial_items` table to isolate production trial; `step_cache` key invalidation on `recipeVersion` bump; `DATABASE_PUBLIC_URL`; `spend.budget` |
| `argon-15` | `minor` | Sync (`IN-12`, `F-31`) | Define deterministic matching rule for renamed authors in `authors.csv` (never by row index) |
| `argon-16` | `minor` | Rights & publish (`SRC-11`, `F-24`) | Refuse/hold `CC BY-SA 1.0` before paid AI steps, and mark `OUT-04` failures `set_aside` to prevent infinite retries |
| `argon-17` | `minor` | Same-photo (`PIP-20`, `F-42`) | Cropped-face perceptual hash can collide on different frontal sittings; use tight threshold ($\le 2$ bits) and cache SIFT descriptors |
| `argon-18` | `minor` | Contract (`F-03`, `F-44`) | Constrain `Decision.value` by `field` in OpenAPI so `ajv` and `zod` agree; specify `ChangeFeed` empty/cursor fields |
| `argon-19` | `nit` | Cards (`F-01`, `F-36`, `HT-18`) | Install OpenCV.js/sharp in `F-01` for `F-36` healthcheck; note `O-10` on Phase 2 cards; send `"usage": {"include": true}` to OpenRouter |

---

## Responses (Claude, 2026-10-20)

Filed from `Argon Notes.md` unchanged, with this section added. **All 19 points are accepted**; none is declined. Two needed the owner, who answered the same day: the optional id columns (argon-5, **D-60**) and keeping the swap for a different photograph (argon-13, **D-61**). Where a suggestion was refined or corrected, the response says why.

New requirements: **PIP-21** (the order of steps), **PIP-22** (what the models are sent), **PIP-23** (working resolution) and **TRI-09** (trial results kept apart). The contract is now draft 5, the cards draft 3.

Merging also brought up one thing the review didn't: the prototype had measured the crop with a different face detector from the app's. **Recipe 0.5.0** fixes that (under argon-8).

| Point | Response | What changed |
|---|---|---|
| argon-1 | **Accepted, refined.** Copies are grouped, and pre-checked, on previews (at most 1,600 px, from each source's own sized-image service), not on downloaded originals. A full original is downloaded only for a photograph chosen for a slot | PIP-21 (new); PIP-01, SRC-07; architecture.md's data flow; `sources.md`; F-09, F-10 and F-34 record preview links; F-11 now gathers, previews, groups and orders; F-23 pre-checks before choosing, tries the next copy on damage, and counts downloads |
| argon-2 | **Accepted.** | PIP-22 (new): 8-bit sRGB PNG at most 1,600 px and under 5 MB; the enhance and cut-out calls get the descreened working region; the same-photo check gets 800 px. `modelImage.ts` in F-41. Request-shape checks in F-18, F-19, F-21 and F-43 (each now depends on F-41). The prompts' *Send* lines |
| argon-3 | **Accepted.** | PIP-09 and F-21 follow `draftcheck.md`'s order; `checkPageRgb: [28, 30, 38]` in settings (F-01, architecture.md) and named in `draftcheck.md` |
| argon-4 | **Accepted.** | PIP-19: the 98% share is measured on the raw cut-out before smoothing, the other limits on the smoothed figure; F-15's check |
| argon-5 | **Accepted** (owner: D-60). Checked read-only in library-pipeline: its reader uses `csv.DictReader`, and `propose.py` rewrites the file keeping its existing columns, so extra columns are safe | IN-01, IN-02 (malformed ids refused, by pattern), IN-12, F-02, F-31. IN-12 also maps `key_works` (used in argon-6) |
| argon-6 | **Accepted, stricter.** Agreeing years alone can still pick the wrong person when two share a name (there's a linguist called Charles J. Fillmore). The Wikidata person's LoC id (P244) must be the same name record, with the years agreeing in both. When several people qualify, the teacher's `key_works` must pick out exactly one, by a work (P800, or an item whose author P50 is them) | SRC-06(b) rewritten; IN-13; F-08 returns every person found, with P244 and works; F-35 checks undated, same-name and unresolvable cases |
| argon-7 | **Accepted, refined.** An original up to 2,000 px is processed whole, as the prototype does, so parity is untouched. A larger one is processed as a working region: the crop's square plus 25% a side, cut at full resolution, then reduced by area averaging to at most 2,000 px. That keeps more of the face than shrinking the whole scan | PIP-23 (new); PIP-05; F-12 builds the region; F-13 now depends on F-12 and checks time and memory on a 4,000 × 5,000 synthetic original; F-14 builds the threshold map once per recipe, in one pass |
| argon-8 | **Accepted, with one correction.** The suggested 8-bit `medianBlur` route isn't precise enough: on Cady's original it moves one screen peak by a frequency bin. A median on values quantised to 12 bits finds exactly the prototype's peaks on all three. The port computes the median itself, reflecting the border as scipy does. The other traps are as Argon wrote them | architecture.md, new "Porting traps"; F-39's checks. YuNet committed in `models/` (MIT, source commit and SHA-256 in `models/README.md`): the 2023 file for OpenCV and a dynamic-shape copy for `onnxruntime-node`. `prototype/export_parity.py` writes `prototype/parity/`: per-operation arrays with their exact calls and tolerances, plus results for YuNet, ECC, SIFT, the screen detector and the fingerprint |
| argon-8, further | **Found while making the references.** The prototype measured the owner's framing with SCRFD (research licence). With YuNet's landmarks, recipe 0.4.0's constants framed Fillmore 20% and Holmes 7% tighter than the owner's portraits. F-12's old check (landmarks within 5% of the SCRFD fixtures) would have failed on Fillmore (7%). Separately, YuNet's box for Cady reaches the hair's edge, and the drift check wrongly refused a good synthetic copy there (1.41 cells) | **Recipe 0.5.0:** the crop re-measured with YuNet (`eye_mouth_frac` 0.221, `eye_y_frac` 0.449), and the drift check measured inside the face box inset by 0.15 a side (good copies 0.14–0.31, moved features 0.95–1.08). Fixtures now hold YuNet's landmarks; `prototype/out/` regenerated; the measures at the owner's framing are unchanged within 0.006. STY-03, STY-07, PIP-04, PIP-13, F-01, F-12, F-16, F-30, `prototype/README.md` |
| argon-9 | **Accepted, with measured proportions.** The fallback uses where YuNet's landmarks actually sit inside its own box on the three originals: eyes at ±0.22 w and 0.39 h, nose at 0.58 h, mouth corners at ±0.19 w and 0.74 h. A crop made that way puts the eye line within 0.03 of the side of the real crop's, at a scale within 10% | PIP-02 and F-18 (the face box turned into pixels, `minFacePx` checked in code; `precheck.md`'s *Send* line); PIP-04 and F-12; `landmarks_from_box` in `prototype/recipe.py` |
| argon-10 | **Accepted.** | PIP-03 (the cut-out fallback also runs when the enhance call fails, and is aligned the same way; the mask is mapped back onto the original), OUT-11, F-19, F-23, F-30, `cutout_keyed.md` |
| argon-11 | **Accepted.** | SRC-01 lists the hosts, including the file hosts; redirects are followed by hand, each target checked (SRC-01, F-06, architecture.md). SRC-04 lists the accepted link forms, read without fetching (also `sources.md`, the contract, F-45) |
| argon-12 | **Accepted, one detail changed.** The sample's `result_portrait_id` is `charles-fillmore-4`, not `-3`: `-3` already exists in the samples (the turned-down one), and ids are never reused | The sample; `note_kind.md` v2 (cut-out faults are restoration; "crop" and "outline" narrowed); IN-06's request life cycle and refusal reasons; F-45 builds the web side and the worker side (`src/pipeline/requests.ts`), with a fixture for each refusal reason |
| argon-13 | **Accepted.** The owner chose to keep offering a higher-ranked different photograph to a full teacher (D-61), so `replaced` was widened rather than the bullet dropped | OUT-07, PIP-17, IN-07, the contract (`replaced`, `replaces`, `replaced_by`), `handoffs/library-api.md`. Main-portrait rules in IN-07, the contract and F-45. PIP-16's rule step by step (`minSpreadYears` 10; no P18 → best quality first), with a fixture per branch in F-23; F-48's full-slot case |
| argon-14 | **Accepted.** | TRI-09 (new); `trial_runs` and `trial_items` (F-04, architecture.md); F-28 checks that the portraits, candidates and changes tables are untouched. RUN-03: the cache key is the image sent, the step, the model, the prompt version and any note, never `recipeVersion` (F-04, F-28). The CLI uses `DATABASE_PUBLIC_URL ?? DATABASE_URL` (F-01, architecture.md). `spend.budget` and `first_pass_state` (RUN-04, F-04, F-17, F-25) |
| argon-15 | **Accepted.** | IN-12 and F-31: ids, then the same normalised name, then a shared name or alias with compatible years; never row position |
| argon-16 | **Accepted** (the first option). | SRC-02, F-07 and `sources.md`: CC BY-SA 1.0 is held at the licence step, before anything is spent. OUT-04 and F-24: a bad record is `failed` and its candidate set aside |
| argon-17 | **Accepted.** The references bear it out: a half-size or JPEG copy changes the difference hash by at most 1 bit, different people by 29–37 bits | PIP-20 and F-42: a whole-picture 64-bit difference hash, at most 2 bits; feature points computed once per picture; one representative per photograph group |
| argon-18 | **Accepted.** | The contract: `value` constrained by `field`; `reason` only on a turn-down; `field` and `value` only on a correction. `check_api.py` has four more refused payloads (eleven). The change-feed rules in the contract and F-44 |
| argon-19 | **Accepted.** | F-01 installs OpenCV.js and `sharp`; O-10 noted on the Phase 2 cards that record live responses; `"usage": {"include": true}` on every OpenRouter call (F-17, architecture.md); HT-18 widened (model ids, actual cost, one image-edit answer), with a change-log line in `handoffs/harness-throwaway-test.md`; `/admin/trial` shows an empty state until F-28 (F-46) |

### After the merge: an independent check

A separate agent, which hadn't seen the merge being made, checked it against these responses and across the files. Every change claimed above was present. It found ten gaps the merge had left, all now fixed:

1. **The pre-check came before the download** but was sent the viewing copy, made from the downloaded original. Previews are now at most 1,600 px, and the pre-check gets the best copy's preview. The original's width and height come from the source's metadata, for `minFacePx`; without them, the check is repeated after the download (PIP-21, PIP-22, PIP-02, F-09, F-10, F-34, F-11, F-18, `precheck.md`).
2. **The cache key had no attempt number,** so a remake or a note-less `try_again` would have been served the first copy. The key now holds every image sent, in order, plus the attempt (RUN-03, F-04).
3. **F-31 checked ids with F-08, which came after it.** F-08 now comes before F-31, and F-31 depends on it.
4. **`try_again` on an approved portrait** would have replaced it before the library approved anything. Now, on a waiting portrait the remake replaces it at once; on an approved one it's offered with `replaces`. A request on a turned-down or replaced portrait answers 409 (IN-06, the contract, F-45).
5. **Slots:** `replaces` is now set only on an offer in place of an approved portrait, so an offer never frees a slot for a fourth draft (PIP-14, OUT-07, T-07).
6. **D-61's terms are defined:** PIP-16 is re-run over the three and the new photograph. If the new one is chosen, and the one left out is approved and not the main portrait, it's offered in that one's place; otherwise nothing is offered. One open offer per teacher at a time (PIP-17, F-48).
7. **Mask mapping for large originals** composes the working region's offset and scale, and the data flow shows face detection before the region (PIP-03, F-30, architecture.md).
8. **The `held` verdict is carried through** to the rights log, the admin site and SRC-11's check (SRC-11, SRC-12, `sources.md`, F-32, F-46).
9. **T-07 is brought up to date** with a list of additions since D-43; F-04 builds from it.
10. **A failing cut-out fallback** fails the draft; the remake tries once more, then the original is set aside (PIP-03, F-19, F-23).

Smaller ones, also fixed:
- **`refused_reason`** is now a set of codes, with a refused payload in `check_api.py`, making twelve.
- **Works by P50** are found with Wikidata's own search, never the query service, whose host isn't allowed.
- **Link forms:** `www.` is accepted on every LoC form, and so are Commons thumbnail links.
- **The change feed:** an empty `since` page doesn't replay older changes.
- **Spend:** requests during the first pass count toward its budget.
- **Keys:** the bucket client accepts `trial/` keys.
- **Text brought up to date:** PIP-22's checks in F-21 and F-43; TRI-08's figures; RUN-08 now mentions D-61; the prompts README; the request kinds in the contract; the module list; the build plan's header.
