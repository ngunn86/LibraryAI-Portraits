# Feature cards (build order)

Status: **proposed** (Claude, 2026-10-19). The harness builds these one at a time, in this order, respecting *Depends on*. Every check is a pytest test marked with the feature, so `uv run pytest -m f07` runs F-07's checks (see [build-plan.md §5](build-plan.md)).

## Card format (fixed, so the conductor can parse it)

```
### F-NN · Title
- Phase:        1–6
- Goal:         one sentence
- Covers:       requirement IDs
- Depends on:   F-IDs, or "none"
- Owner input:  O-IDs, or "none"
- Build:        modules or files
- Checks:       bulleted, each one a test
- Test data:    fixtures needed
- Live calls:   none | network (free public APIs, fixture recording) | paid (≤ $N)
- Parkable:     yes | no (if stuck, can the build continue without it?)
- Size:         S | M | L
```

## Overview

| F | Title | Phase | Depends on | Owner input | Live | Parkable |
|---|---|---|---|---|---|---|
| F-01 | Project skeleton, settings and keys | 1 | none | none | none | no |
| F-02 | Teacher list loader and validator | 1 | F-01 | none | none | no |
| F-03 | Contracts and manifest validator | 1 | F-01 | O-1 | none | no |
| F-04 | State store and step cache | 1 | F-01 | none | none | no |
| F-05 | Receiver stub | 1 | F-03 | none | none | no |
| F-06 | Network client (allowlist, polite, cached, replayable) | 2 | F-01 | none | none | no |
| F-07 | Licence classifier | 2 | F-06 | none | network | no |
| F-08 | Wikidata: fetch, sanity check, find ids | 2 | F-06 | none | network | no |
| F-09 | Commons: P18 file and P180 depicts search | 2 | F-07, F-08 | none | network | no |
| F-10 | Library of Congress: name and dates match | 2 | F-07 | none | network | yes |
| F-11 | Candidates: assemble, order, de-duplicate, download | 2 | F-04, F-08, F-09, F-10* | none | network | no |
| F-12 | Crop | 3 | F-01 | none | none | no |
| F-13 | Descreen | 3 | F-01 | none | none | yes |
| F-14 | Halftone | 3 | F-01 | none | none | no |
| F-15 | Code outline, composite and master check | 3 | F-12, F-14 | none | none | no |
| F-16 | Recipe regression on the examples | 3 | F-12..F-15 | O-2, P0-3 | none | yes |
| F-17 | Model client, spend ledger and cap | 4 | F-04, F-06 | none | none | no |
| F-18 | Pre-check | 4 | F-17 | none | none | no |
| F-19 | Cut-out | 4 | F-17 | none | none | no |
| F-20 | Model-drawn outline: extract and align | 4 | F-15, F-17 | none | none | yes |
| F-21 | Draft check (and compare-with-target) | 4 | F-17 | none | none | no |
| F-22 | `doctor` | 5 | F-02, F-17 | none | none | yes |
| F-23 | Per-teacher pipeline and failure policy | 5 | F-11, F-13, F-15, F-18, F-19, F-21 (F-20 if not parked) | none | none | no |
| F-24 | Delivery writer, report and zip | 5 | F-03, F-23 | none | none | no |
| F-25 | Run queue: order, requests, status, resume, dry-run | 5 | F-23, F-24 | none | none | no |
| F-26 | End-to-end offline run | 5 | F-05, F-25 | none | none | no |
| F-27 | Live smoke test | 6 | F-22, F-26 | O-4, O-5 | paid ≤ $2 | no |
| F-28 | Trial, board and defaults | 6 | F-27 | O-2, O-3, O-4 | paid ≤ $40 | no |
| F-29 | Examples reproduced | 6 | F-16, F-28 | O-2 | paid ≤ $5 | yes |

\* If F-10 is parked, F-11 is built without rule 3, and the digest says so.

SCOPE-01..04 are boundaries rather than features. Reviewers check them, and AC-06 is also enforced by F-06's allowlist test.

---

## Phase 1: Foundation

