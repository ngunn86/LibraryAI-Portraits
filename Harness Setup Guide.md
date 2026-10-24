# Harness Setup Guide: hosting a project for the Coding Harness

**From:** the Coding Harness chat · **Written** 2026-10-24, from setting up the harness's throwaway test (harness HD-73, HD-75, HD-76) · **For:** this repo's planning chat, when the owner is ready to set up hosting for the harness's build.

This file says how to set up a project's Northflank and Cloudflare R2 hosting with the owner, the way that worked. Use it with this repo's `Coding Harness Instructions.md`, which says what layout the harness needs and why; this file says how to build it. The harness chat updates both files when something changes.

## 1. Who does what (the owner's standing decision, harness HD-73)

- **Claude does the dashboard work itself** in the built-in browser of the owner's Claude app: projects, services, add-ons, secret groups, the preview blueprint, roles, buckets, and the forms for each key. The owner said: "you are absolutely going to do as much of the setup as you can." Don't walk the owner through clicks Claude can make.
- **The owner only:** signs in, confirms, clicks the final button that reveals a key or token, copies secrets, pastes secret values, and runs commands in Ubuntu.
- **Claude never types or reads a secret.** Fill every form up to the button that shows the key; let the owner click it. Don't take a screenshot while values are on screen; say so when you stop looking.
- **Check before deleting anything.** Before suggesting the owner delete something, check what later stages need. A test setup was once deleted that the next stage needed.
- **Plain language, one screen at a time, complete steps.** The owner calls themselves a beginner. Number the steps and say exactly which button and where. Don't guess: when unsure what a screen shows, take a screenshot or read the docs first. When the owner reports something odd, look before answering.

## 2. Before starting

1. **Read** this repo's `Coding Harness Instructions.md` (the layout, `harness.yaml`, deploys) and this project's spec for its processes, environment variables, add-ons and storage.
2. **Write the plan** in this repo's notes, as a checklist the owner can tick:
   - **The two Northflank projects:** `<project>-staging` and `<project>-production`, in the same region.
   - **Staging:** add-ons, the build service, deployment services (each with its start command, port, health checks and size), jobs, secret groups, and the `pr-copy` blueprint if the project uses pull-request copies.
   - **Production:** add-ons with backups, deployment services on staging's shared builds, secret groups.
   - **The R2 buckets.**
   - **The owner inputs:** each secret, where it goes, who makes it.
3. **Ask the owner to sign in** to Northflank and Cloudflare in the browser panel. Later, also OpenRouter and GitHub, where those keys are needed.

## 3. Building it in Northflank (Claude, in the browser)

Proved in the dashboard on 2026-10-24. Names in `code` are what to click or type.

### Staging project

- **Postgres add-on:** `Create new` → `Addon` → PostgreSQL, newest version, `Development` preset. Choose the plan from the list; the smallest that suits, such as `nf-compute-20` (0.2 vCPU, 512 MB). 6 GB storage is the minimum. Private, TLS on.
- **The build service** (`Service` → `Build`):
  - **Name:** `build`. The harness looks for this name.
  - **Repo:** the project's repo. Its rows only list repos Northflank's GitHub app may see; ask the owner to grant access if it's missing.
  - **Build rules:** remove the default "every pull request" rule and keep the branch rule `main`. Copies build their own branch through the blueprint, and the harness builds `main` after each merge.
  - **Dockerfile:** location and build context as the project's `Dockerfile` needs.
  - **Build sharing:** Advanced build settings → Cross project access → `Share build access to other projects`. Production needs it.
  - It's fine to create it before the app has a `Dockerfile`; the first build happens after the card that adds it.
- **Each deployment service** (`Service` → `Deployment` → `Northflank` → Link build service `build`, branch `main`, no build yet):
  - **Plan:** the size the spec needs. The 256 MB plan is too small for image libraries such as onnxruntime.
  - **Ports:** a web service gets `8080` HTTP Public, plus a `PORT=8080` runtime variable if the app reads it.
  - **Start command:** Advanced → Docker runtime mode → `Custom command`, such as `node src/web.ts`.
  - **After creating it:**
    - **Turn CD off** with the `CD` switch at the top of the service page. The harness decides which build runs.
    - **Add the health checks** under More → Health checks: a readiness probe on the health path and a liveness probe, both on the public port. Save.
  - The "Create service" button moves as sections open, so take a screenshot before each click. A service created too early can be finished on its own page.
