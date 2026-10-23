# Feature cards (build order)

**Status: draft 4 (Claude, 2026-10-21),** for the hosted TypeScript app (D-31..D-68), in the Coding Harness's **format 1** (`../../Coding Harness Instructions.md` §5, D-65). Draft 3 merged Argon's review; draft 4 adapts the cards to the harness.
- **Converted so far, as the sample for the harness chat's `harness cards check`:** F-01, F-51, F-04, F-36, F-49, F-53, F-31, F-07, F-38, F-54, F-55, F-23, F-27, F-28, F-52, F-50, F-29 and F-47 (headings with a colon). The others still use draft 3's fields (headings with "·") and are converted once the sample passes. Their dependencies are already settled here (no soft dependencies).
- The harness builds them one at a time, **in the order of the overview table**, each once every card in its *Depends on* is merged. IDs are permanent, so the build order isn't numeric. Retired cards keep their IDs as *withdrawn*.

**How checks run** ([build-plan.md §4–5](build-plan.md)):
- **Tests first** (D-65): Codex writes each card's acceptance tests from Gemini's list of cases, in `test/fNN-*.test.ts` with fixtures in `test/fixtures/fNN/`, and they're locked before Claude builds (after the contract, on size L cards). Each test case has a unique name starting with its card's ID (`"F-07: …"`). One card's tests run by path, printing TAP: `./node_modules/.bin/tsx --test --test-reporter=tap "test/f07-*.test.ts"`. F-01, the setup card, skips this step.
- **Each card says what it creates** (module paths and exported names, routes or commands) in its `Goal`, so the test author's tests and the builder's code meet. The converted cards do; the others will when they're converted.
- Offline by default: outbound calls refused, no keys, PGlite for the database.
- *Smoke* checks run on a deployed copy (`npm run smoke -- --url {url}`), over HTTP, with that environment's test credentials (O-13): the pull request's copy, or staging for Phase 6's prove-it cards. Their tests are `test/fNN-*.smoke.ts`, which `npm test` never runs. *Live* checks make paid calls, on staging only. No check touches production.
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
| 3 | F-03 | The API contract in code | 1 | F-01 | none | none | no | draft 3 |
| 4 | F-04 | Database, queue and step cache | 1 | F-01, F-51 | none | migration | no | 1 |
| 5 | F-37 | Storage bucket client | 1 | F-01, F-51 | none | none | no | draft 3 |
| 6 | F-36 | Northflank setup, deploys and the health check | 1 | F-01, F-04, F-37 | O-8, O-14 | deploy, migration | no | 1 |
| 7 | F-49 | Jobs started over the web | 1 | F-04, F-36 | none | deploy | no | 1 |
| 8 | F-53 | Phase 1 gate | 1 | F-03, F-49 | none | deploy | no | 1 |
| 9 | F-02 | Authors list reader and row checks | 2 | F-01 | none | none | no | draft 3 |
| 10 | F-06 | Outbound client | 2 | F-01, F-04, F-51 | none | none | no | draft 3 |
| 11 | F-08 | Wikidata: fetch, check, find ids | 2 | F-06 | none | network | no | draft 3 |
| 12 | F-31 | Teacher sync through GitHub | 2 | F-02, F-04, F-06, F-08, F-49 | none | network, deploy | no | 1 |
| 13 | F-07 | Licence classifier and credit lines | 2 | F-06 | none | network | no | 1 |
| 14 | F-32 | Rights log | 2 | F-04, F-07 | none | none | no | draft 3 |
| 15 | F-09 | Commons: P18 and depicts | 2 | F-07, F-08 | none | network | no | draft 3 |
| 16 | F-10 | Library of Congress pictures | 2 | F-07, F-32 | none | network | yes | draft 3 |
| 17 | F-34 | Wellcome Collection | 2 | F-07, F-32 | none | network | yes | draft 3 |
| 18 | F-35 | Finding missing dates and ids | 2 | F-08, F-31 | none | network | yes | draft 3 |
| 19 | F-38 | Coverage survey | 2 | F-09, F-31, F-49 | none | network, deploy | no | 1 |
| 20 | F-54 | Phase 2 gate | 2 | F-32, F-38 | none | none | no | 1 |
| 21 | F-39 | Porting spike: OpenCV.js and sharp | 3 | F-01, F-51 | none | none | no | draft 3 |
| 22 | F-12 | Face landmarks and crop | 3 | F-39 | none | none | no | draft 3 |
| 23 | F-13 | Descreen and edge-preserving blur | 3 | F-12 | none | none | no | draft 3 |
| 24 | F-14 | Tone and halftone | 3 | F-39 | none | none | no | draft 3 |
| 25 | F-15 | Mask, code outline, master and cut-out limits | 3 | F-12, F-14 | none | none | no | draft 3 |
| 26 | F-30 | AI copy: key mask, alignment, drift check, blend | 3 | F-12, F-13 | none | none | no | draft 3 |
| 27 | F-41 | Black-and-white, 500 px and viewing copies | 3 | F-15 | none | none | no | draft 3 |
| 28 | F-42 | Same photograph or different (code layers) | 3 | F-12 | none | none | no | draft 3 |
| 29 | F-16 | Parity with the Python prototype | 3 | F-13, F-15, F-30, F-41, F-42 | none | none | no | draft 3 |
| 30 | F-17 | OpenRouter client, spend ledger and caps | 4 | F-04, F-06 | none | none | no | draft 3 |
| 31 | F-18 | Pre-check | 4 | F-17, F-41 | none | none | no | draft 3 |
| 32 | F-19 | AI copy and keyed cut-out calls | 4 | F-17, F-30, F-41 | none | none | no | draft 3 |
| 33 | F-21 | Draft check and compare-with-target | 4 | F-17, F-15, F-41 | none | none | no | draft 3 |
| 34 | F-43 | Same-photograph tie-break | 4 | F-17, F-41, F-42 | none | none | no | draft 3 |
| 35 | F-11 | Candidates: gather, previews, group, order | 4 | F-09, F-32, F-37, F-42, F-43 | none | none | no | draft 3 |
| 36 | F-55 | Phase 4 gate | 4 | F-11, F-18, F-19, F-21 | none | none | no | 1 |
| 37 | F-24 | Publishing a portrait | 5 | F-03, F-04, F-07, F-37, F-41 | none | none | no | draft 3 |
| 38 | F-23 | Per-teacher pipeline and failure policy | 5 | F-11, F-16, F-18, F-19, F-21, F-24 | none | none | no | 1 |
| 39 | F-25 | Queue, schedule and run reports | 5 | F-23, F-31, F-36 | none | none | no | draft 3 |
| 40 | F-44 | API: reads, change feed, files, keys | 5 | F-03, F-24, F-49 | none | none | no | draft 3 |
| 41 | F-45 | API: decisions and requests | 5 | F-44, F-25 | none | none | no | draft 3 |
| 42 | F-48 | Later runs: better copies, turn-downs, corrections | 5 | F-23, F-45 | none | none | no | draft 3 |
| 43 | F-46 | Admin site | 5 | F-25, F-32, F-44 | none | none | no | draft 3 |
| 44 | F-22 | Commands and `doctor` | 5 | F-17, F-25, F-44 | none | none | yes | draft 3 |
| 45 | F-05 | Library stub | 5 | F-45 | none | none | no | draft 3 |
| 46 | F-26 | End-to-end offline run | 5 | F-05, F-46, F-48 | none | none | no | draft 3 |
| 47 | F-27 | Live smoke test on staging | 6 | F-26 | none | paid (≤ $2), staging only; external write | no | 1 |
| 48 | F-28 | The trial, its board and its result | 6 | F-26, F-38 | none | none | no | 1 |
| 49 | F-52 | Run the trial on staging | 6 | F-28 | none | paid (≤ $27), staging only; network; external write | no | 1 |
| 50 | F-50 | The trial's winner in the settings | 6 | F-52 | none | network | no | 1 |
| 51 | F-29 | The examples reproduced | 6 | F-50 | none | paid (≤ $3), staging only; external write | yes | 1 |
| 52 | F-47 | The release | 6 | F-27, F-50 | none | deploy (pull-request copies; production, after the window); external write | no | 1 |
| — | F-20 | ~~Model-drawn outline~~ | — | — | — | — | — | *withdrawn* (D-49) |
| — | F-33 | ~~Internet Archive book plates~~ | — | — | — | — | — | *withdrawn* (D-24) |

**No soft dependencies.** A card lists only the cards that must be merged before it. A card that can be built without another doesn't list it, and its checks don't rely on it. If a parkable card (F-10, F-34, F-35, F-22, F-29) is parked, nothing waits for it: the sources register themselves (F-11), the admin site shows an empty state for F-35's suggestions, and the release doesn't depend on F-29.

F-52 and F-29 share the trial's $30 budget (TRI-07). O-10 (the User-Agent contact) is needed only where a check or a recording calls a live source; offline checks use a placeholder. SCOPE-01..04 are boundaries rather than features; reviewers check them, and F-06's allowlist test enforces AC-06. OUT-08 (the zip) is withdrawn (D-58).

---

## Phase 1: Foundation and deploys

