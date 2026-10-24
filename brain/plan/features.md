# Feature cards (build order)

**Status: draft 5 (Claude, 2026-10-23),** for the hosted TypeScript app (D-31..D-71), in the Coding Harness's **format 1** (`../../Coding Harness Instructions.md` §5, D-65). Draft 3 merged Argon's review; draft 4 adapted the cards to the harness, with 18 as a sample that `harness cards check` passed (HD-65); **draft 5 converts the other 34**, so every card is in format 1. Dependencies are settled (no soft dependencies).
- The harness builds them one at a time, **in the order of the overview table**, each once every card in its *Depends on* is merged. IDs are permanent, so the build order isn't numeric. Retired cards keep their IDs as *withdrawn*.

**How checks run** ([build-plan.md §4–5](build-plan.md)):
- **Tests first** (D-65): Codex writes each card's acceptance tests from Gemini's list of cases, in `test/fNN-*.test.ts` with fixtures in `test/fixtures/fNN/`, and they're locked before Claude builds (after the contract, on size L cards). Each test case has a unique name starting with its card's ID (`"F-07: …"`). One card's tests run by path, printing TAP: `./node_modules/.bin/tsx --test --test-reporter=tap "test/f07-*.test.ts"`. F-01, the setup card, skips this step.
- **Each card says what it creates** (module paths and exported names, routes or commands) in its `Goal`, so the test author's tests and the builder's code meet. Exact types are the builder's, within those names.
- **Shared test fixtures** (HD-65): a later card's acceptance tests may import an earlier, merged card's fixtures from `test/fixtures/fNN/`, read-only; they stay locked. Helpers a builder may need to extend live in the product's code (F-04's `openTestDb()`, F-03's `checkAgainstContract`, F-17's `createStubModelClient`, F-37's `createFakeBucket`).
- Offline by default: outbound calls refused, no keys, PGlite for the database.
- **`ctx`** in any card is F-04's `Ctx` (`src/context.ts`): `db`, `env`, `settings`, `clock`, `log`, and the ports `http`, `models` and `bucket`, which F-06, F-17 and F-37 implement. Tests build one with `makeTestCtx(parts?)`.
- **Recordings:** the test author lists the exact request URLs in `test/fixtures/fNN/record.json`, from each source's public API (the test author picks the forms; `brain/spec/sources.md` names the APIs). The builder reads that file and forms its requests the same way; replay matches on the normalised URL (F-06), so only parameter order may differ.
- *Smoke* checks run on a deployed copy (`npm run smoke -- --url {url}`), over HTTP, with that environment's test credentials (O-13): the pull request's copy, or staging for Phase 6's prove-it cards. The harness passes them as `PORTRAITS_OPS_KEY`, `PORTRAITS_TEST_LIBRARY_KEY` and `PORTRAITS_TEST_ADMIN_PASSWORD`, with the copy's address as `{url}` and `HARNESS_URL`, and `HARNESS_ENV` (`staging` or `preview`) (HD-65). Their tests are `test/fNN-*.smoke.ts`, which `npm test` never runs. *Live* checks make paid calls, on staging only. No check touches production.
- **Packages:** only F-01 changes `package.json` and `package-lock.json`. It installs every package in `brain/spec/architecture.md`'s package list and names every npm script the later cards fill in, because `harness cards check` flags two cards owning a file unless one depends on the other. A card that finds it needs another package stops and explains in `BLOCKED.md`; the Tech Lead rules, and planning adds it.
- **Shared files without overlap:** commands (`src/cli/commands/<name>.ts`), job kinds (`src/jobs/<kind>.ts`), admin pages (`src/admin/pages/<page>.ts`) and sources (`src/sources/registered/<name>.ts`) are one file each, loaded from their folder, so each card owns its own file.

## Card format (format 1)

```
### F-NN: Title
- Phase:         1–6
- Goal:          one observable result, with its main example and its failure example,
                 and what it creates (module paths and exported names, routes or commands)
                 ("Prove it" for a card that shows something already works)
- Covers:        the requirement IDs it delivers (IDs only)
- Defers:        requirement IDs it leaves for a later card, and which, or "none"
- Depends on:    cards that must be merged first, or "none" (no soft dependencies)
- Owner input:   owner inputs (O-n) the card can't be built without, or "none"
- Owns:          the files and folders it may change; nothing outside them
                 (never the acceptance tests or their fixtures: those come from the test author)
- Reads:         the spec sections and contracts its packet needs, beyond CLAUDE.md
- Checks:        one per line, each starting with its marks:
                 "blocking" or "report"; "smoke" (on the deployed copy); "live" (paid calls);
                 "needs O-n" (that check waits for the input)
- Test data:     the fixtures it needs, and any recording ("record: npm run record -- F-NN")
- Side effects:  none | network | deploy | migration | paid (≤ $N) | external write | production,
                 with the environments allowed
- Parkable:      yes | no (if it's stuck, can the build go on without it?)
- Size:          S | M | L (L cards get the contract step)
- Stop if:       optional: reasons to stop and ask
```

Each phase ends with a **gate card** (F-53, F-54, F-16, F-55, F-26, F-47), where the verifier adds its tests.

## Overview, in build order

| # | F | Title | Phase | Depends on | Owner input | Side effects | Parkable | Format |
|---|---|---|---|---|---|---|---|---|
| 1 | F-01 | Repo, toolchain and offline test runner | 1 | none | none | none | no | 1 |
| 2 | F-51 | Settings and secrets | 1 | F-01 | none | none | no | 1 |
| 3 | F-03 | The API contract in code | 1 | F-01 | none | none | no | 1 |
| 4 | F-04 | Database, queue and step cache | 1 | F-01, F-51 | none | migration | no | 1 |
| 5 | F-37 | Storage bucket client | 1 | F-01, F-51 | none | none | no | 1 |
| 6 | F-36 | Northflank deploys and the health check | 1 | F-01, F-03, F-04, F-37 | O-8, O-14 | deploy, migration | no | 1 |
| 7 | F-49 | Jobs started over the web | 1 | F-04, F-36 | none | deploy | no | 1 |
| 8 | F-53 | Phase 1 gate | 1 | F-03, F-49 | none | deploy | no | 1 |
| 9 | F-02 | Authors list reader and row checks | 2 | F-01 | none | none | no | 1 |
| 10 | F-06 | Outbound client | 2 | F-01, F-04, F-51 | none | none | no | 1 |
| 11 | F-08 | Wikidata: fetch, check, find ids | 2 | F-06 | none | network | no | 1 |
| 12 | F-31 | Teacher sync through GitHub | 2 | F-02, F-04, F-06, F-08, F-49 | none | network, deploy | no | 1 |
| 13 | F-07 | Licence classifier and credit lines | 2 | F-06 | none | network | no | 1 |
| 14 | F-32 | Rights log | 2 | F-04, F-07 | none | none | no | 1 |
| 15 | F-09 | Commons: P18 and depicts | 2 | F-07, F-08 | none | network | no | 1 |
| 16 | F-10 | Library of Congress pictures | 2 | F-07, F-09, F-32 | none | network | yes | 1 |
| 17 | F-34 | Wellcome Collection | 2 | F-07, F-09, F-32 | none | network | yes | 1 |
| 18 | F-35 | Finding missing dates and ids | 2 | F-08, F-31 | none | network | yes | 1 |
| 19 | F-38 | Coverage survey | 2 | F-09, F-31, F-49 | none | network, deploy | no | 1 |
| 20 | F-54 | Phase 2 gate | 2 | F-32, F-38 | none | none | no | 1 |
| 21 | F-39 | Porting spike: OpenCV.js and sharp | 3 | F-01, F-51 | none | none | no | 1 |
| 22 | F-12 | Face landmarks and crop | 3 | F-39 | none | none | no | 1 |
| 23 | F-13 | Descreen and edge-preserving blur | 3 | F-12 | none | none | no | 1 |
| 24 | F-14 | Tone and halftone | 3 | F-39 | none | none | no | 1 |
| 25 | F-15 | Mask, code outline, master and cut-out limits | 3 | F-12, F-14 | none | none | no | 1 |
| 26 | F-30 | AI copy: key mask, alignment, drift check, blend | 3 | F-12, F-13 | none | none | no | 1 |
| 27 | F-41 | Black-and-white, 500 px, viewing copies and the whole recipe | 3 | F-15, F-30 | none | none | no | 1 |
| 28 | F-42 | Same photograph or different (code layers) | 3 | F-12 | none | none | no | 1 |
| 29 | F-16 | Parity with the Python prototype | 3 | F-13, F-15, F-30, F-41, F-42 | none | none | no | 1 |
| 30 | F-17 | OpenRouter client, spend ledger and caps | 4 | F-04, F-06 | none | none | no | 1 |
| 31 | F-18 | Pre-check | 4 | F-17, F-41 | none | none | no | 1 |
| 32 | F-19 | AI copy and keyed cut-out calls | 4 | F-17, F-30, F-41 | none | none | no | 1 |
| 33 | F-21 | Draft check and compare-with-target | 4 | F-17, F-15, F-41 | none | none | no | 1 |
| 34 | F-43 | Same-photograph tie-break | 4 | F-17, F-41, F-42 | none | none | no | 1 |
| 35 | F-11 | Candidates: gather, previews, group, order | 4 | F-09, F-32, F-37, F-42, F-43 | none | none | no | 1 |
| 36 | F-55 | Phase 4 gate | 4 | F-11, F-18, F-19, F-21 | none | none | no | 1 |
| 37 | F-24 | Publishing a portrait | 5 | F-03, F-04, F-07, F-37, F-41 | none | none | no | 1 |
| 38 | F-23 | Per-teacher pipeline and failure policy | 5 | F-11, F-16, F-18, F-19, F-21, F-24 | none | none | no | 1 |
| 39 | F-25 | Queue, schedule and run reports | 5 | F-23, F-31, F-36 | none | none | no | 1 |
| 40 | F-44 | API: reads, change feed, files, keys | 5 | F-03, F-24, F-49 | none | none | no | 1 |
| 41 | F-45 | API: decisions and requests | 5 | F-44, F-25 | none | none | no | 1 |
| 42 | F-48 | Later runs: better copies, turn-downs, corrections | 5 | F-23, F-45 | none | none | no | 1 |
| 43 | F-46 | Admin site | 5 | F-25, F-32, F-44 | none | none | no | 1 |
| 44 | F-22 | Commands and `doctor` | 5 | F-17, F-25, F-44 | none | none | yes | 1 |
| 45 | F-05 | Library stub | 5 | F-45 | none | none | no | 1 |
| 46 | F-26 | End-to-end offline run | 5 | F-05, F-46, F-48 | none | none | no | 1 |
| 47 | F-27 | Live smoke test on staging | 6 | F-26 | none | paid (≤ $2), staging only; external write | no | 1 |
| 48 | F-28 | The trial, its board and its result | 6 | F-26, F-38 | none | none | no | 1 |
| 49 | F-52 | Run the trial on staging | 6 | F-28 | none | paid (≤ $27), staging only; network; external write | no | 1 |
| 50 | F-50 | The trial's winner in the settings | 6 | F-52 | none | network | no | 1 |
| 51 | F-29 | The examples reproduced | 6 | F-50 | none | paid (≤ $3), staging only; external write | yes | 1 |
| 52 | F-47 | The release | 6 | F-27, F-50 | none | deploy (pull-request copies); production (after the window); external write | no | 1 |
| — | F-20 | ~~Model-drawn outline~~ | — | — | — | — | — | *withdrawn* (D-49) |
| — | F-33 | ~~Internet Archive book plates~~ | — | — | — | — | — | *withdrawn* (D-24) |

**No soft dependencies.** A card lists only the cards that must be merged before it. A card that can be built without another doesn't list it, and its checks don't rely on it. If a parkable card (F-10, F-34, F-35, F-22, F-29) is parked, nothing waits for it: the sources register themselves (F-11), the admin site shows an empty state for F-35's suggestions, and the release doesn't depend on F-29.

F-52 and F-29 share the trial's $30 budget (TRI-07). O-10 (the User-Agent contact) is needed only where a check or a recording calls a live source; offline checks use a placeholder. SCOPE-01..04 are boundaries rather than features; reviewers check them, and F-06's allowlist test enforces AC-06. OUT-08 (the zip) is withdrawn (D-58).

---

## Phase 1: Foundation and deploys

