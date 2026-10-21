# Coding Harness Instructions: the portraits tool

**From:** the Coding Harness chat · **Date:** 2026-10-20 · **For:** this repo's planning chat
**Harness plan:** `ngunn86/Coding-Harness` at commit `68dee18`. That repo is private, so this file is complete on its own.
**Placed here** at the owner's request (harness decision HD-47). It's the only file the harness chat writes in this repo; commit it with your next planning round. When the harness's requirements change, the harness chat updates this file and says so at the top.

## 1. What this file is, and how to use it

The Coding Harness will build this project, right after its throwaway test app (HT-01 to HT-29, specified in this repo) and before Library-AI Rev1. This file lists everything this project's planning needs to change or add so the harness can build it unattended.

- **Section 3 holds owner decisions** made in the harness chat. Record them in your Decisions as the owner's, with their quotes.
- **Everything else is what the harness requires.** Write it into your notes your own way, under your own rules, status words and IDs.
- **Section 9 is your checklist,** with file and line references as of commit `a2a5ce5`. Lines drift, so each item quotes enough text to find it.
- **When you're done,** tell the owner. The harness chat will then run `harness cards check` on a sample of your cards and send back anything it finds. Convert the rest of the cards after that.
- **Questions about the harness itself** go to the owner, who brings them to the harness chat. Don't change the harness's rules here. Where the two disagree, the owner's decisions and this project's own rules win, and the harness adapts.

## 2. How the harness will build this project

The harness is a script on the owner's PC (Windows, WSL Ubuntu) that builds a project one work card at a time, unattended, on the owner's subscriptions (Claude Max, ChatGPT, Google AI Ultra), never API billing for its agents. Its plan lives in the private repo `ngunn86/Coding-Harness`; this file carries everything a project needs from it, so you don't need that repo.

**Who does what**

| Role | Model | What it does |
|---|---|---|
| Test advisor | Gemini (Argon, if available), read-only | Lists the cases a card's tests must cover |
| Test author | Codex (GPT-6.1 Sol), test files only | Writes the card's acceptance tests before any code |
| Builder | Claude Opus 5.5 | Writes the product's code. The only role that does |
| Reviewers | Codex and Gemini, read-only | Review the same commit independently; Gemini also tries screens in a browser |
| Verifier | a family other than the phase's builder, test files only | At each phase boundary, adds one to three tests chosen by risk |
| Tech Lead | Claude Opus 5.5, maximum effort | Makes judgment calls from a fixed menu, and logs each ruling |
| Conductor | no model: ordinary code | Picks cards, runs checks, computes the grade, pushes, merges and deploys |

**One card's path**

1. **Pick** the next ready card: dependencies done, owner inputs present, in the file's order.
2. **Tests first.** Gemini lists the cases the tests must cover. Codex writes the card's acceptance tests from the card, its specs and that list. The conductor checks they fail on the code as it stands (so they test something real), then locks them for the card.
3. **Contract** (size L cards only). The builder says how it will build the card and prove each check; Codex approves or asks for changes.
4. **Build.** Claude works on the card's branch in a fresh session, inside the worker box (below), and may add its own tests.
5. **Check,** in a fresh box from the exact commit: the project's `check`, the card's tests, the full suite, `build`, and a scan for gaming (skipped or deleted tests, swallowed errors, hard-coded answers). A check that runs no tests fails.
6. **Review.** Codex and Gemini review the same commit and return structured verdicts. P0 and P1 findings block; P2 and P3 go to a backlog.
7. **Deploy and smoke,** for cards with smoke checks: on the pull-request copy where the project uses them, otherwise on staging before the merge.
8. **Grade.** A only if every blocking check, both reviews and the smoke checks pass, all for the same commit. No model can award it.
9. **Merge** that commit only, as soon as it passes, with its evidence posted on the project's control issue at once. The owner's veto reverts it.
10. **Record** the evidence, spend and lessons.

