# T-01 · Where the app runs and how the library reaches it

**Status: decided (2026-10-19). Host: Railway** (D-36), from the library's planning, which wrote one hosting review for both projects (Rev1 `brain/reference/hosting-railway-review.md`, to be copied to `brain/reference/rev1/`). The Replit spike is skipped.

- **Decided:**
  - Fully hosted, with a two-way API (D-31).
  - The authors list through GitHub (D-32).
  - An admin page to browse (D-33).
  - Extra keys are fine when needed, kept to a minimum (D-34).
  - The owner can deploy by hand from Replit (D-35).
- **Host:** Railway (D-36). The comparison below is kept for the record.

*History:* the owner leaned towards fully hosted "simply for the goal of testing everything we need to test with the harness" and asked for a feasibility review. The review follows.

## The options (as put to the owner)

| | Processing | API | Notes |
|---|---|---|---|
| A | Owner's PC | none (files and an index on Drive) | Cheapest, but not an API |
| B | Owner's PC | Small hosted service | Earlier recommendation; the PC stays private |
| **C** | **Hosted** | **Hosted, the same app** | **The owner's lean: it exercises the most for the harness** |
| D | Owner's PC | The PC, through a tunnel | Not recommended |

## Is fully hosted feasible? Yes

The heavy work isn't done by the app. Image editing and the vision checks run at OpenRouter. What the app does itself is modest:

| Need | What the prototype shows | What that means for hosting |
|---|---|---|
| CPU | Recipe 0.3.1 takes about 10 s per portrait on 2 vCPU here (descreen, crop, halftone at 4× supersampling, outline) | A small instance is enough. A full run is limited by AI call times (tens of seconds each), not by CPU |
| Memory | The 4× halftone holds a few 4,000 × 4,000 arrays at once, so a few hundred MB at peak | 1–2 GB is comfortable. Supersampling at 3×, or in tiles, cuts it further if needed |
| Local models | Only the face detector (YuNet, a few hundred KB). No background-removal model, since the cut-out comes from the AI copy's green background | Nothing large to install |
| Run length | About 1–3 min per portrait, mostly waiting on AI. The first run is a few hours | It needs a background worker or a scheduled job, not a web request |
| Storage | 3 versions per portrait: the full original, plus two 1,000 px PNGs. A few MB per portrait, ~600 portraits at most | A few GB at most. Cheap anywhere |
| Data | Teachers, portraits, versions, rights log, jobs, spend | A small Postgres database (replacing the SQLite planned before) |

## What a hosted app is made of

```
             ┌──────────────── hosted app (one repo, one deploy) ────────────────┐
library  ──► │  API (read records and files; send approvals and requests)        │
owner    ──► │  admin pages (portraits by teacher, run status, trial board)      │
             │  worker (runs jobs from a queue in the database, one at a time)   │──► OpenRouter (AI)
schedule ──► │  scheduled run (sync the teacher list, process new teachers)      │──► Commons, LoC, Wellcome…
             │  Postgres (records, rights log, jobs, spend)                      │
             │  file storage (by teacher: original, white, black-and-white)      │
             └───────────────────────────────────────────────────────────────────┘
secrets (in the host): OpenRouter key · library API key · a read-only GitHub token for authors.csv
```

## What it changes in the plan

- **No dependence on your PC.** The tool runs whether or not your PC is on. The harness still builds on your PC, then deploys.
- **No Google Drive hand-off.** Portraits live in the app's storage, organised by teacher (D-27), and the library pulls them through the API (D-28). Q-03 (synced folder vs Drive API) and the request and status files go away.
- **`authors.csv` must be fetched from GitHub.** library-pipeline is a private repo, so the app needs a **read-only GitHub token** limited to that one repo. That's a second, non-AI key. The alternative is for you to upload the file through the admin page.
- **A small admin page becomes natural.** Browsing portraits by teacher, run status and the trial board all live in the app. This also tests the harness on building a UI, which Rev1 needs too.
- **More to build.** Roughly 8–12 more feature cards: the API, database and migrations, file storage, the job queue and worker, the scheduler, keys and auth, deploy configuration, the admin pages, and smoke tests against the live app.
- **Security matters more.** The API is on the internet. It needs keys for the library and for you, rate limits, and no secrets in logs (T-21).
- **Running costs** are a small monthly hosting fee on top of AI usage (below).

