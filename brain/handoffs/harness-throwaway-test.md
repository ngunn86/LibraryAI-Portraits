# Harness throwaway test: requirements

**What this is:** the requirements for a small, throwaway app that the build harness builds, deploys, tests and tears down **before** any Nexus Portraits feature work. It proves that the harness and the host can do everything the real app will need. The app itself does nothing useful and is deleted afterwards.

**Who uses it:** the owner plans and runs this test in the harness chat (D-15). This file is the portraits project's list of what the test must prove. **Claude keeps it updated** as portraits decisions change what the hosted app needs. Every change is logged at the bottom.

**Status:** draft v1, 2026-10-19; updated 2026-10-20 to 2026-10-23 (see the change log).

- **Host: Northflank, decided** (D-70, 2026-10-23, the harness's HD-60). It replaced Railway (D-36) after Railway disclosed on 2026-10-21 that attackers may have read customers' environment variables. This test is the harness's own proof on Northflank, not a way of choosing a host.
- Rev1's Railway hosting review no longer applies to this project.
- Requirements marked *(Northflank)* name Northflank's features; the rest apply to any host.

**Linked:** tracker T-01 and T-27 · [topics/T-01-where-it-runs.md](../topics/T-01-where-it-runs.md) · decisions D-31..D-35

---

## The throwaway app

The app is a tiny **TypeScript (Node 24) web app**, with the same shape and stack as the real one (D-57): Express, Drizzle with SQL migrations, `node:test`, and the S3 SDK for the bucket.

```
throwaway project (one GitHub repo, one host project)
  web       /health · /items (Postgres read/write) · /files (bucket upload, presigned download)
            /secure (needs an API key) · /admin (one plain HTML page) · /ai (one tiny OpenRouter call)
            /github (reads a file from a private repo with a read-only token)
  worker    a job that runs for 40 minutes, writing progress to Postgres; picks up queued jobs
  cron      a scheduled job that runs, writes a row and exits
  postgres  one table plus one migration
  bucket    a few test files (Cloudflare R2, or Northflank's MinIO add-on)
two Northflank projects: staging, with a temporary preview environment per pull request · production
```

## Requirements

Each requirement has an ID (HT-nn), what the test must show, and when it counts as passed. IDs are permanent, and new ones are added at the end of their group.

### A. Build and repository

| ID | What must be shown | Passed when |
|---|---|---|
| HT-01 | The harness creates the throwaway repo, or uses one the owner creates, with the project skeleton and an offline test suite | The tests pass in the harness's worker box on the PC, and on each pull request |
| HT-02 | The host builds the Node 24 TypeScript app from the repo with no hand-made build steps *(Northflank: a Dockerfile, or its buildpacks)*. *Since D-57:* include one WebAssembly dependency (OpenCV.js) and `sharp`'s native binary, to prove they build and run on the host. *Since Argon's review:* also `onnxruntime-node`, the real app's fallback for its face detector | The build log shows success for the commit pushed, and `/health` reports that OpenCV.js, `sharp` and `onnxruntime-node` loaded. `onnxruntime-node` runs one small ONNX model (the portraits repo's `models/face_detection_yunet_2026may.onnx`) on a test image |

### B. Deploying

