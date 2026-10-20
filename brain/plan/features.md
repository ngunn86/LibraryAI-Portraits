# Feature cards (build order)

**Status: draft 2 (Claude, 2026-10-20),** for the hosted TypeScript app (D-31..D-57). It replaces draft 1, the Python CLI cards, which are in git history.
- The harness builds these one at a time, **in the order of the overview table**, respecting *Depends on*. IDs are permanent, so the build order isn't numeric. Retired cards keep their IDs as *withdrawn*.
- The card format stays provisional until the harness settles its own (D-15). Converting should be mechanical.

**How checks run** ([build-plan.md §5](build-plan.md)):
- Every check is a `node:test` test in `test/fNN-*.test.ts`, named with its card (`"F-07: …"`), so `npm test -- --test-name-pattern "F-07"` runs one card.
- Offline by default: outbound calls refused, no keys, PGlite for the database.
- *Smoke* checks run against the pull request's deployed copy (HT-26).

## Card format

```
### F-NN · Title
- Phase:        1–6
- Goal:         one sentence
- Covers:       requirement IDs
- Depends on:   F-IDs, or "none"
- Owner input:  O-IDs, or "none"
- Build:        modules or files (paths as in spec/architecture.md)
- Checks:       bulleted; each one a test (offline unless marked smoke or live)
- Test data:    fixtures needed
- Live calls:   none | network (free public APIs) | deploy (Railway, no AI spend) | paid (≤ $N)
- Parkable:     yes | no (if stuck, can the build continue without it?)
- Size:         S | M | L
```

## Overview, in build order

| # | F | Title | Phase | Depends on | Owner input | Live | Parkable |
|---|---|---|---|---|---|---|---|
| 1 | F-01 | Skeleton, settings, secrets, offline tests | 1 | none | none | none | no |
| 2 | F-03 | The API contract in code | 1 | F-01 | none | none | no |
| 3 | F-04 | Database, queue and step cache | 1 | F-01 | none | none | no |
| 4 | F-37 | Storage bucket client | 1 | F-01 | none | none | no |
| 5 | F-36 | Railway setup and deploys | 1 | F-01, F-04, F-37 | O-8 | deploy | no |
| 6 | F-02 | Authors list reader and row checks | 2 | F-01 | none | none | no |
| 7 | F-06 | Outbound client (allowlist, polite, cached, replayable) | 2 | F-01, F-04 | none | none | no |
| 8 | F-31 | Teacher sync through GitHub | 2 | F-02, F-04, F-06 | O-9 (live only) | network | no |
| 9 | F-07 | Licence classifier and credit lines | 2 | F-06 | none | network | no |
| 10 | F-32 | Rights log | 2 | F-04, F-07 | none | none | no |
| 11 | F-08 | Wikidata: fetch, check, find ids | 2 | F-06 | none | network | no |
| 12 | F-09 | Commons: P18 and depicts | 2 | F-07, F-08 | none | network | no |
| 13 | F-10 | Library of Congress pictures | 2 | F-07, F-32 | none | network | yes |
| 14 | F-34 | Wellcome Collection | 2 | F-07, F-32 | none | network | yes |
| 15 | F-35 | Finding missing dates and ids | 2 | F-08, F-31 | none | network | yes |
| 16 | F-38 | Coverage survey | 2 | F-09, F-10*, F-34*, F-35*, F-36 | O-9, O-10 | network | yes |
| 17 | F-39 | Porting spike: OpenCV.js and sharp | 3 | F-01 | none | none | no |
| 18 | F-12 | Face landmarks and crop | 3 | F-39 | none | none | no |
| 19 | F-13 | Descreen and edge-preserving blur | 3 | F-39 | none | none | no |
| 20 | F-14 | Tone and halftone | 3 | F-39 | none | none | no |
| 21 | F-15 | Mask, code outline, master and cut-out limits | 3 | F-12, F-14 | none | none | no |
| 22 | F-30 | AI copy: key mask, alignment, drift check, blend | 3 | F-12, F-13 | none | none | no |
| 23 | F-41 | Black-and-white, 500 px and viewing copies | 3 | F-15 | none | none | no |
| 24 | F-42 | Same photograph or different (code layers) | 3 | F-12 | none | none | no |
| 25 | F-16 | Parity with the Python prototype | 3 | F-13, F-15, F-30, F-41 | none | none | no |
| 26 | F-17 | OpenRouter client, spend ledger and caps | 4 | F-04, F-06 | none | none | no |
| 27 | F-18 | Pre-check | 4 | F-17 | none | none | no |
| 28 | F-19 | AI copy and keyed cut-out calls | 4 | F-17, F-30 | none | none | no |
| 29 | F-21 | Draft check and compare-with-target | 4 | F-17, F-15 | none | none | no |
| 30 | F-43 | Same-photograph tie-break | 4 | F-17, F-42 | none | none | no |
| 31 | F-11 | Candidates: gather, group, order, download | 4 | F-09, F-10*, F-34*, F-32, F-37, F-42, F-43 | none | none | no |
| 32 | F-24 | Publishing a portrait | 5 | F-03, F-04, F-07, F-37, F-41 | none | none | no |
| 33 | F-23 | Per-teacher pipeline and failure policy | 5 | F-11, F-16, F-18, F-19, F-21, F-24 | none | none | no |
| 34 | F-25 | Queue, schedule and run reports | 5 | F-23 | none | none | no |
| 35 | F-44 | API: reads, change feed, files, keys | 5 | F-03, F-24 | none | none | no |
| 36 | F-45 | API: decisions and requests | 5 | F-44, F-25 | none | none | no |
| 37 | F-48 | Later runs: better copies, turn-downs, corrections | 5 | F-23, F-45 | none | none | no |
| 38 | F-46 | Admin site | 5 | F-25, F-32, F-35*, F-44 | none | none | no |
| 39 | F-22 | Commands and `doctor` | 5 | F-17, F-25, F-44 | none | none | yes |
| 40 | F-05 | Library stub | 5 | F-45 | O-12 (Q-27) | none | no |
| 41 | F-26 | End-to-end offline run | 5 | F-05, F-22*, F-46, F-48 | none | none | no |
| 42 | F-27 | Live smoke test on staging | 6 | F-26, F-36 | O-4, O-8, O-9, O-10 | paid ≤ $2 | no |
| 43 | F-28 | Trial, board and defaults | 6 | F-27, F-38 | O-4 | paid ≤ $27 | no |
| 44 | F-29 | The examples reproduced | 6 | F-28 | none | paid ≤ $3 | yes |
| 45 | F-47 | Production release and first nightly run | 6 | F-27, F-28, F-29* | O-11 | paid ≤ $100 | no |
| — | F-20 | ~~Model-drawn outline~~ | — | — | — | — | *withdrawn* (D-49) |
| — | F-33 | ~~Internet Archive book plates~~ | — | — | — | — | *withdrawn* (D-24) |

