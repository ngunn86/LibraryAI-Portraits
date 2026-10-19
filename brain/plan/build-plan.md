# Build plan

Status: **proposed** (Claude, 2026-10-19). It waits for the owner, for the review rounds and for the open questions marked *now* and *build*.

## 1. The shape of the work

| Phase | What | Who | Paid spend (tool key) |
|---|---|---|---|
| **0 · Planning** | Notes, contracts, decisions, Rev1 reconciliation, style prototype, trial set, review rounds | Claude with the owner, in chat; other AI tools review | none |
| **1 · Foundation** | Skeleton, teacher list, contracts and validator, state store, receiver stub (F-01..F-05) | Harness | none |
| **2 · Sources and rights** | Network client, licences, Wikidata, Commons, LoC, candidates (F-06..F-11) | Harness | none (free public APIs, to record fixtures) |
| **3 · Imaging** | Crop, descreen, halftone, code outline, composite, recipe regression (F-12..F-16) | Harness | none |
| **4 · Model steps** | Model client and spend cap, pre-check, cut-out, model outline, draft check (F-17..F-21) | Harness | none (stubbed) |
| **5 · Orchestration and delivery** | Doctor, per-teacher pipeline, delivery, run queue, offline end-to-end run (F-22..F-26) | Harness | none |
| **6 · Live** | Smoke test, trial and board, reproduction of the examples (F-27..F-29) | Harness, using the tool's key | ≤ $2 + ≤ $40 + ≤ $5 |
| **After the build** | First full run over the owner's list (R-1); later runs answer the library's requests | The owner starts it (one command) | ≤ $250 cap |

The project is done when AC-01..AC-06 in [../spec/requirements.md](../spec/requirements.md) are met.

## 2. Phase 0: planning tasks (in this chat)

| # | Task | Needs | Output |
|---|---|---|---|
| P0-1 | Copy in Rev1's portrait files and reconcile every `tool` PORT line with the requirements | O-1 | `brain/reference/rev1/`, the filled reconciliation table, new questions if any; Q-09 and Q-16 resolved |
| P0-2 | Owner answers the questions marked *now* and *build* | the owner | Entries in `decisions.md`; requirement statuses updated |
| P0-3 | **Style prototype** (Q-04): crop, descreen, halftone and code outline against the three examples, side by side, until the owner says it's close | O-2 | `recipe_version` 0.1.0 settings, a reference output per example, the code-metric thresholds, the prototype code kept under `prototype/` as a reference (not the product) |
| P0-4 | **Trial set curation** (TRI-02): about 20 real originals found by the match rules, covering every listed case, each with its expected outcome | O-3 (a first partial list) | `tests/fixtures/trial/trial-set.yaml` (proposed path) |
| P0-5 | Contract files: JSON Schemas for the teacher list, requests and status, plus a sample run made from prototype outputs | P0-1, P0-3 | Schemas and fixtures ready for F-02, F-03 and F-05 |
| P0-6 | Review rounds by other AI tools, merged | P0-1..P0-5 | `brain/reviews/*`, with responses |
| P0-7 | Freeze plan v1: the git tag `plan-v1`, and a status line telling the harness to start | everything above, plus O-7 | Harness starts at F-01 |

## 3. Inputs only the owner can supply

| ID | What | Needed by | Notes |
|---|---|---|---|
| O-1 | Rev1's `brain/spec/portraits.md`, `brain/contracts/portraits.manifest.schema.json` with its sample, and `validate.py`, plus the Rev1 commit they're from | P0-1 (**now**) | Copied into `brain/reference/rev1/` unchanged. Rev1 stays read-only for Claude |
| O-2 | The three hand-made portraits and their originals | P0-3 (**now**) | **Done 2026-10-19** (`design/portraits/`); sources unknown, so test use only (D-13) |
| O-3 | `teachers.csv`: a first partial list (about 25 teachers, Wikidata ids where known), then the full list | P0-4; the full list before R-1 | Format: [../contracts/teachers-csv.md](../contracts/teachers-csv.md) |
| O-4 | The tool's own OpenRouter key (and a fal key if needed), set as environment variables in WSL. Never in chat or the repo | F-27 | A key separate from other projects, so spend is easy to see |
| O-5 | The delivery folder: create `portraits/` in Drive and give its path (or its id, if Q-03 goes the API way) | F-27 | |
| O-6 | The Claude GitHub App installed on this repo (Q-20) | **now** | **Done 2026-10-19** |
| O-7 | The harness, ready to run | Phase 1 | Designed in a separate chat (D-15) |

## 4. Working with the harness

*Provisional until the harness, designed in a separate chat (D-15), settles its format. This section and the card format in `features.md` are this project's interface to it: point the harness chat at them.*

**What the harness reads**

- `CLAUDE.md`, for the rules.
- [features.md](features.md), the feature cards in build order, each in a fixed field format.
- [../spec/requirements.md](../spec/requirements.md), for any ID a card cites.

**Per feature (as the owner has described the harness, D-12)**

