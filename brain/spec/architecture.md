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
| Face box and landmarks | YuNet (MIT, a small ONNX file, committed), run through OpenCV.js's `FaceDetectorYN` if present, otherwise `onnxruntime-node` | Free, local and the same every time (PIP-04) |
| HTTP out | Node's `fetch` (undici), wrapped in one client with a host allowlist, User-Agent, pacing, retries and a response cache (SRC-01, SRC-09) | One place to enforce rule 5 |
| AI | OpenRouter only (D-19), through `fetch`, with a spend ledger and caps (RUN-04, D-54) | One key |
| Admin pages | Server-rendered HTML (a few templates, no client framework), behind one password (RUN-10) | Read-only browsing doesn't need React. The library's React and Vite stay the library's |
| Tests | `node:test` through `tsx --test`, offline by default (RUN-06); `tsc` for types; esbuild for the build | As the library uses |
| Deploys | Railway, configured as code in `.railway/railway.ts` (`railway.toml` stops being read on 2026-12-01). Healthcheck `GET /api/v1/health` | The harness deploys and checks by itself (HT-03, HT-07, HT-08) |

## Railway layout

```
project nexus-portraits (environments: production · staging · one per pull request)
  web      node dist/web.js     API (OUT-14) + admin pages (OUT-13); healthcheck /api/v1/health
  worker   node dist/worker.js  claims jobs from Postgres, one teacher at a time (RUN-02, RUN-03)
  cron     node dist/cron.js    nightly: sync the teacher list, queue teachers, exit (RUN-08)
  postgres                      records, queue, rights log, spend ledger; Railway backups (D-42)
  bucket                        portraits/<teacher_id>/<portrait_id>/… (OUT-12)
pre-deploy: drizzle-kit migrate
```

All three services are built from the same repo and image, each with its own start command.

## Modules

```
src/
  web.ts · worker.ts · cron.ts        entry points
  cli.ts                              commands for the harness and owner (railway run): doctor, survey, teacher, keys, password, trial
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
    face.ts                           YuNet box and landmarks
    descreen.ts · crop.ts · align.ts · blend.ts · tone.ts · halftone.ts · mask.ts · outline.ts · versions.ts · checks.ts
    samePhoto.ts                      PIP-20
  models/
    openrouter.ts                     client, spend ledger, caps, stub mode (RUN-04, RUN-06)
    precheck.ts · enhance.ts · cutout.ts · draftCheck.ts · samePhotoCheck.ts
    prompts/                          the prompt files, versioned (from prototype/prompts/)
  pipeline/
    teacher.ts                        one teacher end to end: slots, candidates, drafts, failure policy (PIP-01..PIP-20)
    portrait.ts                       one portrait: the eight files and the record (OUT-11, SRC-11)
    trial.ts                          TRI-01..TRI-08
  api/                                routes, auth, change feed, decisions, requests (OUT-14)
  admin/                              pages and templates (OUT-13)
test/
  fixtures/                           recorded source and model responses, images, the prototype's reference outputs
  *.test.ts
prototype/                            the Python reference (not the product)
```

## Data flow for one teacher

```
teacher (synced from authors.csv; id and dates checked or found, IN-12, IN-13)
  → candidates by R1, R2, R3 (+ library try_link)  → licence filter (SRC-02)
  → group copies of one photograph (PIP-20) → best copy per photograph (SRC-07)
  → choose for open slots: best-known first, then spread across life (PIP-16)
  → download original (SHA-256, rights log)                          [bucket, record]
  → PRE-CHECK (Haiku)                                                 [cache]
  → descreen + edge-preserving blur                                   (code)
  → ENHANCE (Nano Banana Pro): restored copy on flat green            [cache]
  → align + drift check; keyed cut-out (fallback: cutout_keyed call)  (code)
  → crop → blend 50% → tone → halftone → mask → code outline          (code)
  → cut-out limits (PIP-19) → white master check (STY-06)             (code)
  → DRAFT CHECK (Sonnet) on white-1000                                [cache]
  → pass: black-and-white version, 500 px copies, viewing copy, record (OUT-11) → status waiting → change feed
  → fail: one remake with a fresh AI copy, then set aside (PIP-10, PIP-11)
```

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
- `step_cache`
- `api_keys` (hashes)
- `changes` (the feed, with a sequence)
- `sessions`

Additions are additive migrations only, once live.

## Settings

`src/config/settings.ts` is committed and holds no keys. It carries:
- the recipe (the values in `prototype/recipe.py`, `SETTINGS`, recipe 0.4.0);
- the sources and their pacing;
- the models (D-52);
- the caps (D-54, RUN-10);
- the schedule (RUN-08).

A test fails if the recipe values change without a new `recipeVersion` (STY-05).

## Secrets (Railway variables, per environment)

| Variable | What |
|---|---|
| `OPENROUTER_API_KEY` | The tool's one AI key, the same in every environment (D-55); credit limit set at OpenRouter (O-4) |
| `GITHUB_TOKEN` | Read-only, fine-grained, library-pipeline contents only (D-32, O-9) |
| `ADMIN_PASSWORD_HASH`, `SESSION_SECRET` | The admin login (RUN-10) |
| `DATABASE_URL` | From Railway's Postgres |
| Bucket variables | From Railway's bucket (endpoint, name, access key, secret) |

`doctor` reports only whether each one is present, never its value.

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
| DFT speed or memory in WebAssembly | Process at the cell scale the descreen needs, not full resolution |
| Leaks: every OpenCV.js `Mat` must be freed by hand | One helper that frees all Mats made inside a step, with a test that memory stays flat over 50 runs |

## Things to verify at build time (not assumed here)

- The exact OpenRouter model ids and prices (D-52, D-56), confirmed by `doctor`.
- The OpenRouter request shape for image editing, and whether answers include the actual cost.
- The Commons API for depicts search (`haswbstatement:P180=<Q-id>` in the file namespace) and `imageinfo` with `extmetadata`.
- The loc.gov JSON fields for names, dates, LoC name ids, rights advisory and image links; Wellcome's licence and contributor fields (marked *confirm* in `../topics/T-11-picture-sources.md`).
- Railway's bucket variables and signed-URL support; the Hobby plan's backup options (HT-12).
- Which OpenCV.js build has every function above (the porting spike).