### F-01 · Project skeleton, settings and keys
- **Phase:** 1
- **Goal:** A Python package with a CLI, a validated settings file, key loading and an offline test suite.
- **Covers:** IN-10, IN-11, STY-05, RUN-01, RUN-05 (frame), RUN-06, RUN-07
- **Depends on:** none
- **Owner input:** none
- **Build:** `pyproject.toml` and lock (uv); `portraits/cli.py`, `config.py`, `keys.py`; `settings.toml` with placeholder recipe numbers; `tests/conftest.py`, which blocks network access; pytest markers `f01`..`f29` and `live`.
- **Checks:**
  - `uv run pytest` passes with networking blocked and no keys set.
  - `portraits --help` lists `doctor`, `teachers`, `run`, `trial`, `validate`, `zip` and `status`. Commands not built yet say "not built yet" and exit non-zero.
  - A settings file with a wrong type or a missing value is refused, and the message names the setting.
  - Changing any `[recipe]` value without changing `recipe_version` fails a test (STY-05).
  - Keys are read from the environment, falling back to the keys file. A missing key is reported by name only, and a key's value never appears in the output or the logs.
  - Settings refuse a draft-check model of the same family as the outline model or any challenger (PIP-09). One checker outside all three families, such as Claude, covers the whole trial.
- **Test data:** valid and invalid settings files.
- **Live calls:** none
- **Parkable:** no
- **Size:** M

