# For the harness chat: what the portraits plan did with your instructions, and its questions

**From:** Nexus Portraits planning, 2026-10-21; updated 2026-10-22 and 2026-10-23 (twice). **For:** the Coding Harness chat, relayed by the owner.
**About:** `Coding Harness Instructions.md`: first as of harness plan `68dee18`, then as updated to HD-59 (commits `2e2b073` and `3e16ff8`), then to HD-60 (commit `c6d0199`, the move to Northflank), then to HD-65 (commit `066b394`, your answers and the card check).

## Update, 2026-10-23 (later): all cards converted, and your answers applied

Thank you for the answers (HD-65). Recorded here as **D-71**.
- **All 52 cards are in format 1** (`brain/plan/features.md`, draft 5). `harness cards check` on this commit reads every card: "All good", with only the three notes about protected paths named in `Owns` (F-01 `tsconfig.json`, F-03 `contracts/`, F-36 `northflank/`) and `digest.issue`.
- **F-47's Side effects** now say `deploy (pull-request copies); production (promoted by the conductor after the 24-hour window, D-66); external write (the seed, on the deployed copy)`. Its Goal says the release notice names the first `northflank/production.json` run.
- **`harness.yaml`:** `limits.paid_calls.openrouter.spend: /api/ops/spend`.
- **Credentials:** the smoke script, F-49's `record-ops` and F-05's library stub read `PORTRAITS_OPS_KEY`, `PORTRAITS_TEST_LIBRARY_KEY`, `PORTRAITS_TEST_ADMIN_PASSWORD`, and `HARNESS_URL` when no `--url` is given. F-50's recording is `npm run record-ops -- F-50 --kind trial --url {url}`.
- **Shared fixtures:** the cards' header says later cards may import earlier cards' fixtures read-only; reusable helpers are in the product (`openTestDb`, `checkAgainstContract`, `createStubModelClient`, `createFakeBucket`).
- **One thing to tell you:** your instructions (§5) say `package.json` "may be owned by any card that adds a dependency", but `harness cards check` flags two such cards as a clash unless one depends on the other (it gave 23 ✗ lines for that on our first try). We made F-01 the only owner: it installs every package in the architecture's list and names every npm script. Either the checker or the instructions may want changing; we're fine as we are.

## Update, 2026-10-23: the move to Northflank is done here

Your "Hosting change" section (HD-60) is applied. Recorded as **D-70**, the owner's decision, superseding D-36.
- **`harness.yaml`:** `deploy.host: northflank`; `northflank/` (the templates F-36 makes) replaces `.railway/` among the protected paths. `deploy.starts_at` is F-36, as before.
- **Your checklist items:**
  - **no project code through the host's command line:** already so since 2026-10-21 (jobs over the web, RUN-11). The owner's own commands now run in a shell on the web service from Northflank's dashboard, and nothing reaches the database from outside Northflank;
  - **O-4:** the owner sets every secret in Northflank's secret groups (one per environment: production, staging, preview); the harness keeps its own copies of the test credentials (O-13) in its store, and the AI key only if you need it (question 2);
  - **HT-23:** reworded: the conductor reads logs and deploy status through Northflank's API; no host MCP server.
- **The plan's Northflank layout** (architecture, RUN-01, RUN-10, RUN-12, F-36):
  - the staging project: a pipeline whose release flow builds, migrates and deploys `main` on each merge; a preview template for pull-request copies (own empty Postgres, migrated by a `migrate` job, with test credentials seeded at start-up; the preview secret group, **which has no AI key**; at most 3 days);
  - the production project: **empty until the release.** Its template (`northflank/production.json`) is run once at the release, creating its services, Postgres, cron job and a release flow that builds a given commit, backs up the database, migrates and deploys; that flow is started by the conductor with the production token after the 24-hour window, or by the owner in the dashboard;
  - **the preview group holds its own test credentials,** not staging's (your §7 says copies get staging's): a pull request's code then can't use staging's ops key to start paid jobs on staging. So the harness keeps three sets: production's ops key, staging's, and the previews';
  - the templates are applied from the repo one way, so a dashboard edit never commits to `main` under a running card;
  - readiness is `/api/v1/health` (`deploy.health`), and liveness a new `/api/v1/live` that checks only the process (contract draft 8);
  - the environment's name comes from the app's own `PORTRAITS_ENV` (`production`, `staging` or `preview`);
  - **files on Cloudflare R2:** three buckets (production, staging, previews), one token each limited to its bucket; each pull-request copy writes under its own prefix in the previews bucket, which deletes objects after 7 days. New owner input **O-14**.
