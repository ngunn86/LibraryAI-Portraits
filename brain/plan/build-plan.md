# Build plan

**Status (2026-10-20):** proposed by Claude, rewritten for the hosted TypeScript app (D-31..D-57). It waits for the review rounds (P0-6) and for Q-27.

## 1. The shape of the work

| Phase | What | Cards | Who | Paid AI spend (tool key) |
|---|---|---|---|---|
| **0 · Planning** | Notes, decisions, API contract, style prototype, reviews | — | Claude with the owner; other AI tools review | none |
| **— · Harness proof** | The throwaway app: build, deploy, test and tear down on Railway ([../handoffs/harness-throwaway-test.md](../handoffs/harness-throwaway-test.md)) | HT-01..HT-29 | Harness (planned in its own chat) | ≤ $0.50 |
| **1 · Foundation and deploys** | Skeleton, API contract in code, database and queue, bucket, Railway setup with staging and PR copies | F-01, F-03, F-04, F-37, F-36 | Harness | none |
| **2 · Teachers and sources** | The authors list, the outbound client, licences, rights log, Wikidata, Commons, LoC, Wellcome, finding ids, the coverage survey | F-02, F-06, F-31, F-07, F-32, F-08, F-09, F-10, F-34, F-35, F-38 | Harness | none (free public APIs) |
| **3 · Imaging (ported from the Python prototype)** | Porting spike, face and crop, descreen, halftone, mask and outline, blend, versions, same-photo check, parity with the prototype | F-39, F-12, F-13, F-14, F-15, F-30, F-41, F-42, F-16 | Harness | none |
| **4 · Model steps** | OpenRouter client and caps, pre-check, AI copy and cut-out, draft check, same-photo tie-break, candidates | F-17, F-18, F-19, F-21, F-43, F-11 | Harness | none (stubbed) |
| **5 · Pipeline and service** | Publishing, the per-teacher pipeline, queue and schedule, the API, decisions and requests, later runs, admin site, commands, the library stub, the offline end-to-end run | F-24, F-23, F-25, F-44, F-45, F-48, F-46, F-22, F-05, F-26 | Harness | none |
| **6 · Live** | Smoke test on staging; the trial and its board, and the examples, in production before the release (schedule off, no library key); production release and first nightly run | F-27, F-28, F-29, F-47 | Harness, with the owner's veto | ≤ $2 + ≤ $30 (trial, F-29 included) + ≤ $100 (first full run) |

The project is done when AC-01..AC-06 in [../spec/requirements.md](../spec/requirements.md) are met.

## 2. Phase 0: planning tasks (in this chat)

| # | Task | Needs | State |
|---|---|---|---|
| P0-1 | Copy in Rev1's portrait files and the shared hosting review; reconcile every `tool` PORT line (requirements §10) | O-1 | **Waiting** for the library chat to push |
| P0-2 | The owner's decisions on the tracker topics | the owner | **Done** for T-01..T-23 (D-31..D-57); Q-27 open |
| P0-3 | Style prototype (D-16) | O-2 | **Done:** recipe 0.4.0 accepted as the starting point (D-49) |
| P0-4 | Trial set curation (TRI-02) | the coverage survey | **Moved into the build:** F-28 picks the set from F-38's report, with the owner's veto |
| P0-5 | Contract files | — | **Done:** `contracts/portraits-api.openapi.json` with samples and a check (D-44) |
| P0-6 | Review rounds by other AI tools, merged | P0-2 | **Next** (2026-10-20 onwards; `brain/reviews/`) |
| P0-7 | Freeze plan v1: the git tag `plan-v1`, and a status line telling the harness to start | P0-6, Q-27, the harness's card format (D-15), the throwaway test passed | Later |

## 3. Inputs only the owner can supply

| ID | What | Needed by | Notes |
|---|---|---|---|
| O-1 | Rev1's latest planning pushed to GitHub (the library chat), including `brain/reference/hosting-railway-review.md` and its portrait spec, so Claude can copy them into `brain/reference/rev1/` unchanged | P0-1 (**now**) | Rev1 is readable here through GitHub (read-only). At 3e444eb (2026-10-18) it predates the library adopting this API |
| O-2 | The three hand-made portraits and their originals | P0-3 | **Done 2026-10-19** (`design/portraits/`); sources unknown, so test use only (D-13) |
| O-3 | The teacher list. **Taken from library-pipeline's `authors.csv`** (D-22, D-45, read-only). The owner adds the dates and Wikidata ids the tool suggests (from the admin page's CSV) in `authors.csv` | Ongoing | |
| O-4 | The tool's own OpenRouter key, set as a Railway variable (per environment). It is the only AI key (D-19). Never in chat or the repo. **Set a credit limit on the key at OpenRouter** as a backstop (D-54) | The first live feature | A key separate from other projects, so spend is easy to see |
| O-5 | ~~The delivery folder~~ *withdrawn* (D-42: the library pulls through the API) | — | |
| O-6 | The Claude GitHub App installed on this repo (Q-20) | — | **Done 2026-10-19** |
| O-7 | The harness, ready to run | Phase 1 | Designed in a separate chat (D-15) |
| O-8 | A Railway account (Hobby to start) with the project created, and the harness given deploy access (D-36) | Phase 1 | After the throwaway test (`handoffs/harness-throwaway-test.md`) |
| O-9 | A read-only, fine-grained GitHub token for library-pipeline, limited to that repo's contents (D-32), set as a Railway variable | The teacher sync | Never in chat or the repo |
| O-10 | A contact email address for the tool's User-Agent (D-46), one meant for the app rather than a personal one | The source clients | Wikimedia's 2026 limits require it |
| O-11 | The library's key for this API, made by the owner once the API is deployed (`portraits keys new`), and handed to the library's settings (D-44) | F-47 | |
| O-12 | Answer Q-27 (the zip, and the restated acceptance checks) | Before F-05 | |

