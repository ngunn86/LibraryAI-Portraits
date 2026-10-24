# Coding Harness Instructions: the portraits tool

**From:** the Coding Harness chat · **Date:** 2026-10-20 · **For:** this repo's planning chat
**Harness plan:** `ngunn86/Coding-Harness`, as of 2026-10-23 (its decisions up to HD-71). That repo is private, so this file is complete on its own.
**Updated** 2026-10-24: three hosting rules proved by the harness's own Northflank test (copies name their resources after the copy, project-only API roles, CD off; harness HD-71), in the first section below. 2026-10-23 (evening): **how the two Northflank projects must be laid out** (a build service sharing its builds, deployment services, a `pr-copy` preview blueprint; harness HD-70); see the first section below. 2026-10-23 (later): `harness cards check` is ready, your sample passes, and your twelve questions are answered (harness HD-65); see the two sections below. 2026-10-23: **the host is now Northflank, not Railway** (the owner, harness HD-60); see "Hosting change" below. 2026-10-22: the veto window is 24 hours, as your D-66 already says (the owner, harness HD-59). 2026-10-21: pull-request copies are based on staging, never production, and the health check names its environment, database and bucket (Codex's third review); earlier the same day, per-card spending caps became soft, with the provider's limit as the hard ceiling (the owner's choice); and before that, `test_card` never uses `npx` and each test case gets a unique name starting with its card's ID (Argon's third review), TAP output with each named case checked, `deploy.starts_at`, contracts before tests on size L cards, fast-forward merges (Codex's second), and tests run by file path with each card saying what it creates (Argon's second). Earlier, 2026-10-20: the veto window was set at 72 hours (now 24), the one paid key stays, library-pipeline may run on a second PC.
**Placed here** at the owner's request (harness decision HD-47). It's the only file the harness chat writes in this repo; commit it with your next planning round. When the harness's requirements change, the harness chat updates this file and says so at the top.


## How the Northflank projects are laid out (2026-10-23, harness HD-70)

The harness now has its Northflank code, checked against Northflank's API reference. Three findings set the layout each hosted project needs, so please record them in your hosting notes (Claude's choices; the owner can veto):

