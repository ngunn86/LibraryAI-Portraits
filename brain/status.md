# Status

**Phase 0: planning.** There is no code yet. Last updated 2026-10-23 by Claude.

**Where planning is:**
- **The owner's decisions are made** for tracker topics T-01..T-23 (D-31..D-57), plus D-58..D-70. The tool is a hosted app on **Northflank** (D-70, since 2026-10-23; it was Railway) in TypeScript, like the library, with an API the library adopts.
- **Requirements consolidated** on 2026-10-20 and **feature cards drafted** for the new design.
- **The first outside review is merged:** Gemini 4 Argon's 19 points, all accepted ([reviews/2026-10-20-argon-round-2.md](reviews/2026-10-20-argon-round-2.md)). Recipe 0.5.0 and the porting references (`prototype/parity/`) came out of it.
- **Adapted to the Coding Harness** (2026-10-21, D-62..D-68): `harness.yaml`, the build-agent carve-out, the build loop and veto window, jobs over the web instead of the host's command line, a health check that proves the database and bucket, and 18 of the 52 cards in format 1 as a sample.
- **Moved to Northflank** (2026-10-23, D-70, the harness's HD-60): two projects (staging with the pull-request copies; production), files on Cloudflare R2, a liveness route (contract draft 8), new owner input O-14, and HT-33 in the throwaway test.
- **Next:** the owner relays [handoffs/harness-questions.md](handoffs/harness-questions.md) to the harness chat, which checks the sample; then the other 34 cards are converted. T-09 once Rev1 is pushed.

## Where things stand

| Piece | State |
|---|---|
| Tracker | [tracker.md](tracker.md). T-01..T-08, T-10..T-14 and T-16..T-23 decided. T-24 proposed in full; T-25 converting to the harness's format. T-09 waits for Rev1's push; T-15 for real AI copies in the trial; T-26 is the review rounds; T-27 is the harness's own planning |
| Briefs | v1 (2026-10-17) and v2 (2026-10-19), in `brief/`. v2 is the brief; decisions D-24 onwards extend it |
| Requirements | [spec/requirements.md](spec/requirements.md), consolidated 2026-10-20: every ID kept, every item current. Open: only the PORT reconciliation (needs O-1) |
| Architecture | [spec/architecture.md](spec/architecture.md) v2 (proposed): TypeScript on Node 24 (D-57); on Northflank (D-70): web and worker, with production's nightly cron job, in two projects; Postgres add-ons with a queue table; Cloudflare R2 buckets; `sharp` and OpenCV.js, with a porting spike. The Python prototype is the reference |
| API contract | [contracts/portraits-api.openapi.json](contracts/portraits-api.openapi.json), draft 8, with samples and an offline check (`check_api.py`, passing). The library adopts it (D-37); hand-off note in [handoffs/library-api.md](handoffs/library-api.md) |
| Sources | [spec/sources.md](spec/sources.md): Wikidata/Commons, the LoC and Wellcome (D-46); Smithsonian only if the survey shows gaps |
| Build plan and features | [plan/build-plan.md](plan/build-plan.md) (adapted to the harness 2026-10-21) and [plan/features.md](plan/features.md) (draft 4: 52 cards with gate cards; 18 in the harness's format 1 as a sample). The harness's settings: [../harness.yaml](../harness.yaml). The owner's release steps: [plan/release-checklist.md](plan/release-checklist.md) |
| Decisions | D-01..D-70 |
| Open questions | None. Q-27 and Q-28 were resolved on 2026-10-20 (D-58, D-59); Argon's two calls were answered the same day (D-60, D-61) |
| Style prototype | Recipe 0.5.0 (`prototype/`): 0.4.0's look, accepted as the starting point (D-49), with the crop measured with YuNet and the drift check inside the inner face. Descreen, AI-enhanced blend with safeguards, code outline, black-and-white and 500 px versions, and the same-photo check prototype. Prompts in `prototype/prompts/`; per-operation references for the port in `prototype/parity/`; the face model in `models/` |
| Harness | Planned in its own chat (D-15); its requirements of this project are in `../Coding Harness Instructions.md`, and this project's answers and questions in [handoffs/harness-questions.md](handoffs/harness-questions.md). The throwaway test: [handoffs/harness-throwaway-test.md](handoffs/harness-throwaway-test.md) (HT-01..HT-33, kept updated) |
| Reviews | Format and prompt in [reviews/README.md](reviews/README.md). Round with Gemini 4 Argon merged 2026-10-20 |

## Waiting on the owner

1. **Pass [handoffs/library-api.md](handoffs/library-api.md) to the library chat** and have Rev1's latest planning pushed to GitHub (O-1). That unblocks T-09 and the PORT reconciliation.
2. **Relay [handoffs/harness-questions.md](handoffs/harness-questions.md) to the harness chat,** and ask it to run `harness cards check` on the sample cards.
3. **Any further outside reviews** (P0-6): point the reviewing tools at `brain/reviews/README.md`. Argon's round is merged.
4. **Rotate any key ever stored in Railway** (its disclosure of 2026-10-21).
5. Later: the throwaway test, on Northflank; then the owner inputs (O-4, O-8..O-11, O-13, O-14) as the build reaches them, and the [release checklist](plan/release-checklist.md).

## Next planning steps, in order

1. Further outside review rounds, if any; Claude merges accepted points and records decisions (P0-6, T-26).
2. T-09 and the PORT reconciliation, once Rev1 is pushed (P0-1).
3. Convert the other 34 cards to format 1 once the sample passes `harness cards check` (T-25).
4. Freeze plan v1 (P0-7).

## Session log

- **2026-10-17:** Brief v1. Claude reviewed it and proposed a stand-in library server, a style prototype first, and a code-drawn outline contender.
- **2026-10-19:** Brief v2: no dependency on the library; input is `teachers.csv`, output a Drive folder.
  - Claude reviewed it: authority match undefined; re-runs could pay twice; deliver through a synced folder.
  - Repo created. The GitHub connection was made, but pushes are refused until the Claude app is installed on the repo.
  - Claude wrote the planning notes: rules, requirements, architecture, contracts, decisions, questions, build plan and feature cards.
- **2026-10-19 (later):** The owner installed the Claude GitHub App; Claude's push to `main` works.
  - The owner's sample portraits arrived (in `Sample Portraits/`, committed on the owner's PC only). Claude moved them to `design/portraits/targets/` and `originals/`, under teacher-id names, and noted their sizes.
  - The targets are 500 px; the originals are small (250–340 px wide).
- **2026-10-19 (later):** The owner answered three questions:
  - the example originals are of unknown source, for evaluating the processing only (D-13);
  - credit metadata must be complete (D-14);
  - the harness is designed in a separate chat (D-15).
  The examples are to be used to evaluate the processing steps, so the style prototype goes ahead (D-16). Claude started the prototype (P0-3).
- **2026-10-19 (later):** Style prototype (P0-3), recipe 0.1.0.
  - Measured the owner's portraits: 45° grid, 110 cells across, line 6 px with a 2 px gap at 1,000 px, crop by eye-to-mouth distance.
  - Built the recipe in code and reproduced all three: figure overlap 0.88–0.97, tone error 0.05–0.07.
  - The code-drawn line matches the owner's, which supports Q-05.
  - Known gap: the stand-in cut-out is weak on a dark suit against a dark background (Holmes).
  - Fixtures and reference outputs saved for F-16.
- **2026-10-19 (later):** Owner feedback on the board:
  - Fillmore and Cady are book prints with a dot pattern, so descreen with an edge-preserving blur (D-17).
  - The owner's own method blended a subtly AI-enhanced copy at about 50% before the halftone.
  - The owner's AI cut-out did better than the stand-in.
  Recipe 0.2.0 adds descreening: a screen is detected in Fillmore and Cady, not in Holmes, and the texture is cleaner. The enhanced blend is added as PIP-13 and F-30 (align, then blend), pending Q-21, since it changes STY-04. The owner's cut-out tool becomes a trial contender (Q-18, Q-22).
- **2026-10-19 (later):** The owner adopted the AI-enhanced blend with the safeguards (D-18). All AI goes through OpenRouter with one key (D-19). There are no in-between files, so Claude proposes the prompts (D-20).
  - Recipe 0.3.0: one OpenRouter image call per original gives a restored copy on flat green, which supplies both the 50% blend (aligned, in the frame) and the cut-out.
  - Proposed models: Nano Banana Pro to start, with Nano Banana 2 and GPT Image 2 as challengers.
  - Mechanics checked on synthetic copies. Prompts are in `prototype/prompts/`.
- **2026-10-19 (later):** The owner asked how the larger AI copy is aligned. Claude explained, drew `prototype/out/alignment-explainer.png`, and added a local face-drift check (recipe 0.3.1).
  - The edge-preserving blur stays (D-23), and the AI copy now gets it too.
  - Claude read library-pipeline read-only (commit 363aa14). Its `collection/authors.csv` (182 active authors, 71 with dates, no Wikidata ids) becomes the source of `data/teachers.csv`, with stable ids and enrichment (D-22, IN-12, IN-13).
  - Sources widened at the owner's request (D-21). `spec/sources.md` proposes Wikidata/Commons, LoC, Internet Archive book plates (new rule R4: a pre-1931 book by or about the teacher, with a caption naming them) and Wellcome now; Smithsonian, NYPL and DPLA later. It also adds a permanent rights log (SRC-12).
  - New cards F-31 to F-35.
- **2026-10-19 (later):** Owner's new requirements (D-24..D-30):
  - no book extraction (Internet Archive omitted);
  - plan the other picture sources and detail them at the formal review;
  - up to 3 different portraits per teacher, checked visually;
  - three versions (original, white dots, black-and-white clipped to the outline);
  - organised by teacher;
  - an API for the library;
  - plan in dependency order with a tracker.
  Claude created `brain/tracker.md` (T-01..T-26), withdrew R4, SRC-13, F-33 and Q-24, and marked the run-based delivery as under rework. Next: T-01.
- **2026-10-19 (later):** T-01 discussion. The owner leans towards fully hosted, for the harness test. Claude's feasibility review is in `topics/T-01-where-it-runs.md`: feasible, since the AI runs at OpenRouter and the code steps need a small instance; build in layers; a deploy spike picks the host (Replit first, Railway or Render as the fallback). Tracker T-27 added (the harness's deploy duties).
- **2026-10-19 (later):** T-01 decisions D-31..D-35:
  - fully hosted, with a two-way API;
  - the authors list through GitHub (read-only token);
  - an admin page;
  - extra keys are fine, kept to a minimum;
  - the owner can deploy by hand from Replit (phone).

  Host options beyond Replit compared against ten requirements (Railway, Render, DigitalOcean, Cloud Run). Recommendation: Replit (the Rev1 rehearsal), or Railway for automatic deploys and staging.
