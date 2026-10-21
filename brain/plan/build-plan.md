# Build plan

**Status (2026-10-21):** proposed by Claude, for the hosted TypeScript app (D-31..D-68). Adapted to the Coding Harness's format 1 (`../../Coding Harness Instructions.md`, D-62..D-66): the harness's settings are in `../../harness.yaml`.

## 1. The shape of the work

| Phase | What | Cards | Who | Paid AI spend (tool key) |
|---|---|---|---|---|
| **0 · Planning** | Notes, decisions, API contract, style prototype, reviews | — | Claude with the owner; other AI tools review | none |
| **— · Harness proof** | The throwaway app: build, deploy, test and tear down on Railway ([../handoffs/harness-throwaway-test.md](../handoffs/harness-throwaway-test.md)) | HT-01..HT-32 | Harness (planned in its own chat) | ≤ $0.50 |
| **1 · Foundation and deploys** | Repo and test runner, settings and secrets, API contract in code, database and queue, bucket, Railway setup with staging and PR copies and the health check, jobs over the web; the phase's gate | F-01, F-51, F-03, F-04, F-37, F-36, F-49, F-53 | Harness | none |
| **2 · Teachers and sources** | The authors list, the outbound client, Wikidata, the teacher sync, licences, rights log, Commons, LoC, Wellcome, finding ids, the coverage survey; the phase's gate | F-02, F-06, F-08, F-31, F-07, F-32, F-09, F-10, F-34, F-35, F-38, F-54 | Harness | none (free public APIs) |
| **3 · Imaging (ported from the Python prototype)** | Porting spike, face and crop, descreen, halftone, mask and outline, blend, versions, same-photo check; parity with the prototype is the phase's gate | F-39, F-12, F-13, F-14, F-15, F-30, F-41, F-42, F-16 | Harness | none |
| **4 · Model steps** | OpenRouter client and caps, pre-check, AI copy and cut-out, draft check, same-photo tie-break, candidates; the phase's gate | F-17, F-18, F-19, F-21, F-43, F-11, F-55 | Harness | none (stubbed) |
| **5 · Pipeline and service** | Publishing, the per-teacher pipeline, queue and schedule, the API, decisions and requests, later runs, admin site, commands, the library stub; the offline end-to-end run is the phase's gate | F-24, F-23, F-25, F-44, F-45, F-48, F-46, F-22, F-05, F-26 | Harness | none |
| **6 · Live** | Smoke test on staging; the trial built, then run on staging; the winner written into the settings; the examples; the release, which is production's first deploy | F-27, F-28, F-52, F-50, F-29, F-47 | Harness, with the owner's veto on the control issue | ≤ $2 + ≤ $30 (trial, F-29 included) + ≤ $100 (first full run, in production) |

The project is done when AC-01..AC-06 in [../spec/requirements.md](../spec/requirements.md) are met.

## 2. Phase 0: planning tasks (in this chat)