| ID | What must be shown | Passed when |
|---|---|---|
| HT-03 | A merge to `main` deploys staging **without clicking** *(Northflank: the staging pipeline's release flow, started by the push: build, migrate, deploy)* | Staging's `/health` shows the new commit within a few minutes of the merge |
| HT-04 | A pull request gets its own **temporary copy**, with its own URL, database and bucket *(Northflank: a preview environment in the staging project, made from its preview template, with its own Postgres add-on, empty and seeded, or forked from staging's latest backup)* | The harness finds the PR copy's URL and gets 200 from `/health`. The copy disappears when the PR is closed or merged, and after the template's lifetime |
| HT-05 | Promotion to production happens only **after the owner's veto window**, announced on the control issue (D-63, D-66) *(Northflank: the conductor starts production's release flow, in the production project, with the production token)* | Production changes only after the window. The window covers one exact release and restarts if it changes; the conductor promotes only if it read the control issue within the last 10 minutes. `/veto <id>` stops it |
| HT-06 | The owner's own deploy path works from a phone (D-35 fallback) *(Northflank: the dashboard in the phone's browser; there's no app)* | The owner deploys or redeploys from the phone in under 2 minutes |
| HT-07 | The project setup lives in the repo, as far as the host allows *(Northflank: templates as JSON files in the repo, synced both ways with the dashboard, covering the pipelines, release flows, the preview template, add-ons and the cron job; they name secret groups but hold no values)* | Running the templates reproduces the setup in an empty project. Anything they can't express is listed in the repo as a one-time dashboard step |

### C. Health checks and rollback

| ID | What must be shown | Passed when |
|---|---|---|
| HT-08 | A deliberately broken release **doesn't go live**: the healthcheck holds it back *(Northflank: the readiness check; new instances that never become ready don't replace the old ones. A liveness check that does nothing but answer restarts a hung process)* | The previous release keeps serving, and the failed deploy is alerted on the control issue at once (the digest summarizes it) |
| HT-09 | Rolling back works: the owner taps once in the dashboard (the owner's own path), and the harness redeploys a fix. A `/veto` reverts the card, and the conductor redeploys | Production is back on the good release within 5 minutes, and the harness confirms with `/health` |

### D. Data

| ID | What must be shown | Passed when |
|---|---|---|
| HT-10 | Postgres is reachable from web, worker and cron | `/items` writes and reads a row; worker and cron rows appear |
| HT-11 | Database migrations run automatically on deploy *(Northflank: a migrate job step in each release flow and in the preview template, before the services deploy)* | A new migration in a PR is applied in the PR copy, then in staging, with no hand step |
| HT-12 | Backups are switched on, and one is restored *(Northflank: the Postgres add-on's scheduled backups, and a backup step in production's release flow)* | A restored copy holds the test rows. The backup schedule and how long backups are kept are noted |
| HT-13 | The bucket stores and returns files. A presigned link opens in a browser. Each environment's bucket is separate *(the portraits app uses Cloudflare R2: one bucket each for production and staging, one shared by the PR copies under a prefix each, and a token limited to each bucket)* | Upload, then download, works, and the link opens on a phone. Staging's token can't read production's bucket |

### E. Background and scheduled jobs

| ID | What must be shown | Passed when |
|---|---|---|
| HT-14 | A **40-minute** job runs to the end without being killed | Progress rows cover the full 40 minutes, and the job ends with "done" |
| HT-15 | A queued job **survives a restart or redeploy** of the worker and carries on where it left off | After a redeploy mid-job, the job resumes and doesn't redo finished steps |
| HT-16 | The cron job runs on its schedule, can be started by hand, and exits *(Northflank: a cron job whose concurrency policy forbids overlaps, started by hand from the dashboard or the API)* | Two scheduled runs and one manual run are logged; an overlap shows as skipped |

### F. Secrets and integrations

| ID | What must be shown | Passed when |
|---|---|---|
| HT-17 | Secrets are set per environment in the host, never in the repo, logs or responses *(Northflank: secret groups, each linked only to its own environment's services and jobs)* | A scan of the repo, the logs and every API response finds no key value |
| HT-18 | One OpenRouter call works from the host, under a spend cap of a few cents. It also confirms the real app's model ids and answer formats before any feature work | `/ai` returns an answer, and the spend is logged with the actual cost the answer reported (the request sends `"usage": {"include": true}`). OpenRouter's model list (`GET /api/v1/models`) contains all five ids in settings (D-52, D-56). One image-edit call returns an image, and its answer's shape is saved as a fixture |
| HT-19 | **GitHub integration**: a read-only, single-repo token reads a file from a private repo (D-32) | `/github` returns the file's first line. The same token can't write: a write attempt is refused |
| HT-20 | The API needs a key | `/secure` answers 401 without a key and 200 with one. The key can be rotated without a deploy |
| HT-21 | The admin page sits behind a login and is usable on a phone | The owner opens `/admin` on a phone, after logging in |

### G. Seeing what's happening

| ID | What must be shown | Passed when |
|---|---|---|
| HT-22 | The harness reads logs and deploy status by itself *(Northflank: its API, for log lines and deployment and release-flow status)* | The harness quotes the failing line from HT-08's broken deploy in its alert on the control issue |
| HT-23 | *withdrawn* (2026-10-21): the conductor reads logs and deploy status through the host's API (HT-22; Northflank's since 2026-10-23); no host MCP server is used | — |
| HT-24 | The owner can see logs and costs on a phone *(Northflank: the dashboard in the phone's browser)* | The owner finds the HT-14 job's logs and the cost so far, from the phone |
| HT-25 | Costs are visible after 24 hours, and a usage alert is set *(Northflank has no hard spending cap, only a billing alert, so short lifetimes and the daily clean-up matter)* | The cost view shows the day's cost, and an alert is set at a chosen amount |

### H. What the harness itself must do (for the harness design)

| ID | What must be shown | Passed when |
|---|---|---|
| HT-26 | The harness runs smoke tests against a **deployed URL** (PR copy or staging; never production) as part of a feature's checks | A card's smoke check runs against the PR copy, with that environment's test credentials from the harness's store, and its result appears in the grade |
| HT-27 | The control issue carries each merge's evidence, alerts and anything waiting for the owner, with `/veto` and `/approve`; the morning digest summarizes deploys, failures and costs (D-62, D-63) | The owner sees a merge's notice and a test alert on the phone, and a `/veto` from the GitHub app is obeyed |
| HT-28 | The harness waits for the owner only for veto windows and `/approve`, and otherwise carries on with every card a question doesn't block | The run doesn't stall on any step that isn't a veto window or an authorization |
| HT-29 | **Teardown**: the throwaway projects (both), their environments, the bucket and the repo are removed, with no running costs left | The host shows no services, and the next day's cost is $0 |
| HT-30 | **A veto after a merge:** `/veto <id>` reverts a merged card, and staging is redeployed without it | Staging's `/health` shows the commit before the card within a few minutes, and the cards built on it are sent back to have their checks run again |
| HT-31 | **A failed health check after a merge** rolls staging back and stops new cards until it's fixed | A merge whose `/health` answers 503 on staging is rolled back automatically; no new card starts; an alert names the failure |
| HT-32 | **Pull-request copies are based on staging, never production, and get only the variables they should.** Each has its own test database and bucket, staging's test credentials and the GitHub token, and **not** the AI key *(Northflank: the preview template links only a preview secret group, which doesn't hold the AI key)* | A PR copy's `/health` names its own environment, database and bucket, none of them production's; the variables it needs are present, and the AI key isn't |
| HT-33 | **The two projects keep production apart** (D-70). The harness's everyday token reaches only the staging project; the production token is held only by the conductor, outside the worker box; production builds and deploys the exact commit it's given *(Northflank: production's release flow, started through the API with the commit; or a `production` branch its build follows, moved only by the conductor)* | With the staging token, every call to the production project is refused. The conductor starts production's release flow for a chosen commit, and production's `/health` shows that commit, with its database backed up before the migration |

## Limits for the test

- **Hosting spend:** at most $5 in total. **AI spend:** at most $0.50.
- **Owner's time:** about an hour, mostly for HT-06, HT-09, HT-21 and HT-24, the steps done on a phone.

## What the owner provides

- A Northflank account (pay as you go), with two projects for the test, one for staging and its previews and one for production, and a token for each (HT-33).
- A Cloudflare R2 bucket and token, or the MinIO add-on, for HT-13.
- The GitHub repo, or permission for the harness to create one.
- The tool's OpenRouter key. Use a separate key with a low limit for the test.
- A read-only GitHub token for a private repo. It can be a test repo, or library-pipeline itself, limited to read.
- A phone with the host's dashboard open in its browser, and the harness's notifications.

## What the result decides

- **All of B, C, E and G pass, and HT-32 and HT-33:** the portraits build uses the same setup on Northflank.
- **HT-03, HT-04, HT-22 or HT-26 fails:** the harness can't yet deploy and test by itself. Fix the harness side first. Only if Northflank itself can't do it is the host reopened (T-01).
- **Anything else fails:** note a workaround in this file, and carry it into the portraits plan.

---

## Change log

- **2026-10-19:** v1 created from tracker T-01 (fully hosted, D-31), D-32 (GitHub token), D-33 (admin page), D-35 (owner can deploy by hand) and the Railway review. Railway is assumed, pending the owner's confirmation in the harness chat.
- **2026-10-19 (evening):** Host decided: Railway (D-36). The Replit spike is skipped. The test no longer picks a host; it proves the harness on Railway. It follows Rev1's shared hosting review once that's copied here.
- **2026-10-19 (evening):** D-39 (the versions of a portrait) puts eight files per portrait in the bucket, including byte-for-byte originals that can be large TIFFs. No new requirement: HT-13 already covers storing and serving files. For the real app, about 540 portraits at roughly 15 MB each is about 8 GB, or roughly $0.12 a month on Railway's buckets.
- **2026-10-19 (evening):** D-42 (storage):
  - the app's bucket is the only store; the library keeps its own copies;
  - backups are the database only, at first. HT-12 (restore one database backup) stays as is;
  - the bucket isn't backed up, so HT-13 needs nothing more.
  - The admin page is read-only, which HT-21 already covers.
- **2026-10-19 (night):** D-44 (the library API):
  - one bearer key, which HT-20 already covers (401 without it, 200 with it, rotation without a deploy);
  - the library's requests are queued for the worker at once, which HT-15 covers (queued jobs survive a redeploy);
  - pull only, so the app makes no outbound call to the library. The test needs no new requirement.
- **2026-10-19 (night):** D-46 (picture sources). The real app calls Wikimedia, the Library of Congress and Wellcome, with no keys, through an allowlist of hosts. The throwaway test already proves outbound calls (HT-18, HT-19), so no new requirement. For the real build, the coverage survey (SRC-14) is a cron or one-off job like HT-16's.
- **2026-10-19 (night):** D-53 (runs):
  - a nightly cron job, which HT-16 already covers (it runs on schedule, can be started by hand, exits, and skips an overlap);
  - a database queue that survives redeploys, which HT-15 covers;
  - no email from the app;
  - Railway's alerts on crashes and failed deploys are the owner's only push notice from the host. Worth adding to HT-25's alert check when the harness chat next revises the test.
- **2026-10-20:** D-55 (security):
  - the real app's admin page uses one password with a 30-day session. HT-21's login can be the same kind;
  - the same OpenRouter key is used in every environment, with low caps for staging and pull-request copies. HT-18's separate low-limit test key remains right for the throwaway test, since it is a different project.
- **2026-10-20:** D-57 (TypeScript, like the library). The throwaway app is now a tiny Node 24 TypeScript app with the real app's stack: Express, Drizzle migrations, `node:test` and the S3 SDK. HT-02 now also proves that OpenCV.js (WebAssembly) and `sharp` build and load on Railway, since the real app's image work depends on them.
- **2026-10-20 (consistency review):** the real app's environment rules (RUN-10):
  - pull-request copies make no paid calls and have no cron;
  - staging has no cron and runs by hand;
  - production's nightly schedule is switched on only at the release.

  The throwaway test can mirror this. HT-16's cron belongs in production, or in one chosen environment, rather than in every PR copy. The trial runs in production before the release.
- **2026-10-20 (morning):** D-58 and D-59. The real app's nightly job also queues teachers whose slots are full, for monthly better-copy searches, and the first-run cap spans several nights. Neither changes the throwaway test.
- **2026-10-20 (Argon's review):**
  - **HT-18 widened:** it also checks the five OpenRouter model ids, the actual cost in the answer, and one image-edit answer's shape, so a wrong id is caught before the build rather than at the first live card.
  - **`railway run` from the owner's PC:** Railway's `DATABASE_URL` uses a private hostname that only resolves inside Railway. The real app's command-line tool uses `DATABASE_PUBLIC_URL` when it's set. If the throwaway app has a command run through `railway run`, it should do the same; HT-12's restore check is unaffected.
  - The real app's outbound client follows redirects by hand and checks each target host, and its allowlist includes the sources' file hosts (`upload.wikimedia.org`, `tile.loc.gov`, `iiif.wellcomecollection.org`). No change to the test.
  - **The face detector:** the real app commits YuNet (`models/`, about 230 KB). If OpenCV.js lacks `FaceDetectorYN`, the app runs the model with `onnxruntime-node`, a native module. HT-02 now also loads `onnxruntime-node` on Railway and runs that model once, so the fallback is proven on the host too.
- **2026-10-21 (the harness's instructions, `Coding Harness Instructions.md`):** this file brought up to the harness's current design (D-62..D-66):
  - **wording:** HT-01's tests run in the harness's worker box, not in WSL directly. The digest as a channel becomes the control issue (HT-05, HT-08, HT-22, HT-27, HT-28); the digest only summarizes. HT-26 is a *smoke* check ("live" now means paid);
  - **HT-05** gains the veto window's rules; the portraits project chose 24 hours (D-66);
  - **HT-09** keeps the owner's own rollback, and adds `/veto` reverting a card;
  - **HT-23 withdrawn:** the conductor uses the Railway CLI, not the MCP server;
  - **HT-30..HT-32 added:** a veto that reverts a merged card and redeploys staging; a failed health check that rolls staging back; pull-request copies without the AI key (the portraits app keeps one key, D-67, and gives it to production and staging only).
- **2026-10-22 (the harness's instructions, as of HD-59):** pull-request copies are based on staging, never production, and the health check names its environment, database and bucket. HT-32 now checks both, and records whether Railway can leave the AI key out of the copies (if it can't, the portraits app relies on stub mode in code, with the key's OpenRouter limit as the ceiling). The throwaway app can also use `deploy.starts_at`, so its early scaffolding never deploys.
- **2026-10-23 (the harness's instructions, HD-60): the host is Northflank, not Railway** (D-70). Railway disclosed on 2026-10-21 that attackers may have read customers' environment variables.
  - Every *(Railway)* note is now a *(Northflank)* one: HT-02 (Dockerfile or buildpacks), HT-03 (a merge to `main` starts the staging pipeline's release flow), HT-04 (preview environments from a preview template), HT-05 (production's release flow, started with the production token), HT-06 and HT-24 (the dashboard in a phone's browser; no app), HT-07 (templates in the repo, synced both ways), HT-08 (readiness and liveness checks), HT-11 (a migrate job step), HT-12 (the Postgres add-on's backups), HT-13 (Cloudflare R2 or the MinIO add-on), HT-16 (a cron job that forbids overlaps), HT-17 (secret groups), HT-22 (Northflank's API), HT-25 (a billing alert, since there's no hard cap), HT-29 (both projects).
  - **HT-32 tightened:** secret groups can be linked to chosen environments, so a PR copy must now lack the AI key, not merely record whether it can.
  - **HT-33 added:** the two projects keep production apart, and production builds and deploys the exact commit the conductor gives it.
  - The owner needs a Northflank account with two projects and a token for each, and R2 or MinIO for the bucket. Any key ever stored in Railway should be rotated.