- **2026-10-19 (later):** Railway explored in depth (notes in T-01). The owner may move Library-AI there too. Claude wrote `handoffs/harness-throwaway-test.md` (HT-01..HT-29), the throwaway hosted app the harness must build, deploy, test and tear down before feature work, and will keep it updated. The owner is checking Railway in the other chat.
- **2026-10-19 (evening):** Relayed from the library's planning:
  - host Railway, Replit spike skipped (D-36);
  - the library adopts this project's API, OpenAPI file and three-portrait scope (D-37);
  - approval and the main portrait are decided in the library and reported back (D-38).

  T-01 and T-05 closed, T-09 mostly decided, Q-09 superseded. Rev1's shared hosting review isn't on GitHub yet (latest Rev1 commit 2026-10-18), so it's copied once pushed. Next: T-02.
- **2026-10-19 (evening):** T-02 opened. Mock-ups of the black-and-white version's edge (A white line, B no line, C black edge) on light, dark and coloured pages. Proposals in `topics/T-02-three-versions.md`: original byte for byte plus a viewing copy; the white version at 1,000 px only; the black-and-white version as option A; version names; working files kept internally.
- **2026-10-19 (evening):** **T-02 decided** (D-39).
  - Black-and-white version: option C, black edge.
  - Original: kept byte for byte, with a PNG viewing copy.
  - The white and black-and-white versions come at 1,000 and 500 px.
  - The AI-enhanced copy and the cut-out mask are offered to the library.

  Recipe 0.4.0 makes them, and the outputs are in `prototype/out/versions/`. STY-08, STY-09 and OUT-11 added, OUT-05 amended, T-15 mostly decided. Next: T-03.
