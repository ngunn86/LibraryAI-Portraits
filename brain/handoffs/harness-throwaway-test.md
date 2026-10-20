# Harness throwaway test: requirements

**What this is:** the requirements for a small, throwaway app that the build harness builds, deploys, tests and tears down **before** any Nexus Portraits feature work. It proves that the harness and the host can do everything the real app will need. The app itself does nothing useful and is deleted afterwards.

**Who uses it:** the owner plans and runs this test in the harness chat (D-15). This file is the portraits project's list of what the test must prove. **Claude keeps it updated** as portraits decisions change what the hosted app needs. Every change is logged at the bottom.

**Status:** draft v1, 2026-10-19.

- **Host: Railway, decided** (D-36, 2026-10-19). The Replit spike is skipped, so this test is the harness's own proof on Railway, not a way of choosing a host.
- Rev1's `brain/reference/hosting-railway-review.md` is written for both projects. Where it sets plan, region or layout, this test follows it.
- Requirements marked *(Railway)* name Railway features; the rest apply to any host.

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
  bucket    a few test files
environments: production · staging · a temporary one per pull request
```

## Requirements

Each requirement has an ID (HT-nn), what the test must show, and when it counts as passed. IDs are permanent, and new ones are added at the end of their group.

### A. Build and repository

| ID | What must be shown | Passed when |
|---|---|---|
| HT-01 | The harness creates the throwaway repo, or uses one the owner creates, with the project skeleton and an offline test suite | The tests pass locally in WSL and on each pull request |
| HT-02 | The host builds the Node 24 TypeScript app from the repo with no hand-made build steps *(Railway: Railpack, or a Dockerfile)*. *Since D-57:* include one WebAssembly dependency (OpenCV.js) and `sharp`'s native binary, to prove they build and run on the host | The build log shows success for the commit pushed, and `/health` reports that OpenCV.js and `sharp` loaded |

### B. Deploying

| ID | What must be shown | Passed when |
|---|---|---|
| HT-03 | A push to the staging branch deploys staging **without clicking** | Staging's `/health` shows the new commit within a few minutes of the push |
| HT-04 | A pull request gets its own **temporary copy**, with its own URL, database and bucket *(Railway: PR environments)* | The harness finds the PR copy's URL and gets 200 from `/health`. The copy disappears when the PR is closed or merged |
| HT-05 | Promotion to production happens only **after the owner's veto window**, announced in the digest | Production changes only after the window. A veto (reply or tap) stops it |
| HT-06 | The owner's own deploy path works from a phone (D-35 fallback) | The owner deploys or redeploys from the phone in under 2 minutes |
| HT-07 | The project setup lives in the repo, as far as the host allows *(Railway: the Infrastructure-as-Code file, `.railway/railway.ts`; the older `railway.toml` stops being read on 2026-12-01)* | `plan` and `apply` (or the host's equivalent) reproduce the setup. Anything the file can't express is listed in the repo as a one-time dashboard step |

### C. Health checks and rollback

| ID | What must be shown | Passed when |
|---|---|---|
| HT-08 | A deliberately broken release **doesn't go live**: the healthcheck holds it back | The previous release keeps serving, and the failed deploy is reported in the digest |
| HT-09 | Rolling back works: the owner taps once in the dashboard, and the harness redeploys a fix | Production is back on the good release within 5 minutes, and the harness confirms with `/health` |

### D. Data

| ID | What must be shown | Passed when |
|---|---|---|
| HT-10 | Postgres is reachable from web, worker and cron | `/items` writes and reads a row; worker and cron rows appear |
| HT-11 | Database migrations run automatically on deploy *(Railway: pre-deploy command; `drizzle-kit migrate`)* | A new migration in a PR is applied in the PR copy, then in staging, with no hand step |
| HT-12 | Backups are switched on, and one is restored *(Railway: scheduled backups, point-in-time recovery)* | A restored copy holds the test rows. The plan that's needed is noted (Hobby or Pro) |
| HT-13 | The bucket stores and returns files. A presigned link opens in a browser. Each environment's bucket is separate | Upload, then download, works, and the link opens on a phone. Staging can't see production's files |

### E. Background and scheduled jobs

| ID | What must be shown | Passed when |
|---|---|---|
| HT-14 | A **40-minute** job runs to the end without being killed | Progress rows cover the full 40 minutes, and the job ends with "done" |
| HT-15 | A queued job **survives a restart or redeploy** of the worker and carries on where it left off | After a redeploy mid-job, the job resumes and doesn't redo finished steps |
| HT-16 | The cron job runs on its schedule, can be started by hand, and exits *(Railway: `railway cron run`; an overlapping run is skipped)* | Two scheduled runs and one manual run are logged; an overlap shows as skipped |

### F. Secrets and integrations

| ID | What must be shown | Passed when |
|---|---|---|
| HT-17 | Secrets are set per environment in the host, never in the repo, logs or responses | A scan of the repo, the logs and every API response finds no key value |
| HT-18 | One OpenRouter call works from the host, under a spend cap of a few cents | `/ai` returns an answer, and the spend is logged |
| HT-19 | **GitHub integration**: a read-only, single-repo token reads a file from a private repo (D-32) | `/github` returns the file's first line. The same token can't write: a write attempt is refused |
| HT-20 | The API needs a key | `/secure` answers 401 without a key and 200 with one. The key can be rotated without a deploy |
| HT-21 | The admin page sits behind a login and is usable on a phone | The owner opens `/admin` on a phone, after logging in |

### G. Seeing what's happening

| ID | What must be shown | Passed when |
|---|---|---|
| HT-22 | The harness reads logs and deploy status by itself *(Railway: CLI `railway logs`, `railway deployment list`, ideally as JSON)* | The harness quotes the failing line from HT-08's broken deploy in its digest |
| HT-23 | Claude Code can use the host's MCP server for reading and diagnosis *(Railway: `railway mcp`; it asks before destructive actions)* | One read-only question about the project ("what failed in the last deploy?") is answered through the MCP server |
| HT-24 | The owner can see logs and costs on a phone | The owner finds the HT-14 job's logs and the cost so far, from the phone |
| HT-25 | Costs are visible after 24 hours, and a usage alert is set | The cost view shows the day's cost, and an alert is set at a chosen amount |

### H. What the harness itself must do (for the harness design)

| ID | What must be shown | Passed when |
|---|---|---|
| HT-26 | The harness runs smoke tests against a **deployed URL** (PR copy, staging, production) as part of a feature's checks | A feature card's live check runs against the PR copy, and its result appears in the grade |
| HT-27 | The harness's digest reports deploys, failures, costs and anything waiting for the owner, and offers the veto | The digest reaches the owner's phone with those items and a way to veto |
| HT-28 | The harness waits for the owner only where a card says so (veto windows, one-tap deploys), and otherwise carries on | The run doesn't stall on any non-veto step |
| HT-29 | **Teardown**: the throwaway project, its environments and the repo are removed, with no running costs left | The host shows no services, and the next day's cost is $0 |

## Limits for the test

- **Hosting spend:** at most $5 in total. **AI spend:** at most $0.50.
- **Owner's time:** about an hour, mostly for HT-06, HT-09, HT-21 and HT-24, the steps done on a phone.

## What the owner provides

- A host account (Railway Hobby to start).
- The GitHub repo, or permission for the harness to create one.
- The tool's OpenRouter key. Use a separate key with a low limit for the test.
- A read-only GitHub token for a private repo. It can be a test repo, or library-pipeline itself, limited to read.
- A phone with the host's dashboard and the harness's notifications.

## What the result decides

- **All of B, C, E and G pass:** the portraits build uses the same setup on Railway.
- **HT-03, HT-04, HT-22 or HT-26 fails:** the harness can't yet deploy and test by itself. Fix the harness side first. Only if Railway itself can't do it is the host reopened (T-01).
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