## Value for testing the harness

A hosted build exercises nearly everything Library-AI Rev1 will need:

- an API;
- a database with migrations;
- file storage;
- background jobs;
- schedules;
- secrets;
- deploys to staging and production;
- smoke tests against a live URL;
- reading logs;
- rolling back.

Finding the harness's gaps on this small app is cheaper than finding them on Rev1. Those deploy steps are also **requirements on the harness itself**, which is being designed in another chat. They're tracked as T-27 so that chat can pick them up.

## Risks, and how to keep them small

| Risk | How we handle it |
|---|---|
| The first harness project gets bigger, with more places to get stuck | **Build in layers.** (1) The processing core as a plain Python library, fully tested offline. (2) The database, storage and worker. (3) The API and admin pages. (4) Deployment and live smoke tests. Each layer is finished and tested before the next starts, and the UI cards can be parked |
| The host can't be deployed to without someone clicking | **A deploy spike first** (below). If the host fails it, pick another before any feature work |
| Hosting costs creep | Small instances; the worker only runs when there's work; cost alerts set in the host |
| A public API is attacked or misused | Keys, rate limits, read-only by default, no secrets in responses or logs (T-21) |

## Which host (part of this decision)

| | Replit | Railway | Render |
|---|---|---|---|
| Same platform as Library-AI and Rev1 | **yes**: a real rehearsal for Rev1 | no | no |
| Deploys without clicking (push to GitHub, or a CLI or API) | **Uncertain.** GitHub sync exists; a deploy API is thinly documented. **The spike must prove it** | yes: GitHub deploys and a CLI | yes: deploy on push, and a Blueprint file describes the whole app |
| API plus a background worker | A Reserved VM runs both, always on. Or Autoscale for the API (it idles after 15 min) plus a Scheduled deployment for runs | yes | yes (web service plus background worker, and cron jobs) |
| Postgres and file storage | yes, built in (Postgres and Object Storage) | yes (Postgres service, volumes) | yes (Postgres, disks) |
| Indicative cost | Reserved VM, shared 0.5 vCPU / 2 GB: **$15/month**. Autoscale or Scheduled: $2/month base plus usage | Hobby **$5/month** with $5 usage included; then about $10 per GB of RAM and $20 per vCPU per month | Comparable small-service pricing (check at the spike) |
| Staging and production | to be checked in the spike | environments | preview environments |

**Proposal:** try **Replit first**, because rehearsing Rev1's platform is the point. Keep **Railway** (or Render) as the fallback if Replit can't be deployed to hands-free.

## The deploy spike (about an hour, before feature work)

A throwaway "hello" app, deployed the way the harness would do it, proves seven things:

1. A push to a GitHub branch deploys it, or a command or API call does, with no clicking.
2. A staging copy and a production copy can exist side by side.
3. Secrets are set in the host and reach the app.
4. Postgres and file storage work from the app.
5. A background or scheduled job runs for over 30 minutes without being killed.
6. Logs can be read from the command line or an API.
7. A bad deploy can be rolled back.

If Replit passes all seven, the decision is Replit. If it fails on 1 or 6, the harness can't run it unattended, so use Railway or Render.

## Recommendation

**Go fully hosted (C).** It's feasible, the processing needs are small, and it tests the harness on the full set of things Rev1 will need. Build it in layers so a stuck layer doesn't sink the rest. Settle the host with the deploy spike: Replit first, Railway or Render as the fallback. The API both serves records and takes the library's approvals and requests back.

## Sub-decisions for the owner