### F-01: Repo, toolchain and offline test runner
- Phase: 1
- Goal: A TypeScript repo on Node 24, matching the library's toolchain, whose `check`, `test` and `build` commands run offline. Main example: `npm test` runs with every outbound call refused and reports how many tests ran. Failure example: a test that tries to reach the network fails at once. This is a setup card: its checks are the commands themselves, so it skips the tests-first step. It installs every package in `brain/spec/architecture.md`'s package list, so no other card changes `package.json`. It creates: the scripts `check`, `test` (`tsx --test` over `test/**/*.test.ts`) and `build` (esbuild, bundling each entry point that exists: `src/cli.ts` now, and `src/web.ts` and `src/worker.ts` once F-36 adds them) in `package.json`, and the scripts later cards fill in, each failing until its file exists: `smoke` (`tsx scripts/smoke.ts`, F-36), `record` (`tsx scripts/record.ts`, F-06), `record-ops` (`tsx scripts/record-ops.ts`, F-49), `check:api` (`tsx scripts/check-api.ts`, F-03) and `library-stub` (`tsx tools/library-stub.ts`, F-05); the command-line entry `src/cli.ts` (`node dist/cli.js <command>`), which loads every file in `src/cli/commands/`, each exporting `command: { name: string; describe: string; run(args: string[]): Promise<number> }`.
- Covers: RUN-06
- Defers: RUN-05 (each command arrives with its own card; F-22 finishes them)
- Depends on: none
- Owner input: none
- Owns: `package.json` (every package and script), `package-lock.json`, `.nvmrc`, `tsconfig.json`, `esbuild.config.mjs`, `test/setup.ts` (the test runner's settings: outbound calls refused, no keys), `test/setup.test.ts`, `src/cli.ts`, `src/cli/commands/`
- Reads: `brain/spec/architecture.md` (Stack, Modules); `harness.yaml` (commands); `brain/plan/build-plan.md` §5
- Checks:
  - blocking: `npm ci` installs from the lock file every package in architecture.md's list, among them `@techstark/opencv-js` and `sharp` (so F-36's health check can report them)
  - blocking: `package.json` names the scripts `smoke`, `record`, `record-ops`, `check:api` and `library-stub`
  - blocking: `npm run check` passes with no keys set
  - blocking: `npm test` passes with every outbound call refused
  - blocking: `./node_modules/.bin/tsx --test --test-reporter=tap "test/setup.test.ts"` prints TAP naming each case, all passing (the form of `harness.yaml`'s `test_card`)
  - blocking: `npm test` runs every `test/**/*.test.ts` and never a smoke test (`*.smoke.ts`), which needs a deployed copy
  - blocking: `npm run build` writes `dist/cli.js`
  - blocking: `node dist/cli.js --help` lists `doctor`, `sync`, `survey`, `run`, `trial`, `keys`, `password` and `status`; one with no file in `src/cli/commands/` yet prints "not built yet" and exits non-zero
- Test data: none
- Side effects: none
- Parkable: no
- Size: S
- Stop if: the test runner can't be made to refuse outbound calls in every test file


### F-51: Settings and secrets
- Phase: 1
- Goal: Typed, committed settings and secrets from the environment. Main example: recipe 0.5.0's settings load and start-up goes ahead. Failure example: a setting of the wrong type, or a recipe change without a new `recipeVersion`, stops start-up and names it. It creates: `settings` and `loadSettings(overrides?)` in `src/config/settings.ts`; `readEnv(env = process.env): Env` (throwing `ConfigError`, which names the variable), with `env.environment` from `PORTRAITS_ENV` and `env.bucket` (`endpoint`, `name`, `accessKeyId`, `secretAccessKey`, `prefix`), in `src/config/env.ts`; `recipeHash(recipe)` and `RECIPE_HASHES` (version → hash) in `src/config/recipeHash.ts`.
- Covers: IN-10, IN-11, STY-05
- Defers: PIP-09 (the family rule is enforced here at start-up, and again at call time in F-17)
- Depends on: F-01
- Owner input: none
- Owns: `src/config/settings.ts`, `src/config/env.ts`, `src/config/recipeHash.ts`
- Reads: `brain/spec/requirements.md` IN-10, IN-11, STY-05, PIP-09, PIP-13, RUN-04, RUN-10; `brain/spec/architecture.md` (Settings, Secrets); `prototype/recipe.py` (`SETTINGS`, `BOX_LANDMARKS`)
- Checks:
  - blocking: F-51 the recipe settings equal recipe 0.5.0's values in `prototype/recipe.py`, including `drift_box_inset` and the box landmarks
  - blocking: F-51 the other settings hold the models, caps, schedule, sources and allowed hosts, plus `checkPageRgb`, `maxModelImagePx`, `previewPx`, `maxWorkingPx`, `minSpreadYears` and `maxCandidatesPerTeacher`
  - blocking: F-51 an invalid setting (wrong type, missing value, unknown source host) stops start-up with a message naming it
  - blocking: F-51 changing a recipe value without a new `recipeVersion` fails, by the recipe block's hash
  - blocking: F-51 a checking model of the same family as an enhance model is refused at start-up
  - blocking: F-51 a missing secret is reported by name only, and no fake secret's value appears in any output
  - blocking: F-51 `PORTRAITS_ENV` must be `production`, `staging` or `preview`; missing or any other value stops start-up, naming it
  - blocking: F-51 the bucket settings come from `S3_ENDPOINT`, `S3_BUCKET`, `S3_ACCESS_KEY_ID` and `S3_SECRET_ACCESS_KEY`; in `preview`, a missing or empty `S3_PREFIX` stops start-up, and outside `preview` a non-empty one does
  - blocking: F-51 `USER_AGENT_CONTACT` fills the User-Agent. Without it, tests use a placeholder; staging and production still start and answer health, but refuse calls to the sources, naming the missing variable
- Test data: valid and invalid settings objects
- Side effects: none
- Parkable: no
- Size: S


### F-03: The API contract in code
- Phase: 1
- Goal: The app's request and answer types follow the contract exactly, and one product helper checks any answer against it. Main example: every sample in the contract's sample file validates with ajv and parses with its zod type. Failure example: a turn-down decision without a reason is refused by both. It creates: `contracts/portraits-api.openapi.json` and `contracts/portraits-api.sample.json`, byte-for-byte copies of the files in `brain/contracts/`; a zod type for every schema in the contract, under the schema's own name (`Portrait`, `Decision`, `Health`, …), in `src/api/schemas.ts`; `checkAgainstContract(schemaName, value): string[]` (ajv 2020-12, compiled once from `contracts/portraits-api.openapi.json`; an empty list means valid) in `src/api/contract.ts`, which later cards' tests use; and `npm run check:api` (`scripts/check-api.ts`, a TypeScript port of `brain/contracts/check_api.py`).
- Covers: OUT-10, AC-02
- Defers: OUT-02 (records written: F-24), OUT-14 (the routes: F-44, F-45), IN-06 and IN-07 (handled: F-45)
- Depends on: F-01
- Owner input: none
- Owns: `contracts/`, `src/api/schemas.ts`, `src/api/contract.ts`, `scripts/check-api.ts`
- Reads: `brain/contracts/portraits-api.openapi.json`, `brain/contracts/portraits-api.md`, `brain/contracts/portraits-api.sample.json` and `brain/contracts/check_api.py`; `brain/spec/requirements.md` OUT-02, OUT-10, OUT-14, IN-06, IN-07
- Checks:
  - blocking: F-03 every sample in `contracts/portraits-api.sample.json` validates against its schema with `checkAgainstContract`, and parses with the matching zod type, paired as `check_api.py` pairs them
  - blocking: F-03 the thirteen payloads `check_api.py` refuses are refused by both ajv and zod (among them a turn-down without a reason, an unknown field in a decision, an `approx_date` given as text, a `refused_reason` that isn't one of the codes, and a health answer without `database`)
  - blocking: F-03 zod and ajv agree on 10 good and 10 bad generated payloads per request body, including a `correct` decision whose `value` doesn't suit its `field`
  - blocking: F-03 `contracts/portraits-api.openapi.json` and `contracts/portraits-api.sample.json` are byte-for-byte the same as their originals in `brain/contracts/`
  - blocking: F-03 `npm run check:api` reports the same counts as `check_api.py` (today 24 schemas, 18 samples and 13 refused payloads, with no failures) and exits 0
- Test data: none beyond the contract's own samples
- Side effects: none
- Parkable: no
- Size: S


### F-04: Database, queue and step cache
- Phase: 1
- Goal: The records in Postgres through Drizzle, a job queue that survives crashes, and a cache of paid step results. Main example: the migrations run from empty and every table records and reads back. Failure example: a job whose worker stops is claimed again and resumes at its last finished step. It creates: the Drizzle tables in `src/db/schema.ts`, named as in T-07; `openDb(url)` and `openTestDb()` (PGlite, migrated, for every later card's tests) in `src/db/client.ts`; `enqueue` (with an optional priority), `claim` (highest priority first, then oldest), `heartbeat`, `finish`, `fail` and `reclaimStale` in `src/queue.ts`; `cacheKey({ images, step, model, promptVersion, note, attempt })`, `getCached` and `putCached` in `src/cache.ts`; and the context every pipeline and job function takes, `Ctx` (`db`, `env`, `settings`, `clock`, `log`, and the ports `http`, `models` and `bucket`, declared here as small interfaces: `HttpPort` with `get` and `getJson`, `ModelPort` with `call`, `BucketPort` with `put`, `get`, `signedUrl` and `check`), and `makeTestCtx(parts?): Promise<Ctx>` (a migrated PGlite database, a fake clock, a silent log, and ports that refuse every call unless the test passes its own), in `src/context.ts`.
- Covers: RUN-03
- Defers: RUN-04 (the spend ledger is stored here; caps in F-17, the first pass in F-25), PIP-12 (set-asides used in F-23), IN-08 (applied once in F-45), TRI-09 (the trial tables are used in F-28)
- Depends on: F-01, F-51
- Owner input: none
- Owns: `src/db/schema.ts`, `src/db/migrations/`, `src/db/client.ts`, `drizzle.config.ts`, `src/queue.ts`, `src/cache.ts`, `src/context.ts`
- Reads: `brain/topics/T-07-records.md` (with its additions of 2026-10-20); `brain/spec/architecture.md` (Database); `brain/spec/requirements.md` RUN-03, RUN-04, RUN-12, TRI-09
- Checks:
  - blocking: F-04 the migrations run from empty, and every table records and reads back (`teachers`, `candidates`, `photographs`, `portraits`, `files`, `portrait_events`, `library_decisions`, `requests`, `runs`, `spend` with its `budget`, `jobs`, `step_cache`, `api_keys`, `changes`, `sessions`, `trial_runs`, `trial_items`, `app_settings`), each with the fields in `brain/topics/T-07-records.md`, its additions of 2026-10-20 included (the teacher's `lcnaf_id`, `ids_from`, `dates_from`, `key_works` and `suggestion`)
  - blocking: F-04 two workers claiming at once never get the same job (two connections)
  - blocking: F-04 a job queued with a higher priority is claimed before older ones
  - blocking: F-04 `makeTestCtx()` gives a context on a migrated PGlite database with a fake clock, whose `http`, `models` and `bucket` refuse every call unless the test passes its own
  - blocking: F-04 a job whose worker stops heartbeating is claimed again after the timeout, and resumes at its last finished step
  - blocking: F-04 the step cache hits for the same key, and misses when any image's SHA-256, the step, the model, the prompt version, the note or the attempt changes
  - blocking: F-04 a remake (attempt 1) and a `try_again` without a note both miss; changing `recipeVersion` alone still hits
  - blocking: F-04 the `changes` table hands out increasing sequence numbers, also inside concurrent transactions
  - blocking: F-04 no migration drops, renames or rewrites a table or column (RUN-12)
- Test data: a PGlite helper that later cards' tests reuse
- Side effects: migration (pull-request copies, staging)
- Parkable: no
- Size: M


### F-37: Storage bucket client
- Phase: 1
- Goal: Store and fetch a portrait's files in the environment's private bucket on Cloudflare R2 (D-70), under OUT-12's layout and the copy's prefix, and hand out 15-minute signed links. Main example: a file put under `portraits/charles-fillmore/charles-fillmore-1/white-1000.png` comes back with the same bytes, content type and SHA-256. Failure example: a key outside the layout, or an id containing `/` or `..`, is refused before any call. It creates: `createBucket(settings: BucketSettings, s3?: S3Client): Bucket` and `createFakeBucket(): Bucket` (in memory, for later cards' tests) in `src/storage/bucket.ts`, where `Bucket` has `put(key, bytes, contentType): Promise<{ sha256 }>`, `get(key): Promise<{ bytes, contentType, sha256 }>`, `signedUrl(key, seconds = 900): Promise<string>` and `check(): Promise<void>` (which writes and reads `health/check`, the one key outside the layout, for F-36's health check); and `portraitKey(teacherId, portraitId, file)` and `trialKey(trialRunId, file)` in `src/storage/layout.ts`.
- Covers: OUT-12
- Defers: OUT-14 (signed links served by the API: F-44), RUN-10 (keys, login and caps: F-44, F-46, F-17)
- Depends on: F-01, F-51
- Owner input: none
- Owns: `src/storage/bucket.ts`, `src/storage/layout.ts`
- Reads: `brain/spec/requirements.md` OUT-12, OUT-14, RUN-10; `brain/spec/architecture.md` (Stack: Files; Secrets: the `S3_` variables)
- Checks:
  - blocking: F-37 putting and getting a file round-trips its bytes, content type and SHA-256
  - blocking: F-37 keys follow `portraits/<teacher_id>/<portrait_id>/<file>` or `trial/<trial_run_id>/<file>`; any other key, or an id with `/`, `..` or other path characters, is refused before any call
  - blocking: F-37 with a prefix (`pr-12/`), every key written or read starts with it, and the layout check applies after it
  - blocking: F-37 a signed link is asked for with a 900-second expiry, on a stubbed S3 client
  - blocking: F-37 the real client is built with the settings' endpoint, region `auto` and bucket name, on a stubbed S3 client
  - blocking: F-37 `check()` writes and reads `health/check`, and nothing else outside the layout
  - blocking: F-37 the bucket has no delete method
- Test data: small files, made in the tests
- Side effects: none
- Parkable: no
- Size: S


### F-36: Northflank deploys and the health check
- Phase: 1
- Goal: The app builds from its `Dockerfile` on Northflank and runs as a web and a worker deployment service from one build, in the layout the harness needs (harness HD-70, D-72; the owner sets the projects up with the harness chat, O-8); it migrates itself at start-up, and its health check proves it really works. Main example: the pull request's copy (the `pr-copy` preview blueprint) answers `/api/v1/health` with this commit, and the database and bucket working. Failure example: with the database unreachable, health answers 503 and names it. It creates: the `Dockerfile` and `.dockerignore` (Node 24; `npm ci`, `npm run build`; `node dist/web.js` and `node dist/worker.js` as the two start commands); `createApp(deps)` (Express) in `src/web.ts`, serving `GET /api/v1/health` (readiness) and `GET /api/v1/live` (liveness); `checkHealth(deps): Promise<Health>` in `src/health.ts`; `hashSecret(plain)` and `verifySecret(plain, hash)` in `src/auth/hash.ts`; `seedTestCredentials(db, env)` in `src/config/seed.ts`; the worker's entry (`src/worker.ts`) and an empty nightly tick, `nightly(ctx)` (`src/cron.ts`), which F-25 fills; `runMigrations(db)` in `src/migrate.ts`, which both entry points call at start-up under a Postgres advisory lock; `npm run smoke -- --url <url>` (`scripts/smoke.ts`); and `docs/northflank-setup.md`, the settings each service needs (start command, port, health checks, secret group), for the owner and the harness chat.
- Covers: RUN-01, RUN-12
- Defers: RUN-08 (the nightly tick's work: F-25), RUN-10 (keys, login and caps: F-44, F-46, F-17)
- Depends on: F-01, F-03, F-04, F-37
- Owner input: O-8, O-14
- Owns: `Dockerfile`, `.dockerignore`, `src/web.ts`, `src/worker.ts`, `src/cron.ts`, `src/migrate.ts`, `src/health.ts`, `src/auth/hash.ts`, `src/config/seed.ts`, `scripts/smoke.ts`, `docs/northflank-setup.md`
- Reads: `brain/spec/architecture.md` (Stack, Northflank layout, Modules, Secrets, Environments); `brain/spec/requirements.md` RUN-01, RUN-10, RUN-12, OUT-12; the contract's `Health`, `/api/v1/health` and `/api/v1/live`; `harness.yaml` (deploy); `brain/handoffs/harness-throwaway-test.md` (what HT-02..HT-04, HT-11..HT-13, HT-32 and HT-33 proved)
- Checks:
  - blocking: F-36 health answers 200 with the version, the commit, the environment's name, the database's and bucket's names, and `database`, `bucket`, `opencv` and `sharp` true, against working fakes
  - blocking: F-36 no health answer contains a secret or a connection string
  - blocking: F-36 with the database or the bucket failing (faked), health answers 503 and names it in `failing`, while `/api/v1/live` still answers 200
  - blocking: F-36 `runMigrations` brings an empty database up to date, and run again changes nothing
  - blocking: F-36 two services starting at once both call `runMigrations`, and the migrations are applied once (the advisory lock)
  - blocking: F-36 health's answers validate against the contract's `Health`
  - blocking: F-36 in staging and pull-request environments, start-up seeds the test admin password's hash as `app_settings.admin_password_hash` and the test library key's hash as an `api_keys` row labelled `test`; in production it never does
  - blocking: F-36 the empty nightly tick returns "nothing to do"
  - blocking: F-36 `npm run smoke -- --url <url>` runs every `test/**/*.smoke.ts` (and nothing else) against that address (or `HARNESS_URL` without `--url`), and the tests read the test credentials from `PORTRAITS_OPS_KEY`, `PORTRAITS_TEST_LIBRARY_KEY` and `PORTRAITS_TEST_ADMIN_PASSWORD`
  - blocking: F-36 the `Dockerfile` builds with `npm ci` and `npm run build`, and holds no secret value (the scan finds none of the fake secrets)
  - blocking, smoke: F-36 the deployed copy's `/api/v1/health` answers 200 with this commit, and the database and bucket working
  - blocking, smoke: F-36 the pull request's copy names its own environment, database and bucket, none of them production's
- Test data: none
- Side effects: deploy (pull-request copies), migration (pull-request copies, staging)
- Parkable: no
- Size: M
- Stop if: the services can't be set up in the layout `brain/spec/architecture.md` gives (O-8): ask on the control issue


### F-49: Jobs started over the web
- Phase: 1
- Goal: The harness starts work on a deployed copy over HTTPS, never through the host's command line. Main example: `POST /api/ops/jobs` with the ops key and kind `noop` answers 202, and the job's state reads `done`. Failure example: without the ops key, 401; a trial job on a pull-request copy is refused. It creates: `opsRouter(deps)` in `src/api/ops.ts`, serving `POST /api/ops/jobs`, `GET /api/ops/jobs/{id}` and `GET /api/ops/spend`; `loadJobKinds()` and the type `JobKind = { kind; environments; run(ctx, params): Promise<report> }` in `src/jobs/index.ts`; the `noop` kind; and `npm run record-ops -- F-NN --kind <kind> --url <url>`.
- Covers: RUN-11
- Defers: none (each job kind arrives with its own card)
- Depends on: F-04, F-36
- Owner input: none
- Owns: `src/api/ops.ts`, `src/jobs/index.ts` (loads every file in `src/jobs/`), `src/jobs/noop.ts`, `src/web.ts` and `src/worker.ts` (to mount the routes and load the jobs), `scripts/record-ops.ts`
- Reads: `brain/spec/requirements.md` RUN-04, RUN-10, RUN-11; `brain/spec/architecture.md` (Modules, Secrets, Environments)
- Checks:
  - blocking: F-49 `POST /api/ops/jobs` without the ops key answers 401, and with a wrong one 401
  - blocking: F-49 a `noop` job answers 202 with an id; `GET /api/ops/jobs/{id}` shows it `queued`, then `done` with its report
  - blocking: F-49 an unknown kind answers 422, naming it
  - blocking: F-49 each environment's rules hold, with stand-in kinds: `trial` and `trial_examples` are refused outside staging, and `seed_fixtures` in production
  - blocking: F-49 `GET /api/ops/spend` sums fixture spend by environment, budget and cap
  - blocking: F-49 a new file in `src/jobs/` is picked up without editing any other file
  - blocking: F-49 `npm run record-ops -- F-NN --kind <kind> --url <url>` fetches the latest finished job of that kind from that address, with the ops key in `PORTRAITS_OPS_KEY`, and saves its report in `test/fixtures/fNN/`
  - blocking, smoke, needs O-13: F-49 on the deployed copy, a `noop` job started with its ops key finishes
- Test data: none
- Side effects: deploy (pull-request copies)
- Parkable: no
- Size: S


### F-53: Phase 1 gate
- Phase: 1
- Goal: Prove it: the foundation holds together on a deployed copy (health, migrations, the bucket and jobs over the web), with no secret anywhere. This is Phase 1's gate card; the verifier adds its tests here. It creates nothing: it's a gate.
- Covers: none
- Defers: none
- Depends on: F-03, F-49
- Owner input: none
- Owns: none
- Reads: `brain/plan/build-plan.md` §4–5
- Checks:
  - blocking: `npm test` (the full suite)
  - blocking: F-53 a scan of the repo and of the suite's output finds none of the fake secrets
  - blocking, smoke, needs O-13: F-53 on the deployed copy, health answers 200 and a `noop` job finishes
- Test data: none
- Side effects: deploy (pull-request copies)
- Parkable: no
- Size: S


---

## Phase 2: Teachers and sources

### F-02: Authors list reader and row checks
- Phase: 2
- Goal: Read library-pipeline's `authors.csv`, keep the active rows, read their dates and optional ids, and report bad rows by number while the rest load. Main example: a 12-row fixture yields exactly its active rows, with aliases split on `;`. Failure example: a row whose death year comes before its birth year is reported with its row number, and the other rows load. It creates: `parseAuthors(csvText: string): AuthorsRead` (`{ rows: AuthorRow[]; problems: RowProblem[] }`), which throws `AuthorsFileError` for a whole-file refusal, and `parseDates(text: string): { born?: number; died?: number } | null`, in `src/teachers/authors.ts`.
- Covers: IN-01, IN-02, IN-03, IN-05
- Defers: IN-12 (read through GitHub and turned into teachers: F-31), AC-01 (the whole sync: F-31, F-26)
- Depends on: F-01
- Owner input: none
- Owns: `src/teachers/authors.ts`
- Reads: `brain/spec/requirements.md` IN-01..IN-05, IN-12; `brain/decisions.md` D-45, D-60
- Checks:
  - blocking: F-02 a fixture with the real file's header and 12 rows (active, proposed and excluded; dates `1854-1948`, `d. 1925`, `b. 1870`, blank and unreadable) yields exactly the active rows, with aliases split on `;`
  - blocking: F-02 each row problem is reported with its row number while the other rows load: a missing name, an unreadable date, death before birth, a lifespan over 120 years, a future year, a malformed `wikidata_qid` or `lcnaf_id`
  - blocking: F-02 a file without the optional `wikidata_qid` and `lcnaf_id` columns reads as before; with them, good ids (`^Q[1-9][0-9]*$`, `^n[a-z]?[0-9]+$`) are read
  - blocking: F-02 `key_works` is split into titles, without their bracketed years and edition notes
  - blocking: F-02 a whole-file refusal (not UTF-8, no header, no `name`, `status` or `dates` column, no active rows) throws `AuthorsFileError` naming the reason
  - blocking: F-02 changing a row's stream or tier changes only its `notes`
- Test data: about eight small CSV fixtures, one with the real file's header
- Side effects: none
- Parkable: no
- Size: S


### F-06: Outbound client
- Phase: 2
- Goal: One HTTP client for every outbound call, with SRC-01's allowlist, an identifying User-Agent, per-source pacing, retries, a cache, and recording and replay for tests. Main example: a GET to `www.wikidata.org` carries the User-Agent, and a second identical GET is served from the cache. Failure example: a request to `example.com` fails before leaving the process, naming the host. It creates: `createHttpClient(opts): HttpClient` in `src/net/client.ts`, with `get(url, init?)` and `getJson(url)`, where `opts` has `mode` (`live`, `record` or `replay`), `fixtureDir`, `transport` and `clock`, and the errors `HostNotAllowedError` and `NoRecordingError`; and `npm run record -- F-NN` (`scripts/record.ts`), which fetches the URLs listed in `test/fixtures/fNN/record.json` through this client and saves each response beside it.
- Covers: SRC-01, SRC-09, SRC-10, RUN-06, AC-06
- Defers: none
- Depends on: F-01, F-04, F-51
- Owner input: none
- Owns: `src/net/client.ts`, `scripts/record.ts`
- Reads: `brain/spec/requirements.md` SRC-01, SRC-09, SRC-10, RUN-06; `brain/spec/sources.md` (each source's limits); `brain/spec/architecture.md` (Stack: HTTP out)
- Checks:
  - blocking: F-06 a request to a host outside the allowlist fails before leaving the process, naming it. The allowlist is SRC-01's: `www.wikidata.org`, `commons.wikimedia.org`, `upload.wikimedia.org`, `www.loc.gov`, `loc.gov`, `tile.loc.gov`, `id.loc.gov`, `api.wellcomecollection.org`, `iiif.wellcomecollection.org`, `openrouter.ai`, `api.github.com` and the bucket's endpoint host
  - blocking: F-06 the client calls `fetch` with `redirect: "manual"`; a redirect to an allowed host is followed (up to 5), and one to any other host is refused, naming it
  - blocking: F-06 every request carries the User-Agent from settings: name, version and contact
  - blocking: F-06 on a fake clock, LoC calls are spaced evenly, one every 3 seconds (30 take at least 87 seconds), and Wikimedia and Wellcome calls never overlap
  - blocking: F-06 a 429, a 503 and an HTML CAPTCHA page each back off and retry up to the limit; a 404 isn't retried
  - blocking: F-06 a second identical GET within the cache's lifetime is served from the cache
  - blocking: F-06 in replay mode, recorded responses are served with no network, matched on the normalised URL (scheme and host in lower case, query parameters sorted); a request with no recording throws `NoRecordingError` naming the URL
  - blocking: F-06 in record mode, each response is saved with its URL, status, headers and body, and replay serves it back unchanged
- Test data: a fake transport and clock; a CAPTCHA page sample
- Side effects: none
- Parkable: no
- Size: M


### F-08: Wikidata: fetch, check, find ids
- Phase: 2
- Goal: Read a teacher's Wikidata item, check a given id, and search for a missing one as SRC-06 allows. Main example: Charles Fillmore's id returns his P18 file, 1854 and 1948, and his LoC name id. Failure example: an id that isn't a human, or whose years disagree with the teacher's, is refused with the reason. It creates: `fetchPerson(client, qid): Promise<WikidataPerson>`, `checkId(client, qid, teacher): Promise<IdCheck>` (accepted, or refused with a reason) and `searchPeople(client, teacher): Promise<WikidataPerson[]>` in `src/sources/wikidata.ts`, where `WikidataPerson` holds the id, labels, aliases, birth and death years, P18 file name, LoC name id (P244) and works.
- Covers: SRC-03, SRC-06
- Defers: IN-13 (agreement with the LoC name authority: F-35), IN-04 (eligibility, set at sync: F-31)
- Depends on: F-06
- Owner input: none
- Owns: `src/sources/wikidata.ts`
- Reads: `brain/spec/requirements.md` SRC-03, SRC-06, IN-04, IN-13; `brain/spec/sources.md` (Wikidata)
- Checks:
  - blocking: F-08 a good id returns its P18 file name, birth and death years, labels and aliases, and its LoC name id (P244) when present
  - blocking: F-08 an id that isn't a human, or whose years disagree with the teacher's, is refused with the reason
  - blocking: F-08 the search finds humans whose label or alias matches the teacher's name or an alias (normalised) and who have both years on Wikidata; any years the teacher already has must match
  - blocking: F-08 each person found comes with their id, years, LoC name id and works (P800, and items whose author P50 is them, found with `haswbstatement:P50=<Q-id>` in Wikidata's own search on `www.wikidata.org`, never the query service)
  - blocking: F-08 no match, or a year mismatch, returns nothing; several people are all returned, for F-35 to tell apart
- Test data: record: `npm run record -- F-08` (needs O-10), fetching what `test/fixtures/f08/record.json` lists: about six real teachers and the edge cases
- Side effects: network (the recording only)
- Parkable: no
- Size: S


### F-31: Teacher sync through GitHub
- Phase: 2
- Goal: Sync the active authors from the private library-pipeline repo into the database, with stable teacher ids, as a job and by command. Main example: a recorded `authors.csv` syncs to the expected teachers, and a second sync changes nothing. Failure example: a broken file leaves the existing teachers exactly as they were. It creates: `syncTeachers(db, csvText, opts): Promise<SyncReport>` in `src/teachers/sync.ts`; `fetchAuthorsCsv(client, token): Promise<string>` in `src/teachers/github.ts`; the job kind `sync`; the command `portraits sync`.
- Covers: IN-01, IN-03, IN-04, IN-12
- Defers: AC-01 (the whole chain: F-26), RUN-08 (nightly, through the worker's nightly tick: F-25)
- Depends on: F-02, F-04, F-06, F-08, F-49
- Owner input: none
- Owns: `src/teachers/sync.ts`, `src/teachers/github.ts`, `src/jobs/sync.ts`, `src/cli/commands/sync.ts`
- Reads: `brain/spec/requirements.md` IN-01..IN-05, IN-12, SRC-06; `brain/decisions.md` D-45, D-60; `brain/spec/architecture.md` (Secrets: `GITHUB_TOKEN`)
- Checks:
  - blocking: F-31 a recorded GitHub contents response syncs to the expected teachers
  - blocking: F-31 a second sync with the same file changes nothing: no new rows, no `record_version` bumps, no change-feed entries
  - blocking: F-31 a renamed author keeps its `teacher_id`, matched by id, then by normalised name, then by a shared name or alias with compatible years; inserting a row above it changes nothing
  - blocking: F-31 a clashing slug gets `-2` and is reported
  - blocking: F-31 an author no longer active gets `on_list = false`, and their portraits are untouched
  - blocking: F-31 ids from the optional columns are stored with `ids_from = list` and checked with F-08 (SRC-06a); one that fails is refused for that row, with its reason
  - blocking: F-31 each teacher's eligibility (IN-04) is set: `qid`, `lcnaf_or_years` or `none`
  - blocking: F-31 a broken file (F-02's whole-file refusals) leaves the existing teachers exactly as they were
  - blocking: F-31 the only GitHub call is a GET of `collection/authors.csv`; the client has no write method
  - report, smoke, needs O-9, needs O-13: F-31 a `sync` job on the deployed copy reads the real `authors.csv` and reports 182 ± 20 active authors
- Test data: a GitHub contents response in GitHub's own format, with a fixture CSV (made by hand; no recording needed)
- Side effects: network (GitHub, in the smoke check), deploy (pull-request copies)
- Parkable: no
- Size: M


### F-07: Licence classifier and credit lines
- Phase: 2
- Goal: Map any Commons, LoC or Wellcome rights statement to tier 1, tier 2, held or refused, and build each file's licence and credit line. Main example: "No known restrictions on publication" is tier 1. Failure example: CC BY-NC is refused, and CC BY-SA 1.0 is held before anything is spent. It creates: `classifyLicence(evidence: RightsEvidence): LicenceVerdict` (tier 1 or 2, or `held` or `refused` with a reason and the raw text) and `adaptationLicence(verdict)` in `src/sources/licences.ts`; `originalCredit(record)` and `adaptationCredit(record, fileKind)` in `src/sources/credits.ts`.
- Covers: SRC-02, SRC-11
- Defers: none
- Depends on: F-06
- Owner input: none
- Owns: `src/sources/licences.ts`, `src/sources/credits.ts`
- Reads: `brain/spec/requirements.md` SRC-02, SRC-08, SRC-11; `brain/spec/sources.md` (Rights, per kind of evidence)
- Checks:
  - blocking: F-07 public-domain marks, CC0, "No known restrictions on publication" and Wellcome's PDM classify as tier 1
  - blocking: F-07 CC BY in several versions, and CC BY-SA 2.0 and later, classify as tier 2
  - blocking: F-07 CC BY-SA 1.0 is `held`, with its reason, and never becomes a candidate
  - blocking: F-07 NC, ND, fair use, GFDL alone, "rights status not evaluated" and blank are refused
  - blocking: F-07 the 40 or more recorded strings each get their expected class
  - blocking: F-07 a dual-licensed file takes its most open allowed licence; an unknown string is refused, and its raw text is kept
  - blocking: F-07 adaptation licences follow SRC-11's table: CC0 1.0, CC BY 4.0, CC BY-SA 4.0
  - blocking: F-07 credit lines match SRC-11's formats, including its example and "Portrait by New Thought Nexus, adapted from: …"
- Test data: record: `npm run record -- F-07` (needs O-10), fetching the records listed in `test/fixtures/f07/record.json`: about 40 real Commons, LoC and Wellcome records with their rights statements
- Side effects: network (the recording only)
- Parkable: no
- Size: S


### F-32: Rights log
- Phase: 2
- Goal: Keep one permanent row for every original considered, refusals included, with its evidence, verdict, match and credit, and export it as CSV. Main example: recording the same original twice keeps one row and adds to its history. Failure example: a candidate missing its credit line is refused, naming the field. It creates: `recordOriginal(db, entry: RightsEntry): Promise<RightsRow>`, `findRefusal(db, source, sourceId): Promise<RightsRow | null>`, `listHeld(db): Promise<RightsRow[]>` and `exportRightsCsv(db): Promise<string>` in `src/sources/rightsLog.ts`.
- Covers: SRC-08, SRC-12
- Defers: none
- Depends on: F-04, F-07
- Owner input: none
- Owns: `src/sources/rightsLog.ts`
- Reads: `brain/spec/requirements.md` SRC-02, SRC-08, SRC-12; `brain/topics/T-07-records.md` (Candidate); `brain/decisions.md` D-14
- Checks:
  - blocking: F-32 recording the same original twice keeps one row, keyed by source and source id (and its SHA-256 once downloaded), and adds to its history
  - blocking: F-32 a refused original keeps its reason, and `findRefusal` finds it, so a later run doesn't research it
  - blocking: F-32 a `held` original keeps its verdict and appears in `listHeld`
  - blocking: F-32 a candidate missing its source, item link, licence or credit line is refused, naming the field (SRC-08)
  - blocking: F-32 the CSV export has every SRC-08 and SRC-12 field, with the raw record kept beside it
- Test data: records from F-07's fixtures (`test/fixtures/f07/`, read-only)
- Side effects: none
- Parkable: no
- Size: S


### F-09: Commons: P18 and depicts
- Phase: 2
- Goal: Turn a teacher's P18 image and their depicts-tagged Commons files into candidates, with licence, author and credit, and start the registry every source joins. Main example: Charles Fillmore's P18 file becomes a `wikidata_p18` candidate with its licence, author, credit, size and file link. Failure example: a file that is only in the teacher's Commons category, not tagged as depicting them, is not a candidate. It creates: `commonsCandidates(client, teacher): Promise<FoundCandidate[]>` in `src/sources/commons.ts` (`imageinfo` with `extmetadata`; search with `haswbstatement:P180=<Q-id>` in the file namespace); `loadSources(): RegisteredSource[]` in `src/sources/registry.ts`, which loads every file in `src/sources/registered/`, each exporting `source: { name: string; hosts: string[]; find(client, teacher): Promise<FoundCandidate[]>; fetchById(client, id): Promise<FoundCandidate | null> }` (`fetchById` reads one item a pasted link names, for `try_link`); and `src/sources/registered/commons.ts`.
- Covers: SRC-03, SRC-08, AC-06
- Defers: SRC-05 (the LoC and Wellcome: F-10, F-34), SRC-12 (rights-log rows, written by the gatherer: F-11)
- Depends on: F-07, F-08
- Owner input: none
- Owns: `src/sources/commons.ts`, `src/sources/registry.ts`, `src/sources/registered/commons.ts`
- Reads: `brain/spec/requirements.md` SRC-02, SRC-03, SRC-08, PIP-21; `brain/spec/sources.md` (Commons)
- Checks:
  - blocking: F-09 the P18 file becomes a `wikidata_p18` candidate with its licence, author, credit, size and file link
  - blocking: F-09 each depicts-tagged file becomes a `commons_p180` candidate; a file only in the teacher's category doesn't
  - blocking: F-09 non-image files (PDF, DjVu, audio) are skipped
  - blocking: F-09 each candidate records a preview link at the largest of Wikimedia's standard thumbnail widths not over 1,600 px, beside the full file link and the full width and height from `imageinfo`
  - blocking: F-09 a file with a refused licence comes back marked refused, with F-07's reason, never as a candidate
  - blocking: F-09 `loadSources()` returns every source in `src/sources/registered/`, and a new file there is picked up without editing any other
  - blocking: F-09 Commons' `fetchById` reads one file by its title, with its licence classified
- Test data: record: `npm run record -- F-09` (needs O-10): two teachers, one with several depicts-tagged files
- Side effects: network (the recording only)
- Parkable: no
- Size: S


### F-10: Library of Congress pictures
- Phase: 2
- Goal: Find Prints & Photographs records that name the teacher with matching dates or their LoC name id, and turn them into candidates. Main example: a record headed `Fillmore, Charles, 1854-1948` becomes a candidate, with its rights advisory classified. Failure example: a record with the same name and other dates is not a candidate. It creates: `locCandidates(client, teacher): Promise<FoundCandidate[]>` in `src/sources/loc.ts` (loc.gov JSON, `fo=json`), and `src/sources/registered/loc.ts`, which registers it.
- Covers: SRC-03, SRC-05, SRC-08, AC-06
- Defers: none
- Depends on: F-07, F-09, F-32
- Owner input: none
- Owns: `src/sources/loc.ts`, `src/sources/registered/loc.ts`
- Reads: `brain/spec/requirements.md` SRC-02, SRC-03, SRC-05, SRC-08, SRC-09, PIP-21; `brain/spec/sources.md` (Library of Congress)
- Checks:
  - blocking: F-10 a record whose name heading carries the teacher's LoC name id matches, and so does one headed like `Fillmore, Charles, 1854-1948` whose dates match
  - blocking: F-10 a near miss (the same name, other dates), an undated heading and a name only in the title don't match
  - blocking: F-10 the rights advisory is classified by F-07, and "rights status not evaluated" is refused
  - blocking: F-10 the largest image link is chosen, with its pixel size (from the IIIF `info.json` when the record lacks it), and a preview link at most 1,600 px (`full/!1600,1600/0/default.jpg`) is recorded
  - blocking: F-10 its requests go through F-06's client, paced to 20 a minute
  - blocking: F-10 `fetchById` reads one item by its LoC id, with its rights advisory classified
- Test data: record: `npm run record -- F-10` (needs O-10): three teachers, plus near-miss and undated records
- Side effects: network (the recording only)
- Parkable: yes (no card lists F-10; the gatherer then runs without the LoC)
- Size: M


### F-34: Wellcome Collection
- Phase: 2
- Goal: Find Wellcome picture records whose contributor or subject is the teacher, by LoC name id or by name and dates, with clean licences. Main example: a record whose subject carries the teacher's LoC name id becomes a candidate, its PDM licence tier 1. Failure example: a CC BY-NC record comes back refused. It creates: `wellcomeCandidates(client, teacher): Promise<FoundCandidate[]>` in `src/sources/wellcome.ts` (the catalogue API, no key; images through IIIF), and `src/sources/registered/wellcome.ts`, which registers it.
- Covers: SRC-03, SRC-05, SRC-08, AC-06
- Defers: none
- Depends on: F-07, F-09, F-32
- Owner input: none
- Owns: `src/sources/wellcome.ts`, `src/sources/registered/wellcome.ts`
- Reads: `brain/spec/requirements.md` SRC-02, SRC-03, SRC-05, SRC-08, PIP-21; `brain/spec/sources.md` (Wellcome Collection)
- Checks:
  - blocking: F-34 a record whose contributor or subject carries the teacher's LoC name id matches, and so does one with the name and matching dates
  - blocking: F-34 licences map through F-07: PDM and CC0 to tier 1, CC BY to tier 2, and CC BY-NC is refused
  - blocking: F-34 the IIIF links for the full size and for a preview at most 1,600 px (`/full/!1600,1600/0/default.jpg`) are recorded, with the full width and height from `info.json`
  - blocking: F-34 `fetchById` reads one work by its Wellcome id, with its licence classified
- Test data: record: `npm run record -- F-34` (needs O-10): two teachers, one of them a mind-cure figure
- Side effects: network (the recording only)
- Parkable: yes
- Size: S


### F-35: Finding missing dates and ids
- Phase: 2
- Goal: Fill a teacher's missing Wikidata id, LoC name id and dates only when Wikidata and the LoC name authority agree, and leave a suggestion for the owner otherwise. Main example: an undated teacher whose one Wikidata match links (P244) to a LoC name record with the same life dates gets both ids and the dates, marked as found by the tool. Failure example: when P244 points elsewhere, nothing is stored on the teacher's ids or dates, and a suggestion with its evidence is kept instead. It creates: `enrichTeacher(db, client, teacherId): Promise<EnrichResult>` in `src/teachers/enrich.ts`, which stores what agrees, or a suggestion in the teacher's `suggestion` field (the columns of `authors.csv`, plus the evidence); `fetchName(client, lcnafId)` and `searchNames(client, name)` in `src/sources/locNames.ts` (id.loc.gov); and a step in the `sync` job that enriches each teacher still lacking an id or dates.
- Covers: IN-04, IN-13, SRC-06
- Defers: none (the suggestions page and its CSV are F-46's, which shows an empty state without this card)
- Depends on: F-08, F-31
- Owner input: none
- Owns: `src/teachers/enrich.ts`, `src/sources/locNames.ts`, `src/jobs/sync.ts` (to add the enrichment step)
- Reads: `brain/spec/requirements.md` IN-04, IN-12, IN-13, SRC-06; `brain/topics/T-07-records.md` (Teacher); `brain/decisions.md` D-45
- Checks:
  - blocking: F-35 an undated teacher whose one Wikidata person links (P244) to a LoC name record with the same life dates gets the ids and dates, with `ids_from` and `dates_from` saying the tool found them
  - blocking: F-35 when two people share the name (the theologian and the linguist Charles J. Fillmore), the teacher's `key_works` pick out exactly one by a work title, and it's accepted; if they pick out none or both, nothing is stored and a suggestion is kept
  - blocking: F-35 a disagreement (P244 points elsewhere, or the years differ), or only one source with data, stores no id or date and keeps a suggestion with its evidence
  - blocking: F-35 a stored suggestion has `name`, `aliases`, `dates`, `wikidata_qid`, `lcnaf_id` and `evidence`
  - blocking: F-35 a teacher left with no id and no dates is marked skipped, saying what to add
  - blocking: F-35 the `sync` job enriches only teachers still lacking an id or dates, and a second sync makes no request for teachers already settled
- Test data: record: `npm run record -- F-35` (needs O-10): Wikidata and id.loc.gov responses for agreeing (dated and undated), disagreeing, same-name and one-sided cases
- Side effects: network (the recording only)
- Parkable: yes (teachers without ids then stay skipped until the owner adds them)
- Size: M


### F-38: Coverage survey
- Phase: 2
- Goal: Search every active teacher on every registered source, without downloading or spending, and report coverage, so Smithsonian, the trial set and PIP-20's real pairs can be decided. Main example: five recorded teachers give the expected counts by source, rule and licence tier. Failure example: any file download or model call fails the check. It creates: `runSurvey(db, sources, teachers, opts): Promise<SurveyReport>` in `src/sources/survey.ts`; the job kind `survey`; the command `portraits survey [--teacher ID]`.
- Covers: SRC-14
- Defers: TRI-02 (the trial set is picked from the survey's report in F-28, from staging's real survey in F-52), PIP-20 (its thresholds are checked on the real pairs in F-52)
- Depends on: F-09, F-31, F-49
- Owner input: none
- Owns: `src/sources/survey.ts`, `src/jobs/survey.ts`, `src/cli/commands/survey.ts`
- Reads: `brain/spec/requirements.md` SRC-03, SRC-09, SRC-14, TRI-02, PIP-20; `brain/spec/sources.md`
- Checks:
  - blocking: F-38 on the recorded responses for five teachers, the report's counts by source, rule and licence tier match the expected counts
  - blocking: F-38 no file download, model call or portrait is made (the clients assert it)
  - blocking: F-38 the report lists the teachers with no candidate and, per teacher with two or more candidates, the pairs worth comparing (PIP-20)
  - blocking: F-38 the survey uses every source in F-09's registry, and runs without one that isn't registered (F-10 or F-34 parked)
  - report, smoke, needs O-9, needs O-10, needs O-13: F-38 on the deployed copy, a `sync` job, then a `survey` job for ten teachers, finish within the sources' limits, and the report counts their candidates
- Test data: record: `npm run record -- F-38` (needs O-10), the responses for five teachers from each registered source, listed in `test/fixtures/f38/record.json`
- Side effects: network (the recording and the smoke check), deploy (pull-request copies)
- Parkable: no
- Size: M
- Stop if: a source's limits make the ten-teacher survey take longer than an hour


### F-54: Phase 2 gate
- Phase: 2
- Goal: Prove it: Phase 2's pieces work together offline, from the authors list to candidates in the rights log, and every recorded request went only to an allowed host. This is Phase 2's gate card; the verifier adds its tests here. It creates nothing: it's a gate.
- Covers: none
- Defers: none
- Depends on: F-32, F-38
- Owner input: none
- Owns: none
- Reads: `brain/spec/requirements.md` SRC-01, SRC-03, SRC-12; `brain/spec/sources.md`
- Checks:
  - blocking: `npm test` (the full suite)
  - blocking: F-54 a recorded teacher goes from a fixture `authors.csv`, through every registered source, to candidates and refusals in the rights log, offline
  - blocking: F-54 every request in every Phase 2 recording went to a host on SRC-01's list
  - report: F-54 which sources are registered (whether F-10 or F-34 was parked)
- Test data: the Phase 2 cards' recordings
- Side effects: none
- Parkable: no
- Size: S


---

## Phase 3: Imaging (ported from the Python prototype)

### F-39: Porting spike: OpenCV.js and sharp
- Phase: 3
- Goal: Prove that every image operation the recipe needs works in TypeScript against the Python reference, choose the fallback for any gap, and give the imaging cards one safe way to use OpenCV.js. Main example: each operation's output matches its reference in `prototype/parity/` within the tolerance in the reference's own `.json` beside it. Failure example: a Mat left unfreed shows as memory growing over 50 runs, and fails the card. It creates: `loadCv(): Promise<Cv>` (OpenCV.js, loaded once) and `withMats(fn)` (frees every Mat made inside) in `src/imaging/cv.ts`; `decodeImage(bytes): Promise<RgbImage>` (sharp: decode, colour to sRGB) and `encodePng(image): Promise<Buffer>` (8-bit RGBA) in `src/imaging/io.ts`; one function per operation, on plain typed arrays, in `src/imaging/ops.ts`: `gaussianBlur`, `bilateralFilter`, `dft`, `idft`, `warpAffine`, `findTransformEcc`, `opticalFlowFarneback`, `distanceTransform`, `connectedComponents`, `matchFeatures` (SIFT with RANSAC, `estimateAffinePartial2D`), `medianFilter` and `maximumFilter`; `runYunet(image): Promise<YunetFace[]>` (YuNet's raw boxes `[x, y, w, h]`, five landmarks and scores, through `FaceDetectorYN` or `onnxruntime-node`) in `src/imaging/yunet.ts`; and `docs/porting.md`, saying what each operation uses and any fallback.
- Covers: none
- Defers: PIP-04 (F-12), PIP-05 (F-13), PIP-06 (F-14), PIP-13 (F-30), PIP-20 (F-42)
- Depends on: F-01, F-51
- Owner input: none
- Owns: `src/imaging/cv.ts`, `src/imaging/io.ts`, `src/imaging/ops.ts`, `src/imaging/yunet.ts`, `docs/porting.md`
- Reads: `brain/spec/architecture.md` (Stack, Porting risks, Porting traps); `prototype/parity/index.json` and `prototype/parity/results.json`; `models/README.md`
- Checks:
  - blocking: F-39 each operation matches its reference in `prototype/parity/` within the tolerance in the reference's own `.json` (`index.json` lists the files and their calls): Gaussian blur, both bilateral filters, the DFT and its inverse, both `warpAffine`s, `findTransformEcc` (with all seven arguments), Farneback flow, the distance transform, connected components, and SIFT with RANSAC
  - blocking: F-39 the 15 × 15 median on the log spectrum matches scipy's `median_filter` within one 12-bit step, with the border reflected as scipy does (computed in TypeScript, exactly or with a 12-bit sliding histogram, never with OpenCV's 8-bit `medianBlur`)
  - blocking: F-39 the 5 × 5 maximum matches `maximum_filter`
  - blocking: F-39 `idft` with `DFT_SCALE | DFT_REAL_OUTPUT` round-trips an image
  - blocking: F-39 `runYunet` on the three originals matches `results.json`'s `yunet` within 1 px, with scores within 0.01
  - blocking: F-39 an operation missing from the OpenCV.js build uses its fallback from architecture.md (AKAZE or ORB, `onnxruntime-node`, block matching), which passes the same check, and `docs/porting.md` names it
  - blocking: F-39 running the whole set 50 times leaves memory flat within 10%
  - blocking: F-39 `decodeImage` reads JPEG, PNG with alpha, TIFF and WebP fixtures; `encodePng` writes 8-bit RGBA; and an alpha channel survives a round trip
- Test data: the references in `prototype/parity/` (copied by the test author to `test/fixtures/f39/`), and small JPEG, PNG, TIFF and WebP images
- Side effects: none
- Parkable: no (everything in Phase 3 needs it)
- Size: M


### F-12: Face landmarks and crop
- Phase: 3
- Goal: Find the face box and five landmarks with YuNet, crop to STY-03's square by a similarity transform, and cut a working region out of a large original. Main example: on the owner's three originals, the box and landmarks match the Python reference within 1 px. Failure example: a face narrower than `minFacePx` is reported as too small. It creates: `findFace(image, preBox?): Promise<FaceResult>` (the box as `[x0, y0, x1, y1]`, five landmarks, the score, whether the landmarks came from the pre-check's box, and `tooSmall`) and `landmarksFromBox(box)` in `src/imaging/face.ts`; `cropTransform(face, settings): Similarity`, `cropSquare(image, transform, size)` and `workingRegion(image, transform, maxWorkingPx): Region` (the crop's square plus 25% a side, reduced by area averaging, with its offset and scale) in `src/imaging/crop.ts`.
- Covers: PIP-04, PIP-23, STY-03
- Defers: none
- Depends on: F-39
- Owner input: none
- Owns: `src/imaging/face.ts`, `src/imaging/crop.ts`
- Reads: `brain/spec/requirements.md` PIP-04, PIP-23, STY-03; `brain/spec/architecture.md` (Porting traps); `prototype/recipe.py` (`landmarks_from_box`, `crop_transform`)
- Checks:
  - blocking: F-12 on the owner's three originals (`prototype/parity/inputs/`), the box and landmarks match `results.json`'s `yunet` within 1 px, and the score within 0.01
  - blocking: F-12 an original over 640 px is searched on a copy reduced to 640 px, and the coordinates are scaled back
  - blocking: F-12 YuNet's `[x, y, w, h]` becomes `[x0, y0, x1, y1]` (a known box)
  - blocking: F-12 the crop puts the eye line at 0.449 of the side and the eye-to-mouth distance at 0.221 of the side, with the face centred, each within 1%
  - blocking: F-12 with no face found, the landmarks come from the pre-check's box by PIP-04's proportions and match `results.json`'s `landmarks_from_box`; on the three originals, a crop made that way puts the eye line within 0.03 of the side of the real crop's, at a scale within 10%
  - blocking: F-12 a face narrower than `minFacePx` is reported as too small
  - blocking: F-12 the working region of a 4,000 × 5,000 synthetic original is at most 2,000 px on its long side and contains the whole crop square; an original of 2,000 px or less is used whole
- Test data: the three originals and `prototype/fixtures/`; a synthetic image with no face, made in the test
- Side effects: none
- Parkable: no
- Size: M


### F-13: Descreen and edge-preserving blur
- Phase: 3
- Goal: Detect a printed dot screen by frequency analysis, notch it out, and give every original an edge-preserving blur sized in dot cells, on the working region. Main example: the owner's Fillmore and Cady originals are found to be screened and Holmes isn't, as in the prototype. Failure example: a 4,000 × 5,000 original taking over 60 seconds or 1.5 GB fails the card. It creates: `detectScreen(grey): ScreenInfo` and `descreen(grey, cellPx, settings): { image; applied: ScreenInfo }` in `src/imaging/descreen.ts` (ports of `detect_screen` and `descreen` in `prototype/recipe.py`).
- Covers: PIP-05
- Defers: none
- Depends on: F-12
- Owner input: none
- Owns: `src/imaging/descreen.ts`
- Reads: `brain/spec/requirements.md` PIP-05, PIP-23; `brain/spec/architecture.md` (Porting traps); `prototype/recipe.py` (`detect_screen`, `descreen`)
- Checks:
  - blocking: F-13 Fillmore and Cady are detected as screened and Holmes isn't, and `detectScreen` finds exactly the prototype's peaks on all three (`results.json`, `detect_screen`)
  - blocking: F-13 a synthetic screened image has its screen peaks reduced by at least the factor the prototype achieves
  - blocking: F-13 a clean image gets only the mild blur, differing from its input by no more than the prototype's output does
  - blocking: F-13 what was found and applied is returned for the record
  - blocking: F-13 a 4,000 × 5,000 synthetic screened original, cut to its working region (F-12), finishes in under 60 seconds and stays under 1.5 GB
- Test data: the three originals; a synthetic screen and the large synthetic original, made in the test
- Side effects: none
- Parkable: no
- Size: M


### F-14: Tone and halftone
- Phase: 3
- Goal: Turn the cropped tones into coverage (levels from the face, gamma, unsharp mask) and screen them as round white dots on a 45° grid, supersampled. Main example: on a synthetic gradient, frequency analysis finds a pitch of 1000/110 px along a 45° grid, and dot area grows with brightness. Failure example: a threshold map outside the prototype's tolerance fails the card. It creates: `toneToCoverage(grey, mask, faceBox, pitch, settings): Float32Array` in `src/imaging/tone.ts`; `thresholdMap(size, supersample, pitch, angleDeg): Float32Array` (built once per recipe and kept) `halftone(coverage, settings): Uint8Array` (the dots' alpha) and `halftoneStats` (`{ thresholdMapBuilds }`, a count for tests) in `src/imaging/halftone.ts` (ports of `tone_to_coverage` and `_threshold_map`).
- Covers: STY-01, PIP-06
- Defers: none
- Depends on: F-39
- Owner input: none
- Owns: `src/imaging/tone.ts`, `src/imaging/halftone.ts`
- Reads: `brain/spec/requirements.md` STY-01, PIP-06; `prototype/recipe.py` (`tone_to_coverage`, `_threshold_map`)
- Checks:
  - blocking: F-14 on a synthetic gradient, frequency analysis finds a pitch of 1000/110 px along a 45° grid, and dot area grows with brightness
  - blocking: F-14 dark tones are fully transparent, and the brightest face tone is near full coverage
  - blocking: F-14 `thresholdMap(64, 2, 64/11, 45)` matches `prototype/parity/synthetic/threshold_map.f32` within the tolerance in `threshold_map.json` beside it
  - blocking: F-14 the map is built once per recipe, in one pass without full-size intermediate arrays, and a second portrait reuses it (`halftoneStats.thresholdMapBuilds` stays 1)
- Test data: synthetic gradients, made in the test; `prototype/parity/synthetic/threshold_map.f32`
- Side effects: none
- Parkable: no
- Size: M


### F-15: Mask, code outline, master and cut-out limits
- Phase: 3
- Goal: Smooth the figure mask (head and shoulders differently), draw the code outline, composite the white master, check it, and refuse figures that break the cut-out limits. Main example: the three examples' masters pass STY-06, with a 6 px line starting 2 px outside the figure. Failure example: a mask with a floating fragment is refused, naming the limit. It creates: `smoothMask(mask, settings, chinY?)` in `src/imaging/mask.ts`; `drawOutline(mask, settings)` in `src/imaging/outline.ts`; `makeMaster(croppedGrey, croppedMask, face, settings): Master` (the white master and its layers, as the prototype's `make_master` makes them after its blend step) in `src/imaging/compose.ts`; and `checkMaster(rgba): string[]` (STY-06) and `checkCutoutLimits(rawMask): LimitResult` (PIP-19) in `src/imaging/checks.ts`.
- Covers: STY-02, STY-06, PIP-07, PIP-08, PIP-19
- Defers: none
- Depends on: F-12, F-14
- Owner input: none
- Owns: `src/imaging/mask.ts`, `src/imaging/outline.ts`, `src/imaging/compose.ts`, `src/imaging/checks.ts`
- Reads: `brain/spec/requirements.md` STY-02, STY-06, PIP-07, PIP-08, PIP-19; `prototype/recipe.py` (`smooth_mask`, `make_master`, `check_master`)
- Checks:
  - blocking: F-15 the line is one connected piece, 6 ± 1 px wide, starting 2 ± 1 px outside the figure, and runs off the bottom where the shoulders leave the square
  - blocking: F-15 the master passes STY-06: every visible pixel is pure white, and the corners and the outside are transparent
  - blocking: F-15 the three examples pass PIP-19's limits; fixtures with a floating fragment, a figure cut off above the shoulders and a full square are each refused, naming the limit
  - blocking: F-15 the 98% piece share is measured on the raw cut-out before smoothing; smoothing still keeps only the largest piece, and the fragment fixture is refused all the same
- Test data: the prototype's cut-out fixtures (`prototype/fixtures/`); synthetic bad masks, made in the test
- Side effects: none
- Parkable: no
- Size: M


### F-30: AI copy: key mask, alignment, drift check, blend
- Phase: 3
- Goal: Take an AI copy on flat green, read the cut-out from its green, align it to the original, refuse it if details moved, and blend it at 50% in the portrait's frame. Main example: a synthetic keyed copy (2.8× larger, sharpened, rescaled by 2%, shifted, on green) aligns with correlation ≥ 0.99 and blends with no double edges. Failure example: a copy with the eyes and mouth moved by about 1.2 dot cells measures over 0.7 and is refused. It creates: `keyMask(rgb, settings)`, `alignEnhanced(grey, enhancedRgb, settings): Alignment` (the matrix and correlation, or refused) and `localDrift(grey, alignedGrey, alignment, faceBox, cellPx, settings): number` in `src/imaging/align.ts`; and `blendEnhanced(croppedGrey, alignedCrop, share)` and `mapMaskBack(mask, alignment, region?): Mask` (onto the original's own size and position, through the working region's offset and scale) in `src/imaging/blend.ts` (ports of `key_mask`, `align_enhanced`, `local_drift` and the blend in `make_master`).
- Covers: PIP-03, PIP-13, STY-04
- Defers: OUT-11 (`mask.png` stored with the portrait: F-24)
- Depends on: F-12, F-13
- Owner input: none
- Owns: `src/imaging/align.ts`, `src/imaging/blend.ts`
- Reads: `brain/spec/requirements.md` PIP-03, PIP-13, PIP-23, STY-04; `prototype/recipe.py` (`key_mask`, `align_enhanced`, `local_drift`, `make_master`); `prototype/test_enhance_mechanics.py`
- Checks:
  - blocking: F-30 synthetic keyed copies (2.8× larger, sharpened, rescaled by 2%, shifted, on green) align with correlation ≥ 0.99
  - blocking: F-30 the blend shows no double edges (edge agreement ≥ 0.98), and its share is exactly `enhanceBlend`
  - blocking: F-30 the mask from the green matches the prototype's cut-out fixture with overlap ≥ 0.94
  - blocking: F-30 the drift check, inside the face box shrunk by `driftBoxInset` (0.15) on each side, measures copies with the eyes and mouth moved by about 1.2 dot cells above 0.7 and good copies below, each within 0.1 of `prototype/out/enhance-mechanics.json` (good 0.14–0.31, moved 0.95–1.08)
  - blocking: F-30 a copy that can't be aligned (a different face) is refused
  - blocking: F-30 the key mask, mapped back through the inverse of the alignment (and the working region's offset and scale for a large original), overlaps the true figure in the original by at least 0.97, for a small and a 4,000 × 5,000 synthetic original
- Test data: synthetic keyed copies from a TypeScript port of the generator in `prototype/test_enhance_mechanics.py`, written by the test author in `test/fixtures/f30/` (F-19's tests import it); `prototype/out/enhance-mechanics.json`
- Side effects: none
- Parkable: no (the cut-out depends on it)
- Size: M


### F-41: Black-and-white, 500 px, viewing copies and the whole recipe
- Phase: 3
- Goal: Make the black-and-white version (option C) and the 500 px copies from the master's layers, the original's PNG viewing copy and the images sent to models, and run the whole code recipe in one call. Main example: `renderPortrait` on an example's fixture gives `white-1000`, `white-500`, `bw-1000` and `bw-500`, each passing its checker. Failure example: a 300 px original's viewing copy enlarged past 300 px fails the card. It creates: `bwVersion(layers, settings)`, `small(rgba, settings)` and `checkBw(rgba, master?): string[]` in `src/imaging/versions.ts` (ports of `bw_version`, `small` and `check_bw`); `viewingCopy(original): Promise<Buffer>` and `modelImage(image, maxPx): Promise<Buffer>` (an 8-bit sRGB PNG, PIP-22) in `src/imaging/modelImage.ts`; and `renderPortrait(input, settings): Promise<PortraitImages>` in `src/imaging/recipe.ts`, where `input` is the original, its face (box and landmarks), its cut-out mask, an optional aligned AI copy and an optional `framing` (a crop transform that overrides the automatic crop, as the fixtures' `target_warp_500` gives the owner's framing). It runs the code steps in the prototype's order: descreen (F-13), crop (F-12), the blend when an aligned AI copy is given (F-30), `makeMaster` (F-15), then the black-and-white and 500 px versions.
- Covers: STY-08, STY-09, OUT-05, PIP-22
- Defers: STY-07 (parity with the prototype, proved in F-16)
- Depends on: F-15, F-30
- Owner input: none
- Owns: `src/imaging/versions.ts`, `src/imaging/modelImage.ts`, `src/imaging/recipe.ts`
- Reads: `brain/spec/requirements.md` STY-08, STY-09, OUT-05, PIP-22; `brain/spec/architecture.md` (Data flow for one teacher); `prototype/recipe.py` (`make_master`, `bw_version`, `small`, `check_bw`)
- Checks:
  - blocking: F-41 `bw-1000` passes `checkBw`: visible pixels are grey, the corners are transparent, and it's opaque wherever the master shows
  - blocking: F-41 both 500 px copies pass their checkers
  - blocking: F-41 the viewing copy is a PNG at most 1,600 px on its long side, never enlarged (a 300 px original stays 300 px), and keeps a PNG original's transparency
  - blocking: F-41 a 16-bit TIFF and a CMYK JPEG each become an 8-bit sRGB PNG, at most `maxModelImagePx` on the long side and under 5 MB
  - blocking: F-41 `renderPortrait` on each example's fixture (with its given landmarks and cut-out) returns the four versions, each passing its checker; given an aligned AI copy, it blends it at `enhanceBlend`; given `framing`, it crops by that instead of the automatic crop
- Test data: the three examples' fixtures (`prototype/fixtures/`); a transparent PNG, a 16-bit TIFF and a CMYK JPEG
- Side effects: none
- Parkable: no
- Size: M


### F-42: Same photograph or different (code layers)
- Phase: 3
- Goal: Tell copies of one photograph from different photographs with a whole-picture fingerprint and feature matching, leaving the unclear middle for the model (F-43). Main example: the prototype's 30 doctored copies (crop, rescale, rotation, JPEG, blur, reprint screen, mirror, noise) are judged the same. Failure example: two different frontal sittings judged the same by fingerprint fail the card. It creates: `fingerprint(image): bigint` (a 64-bit difference hash of the whole picture), `featurePoints(image): Features`, `comparePhotos(a, b, settings): { verdict: "same" | "different" | "unclear"; inliers: number; bits: number }` and `groupByPhotograph(items, resolveUnclear): Promise<PhotographGroup[]>` (each new item compared with one representative per group; `resolveUnclear(a, b): Promise<boolean>` decides the pairs in the middle, true meaning the same photograph), and `samePhotoStats` (`{ featurePointRuns }`, a count for tests) in `src/imaging/samePhoto.ts` (a port of `prototype/same_photo.py`).
- Covers: PIP-15, PIP-20
- Defers: none (the model's layers of the same-photograph check are F-43's)
- Depends on: F-12
- Owner input: none
- Owns: `src/imaging/samePhoto.ts`
- Reads: `brain/spec/requirements.md` PIP-15, PIP-20; `prototype/same_photo.py`; `prototype/out/same-photo.json`
- Checks:
  - blocking: F-42 the 30 doctored copies, generated as in `same_photo.py`, are judged the same, with inlier counts within 25% of `prototype/out/same-photo.json`
  - blocking: F-42 the different-photograph pairs score at or below `diffMaxInliers`
  - blocking: F-42 exact duplicates and resized or re-encoded copies are caught by the fingerprint alone (at most 2 bits apart), and two different frontal sittings never are
  - blocking: F-42 `groupByPhotograph` compares a new item with one representative per group, and each picture's feature points are computed once (`samePhotoStats.featurePointRuns`)
  - blocking: F-42 a pair between the thresholds comes back `unclear` and goes to `resolveUnclear`
  - report: F-42 if F-39 chose a fallback detector (AKAZE or ORB), `sameMinInliers` and `diffMaxInliers` measured again on the same fixtures, for a recipe change the Tech Lead rules on
- Test data: the three originals; a TypeScript port of `same_photo.py`'s generator, written by the test author
- Side effects: none
- Parkable: no
- Size: M


### F-16: Parity with the Python prototype
- Phase: 3
- Goal: Prove it: from the prototype's fixtures, the TypeScript recipe (`renderPortrait`, F-41) reproduces the prototype's outputs within tolerance. Main example: each example's `white-1000` overlaps the prototype's by at least 0.98. Failure example: a version with 112 dots across fails the card. This is Phase 3's gate card; the verifier adds its tests here. It creates nothing: it's a gate.
- Covers: STY-07
- Defers: AC-04 (the examples against the hand-made targets: F-29)
- Depends on: F-13, F-15, F-30, F-41, F-42
- Owner input: none
- Owns: none
- Reads: `brain/spec/architecture.md` (The Python prototype is the reference); `prototype/README.md`
- Checks:
  - blocking: `npm test` (the full suite)
  - blocking: F-16 for each of the three examples, at the automatic crop and at the owner's framing, `white-1000` matches the prototype's with figure overlap ≥ 0.98, mean alpha difference ≤ 0.02 and 110 ± 1 dots across
  - blocking: F-16 the same for `bw-1000` and both 500 px copies
  - blocking: F-16 the test uses a frozen copy of the recipe 0.5.0 settings in `test/fixtures/f16/`, not the live settings, so a later recipe version doesn't break it
  - blocking: F-16 the landmarks are the fixtures' own (given, not detected), so a detector difference can't move the crop
- Test data: `prototype/fixtures/` and `prototype/out/`, with the frozen 0.5.0 settings, copied by the test author to `test/fixtures/f16/`
- Side effects: none
- Parkable: no (a failure stops the build, with the measures on the control issue)
- Size: S


---

## Phase 4: Model steps

### F-17: OpenRouter client, spend ledger and caps
- Phase: 4
- Goal: One client for every model call through OpenRouter, with a stub mode, a spend ledger and every cap checked before each call. Main example: in stub mode, canned answers come back with no key and no network, and each call's cost lands in the ledger with its budget. Failure example: a call that would pass the night's cap is never made, and the stop is reported. It creates: `createModelClient(deps): ModelClient`, with `call(request: ModelRequest): Promise<ModelAnswer>` (the request names the step, model, prompt and its version, images, teacher and budget), in `src/models/openrouter.ts`; `createStubModelClient(answers): ModelClient` in `src/models/stub.ts`, for later cards' tests; and `checkCaps(db, env, { estimateUsd, budget, teacherId, runId }): Promise<CapVerdict>` and `CapReachedError` in `src/models/caps.ts`.
- Covers: RUN-04, RUN-06, RUN-10, PIP-09
- Defers: none (the first pass's state changes are F-25's)
- Depends on: F-04, F-06
- Owner input: none
- Owns: `src/models/openrouter.ts`, `src/models/stub.ts`, `src/models/caps.ts`
- Reads: `brain/spec/requirements.md` RUN-04, RUN-06, RUN-10, PIP-09, PIP-22; `brain/spec/architecture.md` (Stack: AI; Environments); `brain/decisions.md` D-19, D-52, D-54
- Checks:
  - blocking: F-17 in stub mode, canned answers come back with no key and no network
  - blocking: F-17 each cap, crossed mid-run with stubbed costs, stops the next call before it's made and is reported: the first pass's $100 total (no night cap during it); after it, $10 a night and $30 a month; $2 per teacher per run; the trial's $27 and $3; staging's $2 a night and $10 a month
  - blocking: F-17 in a pull-request copy (`PORTRAITS_ENV=preview`), every paid call is refused
  - blocking: F-17 every request asks for usage (`"usage": {"include": true}`), and each call's cost is logged with its run, teacher, step, model, environment and budget, and whether it's actual or estimated
  - blocking: F-17 the month cap sums only `regular` spend, and the trial's spend never counts toward it
  - blocking: F-17 a checking model of the same family as the enhance model is refused
  - blocking: F-17 model ids and prices come from settings, and an unknown model id is refused before any call
- Test data: canned OpenRouter answers, including usage and cost fields
- Side effects: none
- Parkable: no
- Size: M


### F-18: Pre-check
- Phase: 4
- Goal: Ask Claude Haiku whether an original can be used, from its preview, and record its structured verdict. Main example: a canned pass verdict comes back parsed, with the face box turned into the original's pixels. Failure example: a caption naming someone else fails the original. It creates: `precheck(ctx, candidate): Promise<PrecheckVerdict>` (pass, or fail with reasons; the face box in pixels; the medium; the age estimate; the dot pattern; the caption) in `src/models/precheck.ts`; and the prompt `src/models/prompts/precheck.md`, copied from `prototype/prompts/precheck.md` (v2).
- Covers: PIP-02, PIP-22
- Defers: PIP-18 (the approximate date from the age estimate: F-23, F-48)
- Depends on: F-17, F-41
- Owner input: none
- Owns: `src/models/precheck.ts`, `src/models/prompts/precheck.md`
- Reads: `brain/spec/requirements.md` PIP-02, PIP-18, PIP-22; `prototype/prompts/precheck.md`; `brain/decisions.md` D-47, D-52
- Checks:
  - blocking: F-18 canned verdicts drive pass and fail, and a fail comes back with its reasons
  - blocking: F-18 the face box, medium, age estimate, dot pattern and caption are parsed; malformed JSON is retried once, then counted as a failure with the raw text kept
  - blocking: F-18 the face box comes back as fractions and is turned into the original's pixels with the width and height the source gave; a face under `minFacePx` fails in code, whatever the model said
  - blocking: F-18 with no size from the source, the verdict says the size check must be repeated on the downloaded original, before the enhance call
  - blocking: F-18 the request carries the preview as an 8-bit PNG at most 1,600 px (F-41's `modelImage`), never a TIFF or the full original
  - blocking: F-18 a caption naming someone else fails
  - blocking: F-18 `allowedMedia` excludes engravings when set
  - blocking: F-18 a second pre-check of the same original makes no call (the step cache)
- Test data: canned verdicts for each case
- Side effects: none
- Parkable: no
- Size: S


### F-19: AI copy and keyed cut-out calls
- Phase: 4
- Goal: Ask the image model for the enhanced copy on green, and for the cut-out-only fallback when it's needed, cache the answer, and keep it with its record. Main example: a canned image answer becomes `enhanced.png`, with the model, prompt version, alignment and drift scores and whether it was used. Failure example: when the enhance call errors and the fallback can't be aligned, the draft fails for its cut-out, and no further call is made for that attempt. It creates: `enhance(ctx, original, opts): Promise<EnhanceResult>` (`opts`: the attempt and any `try_again` note) in `src/models/enhance.ts`; `cutoutKeyed(ctx, original, opts): Promise<CutoutResult>` and `makeCutout(ctx, original, opts): Promise<CutoutOutcome>` (the enhance call, then one `cutout_keyed` call when its copy errors, is refused by its safeguards or its mask fails PIP-19) in `src/models/cutout.ts`; and the prompts `src/models/prompts/enhance_keyed.md` and `src/models/prompts/cutout_keyed.md`, copied from `prototype/prompts/`.
- Covers: PIP-03, PIP-10, PIP-13, PIP-22
- Defers: none
- Depends on: F-17, F-30, F-41
- Owner input: none
- Owns: `src/models/enhance.ts`, `src/models/cutout.ts`, `src/models/prompts/enhance_keyed.md`, `src/models/prompts/cutout_keyed.md`
- Reads: `brain/spec/requirements.md` PIP-03, PIP-10, PIP-13, PIP-19, PIP-22; `prototype/prompts/enhance_keyed.md` and `prototype/prompts/cutout_keyed.md`; `brain/decisions.md` D-52, D-56
- Checks:
  - blocking: F-19 a canned image answer becomes `enhanced.png`, recorded with the model, prompt version, alignment and drift scores, and whether it was used
  - blocking: F-19 a second try on the same original makes no call, and a remake (attempt 1) makes exactly one new call
  - blocking: F-19 exactly one `cutout_keyed` call is made when the enhance call errors, its copy is refused by its safeguards, or its mask fails PIP-19; its image is aligned like the AI copy, and its mask becomes `mask.png`
  - blocking: F-19 when the fallback errors, can't be aligned or fails PIP-19, the draft fails for its cut-out, and no further call is made for that attempt
  - blocking: F-19 the enhance and cut-out requests carry the descreened working region as a PNG at most 1,600 px, never the original file
  - blocking: F-19 a `try_again` note is added to the enhance prompt, and recorded
- Test data: synthetic keyed images as canned answers (F-30's fixtures, read-only from `test/fixtures/f30/`)
- Side effects: none
- Parkable: no
- Size: M


### F-21: Draft check and compare-with-target
- Phase: 4
- Goal: Ask Claude Sonnet to judge a draft on five criteria against its original, and score a draft against a hand-made target. Main example: a canned answer passing all five criteria passes the draft, with its scores and notes recorded. Failure example: an answer failing one criterion fails the draft. It creates: `draftCheck(ctx, draft, original, opts): Promise<DraftVerdict>` (`opts.note` adds a `try_again` criterion) and `compareWithTarget(ctx, draft, target): Promise<CompareScores>` in `src/models/draftCheck.ts`; and the prompts `src/models/prompts/draftcheck.md` and `src/models/prompts/compare.md`, copied from `prototype/prompts/`.
- Covers: PIP-09, PIP-22
- Defers: TRI-08 (the examples measured: F-29)
- Depends on: F-17, F-15, F-41
- Owner input: none
- Owns: `src/models/draftCheck.ts`, `src/models/prompts/draftcheck.md`, `src/models/prompts/compare.md`
- Reads: `brain/spec/requirements.md` PIP-09, PIP-22, TRI-08; `prototype/prompts/draftcheck.md` and `prototype/prompts/compare.md`; `brain/decisions.md` D-52
- Checks:
  - blocking: F-21 the request carries, in this order, the original's viewing copy, the draft on `checkPageRgb`, then the three examples (`design/portraits/targets/`) on the same colour; every image is an 8-bit PNG at most 1,600 px and under 5 MB, never a TIFF
  - blocking: F-21 canned answers pass only when all five criteria pass, and the scores and notes are recorded
  - blocking: F-21 a `try_again` note becomes an extra criterion
  - blocking: F-21 the compare mode returns a score per criterion against the target
  - blocking: F-21 a malformed answer is retried once
- Test data: canned answers
- Side effects: none
- Parkable: no
- Size: S


### F-43: Same-photograph tie-break
- Phase: 4
- Goal: For pairs F-42 finds unclear, ask Claude Sonnet whether they're the same photograph, treating "unsure" as the same. Main example: a canned "same" groups the pair, with its evidence recorded. Failure example: asking about the same pair twice, in either order, makes a second call and fails the card. It creates: `samePhotoCheck(ctx, a, b): Promise<{ verdict: "same" | "different" | "unsure"; evidence: string }>` and `unclearResolver(ctx)`, which returns the async resolver F-42's `groupByPhotograph` takes, in `src/models/samePhotoCheck.ts`; and the prompt `src/models/prompts/same_photo.md`, copied from `prototype/prompts/`.
- Covers: PIP-20, PIP-22
- Defers: none
- Depends on: F-17, F-41, F-42
- Owner input: none
- Owns: `src/models/samePhotoCheck.ts`, `src/models/prompts/same_photo.md`
- Reads: `brain/spec/requirements.md` PIP-20, PIP-22; `prototype/prompts/same_photo.md`; `brain/decisions.md` D-50
- Checks:
  - blocking: F-43 "same" groups the pair, "different" separates it, and "unsure" groups it (D-50)
  - blocking: F-43 the evidence is recorded with the pair
  - blocking: F-43 a pair is never asked twice: the answer is cached by both SHA-256s, in either order
  - blocking: F-43 both images are the candidates' previews, reduced to 800 px and sent as 8-bit PNGs, never TIFFs
- Test data: canned answers
- Side effects: none
- Parkable: no
- Size: S


### F-11: Candidates: gather, previews, group, order
- Phase: 4
- Goal: Gather a teacher's candidates from every registered source, log refusals, fetch small previews, group copies of one photograph and order the copies (PIP-21, steps 1–3), and download the full original of a copy F-23 chooses. Main example: a fixture teacher with candidates from three sources gives two photographs, the refused one logged, the duplicate merged, and each photograph's copies in SRC-07's order. Failure example: a full original fetched while gathering, or a preview kept in the bucket, fails the card. It creates: `gatherPhotographs(ctx, teacher): Promise<Photograph[]>` (each with its copies in order, and the best-known flag on the P18 photograph) and `downloadOriginal(ctx, copy, portraitId): Promise<StoredOriginal>` in `src/sources/candidates.ts`.
- Covers: SRC-07, SRC-08, PIP-15, PIP-21, IN-05
- Defers: PIP-01 (choosing which to draft: F-23), OUT-12 (the portrait's other files: F-24)
- Depends on: F-09, F-32, F-37, F-42, F-43
- Owner input: none
- Owns: `src/sources/candidates.ts`
- Reads: `brain/spec/requirements.md` SRC-07, SRC-08, SRC-12, PIP-12, PIP-15, PIP-20, PIP-21, IN-05; `brain/spec/architecture.md` (Data flow for one teacher)
- Checks:
  - blocking: F-11 a fixture teacher with candidates from three sources (one refused licence, one exact duplicate, two copies of one photograph, one different photograph) gives two photographs, the refused one in the rights log, the duplicate merged, and each photograph's copies in SRC-07's order (licence tier, then size)
  - blocking: F-11 at most `maxCandidatesPerTeacher` previews are fetched, each at most 1,600 px from its source's sized-image link, kept only in memory or temporary files and never in the bucket; no full original is fetched while gathering
  - blocking: F-11 `downloadOriginal` checks the SHA-256 on a second fetch, and stores the file as `original.<ext>` under the portrait's key
  - blocking: F-11 set-aside photographs are left out
  - blocking: F-11 the best-known flag is set on the P18 photograph and its copies
  - blocking: F-11 changing a teacher's notes changes none of their candidates
  - blocking: F-11 only registered sources are asked (the tests register fakes), so a parked source is simply missing
- Test data: recorded source responses (earlier cards' fixtures, read-only) and small image fixtures, including doctored copies
- Side effects: none
- Parkable: no
- Size: M


### F-55: Phase 4 gate
- Phase: 4
- Goal: Prove it: in stub mode, one teacher's candidates go through every model step with every cap enforced, and no model is ever sent a TIFF or an oversized image. This is Phase 4's gate card; the verifier adds its tests here. It creates nothing: it's a gate.
- Covers: none
- Defers: none
- Depends on: F-11, F-18, F-19, F-21
- Owner input: none
- Owns: none
- Reads: `brain/spec/requirements.md` PIP-02, PIP-09, PIP-13, PIP-20, PIP-21, PIP-22, RUN-04, RUN-10
- Checks:
  - blocking: `npm test` (the full suite)
  - blocking: F-55 in stub mode, one teacher's candidates go through the pre-check, the AI copy, the draft check and the tie-break, and the spend ledger records each call
  - blocking: F-55 no request to a model carries a TIFF, an image over 1,600 px or an image over 5 MB
  - blocking: F-55 a pull-request environment refuses every paid call
- Test data: the Phase 4 cards' canned answers
- Side effects: none
- Parkable: no
- Size: S


---

## Phase 5: Pipeline and service

### F-24: Publishing a portrait
- Phase: 5
- Goal: Write a portrait's files (OUT-11) and its record atomically, with each file's licence and credit, and add it to the change feed. Main example: a fixture portrait produces all eight files under its key, each passing its checker, plus `record.json`, and the record validates against the contract's `Portrait`. Failure example: a record missing a licence isn't published: the failure names the field, the portrait is `failed`, and its candidate is set aside. It creates: `nextPortraitId(db, teacherId): Promise<string>`, `publishPortrait(ctx, draft: PortraitDraft): Promise<Portrait>`, `portraitRecord(db, portraitId): Promise<Portrait>` (the contract's shape) and `writeRecordJson(ctx, portraitId)` (rewrites `record.json` from the database, for every later change) in `src/pipeline/portrait.ts`.
- Covers: OUT-02, OUT-03, OUT-04, OUT-11, OUT-12, SRC-11, AC-02
- Defers: none
- Depends on: F-03, F-04, F-07, F-37, F-41
- Owner input: none
- Owns: `src/pipeline/portrait.ts`
- Reads: `brain/spec/requirements.md` OUT-02, OUT-03, OUT-04, OUT-11, OUT-12, SRC-11; the contract's `Portrait`; `brain/topics/T-07-records.md`
- Checks:
  - blocking: F-24 a fixture portrait produces all eight files under its key, each passing its checker, plus `record.json`, and the record validates against the contract's `Portrait`
  - blocking: F-24 a fixture whose enhance call failed produces the other seven, with `enhanced_used` false
  - blocking: F-24 each file's licence and credit follow SRC-11's table, for a public-domain, a CC BY and a CC BY-SA fixture
  - blocking: F-24 stopping after the files are written but before the database commit leaves no visible portrait and no change-feed entry
  - blocking: F-24 a record missing a licence isn't published: the failure names the field, the portrait is `failed`, and its candidate is marked set aside
  - blocking: F-24 portrait ids count up per teacher and are never reused after a turn-down
  - blocking: F-24 `writeRecordJson` rewrites `record.json` from the database, and a turned-down portrait's files remain
- Test data: images from `renderPortrait` (F-41) on the examples' fixtures, never published; F-07's fixtures, read-only
- Side effects: none
- Parkable: no
- Size: M


### F-23: Per-teacher pipeline and failure policy
- Phase: 5
- Goal: Take one teacher from candidates to published portraits: open slots, the choice of photographs, pre-check, AI copy, draft, check, remake and set-asides, all with stubs. Main example: a teacher with five different photographs gets three portraits, the best-known one first, then spread across their life. Failure example: a draft failing twice sets its original aside, and the next photograph is tried. It creates: `processTeacher(ctx, teacherId): Promise<TeacherRunResult>` in `src/pipeline/teacher.ts`; `choosePhotographs(photographs, openSlots, teacher): Photograph[]` in `src/pipeline/choose.ts`; `draftOriginal(ctx, teacherId, copy, opts: { note?, attempt, replaces? }): Promise<DraftOutcome>` (one draft from one given copy, for the library's requests, F-45) in `src/pipeline/teacher.ts`; `recordFailure(...)` and `isSetAside(...)` in `src/pipeline/failures.ts`. The contract step settles their exact types.
- Covers: PIP-01, PIP-10, PIP-11, PIP-12, PIP-14, PIP-16, PIP-19, PIP-21
- Defers: PIP-17 and PIP-18 (later runs and the library's corrections: F-48)
- Depends on: F-11, F-16, F-18, F-19, F-21, F-24
- Owner input: none
- Owns: `src/pipeline/teacher.ts`, `src/pipeline/choose.ts`, `src/pipeline/failures.ts`
- Reads: `brain/spec/requirements.md` PIP-01..PIP-23, SRC-07; `brain/spec/architecture.md` (Data flow for one teacher)
- Checks:
  - blocking: F-23 the best copies are pre-checked before any photograph is chosen
  - blocking: F-23 a photograph whose best copy fails for damage tries its next copy
  - blocking: F-23 full originals are downloaded only for the photographs chosen
  - blocking: F-23 five different photographs give three portraits: the P18 photograph first, then the best-quality dated one at least 10 years from those chosen
  - blocking: F-23 with none 10 years away, the one furthest from its nearest chosen year is taken; with no dated ones left, the best undated one; with no P18, the best-quality one first
  - blocking: F-23 a draft failing twice sets its original aside, and the next photograph is tried
  - blocking: F-23 a failure a new copy can't change sets the original aside at once
  - blocking: F-23 at most 6 originals are drafted and 12 pre-checked per teacher per run
  - blocking: F-23 a source date beats an estimated one; an estimate uses the birth year
  - blocking: F-23 a cut-out limit failure, or a failed enhance call, triggers one fallback call; a failing fallback fails the draft, and the remake tries once more
  - blocking: F-23 a second run never tries a set-aside photograph again
  - blocking: F-23 an original failing its pre-check is set aside, and no further call is made for it
  - blocking: F-23 with no size from the source, the `minFacePx` check is repeated on the downloaded original before the enhance call, and a face too small sets it aside with no enhance call
  - blocking: F-23 `draftOriginal` drafts one given copy with a note and a fresh AI copy (the attempt counted up), and offers it with `replaces` when given
- Test data: a stub world for three teachers in `test/fixtures/f23/` (recorded source responses, canned model answers and images), served through the product's own replay client (F-06) and stub model client (F-17); F-25, F-26 and F-48 reuse it
- Side effects: none
- Parkable: no
- Size: L
- Stop if: a check needs a model answer the stub world can't give: ask for the fixture rather than fake it in the product code


### F-25: Queue, schedule and run reports
- Phase: 5
- Goal: Run the nightly schedule and the queue: sync, queue the teachers due a search, take requests first, resume after a crash, stop at a cap, track the first pass and write each run's report. Main example: on a fake clock, a teacher searched 35 days ago is queued and one searched 10 days ago isn't. Failure example: a worker killed mid-teacher that repeats a paid call on restart fails the card. It creates: `nightly(ctx): Promise<NightlyResult>` (sync, then queue the teachers due) in `src/cron.ts`; `runWorker(ctx, opts)` in `src/worker.ts`, which also calls `nightly` at the set hour in production, never twice at once; `teachersDue(db, now, settings): Promise<string[]>`, `planRun(ctx, opts): Promise<RunPlan>` (with the estimated spend) and `runQueue(ctx, opts): Promise<RunReport>` in `src/pipeline/run.ts`; the job kind `run` (with `teacher` or `limit`); and the command `portraits run [--limit N] [--teacher ID] [--dry-run]`.
- Covers: RUN-02, RUN-03, RUN-04, RUN-08, OUT-06
- Defers: IN-06 (the library's requests handled: F-45)
- Depends on: F-23, F-31, F-36
- Owner input: none
- Owns: `src/cron.ts`, `src/worker.ts`, `src/pipeline/run.ts`, `src/jobs/run.ts`, `src/cli/commands/run.ts`
- Reads: `brain/spec/requirements.md` RUN-02, RUN-03, RUN-04, RUN-08, RUN-11, OUT-06; `brain/decisions.md` D-53, D-59
- Checks:
  - blocking: F-25 on a fake clock, a teacher searched 10 days ago isn't queued, and one searched 35 days ago is
  - blocking: F-25 a full teacher is queued monthly, and only new candidates are looked at; with `researchFullTeachers` off, it isn't queued
  - blocking: F-25 a library request (a stand-in `request` job) goes ahead of queued teachers
  - blocking: F-25 on a fake clock, the worker runs the nightly tick once a night at the set hour in production, never two at once, and never outside production; the tick syncs and queues the teachers due
  - blocking: F-25 killing the worker mid-teacher and restarting it resumes with no repeated paid call (stub call counts)
  - blocking: F-25 reaching a cap stops the run cleanly; finished portraits stay published, and the report says so
  - blocking: F-25 production's first nightly run sets `first_pass_state` to `active`; while it's `active`, spend is booked to `first_pass` and the night cap doesn't apply; it becomes `done` when the queue first empties or `first_pass` spend reaches $100, after which spend is `regular` under the night and month caps
  - blocking: F-25 `run --dry-run` shows the plan and the estimated spend, and queues nothing
  - blocking: F-25 a snapshot of the fixture run's report covers every field of OUT-06
- Test data: F-23's stub world, read-only from `test/fixtures/f23/`
- Side effects: none
- Parkable: no
- Size: M


### F-44: API: reads, change feed, files, keys
- Phase: 5
- Goal: Serve the read side of the contract (teachers, portraits, history, files and the change feed) behind the library's key, with rate limits, and make and switch off keys by command. Main example: every read route's answers validate against the contract, on a fixture database. Failure example: a switched-off key gets 401. It creates: `apiRouter(deps): Router` in `src/api/router.ts`, mounted in `src/web.ts`, serving `GET /api/v1/teachers`, `/api/v1/teachers/{teacher_id}`, `/api/v1/portraits`, `/api/v1/portraits/{portrait_id}`, `/api/v1/portraits/{portrait_id}/history`, `/api/v1/portraits/{portrait_id}/files/{kind}` and `/api/v1/changes` (in `src/api/reads.ts` and `src/api/changes.ts`); `requireLibraryKey(db)` in `src/api/auth.ts`; `newKey(db, label)`, `switchOffKey(db, keyId)` and `listKeys(db)` in `src/api/keys.ts`; and the command `portraits keys new|off|list`.
- Covers: OUT-14, SCOPE-02, RUN-10
- Defers: IN-06, IN-07 and IN-08 (decisions and requests: F-45)
- Depends on: F-03, F-24, F-49
- Owner input: none
- Owns: `src/api/router.ts`, `src/api/reads.ts`, `src/api/changes.ts`, `src/api/auth.ts`, `src/api/keys.ts`, `src/web.ts` (to mount the router), `src/cli/commands/keys.ts`
- Reads: `brain/spec/requirements.md` OUT-14, RUN-10, SCOPE-02; the contract and `brain/contracts/portraits-api.md` (the change feed's rules)
- Checks:
  - blocking: F-44 every read route's answers validate against the contract (`checkAgainstContract`), on a fixture database
  - blocking: F-44 no key gives 401 `key_off`, a switched-off key gives 401, and a good key gives 200, checked with F-36's `verifySecret` against the `api_keys` hashes (the seeded `test` key included); a new key is shown once
  - blocking: F-44 `since` then `after` pages through every change in order, with `more` and `next_cursor` as the contract says
  - blocking: F-44 with `after`, the answer's `since` is the time of the cursor's entry (the service's start for `c_0`)
  - blocking: F-44 an empty page echoes its cursor as `next_cursor`, with `more: false`; with `since` and nothing after it, `next_cursor` is the cursor of the last change at or before `since` (`c_0` when there's none)
  - blocking: F-44 neither `since` nor `after`, or both, gives 422 `invalid`; a cursor older than 30 days gives 410 `cursor_too_old`
  - blocking: F-44 `/files/{kind}` redirects to a signed link that expires in 15 minutes
  - blocking: F-44 portraits being made, or that failed, never appear
  - blocking: F-44 calls over the rate limit get 429 with `Retry-After`
  - blocking: F-44 `portraits keys new|off|list` work against PGlite, and `list` shows labels and last use, never a key
- Test data: a fixture database with teachers and portraits in every status
- Side effects: none
- Parkable: no
- Size: M


### F-45: API: decisions and requests
- Phase: 5
- Goal: Accept the library's decisions and requests, apply each once, and handle requests in the worker at once. Main example: an approve decision makes the portrait `approved`, in its history and the change feed. Failure example: a turn-down without a reason is refused with `invalid` naming `/reason`. The worker drafts with F-23's `draftOriginal`, reads a pasted link with its source's `fetchById` (F-09's registry), and rewrites `record.json` with F-24's `writeRecordJson`. It creates: `POST /api/v1/decisions` in `src/api/decisions.ts`; `POST /api/v1/requests`, `GET /api/v1/requests` and `GET /api/v1/requests/{request_id}` in `src/api/requests.ts`, both mounted by `src/api/router.ts`; `handleRequest(ctx, requestId): Promise<RequestOutcome>` in `src/pipeline/requests.ts`, run by the job kind `request` (`src/jobs/request.ts`, queued by `POST /api/v1/requests`); and `classifyNote(ctx, note): Promise<"restoration" | "crop" | "outline">` in `src/models/noteKind.ts`, with the prompt `src/models/prompts/note_kind.md` (v2, copied from `prototype/prompts/`).
- Covers: IN-06, IN-07, IN-08, SRC-04
- Defers: PIP-17 (better copies and higher-ranked photographs offered on later runs: F-48)
- Depends on: F-44, F-25
- Owner input: none
- Owns: `src/api/decisions.ts`, `src/api/requests.ts`, `src/api/router.ts` (to mount them), `src/pipeline/requests.ts`, `src/jobs/request.ts`, `src/models/noteKind.ts`, `src/models/prompts/note_kind.md`
- Reads: `brain/spec/requirements.md` IN-06, IN-07, IN-08, SRC-04, PIP-14, OUT-07; the contract (`Decision`, `DecisionResult`, `NewRequest`, `Request`) and `brain/contracts/portraits-api.md`; `brain/decisions.md` D-61
- Checks:
  - blocking: F-45 approve, turn_down (each reason), set_main and correct change the portrait as IN-07 says, and appear in its history and the change feed
  - blocking: F-45 approving a portrait with `replaces` makes the old one `replaced`, with `replaced_by` set; when the replaced one was the main portrait, `main` passes to the new one
  - blocking: F-45 turning down the main portrait clears `main`, and the teacher has none
  - blocking: F-45 a turn-down without a reason is refused with `invalid` naming `/reason`; set_main on a waiting portrait gives `conflict`
  - blocking: F-45 resending the same `decision_id` or `request_id` changes nothing and says it's a duplicate; reusing an id with different content gives `conflict`
  - blocking: F-45 a `try_link` in each of SRC-04's forms is read without fetching the page, and queued; a link anywhere else gets 422 with the reason; a link to a source that isn't registered (a parked card) is answered `refused` with `no_candidates`
  - blocking: F-45 a `try_again` whose note the stubbed model (`note_kind.md`) judges to be about the crop or the outline is answered `refused`, suggesting `another_original`; a restoration note is passed on, and "the line cuts off the left ear" counts as restoration
  - blocking: F-45 `another_original` makes the portrait `turned_down` (reason `other`) and queues the teacher
  - blocking: F-45 an unknown teacher or portrait gets 404; a `try_again` or `another_original` on a turned-down or replaced portrait gets 409
  - blocking: F-45 a `try_again` on a waiting portrait replaces it when done; on an approved one, the new draft is offered with `replaces`, and the approved one (and `main`) stays until the library approves the new one
  - blocking: F-45 a request answers 202 `queued`; the worker sets `working`, then `done` with a new `result_portrait_id`, or `refused` with one of IN-06's codes and no result; each code has a fixture, and each change is in the change feed
  - blocking: F-45 every decision rewrites the portrait's `record.json`
  - blocking: F-45 every answer validates against the contract
- Test data: F-44's fixture database (read-only), canned note answers and F-23's stub world (read-only)
- Side effects: none
- Parkable: no
- Size: M


### F-48: Later runs: better copies, turn-downs, corrections
- Phase: 5
- Goal: On later runs, offer clearly better copies and higher-ranked photographs, bring back a turned-down photograph only when allowed, and never overwrite the library's corrections. Main example: a copy twice the size of an approved portrait's original becomes a new waiting portrait with `replaces` set, and the approved one is untouched. Failure example: a photograph turned down as `do_not_use` coming back on a later run fails the card. It creates: `betterCopyOffers(ctx, teacher, photographs): Promise<Offer[]>` and `fullSlotsOffer(ctx, teacher, photographs): Promise<Offer | null>` in `src/pipeline/offers.ts`, which `processTeacher` (F-23) calls on later runs.
- Covers: PIP-17, PIP-18, OUT-07
- Defers: none
- Depends on: F-23, F-45
- Owner input: none
- Owns: `src/pipeline/offers.ts`, `src/pipeline/teacher.ts` (to call them)
- Reads: `brain/spec/requirements.md` PIP-14, PIP-16, PIP-17, PIP-18, OUT-07; `brain/decisions.md` D-59, D-61
- Checks:
  - blocking: F-48 a 2× better copy of an approved portrait's original becomes a new waiting portrait with `replaces` set, and the approved one is untouched
  - blocking: F-48 a better copy of a waiting portrait's original replaces it, and the old one becomes `replaced`, keeping its files
  - blocking: F-48 a photograph turned down for `quality` comes back once, as a 2× better copy, and not a second time
  - blocking: F-48 one turned down as `not_this_teacher` or `do_not_use` never returns
  - blocking: F-48 with all slots full, PIP-16 is re-run over the three and a new photograph; when the new one is chosen and the one left out is approved and not main, it's offered with `replaces` set to that one
  - blocking: F-48 approving that offer makes the left-out one `replaced`; turning it down leaves the three as they were, and it isn't offered again
  - blocking: F-48 when the one left out is waiting, or the main portrait, nothing is offered, and a photograph PIP-16 wouldn't choose isn't offered
  - blocking: F-48 only one such offer per teacher is open at a time, and an open offer doesn't take a slot (a teacher with three portraits and an offer gets no fourth draft)
  - blocking: F-48 a date and best-known flag corrected by the library survive a re-run
- Test data: F-23's stub world over three runs, read-only from `test/fixtures/f23/`
- Side effects: none
- Parkable: no
- Size: M


### F-46: Admin site
- Phase: 5
- Goal: A read-only, phone-friendly admin site behind one password, whose front page says whether all is well. Main example: after logging in, the front page shows last night's run, the month's spend against its cap and what needs the owner, from a fixture database. Failure example: any page with a form that changes data, other than logging in and out, fails the card. It creates: `adminRouter(deps): Router` in `src/admin/frame.ts`, mounted at `/admin` in `src/web.ts`, which loads every page in `src/admin/pages/` (each exporting `page: { path: string; title: string; render(ctx, req): Promise<string> }`); login and sessions in `src/admin/login.ts`; one stylesheet, `src/admin/style.css`; the pages `front`, `teachers`, `teacher`, `runs`, `run`, `rights`, `held`, `suggestions`, `keys` and `trial` (an empty state until F-28) in `src/admin/pages/`; and the command `portraits password set` (`src/cli/commands/password.ts`).
- Covers: OUT-13, RUN-09, RUN-10
- Defers: TRI-05 (the trial board: F-28)
- Depends on: F-25, F-32, F-44
- Owner input: none
- Owns: `src/admin/frame.ts`, `src/admin/login.ts`, `src/admin/style.css`, `src/admin/pages/`, `src/web.ts` (to mount the site), `src/cli/commands/password.ts`
- Reads: `brain/spec/requirements.md` OUT-06, OUT-13, RUN-09, RUN-10, SRC-02, SRC-12, IN-02, IN-13; `brain/decisions.md` D-33, D-68; `brain/spec/architecture.md` (Settings: `checkPageRgb`)
- Checks:
  - blocking: F-46 every page needs a login, checked with F-36's `verifySecret` against `app_settings.admin_password_hash`, which `portraits password set` writes as a slow hash
  - blocking: F-46 a wrong password locks out after the set number of tries
  - blocking: F-46 the session cookie is secure, HTTP-only and SameSite, and lasts 30 days
  - blocking: F-46 the front page shows last night's run, the month's spend against its cap (and the first pass's against $100 while it's active), errors since the last run, and what needs the owner: teachers to identify, held originals, bad rows in the authors list and anything stuck
  - blocking: F-46 the teacher list, one teacher (all versions, the rights record and the library's decisions), the runs and one run's report render from the fixture database
  - blocking: F-46 every portrait is shown on the dark page colour (`checkPageRgb`), never on white
  - blocking: F-46 `/admin/trial` shows "No trial run yet"
  - blocking: F-46 held originals are listed with their source and licence
  - blocking: F-46 the rights-log CSV, and the suggestions CSV (the teachers' stored suggestions, in `authors.csv`'s columns plus the evidence), download with the right columns; with no suggestions, the page shows an empty state
  - blocking: F-46 no page has a form that changes data, except logging in and out
  - blocking: F-46 every page is laid out for 390 px: it has the viewport meta tag, no style sets a fixed width over 390 px, and tables sit in horizontally scrolling wrappers
  - blocking: F-46 no key or secret appears on any page
  - blocking: F-46 a dependency check finds no mail-sending package and no SMTP code
  - blocking: F-46 a new file in `src/admin/pages/` is picked up without editing any other file
- Test data: F-44's fixture database, read-only
- Side effects: none
- Parkable: no
- Size: M


### F-22: Commands and `doctor`
- Phase: 5
- Goal: Finish the command-line tool with `doctor` and `status`. Main example: `doctor` reports the settings, each secret's presence, the models and their prices, and each source's reachability, and spends nothing. Failure example: `doctor` with a secret missing exits non-zero, naming it and never showing a value. It creates: `runDoctor(ctx): Promise<DoctorReport>` in `src/doctor.ts`, and the commands `portraits doctor` and `portraits status` (`src/cli/commands/doctor.ts`, `src/cli/commands/status.ts`).
- Covers: RUN-05
- Defers: none
- Depends on: F-17, F-25, F-44
- Owner input: none
- Owns: `src/doctor.ts`, `src/cli/commands/doctor.ts`, `src/cli/commands/status.ts`
- Reads: `brain/spec/requirements.md` RUN-04, RUN-05, IN-11; `brain/spec/architecture.md` (Secrets)
- Checks:
  - blocking: F-22 `doctor` reports the settings, each secret's presence (never its value), the models and prices from settings, and each source's reachability (replayed), and exits non-zero on a problem
  - blocking: F-22 `doctor` makes no paid call and writes nothing
  - blocking: F-22 `status` shows the queue, recent runs and the spend, against PGlite
- Test data: F-44's fixture database (read-only); replayed source answers
- Side effects: none
- Parkable: yes
- Size: S


### F-05: Library stub
- Phase: 5
- Goal: A small program that plays the library: it pulls the change feed, fetches portraits and files, checks their SHA-256 and sends decisions and requests, proving the API from the other side; and a job that seeds fixture portraits for it on staging. Main example: against the in-process app on a fixture database, it pages the whole feed, verifies every file and reports success. Failure example: a file whose bytes don't match its SHA-256 is refused, naming it. It creates: `runLibraryStub({ baseUrl, key }): Promise<StubReport>` in `tools/library-stub.ts`, run as `npm run library-stub -- --base-url <url> --key <key>` (reading `HARNESS_URL` and `PORTRAITS_TEST_LIBRARY_KEY` when they aren't given); and the job kind `seed_fixtures` (`src/jobs/seed_fixtures.ts`), which publishes fixture portraits made from synthetic images in stub mode, marked as fixtures in their history, and is refused in production.
- Covers: OUT-10, AC-03
- Defers: none
- Depends on: F-45
- Owner input: none
- Owns: `tools/library-stub.ts`, `src/jobs/seed_fixtures.ts`
- Reads: `brain/spec/requirements.md` OUT-10, IN-06, IN-07, IN-08, RUN-11, AC-03; the contract; `brain/decisions.md` D-13, D-58
- Checks:
  - blocking: F-05 against the in-process app on a fixture database, the stub pages the whole feed, downloads every file and verifies its SHA-256, sends one decision and one request of each kind and resends one of each, and reports success
  - blocking: F-05 a portrait whose file doesn't match its SHA-256 is refused, naming it
  - blocking: F-05 `tools/library-stub.ts` imports nothing from `src/` except `src/api/schemas.ts`, the contract's types
  - blocking: F-05 a `seed_fixtures` job publishes portraits the stub can pull, each marked as a fixture and none made from the owner's examples (D-13); in production it's refused
- Test data: F-44's fixture database, read-only
- Side effects: none
- Parkable: no
- Size: S


### F-26: End-to-end offline run
- Phase: 5
- Goal: Prove it: one full offline run, from the authors list to the library stub's decisions and the next run's response, with stubs. Main example: six teachers sync, a run publishes portraits for those with candidates, and the next run handles the library's requests first. Failure example: a fake secret appearing in any file, log line or answer the run produced fails the card. This is Phase 5's gate card; the verifier adds its tests here. It creates nothing: it's a gate.
- Covers: AC-01, AC-02, AC-03, RUN-07
- Defers: none
- Depends on: F-05, F-46, F-48
- Owner input: none
- Owns: none
- Reads: `brain/spec/requirements.md` SRC-08, SRC-12, IN-11, RUN-07, AC-01, AC-02, AC-03; the contract
- Checks:
  - blocking: `npm test` (the full suite)
  - blocking: F-26 a fixture `authors.csv` with six teachers syncs, and a run publishes portraits for those with candidates, each record complete (SRC-08) and valid against the contract
  - blocking: F-26 the library stub then approves one portrait, turns one down as `not_this_teacher`, sets a main portrait, and sends a `try_again` and a `try_link`
  - blocking: F-26 the next run handles the requests first, skips the teacher whose slots are full, never tries the turned-down photograph again, and publishes the swap when a better copy is approved
  - blocking: F-26 the rights log has one row per original considered, and a second run adds no duplicates
  - blocking: F-26 a scan of every file, log line and answer the run produced finds none of the fake secrets
- Test data: F-23's stub world, extended to six teachers
- Side effects: none
- Parkable: no
- Size: M


---

## Phase 6: Live

### F-27: Live smoke test on staging
- Phase: 6
- Goal: Prove it: on staging, with the real models, one real teacher goes end to end within $2, and the library stub completes against staging. Main example: a `run` job for Charles Fillmore publishes at least one portrait whose files all pass their checkers. Failure example: a file failing its checker fails the card. It creates nothing: it's a prove-it card.
- Covers: OUT-10
- Defers: none
- Depends on: F-26
- Owner input: none
- Owns: none (prove it: the tests come from the test author, and the code is already merged)
- Reads: `brain/spec/requirements.md` OUT-10, OUT-14, RUN-04, RUN-10, RUN-11; the contract
- Checks:
  - blocking, smoke, live, needs O-4, needs O-9, needs O-10, needs O-13: F-27 on staging, a `sync` job, then a `run` job for `charles-fillmore`, publish at least one real portrait within $2, and every file passes its checker
  - blocking, smoke, needs O-13: F-27 staging's spend shows each of those calls' actual cost, and the night's total is under staging's cap
  - blocking, smoke, needs O-13: F-27 staging's health answers 200; the API answers 401 without the library key and 200 with the test key
  - blocking, smoke, needs O-13: F-27 after a `seed_fixtures` job, the library stub completes against staging, SHA-256s included, and the seeded portraits are marked as fixtures
  - blocking, smoke, needs O-13: F-27 logging in to the admin site with the test password works, and the front page and the teacher list open
- Test data: none
- Side effects: paid (≤ $2), staging only; external write (the seed, staging only)
- Parkable: no
- Size: M


### F-28: The trial, its board and its result
- Phase: 6
- Goal: Build the trial: pick the set from a survey report, run each enhance model on each original with and without the blend, score them, choose the winner and show the board, all offline with stubs. Main example: from a fixture survey report and canned answers, the result names the winner by TRI-04 and the board shows every contender side by side. Failure example: a stubbed trial that touches the portraits, candidates or changes tables fails the card. It creates: `pickTrialSet(surveyReport, examples): TrialItem[]` in `src/pipeline/trialSet.ts`; `runTrial(ctx, opts): Promise<TrialResult>` and `chooseWinner(scores): Winner` in `src/pipeline/trial.ts`; the job kinds `trial` and `trial_examples`; the page `GET /admin/trial`; the command `portraits trial`. The contract step settles their exact types.
- Covers: TRI-01, TRI-03, TRI-04, TRI-05, TRI-07, TRI-09
- Defers: TRI-02 (the real set, from staging's survey: F-52), TRI-06 (written into the settings: F-50), TRI-08 (the examples: F-29)
- Depends on: F-26, F-38
- Owner input: none
- Owns: `src/pipeline/trial.ts`, `src/pipeline/trialSet.ts`, `src/jobs/trial.ts`, `src/jobs/trial_examples.ts`, `src/admin/pages/trial.ts`, `src/cli/commands/trial.ts`
- Reads: `brain/spec/requirements.md` TRI-01..TRI-09, PIP-13, PIP-20, OUT-13; `brain/decisions.md` D-47, D-56, D-68; `design/portraits/README.md`
- Checks:
  - blocking: F-28 the set picked from a fixture survey report covers every case in TRI-02
  - blocking: F-28 each contender runs on each original, with and without the blend
  - blocking: F-28 the winner follows TRI-04: the best total score, or the cheaper within 5%
  - blocking: F-28 the result holds the winner, every score and cost, the engraving results and PIP-20's re-measured thresholds, in the shape F-50 reads
  - blocking: F-28 a stubbed trial leaves the portraits, candidates and changes tables unchanged, and its files are under `trial/<trial_run_id>/`
  - blocking: F-28 the trial stops cleanly at its $27 sub-budget, and the examples at $3 (stubbed costs)
  - blocking: F-28 `trial_examples` reads the owner's originals and targets bundled from `design/portraits/`, and never publishes them (D-13)
  - blocking: F-28 the board shows a row per original with every contender side by side, each beside its no-blend version, on the dark page colour, laid out for 390 px as F-46's pages are (viewport meta tag, no fixed width over 390 px)
- Test data: a fixture survey report and canned model answers
- Side effects: none
- Parkable: no
- Size: L


### F-52: Run the trial on staging
- Phase: 6
- Goal: Prove it: the trial runs on staging with the real models, within $27, and its result names a winner for F-50 to apply. Main example: sync, survey and trial jobs finish, and the result scores every contender. Failure example: the trial's spend passing $27 fails the card. It creates nothing: it's a prove-it card.
- Covers: TRI-02
- Defers: TRI-06 (F-50)
- Depends on: F-28
- Owner input: none
- Owns: none (prove it)
- Reads: `brain/spec/requirements.md` TRI-01..TRI-07, RUN-11
- Checks:
  - blocking, smoke, live, needs O-4, needs O-9, needs O-10, needs O-13: F-52 on staging, a `sync` job, a `survey` job and a `trial` job finish, and the trial's spend is at most $27
  - blocking, smoke, needs O-13: F-52 the trial's result names a winner by TRI-04, with every contender scored
  - report, smoke, needs O-13: F-52 each item's expected outcome held (for example, the group photo refused at the pre-check)
  - report, smoke, needs O-13: F-52 the engraving results, for the owner's verdict on `allowedMedia` (D-47)
  - report, smoke, needs O-13: F-52 PIP-20's thresholds on the survey's real pairs, flagging any two sittings of one teacher that would be judged "same"
- Test data: none
- Side effects: paid (≤ $27), staging only; network; external write (the trial's rows and files, staging only)
- Parkable: no
- Size: M
- Stop if: the trial would pass $27


### F-50: The trial's winner in the settings
- Phase: 6
- Goal: Write the trial's result into the settings with a new `recipeVersion`. A job on a deployed copy can't change the repo, so this card does (TRI-06). Main example: the recorded result's winning model and thresholds land in `settings.ts` under a new version. Failure example: changing the recipe without a new version fails STY-05's check. It merges at once, with its notice on the control issue; the owner's `/veto` reverts it. It changes only `src/config/settings.ts`: the enhance model, the blend and any thresholds the trial set, under a new `recipeVersion`.
- Covers: TRI-06
- Defers: none
- Depends on: F-52
- Owner input: none
- Owns: `src/config/settings.ts`
- Reads: `brain/spec/requirements.md` TRI-04, TRI-06, STY-05, PIP-20; `brain/decisions.md` D-47, D-56
- Checks:
  - blocking: F-50 the settings hold the recorded result's winning model and blend, and any thresholds it changed, under a new `recipeVersion`
  - blocking: F-50 STY-05's hash check passes for the new version
  - blocking: F-50 F-16's parity test still uses its frozen 0.5.0 copy, and passes
  - report: F-50 the change, set out for the notice: the winner, its scores and cost, and the engraving results
- Test data: record: `npm run record-ops -- F-50 --kind trial --url {url}` (needs O-13), run against staging: it saves the latest trial result from staging's ops API to `test/fixtures/f50/` (F-49's recorder)
- Side effects: network (the recording, from staging)
- Parkable: no
- Size: S
- Stop if: the recorded result has no winner


### F-29: The examples reproduced
- Phase: 6
- Goal: Prove it: with the trial's defaults, the pipeline reproduces the owner's three hand-made portraits closely enough. Main example: each example passes "compare with target", and the code measures meet TRI-08. Failure example: an example appearing in any portrait, candidate or change fails the card (D-13). It creates nothing: it's a prove-it card.
- Covers: TRI-08, IN-09, AC-04
- Defers: none
- Depends on: F-50
- Owner input: none
- Owns: none (prove it)
- Reads: `brain/spec/requirements.md` TRI-08, IN-09; `design/portraits/README.md`
- Checks:
  - blocking, smoke, live, needs O-4, needs O-13: F-29 a `trial_examples` job on staging finishes within $3, reusing the trial's cache
  - blocking, smoke, needs O-13: F-29 the examples appear in no portrait, candidate or change
  - report, smoke, needs O-13: F-29 "compare with target" passes for each example
  - report, smoke, needs O-13: F-29 the code measures at the owner's framing meet TRI-08: overlap ≥ 0.85, tone error ≤ 0.08, dots across 110 ± 2, no STY-06 problems
- Test data: none
- Side effects: paid (≤ $3), staging only; external write (the examples' trial rows, staging only)
- Parkable: yes (the measures are reported; the release doesn't depend on this card)
- Size: S


### F-47: The release
- Phase: 6
- Goal: Prove it: the release candidate works on its deployed copy, with the trial's defaults in its settings. The conductor then promotes that exact build to production after the 24-hour veto window (D-66): it puts the build staging tested on production's web and worker deployment services (harness HD-70), and they migrate themselves at start-up. It's production's first deploy, and its nightly schedule is on from then (RUN-08). The owner's steps around it are on the release checklist. This is Phase 6's gate card; the verifier adds its tests here. It creates nothing: it's a prove-it card and Phase 6's gate.
- Covers: RUN-08
- Defers: RUN-04 (the first pass is watched over the nights it takes, on the release checklist), AC-05 (completed by the harness's own record)
- Depends on: F-27, F-50
- Owner input: none
- Owns: none (prove it)
- Reads: `brain/plan/build-plan.md` §4 and §7; `brain/plan/release-checklist.md`; `brain/spec/requirements.md` RUN-04, RUN-08, RUN-12
- Checks:
  - blocking: `npm test` (the full suite)
  - blocking: F-47 the settings carry the trial's `recipeVersion` (F-50), and production's schedule is on from its first deploy
  - blocking, smoke, needs O-13: F-47 the deployed copy's health shows this commit, with the database and bucket working
  - blocking, smoke, needs O-13: F-47 after a `seed_fixtures` job, the library stub completes against the deployed copy
  - blocking, smoke, needs O-13: F-47 staging's spend so far is within the trial's and staging's caps
  - report, smoke, needs O-13: F-47 for the release notice: teachers with no candidate and teachers skipped for missing ids (from staging's survey), and the spend so far
- Test data: none
- Side effects: deploy (pull-request copies); production (promoted by the conductor after the 24-hour window, D-66); external write (the seed, on the deployed copy)
- Parkable: no
- Size: S
- Stop if: the trial's winner (F-50) was vetoed and not replaced


---

## Withdrawn

- **F-20 · Model-drawn outline:** *withdrawn* by D-49. The outline is drawn by code (F-15).
- **F-33 · Internet Archive book plates:** *withdrawn* by D-24.
