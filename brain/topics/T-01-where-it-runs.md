# T-01 · Where the app runs and how the library reaches it

**Status:** in discussion (2026-10-19). The owner is leaning towards **fully hosted**, "simply for the goal of testing everything we need to test with the harness". The owner asked for a feasibility review. If hosted, Claude builds the API as proposed: the library both pulls records and sends approvals and requests back.

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

## Sources (checked 2026-10-19)

- Replit deployment pricing: https://docs.replit.com/billing/deployment-pricing.md
- Railway plans: https://docs.railway.com/reference/pricing/plans
- Render Blueprint spec: https://render.com/docs/yaml-spec
- Replit and GitHub deploys (third-party, unverified): https://cdn.jsdelivr.net/npm/@intentsolutionsio/replit-pack@1.0.3/skills/replit-ci-integration/SKILL.md