1. Fully hosted (C)? *(The owner's lean.)*
2. Run the deploy spike, Replit first, with Railway or Render as the fallback?
3. Is a read-only GitHub token for `authors.csv` acceptable, or would you rather upload the file?
4. Include a small admin page for browsing portraits by teacher? (Recommended; it also tests UI work.)

## Hosts that meet our requirements (owner asked for options beyond Replit, 2026-10-19)

### What the host must do

| # | Requirement | From |
|---|---|---|
| H1 | Run a Python web app (the API and admin pages) that the library and the owner can reach at any time. A few seconds' wake-up is acceptable | D-28, D-33 |
| H2 | Run a long background job (hours) and a schedule | D-31, T-19 |
| H3 | Postgres | T-07 |
| H4 | Durable file storage, a few GB | D-26, D-27 |
| H5 | Secrets: OpenRouter, GitHub (read-only), the library's API key | D-19, D-32, D-34 |
| H6 | Deploy from GitHub, automatically or with one tap from a phone | D-35 |
| H7 | A staging copy beside the live one | T-27 |
| H8 | Logs and a dashboard usable from a phone; ideally a CLI the harness can read | D-35, T-27 |
| H9 | Low cost (aim: about $25/month or less) and low complexity (one platform for everything, if possible) | D-34 |
| H10 | Bonus: the same platform as Library-AI and Rev1, so this build rehearses Rev1's deployment | goal of the harness test |

### The candidates

| | **Replit** | **Railway** | **Render** | **DigitalOcean App Platform** | **Google Cloud Run** |
|---|---|---|---|---|---|
| H1 web app | Autoscale ($2/month plus usage; idles after 15 min) or Reserved VM (shared 0.5 vCPU / 2 GB, $15/month) | A service, billed by usage | A web service (paid Starter tier; free services sleep after 15 min) | A web service from $5/month (512 MiB) | A service that scales to zero |
| H2 long job and schedule | A Reserved VM runs a worker; Scheduled deployments ($2/month plus compute) | A worker service plus cron schedules | A background worker (paid) plus cron jobs ($1/month minimum, per minute) | Workers and jobs | Cloud Run Jobs plus Cloud Scheduler |
| H3 Postgres | Built in | Postgres service | Render Postgres (storage $0.30/GB/month) | Managed Postgres from $15/month | Cloud SQL, or an outside Postgres (for example Neon) |
| H4 files | Object Storage, built in | Volumes ($0.15/GB/month; a volume attaches to one service) | Disks ($0.25/GB/month; a disk attaches to one service) | Spaces from $5/month (250 GB) | Cloud Storage |
| H6 deploy | Deploy button (phone OK); GitHub sync | Automatic from GitHub branches | Automatic on push; one Blueprint file describes the app | Automatic from GitHub | Through the gcloud CLI or CI; more setup |
| H7 staging | A second deployment, set up by hand | Built-in environments, plus temporary copies for pull requests | Preview environments (check the plan) | A second app | A second service |
| H8 logs, phone | Dashboard and mobile app | Dashboard and CLI | Dashboard and CLI | Dashboard and `doctl` CLI | Console and `gcloud` |
| H9 rough monthly cost | About $15–20 (Reserved VM, plus database and storage usage) | About $5–20 (Hobby $5 includes $5 of usage; then about $10 per GB of RAM and $20 per vCPU per month) | Hobby workspace $0, plus paid web, worker, Postgres and disk (check current rates) | About $30 ($5 web + $5 worker + $15 Postgres + $5 Spaces) | Near $0 when idle, billed by use; plus the database |
| H10 same as Library-AI | **yes** | no | no | no | no |
| Complexity for the owner | **lowest**: already known | low | low to medium | medium | highest (cloud console, permissions) |

**Notes:**
- On Railway and Render a disk or volume attaches to one service. So either the API and the worker run as one service, or files go to a shared object store such as Cloudflare R2 (free up to 10 GB, S3-compatible, one more key).
- On Replit, Object Storage is shared by the app's deployments.

### Recommendation

- **Replit**, if rehearsing Rev1's platform matters most. That is the purpose of this build, and the owner is fine deploying from a phone (D-35).
  - Everything is built in: a Reserved VM running the API and the worker together, Postgres, Object Storage, Secrets and Scheduled jobs.
  - It's the platform the owner already uses.
- **Railway**, if the harness should also exercise fully automatic deploys and staging. Railway has environments, temporary copies per pull request and GitHub deploys, and it's cheap.
- Render and DigitalOcean meet the requirements, but don't beat those two on anything that matters here.
- Cloud Run is the cheapest when idle, but the most setup for a beginner.

**Suggested next step:** a short check on the chosen host before feature work. Confirm:

- a background job runs for over 30 minutes;
- Postgres and file storage are reachable from the app;
- secrets work;
- logs can be read from a phone;
- a staging copy can sit beside the live one.


## Railway in detail (owner asked to explore it, 2026-10-19)

The owner may move Library-AI to Railway too, and likes the idea of the harness deploying and testing by itself. If Library-AI moves, Railway also gets this build's "rehearsal for Rev1" value (H10).

### How our app would sit on Railway

```
Railway project "nexus-portraits"   (one GitHub repo)
  environments:  production · staging · a temporary one per pull request
  services:
    web       API + admin pages (Python); /health checked before each deploy goes live
    worker    runs queued jobs (portraits) from Postgres; always on, or woken on a schedule (T-19)
    cron      nightly: sync the teacher list from GitHub, queue new teachers; exits when done
    postgres  Railway Postgres (a service with a volume); backups switched on
  bucket      "portraits": S3-compatible storage, one per environment (originals, white, black-and-white)
  variables   OPENROUTER_API_KEY · GITHUB_TOKEN (read-only, library-pipeline) · LIBRARY_API_KEY · admin login
              (database and bucket credentials are filled in by Railway)
```

### How it meets the requirements

| # | Requirement | On Railway |
|---|---|---|
| H1 | Web app always reachable | A web service. A **healthcheck** (`/health`) must answer before traffic switches to a new deploy, so a broken release never goes live |
| H2 | Long job and schedule | A worker service, plus a **cron service**. A cron run must finish and exit; a run is *skipped* if the previous one is still going. `railway cron run` starts one by hand. No time limit is documented, so the spike checks a 40-minute run |
| H3 | Postgres | Railway Postgres is a service with a volume. **Backups** can be scheduled (daily, kept 6 days; weekly, kept a month; monthly, kept 3 months), and **point-in-time recovery** can be switched on. Which plans include these: check in the spike |
| H4 | Files | **Storage Buckets**: S3-compatible, $0.015 per GB-month, free egress and free operations, private, with presigned links. Each environment gets its own bucket, and any service can use it. This avoids the "one volume per service" limit |
| H5 | Secrets | Variables per environment. Database and bucket credentials are referenced automatically |
| H6 | Deploys | **Automatic from GitHub branches.** The CLI also deploys (`railway up`, `railway redeploy`) |
| H7 | Staging | **Environments** (production, staging), plus a **temporary environment per pull request**, removed when it's merged or closed |
| H8 | Logs | The CLI (`railway logs`, `railway deployment list`) and the web dashboard. There's also an **MCP server for Claude Code** (`railway mcp`, using the CLI's login). It can list services, redeploy and analyse logs; destructive actions ask for confirmation |
| H9 | Cost | Hobby **$5/month, including $5 of usage**. After that: RAM $10/GB-month, CPU $20/vCPU-month, volumes $0.15/GB-month, buckets $0.015/GB-month, egress $0.05/GB. Estimate for this app: **about $8–15/month** (a small web service, the database, a worker that mostly idles, a few GB in a bucket). Staging adds a little unless it's put to sleep when idle |
| Rollback | — | One click in the dashboard to an earlier deploy (it reuses that build, so it takes seconds), within the plan's retention window. The CLI can redeploy or restart |