### F-02 · Teacher list loader and validator
- **Phase:** 1
- **Goal:** Load `teachers.csv`, refuse bad rows by name, and refuse broken files before anything is spent.
- **Covers:** IN-01, IN-02, IN-03, IN-04 (the eligibility flag per row), IN-05, AC-01
- **Depends on:** F-01
- **Owner input:** none (the owner's real list is checked later with `teachers check`)
- **Build:** `portraits/teachers.py`; the `portraits teachers check <file>` command.
- **Checks:**
  - A valid fixture with 10 rows loads all 10, with aliases split on ` | `.
  - Each refusal reason (bad slug, missing name, each kind of impossible date, malformed Wikidata id, duplicate id) is refused, with row number, id and reason named, while the other rows load.
  - Whole-file refusals: not UTF-8, no header, a missing required column, no valid rows.
  - Each row gets the right eligibility: `qid`, `years_only` or `neither`.
  - Changing a row's `notes` doesn't change anything the loader returns except `notes` itself.
  - `teachers check` exits non-zero when any row is refused, and prints the refusals.
- **Test data:** about eight small CSV fixtures.
- **Live calls:** none
- **Parkable:** no
- **Size:** S

### F-03 · Contracts and manifest validator
- **Phase:** 1
- **Goal:** Hold every contract as a schema, and validate manifests exactly as the library will.
- **Covers:** OUT-02, OUT-04, IN-06 and IN-07 (schemas), AC-02 (validation part)
- **Depends on:** F-01
- **Owner input:** O-1 (blocking: the Rev1 schema, its sample and `validate.py`)
- **Build:** `portraits/contracts/` (manifest, requests and status, with `schemas/`); the `portraits validate <manifest.json>` command.
- **Checks:**
  - Rev1's sample manifest validates unchanged, with the tool's validator and with Rev1's `validate.py`.
  - The sample with the licence removed from one record is refused, and the message names the field.
  - The tool's validator and `validate.py` agree on 5 good and 5 bad fixtures.
  - Fixtures of `requests.json` and `status.json` validate; malformed ones are refused with the field named.
- **Test data:** Rev1's sample; derived bad manifests; requests and status fixtures (P0-5).
- **Live calls:** none
- **Parkable:** no
- **Size:** S

### F-04 · State store and step cache
- **Phase:** 1
- **Goal:** One SQLite store that keeps jobs, candidates, set-asides, attempts, spend, handled requests, deliveries and cached step results across runs and crashes.
- **Covers:** RUN-03 (storage), PIP-12 (storage), IN-08 (storage)
- **Depends on:** F-01
- **Owner input:** none
- **Build:** `portraits/state.py` (tables as in [../spec/architecture.md](../spec/architecture.md)); a simple, numbered schema version.
- **Checks:**
  - A fresh store is created in a temporary folder. Each table records and reads back.
  - The step cache returns a hit for the same key and a miss when the SHA-256, step, model or settings hash changes.
  - Data written before the process is killed (simulated by closing without a clean shutdown) is still there after reopening.
  - The state folder defaults outside the repo and follows the setting.
- **Test data:** none
- **Live calls:** none
- **Parkable:** no
- **Size:** S

### F-05 · Receiver stub
- **Phase:** 1
- **Goal:** A small program that inspects a delivery folder the way the library will, and accepts it or refuses it with reasons.
- **Covers:** AC-03, OUT-01, OUT-10
- **Depends on:** F-03
- **Owner input:** none
- **Build:** `stub/receiver.py`, runnable as `python -m stub.receiver <folder>`; helpers to write `requests.json` and `status.json` fixtures into a folder.
- **Checks:**
  - It accepts the sample run fixture.
  - It refuses each of these, naming the reason: a missing master; a master SHA-256 mismatch; a master that isn't 1,000 × 1,000; a master with any non-white visible pixel; an original over 1,600 px; a manifest that fails the schema.
  - It reports late-arriving files as "waiting", not as an error, when told it's checking a live, syncing folder.
- **Test data:** the sample run (P0-5); broken variants made in tests.
- **Live calls:** none
- **Parkable:** no
- **Size:** S

---

## Phase 2: Sources and rights

### F-06 · Network client
- **Phase:** 2
- **Goal:** One HTTP client for every source call: an allowlist, a polite User-Agent, rate limits, retries, an on-disk cache, and record/replay for tests.
- **Covers:** SRC-01, SRC-09, SRC-10, RUN-06, AC-06
- **Depends on:** F-01
- **Owner input:** none
- **Build:** `portraits/net.py`
- **Checks:**
  - A request to any host outside the allowlist fails before leaving the process.
  - Every request carries the User-Agent built from settings.
  - 429 and 5xx responses are retried with backoff, up to a limit (mocked transport); a 404 is not retried.
  - A second identical request is served from the cache.
  - In replay mode, recorded responses are served with networking blocked; a request with no recording fails clearly.
- **Test data:** mocked transports
- **Live calls:** none
- **Parkable:** no
- **Size:** S

### F-07 · Licence classifier
- **Phase:** 2
- **Goal:** Map any Commons or LoC rights statement to tier 1, tier 2 or refused, and build the credit line.
- **Covers:** SRC-02, SRC-11
- **Depends on:** F-06
- **Owner input:** none
- **Build:** `portraits/sources/licences.py`; a fixture table of real licence strings.
- **Checks:**
  - A table test of at least 30 real strings, each with its expected class:
    - public-domain marks, CC0, "No known restrictions on publication" → tier 1;
    - CC BY and CC BY-SA, several versions → tier 2;
    - NC, ND, fair use, GFDL alone, "rights not evaluated", blank → refused.
  - A dual-licensed file takes its most open allowed licence.
  - An unknown string is refused, and its raw text is kept.
  - The credit line includes "adapted from" for tier 2, and the portrait licence is CC BY-SA for a CC BY-SA original (SRC-11, pending Q-16).
- **Test data:** licence strings collected from real Commons and LoC responses.
- **Live calls:** network (free; to collect the strings once)
- **Parkable:** no
- **Size:** S

### F-08 · Wikidata: fetch, sanity check, find ids
- **Phase:** 2
- **Goal:** Read a teacher's Wikidata item (P18 image, birth and death years, labels and aliases, P31), check a given id, and find a missing one under SRC-06.
- **Covers:** SRC-03 (rule 1), SRC-06, IN-04
- **Depends on:** F-06
- **Owner input:** none (Q-01 decides whether finding ids is switched on)
- **Build:** `portraits/sources/wikidata.py`
- **Checks:**
  - A good id returns its P18 file and its years.
  - An id that isn't a human, or whose years disagree with the list, is refused with a reason that names it.
  - Finding an id: one unique match → accepted and marked `resolved_by_tool`; two matches → refused; no match → refused; any year mismatch → refused.
  - Finding ids can be switched off in settings.
- **Test data:** recorded responses for about 6 real teachers and the edge cases.
- **Live calls:** network (free; fixture recording)
- **Parkable:** no
- **Size:** M

### F-09 · Commons: P18 file and P180 depicts search
- **Phase:** 2
- **Goal:** For a Wikidata id, list the Commons files that certainly show the teacher (rules 1 and 2), each with its full original record.
- **Covers:** SRC-03 (rules 1, 2), SRC-08
- **Depends on:** F-07, F-08
- **Owner input:** none
- **Build:** `portraits/sources/commons.py`
- **Checks:**
  - The P18 file comes back with `matched_by: wikidata_p18`.
  - Files with a P180 depicts statement for the id come back with `matched_by: commons_p180`.
  - A file only in the teacher's category, or one that only names the teacher in its title, is not returned.
  - Each record has every SRC-08 field filled from the file's metadata, and licences are classified by F-07.
  - An owner's Commons link resolves to a record with `matched_by: owner_link` (SRC-04); a non-Commons link is refused.
- **Test data:** recorded responses: a teacher with P18 and P180 files; a teacher with a category-only file.
- **Live calls:** network (free; fixture recording)
- **Parkable:** no
- **Size:** M

### F-10 · Library of Congress: name and dates match
- **Phase:** 2
- **Goal:** Find Prints and Photographs records that name the teacher with matching dates (rule 3), with full records.
- **Covers:** SRC-03 (rule 3), SRC-05, SRC-08
- **Depends on:** F-07
- **Owner input:** none
- **Build:** `portraits/sources/loc.py`
- **Checks:**
  - A record headed `Surname, Forenames, YYYY-YYYY` matches when the name (or an alias) and both years agree.
  - Near-misses are refused: a wrong year; no dates; the name in the title only.
  - Rights advisories are classified by F-07.
  - The best-available image link and its size are recorded.
  - An owner's loc.gov link resolves to a record with `matched_by: owner_link`.
- **Test data:** recorded responses: a matching record, the near-misses, and a record with restricted rights.
- **Live calls:** network (free; fixture recording)
- **Parkable:** yes (rules 1 and 2 still work without it)
- **Size:** M

### F-11 · Candidates: assemble, order, de-duplicate, download
- **Phase:** 2
- **Goal:** For one teacher, gather every allowed candidate from all rules, order them, drop duplicates and set-asides, and download originals with checksums.
- **Covers:** SRC-04, SRC-07, SRC-08, IN-04, PIP-01, PIP-12
- **Depends on:** F-04, F-08, F-09, F-10 (optional)
- **Owner input:** none
- **Build:** `portraits/sources/candidates.py`
- **Checks:**
  - Candidates are ordered by tier, then by pixel count.
  - The same file reached by two rules appears once, keeping the strongest rule; equal SHA-256s are merged after download.
  - Originals already set aside in the store are excluded, unless they come in an owner's link request.
  - A teacher marked `neither` (no id, fewer than two years) gets no candidates and a "skipped: add a Wikidata id" reason.
  - Downloads are stored by SHA-256 in the state folder, and a second call doesn't download again.
- **Test data:** fixtures from F-08, F-09 and F-10; small real images.
- **Live calls:** network (free; fixture recording)
- **Parkable:** no
- **Size:** M

---

## Phase 3: Imaging (code only, free)

### F-12 · Crop
- **Phase:** 3
- **Goal:** Crop a cut-out to the house framing from five face landmarks: square, head near the top, face filling most of the width, shoulders off the bottom.
- **Covers:** PIP-04, STY-03
- **Depends on:** F-01
- **Owner input:** none (geometry from recipe 0.1.0; reference code in `prototype/recipe.py`, `crop_transform`)
- **Build:** `portraits/imaging/crop.py`; the YuNet face detector (model file committed).
- **Checks:**
  - With the landmarks in `prototype/fixtures/*.json`, the crop transform matches `prototype/recipe.py` to within 0.5 px.
  - On synthetic figures, the eye line, eye-to-mouth distance and face centre land inside the setting ranges.
  - On 3 real public-domain photos with fixture masks, the face is detected and the crop meets the ranges.
  - With no detectable face, a supplied box is used instead (the pre-check's).
  - The output is square, at the master size.
- **Test data:** synthetic masks; 3 small real public-domain photos with masks.
- **Live calls:** none
- **Parkable:** no
- **Size:** M

### F-13 · Descreen
- **Phase:** 3
- **Goal:** Find and remove a printed dot pattern from a scan before halftoning; leave clean photos alone.
- **Covers:** PIP-05
- **Depends on:** F-01
- **Owner input:** none
- **Build:** `portraits/imaging/descreen.py`
- **Checks:**
  - A synthetic image overlaid with a screen pattern is detected, and its frequency peaks fall below a set fraction afterwards.
  - A clean image is reported as "no pattern" and comes back unchanged.
  - Whether descreening was applied is returned for the record.
- **Test data:** synthetic images.
- **Live calls:** none
- **Parkable:** yes (the pipeline runs without descreening, and screened originals fail more often)
- **Size:** M

### F-14 · Halftone
- **Phase:** 3
- **Goal:** Turn the cropped photo into round white dots on a 45° grid on transparency, with dot size following tone.
- **Covers:** PIP-06, STY-01, STY-04
- **Depends on:** F-01
- **Owner input:** none (numbers from P0-3)
- **Build:** `portraits/imaging/halftone.py`
- **Checks:**
  - On a horizontal gradient, frequency analysis finds the set dot pitch at 45°, and dot area rises with brightness.
  - Black areas come out fully transparent.
  - The output passes the STY-06 checker (white only, alpha carries the shape).
  - The function's only image input is the cropped photo (STY-04, checked by its signature and a test).
- **Test data:** synthetic gradients.
- **Live calls:** none
- **Parkable:** no
- **Size:** S

### F-15 · Code outline, composite and master check
- **Phase:** 3
- **Goal:** Draw the code outline from the cut-out mask, lay it over the dots and write a valid master; provide the STY-06 checker used everywhere.
- **Covers:** PIP-07 (code method), PIP-08, STY-02, STY-06
- **Depends on:** F-12, F-14
- **Owner input:** none
- **Build:** `portraits/imaging/outline_code.py`, `compose.py`
- **Checks:**
  - On synthetic masks with jagged "hair", the line:
    - is one connected piece;
    - stays within the width range;
    - sits at the set offset outside the figure;
    - doesn't run along the bottom edge.
  - The master is 1,000 × 1,000 RGBA, every visible pixel is pure white, and the corners are transparent.
  - The checker refuses masters with a grey pixel, the wrong size or no alpha.
  - The same inputs give byte-identical output.
- **Test data:** synthetic masks.
- **Live calls:** none
- **Parkable:** no
- **Size:** M

### F-16 · Recipe regression on the examples
- **Phase:** 3
- **Goal:** Lock in the prototype's recipe: the code steps on the owner's three originals reproduce the prototype's reference outputs.
- **Covers:** IN-09, STY-07, TRI-08 (code measures)
- **Depends on:** F-12, F-13, F-14, F-15
- **Owner input:** none. O-2 is done, and the P0-3 outputs are in `prototype/` (recipe 0.1.0, waiting for the owner's look)
- **Build:** `tests/test_f16_recipe.py`, using `prototype/fixtures/` (cut-outs, landmarks, registrations) and `prototype/out/` (reference masters).
- **Checks:**
  - For each example and both framings (`owner-framing`, `auto-crop`), the product's code steps on the fixture cut-out reproduce `prototype/out/<tid>.<framing>.png`. The alpha may differ by at most 2/255 in mean, with at most 1% of pixels differing by more than 64/255.
  - The code measures at the owner's framing meet TRI-08's thresholds: figure overlap ≥ 0.85, tone error ≤ 0.08, dots across 110 ± 2, and no STY-06 problems.
- **Test data:** `prototype/fixtures/`, `prototype/out/`, `design/portraits/`.
- **Live calls:** none
- **Parkable:** yes (raised in the digest)
- **Size:** S

---

## Phase 4: Model steps (stubbed in tests)

### F-17 · Model client, spend ledger and cap
- **Phase:** 4
- **Goal:** One client for OpenRouter (and fal) that every paid step uses: stub mode, cost logging, and a hard cap checked before every call.
- **Covers:** RUN-04, RUN-06, IN-11, SRC-01 (model hosts)
- **Depends on:** F-04, F-06
- **Owner input:** none
- **Build:** `portraits/models/client.py`
- **Checks:**
  - In stub mode, canned responses are returned and no network is used.
  - Every call writes a spend row (run, teacher, step, model, cost, estimated or actual).
  - The actual cost is taken from the provider's usage data when present (a mocked response), otherwise from the estimate.
  - When the next call's estimate would cross the cap, it isn't made: a `CapReached` result goes up, and no call follows.
  - The key never appears in the logs or the store (a test scans them).
  - Text, image and vision call shapes are supported (with mocked transports).
- **Test data:** mocked provider responses.
- **Live calls:** none
- **Parkable:** no
- **Size:** M

### F-18 · Pre-check
- **Phase:** 4
- **Goal:** Ask a vision model whether an original shows one person, with the face fully in view, large enough and undamaged, and get a structured verdict.
- **Covers:** PIP-02
- **Depends on:** F-17
- **Owner input:** none
- **Build:** `portraits/models/precheck.py`; `prompts/precheck.md`
- **Checks:**
  - A stubbed pass and a stubbed fail parse into a verdict with reasons, a face box and the medium.
  - A face smaller than `min_face_px` is failed by code, even if the model says pass.
  - Malformed model output is retried once. If it's still malformed, the step reports an error: the teacher's job pauses, and the original is not set aside.
  - Results are cached by original SHA-256 and model.
- **Test data:** canned responses.
- **Live calls:** none
- **Parkable:** no
- **Size:** S

### F-19 · Cut-out
- **Phase:** 4
- **Goal:** Get a clean figure cut-out from the background-removal model and keep it for later tries.
- **Covers:** PIP-03
- **Depends on:** F-17
- **Owner input:** none (Q-18 decides the provider)
- **Build:** `portraits/models/cutout.py`
- **Checks:**
  - A stubbed result is stored as an RGBA image with a mask.
  - A second request for the same original, model and settings is a cache hit with no call.
  - An empty or all-opaque mask is reported as a failed cut-out.
- **Test data:** canned images.
- **Live calls:** none
- **Parkable:** no
- **Size:** S

### F-20 · Model-drawn outline: extract and align
- **Phase:** 4
- **Goal:** Ask an image model for a white contour around the cut-out on black, keep only the line, and align it to the figure.
- **Covers:** PIP-07 (model method), STY-02, STY-04
- **Depends on:** F-15, F-17
- **Owner input:** none
- **Build:** `portraits/models/outline_model.py`; `portraits/imaging/outline_extract.py`; `prompts/outline.md`
- **Checks:**
  - From a synthetic "model output" (a contour plus stray marks, shifted by up to 5% and scaled by up to 5%), the extracted line is one connected stroke, re-stroked at the set width and aligned to the mask within a set distance.
  - Output with no usable line (blank, or many pieces) is reported as a failed outline.
  - Only the line reaches compositing: the model's image never touches the dot layer (STY-04).
- **Test data:** synthetic images.
- **Live calls:** none
- **Parkable:** yes (the code outline still works; the trial then has only the code contender, and the digest says so)
- **Size:** M

### F-21 · Draft check, and compare with target
- **Phase:** 4
- **Goal:** Ask a vision model (of a different family from the outline model) to judge a draft on five criteria. Also offer a mode that compares a draft with a hand-made target.
- **Covers:** PIP-09, TRI-08
- **Depends on:** F-17
- **Owner input:** none
- **Build:** `portraits/models/draftcheck.py`; `prompts/draftcheck.md`; `prompts/compare.md`
- **Checks:**
  - Stubbed responses parse into per-criterion pass or fail with a 1–5 score, plus notes. A draft passes only if all five criteria pass.
  - The draft is shown on the page colour, with the original and the examples attached (the request shape is checked on the stub).
  - Compare mode returns pass or fail with notes.
  - Malformed output is handled as in F-18.
- **Test data:** canned responses.
- **Live calls:** none
- **Parkable:** no
- **Size:** S

---

## Phase 5: Orchestration and delivery

### F-22 · `doctor`
- **Phase:** 5
- **Goal:** One command that says whether a run can start: settings, keys, models, the delivery folder and the list.
- **Covers:** RUN-05, R-4, R-8
- **Depends on:** F-02, F-17
- **Owner input:** none
- **Build:** the `doctor` command.
- **Checks:**
  - It reports each item as OK or a problem in plain words: settings valid; each key present (never its value); the delivery folder exists and is writable (writes and removes a test file); the list loads; each model id is known to its provider (mocked).
  - Its exit code is non-zero if anything required is missing.
  - It makes no paid calls.
- **Test data:** temporary folders; mocked provider model lists.
- **Live calls:** none
- **Parkable:** yes
- **Size:** S

### F-23 · Per-teacher pipeline and failure policy
- **Phase:** 5
- **Goal:** Take one teacher from candidates to a passing draft, or to set-asides, following the failure rules exactly.
- **Covers:** PIP-01..PIP-12, STY-04, STY-05
- **Depends on:** F-11, F-13, F-15, F-18, F-19, F-21 (and F-20 if not parked)
- **Owner input:** none (Q-06 and Q-07 decide the details; the proposed rules are built unless the owner says otherwise)
- **Build:** `portraits/pipeline.py`
- **Checks (scenario tests with stubbed models):**
  - The first candidate passes everything → one draft, attempt 1, with the check's notes recorded.
  - The first candidate fails the pre-check → it's set aside with the reason, and the next one is tried; this doesn't count toward the three.
  - A draft fails twice on a re-runnable criterion (model outline) → the original is set aside, and the next one is tried.
  - A draft fails on likeness (not re-runnable) → set aside after one failure.
  - Three originals reach drafting and all fail → the teacher is "given up for this run", with all set-asides recorded.
  - The pre-check cap per teacher is reached → stop with the reason.
  - `CapReached` from the client → the teacher's job pauses cleanly; nothing half-made is delivered.
  - The recipe version and settings are recorded with every attempt.
- **Test data:** stubs and small fixtures.
- **Live calls:** none
- **Parkable:** no
- **Size:** L (split into "happy path" and "failure rules" if the harness prefers)

### F-24 · Delivery writer, report and zip
- **Phase:** 5
- **Goal:** Write a run into the delivery folder exactly as the contract says, update it safely as records are added, and write the report; make a bulk zip on request.
- **Covers:** OUT-01..OUT-09, AC-02, SRC-11
- **Depends on:** F-03, F-23
- **Owner input:** none
- **Build:** `portraits/deliver.py`; the `zip` command.
- **Checks:**
  - After 3 stubbed portraits, `runs/<run-id>/` holds the masters, the originals (≤ 1,600 px), a `manifest.json` that validates, and `report.md`.
  - Write order: if the manifest file is read at any point mid-run (simulated), every record in it has its files present.
  - A record missing its licence, or whose teacher isn't on the list, isn't written, and the report names it.
  - The report covers every OUT-06 item (snapshot test).
  - `zip <run-id>` produces a zip that the receiver stub accepts when unzipped.
  - Keys appear in no delivered file (scan).
- **Test data:** stubbed pipeline results.
- **Live calls:** none
- **Parkable:** no
- **Size:** M

### F-25 · Run queue: order, requests, status, resume, dry-run
- **Phase:** 5
- **Goal:** Run all teachers in the right order and skip the right ones; act on requests and status; survive being stopped; estimate before spending.
- **Covers:** RUN-02, RUN-03, RUN-05 (`run`, `status`), IN-06, IN-07, IN-08, OUT-07
- **Depends on:** F-23, F-24
- **Owner input:** none (Q-02 decides skipping waiting teachers; the proposed rule is built)
- **Build:** `portraits/run.py`; the `run` command (`--limit`, `--teacher`, `--dry-run`); the `status` command.
- **Checks:**
  - Order: requests first, then other teachers. Skipped: approved; waiting (from `status.json` or the tool's own record); given up with no new candidates.
  - `try_again`, `another_original` and `try_link` each do what IN-06 says, and the draft carries `request_id`.
  - A request acted on in run 1 isn't redone in run 2.
  - Kill-and-resume: stopping mid-teacher, then running again, finishes the run with no paid step called twice (stub call counts).
  - `--dry-run` lists what would be done and an estimated cost, and makes no paid call.
  - `status` shows queued, delivered, set-aside and given-up counts.
- **Test data:** requests and status fixtures; stubs.
- **Live calls:** none
- **Parkable:** no
- **Size:** M

### F-26 · End-to-end offline run
- **Phase:** 5
- **Goal:** Prove the whole tool works offline: from a fixture list to a delivery folder the receiver stub accepts, then a second run whose behaviour changes with requests and status.
- **Covers:** AC-02, AC-03, IN-06, IN-07, OUT-10
- **Depends on:** F-05, F-25
- **Owner input:** none
- **Build:** `tests/test_f26_end_to_end.py`; refreshes the sample run in `tests/fixtures/sample-run/`.
- **Checks:**
  - Run 1, over 6 fixture teachers covering: a pass; a pre-check refusal then a pass; a set-aside then a pass; no candidates; a wrong Wikidata id; a refused row. The receiver stub accepts the folder.
  - Then `requests.json` (one of each kind) and `status.json` (one approved, one turned down) are written with the stub's helpers.
  - Run 2: requests are handled first; the approved teacher is skipped; the turned-down original is set aside and another is tried; the stub accepts run 2.
  - The sample run in the repo is regenerated from run 1 and still validates (OUT-10).
- **Test data:** everything above, recorded and stubbed.
- **Live calls:** none
- **Parkable:** no
- **Size:** M

---

## Phase 6: Live (spends the tool's key)

### F-27 · Live smoke test
- **Phase:** 6
- **Goal:** One real teacher, end to end, with real sources and real models, into the real delivery folder (or a test subfolder of it).
- **Covers:** whole pipeline; R-4; R-8
- **Depends on:** F-22, F-26
- **Owner input:** O-4 (keys), O-5 (folder)
- **Build:** `tests/live/test_f27_smoke.py`
- **Checks:**
  - `doctor` passes.
  - One teacher (chosen from fixtures with a known public-domain P18 image) is delivered. The receiver stub accepts the folder.
  - The actual spend is logged and is at most $2. Every step's actual cost is within 3× its estimate; if not, the estimates in settings are updated and the digest says so.
- **Test data:** one known teacher.
- **Live calls:** paid ≤ $2
- **Parkable:** no
- **Size:** S

### F-28 · Trial, board and defaults
- **Phase:** 6
- **Goal:** Run the trial set through every outline contender, score the results, pick the winner, write the board, and set the defaults.
- **Covers:** TRI-01..TRI-07, AC-05
- **Depends on:** F-27
- **Owner input:** O-2, O-3 (the trial set from P0-4), O-4
- **Build:** `portraits/trial.py`; the `trial` command; board output (PDF and HTML).
- **Checks:**
  - Every trial item is processed by every contender. The same cut-out and code are used for every contender (shown by cache keys).
  - `trial/<run-id>/board.pdf` and `board.html` exist. Each row shows the original, every contender's result with scores and cost, and the examples.
  - The winner follows TRI-04 (the "close" rule from Q-19), and the reasoning is written in the trial report.
  - Items whose outcome differs from the trial set's expected outcome are listed; this is a finding, not a failure.
  - Settings are updated with the winner and a `recipe_version` bump, committed with a digest note asking for the owner's veto.
  - The trial stops at its sub-cap if reached, and still writes the board for what's done.
- **Test data:** the trial set (P0-4).
- **Live calls:** paid ≤ $40
- **Parkable:** no (AC-05 needs it)
- **Size:** M

### F-29 · Examples reproduced
- **Phase:** 6
- **Goal:** Show that the pipeline, with the trial's defaults, reproduces the owner's three examples closely enough that the check passes them against the hand-made targets.
- **Covers:** TRI-08, AC-04
- **Depends on:** F-16, F-28
- **Owner input:** O-2
- **Build:** `tests/live/test_f29_examples.py`
- **Checks:**
  - For each of the three examples, compare-with-target mode passes, and the F-16 code measures still meet their thresholds.
  - If one fails, the harness may adjust recipe numbers only within the ranges P0-3 set, bumping `recipe_version` each time. After three tries it stops, and the board goes to the owner.
- **Test data:** O-2, the P0-3 outputs, the trial's cache.
- **Live calls:** paid ≤ $5
- **Parkable:** yes (raised to the owner with the board)
- **Size:** S