- **2026-10-19 (evening):** **T-03 decided** (D-40).
  - A different portrait means a different photograph; only the best copy of a photograph is kept.
  - Which three: the best-known image (Wikidata P18) first, then the best quality spread across life.
  - A better copy of an approved portrait is offered to the library.
  - A turned-down photograph returns only as a clearly better copy.

  PIP-14..PIP-17 added. Next: T-04.
- **2026-10-19 (evening):** **T-04 decided** (D-41): no category scheme. Only an approximate date is kept, to spread the three across life, and the library can correct it. PIP-18 added. Next: T-06.
- **2026-10-19 (evening):** **T-06 decided** (D-42).
  - Files live in the tool's Railway bucket, and the library keeps its own copy of everything it pulls.
  - Replaced and turned-down portraits are kept as history.
  - Backups cover the database only, at first.
  - The admin page is read-only: browse and run status.

  OUT-12 and OUT-13 added; OUT-01 and OUT-09 withdrawn. Next: T-07.
- **2026-10-19 (evening):** T-07 drafted as a full proposal (`topics/T-07-records.md`). Waiting for the owner's look; then T-08.
- **2026-10-19 (night):** T-07 accepted as proposed (D-43). T-08 opened, with the API's conventions mirroring the library's own.
- **2026-10-19 (night):** **T-08 decided** (D-44): one key, pull only, requests handled right away.
  - Wrote the OpenAPI contract (draft 1), its samples, a plain-words page, an offline check, and a hand-off note for the library chat.
  - OUT-14 added; IN-06 and IN-07 amended.

  Next: T-10.
