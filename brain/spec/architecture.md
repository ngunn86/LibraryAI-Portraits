# Architecture (proposed)

Status: **proposed** by Claude (2026-10-19), waiting for owner review and for the reviewing agents. The stack choice is Q-15.

The aim is the simplest structure that meets the requirements:

- one Python package;
- one command-line tool;
- one local SQLite state store;
- one process working on one teacher at a time.

Nothing runs as a server.

## Stack

| Piece | Choice | Why |
|---|---|---|
| Language | Python 3.12, run in WSL Ubuntu on the owner's PC | The image work (NumPy, OpenCV, Pillow) is native to Python, and all three coding models are strongest in it |
| Environment | `uv`, with a `pyproject.toml` and a lock file | One command to set up; the same setup on any machine |
| Images | Pillow, NumPy, OpenCV (headless), scikit-image where it saves code | Halftone, descreen (FFT), contours, masks |
| Face box and landmarks | OpenCV's YuNet face detector (box plus five landmarks; a small model file, committed) | Free, local and the same every time. The crop needs the eye and mouth landmarks (PIP-04). Falls back to the pre-check's box |
| HTTP | `httpx`, with an on-disk response cache and record/replay for tests | Retries, timeouts, an allowlist (SRC-01) |
| Data and contracts | `pydantic` for settings and records; `jsonschema` for the manifest | Settings errors name the field; the schema check is the same one the library uses |
| CLI | `typer` | Small and typed |
| State | SQLite (Python standard library) | One file. Survives crashes, and makes runs resumable |
| Tests | `pytest` | Offline by default (RUN-06) |
| PDF board | `reportlab` or Pillow pages saved as PDF | A board readable on a phone |

## Modules

```
portraits/
  cli.py              commands (RUN-05)
  config.py           load and validate settings; recipe hash vs recipe_version (STY-05)
  keys.py             read keys from the environment or the keys file; never log them (IN-11)
  teachers.py         load and validate teachers.csv (IN-01..03)
  contracts/
    manifest.py       build records; validate against portraits.manifest.schema.json (OUT-02, OUT-04)
    requests.py       read and validate requests.json (IN-06)
    status.py         read and validate status.json (IN-07)
    schemas/          JSON Schemas: the manifest schema copied from Rev1, plus requests and status
  net.py              the one HTTP client: allowlist, User-Agent, rate limit, retry, cache (SRC-01, SRC-09)
  sources/
    licences.py       licence classification (SRC-02)
    wikidata.py       entity fetch, the id sanity check, id resolution (SRC-03 rule 1, SRC-06)
    commons.py        file info and metadata; depicts (P180) search (SRC-03 rule 2)
    loc.py            Prints and Photographs search; heading and dates match (SRC-03 rule 3, SRC-05)
    candidates.py     assemble, de-duplicate, order, exclude set-asides; download with checksum (SRC-07, SRC-08)
  imaging/
    crop.py           (PIP-04)
    descreen.py       (PIP-05)
    halftone.py       (PIP-06, STY-01)
    outline_code.py   the code-drawn outline (PIP-07, proposed)
    outline_extract.py  extract and align a model-drawn line (PIP-07)
    compose.py        composite and master writer; the STY-06 checker
  models/
    client.py         OpenRouter and fal; spend ledger and cap (RUN-04); stub mode (RUN-06)
    precheck.py       (PIP-02)
    cutout.py         (PIP-03)
    outline_model.py  (PIP-07)
    draftcheck.py     (PIP-09), including "compare with target" mode (TRI-08)
    prompts/          prompt text, versioned in the repo
  state.py            SQLite: jobs, candidates, set-asides, attempts, spend, handled requests, deliveries, cache
  pipeline.py         one teacher end to end, with the failure policy (PIP-01..12)
  run.py              the run queue: order, skips, resume (RUN-02, RUN-03)
  deliver.py          folder writer, atomic manifest, originals copy, report, zip (OUT-01..08)
  trial.py            trial set, contenders, scoring, board, writing defaults (TRI-01..08)
stub/
  receiver.py         the receiver stub: enforces the contract on a delivery folder (AC-03)
tests/
  fixtures/           recorded API responses, images, lists, requests/status, sample run
  ...
```

## Data flow for one teacher