## 4. Working with the harness

*Provisional until the harness, designed in its own chat (D-15), settles its format. This section and the card format in `features.md` are this project's interface to it.*

**What the harness reads**
- `CLAUDE.md`, for the rules.
- [features.md](features.md), the cards in build order, each in a fixed field format.
- [../spec/requirements.md](../spec/requirements.md) and [../spec/architecture.md](../spec/architecture.md), for anything a card cites.
- [../contracts/portraits-api.openapi.json](../contracts/portraits-api.openapi.json), the API it must serve unchanged.

**Per feature (as the owner has described the harness, D-12)**

1. Build the feature on its own branch.
2. **Run the checks:**
   - the feature's own: `npm test -- --test-name-pattern "F-NN"`;
   - then everything: `npm run check && npm test && npm run build`.
3. Push, so Railway makes the pull request's copy. Run the card's smoke checks against it where the card has any (HT-26).
4. A second and a third model review it. An "A" grade means every check passes across models.
5. Merge to staging. Production changes only after the owner's veto window, announced in the digest (HT-05).
6. Add a line to the digest.

**Blocked features.** A card needing an owner input (O-n) that isn't there is skipped. The harness goes on with features that don't depend on it, and the digest says what is waiting and on what.

**Live features** (F-27, F-28, F-29, F-38, F-47) run only with the keys present and only through the tool's own caps. The digest reports what each spent.

**Parking.** A stuck feature may be parked only if its card says *Parkable: yes*. Features that depend on it then wait. A stuck feature marked *Parkable: no* stops the build and goes to the digest.

**Never change, to make a check pass:**
- a *fixed* requirement;
- the API contract;
- the style rules.

**Recipe numbers** come from the prototype and the trial. The harness may change them only through the trial (TRI-06), always with a `recipeVersion` bump.

## 5. Testing approach (D-09: features work reasonably well and without bugs)

*Rewritten 2026-10-20 for the TypeScript, hosted app (D-57, T-24). Proposed by Claude.*

- **One command:** `npm test` (`tsx --test`, Node's own test runner). It runs offline: the outbound client refuses all hosts in tests, and no keys are set. `npm run check` (`tsc`) and `npm run build` run beside it, as in the library.
- **The database in tests:** PGlite (Postgres compiled to WebAssembly, in-process). The same Drizzle migrations run against it, so tests need no database server. The PR copy's real Postgres is covered by the smoke tests.
- **Per-feature checks:** every check on a card is a test named after the feature, in a file named after it (`test/f12-crop.test.ts`). So `npm test -- --test-name-pattern=F-12` runs one feature's checks.
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
- **Smoke tests on deployed copies** (HT-26): against the PR copy, then staging:
  - `/api/v1/health`;
  - 401 without the key and 200 with it;
  - one fixture teacher end to end in stub mode;
  - the admin page behind its login.
- **Live tests** run only on cards marked *live* (the coverage survey, the trial, the first run), under the caps (D-54, RUN-10), with `PORTRAITS_LIVE=1`.
- **Not machine-tested:** whether a portrait looks good. The trial's board, the owner's veto and the library's approval judge that.
- **Not wanted:** coverage targets, evaluation suites, statistical scoring.

## 6. Spend plan

| Where | Paid by | Limit |
|---|---|---|
| Coding and reviewing during the build | The owner's subscriptions, through the harness | Subscription limits |
| The throwaway test | A separate low-limit OpenRouter key (HT-18) | ≤ $0.50 |
| F-27 live smoke test (one teacher) | The tool's OpenRouter key | ≤ $2 |
| F-28 trial (three enhance models on about 23 originals) and F-29 (the examples, reusing the trial's cache) | The tool's key | $30 trial budget (D-54), as $27 + $3 sub-budgets; estimate about $11 |
| F-47 first full run | The tool's key | $100 cap (D-54); estimate $40–80 |
| After that | The tool's key | $10 a night, $30 a month (D-54) |
| Hosting | Railway | About $8–15 a month (T-01 notes) |

Fixture recording and the coverage survey use free public APIs, with a polite client (SRC-09).

## 7. After the build

- **F-47 is the release.** Production is deployed after the owner's veto window. The owner makes the library's key (O-11), and the first nightly run works through the list under the $100 cap, over as many nights as it needs.
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