| # | Task | Needs | State |
|---|---|---|---|
| P0-1 | Copy in Rev1's portrait files and the shared hosting review; reconcile every `tool` PORT line (requirements §10) | O-1 | **Waiting** for the library chat to push |
| P0-2 | The owner's decisions on the tracker topics | the owner | **Done** for T-01..T-23 (D-31..D-57), plus Q-27 and Q-28 (D-58, D-59) and Argon's two calls (D-60, D-61) |
| P0-3 | Style prototype (D-16) | O-2 | **Done:** recipe 0.4.0 accepted as the starting point (D-49); 0.5.0 (same look) re-measures the crop with the app's face detector. Per-operation references for the port in `prototype/parity/` |
| P0-4 | Trial set curation (TRI-02) | the coverage survey | **Moved into the build:** F-28 picks the set from F-38's report, with the owner's veto |
| P0-5 | Contract files | — | **Done:** `contracts/portraits-api.openapi.json` with samples and a check (D-44) |
| P0-6 | Review rounds by other AI tools, merged | P0-2 | **In progress:** Argon's round merged 2026-10-20; more if the owner runs them (`brain/reviews/`) |
| P0-7 | Freeze plan v1: the git tag `plan-v1`, and a status line telling the harness to start | P0-6, P0-8, the throwaway test passed | Later |
| P0-8 | Adapt to the harness (format 1, D-65): `harness.yaml`, the instruction files, this plan, and the cards (a sample first; the rest once the harness chat's `harness cards check` passes on it) | The harness's instructions (2026-10-20) | **In progress:** everything but the remaining cards done 2026-10-21. The sample in format 1 is F-01, F-51, F-04, F-36, F-49, F-53, F-31, F-07, F-38, F-54, F-55, F-23, F-27, F-28, F-52, F-50, F-29 and F-47 |

## 3. Inputs only the owner can supply

The harness reads the **Status** column: a card whose owner input isn't `done` is skipped, and the build goes on with the others. `withdrawn` inputs aren't needed by any card.

| ID | What | Needed by | Status | Notes |
|---|---|---|---|---|
| O-1 | Rev1's latest planning pushed to GitHub (the library chat), including `brain/reference/hosting-railway-review.md` and its portrait spec, so Claude can copy them into `brain/reference/rev1/` unchanged | P0-1 (**now**) | not done | Rev1 is readable here through GitHub (read-only). At 3e444eb (2026-10-18) it predates the library adopting this API |
| O-2 | The three hand-made portraits and their originals | P0-3 | done | 2026-10-19 (`design/portraits/`); sources unknown, so test use only (D-13) |
| O-3 | The teacher list. **Taken from library-pipeline's `authors.csv`** (D-22, D-45, read-only). The owner adds the dates and ids the tool suggests (from the admin page's CSV) in `authors.csv`, including its optional `wikidata_qid` and `lcnaf_id` columns (D-60) | Ongoing | done | The list exists; adding suggestions is ongoing |
| O-4 | The tool's one OpenRouter key (D-19, D-67), **set by the owner as a Railway variable in production and staging only**, never in pull-request copies, and given to the harness's secret store only if the harness chat says it needs it. **Its limit at OpenRouter, in steps** (D-67): $50 with no reset from the first live card; raised by $100 at the release; then $40 a month after the first pass (see the release checklist) | F-27 (the first live card) | not done | A key separate from other projects, so spend is easy to see. Never in chat or the repo |
| O-5 | ~~The delivery folder~~ (D-42: the library pulls through the API) | — | withdrawn | |
| O-6 | The Claude GitHub App installed on this repo (Q-20) | — | done | 2026-10-19 |
| O-7 | The harness, ready to run, with the throwaway test passed | Phase 1 | not done | Designed in its own chat (D-15) |
| O-8 | A Railway account (Hobby to start) with the project created, PR environments on, and the harness's conductor given a staging-deploy token and a production token, kept in the harness's store, outside the worker box (D-36, D-65) | F-36 | not done | After the throwaway test (`handoffs/harness-throwaway-test.md`) |
| O-9 | A read-only, fine-grained GitHub token for library-pipeline, limited to that repo's contents (D-32), set as the Railway variable `GITHUB_TOKEN` in staging (which pull-request copies take it from) and production | The smoke checks of F-31 and F-38; F-27 and F-52 | not done | Never in chat or the repo |
| O-10 | A contact email address for the tool's User-Agent (D-46), one meant for the app rather than a personal one | The recordings of F-07, F-08, F-09, F-10, F-34, F-35 and F-38; every check that calls a source on a deployed copy (F-38, F-27, F-52) | not done | Wikimedia's 2026 limits require it. Set as the variable `USER_AGENT_CONTACT` in Railway (staging and production) and in the harness's store (for recordings). It isn't a secret, but this way no one edits code to add it. Without it, a deployed copy starts but refuses calls to the sources; tests use a placeholder |
| O-11 | The library's key for this API, made by the owner once production is released (`portraits keys new`, run from the owner's PC), and handed to the library's settings (D-44) | The release checklist | not done | Not a card's input: F-47 doesn't wait for it |
| O-12 | Answer Q-27 (the zip, and the restated acceptance checks) | Before F-05 | done | 2026-10-20 (D-58) |
| O-13 | **Test credentials per environment** (RUN-10, RUN-11): an `OPS_KEY` for staging, pull-request copies and production, and, for staging and pull-request copies only, a `SEED_ADMIN_PASSWORD` and a `SEED_LIBRARY_KEY`. Each set as a Railway variable by the owner, and each given to the harness's secret store | F-49's smoke check (Phase 1), then every check that calls a deployed copy | not done | Random values, made by the owner (a password manager can make them). Production needs only its ops key, for later use; no check touches it. Never in chat or the repo |