```
teachers.csv row
  → Wikidata id check / resolution (SRC-06)
  → candidates from rule 1, rule 2, rule 3 (+ owner link)  → licence filter (SRC-02)
  → order, de-duplicate, drop set-asides (SRC-07)
  → download original (checksum, record)                    [state: originals]
  → PRE-CHECK  (vision model, paid)                         [cache]
  → CUT-OUT    (background model, paid)                     [cache]
  → crop → descreen? → halftone          (code, free)
  → OUTLINE    (image model, paid  |  code, free)           [cache]
  → composite → STY-06 check             (code)
  → DRAFT CHECK (vision model, paid)                        [cache]
  → pass: deliver original copy + master, then manifest record
  → fail: remake or set aside (PIP-10, PIP-11)
```

## State store

- **Location:** `~/.local/share/nexus-portraits/` by default, outside the repo, and changeable in settings.
- **Contents:**
  - `state.db` (SQLite);
  - `originals/` (downloads, named by SHA-256);
  - `cutouts/`, `drafts/` and `cache/` (HTTP and model responses);
  - `logs/`.
- **Tables:**
  - `teachers` (a snapshot of the list per run);
  - `jobs` (per teacher per run: state, step);
  - `candidates`;
  - `originals`;
  - `set_asides`;
  - `attempts` (per draft: outline method, scores, notes, cost);
  - `spend` (per call: run, teacher, step, model, cost, estimated or actual);
  - `handled_requests`;
  - `deliveries` (teacher, run, master SHA-256, request id);
  - `step_cache` (key → artefact path or JSON).

## Settings (layout)

The settings file is `settings.toml` in the repo root. It is committed, and it never holds keys. The values below are illustrative; the real ones come from the prototype and the trial.

```toml
recipe_version = "0.1.0"          # bump on any [recipe] change (STY-05)

[paths]
teachers = "data/teachers.csv"     # Q-14
examples = "design/portraits"
delivery = "/mnt/f/My Drive/…/portraits"   # synced folder (Q-03)
state_dir = "~/.local/share/nexus-portraits"

[sources]
contact = "New Thought Nexus portraits tool; <contact address>"   # User-Agent (SRC-09)

[spend]
run_cap_usd = 250
trial_cap_usd = 40                 # proposed (TRI-07)
precheck_cap_per_teacher = 8       # proposed (PIP-11)

[models]                            # exact model ids confirmed by `doctor` at build time
precheck      = { id = "…", family = "…", est_cost_usd = 0.0 }
cutout        = { id = "…", provider = "fal", est_cost_usd = 0.0 }
outline       = { method = "model", id = "…", family = "google", est_cost_usd = 0.0 }   # or method = "code"
challengers   = [ { id = "…", family = "openai" }, { id = "…", family = "bfl" } ]
draft_check   = { id = "…", family = "…", est_cost_usd = 0.0 }

[recipe]                            # recipe 0.1.0 from the style prototype (prototype/README.md)
size_px = 1000
# crop (PIP-04)
eye_mouth_frac = 0.237
eye_y_frac = 0.443
face_centre_x_frac = 0.50
min_face_px = 90
# tone (STY-01)
white_from_face_p98 = 0.02
black_k = 0.2
gamma = 1.8
sharpen_amount = 0.6
sharpen_radius_cells = 1.0
tone_blur_cells = 0.05
# halftone (STY-01)
dots_across = 110
grid_angle_deg = 45
supersample = 4
# figure mask and outline (STY-02)
mask_smooth_px = 9
body_smooth_px = 28
body_blend_px = 120
outline_gap_px = 2
outline_width_px = 6
```

## Keys

The tool reads these environment variables:

- `OPENROUTER_API_KEY`;
- `FAL_KEY` (only if the cut-out uses fal);
- a Drive credential path, only if Q-03 goes the API way.

If a variable isn't set, the tool reads `~/.config/nexus-portraits/keys.env`. Keys are never logged, and `doctor` reports only whether each key is present.

## Things to verify at build time (not assumed here)

- The exact model ids, and that each one is available through OpenRouter. Also whether a background-removal model is offered there, or only on fal.
- Whether OpenRouter's response includes the actual cost per call. RUN-04 falls back to estimates.
- The Commons API for depicts search. Expected: the search API with `haswbstatement:P180=<Q-id>` in the file namespace, plus `imageinfo` with `extmetadata` for licence, artist and credit. The Commons query service needs a login, so it's avoided.
- The fields of the loc.gov JSON API for Prints and Photographs: names, dates, rights advisory and image links.
- The Wikimedia User-Agent and rate-limit expectations.