**When a card is stuck:** rounds 1 and 2, the builder fixes the findings; round 3, Codex diagnoses and writes a fix plan, which Claude applies; round 4, Gemini does the same; then the Tech Lead, up to twice. Then a `Parkable: yes` card is parked, and retried only when something it depends on changes (at most twice); a `Parkable: no` card stops the build and alerts the owner at once. A missing or malformed review is no sign-off, and another model never stands in for it. A builder that finds a spec or test wrong stops and explains in `BLOCKED.md`; the Tech Lead rules or asks the owner. A test shown to be wrong is rewritten by the test author, the change is logged, and the card's earlier evidence is void. A change pushed to a card, or to the specs it reads, while the card is running also voids its evidence.

**The worker box.** The agents, and all of the project's own commands (install, tests, build, the dev server), run inside a Docker container that holds only the card's working copy, the agents' logins and the test services. It has no GitHub or Railway credentials, no Windows drives and no Docker socket. Test services such as a database run as separate containers that the harness starts. So nothing in the project may depend on Windows paths, on the owner's own logins, or on tools that aren't installed by the project's `install` command or named in its setup.

**Build agents and your instruction files.** Claude Code, Codex and Gemini each load the project's own instruction file by themselves (`CLAUDE.md`, `AGENTS.md`, `GEMINI.md`). The harness's prompt tells each one it's a build agent: it reads what its packet names, changes only its card's `Owns`, never edits the notes, and skips the planning chats' "read first" and "update before you finish" lists. Add a short section saying the same to each of those files (wording in the checklist below), so the two never pull against each other.

**What wins.** The owner's decisions and the project's own rules win over the harness's policy, and the Tech Lead rules only within them.

## 3. Owner decisions that affect this project

Made in the harness chat; IDs are the harness's (`HD-`).