- **The throwaway test:** every Railway note is now Northflank's; **HT-32 is tightened** (a copy must lack the AI key, since secret groups make that possible) and **HT-33 is added** (the staging token can't reach production; production builds and deploys exactly the commit it's given).
- **Questions 8 to 12** below are new; 7 is settled by the move. *(All twelve answered in HD-65; see the update above.)*

## Update, 2026-10-22: your latest instructions are merged

- **A note on the repo.** Your updates of 2026-10-21 and 2026-10-22 were written on the owner's PC, whose copy of the repo didn't yet have this project's two adaptation commits (`9731286`, `1de146f`, on GitHub since 2026-10-21). So your checklist still points at `a2a5ce5`, and lists as to-do several things already done below. Your two commits are now merged into `main` (merge `c470de7` and the commit after it), so the owner's PC fast-forwards when it pulls. From now on, please read the plan from `main`.
- **Your new items, all done:**
  - **one card's tests run by path, printing TAP:** `harness.yaml`'s `test_card`, the build plan and the cards. `test_count` is removed;
  - **unique test case names** starting with the card's ID, and tests that must fail for the right reason before they're locked;
  - **what each card creates** is in the `Goal` of every converted card. The other 34 get it when they're converted;
  - **contracts before tests** on size L cards (F-23, F-28);
  - **fast-forward merges,** and planning pushes batched between cards where possible;
  - **`deploy.starts_at: F-36`**, the card that makes the app deployable with its health endpoint;
  - **pull-request copies based on staging, never production,** and a health check that names its environment, database and bucket (RUN-10, RUN-12, contract draft 7, HT-32);
  - **soft per-card caps** (recorded as D-69); **24 hours** (D-66 already, now with your HD-59 quote); **one key** (D-67, with your HD-50 quote);
  - **library-pipeline on a second PC** during a build (D-64).
- **Questions 1 to 7 below are still open.** Question 2 now has an extra point: section 8 says checks "use the key directly", while here the live checks start the app's own jobs, which use the app's key. Is that all right?

## What's done

Everything in the checklist (§9), except converting the last 34 cards, which waits for your `harness cards check` on the sample.

- **Decisions:** your HD-40..HD-44 are recorded as the owner's (D-62..D-64), and the new way of building as D-65. The owner also decided, in this chat:
  - **D-66:** a **24-hour** veto window;
  - **D-67:** **keep one OpenRouter key**, for production and staging, with its limit at OpenRouter set in steps by the owner. Pull-request copies don't get the key;
  - **D-68:** the admin site gets a front page.
- **`harness.yaml`** is at the repo root (format 1). Left as TODO: the control issue's number.
- **Instruction files:** CLAUDE.md, AGENTS.md and GEMINI.md have the build-agent carve-out, and `BLOCKED.md` replaces "raise it".
- **Build plan** (`brain/plan/build-plan.md` §3–5):
  - the card loop with tests first, merging at once, and the control issue;
  - environments and the veto window's rules;
  - owner inputs with a **Status** column (`done`, `not done`, `withdrawn`);
  - what the harness may write: `brain/status.md`, `brain/rulings.md` and `brain/gotchas/`.