## 4. Working with the harness (format 1; D-62..D-66)

The harness's own rules are in `../../Coding Harness Instructions.md` (from the harness chat). Its settings for this project are in `../../harness.yaml`. Where the two differ, the owner's decisions and this project's rules win, and the harness adapts.

**What a build session reads:** `CLAUDE.md` always, then what its packet names: the card, and the specs and contracts in its `Reads`.

**One card's path** (D-65)
1. **Pick** the next ready card: every card in its *Depends on* merged, its owner inputs `done` (§3), in the file's order.
2. **Tests first.** Gemini lists the cases; Codex writes the card's acceptance tests (`test/fNN-*.test.ts`, fixtures in `test/fixtures/fNN/`). Any recording named in `Test data` is made first, once, with network. The conductor checks the tests fail on the code as it stands, then locks them. F-01, the setup card, skips this step.
3. **Contract** for size L cards (F-23, F-28): Claude says how it will build and prove each check; Codex approves.
4. **Build:** Claude, in the worker box, on the card's branch, changing only the card's `Owns`. It may add its own unit tests and fakes.
5. **Check,** in a fresh box from the exact commit: `npm run check`, the card's tests, the full suite, `npm run build`, and a scan for gaming.
6. **Review:** Codex and Gemini, independently. P0 and P1 findings block.
7. **Smoke,** for cards with smoke checks: on the pull request's copy, with `npm run smoke -- --url {url}`. Phase 6's prove-it cards (F-27, F-52, F-29) say `staging only` in their side effects: their checks run on staging, which already has the code they test.
8. **Grade:** A only if every blocking check, both reviews and the smoke checks pass, for one commit. The conductor computes it.
9. **Merge at once** (D-62), with the evidence on the control issue (D-63). The merge deploys staging. The conductor runs the health check there (RUN-12); a failure rolls staging back and stops new cards until it's fixed.
10. **Record** the evidence, spend and lessons.

**Environments and the veto window** (D-66)
- **Pull-request copies:** stub mode, no AI key, no cron, seeded test credentials (RUN-10, O-13).
- **Staging:** Railway environment `staging`, deployed from `main` on every merge (`deploy.staging: on-merge`).
- **Production:** Railway environment `production`. Only the conductor promotes to it, with a production token kept outside the worker box. It promotes one exact release:
  - after a notice on the control issue, and only once **24 hours** have passed without a `/veto`;
  - the window restarts if the release changes;
  - it promotes only if it has read the control issue within the last 10 minutes.