- **2026-10-19 (night):** **T-10 decided** (D-45).
  - Active authors only.
  - Missing dates and Wikidata ids are filled only when Wikidata and the LoC name authority agree.
  - Teachers still unidentified are skipped and listed for the owner, with suggested additions for `authors.csv`.

  Q-01, Q-12, Q-13 and Q-26 resolved. Next: T-11.
- **2026-10-19 (night):** **T-11 decided** (D-46), after a review that checked each source against its documentation.
  - First build: Commons, the LoC and Wellcome, with no keys.
  - Smithsonian only if the coverage survey shows gaps.
  - NYPL dropped: its API was retired on 1 August 2026.
  - DPLA not used.

  Next: T-12.
- **2026-10-19 (night):** **T-12 decided** (D-47): engravings, drawings and paintings are accepted, and the trial decides. R3 also matches on LoC name ids. Next: T-13.
- **2026-10-19 (night):** **T-13 decided** (D-48).
  - Stylized portraits of public-domain originals are CC0, and credit "Portrait by New Thought Nexus, adapted from …".
  - CC BY and CC BY-SA originals pass their terms on (SRC-11).
  - Q-16 resolved. API draft 2 adds each file's licence link.

  Next: T-14.
- **2026-10-19 (night):** **T-14 decided** (D-49): the owner accepted the board as the starting point, with the outline drawn by code only. Model-drawn outlines are dropped. Cut-out limits proposed (PIP-19). Next: T-16.
- **2026-10-19 (night):** **T-16 decided** (D-50). Copies and different photographs are told apart by a fingerprint, feature matching (prototyped: copies 56–330 points, different ≤ 19) and a model tie-break. When unsure, it's the same photograph. PIP-20 added. Next: T-17.
- **2026-10-19 (night):** **T-17 decided** (D-51): a failed draft gets one remake with a fresh AI copy. The black-and-white version is checked by code. Q-06 and Q-07 resolved. Next: T-18.
- **2026-10-19 (night):** **T-18 decided** (D-52): Claude Haiku 5.5 for pre-checks, Claude Sonnet 5.5 for draft checks and tie-breaks. `same_photo.md` and `precheck.md` v2 written. Next: T-19.
- **2026-10-19 (night):** **T-19 decided** (D-53).
  - Nightly runs, with library requests handled at once.
  - Sources searched again monthly.
  - The owner hears through the library's daily email, the admin page and Railway's alerts.
  - Try-again notes guide a fresh AI copy.

  Next: T-20.
- **2026-10-20 (just after midnight):** **T-20 decided** (D-54).
  - Caps: $100 for the first run; then $10 a night and $30 a month; $30 for the trial.
  - The owner sets a credit limit on the OpenRouter key.
  - Owner inputs updated for the hosted app (O-4, O-8..O-11).

  Next: T-21.
- **2026-10-20:** **T-21 decided** (D-55): one admin password; the same OpenRouter key in every environment, with low caps off production. RUN-10 added. Next: T-22.
- **2026-10-20:** **T-22 decided** (D-56): the trial compares the three enhance models. The checker picks the winner and the owner can veto. Each result is also shown without the blend. Q-19 resolved. Next: T-23.
- **2026-10-20:** **T-23 decided** (D-57).
  - TypeScript, like the library, so the harness rehearses the same toolchain.
  - `spec/architecture.md` rewritten (v2, hosted). It includes a porting spike for the image steps (OpenCV.js) with a fallback for each known gap.
  - The Python prototype stays as the reference.

  Q-15 resolved. Next: T-24.