- **No project code through the host's command line** (it was `railway run`): the app now has **jobs started over the web** (RUN-11): `POST /api/ops/jobs`, `GET /api/ops/jobs/{id}` and `GET /api/ops/spend`, behind a per-environment ops key (O-13). The survey, the trial, the live smoke test and the fixture seed all run that way.
- **Health** (RUN-12, contract draft 6): 200 only when the database, the bucket and the image libraries work, otherwise 503. Migrations are additive from the first staging deploy.
- **No check touches production.** So the trial moved to staging, and **production's first deploy is the release** (F-47), after the 24-hour window, with its nightly schedule on from then. There is no separate switch-on.
- **Multi-night checks** moved to the owner's release checklist (`brain/plan/release-checklist.md`).
- **The throwaway test** is updated: HT-01, HT-05, HT-08, HT-09, HT-22, HT-26..HT-28 reworded, HT-23 withdrawn, and HT-30..HT-32 added (a veto reverting a merge, a failed health check rolling staging back, and pull-request copies without the AI key).
- **Cards** (`brain/plan/features.md`, draft 4):
  - soft dependencies are gone;
  - new cards: F-51 (settings and secrets, split from the setup card), F-49 (jobs over the web), F-52 (running the trial on staging), F-50 (writing the trial's winner into the settings), and gate cards F-53, F-54 and F-55. F-16, F-26 and F-47 are the other phases' gates;
  - shared files are avoided by one-file-per-item folders for commands, jobs, admin pages and sources.
- **Housekeeping:** the duplicate `Argon Notes.md` copies are removed; the merged review is `brain/reviews/2026-10-20-argon-round-2.md`.

## The sample for `harness cards check`

18 cards in format 1 (headings with a colon), one of each awkward kind:

| Kind | Cards |
|---|---|
| The setup card | F-01 |
| Settings | F-51 |
| Migrations | F-04 |
| Deploys, health and smoke | F-36 |
| Jobs over the web | F-49 |
| Gates | F-53, F-54, F-55, F-47 |
| A smoke check that needs an owner input | F-31 |
| A recording that needs O-10 | F-07, F-38 |
| A large card with stubs | F-23 |
| Prove-it, live, on staging | F-27, F-52, F-29 |
| A large card built offline | F-28 |
| A recording from staging | F-50 |
| The release | F-47 |

## Questions

*All answered by the harness chat on 2026-10-23 (HD-65), recorded as D-71.*

1. **Shared test fixtures.** Several cards' tests reuse an earlier card's fixtures: F-04's PGlite helper (almost everything after it), F-03's contract validator (the API cards), and F-23's stub world (F-25, F-26, F-48). May a later card's acceptance tests import from an earlier card's `test/fixtures/fNN/`, read-only? If not, where should shared helpers live?
2. **The AI key.** Live checks start the app's own jobs over the web, so the app spends with its own key (a secret in the app's environment), under its own caps, and the harness never needs to hold the key. The harness can count spend from `GET /api/ops/spend`. Does `limits.paid_calls.openrouter` work as a count like this, or must the harness hold the key itself?
3. **Credentials for recordings and smoke checks.**
   - F-50's recording (`npm run record-ops -- F-50 --kind trial`) fetches the trial's result from staging's ops API, with staging's ops key (O-13). Will the harness give a `record:` command an environment's address and test credentials, and under what names?
   - Under what names does the harness pass test credentials to `npm run smoke`? We'd use `PORTRAITS_URL`, `PORTRAITS_OPS_KEY`, `PORTRAITS_TEST_LIBRARY_KEY` and `PORTRAITS_TEST_ADMIN_PASSWORD` unless you name others.
4. **Checks on staging.** F-27, F-52 and F-29 are prove-it cards with no product code. Their checks run against staging, which already has the code they test, before they merge. Their `Side effects` say `staging only`. Is that how the harness should place them, given `pr_copies: true`?
5. **When production is promoted.** We want production touched only at the release (F-47), and later for fixes, never after every merge. With `deploy.production: { mode: veto-window }`, does the conductor promote after every merge? If it does, and a card can't be marked as a release, we'd switch to `owner-promotes`, with the owner's `/approve` for the release and the 24-hour window as the owner's own habit. That would be the owner's call.
6. **Field values.**
   - F-47's `Side effects` say `deploy (pull-request copies; and production, promoted by the conductor after the 24-hour window)`. Is that how a release card should say it?
   - Gate cards and prove-it cards use `Covers: none` or `Owns: none`. Is that all right?
   - Smoke tests are named `test/fNN-*.smoke.ts`, and `acceptance_tests` is `test/{slug}-*`, so the test author writes both kinds and `npm test` runs only `*.test.ts`. Is a pattern without a file extension all right?
   - The setup card's checks are commands (`npm ci`, `npm run check`, …). Is that all right?
7. ~~**Pull-request copies without the AI key** (HT-32).~~ *Settled by the move to Northflank (2026-10-23):* the preview template links only the preview secret group, which doesn't hold the key, and HT-32 now requires that.
8. **Production builds its own image.** A Northflank pipeline can't span two projects, so production's release flow builds the promoted commit itself, from the same commit and lockfile, then backs up the database, migrates and deploys. Can the conductor start a release flow through Northflank's API with the commit as its argument? If not, the conductor would move a `production` branch that production's build follows. Which suits the harness (HT-33)? And at the release, can the conductor first run `northflank/production.json` once to create the production project's services, or should that be an owner step?
9. **Files on Cloudflare R2,** not the MinIO add-on: three buckets with a token each, and pull-request copies under their own prefix in the previews bucket, which R2 empties after 7 days. So the daily clean-up has nothing to delete in the bucket. Does that fit HT-13 and the clean-up?
10. **Preview databases start empty,** migrated by the `migrate` job, with the test credentials seeded at start-up, rather than forked from staging's latest backup, so nothing real reaches a test copy. Is that all right? And are three sets of test credentials (production, staging, previews) fine?
11. **The preview lifetime** is set to 3 days in the template. Does the harness have a default we should match?
12. **Liveness.** `deploy.health` is the readiness check, `/api/v1/health`. The liveness check is `/api/v1/live`, set in the templates. Does `harness.yaml` need to name it too?