\* If a parkable dependency is parked, the card is built without it, and the digest says so. For example, F-11 is built without the LoC if F-10 is parked.

F-28 and F-29 share the trial's $30 budget (TRI-07). SCOPE-01..04 are boundaries rather than features; reviewers check them, and F-06's allowlist test enforces AC-06. OUT-08 (the zip) has no card unless the owner keeps it (Q-27).

---

## Phase 1: Foundation and deploys

### F-01 · Skeleton, settings, secrets, offline tests
- **Phase:** 1
- **Goal:** A TypeScript repo on Node 24, matching the library's toolchain, with typed settings, secrets from the environment, a CLI frame and an offline test suite.
- **Covers:** IN-10, IN-11, STY-05, RUN-05 (frame), RUN-06, PIP-09 (the family rule)
- **Depends on:** none
- **Owner input:** none
- **Build:**
  - `package.json` with Node 24 engines, `.nvmrc` and `tsconfig.json`;
  - scripts `check` (tsc), `build` (esbuild), `test` (`tsx --test`);
  - `src/config/settings.ts` (recipe 0.4.0 values from `prototype/recipe.py`, models, caps, schedule, sources);
  - `src/config/env.ts` (zod);
  - `src/cli.ts`;
  - a test setup that refuses all outbound calls.
- **Checks:**
  - `npm run check`, `npm test` and `npm run build` pass with no keys set and outbound calls refused.
  - `portraits --help` lists `doctor`, `sync`, `survey`, `run`, `trial`, `keys`, `password` and `status`. Unbuilt commands say "not built yet" and exit non-zero.
  - An invalid setting (wrong type, missing value, an unknown source host) stops start-up with a message naming it.
  - Changing any recipe value without changing `recipeVersion` fails a test (STY-05). The test compares a hash of the recipe block against the hash recorded for its version.
  - A checking model of the same family as any enhance model is refused at start-up (PIP-09).
  - A missing secret is reported by name only. A test that sets fake secrets and runs every command finds none of their values in the output.
- **Test data:** valid and invalid settings objects.
- **Live calls:** none
- **Parkable:** no
- **Size:** M

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
  - The seven refused payloads from `check_api.py` are refused by both ajv and zod. Examples: a turn-down without a reason; an unknown field in a decision.
  - zod and ajv agree on 10 good and 10 bad generated payloads per request body.
  - A test fails if `contracts/portraits-api.openapi.json` differs from `brain/contracts/portraits-api.openapi.json`, so the two copies can't drift.
- **Test data:** the contract's samples.
- **Live calls:** none
- **Parkable:** no
- **Size:** S

### F-04 · Database, queue and step cache
- **Phase:** 1
- **Goal:** The records of T-07 in Postgres through Drizzle, a job queue that survives crashes, and a cache of paid step results.
- **Covers:** RUN-03, PIP-12 (storage), IN-08 (storage), T-07
- **Depends on:** F-01
- **Owner input:** none
- **Build:**
  - `src/db/schema.ts` and `src/db/migrations/` (drizzle-kit SQL), with these tables: `teachers`, `candidates`, `photographs`, `portraits`, `files`, `portrait_events`, `library_decisions`, `requests`, `runs`, `spend`, `jobs`, `step_cache`, `api_keys`, `changes`, `sessions`;
  - `src/queue.ts`;
  - a PGlite test helper.
- **Checks:**
  - The migrations run from empty on PGlite, and every table records and reads back.
  - Two workers claiming at once never get the same job (`FOR UPDATE SKIP LOCKED`, shown with two connections).
  - A job whose worker stops heartbeating is claimed again after the timeout, and resumes at its last finished step.
  - The step cache hits for the same key, and misses when the SHA-256, step, model or settings hash changes.
  - The `changes` table hands out increasing sequence numbers, also inside concurrent transactions.
- **Test data:** none
- **Live calls:** none
- **Parkable:** no
- **Size:** M

### F-37 · Storage bucket client
- **Phase:** 1
- **Goal:** Store and fetch a portrait's files in the private bucket under OUT-12's layout, and hand out 15-minute signed links.
- **Covers:** OUT-12 (layout), RUN-10 (private bucket, signed links)
- **Depends on:** F-01
- **Owner input:** none
- **Build:** `src/storage/bucket.ts` (`@aws-sdk/client-s3`, `s3-request-presigner`); an in-memory fake with the same interface for tests; layout helpers.
- **Checks:**
  - Putting and getting a file round-trips, with its SHA-256 and content type.
  - Keys follow `portraits/<teacher_id>/<portrait_id>/<file>`. A bad id (path characters, `..`) is refused.
  - A signed link expires after 15 minutes (the fake checks the expiry it was given).
  - Nothing is ever deleted by the client's normal calls; there's no delete method outside tests.