- **2026-10-20:** T-24 proposed in full: the testing approach rewritten for TypeScript (node:test, PGlite, contract and smoke tests). Next: T-25, the feature cards.
- **2026-10-20 (overnight):** Consistency pass and card drafts, at the owner's request, before the outside reviews.
  - `spec/requirements.md` consolidated: every ID kept, each item restated for the hosted API app with its origins.
  - B2 items whose new wording needs the owner's OK are gathered as Q-27.
  - `plan/build-plan.md` rewritten: phases, Phase 0 states, harness workflow in TypeScript, spend, risks (R-13 porting, R-14 retired APIs, R-15 the library's readiness).
  - Feature cards redrafted (`plan/features.md`).
  - The API contract (draft 3) adds the teacher's LoC name id.
- **2026-10-20 (overnight, later):** A fresh-eyes consistency review (a separate agent) found 25 issues, all fixed.
  - **The biggest:**
    - full teachers would never be searched for better copies (raised as Q-28);
    - the trial's environment, now production before the release, so its cache carries over;
    - the environment rules: pull-request copies stubbed, staging by hand.
  - **The contract (draft 4):** the source and match vocabulary unified, a `skipped` search state, where ids and dates came from, `replaced` and `another_original` defined, and the health fields.
  - **Elsewhere:**
    - the outbound allowlist gains the bucket endpoint;
    - the admin password moves to the database;
    - LoC pacing is set at 87 s for 30 calls;
    - the trial gets sub-budgets;
    - stale decisions are marked superseded;
    - the library hand-off note is updated;
    - a prompt is added for classifying Try-again notes.
- **2026-10-20 (morning):** The owner answered both questions.
  - **Q-27 → D-58:** the bulk-upload zip is dropped, and B2's checks are restated for the API.
  - **Q-28 → D-59:** full teachers are searched monthly for better copies, and the first-run cap is a total for the first pass.

  No questions are open. The PORT reconciliation waits for Rev1's push.
- **2026-10-20 (afternoon):** **Argon's review merged** (19 points, all accepted; D-60 and D-61 from the owner). Requirements PIP-21..PIP-23 and TRI-09 added; the contract is draft 5 and the cards draft 3. Making the porting references showed the prototype's crop had been measured with a different face detector, so recipe 0.5.0 re-measures it with YuNet (committed in `models/`). The references are in `prototype/parity/`.
- **2026-10-21:** **Adapted to the Coding Harness** (its instructions of 2026-10-20). The owner chose a 24-hour veto window (D-66), one OpenRouter key (D-67) and the admin front page (D-68); the harness chat's decisions are D-62..D-65. RUN-11 (jobs over the web) and RUN-12 (a real health check) added; the trial moved to staging, so production's first deploy is the release; 18 cards in format 1, with F-49..F-55 new. Questions for the harness chat in `handoffs/harness-questions.md`.
- **2026-10-22:** **The harness's updated instructions** (to HD-59) merged from the owner's PC, where the harness chat had committed them before that copy had our adaptation commits. Applied: card tests run by path with TAP (`test_card`), unique test names, what each card creates (in the 18 converted cards' goals), contracts before tests on size L cards, fast-forward merges, `deploy.starts_at: F-36`, pull-request copies based on staging and a health check naming its environment, database and bucket (contract draft 7), soft per-card caps (D-69). The questions for the harness chat are still open.
- **2026-10-23:** **Hosting moved to Northflank** (the harness chat's HD-60, recorded as D-70, superseding D-36), after Railway disclosed on 2026-10-21 that attackers may have read customers' environment variables. Claude's choices with it (proposed): Cloudflare R2 for files (three buckets, a token each, pull-request copies under a prefix); templates in `northflank/`; empty, seeded preview databases living at most 3 days; production building the promoted commit through its own release flow (backup, migrate, deploy); `PORTRAITS_ENV`; a liveness route `/api/v1/live` (contract draft 8). Updated: requirements (IN-11, SRC-01, OUT-12, RUN-01, RUN-05, RUN-07, RUN-09..RUN-12, TRI-06), architecture, `harness.yaml`, cards F-36, F-37, F-49, F-51, F-17, F-50, the build plan (owner inputs, new O-14; environments; hosting cost about $25 a month for production plus staging while it runs), the release checklist, the throwaway test (HT-32 tightened, HT-33 added), T-01, and the harness questions (8 to 12 new; 7 settled).