- **Production is first deployed at the release, and only then.** No check touches production (the harness's rule), so everything live runs on staging first:
  1. **F-27** (smoke test, one real teacher), **F-52** (the trial) and **F-29** (the examples) start their jobs on staging over the web (RUN-11). They add no product code, so they test what's already merged and deployed there.
  2. **F-50** writes the trial's winner into the settings. It merges at once, with its notice on the control issue; `/veto` reverts it.
  3. **F-47, the release,** proves the release candidate on its deployed copy. The conductor then posts the promotion notice and, after the 24-hour window, promotes that commit to production. Production's schedule is on from that first deploy (RUN-08).
  4. **After the release,** production is promoted again only for a fix, each through its own window.
- **The owner's own path stays:** the owner can always deploy or roll back by hand in Railway (D-35).

**Never idle** (D-63). A question goes out as an alert on the control issue at once, and the harness carries on with every card it doesn't block. A card whose owner input is missing is skipped (§3).

**Stuck cards.** After the harness's rounds (the builder, then Codex, then Gemini, then the Tech Lead), a card marked *Parkable: yes* is parked. A card marked *Parkable: no* stops the build and alerts the owner. There are no soft dependencies: a card lists only the cards that must be merged first, so if a parkable card is parked, the cards that list it wait, and the others go on.

**When a spec or a test looks wrong,** the build agent stops and explains in `BLOCKED.md`. The Tech Lead rules, or asks the owner on the control issue.

**Never change, to make a check pass:**
- a *fixed* requirement;
- the API contract;
- the style rules.

**What the harness may write** (`notes_writable`):
- `brain/status.md`, its status lines;
- `brain/rulings.md`, the Tech Lead's rulings. A ruling is never an owner decision;
- `brain/gotchas/`, gotchas found while building.

Everything else in `brain/` is protected. **Recipe numbers** change only through the trial: F-50 writes them, with a `recipeVersion` bump.

**Keys and spend** (D-67)
- The app's OpenRouter key is a Railway variable in production and staging, set by the owner (O-4). Its limit at OpenRouter is the boundary; the caps in code are the second line.
- **Live checks start the app's own jobs over the web** (RUN-11), so the app spends with its own key, under its own caps. The harness reads the spend at `GET /api/ops/spend` for its own count.
- Test credentials per environment are in the harness's store (O-13). A check that needs one gets it in a fresh box with no agent running.
- The digest reports spend as three lines: the agents' usage, the app's paid calls, and hosting.

**Things the harness must not do here:** run project code with `railway run`; touch production from a check; deploy production outside the window.

## 5. Testing approach (D-09: features work reasonably well and without bugs)

*Rewritten 2026-10-20 for the TypeScript, hosted app (D-57, T-24). Proposed by Claude.*

- **One command:** `npm test` (`tsx --test`, Node's own test runner). It runs offline: the outbound client refuses all hosts in tests, and no keys are set. `npm run check` (`tsc`) and `npm run build` run beside it, as in the library.
- **The database in tests:** PGlite (Postgres compiled to WebAssembly, in-process). The same Drizzle migrations run against it, so tests need no database server. The PR copy's real Postgres is covered by the smoke tests.
- **Per-card checks:** each check on a card is a test named after the card, in a file named after it (`test/f12-crop.test.ts`), written first by the test author (Codex, D-65) and locked. So `npm test -- --test-name-pattern "F-12"` runs one card's checks. The builder may add its own unit tests, but never edits the locked ones.
- **Fixtures** for a card's acceptance tests go in `test/fixtures/fNN/`, made by the test author. Recordings of real responses are made by the command named in the card's `Test data`, run once by the harness with network before the tests are locked.
- **Fixtures:**
  - recorded responses from Wikidata, Commons, loc.gov, id.loc.gov and Wellcome, recorded once and committed;
  - canned model responses: JSON for the checks, and images for the AI copy (made from the prototype's synthetic keyed copies);
  - small images: synthetic ones generated in tests, the owner's three originals (test only, D-13), and a few public-domain images;
  - **the Python prototype's reference outputs** (`prototype/out/`, `prototype/fixtures/`). The TypeScript port must match them within the tolerances in `spec/architecture.md` (F-16);
  - **same-photograph pairs:** the prototype's doctored copies, plus the real pairs the coverage survey records (two sittings of one teacher included), for PIP-20;
  - an `authors.csv` sample.
- **API tests:**
  - **contract:** every route's answers in tests are validated with `ajv` against `contracts/portraits-api.openapi.json`, and the samples in `portraits-api.sample.json` must validate too;
  - **behaviour:** the library's flows are tested in-process against PGlite: pull the feed, fetch a portrait, send each decision and request, resend safely, key refused when off.
- **Smoke tests on deployed copies** (HT-26): `npm run smoke -- --url {url}`, against the PR copy (or staging, for Phase 6's prove-it cards), with that environment's test credentials (O-13). Over HTTP only. They're `test/fNN-*.smoke.ts`, which `npm test` never runs:
  - `/api/v1/health`;
  - 401 without the key and 200 with it;
  - one fixture teacher end to end in stub mode;
  - the admin page behind its login.
- **Live checks** make paid calls. They're marked `live` on their line, on cards whose `Side effects` allow paid calls (F-27, F-52, F-29, all on staging), under the caps (D-54, RUN-10). A check that only uses free public APIs is marked by the card's `Side effects: network`, not "live".
- **Not machine-tested:** whether a portrait looks good. The trial's board, the owner's veto and the library's approval judge that.
- **Not wanted:** coverage targets, evaluation suites, statistical scoring.

## 6. Spend plan

| Where | Paid by | Limit |
|---|---|---|
| Coding and reviewing during the build | The owner's subscriptions, through the harness | Subscription limits |
| The throwaway test | A separate low-limit OpenRouter key (HT-18) | ≤ $0.50 |
| F-27 live smoke test (one teacher) | The tool's OpenRouter key | ≤ $2 |
| F-52 trial on staging (three enhance models on about 23 originals) and F-29 (the examples, reusing the trial's cache) | The tool's key | $30 trial budget (D-54), as $27 + $3 sub-budgets; estimate about $11 |
| F-47 first full run | The tool's key | $100 cap (D-54); estimate $40–80 |
| After that | The tool's key | $10 a night, $30 a month (D-54) |
| Hosting | Railway | About $8–15 a month (T-01 notes) |

Fixture recording and the coverage survey use free public APIs, with a polite client (SRC-09).

## 7. After the build

- **F-47 is the release.** Production is first deployed after the 24-hour veto window, with its nightly schedule on. The owner works through the [release checklist](release-checklist.md): the key's limit at OpenRouter, the library's key (O-11), and watching the first pass over the nights it takes, under the $100 cap.
- **From then on**, it runs nightly (RUN-08):
  - the library pulls new portraits and sends its decisions back;
  - requests are handled at once;
  - teachers with open slots are searched again monthly.
- **Smithsonian** is added as a source only if the survey shows gaps (D-46).

## 8. Risks

| ID | Risk | What reduces it |
|---|---|---|
| R-1 | Matching the hand-made style is tuning by eye, which is hard for an unattended harness | The prototype settled the recipe in planning (D-49); F-16 locks the TypeScript port to the prototype's outputs |
| R-2 | ~~A model-drawn outline doesn't sit on the dots~~ | *Gone:* the outline is drawn by code (D-49) |
| R-3 | Few certain matches. Many teachers may have no Wikidata image, no depicts-tagged Commons file and no dated LoC record | Accepted: the rules are fixed. Finding ids (IN-13) opens more rules; the survey (F-38) measures coverage before money is spent; the library can paste links (`try_link`) |
| R-4 | Model ids, availability or prices change | Ids and prices live in settings; `doctor` checks them before a run |
| R-5 | The vision checker passes bad drafts or fails good ones | The library's approval is the final gate; the trial calibrates it; "compare with target" is tested on the examples |
| R-6 | Spend overruns | A cap check before every paid call (night, month, teacher, environment); the credit limit on the key (O-4); dry-run estimates |
| R-7 | This is the harness's first project | The throwaway test proves the harness on Railway first; small cards with offline checks; owner inputs listed up front; clear parking rules |
| R-8 | ~~Drive sync order, WSL mount quirks~~ | *Gone:* no Drive folder (D-42) |
| R-9 | Wikimedia or LoC rate limits or blocks (Wikimedia tightened its limits in 2026) | An identifying User-Agent, pacing to published limits and caching (SRC-09); tests replay recordings |
| R-10 | The AI-enhanced copy quietly changes a face | A 50% blend; alignment and the local drift check refuse moved features; likeness checked against the original; the board shows the no-blend version; the library's approval |
| R-11 | Two copies of one photograph kept as two portraits, or two photographs merged | PIP-20's three layers; thresholds checked on the survey's real pairs before relying on them; when unsure, the same (D-50); the library's approval |
| R-12 | Most active authors have no dates | IN-13 fills dates when Wikidata and the LoC name authority agree; the rest are listed for the owner |
| R-13 | **Porting the image steps to TypeScript** (D-57): an OpenCV.js function missing or behaving differently | A porting spike first (F-39), with a planned fallback for each known gap ([../spec/architecture.md](../spec/architecture.md)); parity with the Python prototype is a check (F-16) |
| R-14 | A source retires its API, as NYPL did on 1 August 2026 | Sources sit behind one interface; the survey shows what each contributes; losing one source doesn't stop the others |
| R-15 | The library isn't ready to pull when the tool is | A seeded staging copy and the library stub (F-05) prove the API on its own; the contract is versioned and additive |