### What the harness could do by itself on Railway

1. **Open a pull request.** Railway creates a temporary copy with its own database and bucket. The harness runs the smoke tests against that copy's URL.
2. **Merge.** Staging deploys automatically. The harness runs the smoke tests again and reads the logs (CLI or MCP).
3. **Promote.** After the owner's veto window in the digest, production deploys, either by merging to the production branch or with a CLI command. The healthcheck blocks a broken release.
4. **Recover.** If something slips through, the owner rolls back with one click (from a phone), and the harness redeploys the fix.

### Caveats to know about

- **The project-file format is changing.** Railway's older per-service config file (`railway.json` / `railway.toml`) stops being read on **2026-12-01**. Its replacement, "Infrastructure as Code", describes the whole project in one file (`.railway/railway.ts`; Python and Go versions are still in beta) and is applied with `railway config plan` / `apply`, or by a GitHub Action when a pull request merges.
  - It's new, and some users report gaps.
  - Plan: use the TypeScript file and keep it small. Anything it can't do is set once in the dashboard and noted in the repo.
- **Volumes cause a brief pause on redeploy.** Only the database uses a volume. App files live in the bucket, so web and worker deploys stay seamless.
- **Cron runs must exit,** and overlapping runs are skipped. That suits a "process what's queued, then stop" worker.
- **The MCP server needs a person's login, not a project token.** Its destructive actions ask for confirmation, so the harness should use the CLI with a token for routine deploys, and the MCP server for reading and diagnosis. To verify in the spike.
- **For Library-AI** (if it moves): check Postgres extensions such as pgvector, and backups, in that project's own planning.

