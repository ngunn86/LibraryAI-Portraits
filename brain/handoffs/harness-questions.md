# For the harness chat: what the portraits plan did with your instructions, and its questions

**From:** Nexus Portraits planning, 2026-10-21. **For:** the Coding Harness chat, relayed by the owner.
**About:** `Coding Harness Instructions.md` (harness plan `68dee18`, the checklist at `a2a5ce5`).

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
- **No `railway run`:** the app now has **jobs started over the web** (RUN-11): `POST /api/ops/jobs`, `GET /api/ops/jobs/{id}` and `GET /api/ops/spend`, behind a per-environment ops key (O-13). The survey, the trial, the live smoke test and the fixture seed all run that way.
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

1. **Shared test fixtures.** Several cards' tests reuse an earlier card's fixtures: F-04's PGlite helper (almost everything after it), F-03's contract validator (the API cards), and F-23's stub world (F-25, F-26, F-48). May a later card's acceptance tests import from an earlier card's `test/fixtures/fNN/`, read-only? If not, where should shared helpers live?
2. **The AI key.** Live checks start the app's own jobs over the web, so the app spends with its own key (a Railway variable), under its own caps, and the harness never needs to hold the key. The harness can count spend from `GET /api/ops/spend`. Does `limits.paid_calls.openrouter` work as a count like this, or must the harness hold the key itself?
3. **Credentials for recordings and smoke checks.**
   - F-50's recording fetches the trial's result from staging's ops API, with staging's ops key (O-13). Will the harness give an environment's test credentials to a `record:` command?
   - Under what names does the harness pass test credentials to `npm run smoke`? We'd use `PORTRAITS_URL`, `PORTRAITS_OPS_KEY`, `PORTRAITS_TEST_LIBRARY_KEY` and `PORTRAITS_TEST_ADMIN_PASSWORD` unless you name others.
4. **Checks on staging.** F-27, F-52 and F-29 are prove-it cards with no product code. Their checks run against staging, which already has the code they test, before they merge. Their `Side effects` say `staging only`. Is that how the harness should place them, given `pr_copies: true`?
5. **When production is promoted.** We want production touched only at the release (F-47), and later for fixes, never after every merge. With `deploy.production: { mode: veto-window }`, does the conductor promote after every merge? If so, how should a card mark itself as a release: a field, a check, or `/approve`?
6. **Field values.**
   - F-47's `Side effects` use `production` (the conductor's promotion after the window). Is that an accepted value, or should it be written another way?
   - Gate cards use `Covers: none (a gate)` and `Owns: none`. Is that all right?
   - The setup card's checks are commands (`npm ci`, `npm run check`, …). Is that all right?
7. **Pull-request copies without the AI key** (HT-32). The portraits app keeps one key (D-67) but gives it only to production and staging. Railway's pull-request environments may copy every variable from their base environment. The throwaway test should show how to keep the key out of them.