- **Test data:** small files.
- **Live calls:** none (the real bucket is first used in F-36's smoke checks)
- **Parkable:** no
- **Size:** S

### F-36 · Railway setup and deploys
- **Phase:** 1
- **Goal:** The app deploys itself to Railway as web, worker and cron services with Postgres and a bucket, in production, staging and per-PR copies, set up as code.
- **Covers:** RUN-01, RUN-08 (cron frame), RUN-10 (environment caps as variables), HT-02..HT-04, HT-07, HT-08, HT-11
- **Depends on:** F-01, F-04, F-37
- **Owner input:** O-8 (Railway account and project, harness access)
- **Build:**
  - `.railway/railway.ts`: services, start commands, pre-deploy `drizzle-kit migrate`, healthcheck path, cron schedule, environments;
  - `src/web.ts` with `GET /api/v1/health`, which reports the version, the commit and whether OpenCV.js and `sharp` loaded;
  - `src/worker.ts` and `src/cron.ts` frames (the cron job exits with "nothing to do").
- **Checks:**
  - **Smoke:** the PR copy's `/api/v1/health` answers 200 with this commit within a few minutes of the push.
  - **Smoke:** the PR copy's database has the migrations applied; its bucket accepts a put and returns a signed link that downloads.
  - **Smoke:** a deliberately failing healthcheck (behind a test flag) doesn't replace the running release (HT-08).
  - The cron command exits 0 in a test.
  - `.railway/railway.ts` type-checks. Anything it can't express is listed in `docs/railway-dashboard-steps.md`.
- **Test data:** none
- **Live calls:** deploy (Railway; no AI spend)
- **Parkable:** no
- **Size:** M

---

## Phase 2: Teachers and sources

### F-02 · Authors list reader and row checks
- **Phase:** 2
- **Goal:** Read library-pipeline's `authors.csv`, keep the active rows, read their dates, and report bad rows by name while the rest load.
- **Covers:** IN-01, IN-02, IN-03, IN-05, AC-01 (part)
- **Depends on:** F-01
- **Owner input:** none
- **Build:** `src/teachers/authors.ts`
- **Checks:**
  - A fixture copied from the real header, with 12 rows (active, proposed, excluded; dates `1854-1948`, `d. 1925`, `b. 1870`, blank and unreadable), yields exactly the active rows. Aliases are split on `;`.
  - Each reason (missing name, unreadable date, death before birth, a lifespan over 120 years, a future year) is reported with its row number, and the other rows load.
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
- **Depends on:** F-01, F-04
- **Owner input:** none
- **Build:** `src/net/client.ts`
- **Checks:**
  - A request to a host outside the allowlist (the adopted sources, `api.github.com`, `openrouter.ai`) fails before leaving the process.
  - Every request carries the User-Agent from settings: name, version, contact.
  - **Pacing, on a fake clock:**
    - 30 LoC calls take at least 90 seconds (20 a minute);
    - Wikimedia and Wellcome calls never overlap.
  - **Retries:** a 429, a 503 and an HTML CAPTCHA page each back off and retry up to the limit; a 404 isn't retried.
  - A second identical GET within the cache's lifetime is served from the cache.
  - In replay mode, recorded responses are served with no network. A request with no recording fails clearly, naming the URL.
- **Test data:** a fake transport; a CAPTCHA page sample.
- **Live calls:** none
- **Parkable:** no
- **Size:** M

### F-31 · Teacher sync through GitHub
- **Phase:** 2
- **Goal:** Sync the active authors from the private library-pipeline repo into the database, with stable teacher ids, nightly and by command.
- **Covers:** IN-01, IN-04 (eligibility), IN-12, AC-01
- **Depends on:** F-02, F-04, F-06
- **Owner input:** O-9 (the read-only GitHub token), needed for the live check only
- **Build:** `src/teachers/sync.ts`; the `sync` command; the cron job calls it.
- **Checks:**
  - A recorded GitHub contents response syncs to the expected teachers.
  - A second sync with the same file changes nothing (no new rows, no `record_version` bumps, no change-feed entries).
  - Renaming an author keeps the `teacher_id`. A clashing slug gets `-2` and is reported. An author no longer active gets `on_list = false`, and their portraits are untouched.
  - Each teacher's eligibility (IN-04) is set: `qid`, `lcnaf_or_years` or `none`.
  - The only GitHub call is a GET of `collection/authors.csv`. No write method exists in the client.
  - **Live:** with O-9 present, `portraits sync` reads the real file and reports 182 ± 20 active authors.
- **Test data:** a recorded contents response with a fixture CSV.
- **Live calls:** network (GitHub, free)
- **Parkable:** no
- **Size:** M

### F-07 · Licence classifier and credit lines
- **Phase:** 2
- **Goal:** Map any Commons, LoC or Wellcome rights statement to tier 1, tier 2 or refused, and build each file's licence and credit line.
- **Covers:** SRC-02, SRC-11
- **Depends on:** F-06
- **Owner input:** none
- **Build:** `src/sources/licences.ts`; a fixture table of real licence strings.
- **Checks:**
  - A table test over at least 40 real strings, each with its expected class:
    - public-domain marks, CC0, "No known restrictions on publication" and Wellcome's PDM → tier 1;
    - CC BY and CC BY-SA in several versions → tier 2;
    - NC, ND, fair use, GFDL alone, "rights status not evaluated" and blank → refused.
  - A dual-licensed file takes its most open allowed licence. An unknown string is refused, and its raw text is kept.
  - Adaptation licences follow SRC-11's table: CC0 1.0 for public domain, CC BY 4.0 for CC BY, CC BY-SA 4.0 for CC BY-SA 2.0 and later; CC BY-SA 1.0 is held.
  - Credit lines match SRC-11's formats, including the example, and "Portrait by New Thought Nexus, adapted from: …" for the adaptations.
- **Test data:** strings recorded once from real responses.
- **Live calls:** network (free; to record the strings once)
- **Parkable:** no
- **Size:** S

### F-32 · Rights log
- **Phase:** 2
- **Goal:** One permanent row for every original considered, refusals included, with its evidence, verdict, match and credit, and a CSV export.
- **Covers:** SRC-12, SRC-08, D-14
- **Depends on:** F-04, F-07
- **Owner input:** none
- **Build:** `src/sources/rightsLog.ts`
- **Checks:**
  - Recording the same original twice keeps one row, keyed by source and source id (and SHA-256 once downloaded), and adds to its history.
  - A refused original keeps its reason, and a later run doesn't research it.
  - A candidate missing its source, item link, licence or credit line is refused (SRC-08).
  - The CSV export has every SRC-08 and SRC-12 field, and the raw record is kept beside it.
- **Test data:** records from F-07's fixtures.
- **Live calls:** none
- **Parkable:** no
- **Size:** S

### F-08 · Wikidata: fetch, check, find ids
- **Phase:** 2
- **Goal:** Read a teacher's Wikidata item, check a given id, and find a missing one as SRC-06 allows.
- **Covers:** SRC-03 (R1), SRC-06 (a, b's Wikidata half), IN-04
- **Depends on:** F-06
- **Owner input:** none
- **Build:** `src/sources/wikidata.ts`
- **Checks:**
  - A good id returns its P18 file name, its birth and death years, its labels and aliases, and its LoC name id (P244) if present.
  - An id that isn't a human, or whose years disagree with the teacher's, is refused with the reason.
  - **Search:** one unique human with the name or an alias and both years is returned as a candidate; two matches, none, or a year mismatch return nothing.
- **Test data:** recorded responses for about six real teachers and the edge cases.
- **Live calls:** network (free; to record)
- **Parkable:** no
- **Size:** S

### F-09 · Commons: P18 and depicts
- **Phase:** 2
- **Goal:** Turn a teacher's P18 image and their depicts-tagged Commons files into candidates, with licence, author and credit.
- **Covers:** SRC-03 (R1, R2), SRC-08
- **Depends on:** F-07, F-08
- **Owner input:** none
- **Build:** `src/sources/commons.ts` (`imageinfo` with `extmetadata`; search with `haswbstatement:P180=<Q-id>` in the file namespace).
- **Checks:**
  - **R1:** the P18 file becomes a candidate (`wikidata_p18`) with its licence, author, credit, size and file link.
  - **R2:** each depicts-tagged file becomes a candidate (`commons_p180`); a file that is only in the teacher's category doesn't (negative fixture).
  - Non-image files (PDF, DjVu, audio) are skipped.
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
- **Owner input:** none
- **Build:** `src/sources/loc.ts` (loc.gov JSON, `fo=json`)
- **Checks:**
  - **Matches:** a record whose name heading carries the teacher's LoC name id; a record with a heading like `Fillmore, Charles, 1854-1948` whose dates match.
  - **No match:** a near miss (same name, different dates); an undated heading; a name in the title only.
  - The rights advisory is classified by F-07. "Rights status not evaluated" is refused.
  - The largest available image link is chosen, and its pixel size is recorded when given.
  - Requests are paced to 20 a minute (through F-06).
- **Test data:** recorded responses for three teachers, plus near-miss and undated records.
- **Live calls:** network (free; to record)
- **Parkable:** yes (F-11 is then built without the LoC)
- **Size:** M

### F-34 · Wellcome Collection
- **Phase:** 2
- **Goal:** Find Wellcome picture records whose contributor or subject is the teacher, by LoC name id or name and dates, with clean licences.
- **Covers:** SRC-03 (R3), SRC-05, SRC-08
- **Depends on:** F-07, F-32
- **Owner input:** none
- **Build:** `src/sources/wellcome.ts` (catalogue API, no key; images through IIIF).
- **Checks:**
  - A record whose contributor or subject carries the teacher's LoC name id matches. So does one with the name and matching dates.
  - Licences map through F-07: PDM and CC0 → tier 1; CC BY → tier 2; CC BY-NC → refused.
  - The IIIF image link for the full size is recorded.
- **Test data:** recorded responses for two teachers (one mind-cure figure).
- **Live calls:** network (free; to record)
- **Parkable:** yes
- **Size:** S

### F-35 · Finding missing dates and ids
- **Phase:** 2
- **Goal:** Fill a teacher's missing Wikidata id, LoC name id and dates only when Wikidata and the LoC name authority agree; list everything else for the owner.
- **Covers:** IN-13, SRC-06 (b, c), IN-04
- **Depends on:** F-08, F-31
- **Owner input:** none
- **Build:** `src/teachers/enrich.ts`; `src/sources/locNames.ts` (id.loc.gov).
- **Checks:**
  - Both sources agree on the person and both years → the ids and dates are stored and marked `resolved_by_tool`.
  - Disagreement, or only one source with data → nothing stored; a suggestion with its evidence is listed.
  - The suggestions export as a CSV whose columns match `authors.csv` (name, aliases, dates, plus `wikidata_qid` and `lcnaf_id` and the evidence).
  - A teacher left with no id and no dates is marked skipped, with what to add.
- **Test data:** recorded Wikidata and id.loc.gov responses for agree, disagree and one-sided cases.
- **Live calls:** network (free; to record)
- **Parkable:** yes (teachers without ids then stay skipped until the owner adds them)
- **Size:** M

### F-38 · Coverage survey
- **Phase:** 2
- **Goal:** Search every active teacher on every adopted source without downloading or spending, and report coverage, so Smithsonian, the trial set and PIP-20's real pairs can be decided.
- **Covers:** SRC-14, TRI-02 (input), PIP-20 (real pairs)
- **Depends on:** F-09, F-10*, F-34*, F-35*, F-36
- **Owner input:** O-9 (GitHub token, for the teacher list), O-10 (User-Agent contact)
- **Build:** `src/sources/survey.ts`; the `survey` command; a report stored in the database and shown on the admin site later (F-46).
- **Checks:**
  - Offline, on recorded responses for five teachers, the report's counts by source, rule and licence tier match the fixture's expected counts.
  - No file download, no model call and no portrait is made (the clients assert it).
  - The report lists teachers with no candidate, and, per teacher with two or more candidates, the pairs worth recording as same-photo fixtures.
  - **Live:** `railway run portraits survey` on staging completes for all active teachers within the sources' limits. It writes the report and records the responses used for the trial set as fixtures.
- **Test data:** recorded responses for five teachers.
- **Live calls:** network (free)
- **Parkable:** yes (the trial waits for it)
- **Size:** M

---

## Phase 3: Imaging (ported from the Python prototype)

### F-39 · Porting spike: OpenCV.js and sharp
- **Phase:** 3
- **Goal:** Prove that every image operation the recipe needs works in TypeScript, choose the fallback for any gap, and give the imaging cards a safe way to use OpenCV.js.
- **Covers:** architecture.md ("Porting risks"); groundwork for STY-01..STY-09, PIP-04, PIP-05, PIP-13, PIP-20
- **Depends on:** F-01
- **Owner input:** none
- **Build:**
  - `src/imaging/cv.ts`: load OpenCV.js once, and a `withMats(fn)` helper that frees every Mat made inside;
  - `src/imaging/io.ts` (`sharp`: decode, colour to sRGB, RGBA PNG out);
  - `prototype/export_parity.py`, run once in Python and its outputs committed, which writes reference results for each operation on two fixture images;
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
- **Covers:** PIP-04, STY-03
- **Depends on:** F-39
- **Owner input:** none
- **Build:** `src/imaging/face.ts` (YuNet ONNX, MIT, committed with its source and licence noted); `src/imaging/crop.ts`
- **Checks:**
  - On the owner's three originals, the landmarks fall within 3% of the face width of the prototype's fixtures (`prototype/fixtures/*.json`).
  - The crop puts the eye line at 0.443 of the side and the eye-to-mouth distance at 0.237 of the side, with the face centred, each within 1%.
  - With no face found, the pre-check's box is used and the eye line is estimated from it (synthetic case).
  - A face narrower than `minFacePx` is reported as too small.
- **Test data:** the three originals; the prototype's fixtures; a synthetic image with no face.
- **Live calls:** none
- **Parkable:** no
- **Size:** M

### F-13 · Descreen and edge-preserving blur
- **Phase:** 3
- **Goal:** Detect a printed dot pattern by frequency analysis, notch it out, and give every original an edge-preserving blur sized in dot cells.
- **Covers:** PIP-05
- **Depends on:** F-39
- **Owner input:** none
- **Build:** `src/imaging/descreen.ts` (port of `descreen` and `detect_screen` in `prototype/recipe.py`).
- **Checks:**
  - The owner's Fillmore and Cady originals are detected as screened, and Holmes isn't (the prototype's result).
  - A synthetic screened image has its screen peaks reduced by at least the factor the prototype achieves.
  - A clean image gets only the mild blur. Its output differs from the input by no more than the prototype's on the same image.
  - What was found and applied is returned for the record.
- **Test data:** the three originals; a synthetic screen.
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
- **Test data:** the prototype's cut-out fixtures; synthetic bad masks.
- **Live calls:** none
- **Parkable:** no
- **Size:** M

### F-30 · AI copy: key mask, alignment, drift check, blend
- **Phase:** 3
- **Goal:** Take an AI copy on flat green, read the cut-out from its green, align it to the original, refuse it if details moved, and blend it at 50% in the portrait's frame.
- **Covers:** PIP-13 (code side), PIP-03 (key mask), STY-04
- **Depends on:** F-12, F-13
- **Owner input:** none
- **Build:** `src/imaging/align.ts`, `blend.ts` (ports of `key_mask`, `align_enhanced`, `local_drift` and the blend in `make_master`).
- **Checks:**
  - **Alignment:** synthetic keyed copies (2.8× larger, sharpened, rescaled by 2%, shifted, on green) align with correlation ≥ 0.99.
  - **Blend:** it shows no double edges (edge agreement ≥ 0.98), and the blend share is exactly `enhanceBlend`.
  - **Key mask:** the mask from the green matches the prototype's cut-out fixture with overlap ≥ 0.94.
  - **Drift check:** copies with the eyes and mouth moved by about 1.2 dot cells measure above 0.7 and are refused; good copies measure below. Both are within 0.1 of the prototype's figures (`prototype/out/enhance-mechanics.json`).
  - **Poor alignment:** a copy that can't be aligned (a different face) is refused, and the original is used alone.
- **Test data:** the generator from `prototype/test_enhance_mechanics.py`, ported.
- **Live calls:** none
- **Parkable:** no (the cut-out depends on it)
- **Size:** M

### F-41 · Black-and-white, 500 px and viewing copies
- **Phase:** 3
- **Goal:** Make the black-and-white version (option C) and the 500 px copies from the master's layers, and the original's PNG viewing copy.
- **Covers:** STY-08, STY-09, OUT-05
- **Depends on:** F-15
- **Owner input:** none
- **Build:** `src/imaging/versions.ts` (ports of `bw_version`, `small` and `check_bw`).
- **Checks:**
  - `bw-1000` passes `check_bw`: visible pixels are grey; the corners are transparent; it's opaque wherever the master shows.
  - Both 500 px copies pass their checkers.
  - The viewing copy:
    - is a PNG at most 1,600 px on the long side;
    - is never enlarged (a 300 px original stays 300 px);
    - keeps transparency from a PNG original.
- **Test data:** the prototype's layers via the three examples; a transparent PNG.
- **Live calls:** none
- **Parkable:** no
- **Size:** S

### F-42 · Same photograph or different (code layers)
- **Phase:** 3
- **Goal:** Tell copies of one photograph from different photographs with a face fingerprint and feature matching, leaving the unclear middle for the model (F-43).
- **Covers:** PIP-20 (layers 1 and 2), PIP-15
- **Depends on:** F-12
- **Owner input:** none
- **Build:** `src/imaging/samePhoto.ts` (a port of `prototype/same_photo.py`, plus a perceptual hash of the cropped face).
- **Checks:**
  - The prototype's 30 doctored copies are judged the same. These are crop, rescale, rotation, JPEG, blur, reprint screen, mirror and noise, generated as in `same_photo.py`. Their inlier counts are within 25% of `prototype/out/same-photo.json`.
  - The different-photograph pairs score at or below `diffMaxInliers`.
  - Exact duplicates are caught by the fingerprint alone.
  - A pair between the thresholds is returned as "unclear", for F-43.
  - When the survey's real pairs exist (F-38), they're added as fixtures. Two sittings of one teacher must come out "different" or "unclear", never "same".
- **Test data:** the three originals and the generator; the survey's pairs when recorded.
- **Live calls:** none
- **Parkable:** no
- **Size:** M

### F-16 · Parity with the Python prototype
- **Phase:** 3
- **Goal:** Lock the TypeScript recipe to the Python reference: from the prototype's fixtures, it must reproduce the prototype's outputs within tolerance.
- **Covers:** STY-07; AC-04 (groundwork)
- **Depends on:** F-13, F-15, F-30, F-41
- **Owner input:** none
- **Build:** `test/f16-parity.test.ts`; the reference outputs from `prototype/out/` copied into `test/fixtures/reference/`.
- **Checks:**
  - For each of the three examples, at the automatic crop and at the owner's framing, against the prototype's `white-1000`:
    - figure overlap ≥ 0.98;
    - mean alpha difference ≤ 0.02;
    - dots across 110 ± 1.
  - The same for `bw-1000`, and for both 500 px copies.
  - The recipe version and settings hash are equal to the prototype's 0.4.0 values.
- **Test data:** `prototype/fixtures/`, `prototype/out/`.
- **Live calls:** none
- **Parkable:** no (a failure goes to the digest with the measures)
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
  - **Caps,** each crossed mid-run with stubbed costs, stop the next call before it is made:
    - the first-run cap ($100);
    - the night ($10) and month ($30) caps;
    - $2 per teacher per run;
    - $2 a night in staging and PR copies;
    - the trial budget ($30).

    The stop is reported cleanly.
  - Each call's cost is logged with run, teacher, step, model, environment and whether it is actual or estimated.
  - A model whose family equals the enhance model's is refused for checking.
  - Model ids and prices come from settings. An unknown model id is refused before any call.
- **Test data:** canned OpenRouter answers, including usage and cost fields.
- **Live calls:** none
- **Parkable:** no
- **Size:** M

### F-18 · Pre-check
- **Phase:** 4
- **Goal:** Ask Claude Haiku whether an original can be used, and record its structured verdict.
- **Covers:** PIP-02, PIP-18 (age estimate), D-47 (medium), D-52
- **Depends on:** F-17
- **Owner input:** none
- **Build:** `src/models/precheck.ts`; `src/models/prompts/precheck.md` (from `prototype/prompts/`, v2)
- **Checks:**
  - Canned verdicts drive pass and fail. A fail sets the original aside with its reasons, and no further call is made for it.
  - The face box, medium, age estimate, dot pattern and caption are parsed. Malformed JSON is retried once, then counted as a failure with the raw text kept.
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
- **Covers:** PIP-13 (calls and records), PIP-03 (fallback), PIP-10 (fresh copy on a remake), D-52, D-56
- **Depends on:** F-17, F-30
- **Owner input:** none
- **Build:** `src/models/enhance.ts`, `cutout.ts`; prompts `enhance_keyed.md`, `cutout_keyed.md`
- **Checks:**
  - A canned image answer becomes `enhanced.png`, with the model, prompt version, alignment and drift scores and whether it was used.
  - A second try on the same original makes no call; a remake (PIP-10) makes exactly one new call.
  - A mask failing PIP-19, or a copy refused by its safeguards, triggers one `cutout_keyed` call.
  - A `try_again` note is added to the enhance prompt, and recorded.
- **Test data:** synthetic keyed images as canned answers (from F-30's generator).
- **Live calls:** none
- **Parkable:** no
- **Size:** M

### F-21 · Draft check and compare-with-target
- **Phase:** 4
- **Goal:** Ask Claude Sonnet to judge a draft on five criteria against the original, and score a draft against a hand-made target.
- **Covers:** PIP-09, TRI-08 (mode), D-52
- **Depends on:** F-17, F-15
- **Owner input:** none
- **Build:** `src/models/draftCheck.ts`; prompts `draftcheck.md`, `compare.md`
- **Checks:**
  - The request carries the draft on a dark page, the original and the three examples.
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
- **Covers:** PIP-20 (layers 3 and 4), D-50
- **Depends on:** F-17, F-42
- **Owner input:** none
- **Build:** `src/models/samePhotoCheck.ts`; prompt `same_photo.md`
- **Checks:**
  - "same" groups the pair; "different" separates it; "unsure" groups it (D-50).
  - The evidence is recorded with the pair.
  - A pair is never asked twice (cached by both SHA-256s, in either order).
- **Test data:** canned answers.
- **Live calls:** none
- **Parkable:** no
- **Size:** S

### F-11 · Candidates: gather, group, order, download
- **Phase:** 4
- **Goal:** Gather a teacher's candidates from every adopted source, drop refused licences, group copies of one photograph, order the copies, and download the chosen ones with a checksum.
- **Covers:** SRC-07, SRC-08, PIP-15, PIP-01 (part), OUT-12 (originals)
- **Depends on:** F-09, F-10*, F-34*, F-32, F-37, F-42, F-43
- **Owner input:** none
- **Build:** `src/sources/candidates.ts`
- **Checks:**
  - A fixture teacher with candidates from three sources (one refused licence, one exact duplicate, two copies of one photograph, one different photograph) gives:
    - two photographs;
    - the refused one logged;
    - the duplicate merged;
    - the right best copy per photograph (licence tier, then size).
  - Downloads are checked against their SHA-256 on a second fetch, and stored as `original.<ext>`.
  - Set-aside photographs are excluded.
  - The best-known flag is set on the P18 photograph and its copies.
- **Test data:** recorded responses; small image fixtures, including doctored copies.
- **Live calls:** none
- **Parkable:** no
- **Size:** M

---

## Phase 5: Pipeline and service

### F-24 · Publishing a portrait
- **Phase:** 5
- **Goal:** Write a portrait's eight files and its record atomically, with each file's licence and credit, and add it to the change feed.
- **Covers:** OUT-02, OUT-03, OUT-04, OUT-11, OUT-12, SRC-11, AC-02
- **Depends on:** F-03, F-04, F-07, F-37, F-41
- **Owner input:** none
- **Build:** `src/pipeline/portrait.ts`
- **Checks:**
  - A fixture portrait produces all eight files under its key, each passing its checker, plus `record.json`. The record validates against the contract's `Portrait`.
  - Each file's licence and credit follow SRC-11's table, for a public-domain, a CC BY and a CC BY-SA fixture.
  - Stopping the work after the files but before the database commit leaves no visible portrait, and no change-feed entry.
  - A record missing a licence isn't published. The failure names the field.
  - Portrait ids count up per teacher, and are never reused after a turn-down.
- **Test data:** images from phase 3; F-07's fixtures.
- **Live calls:** none
- **Parkable:** no
- **Size:** M

### F-23 · Per-teacher pipeline and failure policy
- **Phase:** 5
- **Goal:** Take one teacher from candidates to published portraits: open slots, the choice of photographs, pre-check, AI copy, draft, check, remake and set-asides.
- **Covers:** PIP-01, PIP-10, PIP-11, PIP-12, PIP-14, PIP-16, PIP-18 (dates), PIP-19 (in the flow)
- **Depends on:** F-11, F-16, F-18, F-19, F-21, F-24
- **Owner input:** none
- **Build:** `src/pipeline/teacher.ts`
- **Checks (all with stubs):**
  - A teacher with 5 different photographs gets 3 portraits: the P18 photograph first, then a spread across the teacher's life by approximate date.
  - **Failures:**
    - a draft failing twice sets its original aside, and the next photograph is tried;
    - a failure a new copy can't change sets it aside at once;
    - at most 6 drafted and 12 pre-checked per teacher per run.
  - A source date beats an estimated date; an estimate uses the birth year.
  - A cut-out limit failure triggers the keyed fallback call once.
  - A two-run scenario never tries a set-aside photograph again.
- **Test data:** a stub world (sources, models and images) for three teachers.
- **Live calls:** none
- **Parkable:** no
- **Size:** L

### F-25 · Queue, schedule and run reports
- **Phase:** 5
- **Goal:** Run the nightly schedule and the queue: sync, queue teachers with open slots not searched for a month, take requests first, resume after a crash, stop at a cap, and write each run's report.
- **Covers:** RUN-02, RUN-03, RUN-04 (stop and report), RUN-08, OUT-06
- **Depends on:** F-23
- **Owner input:** none
- **Build:** `src/cron.ts`, `src/worker.ts`; `src/pipeline/run.ts`
- **Checks (fake clock):**
  - **Queueing:**
    - a teacher searched 10 days ago isn't queued; one searched 35 days ago is;
    - a full teacher isn't queued;
    - a request goes ahead of queued teachers.
  - The cron job exits after queueing.
  - Killing the worker mid-teacher and restarting it resumes with no repeated paid call (stub call counts).
  - Reaching a cap stops the run cleanly. Finished portraits stay published, and the report says so.
  - A snapshot test of the fixture run's report covers every field of OUT-06.
- **Test data:** F-23's stub world.
- **Live calls:** none
- **Parkable:** no
- **Size:** M

### F-44 · API: reads, change feed, files, keys
- **Phase:** 5
- **Goal:** Serve the read side of the contract (teachers, portraits, history, files and the change feed) behind the library's key, with rate limits.
- **Covers:** OUT-14, SCOPE-02, RUN-10 (key, rate limit, signed links)
- **Depends on:** F-03, F-24
- **Owner input:** none
- **Build:** `src/api/` (Express routes, key middleware, change feed with cursors); `keys new|off|list`
- **Checks:**
  - Every read route's answers validate against the contract (F-03's helper), on a fixture database.
  - **Keys:** no key gives 401 `key_off`; a switched-off key gives 401; a good key gives 200. Keys are stored as hashes only, and a new key is shown once.
  - **Change feed:**
    - `since` then `after` pages through every change in order;
    - `more` and `next_cursor` behave as the contract says;
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
- **Covers:** IN-06, IN-07, IN-08, SRC-04
- **Depends on:** F-44, F-25
- **Owner input:** none
- **Build:** `src/api/decisions.ts`, `requests.ts`
- **Checks:**
  - **Decisions:**
    - approve, turn_down (each reason), set_main and correct change the portrait as IN-07 says, and appear in its history and the change feed;
    - approving a portrait with `replaces` makes the old one `replaced`.
  - **Bad decisions:** a turn-down without a reason is refused with `invalid` naming `/reason`; set_main on a waiting portrait gives `conflict`.
  - **Resending:** the same `decision_id` or `request_id` changes nothing and says it's a duplicate. Reusing an id with different content gives `conflict`.
  - **Requests:**
    - a `try_link` to an adopted source is queued;
    - a link elsewhere is refused with the reason;
    - a `try_again` asking to change the crop is answered `refused`, suggesting `another_original`.
  - Every answer validates against the contract.
- **Test data:** the fixture database.
- **Live calls:** none
- **Parkable:** no
- **Size:** M

### F-48 · Later runs: better copies, turn-downs, corrections
- **Phase:** 5
- **Goal:** On later runs, offer clearly better copies, bring back a turned-down photograph only when allowed, and never overwrite the library's corrections.
- **Covers:** PIP-17, PIP-18 (corrections), OUT-07
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
  - **Full slots:** with all slots full, a new photograph ranking above one of them is offered with `replaces`.
  - **Corrections:** a library-corrected date and best-known flag survive a re-run.
- **Test data:** F-23's stub world over three runs.
- **Live calls:** none
- **Parkable:** no
- **Size:** M

### F-46 · Admin site
- **Phase:** 5
- **Goal:** A read-only, phone-friendly admin site behind one password. It shows teachers, portraits, runs, the rights log, the suggestions for `authors.csv` and the keys.
- **Covers:** OUT-13, OUT-06 (pages), RUN-09, RUN-10 (login), SRC-12 (CSV), IN-13 (suggestions CSV)
- **Depends on:** F-25, F-32, F-35*, F-44
- **Owner input:** none
- **Build:** `src/admin/` (server-rendered templates); `password set`
- **Checks:**
  - **Login:**
    - each page needs a login, and the password is stored only as a slow hash;
    - a wrong password locks out after the set number of tries;
    - the session cookie is secure, HTTP-only and SameSite, and lasts 30 days.
  - **Pages:** the teacher list, one teacher (all versions, rights, the library's decisions), the runs and one run's report all render from the fixture database.
  - The rights-log CSV and the suggestions CSV download with the right columns.
  - No page has a form that changes data, except logging in and out.
  - Every page renders at 390 px wide without horizontal scrolling (a layout test).
  - No key or secret appears on any page.
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
- **Owner input:** O-12 (Q-27, which confirms this as the library's acceptance check)
- **Build:** `tools/library-stub.ts` (`npm run library-stub -- --base-url … --key …`)
- **Checks:**
  - Against the in-process app on a fixture database, it:
    - pages the whole feed;
    - downloads every file and verifies each SHA-256;
    - sends one decision of each kind and one request of each kind, and resends one of each;
    - reports success.
  - It refuses a portrait whose file doesn't match its SHA-256, naming it.
  - It uses only what the contract defines: it is built from the contract's types alone.
- **Test data:** the fixture database.
- **Live calls:** none (it runs against staging in F-27)
- **Parkable:** no
- **Size:** S

### F-26 · End-to-end offline run
- **Phase:** 5
- **Goal:** One full offline run, from the authors list to the library stub's decisions and the next run's response, proving the whole chain with stubs.
- **Covers:** AC-01, AC-02, AC-03 (offline), SRC-08, SRC-12, IN-11 (key scan), RUN-07
- **Depends on:** F-05, F-22*, F-46, F-48
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

### F-27 · Live smoke test on staging
- **Phase:** 6
- **Goal:** On staging with real keys, process one real teacher end to end, and run the library stub against it.
- **Covers:** OUT-10, OUT-14 (deployed), RUN-10 (deployed), HT-26
- **Depends on:** F-26, F-36
- **Owner input:** O-4 (OpenRouter key with a credit limit), O-8, O-9, O-10
- **Build:** `test/live/f27-smoke.test.ts` (runs only with `PORTRAITS_LIVE=1`); a staging seed of fixture portraits (stub mode) for the library's builders.
- **Checks:**
  - **Live:** `doctor` passes on staging.
  - **Live:** `run --teacher charles-fillmore` publishes at least one real portrait within $2, and every file passes its checker.
  - **Live:**
    - `/api/v1/health` answers 200;
    - a call without the key gets 401, and one with it gets 200;
    - the library stub completes against staging, SHA-256s included.
  - **Live:** the spend ledger shows each call's actual cost, and the night's total is under the staging cap.
  - The seeded fixture portraits are visible to the library stub. They're marked as fixtures in their record's history, and never published in production.
- **Test data:** none (live)
- **Live calls:** paid (≤ $2)
- **Parkable:** no
- **Size:** M

### F-28 · Trial, board and defaults
- **Phase:** 6
- **Goal:** Run the three enhance models over the trial set, score them, show the board, set the defaults with a new recipe version, and confirm PIP-20's thresholds on real pairs.
- **Covers:** TRI-01..TRI-07, PIP-20 (thresholds), D-47 (engravings), D-56
- **Depends on:** F-27, F-38
- **Owner input:** O-4; the owner's veto (by the digest's window)
- **Build:**
  - `src/pipeline/trial.ts`;
  - `test/fixtures/trial/trial-set.json`, picked from the survey: about 20 originals plus the owner's three, with expected outcomes;
  - the board page on the admin site.
- **Checks:**
  - The trial set covers every case in TRI-02, and each item's expected outcome holds. For example, the group photo is refused at the pre-check.
  - Every result is shown on the board with its original, its no-blend version, the examples, scores and cost. The board is readable at 390 px.
  - The winner follows TRI-04: the best score, or the cheaper within 5%. It is written to settings with a new `recipeVersion`, committed through the harness, and reversible by the veto.
  - PIP-20's thresholds are re-measured on the survey's real pairs. If two sittings of one teacher would be judged "same", the thresholds are adjusted (with a new `recipeVersion`) and the digest says so.
  - The engraving results are reported for the owner's verdict on `allowedMedia`.
  - The total spend is within $27, leaving $3 of the trial budget for F-29.
- **Test data:** the trial set.
- **Live calls:** paid (≤ $27)
- **Parkable:** no
- **Size:** L

### F-29 · The examples reproduced
- **Phase:** 6
- **Goal:** Show that the pipeline, with the trial's defaults, reproduces the owner's three hand-made portraits closely enough.
- **Covers:** TRI-08, AC-04, IN-09
- **Depends on:** F-28
- **Owner input:** none
- **Build:** `test/live/f29-examples.test.ts`
- **Checks:**
  - **Live:** for each example, "compare with target" passes against the hand-made portrait.
  - The code measures at the owner's framing (500 px) meet TRI-08: overlap ≥ 0.85, tone error ≤ 0.08, dots across 110 ± 2, no STY-06 problems.
  - It reuses the trial's cached AI copies; new spend stays within $3.
  - The examples are never published (D-13): the test runs them outside the publishing path.
- **Test data:** `design/portraits/`
- **Live calls:** paid (≤ $3)
- **Parkable:** yes (the digest reports the measures; the release can go ahead on the owner's word)
- **Size:** S

### F-47 · Production release and first nightly run
- **Phase:** 6
- **Goal:** Release to production after the owner's veto window, make the library's key, and let the nightly schedule work through the whole list under the first-run cap.
- **Covers:** RUN-01, RUN-08 (live), RUN-04 (first-run cap), AC-05
- **Depends on:** F-27, F-28, F-29*
- **Owner input:** O-11 (the library's key, made with `portraits keys new` and handed to the library); the veto window
- **Build:** a release checklist in the digest; no new code unless something is found.
- **Checks:**
  - **Live:** production's `/api/v1/health` shows the released commit, and `doctor` passes there.
  - **Live:** the first nightly run starts on schedule and publishes portraits. It stays under $100 in total across the nights it takes, and each run's report is on the admin site.
  - **Live:** the library's first pull, if the library is ready, appears in the API's access log. Otherwise the library stub's pull against production does.
  - The digest reports portraits published, teachers with none, teachers skipped for missing ids (with the CSV link), and spend.
- **Test data:** none (live)
- **Live calls:** paid (≤ $100, the first-run cap)
- **Parkable:** no
- **Size:** M

---

## Withdrawn

- **F-20 · Model-drawn outline:** *withdrawn* by D-49. The outline is drawn by code (F-15).
- **F-33 · Internet Archive book plates:** *withdrawn* by D-24.
