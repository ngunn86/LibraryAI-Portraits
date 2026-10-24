# Release checklist (the owner's)

Steps around the release that a card can't do: they need the owner, or they take longer than a card may run. The harness alerts on the control issue when each one is due (D-63). Tick them here or in chat.

## Before the hosting card (Phase 1, F-36)

All of these are in Northflank's and Cloudflare's dashboards, in a browser (Northflank has no phone app). Secrets go into Northflank's **secret groups**: `production` in the production project, `staging` and `preview` in the staging project (D-70).

- [ ] **Rotate any key you ever put in Railway** (Railway's disclosure of 2026-10-21): make a new one at its provider, switch the old one off, and use only the new one below.
- [ ] **O-8:** a Northflank account and the two projects set up with the harness chat in the layout the architecture gives (a shared build service in staging, web and worker services in each, Postgres, the `pr-copy` preview blueprint), this repo linked, the three secret groups (`production`; `staging` and `preview`), each with `PORTRAITS_ENV` set to its own name and its own random `SESSION_SECRET`, a billing alert (about $60 a month), notifications for crashes, failed health checks and failed releases, and the two tokens for the harness (one per project), connected with `harness hosting connect`.
- [ ] **O-14:** Cloudflare R2: the three buckets (`portraits-production`, `portraits-staging`, `portraits-previews`, the last deleting objects after 7 days), one token per bucket, and their values in the matching secret group.

## Before the build's first smoke checks (Phase 1, F-49)

- [ ] **O-13:** the ops keys (one per secret group), and the test admin password and library key (staging and preview groups only, with different values in each), set in Northflank and in the harness's store.

## Before Phase 2's smoke checks (F-31, F-38)

- [ ] **O-9:** the GitHub token, and **O-10:** the User-Agent contact, set in all three secret groups; O-10 in the harness's store too, for recordings.

## Before the first live card (F-27)

- [ ] **O-4:** the OpenRouter key set in the **production and staging secret groups only** (never in the preview group). Its limit at OpenRouter: **$50, no reset** (D-67).

## The release (F-47): production's first deploy

- [ ] The harness posts the promotion notice on the control issue. `/veto` within **24 hours** if anything looks wrong (D-66). The nightly schedule is on from this first deploy.
- [ ] **Raise the key's limit at OpenRouter by $100**, for the first pass ($150 in all since the key was made). Do this before the window ends; if you don't, the first night simply stops at the limit.
- [ ] **O-11:** make the library's key: in Northflank's dashboard, open a shell on production's web service and run `node dist/cli.js keys new`. Copy it into the library's settings. It's shown once.

## During the first pass (the nights it takes)

- [ ] Each morning, glance at the admin site's front page: the night's run, the first pass's spend against $100, errors.
- [ ] When the front page says the first pass is done, **switch the key's limit at OpenRouter to $40 a month** (production's $30 and staging's $10, D-67).
- [ ] Check the teachers to identify, and add the suggested ids and dates to `authors.csv` (O-3). They're searched on a later night.
- [ ] Look at the trial board's engraving results (F-52). If engravings look bad, reply `/direct turn off engravings` on the control issue (D-47).

## After

- [ ] Nothing regular. The admin site's front page lists anything that needs you.