### F-01: Repo, toolchain and offline test runner
- Phase: 1
- Goal: A TypeScript repo on Node 24, matching the library's toolchain, whose `check`, `test` and `build` commands run offline. Main example: `npm test` runs with every outbound call refused and reports how many tests ran. Failure example: a test that tries to reach the network fails at once. This is a setup card: its checks are the commands themselves, so it skips the tests-first step. It creates: the scripts `check`, `test` (`tsx --test` over `test/**/*.test.ts`) and `build` in `package.json`; the command-line entry `src/cli.ts` (`node dist/cli.js <command>`), which loads every file in `src/cli/commands/`, each exporting `command: { name: string; describe: string; run(args: string[]): Promise<number> }`.
- Covers: RUN-06
- Defers: RUN-05 (each command arrives with its own card; F-22 finishes them)
- Depends on: none
- Owner input: none
- Owns: `package.json` (with the `check`, `test` and `build` scripts), `package-lock.json`, `.nvmrc`, `tsconfig.json`, `esbuild.config.mjs`, `test/setup.ts` (the test runner's settings: outbound calls refused, no keys), `test/setup.test.ts`, `src/cli.ts`, `src/cli/commands/`
- Reads: `brain/spec/architecture.md` (Stack, Modules); `harness.yaml` (commands); `brain/plan/build-plan.md` §5
- Checks:
  - blocking: `npm ci` installs from the lock file, including `@techstark/opencv-js` and `sharp` (so F-36's health check can report them)
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
- Goal: Typed, committed settings and secrets from the environment. Main example: recipe 0.5.0's settings load and start-up goes ahead. Failure example: a setting of the wrong type, or a recipe change without a new `recipeVersion`, stops start-up and names it. It creates: `settings` and `loadSettings(overrides?)` in `src/config/settings.ts`; `readEnv(env = process.env): Env` (throwing `ConfigError`, which names the variable), with `env.environment` from `PORTRAITS_ENV`, in `src/config/env.ts`; `recipeHash(recipe)` and `RECIPE_HASHES` (version → hash) in `src/config/recipeHash.ts`.
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
  - blocking: F-51 the bucket settings come from `S3_ENDPOINT`, `S3_BUCKET`, `S3_ACCESS_KEY_ID` and `S3_SECRET_ACCESS_KEY`; in `preview`, a missing `S3_PREFIX` stops start-up, and outside `preview` one that is set does
  - blocking: F-51 `USER_AGENT_CONTACT` fills the User-Agent. Without it, tests use a placeholder; staging and production still start and answer health, but refuse calls to the sources, naming the missing variable
- Test data: valid and invalid settings objects
- Side effects: none
- Parkable: no
- Size: S


### F-03 · The API contract in code
- **Phase:** 1
- **Goal:** The app's request and answer types follow `contracts/portraits-api.openapi.json` exactly, and a reusable test helper checks any answer against it.
- **Covers:** OUT-14 (contract), OUT-02, OUT-10 (samples), IN-06 and IN-07 (body schemas), AC-02 (validation part)
- **Depends on:** F-01
- **Owner input:** none
- **Build:**
  - `src/api/schemas.ts` (zod types mirroring the contract's schemas);
  - `test/helpers/contract.ts` (ajv 2020-12, compiled from the OpenAPI file);
  - `npm run check:api`, a TypeScript port of `brain/contracts/check_api.py`;
  - the contract and samples copied to `contracts/` at the repo root, byte for byte.
- **Checks:**
  - Every sample in `portraits-api.sample.json` validates against its schema with ajv, and parses with the matching zod type.
  - The thirteen refused payloads from `check_api.py` are refused by both ajv and zod. Examples: a turn-down without a reason; an unknown field in a decision; an `approx_date` given as text; a `refused_reason` that isn't one of the codes; a health answer without `database`.
  - zod and ajv agree on 10 good and 10 bad generated payloads per request body. The contract constrains a `correct` decision's `value` by its `field` (a year or null for `approx_date`, true or false for `best_known`), so a discriminated zod union agrees with it.
  - A test fails if `contracts/portraits-api.openapi.json` differs from `brain/contracts/portraits-api.openapi.json`, so the two copies can't drift.
- **Test data:** the contract's samples.
- **Live calls:** none
- **Parkable:** no
- **Size:** S

### F-04: Database, queue and step cache
- Phase: 1
- Goal: The records in Postgres through Drizzle, a job queue that survives crashes, and a cache of paid step results. Main example: the migrations run from empty and every table records and reads back. Failure example: a job whose worker stops is claimed again and resumes at its last finished step. It creates: the Drizzle tables in `src/db/schema.ts`, named as in T-07; `openDb(url)` and `openTestDb()` (PGlite, migrated, for every later card's tests) in `src/db/client.ts`; `enqueue`, `claim`, `heartbeat`, `finish`, `fail` and `reclaimStale` in `src/queue.ts`; `cacheKey({ images, step, model, promptVersion, note, attempt })`, `getCached` and `putCached` in `src/cache.ts`.
- Covers: RUN-03
- Defers: RUN-04 (the spend ledger is stored here; caps in F-17, the first pass in F-25), PIP-12 (set-asides used in F-23), IN-08 (applied once in F-45), TRI-09 (the trial tables are used in F-28)
- Depends on: F-01, F-51
- Owner input: none
- Owns: `src/db/schema.ts`, `src/db/migrations/`, `src/db/client.ts`, `drizzle.config.ts`, `src/queue.ts`, `src/cache.ts`
- Reads: `brain/topics/T-07-records.md` (with its additions of 2026-10-20); `brain/spec/architecture.md` (Database); `brain/spec/requirements.md` RUN-03, RUN-04, RUN-12, TRI-09
- Checks:
  - blocking: F-04 the migrations run from empty, and every table records and reads back (`teachers`, `candidates`, `photographs`, `portraits`, `files`, `portrait_events`, `library_decisions`, `requests`, `runs`, `spend` with its `budget`, `jobs`, `step_cache`, `api_keys`, `changes`, `sessions`, `trial_runs`, `trial_items`, `app_settings`)
  - blocking: F-04 two workers claiming at once never get the same job (two connections)
  - blocking: F-04 a job whose worker stops heartbeating is claimed again after the timeout, and resumes at its last finished step
  - blocking: F-04 the step cache hits for the same key, and misses when any image's SHA-256, the step, the model, the prompt version, the note or the attempt changes
  - blocking: F-04 a remake (attempt 1) and a `try_again` without a note both miss; changing `recipeVersion` alone still hits
  - blocking: F-04 the `changes` table hands out increasing sequence numbers, also inside concurrent transactions
  - blocking: F-04 no migration drops, renames or rewrites a table or column (RUN-12)
- Test data: a PGlite helper that later cards' tests reuse
- Side effects: migration (pull-request copies, staging)
- Parkable: no
- Size: M


### F-37 · Storage bucket client
- **Phase:** 1
- **Goal:** Store and fetch a portrait's files in the environment's private bucket on Cloudflare R2 (D-70), under OUT-12's layout and the copy's prefix, and hand out 15-minute signed links.
- **Covers:** OUT-12 (layout), RUN-10 (private bucket, signed links)
- **Depends on:** F-01, F-51
- **Owner input:** none
- **Build:** `src/storage/bucket.ts` (`@aws-sdk/client-s3`, `s3-request-presigner`; endpoint `S3_ENDPOINT`, region `auto`, every key under `S3_PREFIX` when it's set); an in-memory fake with the same interface for tests; layout helpers.
- **Checks:**
  - Putting and getting a file round-trips, with its SHA-256 and content type.
  - Keys follow `portraits/<teacher_id>/<portrait_id>/<file>`, or `trial/<trial_run_id>/<file>` for the trial (TRI-09). Any other key, or a bad id (path characters, `..`), is refused.
  - A signed link expires after 15 minutes (the fake checks the expiry it was given).
  - Nothing is ever deleted by the client's normal calls; there's no delete method outside tests.
  - With a prefix (a pull-request copy, `pr-12/`), every key written or read starts with it, and the layout check applies after it.
- **Test data:** small files.
- **Live calls:** none (the real bucket, on R2, is first used in F-36's smoke checks)
- **Parkable:** no
- **Size:** S

### F-36: Northflank setup, deploys and the health check
- Phase: 1
- Goal: The app deploys itself to Northflank (D-70), set up as code, and its health check proves it really works. The templates in `northflank/` make: in the staging project, a pipeline whose release flow builds, migrates and deploys `main` on each merge, and a preview template for pull-request copies (own empty Postgres, the preview secret group, a 3-day lifetime); in the production project, a release flow that builds a given commit, backs up the database, migrates and deploys; in each, web and worker services, a `migrate` job and a Postgres add-on; and production's nightly cron job, never two at once. Main example: the pull request's copy answers `/api/v1/health` with this commit, and the database and bucket working. Failure example: with the database unreachable, health answers 503 and names it. It creates: the templates in `northflank/`; `createApp(deps)` (Express) in `src/web.ts`, serving `GET /api/v1/health` (readiness) and `GET /api/v1/live` (liveness); `checkHealth(deps): Promise<Health>` in `src/health.ts`; `hashSecret(plain)` and `verifySecret(plain, hash)` in `src/auth/hash.ts`; `seedTestCredentials(db, env)` in `src/config/seed.ts`; the worker and cron entries (`src/worker.ts`, `src/cron.ts`); `runMigrations(db)` and the migrate job's entry in `src/migrate.ts`; and `npm run smoke -- --url <url>` (`scripts/smoke.ts`).
- Covers: RUN-01, RUN-12
- Defers: RUN-08 (the nightly jobs: F-25), RUN-10 (keys, login and caps: F-44, F-46, F-17)
- Depends on: F-01, F-04, F-37
- Owner input: O-8, O-14
- Owns: `northflank/`, `src/web.ts`, `src/worker.ts`, `src/cron.ts`, `src/migrate.ts`, `src/health.ts`, `src/auth/hash.ts`, `src/config/seed.ts`, `scripts/smoke.ts`, `package.json` (the `smoke` and `migrate` scripts), `docs/northflank-dashboard-steps.md`
- Reads: `brain/spec/architecture.md` (Stack, Northflank layout, Modules, Secrets, Environments); `brain/spec/requirements.md` RUN-01, RUN-10, RUN-12, OUT-12; the contract's `Health`, `/api/v1/health` and `/api/v1/live`; `harness.yaml` (deploy); `brain/handoffs/harness-throwaway-test.md` (what HT-02..HT-04, HT-07, HT-11..HT-13, HT-32 and HT-33 proved)
- Checks:
  - blocking: F-36 health answers 200 with the version, the commit, the environment's name, the database's and bucket's names, and `database`, `bucket`, `opencv` and `sharp` true, against working fakes
  - blocking: F-36 no health answer contains a secret or a connection string
  - blocking: F-36 with the database or the bucket failing (faked), health answers 503 and names it in `failing`, while `/api/v1/live` still answers 200
  - blocking: F-36 `runMigrations` brings an empty database up to date, and run again changes nothing
  - blocking: F-36 health's answers validate against the contract's `Health`
  - blocking: F-36 in staging and pull-request environments, start-up seeds the test admin password and library key as hashes; in production it never does
  - blocking: F-36 the cron entry exits 0 with "nothing to do"
  - blocking: F-36 `npm run smoke -- --url <url>` runs every `test/**/*.smoke.ts` (and nothing else) against that address, with the environment's test credentials passed in
  - blocking: F-36 every file in `northflank/` parses as JSON, and none holds a secret value: the scan finds none of the fake secrets
  - blocking, smoke: F-36 the deployed copy's `/api/v1/health` answers 200 with this commit, and the database and bucket working
  - blocking, smoke: F-36 the pull request's copy names its own environment, database and bucket, none of them production's
  - report: F-36 the preview template links only the preview secret group (no AI key), production's release flow backs up the database before it migrates, and anything the templates can't express is listed in `docs/northflank-dashboard-steps.md`
- Test data: none
- Side effects: deploy (pull-request copies), migration (pull-request copies, staging)
- Parkable: no
- Size: M
- Stop if: Northflank can't keep the AI key out of the pull-request copies, or the staging token can reach production; list it as a dashboard step and ask on the control issue


### F-49: Jobs started over the web
- Phase: 1
- Goal: The harness starts work on a deployed copy over HTTPS, never through the host's command line. Main example: `POST /api/ops/jobs` with the ops key and kind `noop` answers 202, and the job's state reads `done`. Failure example: without the ops key, 401; a trial job on a pull-request copy is refused. It creates: `opsRouter(deps)` in `src/api/ops.ts`, serving `POST /api/ops/jobs`, `GET /api/ops/jobs/{id}` and `GET /api/ops/spend`; `loadJobKinds()` and the type `JobKind = { kind; environments; run(ctx, params): Promise<report> }` in `src/jobs/index.ts`; the `noop` kind; and `npm run record-ops -- F-NN --kind <kind>`.
- Covers: RUN-11
- Defers: none (each job kind arrives with its own card)
- Depends on: F-04, F-36
- Owner input: none
- Owns: `src/api/ops.ts`, `src/jobs/index.ts` (loads every file in `src/jobs/`), `src/jobs/noop.ts`, `src/web.ts` and `src/worker.ts` (to mount the routes and load the jobs), `scripts/record-ops.ts` and `package.json` (its `record-ops` script)
- Reads: `brain/spec/requirements.md` RUN-04, RUN-10, RUN-11; `brain/spec/architecture.md` (Modules, Secrets, Environments)
- Checks:
  - blocking: F-49 `POST /api/ops/jobs` without the ops key answers 401, and with a wrong one 401
  - blocking: F-49 a `noop` job answers 202 with an id; `GET /api/ops/jobs/{id}` shows it `queued`, then `done` with its report
  - blocking: F-49 an unknown kind answers 422, naming it
  - blocking: F-49 each environment's rules hold, with stand-in kinds: `trial` and `trial_examples` are refused outside staging, and `seed_fixtures` in production
  - blocking: F-49 `GET /api/ops/spend` sums fixture spend by environment, budget and cap
  - blocking: F-49 a new file in `src/jobs/` is picked up without editing any other file
  - blocking: F-49 `npm run record-ops -- F-NN --kind <kind>` fetches the latest finished job of that kind from the address and ops key it's given, and saves its report in `test/fixtures/fNN/`
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

### F-02 · Authors list reader and row checks
- **Phase:** 2
- **Goal:** Read library-pipeline's `authors.csv`, keep the active rows, read their dates, and report bad rows by name while the rest load.
- **Covers:** IN-01, IN-02, IN-03, IN-05, AC-01 (part), D-60
- **Depends on:** F-01
- **Owner input:** none
- **Build:** `src/teachers/authors.ts`
- **Checks:**
  - A fixture copied from the real header, with 12 rows (active, proposed, excluded; dates `1854-1948`, `d. 1925`, `b. 1870`, blank and unreadable), yields exactly the active rows. Aliases are split on `;`.
  - Each reason (missing name, unreadable date, death before birth, a lifespan over 120 years, a future year, a malformed `wikidata_qid` or `lcnaf_id`) is reported with its row number, and the other rows load.
  - **The optional columns (D-60):** a file without `wikidata_qid` and `lcnaf_id` reads as before; with them, the ids are read (`ids_from = list`). A good id passes `^Q[1-9][0-9]*$` or `^n[a-z]?[0-9]+$`.
  - `key_works` is split into titles, without their bracketed years and edition notes.
  - Whole-file refusals (not UTF-8, no header, missing `name`, `status` or `dates`, no active rows) stop the read before any client is called.
  - Changing a row's stream or tier changes only `notes`.
- **Test data:** about eight small CSV fixtures.
- **Live calls:** none
- **Parkable:** no
- **Size:** S

### F-06 · Outbound client
- **Phase:** 2
- **Goal:** One HTTP client for every outbound call, with an allowlist, an identifying User-Agent, per-source pacing, retries, a cache, and record and replay for tests.
- **Covers:** SRC-01, SRC-09, SRC-10, RUN-06, AC-06
- **Depends on:** F-01, F-04, F-51
- **Owner input:** none (the User-Agent's contact comes from `USER_AGENT_CONTACT`, O-10; tests use a placeholder)
- **Build:** `src/net/client.ts`; `scripts/record.ts` and the `record` script: `npm run record -- F-NN` fetches what `test/fixtures/fNN/record.json` lists, through this client, and saves the responses beside it. The harness runs it once, with network, before a card's tests are locked.
- **Checks:**
  - A request to a host outside the allowlist fails before leaving the process. The allowlist is SRC-01's: `www.wikidata.org`, `commons.wikimedia.org`, `upload.wikimedia.org`, `www.loc.gov`, `loc.gov`, `tile.loc.gov`, `id.loc.gov`, `api.wellcomecollection.org`, `iiif.wellcomecollection.org`, `openrouter.ai`, `api.github.com` and the environment's bucket host.
  - **Redirects:** the client calls `fetch` with `redirect: "manual"`. A redirect to an allowed host is followed (up to 5); one to any other host is refused, naming it.
  - Every request carries the User-Agent from settings: name, version, contact.
  - **Pacing, on a fake clock:**
    - LoC calls are spaced evenly, one every 3 seconds, so 30 take at least 87 seconds;
    - Wikimedia and Wellcome calls never overlap.
  - **Retries:** a 429, a 503 and an HTML CAPTCHA page each back off and retry up to the limit; a 404 isn't retried.
  - A second identical GET within the cache's lifetime is served from the cache.
  - In replay mode, recorded responses are served with no network. A request with no recording fails clearly, naming the URL.
- **Test data:** a fake transport; a CAPTCHA page sample.
- **Live calls:** none
- **Parkable:** no
- **Size:** M

### F-08 · Wikidata: fetch, check, find ids
- **Phase:** 2
- **Goal:** Read a teacher's Wikidata item, check a given id, and find a missing one as SRC-06 allows.
- **Covers:** SRC-03 (R1), SRC-06 (a, b's Wikidata half), IN-04
- **Depends on:** F-06
- **Owner input:** none (its recording needs O-10)
- **Build:** `src/sources/wikidata.ts`
- **Checks:**
  - A good id returns its P18 file name, its birth and death years, its labels and aliases, and its LoC name id (P244) if present.
  - An id that isn't a human, or whose years disagree with the teacher's, is refused with the reason.
  - **Search** (SRC-06b, step 1), which works for teachers with no years:
    - it finds humans whose label or alias matches the teacher's name or an alias (normalised), and who have both a birth and a death year on Wikidata;
    - any years the teacher already has must match;
    - each person found is returned with their id, years, LoC name id (P244) and works (P800, and items whose author P50 is them, found with `haswbstatement:P50=<Q-id>` in Wikidata's own search on `www.wikidata.org`; never the query service);
    - none, or a year mismatch, returns nothing. Several people are all returned, for F-35 to separate.
- **Test data:** recorded responses for about six real teachers and the edge cases.
- **Live calls:** network (free; to record)
- **Parkable:** no
- **Size:** S

### F-31: Teacher sync through GitHub
- Phase: 2
- Goal: Sync the active authors from the private library-pipeline repo into the database, with stable teacher ids, as a job and by command. Main example: a recorded `authors.csv` syncs to the expected teachers, and a second sync changes nothing. Failure example: a broken file leaves the existing teachers exactly as they were. It creates: `syncTeachers(db, csvText, opts): Promise<SyncReport>` in `src/teachers/sync.ts`; `fetchAuthorsCsv(client, token): Promise<string>` in `src/teachers/github.ts`; the job kind `sync`; the command `portraits sync`.
- Covers: IN-01, IN-03, IN-04, IN-12
- Defers: AC-01 (the whole chain: F-26), RUN-08 (nightly, through the cron job: F-25)
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


### F-32 · Rights log
- **Phase:** 2
- **Goal:** One permanent row for every original considered, refusals included, with its evidence, verdict, match and credit, and a CSV export.
- **Covers:** SRC-12, SRC-08, D-14
- **Depends on:** F-04, F-07
- **Owner input:** none
- **Build:** `src/sources/rightsLog.ts`
- **Checks:**
  - Recording the same original twice keeps one row, keyed by source and source id (and SHA-256 once downloaded), and adds to its history.
  - A refused original keeps its reason, and a later run doesn't research it. A `held` one keeps its verdict and is listed for the owner (SRC-12).
  - A candidate missing its source, item link, licence or credit line is refused (SRC-08).
  - The CSV export has every SRC-08 and SRC-12 field, and the raw record is kept beside it.
- **Test data:** records from F-07's fixtures.
- **Live calls:** none
- **Parkable:** no
- **Size:** S

### F-09 · Commons: P18 and depicts
- **Phase:** 2
- **Goal:** Turn a teacher's P18 image and their depicts-tagged Commons files into candidates, with licence, author and credit.
- **Covers:** SRC-03 (R1, R2), SRC-08
- **Depends on:** F-07, F-08
- **Owner input:** none (its recording needs O-10)
- **Build:** `src/sources/commons.ts` (`imageinfo` with `extmetadata`; search with `haswbstatement:P180=<Q-id>` in the file namespace); `src/sources/registry.ts`, which loads every source in `src/sources/registered/` (the survey, F-38, and the gatherer, F-11, both use it); `src/sources/registered/commons.ts`.
- **Checks:**
  - **R1:** the P18 file becomes a candidate (`wikidata_p18`) with its licence, author, credit, size and file link.
  - **R2:** each depicts-tagged file becomes a candidate (`commons_p180`); a file that is only in the teacher's category doesn't (negative fixture).
  - Non-image files (PDF, DjVu, audio) are skipped.
  - For previews (PIP-21), a thumbnail link at the largest of Wikimedia's standard widths not over 1,600 px is recorded, beside the full file link and the full width and height from `imageinfo`.
  - A file with a refused licence becomes a refused row in the rights log, not a candidate.
- **Test data:** recorded responses for two teachers, one with several depicts files.
- **Live calls:** network (free; to record)
- **Parkable:** no
- **Size:** S

### F-10 · Library of Congress pictures
- **Phase:** 2
- **Goal:** Find Prints & Photographs records that name the teacher with matching dates or their LoC name id, and turn them into candidates.
- **Covers:** SRC-03 (R3), SRC-05, SRC-08, SRC-09 (pacing)
- **Depends on:** F-07, F-32
- **Owner input:** none (its recording needs O-10)
- **Build:** `src/sources/loc.ts` (loc.gov JSON, `fo=json`); `src/sources/registered/loc.ts`, which registers it with the gatherer (F-11).
- **Checks:**
  - **Matches:** a record whose name heading carries the teacher's LoC name id; a record with a heading like `Fillmore, Charles, 1854-1948` whose dates match.
  - **No match:** a near miss (same name, different dates); an undated heading; a name in the title only.
  - The rights advisory is classified by F-07. "Rights status not evaluated" is refused.
  - The largest available image link is chosen, and its pixel size is recorded (from the IIIF `info.json` when the record doesn't give it). An IIIF link at most 1,600 px (`full/!1600,1600/0/default.jpg`) is recorded for previews (PIP-21).
  - Requests are paced to 20 a minute (through F-06).
- **Test data:** recorded responses for three teachers, plus near-miss and undated records.
- **Live calls:** network (free; to record)
- **Parkable:** yes (the gatherer then runs without the LoC: no card lists F-10 as a dependency)
- **Size:** M

### F-34 · Wellcome Collection
- **Phase:** 2
- **Goal:** Find Wellcome picture records whose contributor or subject is the teacher, by LoC name id or name and dates, with clean licences.
- **Covers:** SRC-03 (R3), SRC-05, SRC-08
- **Depends on:** F-07, F-32
- **Owner input:** none (its recording needs O-10)
- **Build:** `src/sources/wellcome.ts` (catalogue API, no key; images through IIIF); `src/sources/registered/wellcome.ts`, which registers it with the gatherer (F-11).
- **Checks:**
  - A record whose contributor or subject carries the teacher's LoC name id matches. So does one with the name and matching dates.
  - Licences map through F-07: PDM and CC0 → tier 1; CC BY → tier 2; CC BY-NC → refused.
  - The IIIF image links for the full size and for a preview at most 1,600 px (`/full/!1600,1600/0/default.jpg`) are recorded, with the full width and height from `info.json`.
- **Test data:** recorded responses for two teachers (one mind-cure figure).
- **Live calls:** network (free; to record)
- **Parkable:** yes
- **Size:** S

### F-35 · Finding missing dates and ids
- **Phase:** 2
- **Goal:** Fill a teacher's missing Wikidata id, LoC name id and dates only when Wikidata and the LoC name authority agree; list everything else for the owner.
- **Covers:** IN-13, SRC-06 (b, c), IN-04
- **Depends on:** F-08, F-31
- **Owner input:** none (its recording needs O-10)
- **Build:** `src/teachers/enrich.ts`; `src/sources/locNames.ts` (id.loc.gov).
- **Checks:**
  - **An undated teacher** whose one Wikidata person links (P244) to a LoC name record with the same life dates → the ids and dates are stored and marked `resolved_by_tool`.
  - **Two people share the name** (the theologian and the linguist Charles J. Fillmore, say): the teacher's `key_works` pick out exactly one, by a work title → accepted; if they pick out none or both → nothing stored, listed.
  - Disagreement (P244 points elsewhere, or the years differ), or only one source with data → nothing stored; a suggestion with its evidence is listed.
  - The suggestions export as a CSV whose columns match `authors.csv` (name, aliases, dates, plus `wikidata_qid` and `lcnaf_id` and the evidence).
  - A teacher left with no id and no dates is marked skipped, with what to add.
- **Test data:** recorded Wikidata and id.loc.gov responses for agree (dated and undated), disagree, same-name and one-sided cases.
- **Live calls:** network (free; to record)
- **Parkable:** yes (teachers without ids then stay skipped until the owner adds them)
- **Size:** M

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

### F-39 · Porting spike: OpenCV.js and sharp
- **Phase:** 3
- **Goal:** Prove that every image operation the recipe needs works in TypeScript, choose the fallback for any gap, and give the imaging cards a safe way to use OpenCV.js.
- **Covers:** architecture.md ("Porting risks" and "Porting traps"); groundwork for STY-01..STY-09, PIP-04, PIP-05, PIP-13, PIP-20, PIP-23
- **Depends on:** F-01, F-51
- **Owner input:** none
- **Build:**
  - `src/imaging/cv.ts`: load OpenCV.js once, and a `withMats(fn)` helper that frees every Mat made inside;
  - `src/imaging/io.ts` (`sharp`: decode, colour to sRGB, RGBA PNG out);
  - the reference results already committed in `prototype/parity/` (made by `prototype/export_parity.py` in Phase 0; `index.json` lists each file, its exact call and its tolerance), copied by the test author to `test/fixtures/f39/`;
  - the YuNet model already committed in `models/` (with its source and licence);
  - `docs/porting.md`: each operation, what was used, and any fallback.
- **Checks:**
  - **Each operation runs and matches the Python reference within a set tolerance on the fixtures:**
    - bilateral filter;
    - forward and inverse DFT;
    - Gaussian blur;
    - `warpAffine`;
    - `findTransformECC` with all seven arguments;
    - Farneback optical flow;
    - distance transform;
    - connected components;
    - SIFT with RANSAC (`estimateAffinePartial2D`);
    - YuNet face detection.
  - **The known traps** (architecture.md, "Porting traps") each have a test:
    - the 15 × 15 median on the float spectrum matches `scipy.ndimage.median_filter` within one 12-bit step (a typed-array median, exact or with a 12-bit sliding histogram; OpenCV's 8-bit `medianBlur` isn't precise enough), with the border reflected as scipy does;
    - with that median, `detect_screen` finds exactly the prototype's peaks on all three originals (`results.json`, `detect_screen`);
    - the 5 × 5 maximum is `cv.dilate` and matches `maximum_filter`;
    - `cv.idft` with `DFT_SCALE | DFT_REAL_OUTPUT` round-trips an image;
    - YuNet's boxes come back as `[x0, y0, x1, y1]`.
  - Each missing operation's fallback from architecture.md is implemented and passes the same check instead, and `docs/porting.md` says which. The fallbacks are AKAZE or ORB, `onnxruntime-node`, and block matching.
  - Running the whole set 50 times leaves memory flat within 10% (no Mat leaks).
  - `sharp` reads JPEG, PNG (with alpha), TIFF and WebP fixtures, and writes 8-bit RGBA PNG. An alpha channel survives a round trip.
- **Test data:** two fixture images and the Python reference outputs.
- **Live calls:** none
- **Parkable:** no (everything in phase 3 needs it)
- **Size:** M

### F-12 · Face landmarks and crop
- **Phase:** 3
- **Goal:** Find the face box and five landmarks with YuNet, and crop to the square of STY-03 by a similarity transform.
- **Covers:** PIP-04, PIP-23 (the working region), STY-03
- **Depends on:** F-39
- **Owner input:** none
- **Build:** `src/imaging/face.ts` (YuNet ONNX from `models/`; an original over 640 px is searched on a copy reduced to 640 px, with coordinates scaled back); `src/imaging/crop.ts`, including the working region for originals over `maxWorkingPx` (the crop's square plus 25% a side, reduced by area averaging to at most `maxWorkingPx`)
- **Checks:**
  - On the owner's three originals (`prototype/parity/inputs/`), the box and landmarks match YuNet's in Python (`prototype/parity/results.json`, `yunet`) within 1 px, and the score within 0.01. The fixtures (`prototype/fixtures/*.json`) hold the same YuNet results since recipe 0.5.0.
  - The crop puts the eye line at 0.449 of the side and the eye-to-mouth distance at 0.221 of the side, with the face centred, each within 1%.
  - YuNet's `[x, y, w, h]` boxes are turned into `[x0, y0, x1, y1]` (a test with a known box).
  - **With no face found** (synthetic case), the five landmarks come from the pre-check's box by PIP-04's proportions (eyes at ±0.22 w and 0.39 h, nose at 0.58 h, mouth corners at ±0.19 w and 0.74 h). They match `results.json`'s `landmarks_from_box`. On the three originals, a crop made that way from the YuNet box puts the eye line within 0.03 of the side of the real crop's, at a scale within 10%.
  - A face narrower than `minFacePx` is reported as too small.
  - The working region of a 4,000 × 5,000 synthetic original is at most 2,000 px on its long side and contains the whole crop square. An original of 2,000 px or less is used whole.
- **Test data:** the three originals; the prototype's fixtures; a synthetic image with no face.
- **Live calls:** none
- **Parkable:** no
- **Size:** M

### F-13 · Descreen and edge-preserving blur
- **Phase:** 3
- **Goal:** Detect a printed dot pattern by frequency analysis, notch it out, and give every original an edge-preserving blur sized in dot cells.
- **Covers:** PIP-05, PIP-23
- **Depends on:** F-12
- **Owner input:** none
- **Build:** `src/imaging/descreen.ts` (port of `descreen` and `detect_screen` in `prototype/recipe.py`), on F-12's working region.
- **Checks:**
  - The owner's Fillmore and Cady originals are detected as screened, and Holmes isn't (the prototype's result).
  - A synthetic screened image has its screen peaks reduced by at least the factor the prototype achieves.
  - A clean image gets only the mild blur. Its output differs from the input by no more than the prototype's on the same image.
  - What was found and applied is returned for the record.
  - A 4,000 × 5,000 synthetic screened original finishes in under 60 seconds, and the process stays under 1.5 GB (the worker's memory), because only the working region is processed.
- **Test data:** the three originals; a synthetic screen; the large synthetic original (generated in the test, not committed).
- **Live calls:** none
- **Parkable:** no
- **Size:** M

### F-14 · Tone and halftone
- **Phase:** 3
- **Goal:** Turn the cropped tones into coverage (levels from the face, gamma, unsharp mask) and screen them as round white dots on a 45° grid, supersampled.
- **Covers:** STY-01, PIP-06
- **Depends on:** F-39
- **Owner input:** none
- **Build:** `src/imaging/tone.ts`, `src/imaging/halftone.ts` (ports of `tone_to_coverage` and `_threshold_map`).
- **Checks:**
  - On a synthetic gradient, frequency analysis finds a pitch of 1000/110 px along a 45° grid, and dot area grows with brightness.
  - Dark tones are fully transparent; the brightest face tone is near full coverage.
  - The threshold map matches the prototype's exactly for the same size and settings (it's pure arithmetic).
  - The map is built once per recipe, in one pass without full-size intermediate arrays, and reused: a second portrait doesn't rebuild it.
- **Test data:** synthetic gradients.
- **Live calls:** none
- **Parkable:** no
- **Size:** M

### F-15 · Mask, code outline, master and cut-out limits
- **Phase:** 3
- **Goal:** Smooth the figure mask (head and shoulders differently), draw the code outline, composite the white master, check it, and refuse figures that break the cut-out limits.
- **Covers:** STY-02, STY-06, PIP-07, PIP-08, PIP-19
- **Depends on:** F-12, F-14
- **Owner input:** none
- **Build:** `src/imaging/mask.ts`, `outline.ts`, `checks.ts` (the STY-06 checker and PIP-19's limits), `compose.ts`
- **Checks:**
  - The line is one connected piece, 6 ± 1 px wide, starting 2 ± 1 px outside the figure. Where the shoulders leave the square, it runs off the bottom.
  - The master passes STY-06: every visible pixel is pure white; the corners and the outside are transparent.
  - The three examples pass PIP-19's limits. Fixtures with a floating fragment, a figure cut off above the shoulders, and a full square are each refused, naming the limit.
  - The 98% piece share is measured on the raw cut-out before smoothing. Smoothing still keeps only the largest piece, as the prototype does, and the fragment fixture is refused all the same.
- **Test data:** the prototype's cut-out fixtures; synthetic bad masks.
- **Live calls:** none
- **Parkable:** no
- **Size:** M

### F-30 · AI copy: key mask, alignment, drift check, blend
- **Phase:** 3
- **Goal:** Take an AI copy on flat green, read the cut-out from its green, align it to the original, refuse it if details moved, and blend it at 50% in the portrait's frame.
- **Covers:** PIP-13 (code side), PIP-03 (key mask, mask.png), OUT-11 (mask), STY-04
- **Depends on:** F-12, F-13
- **Owner input:** none
- **Build:** `src/imaging/align.ts`, `blend.ts` (ports of `key_mask`, `align_enhanced`, `local_drift` and the blend in `make_master`).
- **Checks:**
  - **Alignment:** synthetic keyed copies (2.8× larger, sharpened, rescaled by 2%, shifted, on green) align with correlation ≥ 0.99.
  - **Blend:** it shows no double edges (edge agreement ≥ 0.98), and the blend share is exactly `enhanceBlend`.
  - **Key mask:** the mask from the green matches the prototype's cut-out fixture with overlap ≥ 0.94.
  - **Drift check:** measured inside the face box shrunk by `driftBoxInset` (0.15) on each side. Copies with the eyes and mouth moved by about 1.2 dot cells measure above 0.7 and are refused; good copies measure below. Both are within 0.1 of the prototype's figures (`prototype/out/enhance-mechanics.json`: good 0.14–0.31, moved 0.95–1.08).
  - **Poor alignment:** a copy that can't be aligned (a different face) is refused, and the original is used alone.
  - **The mask is mapped back:** the key mask is warped through the inverse of the alignment onto the original's own size and position, composed with the working region's offset and scale for a large original (PIP-23). On a synthetic copy, small and large (4,000 × 5,000), the mapped mask overlaps the true figure in the original by at least 0.97. It's the same for a `cutout_keyed` image.
- **Test data:** the generator from `prototype/test_enhance_mechanics.py`, ported.
- **Live calls:** none
- **Parkable:** no (the cut-out depends on it)
- **Size:** M

### F-41 · Black-and-white, 500 px and viewing copies
- **Phase:** 3
- **Goal:** Make the black-and-white version (option C) and the 500 px copies from the master's layers, and the original's PNG viewing copy.
- **Covers:** STY-08, STY-09, OUT-05, PIP-22
- **Depends on:** F-15
- **Owner input:** none
- **Build:** `src/imaging/versions.ts` (ports of `bw_version`, `small` and `check_bw`); `src/imaging/modelImage.ts`, which makes the images sent to models (PIP-22).
- **Checks:**
  - `bw-1000` passes `check_bw`: visible pixels are grey; the corners are transparent; it's opaque wherever the master shows.
  - Both 500 px copies pass their checkers.
  - The viewing copy:
    - is a PNG at most 1,600 px on the long side;
    - is never enlarged (a 300 px original stays 300 px);
    - keeps transparency from a PNG original.
  - **Model images (PIP-22):** a 16-bit TIFF and a CMYK JPEG each become 8-bit sRGB PNG, at most `maxModelImagePx` on the long side and under 5 MB.
- **Test data:** the prototype's layers via the three examples; a transparent PNG; a 16-bit TIFF and a CMYK JPEG.
- **Live calls:** none
- **Parkable:** no
- **Size:** S

### F-42 · Same photograph or different (code layers)
- **Phase:** 3
- **Goal:** Tell copies of one photograph from different photographs with a whole-picture fingerprint and feature matching, leaving the unclear middle for the model (F-43).
- **Covers:** PIP-20 (layers 1 and 2), PIP-15
- **Depends on:** F-12
- **Owner input:** none
- **Build:** `src/imaging/samePhoto.ts` (a port of `prototype/same_photo.py`, plus a 64-bit difference hash of the whole picture; feature points computed once per picture and kept).
- **Checks:**
  - The prototype's 30 doctored copies are judged the same. These are crop, rescale, rotation, JPEG, blur, reprint screen, mirror and noise, generated as in `same_photo.py`. Their inlier counts are within 25% of `prototype/out/same-photo.json`.
  - The different-photograph pairs score at or below `diffMaxInliers`.
  - Exact duplicates and resized or re-encoded copies are caught by the fingerprint alone (at most 2 bits different). Two different frontal sittings are never "same" by fingerprint.
  - A new candidate is compared with one representative per photograph group, and each picture's feature points are computed once (a counter in the test).
  - A pair between the thresholds is returned as "unclear", for F-43.
  - *(report)* If F-39 chose a fallback detector (AKAZE or ORB), `sameMinInliers` and `diffMaxInliers` are measured again on the same fixtures, for a recipe change the Tech Lead rules on. The survey's real pairs are checked in the trial (F-52).
- **Test data:** the three originals and the generator.
- **Live calls:** none
- **Parkable:** no
- **Size:** M

### F-16 · Parity with the Python prototype
- **Phase:** 3
- **Goal:** Lock the TypeScript recipe to the Python reference: from the prototype's fixtures, it must reproduce the prototype's outputs within tolerance. Prove it. This is Phase 3's gate card; the verifier adds its tests here.
- **Covers:** STY-07; AC-04 (groundwork)
- **Depends on:** F-13, F-15, F-30, F-41, F-42
- **Owner input:** none
- **Build:** nothing new (prove it). The test author copies the reference outputs from `prototype/out/`, and a frozen copy of the recipe 0.5.0 settings, into `test/fixtures/f16/`.
- **Checks:**
  - For each of the three examples, at the automatic crop and at the owner's framing, against the prototype's `white-1000`:
    - figure overlap ≥ 0.98;
    - mean alpha difference ≤ 0.02;
    - dots across 110 ± 1.
  - The same for `bw-1000`, and for both 500 px copies.
  - The test runs with the frozen copy of the recipe 0.5.0 settings (in `test/fixtures/f16/`), not the live settings, so a later recipe version from the trial doesn't break it.
  - The landmarks are the fixtures' own (given, not detected), so a detector difference can't move the crop.
- **Test data:** `prototype/fixtures/`, `prototype/out/`.
- **Live calls:** none
- **Parkable:** no (a failure stops the build, with the measures on the control issue)
- **Size:** S

---

## Phase 4: Model steps

### F-17 · OpenRouter client, spend ledger and caps
- **Phase:** 4
- **Goal:** One client for every model call through OpenRouter, with a stub mode, a spend ledger and every cap enforced before each call.
- **Covers:** RUN-04, RUN-06, RUN-10 (environment caps), D-19, D-54, PIP-09 (family rule at call time)
- **Depends on:** F-04, F-06
- **Owner input:** none
- **Build:** `src/models/openrouter.ts`
- **Checks:**
  - **Stub mode:** canned answers come back with no key and no network.
  - **Caps,** each crossed mid-run with stubbed costs, stop the next call before it is made, and the stop is reported cleanly:
    - the first pass's $100 total (no night cap during it);
    - after it, the night ($10) and month ($30) caps;
    - $2 per teacher per run;
    - the trial's sub-budgets ($27 and $3);
    - staging's $2 a night and $10 a month.
  - In a pull-request environment, every paid call is refused (stub mode only).
  - The environment's rules are chosen from `PORTRAITS_ENV` through settings.
  - Every request asks for usage (`"usage": {"include": true}`). Each call's cost is logged with run, teacher, step, model, environment, budget, and whether it is actual or estimated.
  - The month cap sums only `regular` spend; the trial's spend never counts toward it.
  - A model whose family equals the enhance model's is refused for checking.
  - Model ids and prices come from settings. An unknown model id is refused before any call.
- **Test data:** canned OpenRouter answers, including usage and cost fields.
- **Live calls:** none
- **Parkable:** no
- **Size:** M

### F-18 · Pre-check
- **Phase:** 4
- **Goal:** Ask Claude Haiku whether an original can be used, and record its structured verdict.
- **Covers:** PIP-02, PIP-18 (age estimate), PIP-22, D-47 (medium), D-52
- **Depends on:** F-17, F-41
- **Owner input:** none
- **Build:** `src/models/precheck.ts`; `src/models/prompts/precheck.md` (from `prototype/prompts/`, v2)
- **Checks:**
  - Canned verdicts drive pass and fail. A fail sets the original aside with its reasons, and no further call is made for it.
  - The face box, medium, age estimate, dot pattern and caption are parsed. Malformed JSON is retried once, then counted as a failure with the raw text kept.
  - The face box comes back as fractions and is turned into the original's pixels with the width and height the source gave; a face under `minFacePx` wide fails in code, whatever the model said. With no size from the source, the check is repeated on the downloaded original before the enhance call.
  - The request carries the copy's preview, re-encoded as an 8-bit PNG at most 1,600 px; never a TIFF, never the full original.
  - A caption naming someone else fails.
  - `allowedMedia` excludes engravings when set.
  - The answer is cached per original (a second check makes no call).
- **Test data:** canned verdicts for each case.
- **Live calls:** none
- **Parkable:** no
- **Size:** S

### F-19 · AI copy and keyed cut-out calls
- **Phase:** 4
- **Goal:** Ask the image model for the enhanced copy on green (and the cut-out-only fallback), cache it, and keep it with its record.
- **Covers:** PIP-13 (calls and records), PIP-03 (fallback), PIP-10 (fresh copy on a remake), PIP-22, D-52, D-56
- **Depends on:** F-17, F-30, F-41
- **Owner input:** none
- **Build:** `src/models/enhance.ts`, `cutout.ts`; prompts `enhance_keyed.md`, `cutout_keyed.md`
- **Checks:**
  - A canned image answer becomes `enhanced.png`, with the model, prompt version, alignment and drift scores and whether it was used.
  - A second try on the same original makes no call; a remake (PIP-10) makes exactly one new call.
  - **One `cutout_keyed` call** is made when the enhance call errors, when its copy is refused by its safeguards, or when its mask fails PIP-19. Its image is aligned like the AI copy, and its mask becomes `mask.png`.
  - If the fallback errors, can't be aligned or fails PIP-19, the draft fails for its cut-out (PIP-03), and no further call is made for that attempt.
  - The enhance and cut-out requests carry the descreened working region as a PNG at most 1,600 px, never the original file.
  - A `try_again` note is added to the enhance prompt, and recorded.
- **Test data:** synthetic keyed images as canned answers (from F-30's generator).
- **Live calls:** none
- **Parkable:** no
- **Size:** M

### F-21 · Draft check and compare-with-target
- **Phase:** 4
- **Goal:** Ask Claude Sonnet to judge a draft on five criteria against the original, and score a draft against a hand-made target.
- **Covers:** PIP-09, PIP-22, TRI-08 (mode), D-52
- **Depends on:** F-17, F-15, F-41
- **Owner input:** none
- **Build:** `src/models/draftCheck.ts`; prompts `draftcheck.md`, `compare.md`
- **Checks:**
  - The request carries, in this order: the original's viewing copy, the draft on `checkPageRgb`, then the three examples on the same colour (as `draftcheck.md` says). Every image is an 8-bit PNG at most 1,600 px and under 5 MB; none is a TIFF.
  - Canned answers pass only when all five criteria pass. The scores and notes are recorded.
  - A `try_again` note becomes an extra criterion.
  - The compare mode returns a score per criterion against the target.
  - Malformed answers are retried once.
- **Test data:** canned answers.
- **Live calls:** none
- **Parkable:** no
- **Size:** S

### F-43 · Same-photograph tie-break
- **Phase:** 4
- **Goal:** For pairs F-42 finds unclear, ask Claude Sonnet whether they are the same photograph, treating "unsure" as the same.
- **Covers:** PIP-20 (layers 3 and 4), PIP-22, D-50
- **Depends on:** F-17, F-41, F-42
- **Owner input:** none
- **Build:** `src/models/samePhotoCheck.ts`; prompt `same_photo.md`
- **Checks:**
  - "same" groups the pair; "different" separates it; "unsure" groups it (D-50).
  - The evidence is recorded with the pair.
  - A pair is never asked twice (cached by both SHA-256s, in either order).
  - Both images are the candidates' previews, reduced to 800 px and sent as 8-bit PNGs; never a TIFF.
- **Test data:** canned answers.
- **Live calls:** none
- **Parkable:** no
- **Size:** S

### F-11 · Candidates: gather, previews, group, order
- **Phase:** 4
- **Goal:** Gather a teacher's candidates from every adopted source, drop refused licences, fetch small previews, group copies of one photograph and order the copies (PIP-21, steps 1–3), and provide the full download that F-23 calls for the photographs it chooses.
- **Covers:** PIP-21 (steps 1–3, and the download of step 6), SRC-07, SRC-08, PIP-15, PIP-01 (part), OUT-12 (originals), IN-05
- **Depends on:** F-09, F-32, F-37, F-42, F-43
- **Owner input:** none
- **Build:** `src/sources/candidates.ts`. The gatherer uses F-09's registry of `src/sources/registered/`, so the LoC and Wellcome join when their cards are merged, and nothing waits if one is parked. Tests use fakes for any source not registered.
- **Checks:**
  - A fixture teacher with candidates from three sources (one refused licence, one exact duplicate, two copies of one photograph, one different photograph) gives:
    - two photographs;
    - the refused one logged;
    - the duplicate merged;
    - the copies of each photograph in SRC-07's order (licence tier, then size; damage once pre-checked).
  - **Previews:** at most `maxCandidatesPerTeacher` previews are fetched, at most 1,600 px, from each source's sized-image link. They're kept only in memory or temporary files, never in the bucket. No full original is fetched by this step.
  - **The download** (called by F-23 for chosen copies only): checked against its SHA-256 on a second fetch, and stored as `original.<ext>`.
  - Set-aside photographs are excluded.
  - The best-known flag is set on the P18 photograph and its copies.
  - Changing a teacher's notes changes none of their candidates (IN-05).
- **Test data:** recorded responses; small image fixtures, including doctored copies.
- **Live calls:** none
- **Parkable:** no
- **Size:** M

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

### F-24 · Publishing a portrait
- **Phase:** 5
- **Goal:** Write a portrait's files (OUT-11) and its record atomically, with each file's licence and credit, and add it to the change feed.
- **Covers:** OUT-02, OUT-03, OUT-04, OUT-11, OUT-12, SRC-11, AC-02
- **Depends on:** F-03, F-04, F-07, F-37, F-41
- **Owner input:** none
- **Build:** `src/pipeline/portrait.ts`
- **Checks:**
  - A fixture portrait produces all eight files under its key, each passing its checker, plus `record.json`. The record validates against the contract's `Portrait`.
  - A fixture whose enhance call failed produces the other seven, with `enhanced_used` false.
  - Each file's licence and credit follow SRC-11's table, for a public-domain, a CC BY and a CC BY-SA fixture.
  - Stopping the work after the files but before the database commit leaves no visible portrait, and no change-feed entry.
  - A record missing a licence isn't published. The failure names the field, the portrait is `failed`, and its candidate is set aside, so a second run doesn't try it again (OUT-04).
  - Portrait ids count up per teacher, and are never reused after a turn-down.
- **Test data:** images from phase 3; F-07's fixtures.
- **Live calls:** none
- **Parkable:** no
- **Size:** M

### F-23: Per-teacher pipeline and failure policy
- Phase: 5
- Goal: Take one teacher from candidates to published portraits: open slots, the choice of photographs, pre-check, AI copy, draft, check, remake and set-asides, all with stubs. Main example: a teacher with five different photographs gets three portraits, the best-known one first, then spread across their life. Failure example: a draft failing twice sets its original aside, and the next photograph is tried. It creates: `processTeacher(ctx, teacherId): Promise<TeacherRunResult>` in `src/pipeline/teacher.ts`; `choosePhotographs(photographs, openSlots, teacher): Photograph[]` in `src/pipeline/choose.ts`; `recordFailure(...)` and `isSetAside(...)` in `src/pipeline/failures.ts`. The contract step settles their exact types.
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
- Test data: a stub world for three teachers in `test/fixtures/f23/` (recorded source responses, canned model answers and images), served through the product's own replay client (F-06) and stub model client (F-17); F-25, F-26 and F-48 reuse it
- Side effects: none
- Parkable: no
- Size: L
- Stop if: a check needs a model answer the stub world can't give: ask for the fixture rather than fake it in the product code


### F-25 · Queue, schedule and run reports
- **Phase:** 5
- **Goal:** Run the nightly schedule and the queue: sync, queue teachers with open slots not searched for a month, take requests first, resume after a crash, stop at a cap, and write each run's report.
- **Covers:** RUN-02, RUN-03, RUN-04 (stop, report and the first pass), RUN-08, OUT-06
- **Depends on:** F-23, F-31, F-36
- **Owner input:** none
- **Build:** `src/cron.ts`, `src/worker.ts`; `src/pipeline/run.ts`; `src/jobs/run.ts`; `src/cli/commands/run.ts`
- **Checks (fake clock):**
  - **Queueing (RUN-02, RUN-08):**
    - a teacher searched 10 days ago isn't queued; one searched 35 days ago is;
    - a full teacher is queued monthly (D-59), and only new candidates are looked at; with `researchFullTeachers` off, it isn't;
    - a request goes ahead of queued teachers;
    - outside production, the cron job queues nothing.
  - The cron job exits after queueing.
  - Killing the worker mid-teacher and restarting it resumes with no repeated paid call (stub call counts).
  - Reaching a cap stops the run cleanly. Finished portraits stay published, and the report says so.
  - **The first pass (RUN-04):** while `first_pass_state` is `active`, spend is booked to `first_pass` and the night cap doesn't apply. It becomes `done` when the queue first empties, or when `first_pass` spend reaches $100; from then on, spend is `regular` and the night and month caps apply.
  - A snapshot test of the fixture run's report covers every field of OUT-06.
- **Test data:** F-23's stub world.
- **Live calls:** none
- **Parkable:** no
- **Size:** M

### F-44 · API: reads, change feed, files, keys
- **Phase:** 5
- **Goal:** Serve the read side of the contract (teachers, portraits, history, files and the change feed) behind the library's key, with rate limits.
- **Covers:** OUT-14, SCOPE-02, RUN-10 (key, rate limit, signed links)
- **Depends on:** F-03, F-24, F-49
- **Owner input:** none
- **Build:** `src/api/` (Express routes, key middleware, change feed with cursors); `keys new|off|list`
- **Checks:**
  - Every read route's answers validate against the contract (F-03's helper), on a fixture database.
  - **Keys:** no key gives 401 `key_off`; a switched-off key gives 401; a good key gives 200. Keys are stored as hashes only, and a new key is shown once.
  - **Change feed:**
    - `since` then `after` pages through every change in order;
    - `more` and `next_cursor` behave as the contract says;
    - with `after`, the answer's `since` is the time of the cursor's entry (the service's start for `c_0`);
    - an empty page echoes the cursor it was given as `next_cursor`, with `more: false`. With `since` and nothing after it, `next_cursor` is the cursor of the last change at or before `since` (`c_0` when there's none), so the next call doesn't replay older changes;
    - neither `since` nor `after`, or both, gives 422 `invalid`;
    - a cursor older than 30 days gives 410 `cursor_too_old`.
  - `/files/{kind}` redirects to a signed link that expires in 15 minutes.
  - Portraits being made or failed never appear.
  - Calls over the rate limit get 429 with `Retry-After`.
- **Test data:** a fixture database with teachers and portraits in every status.
- **Live calls:** none
- **Parkable:** no
- **Size:** M

### F-45 · API: decisions and requests
- **Phase:** 5
- **Goal:** Accept the library's decisions and requests, apply them once, and queue requests at once.
- **Covers:** IN-06, IN-07, IN-08, SRC-04, D-61
- **Depends on:** F-44, F-25
- **Owner input:** none
- **Build:** `src/api/decisions.ts`, `requests.ts` (the web side: validate, store, queue, answer 202); `src/pipeline/requests.ts` (the worker side: classify the note, do the work, finish the request); `src/models/noteKind.ts` with prompt `note_kind.md` v2
- **Checks:**
  - **Decisions:**
    - approve, turn_down (each reason), set_main and correct change the portrait as IN-07 says, and appear in its history and the change feed;
    - approving a portrait with `replaces` makes the old one `replaced`, with `replaced_by` set;
    - **main portrait:** when the replaced portrait was the main one, `main` passes to the new one; turning down the main portrait clears `main`, and the teacher has none.
  - **Bad decisions:** a turn-down without a reason is refused with `invalid` naming `/reason`; set_main on a waiting portrait gives `conflict`.
  - **Resending:** the same `decision_id` or `request_id` changes nothing and says it's a duplicate. Reusing an id with different content gives `conflict`.
  - **Requests:**
    - a `try_link` to an adopted source is queued. Each link form in SRC-04 is read without fetching the page (`commons.wikimedia.org/wiki/File:…`, `upload.wikimedia.org/…` including a thumbnail link, `(www.)loc.gov/item/…`, `(www.)loc.gov/pictures/item/…`, `(www.)loc.gov/resource/…`, `wellcomecollection.org/works/…`, `api.wellcomecollection.org/catalogue/v2/works/…`);
    - a link elsewhere is refused with the reason;
    - a `try_again` whose note Claude Haiku (stubbed, prompt `note_kind.md`) judges to be about the crop or the outline is answered `refused`, suggesting `another_original`; a restoration note is passed on. "The line cuts off the left ear" counts as restoration;
    - `another_original` makes the portrait `turned_down` (reason `other`) and queues the teacher;
    - an unknown teacher or portrait gets 404; a link outside the adopted sources gets 422; a `try_again` or `another_original` on a turned-down or replaced portrait gets 409;
    - a `try_again` on a waiting portrait replaces it when done; on an approved portrait, the new draft is offered with `replaces`, and the approved one (and `main`) stays until the library approves it;
  - **Life cycle (IN-06):** the web answer is 202 with `queued`. The worker sets `working`, then either `done` with `result_portrait_id` (always a new portrait id), or `refused` with a `refused_reason` code and no result. Each code in IN-06 has a fixture. Each state change is in the change feed.
  - Every answer validates against the contract.
- **Test data:** the fixture database.
- **Live calls:** none
- **Parkable:** no
- **Size:** M

### F-48 · Later runs: better copies, turn-downs, corrections
- **Phase:** 5
- **Goal:** On later runs, offer clearly better copies, bring back a turned-down photograph only when allowed, and never overwrite the library's corrections.
- **Covers:** PIP-17, PIP-18 (corrections), OUT-07, D-59, D-61
- **Depends on:** F-23, F-45
- **Owner input:** none
- **Build:** additions to `src/pipeline/teacher.ts`
- **Checks:**
  - **Better copies:**
    - a 2× better copy of an approved portrait becomes a new waiting portrait with `replaces` set, and the approved one is untouched;
    - a better copy of a waiting portrait replaces it, and the old one becomes `replaced`, keeping its files.
  - **Turn-downs:**
    - turned down for `quality`, a 2× copy is offered once, and not a second time;
    - turned down as `not_this_teacher` or `do_not_use`, it never returns.
  - **Full slots (D-61, PIP-17):** with all slots full, PIP-16 is re-run over the three and a new photograph.
    - When the new one is chosen and the one left out is approved and not main, it's offered with `replaces` set to that one. Approving it makes that one `replaced`; turning it down leaves the three as they were, and it isn't offered again.
    - When the one left out is waiting, or the main portrait, nothing is offered. A photograph PIP-16 wouldn't choose isn't offered.
    - Only one such offer per teacher is open at a time.
  - **Slots:** an open offer doesn't take a slot of its own, so a teacher with three portraits and an offer gets no fourth draft (PIP-14).
  - **Corrections:** a library-corrected date and best-known flag survive a re-run.
- **Test data:** F-23's stub world over three runs.
- **Live calls:** none
- **Parkable:** no
- **Size:** M

### F-46 · Admin site
- **Phase:** 5
- **Goal:** A read-only, phone-friendly admin site behind one password. It shows teachers, portraits, runs, the rights log, the suggestions for `authors.csv` and the keys.
- **Covers:** OUT-13, OUT-06 (pages), RUN-09, RUN-10 (login), SRC-12 (CSV), IN-13 (suggestions CSV)
- **Depends on:** F-25, F-32, F-44
- **Owner input:** none
- **Build:** `src/admin/` (the frame, login and one stylesheet); one file per page in `src/admin/pages/`; `src/cli/commands/password.ts`. The suggestions page shows whatever F-35 has stored, or an empty state.
- **Checks:**
  - **Login:**
    - each page needs a login, and the password is stored in the database only as a slow hash;
    - a wrong password locks out after the set number of tries;
    - the session cookie is secure, HTTP-only and SameSite, and lasts 30 days.
  - **The front page** (D-68) shows last night's run, the month's spend against its cap (and the first pass's against $100 while it's active), errors since the last run, and what needs the owner: teachers to identify, held originals, bad rows in the authors list, anything stuck.
  - **Pages:** the teacher list, one teacher (all versions, rights, the library's decisions), the runs and one run's report all render from the fixture database.
  - Every portrait is shown on the dark page colour (`checkPageRgb`), never on white.
  - `/admin/trial` shows "No trial run yet" until F-28 fills it.
  - Held originals (CC BY-SA 1.0) are listed for the owner, with their source and licence (SRC-02, SRC-12).
  - The rights-log CSV and the suggestions CSV download with the right columns.
  - No page has a form that changes data, except logging in and out.
  - Every page renders at 390 px wide without horizontal scrolling (a layout test).
  - No key or secret appears on any page.
  - A dependency check finds no mail-sending package and no SMTP code (RUN-09).
- **Test data:** the fixture database.
- **Live calls:** none
- **Parkable:** no
- **Size:** M

### F-22 · Commands and `doctor`
- **Phase:** 5
- **Goal:** Finish the command-line tool for the harness and the owner, with a `doctor` that checks everything a run needs, without spending.
- **Covers:** RUN-05
- **Depends on:** F-17, F-25, F-44
- **Owner input:** none
- **Build:** `src/cli.ts`
- **Checks:**
  - `doctor` reports settings, each secret's presence (never its value), the models and their prices from settings, and each source's reachability (replayed). It exits non-zero on a problem and spends nothing.
  - `run --dry-run` shows the plan and the estimated spend, and queues nothing.
  - `status`, `keys` and `password` work against PGlite.
- **Test data:** the fixture database.
- **Live calls:** none
- **Parkable:** yes
- **Size:** S

### F-05 · Library stub
- **Phase:** 5
- **Goal:** A small program that plays the library: it pulls the change feed, fetches portraits and files, checks their SHA-256 and sends decisions and requests, to prove the API from the other side.
- **Covers:** OUT-10, AC-03
- **Depends on:** F-45
- **Owner input:** none (D-58 confirms this as the library's acceptance check)
- **Build:** `tools/library-stub.ts` (`npm run library-stub -- --base-url … --key …`); `src/jobs/seed_fixtures.ts`, which seeds fixture portraits in stub mode on staging or a pull-request copy, marked as fixtures in their history (OUT-10), and is refused in production.
- **Checks:**
  - Against the in-process app on a fixture database, it:
    - pages the whole feed;
    - downloads every file and verifies each SHA-256;
    - sends one decision of each kind and one request of each kind, and resends one of each;
    - reports success.
  - It refuses a portrait whose file doesn't match its SHA-256, naming it.
  - It uses only what the contract defines: it is built from the contract's types alone.
  - A `seed_fixtures` job seeds portraits the stub can pull, each marked as a fixture; in production it's refused.
- **Test data:** the fixture database.
- **Live calls:** none (it runs against staging in F-27 and F-47)
- **Parkable:** no
- **Size:** S

### F-26 · End-to-end offline run
- **Phase:** 5
- **Goal:** One full offline run, from the authors list to the library stub's decisions and the next run's response, proving the whole chain with stubs. Prove it. This is Phase 5's gate card; the verifier adds its tests here.
- **Covers:** AC-01, AC-02, AC-03 (offline), SRC-08, SRC-12, IN-11 (key scan), RUN-07
- **Depends on:** F-05, F-46, F-48
- **Owner input:** none
- **Build:** `test/f26-end-to-end.test.ts`
- **Checks:**
  - **Sync and first run:** a fixture `authors.csv` with six teachers syncs, and a run publishes portraits for those with candidates. Every record is complete (SRC-08) and valid against the contract.
  - **The library stub then:**
    - approves one portrait;
    - turns one down as `not_this_teacher`;
    - sets a main portrait;
    - sends a `try_again` and a `try_link`.
  - **The next run:**
    - handles the requests first;
    - skips the teacher whose slots are full;
    - never tries the turned-down photograph again;
    - publishes the swap when a better copy is approved.
  - The rights log has one row per original considered, and a second run adds no duplicates.
  - A scan of every file, log line and answer the run produced finds none of the fake secrets.
- **Test data:** the stub world, extended to six teachers.
- **Live calls:** none
- **Parkable:** no
- **Size:** M

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
  - blocking: F-28 the board shows a row per original with every contender side by side, each beside its no-blend version, on the dark page colour, readable at 390 px
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
- Test data: record: `npm run record-ops -- F-50 --kind trial` (needs O-13), run against staging: it saves the latest trial result from staging's ops API to `test/fixtures/f50/` (F-49's recorder)
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
- Goal: Prove it: the release candidate works on its deployed copy, with the trial's defaults in its settings. The conductor then promotes that exact commit to production after the 24-hour veto window (D-66). It's production's first deploy, and its nightly schedule is on from then (RUN-08). The owner's steps around it are on the release checklist. This is Phase 6's gate card; the verifier adds its tests here. It creates nothing: it's a prove-it card and Phase 6's gate.
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
- Side effects: deploy (pull-request copies; and production, promoted by the conductor after the 24-hour window, D-66); external write (the seed, on the deployed copy)
- Parkable: no
- Size: S
- Stop if: the trial's winner (F-50) was vetoed and not replaced


---

## Withdrawn

- **F-20 · Model-drawn outline:** *withdrawn* by D-49. The outline is drawn by code (F-15).
- **F-33 · Internet Archive book plates:** *withdrawn* by D-24.