### The deploy spike on Railway (about an hour)

1. Create the project from the GitHub repo, with production and staging environments and temporary copies for pull requests switched on.
2. Deploy a "hello" Python web app with `/health`. Check that a push to staging deploys it, and that a pull request gets its own URL.
3. Add Postgres and a bucket. The app writes to and reads from both, and a presigned link opens a file.
4. A cron service runs a 40-minute job, and `railway cron run` starts it by hand.
5. From WSL, `railway logs` and `railway deployment list` work, as does the MCP server in Claude Code.
6. A broken build is held back by the healthcheck, and a dashboard rollback works.
7. Note which plan includes Postgres backups, point-in-time recovery, and how long rollback images are kept.
8. Read the cost view after a day.

### Recommendation

**Railway, on the Hobby plan to start.** Move to Pro ($20/month) only if the spike shows backups or rollback retention need it.

- It fits every requirement.
- It lets the harness deploy and test by itself.
- It costs about $8–15/month.
- If Library-AI moves there too, this build is a direct rehearsal.

## Sources (checked 2026-10-19)

- Replit deployment pricing: https://docs.replit.com/billing/deployment-pricing.md
- Railway plans: https://docs.railway.com/reference/pricing/plans
- Render Blueprint spec: https://render.com/docs/yaml-spec
- Replit and GitHub deploys (third-party, unverified): https://cdn.jsdelivr.net/npm/@intentsolutionsio/replit-pack@1.0.3/skills/replit-ci-integration/SKILL.md
- Render costs and free-tier limits: https://render.com/articles/how-much-does-cloud-application-hosting-cost-for-small-businesses
- Railway environments: https://docs.railway.com/reference/environments
- DigitalOcean pricing summary (third-party): https://kuberns.com/blogs/digitalocean-pricing/
- Railway cron jobs (CLI): https://docs.railway.com/cli/cron
- Railway Storage Buckets: https://docs.railway.com/storage-buckets
- Railway MCP server: https://docs.railway.com/ai/mcp-server
- Railway volumes: https://docs.railway.com/volumes/reference
- Railway rollback and healthchecks: https://docs.railway.com/guides/roll-back-bad-deploy
- Railway Postgres backups: https://docs.railway.com/guides/postgres-backups-restores
- Railway config as code (deprecated 2026-12-01): https://docs.railway.com/config-as-code/reference
- Railway Infrastructure as Code: https://docs.railway.com/infrastructure-as-code
- Community feedback on Railway IaC: https://station.railway.com/feedback/sharing-my-frustration-with-railway-iac-d953c8ba