1. Build the feature on its own branch.
2. Run the feature's checks: `uv run pytest -m "fNN"`. Then run the whole suite: `uv run pytest`.
3. Have a second and a third model review and check it. An "A" grade means every check passes across models.
4. Open a PR and merge it.
5. Add a line to the digest.

**Blocked features.** A card that needs an owner input (O-n) that isn't there is skipped. The harness goes on with features that don't depend on it, and the digest says what is waiting and on what.

**Live features** (F-27..F-29) spend the tool's key.

- The harness runs them only when the keys are present, and only through the tool's own cap.
- The digest reports what each one spent.

**Parking.** A stuck feature may be parked only if its card says *Parkable: yes*. When a feature is parked, the features that depend on it wait. A stuck feature marked *Parkable: no* stops the build and goes to the digest.

**Never** change a *fixed* requirement, the manifest schema, or the style rules to make a check pass.

**Recipe numbers** (`[recipe]` in settings) come from the prototype and the trial. The harness may change them only through the trial (TRI-06), or in F-29 within the ranges the prototype sets, and always with a `recipe_version` bump.

## 5. Testing approach (D-09: features work reasonably well and without bugs)

- **One command:** `uv run pytest`. It runs offline, with networking blocked by a test fixture, and with no keys.
- **Per-feature checks:**
  - every check on a card is a pytest test marked with the feature (`@pytest.mark.f12`), in a file named after it (`tests/test_f12_crop.py`);
  - so `uv run pytest -m f12` runs one feature's checks.
- **Fixtures:**
  - recorded HTTP responses from Wikidata, Commons and loc.gov, recorded once from the free public APIs and committed;
  - small images, synthetic ones generated in tests plus a handful of real public-domain images;
  - canned model responses, as JSON for the checks and synthetic images for model-drawn outlines;
  - teacher lists;
  - requests and status files;
  - the sample run.
- **Live tests** are marked `@pytest.mark.live`. They are skipped unless `PORTRAITS_LIVE=1` is set and the keys are present, and they are used only by F-27..F-29.
- **Not machine-tested:** whether a portrait looks good. That is judged by the trial's board, the owner's veto and, in the end, the admin's approval in the library.
- **Not wanted:** coverage targets, evaluation suites, statistical scoring.

## 6. Spend plan

| Where | Paid by | Limit |
|---|---|---|
| Coding and reviewing during the build | The owner's subscriptions (Claude, ChatGPT/Codex, Gemini), through the harness | Subscription usage limits |
| F-27 live smoke test (one teacher) | The tool's OpenRouter key (and fal if used) | ≤ $2 |
| F-28 trial (about 23 originals × 3–4 contenders) | The tool's key | ≤ $40 (trial sub-cap; B2 estimate about $30) |
| F-29 reproducing the examples (reuses the trial's cache) | The tool's key | ≤ $5 |
| R-1 first full run, a few hundred teachers | The tool's key | $250 cap (B2 estimate $100–200) |

Fixture recording uses free public APIs, with a polite client (SRC-09).

## 7. After the build

- **R-1, the first full run.** The owner starts it with one command once:
  - AC-01..06 are met;
  - the full `teachers.csv` is in place;
  - the trial's defaults stand.

  The run delivers to the folder, and the report says what was done, spent and left blank.
- **Later runs** answer the library's requests once the library exists (requests first), and try teachers left blank when new candidates appear.

## 8. Risks

| ID | Risk | What reduces it |
|---|---|---|
| R-1 | Matching the hand-made style is tuning by eye, which is hard for an unattended harness | Prototype in Phase 0 (Q-04); F-16 locks the recipe with a regression test |
| R-2 | A model-drawn outline doesn't sit on the dots (the figure gets shifted or rescaled) | An alignment step (PIP-07); the code-drawn contender (Q-05) |
| R-3 | Few certain matches. Many 19th- and early-20th-century teachers may have no Wikidata image, no depicts-tagged Commons file and no dated LoC record, so many will stay blank | Expected and accepted (the rules are fixed). The report lists them; the owner can paste links (SRC-04); finding Wikidata ids (SRC-06b) opens rules 1–2 for more teachers |
| R-4 | Model ids, availability or prices change | Model ids and cost estimates live in settings; `doctor` checks them before a run |
| R-5 | The vision checker passes bad drafts or fails good ones | The admin's approval is the final gate; the trial and board calibrate it; "compare with target" is tested on the examples |
| R-6 | Spend overruns | A cap check before every paid call; the trial sub-cap; dry-run estimates; spend per attempt in the report |
| R-7 | This is the harness's first project, so the harness itself is immature | Small features with offline checks; owner inputs listed up front so the build doesn't stall mid-way; clear parking rules |
| R-8 | Drive sync order, or WSL mount quirks | Write order plus atomic manifest (OUT-03); the library waits for late files; `doctor` checks the folder is writable |
| R-9 | Wikimedia or LoC rate limits or blocks | A polite client with caching (SRC-09); tests use recorded fixtures, so the build doesn't hit the APIs repeatedly |