- **Merge right away** (HD-44, 2026-10-20): "Merge the cards right away, yes." A card merges as soon as its blocking checks pass, with its evidence posted on the control issue at once; the morning digest is only a summary; the owner's veto still reverts a merge. This replaces "merges when its blocking checks pass and the digest has gone out".
- **Phone control through GitHub** (HD-42, 2026-10-20): each project's repo gets one GitHub issue, the **control issue**. The owner steers by replying there, from the GitHub app or by email reply: `/status`, `/pause` (after the current step), `/stop` (now), `/resume`, `/approve <id>`, `/veto <id>`, and `/direct <plain words>`, which the Tech Lead reads but which can't raise a budget or a permission. The harness reads the issue every 2 minutes and accepts commands only from the owner's GitHub account. ntfy push alerts notify at once and link to the issue. Remote Control chat is optional, not part of the control path.
- **Never idle waiting for the owner** (HD-42, HR-57): a question goes out as an alert at once, and the harness carries on with every card the question doesn't block.
- **Authorizations** the owner keeps (email to a real address other than the owner's, a production deploy or switch-over, deleting production data, spend above a cap, new keys or accounts, anything irreversible outside the repo) are asked on the control issue with an instant alert, naming the exact action and reason, not in the digest.
- **No usage reserve** (HD-41): the harness uses each plan until the tool stops it, including any extra usage the owner turns on, then waits for the reset.
- **The PC is dedicated to the build while it runs** (HD-40): library-pipeline doesn't run then.

## 4. `harness.yaml`, format 1

Put `harness.yaml` at the repo root. Format 1 is settled, so it can be written now; field names won't change without a new format number.

| Field | What it says |
|---|---|
| `format` | `1` |
| `project` | the project's short name |
| `cards` | path to the cards file (or files) |
| `always_read` | the file every session reads first (`CLAUDE.md` or `AGENTS.md`) |
| `protected` | paths agents may never change: notes, specs, cards, contracts, acceptance and held-back tests, CI settings, design boards. The harness also protects the files that say how checks run (the test scripts in `package.json` and the test runner's settings). A card may change a protected path only if it names it in `Owns` (a setup card, for example) |
| `owner_inputs` | the file listing the owner's inputs, each with an ID (such as `O-4`) and a status the harness can read (done or not), so a card whose input is missing is skipped |
| `notes_writable` | the files or folders the harness may write to: for example the status page and a gotcha notes folder. It writes nowhere else, and its own writes there never void a card's evidence |
| `rulings` | the file where the Tech Lead's rulings are logged (for example `brain/rulings.md`); a ruling is never an owner decision |
| `held_back` | tests or test data kept out of the worker box until the check step, so the builder never sees them |
| `acceptance_tests` | where the test author writes each card's acceptance tests, as a pattern: `{card}` is the card ID as written, `{slug}` the same in lower case without the dash (F-07 becomes `f07`), e.g. `test/{slug}-*.test.ts` |
| `acceptance_fixtures` | where their fixtures and recordings go, e.g. `test/fixtures/{slug}/` |
| `box.apt` | system packages the worker box needs beyond the harness's base image (Node 24, git, the three agent CLIs, Playwright's Chromium), e.g. `[qpdf, tesseract-ocr, python3-jsonschema]` |
| `commands.install` | e.g. `npm ci` |
| `commands.check` | type-check and lint, e.g. `npm run check` |
| `commands.test` | the full suite |
| `commands.test_card` | one card's tests, with `{card}` for its ID |
| `commands.build` | the production build |
| `commands.smoke` | smoke checks against a deployed copy, with `{url}` |
| `commands.test_count` | a pattern for the line that reports how many tests ran (for `node:test`: `'^# tests (\d+)'` with the TAP reporter, `'^ℹ tests (\d+)'` with the default one); a check that ran none fails |
| `services` | test services the harness starts as containers, e.g. `postgres: pgvector/pgvector:pg16` |
| `models` | optional: the model per role (`test_advisor`, `test_author`, `builder`, `tech_lead`, `reviewers`), each with `use`, `effort`, `turns`, `minutes`. Leave it out to use the harness's defaults |
| `limits` | `rounds_per_card`, `hours_per_card`, and `paid_calls`: one entry per paid key the harness holds, each with `per_card_usd`, `per_month_usd` and `total_usd` |
| `deploy.host` | `railway` |
| `deploy.pr_copies` | `true`, or `false` (then smoke checks run on staging before the merge) |
| `deploy.staging` | `on-merge`, or `harness` (the harness deploys it with `railway up` and a staging-only token) |
| `deploy.health` | the health check path, run on staging after every merge that deploys it |
| `deploy.production` | `{ mode: veto-window, hours: N }`, or `{ mode: owner-promotes }` |
| `digest` | `{ issue: N, time: "07:30" }`: the control issue's number and the morning summary's time |

## 5. Work cards

One card per unit of work, in Markdown, in build order. The fields:

```
### <ID>: <title>
- Phase:         the phase or release it belongs to
- Goal:          one observable result, with its main example and its failure example
- Covers:        the requirement IDs it delivers
- Defers:        requirement IDs it deliberately leaves for later, or "none"
- Depends on:    card IDs that must be merged first, or "none"
- Owner input:   IDs of what the owner must supply first (from owner_inputs), or "none"
- Owns:          the files and folders it may change; nothing outside them
- Reads:         the spec sections and contracts its packet needs, beyond the always-read file
- Checks:        one per line: a test name or command, marked blocking or report;
                 "smoke" checks run on the deployed copy; "live" checks make paid calls
- Test data:     the fixtures it needs, and any recording command ("record: …")
- Side effects:  none | network | deploy | migration | paid (≤ $N) | external write,
                 with the environments allowed
- Parkable:      yes | no (if it's stuck, can the build go on without it?)
- Size:          S | M | L
- Stop if:       optional: card-specific reasons to stop and ask
```

Rules:

- IDs are permanent; a withdrawn card keeps its ID and says `withdrawn`.
- `Depends on` lists only cards that must be merged first. There are no soft dependencies: a card that can be built without another simply doesn't list it, and its checks don't rely on it.
- `Owner input` lists only what the card can't be built without. If only one check needs an input (a live recording, say), put `needs O-n` on that check's line instead: that check waits for it, and the card waits only if the check is blocking.
- Each check line starts with its marks, then the check, for example: `- blocking: F-07 resolves a teacher with one portrait`, `- report, live: F-28 trial spend stays under $27`, `- blocking, smoke: GET /api/v1/health answers 200 with this commit`, `- blocking, live, needs O-10: …`. "live" means it makes **paid** calls; a check that only uses the network (free services) is marked by the card's `Side effects: network`, not "live".
- Checks must finish within the card's time limit. Something that has to be watched over several nights belongs on the owner's release checklist, or in a later card that reads the results.
- Checks reach a deployed copy over HTTP only, with that environment's test credentials from the harness's store. The harness never runs project code with `railway run`, and no check touches production.
- A check may name a test that doesn't exist yet: the test author writes the card's acceptance tests before the code. Name tests so a single card's checks can run alone (for example `npm test -- --test-name-pattern "F-12"`).
- A size L card may take up to three builder sessions per review round, each ending with a commit and a handoff note.
- `Owns` may overlap between cards on one dependency chain (a later card adding a command to `src/cli.ts`, say, when it depends on the card that made it). `harness cards check` flags overlaps only between cards that could run at the same time. `package.json` may be owned by any card that adds a dependency; the scripts the `harness.yaml` commands use are protected.
- Each phase ends with a **gate card** carrying the phase's own checks (evals, audits, held-back runs); the verifier adds its tests there.
- The harness records each card's baseline and completion evidence itself; cards don't carry them.
- `harness cards check` reports, with line numbers: duplicate IDs, missing or circular dependencies, overlapping `Owns`, unknown checks, checks that select no tests, and paths outside the repo. The harness chat runs it on a sample of your cards before you convert the rest.

## 6. Testing

- Tests run offline in the box by default, on the project's own recorded responses; paid calls happen only in checks marked `live`, on cards whose `Side effects` allow them, within the caps.
- Acceptance tests are written first, by Codex from Gemini's list, and locked; the builder can't change them. If your plan says the builder writes each card's tests, change it: the builder may add its own unit tests and fakes, but the acceptance tests and their fixtures come from the test author, in the places `acceptance_tests` and `acceptance_fixtures` name. Don't list those files in `Owns`.
- If a card's acceptance tests pass before any code is written, the reviewers judge whether the tests are too weak or the behaviour already exists. For a "prove it" card, whose job is to show something already works, that's the expected result: the tests merge and the card is done.
- A setup card, whose checks are commands rather than tests (the card that sets up the test runner, say), skips the tests-first step; it owns the protected setup files it creates.
- Recorded responses a card's tests need are captured before its tests are locked: name the recording command in `Test data` (for example `record: npm run record -- F-07`), and the harness runs it once with network, then locks the recordings with the tests. If the recording needs an owner input, say `needs O-n` on it.
- The harness adds no coverage targets, mutation scores or evaluation suites of its own (the owner wants features that "work reasonably well without bugs").

## 7. Deploys, releases and data

- Only the conductor pushes, opens pull requests, merges and deploys; the agents never do.
- After every merge that deploys staging, the harness runs the project's health check there (`deploy.health`). A failure rolls staging back and stops new cards until it's fixed. So the app needs a health endpoint that answers only when it's really working.
- A rollback restores the app, not its data, so **database changes must be additive** (add tables and columns; never drop, rename or rewrite in place within a release), and an earlier release must keep working against the newer database.
- A veto reverts the card and sends any card built on it back to have its checks run again.
- Leftover pull-request copies and temporary environments are removed daily and at the end of a run.

## 8. Keys and spending

- Project keys live in the harness's own secret store on the PC. They're never in the repo, never in a `.env` file in the working copy, and never shown to the agents; a check that needs one gets it in a fresh box with no agent running.
- **Every paid-API key the owner gives the harness has a spending limit set on the provider's own website, no higher than the project's cap.** A cap written into code the builder can edit isn't a boundary; the provider's limit is. The harness's own count is the second line.
- The digest reports spend as three lines: the agents' usage, the app's paid calls, and hosting.

## 9. Your checklist

References are to commit `a2a5ce5`.

### Cards (`brain/plan/features.md`)

- [ ] **Rename two fields** on every card and in the format notes (:14-27): `Build` → `Owns`, `Live calls` → `Side effects`. Extend `Side effects` to the harness's values: add `migration` (F-04, F-36), `external write` (the F-27 seed, F-28, F-38, F-47), and the environments each is allowed in.
- [ ] **Add `Reads` and `Defers`** to all 45 cards. Partial covers go to `Defers`, for example "PIP-01 (part)" (:719) and "RUN-05 (frame)" (:92). `Covers` lists requirement IDs only: move T-07 (:143), D-60 (:215), "HT-02…" (:186) and "architecture.md" (:427) to `Reads` or the `Goal`.
- [ ] **Mark every check** `blocking` or `report`, one check per line; nested prose bullets such as :242-244 and :819-825 become separate lines. Keep the field name exactly `Checks`, and move qualifiers to `Test data`: "Checks (all with stubs)" (:769), "Checks (fake clock)" (:793). Likely `report` checks: memory (:455), timing (:493), engravings (:1016), :1052-1054.
- [ ] **"Live" means paid** in the harness. The free calls at :289 (GitHub) and :414 (the survey) become `Side effects: network`, not live. F-28's checks (:1012-1019) and F-29's (:1034) do spend money, so mark them `live`, with their caps in `Side effects: paid (≤ $N)`.
- [ ] **Drop soft dependencies.** Remove the `*` notation (:81) and settle its conflict with `build-plan.md`:74 ("Features that depend on it then wait"): each dependency is either real, so it's listed, or not, so it isn't. Move notes in parentheses out of `Depends on` (:277, :485) into the `Goal` or `Stop if`.
- [ ] **Owner inputs for one check.** "O-10 (the User-Agent contact) before any live recording" (:236), "O-10, to record" (:258) and "needed for the live check only" (:278) become `needs O-10` on the check or recording line, so the rest of the card can be built. "The owner's veto (by the digest's window)" (:1005) and "the veto window" (:1047) aren't owner inputs; the veto window lives in `harness.yaml`.
- [ ] **Test files come from the test author.** Take acceptance-test files out of `Owns` (:598, :954, :984, :1031), and the test helpers and fixtures too (:105, :127, :154, :433, :1008); they go where `acceptance_tests` and `acceptance_fixtures` say. Fakes the product code uses, such as :172, stay with the builder.
- [ ] **Recordings.** For the cards whose tests replay recorded responses (:268, :311, :346, :364, :380, :398), name the recording command in `Test data`, with `needs O-10` if it needs the User-Agent contact. The harness runs it once, with network, before the tests are locked.
- [ ] **"Prove it" cards** (F-16, F-26, F-27, F-29, F-47) are fine: their tests may pass at once, and the reviewers confirm the behaviour is really there. Say "prove it" in each `Goal`. Where a test re-measures its own expected values (:586), the values belong in fixtures the test author records, or the check becomes `report`.
- [ ] **F-01 is a setup card.** Its checks are the commands themselves (`npm run check`, `npm test`, `npm run build`), so it skips the tests-first step. It owns the protected setup files it creates: the `package.json` scripts, `tsconfig.json` and the test runner's settings.
- [ ] **Shared files.** Overlapping `Owns` are fine along one dependency chain. Check that each of these pairs is on one: `src/cli.ts` (:104 and :918, plus commands added at :279, :409, :815, :893), `worker.ts` and `cron.ts` (:192 and :792), `teacher.ts` (:768 and :868), `settings.ts` (:98, :1014 and :586), and `src/admin` (:893 and :1009).
- [ ] **Multi-night checks** (:1051-1052) can't be card checks, because a card has a time limit. Move them to the owner's release checklist, or to a later card that reads the results.
- [ ] **Stale wording:** "provisional" format (CLAUDE.md:84, features.md:5, build-plan.md:51) — format 1 is settled. tracker.md:472 still says "draft 2".

### The build plan and decisions

- [ ] **Add the tests-first step** to the build plan's loop (`build-plan.md`:59-68): Gemini lists the cases, Codex writes the acceptance tests, the harness checks they fail and locks them, then Claude builds.
- [ ] **Merge at once** (HD-44): `build-plan.md`:67-68 ("Merge to staging. Production changes only after the owner's veto window, announced in the digest… Add a line to the digest") becomes: merge as soon as the card passes; post its evidence, and any veto notice, on the control issue; the digest is a summary.
- [ ] **The digest as a channel or gate:** `build-plan.md`:70 and :74, `CLAUDE.md`:89 ("stop and raise it in the digest"), `features.md`:609, :1015, :1039 ("on the owner's word"), :1048 ("a release checklist in the digest") and :1054, `requirements.md`:1033 and :1039, and `decisions.md`:490. Each becomes the control issue: an instant alert, and `/approve <id>` where the owner's word is needed.
- [ ] **A superseding decision** for `decisions.md`:78-81: "Claude, OpenAI Codex and Gemini code and check each other's work" becomes: only Claude writes the product's code; Codex writes the acceptance tests from Gemini's list; Codex and Gemini review. "A digest they can veto" becomes the control issue. "Runs locally… in WSL" becomes: in the worker box on the owner's PC.
- [ ] **`BLOCKED.md`:** where `CLAUDE.md`:65 and :90 say to "raise" a wrong spec or test, a build agent writes `BLOCKED.md` instead.
- [ ] **Owner inputs** (`build-plan.md`:32-47, O-1 to O-12): add a status column the harness can read (done or not), rather than free text in Notes.
- [ ] **What the harness may write** (`build-plan.md`:81 allows only settings, through the trial, with a `recipeVersion` bump): keep that rule, and add the status page, a rulings log (for example `brain/rulings.md`) and a gotcha-notes folder for `notes_writable`.
- [ ] **The carve-out** in `CLAUDE.md`, `AGENTS.md` and `GEMINI.md` (see below).

### Releases, deploys and the veto window

- [ ] **The veto window:** set its hours (in `harness.yaml`) and write its rules into the build plan:
  - it covers one exact release, and restarts if the release changes;
  - the harness promotes only after its notice is posted on the control issue, and only if it has read the control issue within the last 10 minutes;
  - the conductor promotes, with a production token kept outside the worker box.
  Name the staging environment and branch.
- [ ] **Production before the release.** F-28 and F-29 run in production before F-47. Each production deploy or switch-on goes through the veto window, or the owner's `/approve`, so say when production is first deployed and what each of those cards needs from it. F-47's "switches the production schedule on and makes the library's key (O-11)" (:1048) splits in two: the owner makes the key (O-11, `build-plan.md`:46), and switching on the schedule is a production change that goes through the window.
- [ ] **No `railway run`.** Steps that run against a deployed environment have to change: :414, :986-987, :1050, the F-28 trial, :103, `architecture.md`:54 and :166, and `requirements.md`:883. Either the deployed copy exposes an authenticated endpoint the check calls over HTTP, or the deployed service runs the job itself, on cron or at startup. The harness never runs project code with Railway credentials.
- [ ] **Smoke checks:**
  - add `npm run smoke -- --url {url}`;
  - :200, a deliberately failing health check, is a deploy experiment already covered by HT-08, so take it out of the card;
  - for :199 (migrations and the bucket), have `/api/v1/health` report them;
  - :990 and :993 need a library key and an admin password seeded into the pull-request and staging copies. List them as per-environment test credentials the harness keeps in its store.
- [ ] **Health** (`features.md`:191, `architecture.md`:33 and :39, the OpenAPI `Health` schema): add the database and the bucket to `/api/v1/health`, so the check after each staging merge means something. `T-01-where-it-runs.md`:218 has staging rolled back by the owner's click; the harness now rolls staging back automatically when that check fails.
- [ ] **Migrations:** additive from the first staging deploy, not "once live" (`architecture.md`:142).

### Keys and spending

- [ ] **O-4** ("set as a Railway variable", `build-plan.md`:39): give the key's provider-side limit a number, no higher than the cap. Say who sets the Railway variables (the owner, in Railway), and that the harness keeps its own copies, for checks, in its secret store.
- [ ] **Consider separate keys per environment.** Today one key serves every environment (`decisions.md`:128-130), with the per-environment caps enforced in code. Code the builder can edit isn't a boundary, so a separate low-limit key for staging and for the harness's live checks lets the provider enforce each cap. This one is the owner's call, with this chat.
- [ ] **Fix the contradiction:** `decisions.md`:475 gives pull-request copies "$2 a night", while `requirements.md`:994 has them in stub mode only.

### The throwaway test (`brain/handoffs/harness-throwaway-test.md`)

These lines were written for the earlier harness design.

- [ ] HT-01 (:41) "locally in WSL" → in the harness's worker box on the PC.
- [ ] HT-05 (:50) "announced in the digest… (reply or tap)" → a notice on the control issue, `/veto <id>`, and the veto window's rules above.
- [ ] HT-08 (:58) and HT-22 (:92) "in the digest" → an alert and the control issue (the digest still summarizes).
- [ ] HT-09 (:59) "the owner taps once in the dashboard" → keep it as the owner's own path, and add: `/veto` reverts the card, and the conductor redeploys.
- [ ] HT-23 (:93), Railway's MCP server → the conductor reads logs and deploy status with the Railway CLI; the MCP server isn't used.
- [ ] HT-26 (:101) "live check" → "smoke check" ("live" now means paid).
- [ ] HT-27 (:102) "the digest… offers the veto" → the control issue.
- [ ] HT-28 (:103) "one-tap deploys" → veto windows and `/approve`.
- [ ] HT-06 (:51), the owner deploying from the phone, stays: the owner can always deploy by hand.
- [ ] Worth adding, because they need a real host: a `/veto` that reverts a merged card and redeploys staging; and a failed health check after a merge that rolls staging back and stops new cards. The harness's other safety checks are tested in its own stage H2, not here.

### Housekeeping

- [ ] "Argon Notes.md" sits at the repo root and in `brain/reviews/` (commit 4137add), word for word the round already merged. Keep one.

**Carve-out wording** for `CLAUDE.md`, `AGENTS.md` and `GEMINI.md` (adapt as you like):

> **When you're a build agent run by the Coding Harness.** If your prompt says so, this file's "read first" and "update before you finish" lists don't apply to you. Read what your packet names, and any other file you need; change only the files your card's `Owns` lists; never edit `brain/`, the cards or any other protected path; commit only to the card's branch, and only when your prompt asks; never push or deploy. If a spec or a test looks wrong, stop and explain in `BLOCKED.md`.

## 10. Already in place (no change needed)

- File order is build order, and every card already has `Phase`, `Depends on`, `Owner input`, `Parkable`, `Size` and `Covers`.
- IDs are permanent, and withdrawn cards (F-20, F-33) are kept.
- Tests run offline, with stubs, replays and PGlite (no database container needed), and a missing recording fails.
- One test file per card, named by card, so a single card's tests run by name pattern.
- Paid checks are capped, and pull-request copies run in stub mode.
- The health endpoint reports the commit.
- No keys in the repo, and `.env` is ignored. The OpenRouter key has a provider-side limit, and the throwaway test uses its own low-limit key.
- Migrations and the API contract are additive (once live; see above).
- LF line endings (`.gitattributes`), and nothing depends on a Windows path.
- A card with a missing owner input is skipped while the build goes on, and `Parkable` means the same as in the harness.
- Fixed requirements, the API contract and the style rules are never changed to make a check pass.
- Two other models review each card; both size L cards (F-23, F-28) get the contract step.

## 11. A draft `harness.yaml`

Fill in the `TODO`s and put it at the repo root.

```yaml
format: 1
project: libraryai-portraits
cards: brain/plan/features.md
always_read: CLAUDE.md
protected: [brain/, design/, prototype/, models/, test/fixtures/reference/, CLAUDE.md, AGENTS.md, GEMINI.md, .github/, tsconfig.json]   # TODO: add the contracts folder's path
owner_inputs: brain/plan/build-plan.md#3     # needs a status column (checklist above)
notes_writable: [brain/status.md, brain/rulings.md]   # TODO: plus your gotcha-notes folder
rulings: brain/rulings.md
held_back: []
acceptance_tests: "test/{slug}-*.test.ts"     # F-07 -> test/f07-*.test.ts
acceptance_fixtures: "test/fixtures/{slug}/"
box: { apt: [] }                              # sharp and OpenCV.js come from npm
services: {}                                  # PGlite runs in the tests themselves
commands:
  install: npm ci
  check: npm run check
  test: npm test
  test_card: npm test -- --test-name-pattern "{card}"
  build: npm run build
  smoke: npm run smoke -- --url {url}         # TODO: add this script
  test_count: '^ℹ tests (\d+)'               # node:test's default reporter; TODO: confirm against a real run
# models: left out, so the harness's defaults apply
limits:
  rounds_per_card: 4
  hours_per_card: 6
  paid_calls:
    openrouter: { per_card_usd: 2, per_month_usd: 30, total_usd: 100 }   # D-54; a card's own "paid (≤ $N)" sets its cap (F-28: $27)
deploy:
  host: railway
  pr_copies: true
  staging: on-merge                           # TODO: confirm
  health: /api/v1/health
  production: { mode: veto-window, hours: 24 }   # TODO: the owner's number
digest: { issue: TODO, time: "07:30" }        # the control issue, created when the build starts
```
