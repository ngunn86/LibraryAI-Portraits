# Architecture (v2, hosted)

**Status (2026-10-20):**
- **Fixed:** hosted on Railway (D-31, D-36); TypeScript, like the library (D-57).
- **Everything else on this page is proposed by Claude** (T-23), for the reviewing agents to challenge.

It replaces v1, the PC-run Python CLI with SQLite, which is in git history.

The aim is the simplest structure that meets the requirements, and that rehearses the library's own toolchain for the harness (D-57):

- one TypeScript repo;
- three Railway services (web, worker, cron) sharing one codebase;
- Postgres for the records and the queue;
- one private bucket for files.

## Stack

| Piece | Choice | Why |
|---|---|---|
| Language and runtime | **TypeScript on Node 24 LTS** (D-57), pinned in `.nvmrc` and `package.json` engines | The library's stack (Rev1 build plan), so the harness rehearses that exact toolchain |
| Web | Express, with `helmet` and `express-rate-limit` | As the library uses |
| Validation | `zod` for settings, request bodies and records; `ajv` (2020-12) to check answers against `contracts/portraits-api.openapi.json` in tests | One schema per shape; the contract test uses the published file itself |
| Database | Postgres (Railway), **Drizzle ORM with drizzle-kit SQL migrations**, run as Railway's pre-deploy command | As the library uses; migrations apply in PR copies, staging and production with no hand step (HT-11) |
| Queue | A `jobs` table in Postgres, claimed with `FOR UPDATE SKIP LOCKED` | No extra service. A job resumes after a redeploy (HT-15, RUN-03) |
| Files | Railway bucket (S3-compatible) through `@aws-sdk/client-s3` and `@aws-sdk/s3-request-presigner` | Private bucket, 15-minute signed links (OUT-12, OUT-14) |
| Image input and output | `sharp` (libvips): decode, colour to sRGB, resize, PNG and JPEG out | Fast and robust; the library already uses it |
| Image processing | **OpenCV.js** (`@techstark/opencv-js`, WebAssembly). It provides: bilateral filter, DFT, warps, ECC alignment, Farneback optical flow, distance transform, connected components, SIFT, RANSAC | The prototype's steps map onto OpenCV functions one to one. See "Porting risks" |
| Face box and landmarks | YuNet (`face_detection_yunet_2023mar.onnx`, MIT, about 230 KB, committed under `models/`), run through OpenCV.js's `FaceDetectorYN` if present, otherwise `onnxruntime-node` with a decoder for YuNet's outputs (see Porting traps) | Free, local and the same every time (PIP-04) |
| HTTP out | Node's `fetch` (undici), wrapped in one client with a host allowlist (SRC-01's list: the adopted sources and their file hosts, OpenRouter, GitHub, the bucket endpoint), User-Agent, pacing, retries and a response cache (SRC-01, SRC-09). It calls `fetch` with `redirect: "manual"` and checks each redirect's target host before following it | One place to enforce rule 5; a redirect can't slip past it |
| AI | OpenRouter only (D-19), through `fetch`, with a spend ledger and caps (RUN-04, D-54). Every request carries `"usage": {"include": true}` so the answer reports its cost. Images go as 8-bit sRGB PNG, never the original file (PIP-22) | One key |
| Admin pages | Server-rendered HTML (a few templates, no client framework), behind one password (RUN-10) | Read-only browsing doesn't need React. The library's React and Vite stay the library's |
| Tests | `node:test` through `tsx --test`, offline by default (RUN-06); `tsc` for types; esbuild for the build | As the library uses |
| Deploys | Railway, configured as code in `.railway/railway.ts` (`railway.toml` stops being read on 2026-12-01). Healthcheck `GET /api/v1/health`, which proves the database and bucket work (RUN-12) | The harness's conductor deploys and checks by itself (HT-03, HT-07, HT-08); `harness.yaml` names the commands and the deploy rules |

## Railway layout

```
project nexus-portraits
  environments:
    pr-<n>      one per pull request, based on staging (never production): its own test database and bucket,
                staging's test credentials, stub mode, no cron, and no AI key where Railway allows (HT-32)
    staging     deployed from `main` on every merge; jobs only when started (RUN-11)
    production  deployed only by the conductor, after the 24-hour veto window (D-66)
  web      node dist/web.js     API (OUT-14), ops jobs (RUN-11) + admin pages (OUT-13); healthcheck /api/v1/health
  worker   node dist/worker.js  claims jobs from Postgres, one teacher at a time (RUN-02, RUN-03)
  cron     node dist/cron.js    nightly: sync the teacher list, queue teachers, exit (RUN-08)
  postgres                      records, queue, rights log, spend ledger; Railway backups (D-42)
  bucket                        portraits/<teacher_id>/<portrait_id>/… (OUT-12)
pre-deploy: drizzle-kit migrate
```