- **Staging project:** one **build service** that builds the app from its GitHub repo, with **"share build access with other projects"** turned on; one or more **deployment services** that deploy that build service's builds (staging: the web app, and any worker running the same image); the staging add-ons (Postgres, and so on) and test secrets; and, if the project uses pull-request copies, one **preview blueprint** named `pr-copy`, with a lifetime of a few hours, that builds the pull request's branch and makes the copy's own database and deployment service with a public port. Not a "combined" service: Northflank can't put a combined service back on an earlier build, so it can't be rolled back.
- **Production project:** deployment services that deploy the **staging build service's shared builds**, with production's own add-ons and secrets. A Northflank pipeline can't span two projects, so promotion means putting the exact build staging tested on production's deployment services, nothing rebuilt.
- **Pull-request copies are Preview Blueprints** (Northflank's current previews), not the older pipeline preview templates.
- **Nothing about this goes in `harness.yaml`.** `harness hosting connect --project <this repo's folder>` takes the tokens, checks each reaches only its own project, and finds the services by this layout; `harness hosting check --project <folder>` then checks the tokens (read-only for a real project). The owner sets this up with the harness chat when your deploy card comes near.
- **At release,** the harness deploys the build; anything else a release needs (a migration job, a seed) runs from the app itself (additive, at start-up) or must be raised with the harness chat first. The harness doesn't run a release workflow yet.
- **Name every resource a copy makes after the copy** (added 2026-10-24, harness HD-71): in the `pr-copy` blueprint, each database, service and secret group needs the copy's ID in its name, like `${args.previewId}-db`. With a fixed name, Northflank's "create or replace" makes the copy take over staging's resource of that name; this happened in the harness's own test, and `harness hosting connect` now refuses such a blueprint.
- **The harness's two API roles** carry **project permissions only**, each restricted to its one project, with the owner added (and confirmed) as a member; no team permissions (roles, members, tokens, billing), which a project restriction doesn't limit. The harness chat sets them up with the owner.
- **Deploys** put a chosen build on the deployment services through Northflank's API, so leave **CD off** on staging's and production's deployment services: the harness decides which build runs.

## Hosting change: Northflank instead of Railway (2026-10-23)

The owner moved hosting from Railway to Northflank (harness HD-60), because Railway disclosed on 2026-10-21 that attackers may have read customers' environment variables. Record it in your Decisions as the owner's, replacing your Railway decision (your D-36), and change your Railway references to this:

- **Two Northflank projects:** one for staging and the pull-request copies, one for production. The harness's everyday token can reach only the first; a production token exists only where production is promoted after a veto window, and only the harness's conductor holds it.
- **Pull-request copies** are Northflank preview environments: made for each pull request from a preview template, each with its own database (forked from staging's latest backup, or empty and seeded) and its own test secrets, deleted when the pull request closes or merges, and after a lifetime set in the template.
- **Staging** deploys on each merge to `main`, or, with `staging: harness`, when the harness starts a build of a chosen commit. **Production** is promoted by the owner in Northflank's dashboard, or by the harness after a veto window.
- **Health checks** are the service's readiness and liveness checks; **migrations** run as a job step in the release workflow, and stay additive.
- **No hard spending cap:** Northflank only has a billing threshold, so each copy gets a short lifetime and the harness's daily clean-up removes leftovers.
- **Files:** Cloudflare R2, or Northflank's MinIO add-on. Postgres add-ons have pgvector built in. There's no phone app; the owner uses the dashboard in the phone's browser.
- **No host CLI for project code:** checks reach deployed copies over HTTP only, as before.


## `harness cards check` is ready (2026-10-23)

Run it on your cards and `harness.yaml` whenever they change: `harness cards check --project <this repo's folder>` (in Ubuntu, after `cd ~/harness && git pull`). It reports, with line numbers, what would stop or mislead a build: cards it can't read, missing fields, duplicate IDs, missing, withdrawn or circular dependencies, cards owning the same files though they could run at the same time, checks it can't run or that would select no tests (or another card's), owner inputs that don't exist or are withdrawn, smoke checks before `deploy.starts_at`, live checks without a paid cap, `npx`, and paths outside the repo. ✗ lines must be fixed; ! lines deserve a look; · lines are notes.

### Your sample: it passes

`harness cards check` on `main` at `ee3c265` reads all 18 converted cards with no problem, and found every field, dependency, owner input and check as you meant them. What it reports:
- **✗ the other 34 cards** are still in draft 3's format (bold fields, Build, Live calls). Convert them now; the sample shows the format works.
- **! F-47's Side effects** mention production inside the deploy item. Write production as its own item (question 5): `deploy (pull-request copies); production (promoted by the conductor after the 24-hour window, D-66); external write (the seed, on the deployed copy)`.
- **· notes:** F-01 owns `tsconfig.json` and F-36 owns `northflank/`, both protected paths. That's allowed because the cards name them, and the digest will say so. `digest.issue` stays TODO until the harness opens the control issue.

### Answers to your questions (harness HD-65, Claude's choices; the owner can veto)

1. **Shared test fixtures: yes,** a later card's acceptance tests may import an earlier, merged card's fixtures from `test/fixtures/fNN/`, read-only. Every merged card's acceptance tests and fixtures stay locked, so a later builder's change to them is undone (HR-25). Helpers a builder may need to extend belong in the product's code, as F-04's `openTestDb()` already is.
2. **The AI key: the harness doesn't need it.** Live checks starting the app's own jobs is fine. Add `spend: /api/ops/spend` to `limits.paid_calls.openrouter`, and the harness reads that path with the environment's test credentials after each check, stopping a card once it's over its cap (caps are soft, HD-56). The hard ceiling stays the key's own limit at OpenRouter (O-4).
3. **Credentials: use your names.** When the owner puts the test credentials in the harness's store (at stage H3), each is stored under its own name for its environment (`PORTRAITS_OPS_KEY`, `PORTRAITS_TEST_LIBRARY_KEY`, `PORTRAITS_TEST_ADMIN_PASSWORD`). Every smoke or recording command for that environment gets all of them as environment variables, plus the copy's address as `{url}` and as `HARNESS_URL`, and `HARNESS_ENV` (`staging` or `preview`). So `PORTRAITS_URL` isn't needed; read `HARNESS_URL`, or take `--url {url}`. A **recording** that needs a deployed copy says so with `{url}` in its command, and runs against staging: write F-50's as `npm run record-ops -- F-50 --kind trial --url {url}`.
4. **Checks on staging: yes.** A card whose Side effects say `staging only`, and that doesn't deploy, runs its smoke checks against staging, even with `pr_copies: true`, since there's nothing new to deploy. F-27, F-52 and F-29 are right as written.
5. **Production is promoted only after a release card,** never after every merge. A release card says `production` as its own item in Side effects; when it merges, the conductor posts the notice, waits out the 24-hour window, and promotes that commit. Later fixes reach production the same way, through a card that says `production`. So `veto-window` stays right for you, and F-47 only needs the rewording above.
6. **Field values:** F-47, as in 5. `Covers: none` and `Owns: none` on gate and prove-it cards are fine. `acceptance_tests: "test/{slug}-*"` without an extension is fine: the test author writes both `*.test.ts` and `*.smoke.ts`, and the harness locks every file the pattern matches. The setup card's command checks are fine (HR-78).
7. Settled by the move to Northflank.
8. **Production's release flow:** the conductor starts it through Northflank's API with the commit as its argument; the H3 permissions test proves that works with the production token, and if it doesn't, the fallback is moving a `production` branch that production's build follows. **The first `production.json` run** is part of the release: the release notice names it, so the 24-hour veto covers it, and the conductor runs it with the production token. No separate owner step.
9. **R2 with prefixes and a 7-day rule: yes,** it fits. The daily clean-up removes leftover Northflank copies; R2's rule handles their files; HT-13 holds as long as each copy's health names its own prefix, which the harness checks against production's bucket before smoke checks run (HR-43).
10. **Empty, migrated, seeded preview databases: yes,** better than a fork, since nothing real reaches a test copy. Three sets of test credentials are fine.
11. **Preview lifetime:** the harness has no default of its own; 3 days is good. It deletes a copy when its pull request closes or merges, and a copy that expired while a card waited is made again on the next push.
12. **Liveness:** no. The harness only reads `deploy.health`; `/api/v1/live` belongs to Northflank's own settings.

## 1. What this file is, and how to use it

The Coding Harness will build this project, right after its throwaway test app (HT-01 to HT-29, specified in this repo) and before Library-AI Rev1. This file lists everything this project's planning needs to change or add so the harness can build it unattended.

- **Section 3 holds owner decisions** made in the harness chat. Record them in your Decisions as the owner's, with their quotes.
- **Everything else is what the harness requires.** Write it into your notes your own way, under your own rules, status words and IDs.
- **Section 9 is your checklist,** with file and line references as of commit `a2a5ce5`. Lines drift, so each item quotes enough text to find it.
- **When you're done,** tell the owner. The harness chat will then run `harness cards check` on a sample of your cards and send back anything it finds. Convert the rest of the cards after that.
- **Questions about the harness itself** go to the owner, who brings them to the harness chat. Don't change the harness's rules here. Where the two disagree, the owner's decisions and this project's own rules win, and the harness adapts.

## 2. How the harness will build this project

The harness is a general-purpose script on the owner's PC (Windows, WSL Ubuntu) that builds the owner's projects, this one included, one work card at a time, unattended, on the owner's subscriptions (Claude Max, ChatGPT, Google AI Ultra), never API billing for its agents. Its plan lives in the private repo `ngunn86/Coding-Harness`; this file carries everything a project needs from it, so you don't need that repo.

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
2. **Contract** (size L cards only). The builder says how it will build the card and prove each check, including the interfaces it will create; Codex approves or asks for changes.
3. **Tests first.** Gemini lists the cases the tests must cover. Codex writes the card's acceptance tests from the card, its specs, the contract and that list. The conductor checks they fail on the code as it stands, for the right reason, then locks them for the card.
4. **Build.** Claude works on the card's branch in a fresh session, inside the worker box (below), with the card's locked acceptance tests in its packet and the project installed, so it can run `check` and its card's tests as it works. It may add its own tests.
5. **Check,** in a fresh box from the exact commit: the project's `check`, the card's tests, the full suite, `build`, and a scan for gaming (skipped or deleted tests, swallowed errors, hard-coded answers). A check that runs no tests fails.
6. **Review,** only of a commit whose checks passed. Codex and Gemini review the same commit and return structured verdicts. P0 and P1 findings block; P2 and P3 go to a backlog.
7. **Deploy and smoke,** for cards with smoke checks: on the pull-request copy where the project uses them, otherwise on staging before the merge.
8. **Grade.** A only if every blocking check, both reviews and the smoke checks pass, all for the same commit. No model can award it.
9. **Merge** that commit only, as soon as it passes, by a fast-forward push to `main`, with its evidence posted on the project's control issue at once. If `main` moved meanwhile (a planning push, say), the card brings it in and is checked again. The owner's veto reverts a merge.
10. **Record** the evidence, spend and lessons.

**When a card is stuck:** rounds 1 and 2, the builder fixes the findings; round 3, Codex diagnoses and writes a fix plan, which Claude applies; round 4, Gemini does the same; then the Tech Lead, up to twice. Then a `Parkable: yes` card is parked, and retried only when something it depends on changes (at most twice); a `Parkable: no` card stops the build and alerts the owner at once. A missing or malformed review is no sign-off, and another model never stands in for it. A builder that finds a spec or test wrong stops and explains in `BLOCKED.md`; the Tech Lead rules or asks the owner. A test shown to be wrong is rewritten by the test author, the change is logged, and the card's earlier evidence is void. A change pushed to a card, or to the specs it reads, while the card is running also voids its evidence.

**The worker box.** The agents, and all of the project's own commands (install, tests, build, the dev server), run inside a Docker container that holds only the card's working copy, the harness's own logins for the agents and the test services; the checks run in a fresh box with no logins at all. It has no GitHub or Northflank credentials, no Windows drives and no Docker socket. Test services such as a database run as separate containers that the harness starts. So nothing in the project may depend on Windows paths, on the owner's own logins, or on tools that aren't installed by the project's `install` command or named in its setup.

**Build agents and your instruction files.** Claude Code, Codex and Gemini each load the project's own instruction file by themselves (`CLAUDE.md`, `AGENTS.md`, `GEMINI.md`). The harness's prompt tells each one it's a build agent: it reads what its packet names, changes only its card's `Owns`, never edits the notes, and skips the planning chats' "read first" and "update before you finish" lists. Add a short section saying the same to each of those files (wording in the checklist below), so the two never pull against each other.

**What wins.** The owner's decisions and the project's own rules win over the harness's policy, and the Tech Lead rules only within them.

## 3. Owner decisions that affect this project

Made in the harness chat; IDs are the harness's (`HD-`).

- **Merge right away** (HD-44, 2026-10-20): "Merge the cards right away, yes." A card merges as soon as its blocking checks pass, with its evidence posted on the control issue at once; the morning digest is only a summary; the owner's veto still reverts a merge. This replaces "merges when its blocking checks pass and the digest has gone out".
- **Phone control through GitHub** (HD-42, 2026-10-20): each project's repo gets one GitHub issue, the **control issue**. The owner steers by replying there, from the GitHub app or by email reply: `/status`, `/pause` (after the current step), `/stop` (now), `/resume`, `/approve <id>`, `/veto <id>`, and `/direct <plain words>`, which the Tech Lead reads but which can't raise a budget or a permission. The harness reads the issue every 2 minutes and accepts commands only from the owner's GitHub account. ntfy push alerts notify at once and link to the issue. Remote Control chat is optional, not part of the control path.
- **Never idle waiting for the owner** (HD-42, HR-57): a question goes out as an alert at once, and the harness carries on with every card the question doesn't block.
- **Authorizations** the owner keeps (email to a real address other than the owner's, a production deploy or switch-over, deleting production data, spend above a cap, new keys or accounts, anything irreversible outside the repo) are asked on the control issue with an instant alert, naming the exact action and reason, not in the digest.
- **No usage reserve** (HD-41): the harness uses each plan until the tool stops it, including any extra usage the owner turns on, then waits for the reset.
- **The PC is dedicated to the build while it runs** (HD-40): library-pipeline doesn't run on it then; if it's needed during a build, the owner runs it on a second PC (HD-49).

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
| `commands.test_card` | the card's own acceptance test files, by path, using `{slug}`, printing TAP: `node --test --test-reporter=tap "test/{slug}-*.test.ts"` for plain Node TypeScript, or `./node_modules/.bin/tsx --test --test-reporter=tap "test/{slug}-*.test.ts"` for a project that uses tsx. Never `npx`, which would try to download a missing tool in an offline check box, and never a name filter (on Node, `--test-name-pattern` can run every test in the repo, or count each file as a passing test). The harness takes each acceptance case's name from the test author and passes the check only if every one ran and passed; an empty file, a file that crashed, or one with only skipped tests fails |
| `commands.build` | the production build |
| `commands.smoke` | smoke checks against a deployed copy, with `{url}` |
| `commands.test_count` | `withdrawn` (2026-10-21): the harness reads each acceptance case's result from the TAP output itself |
| `services` | test services the harness starts as containers, e.g. `postgres: pgvector/pgvector:pg16` |
| `models` | optional: the model per role (`test_advisor`, `test_author`, `builder`, `tech_lead`, `reviewers`), each with `use`, `effort`, `turns`, `minutes`. Leave it out to use the harness's defaults |
| `limits` | `rounds_per_card`, `hours_per_card`, and `paid_calls`: one entry per paid key, each with `per_card_usd`, `per_month_usd` and `total_usd`, and, when the app spends with its own key rather than the harness holding it, `spend`: the path where a deployed copy reports that key's spend (for example `/api/ops/spend`), read with that environment's test credentials after each check (HD-65) |
| `deploy` | leave out, or `deploy: none`, for a project that isn't hosted (a tool or a library); otherwise the fields below |
| `deploy.host` | `northflank` (the only host the harness drives for now; it replaced Railway, harness HD-60) |
| `deploy.pr_copies` | `true` (each copy is based on staging, never production), or `false` (then smoke checks run on staging before the merge) |
| `deploy.staging` | `on-merge`, or `harness` (the harness starts a staging build of a chosen commit through Northflank's API, with a staging-only token) |
| `deploy.health` | the health check path, run on staging after every merge that deploys it |
| `deploy.starts_at` | the card from which deploys and health checks begin (the one that makes the app deployable, with its health endpoint), so early scaffolding never triggers a rollback |
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
- Checks reach a deployed copy over HTTP only, with that environment's test credentials from the harness's store. The harness never runs project code through the host's CLI or a shell in a deployed container, and no check touches production.
- A check may name a test that doesn't exist yet: the test author writes the card's acceptance tests before the code. Give each test case a unique name starting with the card's ID (`F-07: resolves a teacher with one portrait`). Name test files after their card (for example `test/f12-*.test.ts`), so `test_card` can run a single card's tests by path.
- A size L card may take up to three builder sessions per review round, each ending with a commit and a handoff note.
- `Owns` may overlap between cards on one dependency chain (a later card adding a command to `src/cli.ts`, say, when it depends on the card that made it). `harness cards check` flags overlaps only between cards that could run at the same time. `package.json` may be owned by any card that adds a dependency; the scripts the `harness.yaml` commands use are protected.
- Each phase ends with a **gate card** carrying the phase's own checks (evals, audits, held-back runs); the verifier adds its tests there.
- The harness records each card's baseline and completion evidence itself; cards don't carry them.
- `harness cards check` reports, with line numbers: duplicate IDs, missing or circular dependencies, overlapping `Owns`, unknown checks, checks that select no tests, and paths outside the repo. The harness chat runs it on a sample of your cards before you convert the rest.

## 6. Testing

- Tests run offline in the box by default, on the project's own recorded responses; paid calls happen only in checks marked `live`, on cards whose `Side effects` allow them, within the caps.
- Acceptance tests are written first, by Codex from Gemini's list, and locked; the builder can't change them. If your plan says the builder writes each card's tests, change it: the builder may add its own unit tests and fakes, but the acceptance tests and their fixtures come from the test author, in the places `acceptance_tests` and `acceptance_fixtures` name. Don't list those files in `Owns`.
- **Say what each card creates.** The test author writes tests before the code exists, so it imports from the module paths and names the card gives. Put them in each card's `Goal` (or in a contract it `Reads`): for example "adds `resolveTeacher(name)` in `src/pipeline/resolve.ts`", or the HTTP route or CLI command it adds. Otherwise the test author has to guess, and the builder may build something different that the locked tests can't reach.
- Before the tests are locked they must fail for the right reason (a missing module or a failed assertion, never a syntax error). A type error inside a locked test goes back to the test author, without costing the builder a round.
- If a card's acceptance tests pass before any code is written, the reviewers judge whether the tests are too weak or the behaviour already exists. For a "prove it" card, whose job is to show something already works, that's the expected result: the tests merge and the card is done.
- A setup card, whose checks are commands rather than tests (the card that sets up the test runner, say), skips the tests-first step; it owns the protected setup files it creates. A command check passes when it exits 0 within its time limit; `install` applies once the project has its lockfile; and nothing deploys before the card `deploy.starts_at` names.
- Recorded responses a card's tests need are captured before its tests are locked: name the recording command in `Test data` (for example `record: npm run record -- F-07`), and the harness runs it once with network, then locks the recordings with the tests. If the recording needs an owner input, say `needs O-n` on it.
- The harness adds no coverage targets, mutation scores or evaluation suites of its own (the owner wants features that "work reasonably well without bugs").

## 7. Deploys, releases and data

- Only the conductor pushes, opens pull requests, merges and deploys; the agents never do.
- After every merge that deploys staging, the harness runs the project's health check there (`deploy.health`). A failure rolls staging back and stops new cards until it's fixed. So the app needs a health endpoint that answers only when it's really working.
- A rollback restores the app, not its data, so **database changes must be additive** (add tables and columns; never drop, rename or rewrite in place within a release), and an earlier release must keep working against the newer database.
- A veto reverts the card and sends any card built on it back to have its checks run again.
- **Pull-request copies are based on staging, never production.** On Northflank they live in the staging project, apart from production's, and a copy that reached production's keys or data would be a serious fault. So each copy gets staging's test credentials and its own test database and storage, and the health endpoint reports its environment's name and which database and bucket it uses (names only, never a secret), so the harness can check before smoke checks run that a copy isn't using production's.
- Leftover pull-request copies and temporary environments are removed daily and at the end of a run.

## 8. Keys and spending

- Project keys live in the harness's own secret store on the PC. They're never in the repo, never in a `.env` file in the working copy, and never shown to the agents; a check that needs one gets it in a fresh box with no agent running.
- **Every paid-API key the owner gives the harness has a spending limit set on the provider's own website, no higher than the project's cap.** That's the hard ceiling: a cap written into code the builder can edit isn't a boundary.
- **Per-card caps are soft** (the owner's choice, HD-56): checks use the key directly, and the harness adds up spend after each check and stops the card once it's over. A card's own `Side effects: paid (≤ $N)` sets its cap, overriding the default `per_card_usd`, and only the card can say so.
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
- [ ] **Running one card's tests.** `features.md`:8 and `build-plan.md`:63 and :89 run one card with `npm test -- --test-name-pattern "F-07"`. On Node that filter can run every test in the repo, or count each file as a passing test, so a card with no tests would still pass. Run the card's own files by path instead: `./node_modules/.bin/tsx --test --test-reporter=tap "test/f07-*.test.ts"` (the `test_card` command in section 11; not `npx`, which would try to download tsx in an offline check box).
- [ ] **Say what each card creates:** the module path and exported names (or the route or command) each card adds, in its `Goal`, so the test author's tests and the builder's code meet (section 6).
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

- [ ] **The veto window is 24 hours** (owner, harness HD-59, 2026-10-22: "Switch to 24 hours for the portraits", replacing HD-50's 72 hours; your D-66 already records it). Record it, and write its rules into the build plan:
  - it covers one exact release, and restarts if the release changes;
  - the harness promotes only after its notice is posted on the control issue, and only if it has read the control issue within the last 10 minutes;
  - the conductor promotes, with a production token kept outside the worker box.
  Name the staging environment and branch.
- [ ] **Production before the release.** F-28 and F-29 run in production before F-47. Each production deploy or switch-on goes through the veto window, or the owner's `/approve`, so say when production is first deployed and what each of those cards needs from it. F-47's "switches the production schedule on and makes the library's key (O-11)" (:1048) splits in two: the owner makes the key (O-11, `build-plan.md`:46), and switching on the schedule is a production change that goes through the window.
- [ ] **No running project code through the host's CLI** (it was `railway run`; the rule is the same on Northflank). Steps that run against a deployed environment have to change: :414, :986-987, :1050, the F-28 trial, :103, `architecture.md`:54 and :166, and `requirements.md`:883. Either the deployed copy exposes an authenticated endpoint the check calls over HTTP, or the deployed service runs the job itself, on cron or at startup. The harness never runs project code with the host's credentials.
- [ ] **Smoke checks:**
  - add `npm run smoke -- --url {url}`;
  - :200, a deliberately failing health check, is a deploy experiment already covered by HT-08, so take it out of the card;
  - for :199 (migrations and the bucket), have `/api/v1/health` report them;
  - :990 and :993 need a library key and an admin password seeded into the pull-request and staging copies. List them as per-environment test credentials the harness keeps in its store.
- [ ] **Health** (`features.md`:191, `architecture.md`:33 and :39, the OpenAPI `Health` schema): add the database and the bucket to `/api/v1/health`, so the check after each staging merge means something. `T-01-where-it-runs.md`:218 has staging rolled back by the owner's click; the harness now rolls staging back automatically when that check fails.
- [ ] **Migrations:** additive from the first staging deploy, not "once live" (`architecture.md`:142).
- [ ] **Pull-request copies' base** (section 7): say they're based on staging, with its test database, bucket and keys, never production, and have `/api/v1/health` report the environment's name and the database's and bucket's names (never a secret).

### Keys and spending

- [ ] **O-4** ("set as a Railway variable", `build-plan.md`:39): give the key's provider-side limit a number, no higher than the cap. Say who sets the host's secrets (the owner, in Northflank's secret groups), and that the harness keeps its own copies, for checks, in its secret store.
- [ ] **One key stays** (owner, harness HD-50: "Lets use the one paid key for portraits"): the single OpenRouter key serves every environment, as `decisions.md`:128-130 says. Its provider-side limit is the backstop across all of them, so set it no higher than the overall cap; the per-environment caps in code stay as the first line.
- [ ] **Fix the contradiction:** `decisions.md`:475 gives pull-request copies "$2 a night", while `requirements.md`:994 has them in stub mode only.

### The throwaway test (`brain/handoffs/harness-throwaway-test.md`)

These lines were written for the earlier harness design.

- [ ] HT-01 (:41) "locally in WSL" → in the harness's worker box on the PC.
- [ ] HT-05 (:50) "announced in the digest… (reply or tap)" → a notice on the control issue, `/veto <id>`, and the veto window's rules above.
- [ ] HT-08 (:58) and HT-22 (:92) "in the digest" → an alert and the control issue (the digest still summarizes).
- [ ] HT-09 (:59) "the owner taps once in the dashboard" → keep it as the owner's own path, and add: `/veto` reverts the card, and the conductor redeploys.
- [ ] HT-23 (:93), Railway's MCP server → the conductor reads logs and deploy status through Northflank's API; no host MCP server is used.
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
- One test file per card, named by card, so a single card's tests run by file path.
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
  test_card: ./node_modules/.bin/tsx --test --test-reporter=tap "test/{slug}-*.test.ts"   # the card's own files, by path, printing TAP
  build: npm run build
  smoke: npm run smoke -- --url {url}         # TODO: add this script
# models: left out, so the harness's defaults apply
limits:
  rounds_per_card: 4
  hours_per_card: 6
  paid_calls:
    openrouter: { per_card_usd: 2, per_month_usd: 30, total_usd: 100 }   # D-54; a card's own "paid (≤ $N)" sets its cap (F-28: $27)
deploy:
  host: northflank
  pr_copies: true
  staging: on-merge                           # TODO: confirm
  health: /api/v1/health
  starts_at: TODO                             # the card that makes the app deployable (F-02's hosting setup?)
  production: { mode: veto-window, hours: 24 }   # owner, HD-59 (your D-66)
digest: { issue: TODO, time: "07:30" }        # the control issue, created when the build starts
```