- **Jobs** (cron): `Job` → schedule on, cron expression, concurrency `Forbid` → `Northflank` source, link `build`/`main` → `Custom command`.
  - **Known gap (HD-75):** the harness moves only deployment services, so a job follows the latest `main` build by itself and isn't rolled back with the services. Flag any job whose rollback matters; the harness will need to move jobs too.
- **Secret group `staging-env`:**
  - **Type and scope:** `Secret values`, scope `Runtime`.
  - **Values:** switch the editor to `Env` and type every variable the app reads, one per line. Fill the non-secret ones (environment name, endpoints, bucket names, caps) and leave the secret ones empty (`NAME=`) for the owner.
  - **Linked addons:** `Show addons` → `Configure` → tick `POSTGRES_URI` → add the alias `DATABASE_URL`, or whatever name the app reads.
  - **Restriction:** Advanced → `Restrict secret group` → apply to the staging services and jobs by name. This keeps it away from copies, whose services have other names.
- **The `pr-copy` preview blueprint**, if the project uses copies (`Previews` → `Create preview blueprint`):
  - **Name:** `pr-copy`.
  - **Trigger:** `Git push` on the repo, branch rule `harness/*`, `Enable trigger` **off**. The harness starts copies itself through the API.
  - **Nodes:** add them in the Visual tab, then edit in the Code tab. Use the node formats below, and name every resource after the copy (`${args.previewId}-…`, HD-71). A working blueprint to copy is saved in `ngunn86/harness-throwaway` at `brain/hosting/pr-copy.json`.
  - **Copies' secrets come from the blueprint's argument overrides,** never a project-wide group (HD-75).
    - The copy's own secret group holds `${args.NAME}` for each secret, plus its plain values: the environment name `preview`, the per-copy prefix `${args.previewId}/`, and staging's endpoints and bucket.
    - The owner pastes the values once in the blueprint's Settings → `Argument overrides`, which Northflank stores apart from the template.
    - Copies never get a paid AI key.
  - **Settings:** `Allow preview environments to expire`, 3 hours.
- **Node formats** (as Northflank writes them):
  - **Build:** `{"kind":"BuildSource","spec":{"id":"build","type":"service","branch":"${refs.<trigger name>.branch}","sha":"${refs.<trigger name>.sha}", …},"ref":"build-source-1"}`
  - **Database:** `{"kind":"Addon","spec":{"name":"${args.previewId}-db","type":"postgresql","version":"18","billing":{"deploymentPlan":"nf-compute-20","storage":6144,"replicas":1,"storageClass":"nvme"},"tlsEnabled":true,"tags":["${args.previewId}"]},"ref":"argspreviewid-db"}`
  - **Secret group:** `{"kind":"SecretGroup","spec":{"name":"${args.previewId}-env","type":"secret","secretType":"environment","priority":10,"restrictions":{"restricted":true,"tags":["${args.previewId}"]},"tags":["${args.previewId}"],"secrets":{"variables":{…}},"addonDependencies":[{"addonId":"${refs.argspreviewid-db.id}","keys":[{"keyName":"POSTGRES_URI","aliases":["DATABASE_URL"]}]}]},"ref":"argspreviewid-env"}`
  - **Service:** `{"kind":"DeploymentService","spec":{"name":"${args.previewId}-web","deployment":{"instances":1,"docker":{"configType":"customCommand","customCommand":"node src/web.ts"},"internal":{"id":"${refs.build-source-1.nfObjectId}","branch":"${refs.build-source-1.branch}","buildId":"${refs.build-source-1.id}"}},"billing":{"deploymentPlan":"nf-compute-20"},"ports":[{"name":"p01","internalPort":8080,"public":true,"protocol":"HTTP"}],"runtimeEnvironment":{"PORT":"8080"},"tags":["${args.previewId}"]},"ref":"argspreviewid-web"}`

### Production project

- **Postgres:** the same as staging, plus Advanced → `Backup schedules` → `Daily`, kept for the days the project's spec asks.
- **Each deployment service:** as in staging, except Link build service → `Select project` → the staging project → `build`. Then CD off and the health checks.
- **Secret group `production-env`:** production's values and its own database link, restricted to production's services.

### The two API roles (Team → `Access roles`)

- **One role per project:** `harness-<project>-staging` and `harness-<project>-production`.
- **Project limit:** `Grant this role access only to specific projects` → that one project.
- **Permissions:** `Select all` in every **Project permissions** section, nothing in any **Team permissions** section (Global Secrets, Networking, Templates, Cloud, Platform, Observability, Git, Admin).
- **Members:** add the owner on the role's Members tab, then confirm in the second "Add members" pop-up. A role without its maker as a member can't be chosen for a token.
- **Reuse:** a leftover role can be reused; check its project limit and permissions.