All three services are built from the same repo and image, each with its own start command.

**Production is promoted, never pushed to.** It deploys only the exact commit the conductor promotes, after the window, with a production token kept outside the worker box (Claude's choice: Railway's production environment follows a `production` branch, which only the conductor moves to a commit already merged to `main`). **Production is first deployed at the release (F-47)**, and only then. Before that, everything live (the smoke test, the survey, the trial and the examples) runs on staging, because no check may touch production (the harness's rule, D-65).

## Modules

```
src/
  web.ts · worker.ts · cron.ts        entry points
  cli.ts                              the command frame (RUN-05): loads every file in cli/commands/
  cli/commands/<name>.ts              one file per command (doctor, sync, survey, run, trial, keys, password, status), each owned by the card that adds it. For the owner, from their PC; the harness never runs them on Railway
  jobs/<kind>.ts                      one file per job kind (sync, survey, run, trial, trial_examples, seed_fixtures, and noop for tests), loaded by the worker; started over the web (RUN-11) or by cron
  api/ops.ts                          POST /api/ops/jobs, GET /api/ops/jobs/{id}, GET /api/ops/spend, behind the ops key (RUN-11)
  health.ts                           what /api/v1/health checks (RUN-12)
  config/settings.ts                  the typed, committed settings (no keys); recipe hash vs recipe_version (STY-05)
  config/env.ts                       secrets from the environment (zod); never logged (IN-11, RUN-10)
  db/schema.ts · db/migrations/       Drizzle schema (the records of T-07) and SQL migrations
  queue.ts                            jobs table: enqueue, claim, heartbeat, finish
  net/client.ts                       the one outbound client: allowlist, User-Agent, pacing, retries, cache (SRC-01, SRC-09)
  teachers/sync.ts · enrich.ts        authors.csv via GitHub (IN-12); Wikidata + LoC name authority (IN-13, D-45)
  sources/
    licences.ts                       SRC-02
    wikidata.ts · commons.ts          R1, R2 (SRC-03, SRC-06)
    loc.ts · wellcome.ts              R3 by name and dates or LoC name id (SRC-05, D-47)
    rightsLog.ts · candidates.ts      SRC-07, SRC-08, SRC-12
    survey.ts                         the coverage survey (SRC-14)
  imaging/
    cv.ts                             loads OpenCV.js once; Mat lifetime helpers
    face.ts                           YuNet box and landmarks (PIP-04)
    modelImage.ts                     the PNGs sent to models (PIP-22)
    descreen.ts · crop.ts · align.ts · blend.ts · tone.ts · halftone.ts · mask.ts · outline.ts · versions.ts · checks.ts
    samePhoto.ts                      PIP-20
  models/
    openrouter.ts                     client, spend ledger, caps, stub mode (RUN-04, RUN-06)
    precheck.ts · enhance.ts · cutout.ts · draftCheck.ts · samePhotoCheck.ts · noteKind.ts
    prompts/                          the prompt files, versioned (from prototype/prompts/)
  pipeline/
    teacher.ts                        one teacher end to end: step order, slots, candidates, drafts, failure policy (PIP-01..PIP-23)
    portrait.ts                       one portrait: its files (OUT-11) and the record (SRC-11)
    requests.ts                       the worker's side of the library's requests (IN-06)
    trial.ts                          TRI-01..TRI-09
  api/                                routes, auth, change feed, decisions, requests (OUT-14)
  admin/                              the frame, login and stylesheet (OUT-13)
  admin/pages/<page>.ts               one file per page (front page, teachers, a teacher, runs, a run, rights log, trial board, held originals, keys), loaded by the frame
test/
  fixtures/                           recorded source and model responses, images, the prototype's reference outputs
  *.test.ts
prototype/                            the Python reference (not the product)
```

## Data flow for one teacher

```
teacher (synced from authors.csv; id and dates checked or found, IN-12, IN-13)
  1 → candidates by R1, R2, R3 (+ library try_link) → licence filter (SRC-02;
      CC BY-SA 1.0 held here) → merge exact duplicates                [record]
  2 → fetch previews ≤ 1,600 px, at most 24; note SHA-256 and the original's w × h   [memory/temp only]
  3 → group copies of one photograph (PIP-20) → order copies (SRC-07)
  4 → PRE-CHECK (Haiku) the preview of each photograph's best copy, at most 12   [cache]
      (fails for damage → next copy; face box ×(w, h) → pixels, minFacePx in code)
  5 → choose for open slots: best-known first, then spread across life (PIP-16)
  6 → download the full original of each chosen copy (SHA-256)        [bucket, rights log]
  → face landmarks (YuNet on a ≤ 640 px copy, PIP-04) → crop square   (code)
  → originals over 2,000 px: working region, crop square + 25% (PIP-23)   (code)
  → descreen + edge-preserving blur                                   (code)
  → ENHANCE (Nano Banana Pro): restored copy on flat green            [cache]
      (fails, refused or bad mask → cutout_keyed call, aligned the same way)
  → align + drift check; keyed cut-out; mask mapped back to the original
      (through the alignment and the working region's offset and scale) → mask.png   (code)
  → crop → blend 50% → tone → halftone → mask → code outline          (code)
  → cut-out limits (PIP-19; the 98% piece on the raw cut-out) → white master check (STY-06)   (code)
  → DRAFT CHECK (Sonnet): original view, draft, three examples        [cache]
  → pass: black-and-white version, 500 px copies, viewing copy, record (OUT-11) → status waiting → change feed
  → fail: one remake with a fresh AI copy, then set aside (PIP-10, PIP-11)
```

Steps 1–6 are PIP-21. Nothing in a step needs something a later step makes.

## Database (Drizzle schema)

The tables follow the records of T-07 (`../topics/T-07-records.md`):

- `teachers`
- `candidates` (the rights log)
- `photographs`
- `portraits`
- `files`
- `portrait_events` (history)
- `library_decisions`
- `requests`
- `runs`
- `spend`
- `jobs` (the queue)
- `step_cache`, keyed on the SHA-256s of the images sent, the step, the model, the prompt version, any note and the attempt (RUN-03); never on `recipeVersion`
- `api_keys` (hashes)
- `changes` (the feed, with a sequence)
- `sessions`
- `trial_runs` and `trial_items` (TRI-09): label, example or not, model, blend, scores, cost and file keys under `trial/<trial_run_id>/`. The trial never writes to `portraits`, `candidates` or `changes`
- `app_settings`: small stored values, including `first_pass_state` (`not_started`, `active` or `done`, RUN-04)

`spend` has a `budget` column (`trial`, `trial_examples`, `first_pass` or `regular`); the month cap counts only `regular`.

**Migrations are additive from the first deploy to staging** (RUN-12): add tables and columns; never drop, rename or rewrite in place. A rolled-back release must keep working against the newer database.

## Settings

`src/config/settings.ts` is committed and holds no keys. It carries:
- the recipe (the values in `prototype/recipe.py`, `SETTINGS`, recipe 0.5.0);
- the sources and their pacing;
- the models (D-52);
- the caps (D-54, RUN-10);
- the schedule (RUN-08);
- the allowed hosts (SRC-01);
- the check page colour, `checkPageRgb: [28, 30, 38]` (PIP-09), and the size limits `previewPx: 1600` (PIP-21), `maxWorkingPx: 2000` (PIP-23) and `maxModelImagePx: 1600` (PIP-22);
- `minSpreadYears: 10` (PIP-16) and `maxCandidatesPerTeacher: 24` (PIP-21).

A test fails if the recipe values change without a new `recipeVersion` (STY-05).

## Secrets (Railway variables, per environment)

| Variable | What |
|---|---|
| `OPENROUTER_API_KEY` | The tool's one AI key (D-55, D-67), set in production and staging only; **never in pull-request copies.** Its limit is set at OpenRouter, in steps (O-4) |
| `GITHUB_TOKEN` | Read-only, fine-grained, library-pipeline contents only (D-32, O-9) |
| `SESSION_SECRET` | Signs the admin session (RUN-10). The admin password's hash is in the database, set by `password set` |
| `DATABASE_URL` | From Railway's Postgres (its private hostname works only inside Railway) |
| `DATABASE_PUBLIC_URL` | From Railway's Postgres. The CLI uses `DATABASE_PUBLIC_URL ?? DATABASE_URL`, so the owner can run `railway run portraits …` from their PC. The harness never does (D-65) |
| Bucket variables | From Railway's bucket (endpoint, name, access key, secret) |
| `USER_AGENT_CONTACT` | Not a secret: the contact address in the User-Agent (O-10, SRC-09). Tests use a placeholder |
| `OPS_KEY` | Per environment: the key for starting jobs over the web (RUN-11). Compared as a hash; the harness keeps a copy in its store (O-13) |
| `SEED_ADMIN_PASSWORD`, `SEED_LIBRARY_KEY` | Staging and pull-request copies only: test credentials seeded at start-up, for the harness's smoke checks (RUN-10, O-13). Production never reads them |

`doctor` reports only whether each one is present, never its value.

## Environments (RUN-10)

`RAILWAY_ENVIRONMENT_NAME` picks the rules from settings:

| Environment | Paid calls | Cron | Caps |
|---|---|---|---|
| Pull-request copies | none (stub mode, no key) | none | — |
| Staging | yes, only in jobs started over the web (RUN-11) | none | $2 a night, $10 a month |
| Production | yes | nightly, from its first deploy, which is the release (F-47, after the veto window) | RUN-04 |

The trial runs on staging, under its own $30 budget rather than staging's caps (TRI-06, TRI-07).

## The Python prototype is the reference

`prototype/` stays in Python as the reference implementation of the recipe. The TypeScript port must reproduce `prototype/out/` from `prototype/fixtures/` within tolerances:
- the white master: figure overlap ≥ 0.98 and mean alpha difference ≤ 0.02 against the Python output;
- the black-and-white version, by the same measures;
- the dot pitch, 110 ± 1 across.

This is feature F-16's check. Exact pixel equality isn't expected across two OpenCV builds.

## Porting risks, and what to do about them

The first imaging feature is a **porting spike**. It confirms each OpenCV.js function the recipe needs and compares its output with the Python prototype on the fixtures. Known risks:

| Risk | Fallback |
|---|---|
| `findTransformECC` in OpenCV.js needs all seven arguments (a known quirk) | Pass them all; if it misbehaves, align with feature matching (SIFT + RANSAC), which the same-photo check already uses |
| SIFT missing from the build used | AKAZE or ORB, with PIP-20's thresholds re-measured |
| `FaceDetectorYN` missing | Run the YuNet ONNX file with `onnxruntime-node` |
| `calcOpticalFlowFarneback` missing | Block matching on the face region with `matchTemplate` |
| DFT and bilateral-filter speed or memory in WebAssembly. On a 13-megapixel scan, `bilateralFilter` with `d = -1` gets a kernel about 131 px wide | Work on the working region (PIP-23), never the whole scan |
| The 4,000 × 4,000 halftone threshold map, rebuilt for every portrait | Compute it once per recipe, in one pass, and keep it in memory |
| Leaks: every OpenCV.js `Mat` must be freed by hand | One helper that frees all Mats made inside a step, with a test that memory stays flat over 50 runs |

### Porting traps (argon-8)

These differ between the prototype's numpy, scipy and OpenCV calls and OpenCV.js:

- **`scipy.ndimage.median_filter(M, size=15)` on a float spectrum.** OpenCV's `medianBlur` accepts 32-bit floats only for sizes 3 and 5, and its 8-bit route isn't precise enough: on Cady's original it moves one screen peak by a frequency bin. Compute the median in TypeScript instead: exactly, or on values quantised to 12 bits with a sliding histogram, which finds the prototype's peaks on all three originals. Reflect the border as scipy does (`mode='reflect'`); `medianBlur` would replicate it.
- **`maximum_filter(D, size=5)`** is `cv.dilate` with a 5 × 5 rectangular structuring element.
- **`np.fft.ifft2`** divides by the size; `cv.idft` doesn't unless asked. Always pass `cv.DFT_SCALE | cv.DFT_REAL_OUTPUT`.
- **YuNet's boxes are `[x, y, width, height]`.** The recipe uses `[x0, y0, x1, y1]`. Convert in `face.ts` (x1 = x + w, y1 = y + h), with a test.
- **YuNet's ONNX outputs** are twelve tensors: `cls`, `obj`, `bbox` and `kps` at strides 8, 16 and 32. With `onnxruntime-node`, use `models/face_detection_yunet_2026may.onnx` (dynamic input size), and decode as OpenCV's `FaceDetectorYN` source does. The result must match `prototype/parity/results.json` (`yunet`) within 1 px.
- **YuNet's range:** it finds faces of about 10 to 300 px. Search an original over 640 px on a copy reduced to 640 px.
- **Reference outputs** for each of these operations are committed in `prototype/parity/` (made by `prototype/export_parity.py`), so the porting spike (F-39) compares against them offline. `parity/index.json` names each file's exact call and tolerance. The inputs are the originals as Pillow decoded them (`parity/inputs/*.rgb.png`), so a different JPEG decoder can't cause a mismatch.

## Things to verify at build time (not assumed here)

- The exact OpenRouter model ids and prices (D-52, D-56), confirmed by `doctor`.
- The OpenRouter request shape for image editing, and that answers include the actual cost when `usage.include` is sent (HT-18 checks it first).
- The Commons API for depicts search (`haswbstatement:P180=<Q-id>` in the file namespace) and `imageinfo` with `extmetadata`; Wikimedia's current standard thumbnail widths (for previews, PIP-21).
- The loc.gov JSON fields for names, dates, LoC name ids, rights advisory and image links; Wellcome's licence and contributor fields (marked *confirm* in `../topics/T-11-picture-sources.md`).
- Railway's bucket variables and signed-URL support; the Hobby plan's backup options (HT-12).
- Which OpenCV.js build has every function above (the porting spike).