## 4. Cloudflare R2 (Claude)

- **Buckets:** R2 Object Storage → `Create bucket`, one per environment, such as `<project>-staging` and `<project>-production`. Private.
- **Endpoint:** `https://<account id>.r2.cloudflarestorage.com`. The account ID is in the dashboard address.

## 5. The owner's part, in this order

What worked: Claude fills each form, the owner clicks the last button and copies the value; "done" moves to the next. Before starting, tell the owner:

> Open Notepad as a scratch pad. Paste each key there with a label (like `staging S3_ACCESS_KEY_ID`), because each site shows it only once and most go in two places. Delete the file once the run has started.

1. **R2 keys**, one per bucket.
   - Claude opens R2 → API Tokens → `Create Account API token` (address: `/r2/api-tokens/create?type=account`) and fills in: the name, `Object Read & Write`, `Apply to specific buckets only` with that bucket, TTL `Forever`.
   - The owner clicks `Create Account API Token` and copies the **Access Key ID** and **Secret Access Key**. The page's other values aren't needed.
2. **The AI key, if the app spends:** OpenRouter → Settings → API Keys → `New Key`.
   - Claude fills in: the name, an expiry, `Credit limit` → `Custom amount` at the project's cap.
   - The owner clicks `Create` and copies the key.
   - The account needs credit before the key works.
3. **GitHub read tokens, if the app reads GitHub:**
   - Settings → Developer settings → Fine-grained tokens → `Generate new token`. GitHub first asks the owner to confirm with GitHub Mobile or an emailed code.
   - Claude fills in: the name, the expiry, `Only select repositories` with just the needed repo, `Add permissions` → `Contents`, which defaults to `Read-only`. `Metadata` is added automatically.
   - GitHub shows a confirmation pop-up before generating: tell the owner it's expected, and what it should list.
4. **Made-up values** (seeds, passwords, session secrets): the owner runs `openssl rand -hex 24` in Ubuntu once for each, separately for staging and production.
5. **Pasting into Northflank.** Claude opens each secret group; the owner clicks `Continue` on "Protected content", then `Edit` in the View/Edit/JSON/Env row, pastes into the empty names, and saves.
   - **Warn the owner first:** View mode shows dots for every value, even empty ones, and doesn't allow editing. They aren't existing keys.
   - **For the blueprint:** Claude types the override names into Settings → Argument overrides (Env mode, `NAME=` per line) and fills the non-secret ones; the owner pastes the secrets after each `=` and clicks `Save preview blueprint`.
6. **The two Northflank tokens** (Team → `API tokens` → `Create API token`).
   - Claude fills in: the name, the matching role, a lifetime of about 30 days, or longer for a long build.
   - The owner clicks `Create API token` and copies it.
7. **On the PC, in Ubuntu, one command at a time:**
   ```
   cd ~/harness && git pull
   git clone https://github.com/ngunn86/<repo> ~/<folder>        (if it isn't there yet)
   harness hosting connect --project ~/<folder>                  (pastes the staging, then the production token)
   harness hosting credential --project ~/<folder> staging <NAME>  (each test login the smoke checks use)
   harness hosting credential --project ~/<folder> preview <NAME>  (the same for copies, if the project uses them)
   harness hosting check --project ~/<folder>
   harness cards check --project ~/<folder>
   tmux new -s <name>
   harness run --project ~/<folder>
   ```
   - Pasted values don't show; that's normal.
   - Ask for a screenshot of `connect`'s output: it names the services it found and each token's expiry.
   - `Ctrl+B` then `D` leaves the run going; `tmux attach -t <name>` comes back.

## 6. Dashboard tips (for Claude)

- **Coordinates shift.** Forms grow as sections open, and the panel's size can change. Take a screenshot before clicking.
  - To reach a button, scroll it to the centre of the page with `scrollIntoView` in the page's script, then click.
  - Dropdown options that clicks keep missing can be found by their text and clicked from the page's script.
- **JavaScript clicks on checkboxes** (such as the roles' `Select all`) don't register; use real clicks.
- **The code editor** (Monaco) ignores pasted or inserted text from scripts. Typing minified JSON on one line with real keystrokes works. Read it back from the editor's lines to check.
- **The tag picker for secret-group restrictions** didn't take a selection in the app's browser. Restrict by service name, or use the blueprint's own tag.
- **Record as you go:** each finished part in the plan's checklist with its date, anything new in the harness's research notes, and the blueprint's JSON in the repo.
