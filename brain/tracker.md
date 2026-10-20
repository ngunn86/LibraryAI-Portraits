# Planning tracker

**This is the one place that tracks the planning** (D-30). It lists every topic we need to decide before the build, in the order to decide them: a topic comes after the topics it depends on. As we go:

- **Decisions** go to [decisions.md](decisions.md) (D-numbers) and are linked here.
- **Detailed questions** stay in [open-questions.md](open-questions.md) (Q-numbers) and are linked here.
- **New topics** are added at the end of their stage with the next free T-number. Numbers are never reused.
- **The log** at the bottom is append-only: one dated line per change.

**Status words:**

| Word | Meaning |
|---|---|
| **next** | The one we're on now |
| **open** | Not started |
| **in discussion** | Started, but not settled |
| **decided** | Settled; the D-numbers are listed |
| **mostly decided** | Settled except for listed details |
| **parked** | Deliberately left for later |

## Overview (in order)

| T | Topic | Stage | Depends on | Status |
|---|---|---|---|---|
| T-01 | Where the app runs and how the library reaches it | 1 Shape | none | **decided** (D-31..D-36): fully hosted on **Railway**, two-way API ([notes](topics/T-01-where-it-runs.md)) |
| T-02 | The three versions of a portrait, exactly | 1 Shape | none | **decided** (D-39): original + PNG viewing copy; white and black-edge B&W at 1,000 and 500 px; AI files offered ([notes](topics/T-02-three-versions.md)) |
| T-03 | How many portraits per teacher, and what counts as different | 1 Shape | none | **decided** (D-40): different photographs, best-known first, better copies offered |
| T-04 | Categories for each portrait | 1 Shape | T-03 | **decided** (D-41): no category scheme; an approximate date for the spread; the library can correct |
| T-05 | Approval: what the library approves, and the main portrait | 1 Shape | T-01, T-03 | **decided** (D-38): in the library's queue, reported back |
| T-06 | Storage and organisation by teacher | 2 Data | T-01, T-02, T-03 | **decided** (D-42): tool's bucket; library keeps its own copies; history kept; database backups; read-only admin page |
| T-07 | The records: what we keep about teachers, portraits, versions and sources | 2 Data | T-02 – T-05 | **in discussion**: proposed in full ([notes](topics/T-07-records.md)), waiting for the owner's look |
| T-08 | The library API | 2 Data | T-01, T-06, T-07 | open (D-28 sets "an API") |
| T-09 | The contract with Library-AI (Rev1) | 2 Data | T-08 | **mostly decided** (D-37): this project owns the API and its OpenAPI file; the library adopts it |
| T-10 | The teacher list (from the pipeline's authors) | 3 Finding | none | mostly decided (D-22) |
| T-11 | Picture sources | 3 Finding | T-07 | open (D-24, D-29) |
| T-12 | Match rules: when a picture certainly shows the teacher | 3 Finding | T-10, T-11 | mostly decided |
| T-13 | Rights, licences and credits | 3 Finding | T-02, T-07, T-11 | mostly decided |
| T-14 | The white-dot version: processing recipe | 4 Processing | T-02 | mostly decided (recipe 0.3.1) |
| T-15 | The black-and-white version: style and recipe | 4 Processing | T-02, T-14 | **mostly decided** (D-39: option C, made from the master's layers) |
| T-16 | Telling portraits apart (same photo or a different one) | 4 Processing | T-03, T-14 | open |
| T-17 | Checks and failure rules | 4 Processing | T-02, T-03, T-14, T-15 | open |
| T-18 | Models and prompts | 4 Processing | T-14 – T-17 | mostly decided (D-19, D-20) |
| T-19 | How runs work | 5 Running | T-01, T-05, T-08 | open |
| T-20 | Spend | 5 Running | T-03, T-18, T-19 | open |
| T-21 | Security | 5 Running | T-01, T-08 | open |
| T-22 | The trial | 5 Running | T-14 – T-18, T-20 | open |
| T-23 | Stack and architecture | 6 Build | T-01, T-06, T-08 | open |
| T-24 | Testing approach | 6 Build | T-23 | mostly decided (D-09) |
| T-25 | Feature cards for the harness | 6 Build | all above; the harness format (D-15) | open |
| T-26 | Outside reviews and plan freeze | 6 Build | T-25 | open |
| T-27 | What the harness must do for a hosted app (hand-off to the harness chat) | 6 Build | T-01 | in discussion: [throwaway test requirements](handoffs/harness-throwaway-test.md) v1 |

**Why this order:**

- **Stage 1** is first because almost everything depends on it: where the app lives, what it produces and how many portraits it keeps.
- **Stage 2** fixes the data and the library contract that every feature reads and writes.
- **Stages 3–5** fill in finding, processing and running, each against those foundations.
- **Stage 6** turns it all into the build plan.

Topics within a stage can move in parallel when they don't depend on each other. For example, T-10 and T-14 are nearly done already.

---

## Stage 1: The shape of the app

### T-01 · Where the app runs and how the library reaches it · **decided**
- **Notes:** [topics/T-01-where-it-runs.md](topics/T-01-where-it-runs.md) (feasibility review, hosts, deploy spike, recommendation).
- **Decided (2026-10-19):**
  - fully hosted, with a two-way API (D-31);
  - the authors list through GitHub (D-32);
  - an admin page (D-33);
  - extra keys are fine when needed (D-34);
  - deploying by hand from Replit is fine (D-35).
- **Host: Railway** (D-36), from the library's planning, so the two projects share one hosting review. The Replit spike is skipped. Rev1's `brain/reference/hosting-railway-review.md` will be copied into `brain/reference/rev1/` once it's on GitHub.
- **Depends on:** nothing. It comes first because storage (T-06), the API (T-08), runs (T-19), security (T-21) and the stack (T-23) all follow from it.
- **To decide:**
  1. Where processing runs: your PC (as planned so far), or a hosted service.
  2. Where the API lives, now that the library pulls records through one (D-28). Options:
     - static files the library reads, with no server;
     - a small hosted API service;
     - your PC, through a tunnel.
  3. Whether the API only serves records (pull), or also takes the library's approvals and requests back.
- **Decided so far:** the library pulls records from the tool (D-28). All AI goes through OpenRouter with one key (D-19).
- **Affects:** SCOPE-02, OUT-01..OUT-10, RUN-01, the architecture, and the Drive hand-off of B2.

### T-02 · The three versions of a portrait, exactly · **decided**
- **Depends on:** nothing.
- **To decide:**
  1. **Original:** the file exactly as downloaded, at full size? Or also a smaller copy for viewing?
  2. **White version:** as designed (1,000 × 1,000 PNG, white dots and line on transparency). Any other sizes?
  3. **Black-and-white version** (style details in T-15): black dots on white, or the reverse? Is the outline drawn, and in which colour? Same crop and size as the white version? Same file format?
  4. File naming and formats for all three.
  5. Whether working files (the AI-enhanced copy, the cut-out mask) are kept. *(Added 2026-10-19.)*
- **Decided so far:** the three versions (D-26).
- **Decided (D-39)** ([notes](topics/T-02-three-versions.md), mock-ups in `prototype/out/versions-board.png`):
  - the original is kept byte for byte, plus a **PNG** viewing copy (keeps transparency);
  - the white version comes at **1,000 px and 500 px**;
  - the black-and-white version is **option C, black edge**: the gap and line are black, it is clipped at the line's outer edge, and it comes at both sizes;
  - the AI-enhanced copy and the cut-out mask are kept **and offered to the library**;
  - names and ids are Claude's proposals, confirmed at T-06.
- **Written into:** STY-08, STY-09, OUT-05 (amended), OUT-11; recipe 0.4.0 (`bw_version`, `small`, `check_bw`); outputs in `prototype/out/versions/`.
- **Affects:** STY-01..STY-07, OUT-*, T-06, T-13 (each version's licence), T-15.

### T-03 · How many portraits per teacher, and what counts as different · **decided**
- **Depends on:** nothing.
- **To decide:**
  1. **The limit:** up to 3 per teacher (D-25). Is 3 a hard maximum?
  2. **Different:** a different photograph (another sitting, age or pose), not another copy of the same photograph (a different scan, crop, retouch or print). Agree?
  3. **More than 3 found:** which 3 are kept? Proposed: the best quality, spread across the teacher's life (T-04), public domain first.
  4. **Copies of one photograph:** which copy is kept? Proposed: the best one (largest, cleanest, most open licence). The others are logged as copies.
  5. **Later runs:** a new copy of a photograph already kept replaces it only if it's clearly better. A new, different photograph is added only if there's room or it beats one of the 3.
- **Decided (D-40):**
  1. Up to 3; the cap is a setting (Claude's proposal).
  2. Different means a different photograph. Copies are grouped, and only the best is kept.
  3. More than 3: the best-known image (Wikidata P18) first, then the best quality spread across the teacher's life.
  4. Copies: the best kept (licence tier, size, damage), the others logged.
  5. Later runs:
     - a better copy of an approved portrait is offered as a draft, and the library decides;
     - a turned-down photograph comes back only as a clearly better copy, once;
     - *proposed:* never if it was turned down as "not this teacher".
- **Written into:** PIP-14..PIP-17; PIP-11 and SRC-07 amended.
- **Affects:** PIP-01, PIP-11, SRC-07, RUN-02, T-04 (age or date for the spread), T-08 (turn-down reasons), T-16, T-19, T-20.

### T-04 · Categories for each portrait · **decided**
- **Depends on:** T-03.
- **To decide:**
  1. **Which labels?** Ideas:
     - approximate age or era (young, middle, late);
     - the year, if the source gives it;
     - pose (frontal, three-quarter, profile);
     - medium (photograph, engraving, drawing);
     - quality grade;
     - source.
  2. **Who assigns them:** source metadata first, the vision pre-check for the rest. Are they checked by anyone?
  3. **Used for what:** choosing which 3 to keep (T-03), the library's display (T-05), search?
- **Decided (D-41):**
  - "This kind of detail isn't important for my needs." There is no category scheme. "Categorize" is covered by organising by teacher (D-27).
  - Each portrait records only its source, the best-known flag and an approximate date (for the spread, PIP-16).
  - These are set automatically. The library can correct them through the API, and a correction is never overwritten.
- **Written into:** PIP-18.

### T-05 · Approval: what the library approves, and the main portrait · **decided**
- **Depends on:** T-01, T-03.
- **To decide:**
  1. Does the admin approve each portrait, or each version?
  2. **Main portrait:** which one the library shows by default. Chosen by the admin, or proposed by the tool?
  3. **Turn-downs and requests:** Try again, find another, a pasted link. How do they reach the tool now that there's an API (T-08)?
  4. What the tool does with a turned-down portrait: set it aside, and fill the slot from the next candidate?
- **Decided (D-38):**
  - Approval happens in the library's queue, and so does the choice of a teacher's main portrait.
  - The library reports every decision back to the tool through the API: approved, turned down, main portrait, and requests.
  - Nothing goes live from the tool (SCOPE-03).
- **Left for later topics:**
  - what the tool does with a turned-down portrait (T-03 and T-19: set it aside, and fill the slot from the next candidate);
  - the API's shape for decisions (T-08).
- **Linked:** Q-02 (re-runs), Q-08 (Try-again notes), IN-06, IN-07.

## Stage 2: Data, storage and the library contract

### T-06 · Storage and organisation by teacher · **decided**
- **Depends on:** T-01, T-02, T-03.
- **To decide:**
  1. Where files live: the Google Drive folder, cloud storage behind the API, or both.
  2. **The layout by teacher** (D-27). The files of a portrait are set by OUT-11 (D-39): `original.*`, `original-view.png`, `white-1000.png`, `white-500.png`, `bw-1000.png`, `bw-500.png`, `enhanced.png`, `mask.png`, plus the record. Proposed: `portraits/<teacher_id>/<portrait_id>/…`.
  3. What happens to a replaced portrait: kept as history, or removed?
  4. Full-size originals: kept for every candidate, or only for kept portraits? Backups?
  5. **Your view:** an admin page (D-33). What it shows: portraits by teacher, run status, the trial board, approvals?
- **Decided so far:** organised by teacher (D-27).
- **Decided (D-42):**
  1. Files live in the tool's own Railway bucket, with no Drive copy. The library makes its own local copy of everything it pulls through the API.
  2. Layout `portraits/<teacher_id>/<portrait_id>/`, with the eight files and a `record.json`; the database is the source of truth (Claude's proposal).
  3. Replaced and turned-down portraits keep their files as history.
  4. Candidates that never become portraits are logged only (Claude's proposal). Backups: the database only, at first.
  5. The admin page is read-only: browse and run status.
- **Written into:** OUT-12, OUT-13; OUT-01 and OUT-09 withdrawn; OUT-08 to be confirmed at T-09.
- **Linked:** Q-03 (superseded), OUT-01..OUT-08 (the run-based layout).

### T-07 · The records: what we keep · **in discussion**
- **Depends on:** T-02 – T-05.
- **To decide:**
  1. **Teacher:** id, names, dates, Wikidata id, link to the authors list.
  2. **Portrait:** id, teacher, approximate date and best-known flag (D-41, with the library's corrections), status, main or not, `replaces` (for a better copy), history.
  3. **Version:** the file, its size, checksum and recipe version.
  4. **Source and rights:** from the rights log (SRC-12).
  5. **Checks and costs.**
  6. **Ids:** stable across runs.
- **Decided so far:** complete credit metadata for every portrait (D-14). Every original considered is logged (SRC-12, proposed).
- **Proposed in full** in [topics/T-07-records.md](topics/T-07-records.md): the teacher, candidate (rights log), portrait, file, library decision, request, run and spend records, and the portrait history.
- **Linked:** OUT-02 (the Rev1 manifest schema, probably replaced; see T-09), SRC-08, SRC-11, SRC-12.

### T-08 · The library API · open
- **Depends on:** T-01, T-06, T-07.
- **To decide:**
  1. **What the library can read:** teachers; portraits by teacher; the eight files of each portrait (OUT-11, D-39, the AI-enhanced copy and mask included); credits and rights; what's changed since a date.
  2. **What the library can send** (if T-01 allows): approvals, turn-downs, requests, the main-portrait choice.
  3. **Access:** a key per client, and read-only versus read and write.
  4. Versioning of the API, and its documentation (an OpenAPI file).
- **Decided so far:** an API, for the library to pull records (D-28).

### T-09 · The contract with Library-AI (Rev1) · **mostly decided**
- **Depends on:** T-08.
- **To decide:**
  1. ~~Who owns the contract now~~. **Decided (D-37):** this project defines the API and the records and publishes an OpenAPI file. The library adopts it, pulls, and sends its decisions back. The library has also adopted the three-portrait scope.
  2. What to tell the Rev1 planning: a short hand-off note from here.
  3. **Whether we still need Rev1's portrait files (O-1).** Probably only to see which of the PORT requirements still apply.
- **Linked:** Q-09, Q-16, O-1, OUT-10, AC-02, AC-03.

## Stage 3: Finding pictures

### T-10 · The teacher list · mostly decided
- **Depends on:** nothing.
- **Decided so far:**
  - The list comes from library-pipeline's `authors.csv`, read-only (D-22).
  - The sync keeps stable ids (IN-12).
  - Missing dates and Wikidata ids are filled when two sources agree (IN-13).
- **To decide:**
  1. `active` authors only? (Q-26)
  2. Date forms (Q-12) and duplicate ids (Q-13).
  3. With book plates dropped (D-24), what fills dates for the ~110 active authors without them? Wikidata, plus the LoC name authority (Q-01)?

### T-11 · Picture sources · open
- **Depends on:** T-07 (what each source must supply).
- **Decided so far:**
  - The Internet Archive and book plates are omitted (D-24).
  - Plan these: Wikidata/Commons, LoC, Wellcome, Smithsonian Open Access, NYPL Digital Collections, DPLA (leads) (D-29).
  - The details are for the formal planning review (D-29).
- **To decide, for each source, at the review:**
  - access and limits;
  - key (Q-25);
  - the rights fields;
  - the match rule;
  - what is recorded;
  - the order of preference;
  - whether it's adopted for the first build or later.
- **Linked:** [spec/sources.md](spec/sources.md), SRC-01, SRC-02, Q-23, Q-25.

### T-12 · Match rules · mostly decided
- **Depends on:** T-10, T-11.
- **Decided so far:**
  - Certain matches only (D-03): R1 Wikidata image, R2 Commons depicts, R3 a picture record with name and dates.
  - Owner's links are accepted (SRC-04).
  - Book plates (R4) are withdrawn (D-24).
- **To decide:**
  - checking and finding Wikidata ids (SRC-06, Q-01);
  - the R3 details for each new source;
  - engravings and drawings (Q-11).

### T-13 · Rights, licences and credits · mostly decided
- **Depends on:** T-02, T-07, T-11.
- **Decided so far:**
  - The allowed licence tiers (D-03).
  - Complete credits (D-14).
  - A permanent rights log (SRC-12, proposed).
- **To decide:**
  1. The licence of each derived version, especially from CC BY-SA originals (Q-16, SRC-11). This now includes the AI-enhanced copy and the mask, which are offered to the library too (D-39).
  2. Whether the original file may be shown by the library, and with what credit.
  3. The credit-line format for each source.

## Stage 4: Processing and checking

### T-14 · The white-dot version: processing recipe · mostly decided
- **Depends on:** T-02.
- **Decided so far:**
  - The style (D-04).
  - Descreen with an edge-preserving blur (D-17, D-23).
  - The AI-enhanced 50% blend, with safeguards (D-18).
  - All AI through OpenRouter (D-19).
  - The prototype (D-16): recipe 0.3.1.
- **To decide:**
  - your verdict on the board;
  - the code-drawn outline as the default (Q-05);
  - the cut-out sanity limits.

### T-15 · The black-and-white version · **mostly decided**
- **Depends on:** T-02, T-14.
- **Decided (D-39, at T-02):**
  - option C, black edge, prototyped and chosen (`recipe.bw_version`, STY-08);
  - it is made from the master's own layers, so it shares the white version's tones, crop, cut-out and footprint by construction.
- **Left:** a look at it on real AI-enhanced copies (F-27, F-28), along with T-14's verdict.

### T-16 · Telling portraits apart · open
- **Depends on:** T-03, T-14 (it uses the aligned face crop).
- **To decide:**
  1. **Method.** Proposed, in three layers:
     - (a) a quick fingerprint of the cropped face (perceptual hash) to catch exact and near-exact copies;
     - (b) feature matching between the two pictures, which finds many matching points when they're the same photograph even after a different scan, crop or retouch, and few when they're different sittings;
     - (c) the vision model as tie-break for unclear pairs ("the same photograph, or a different one?").
  2. **Thresholds**, set on known pairs during the prototype.
  3. Which copy survives (T-03, 4).
  4. Checking against portraits from earlier runs.
  5. **Prototype it** on real pairs before the build.

### T-17 · Checks and failure rules · open
- **Depends on:** T-02, T-03, T-14, T-15.
- **To decide:**
  - which checks run on which version (does the black-and-white version need its own draft check?);
  - remaking a draft (Q-06) and limits (Q-07), now that there can be several portraits per teacher;
  - the cut-out sanity check.
- **Linked:** PIP-02, PIP-09, PIP-10, PIP-11.

### T-18 · Models and prompts · mostly decided
- **Depends on:** T-14 – T-17.
- **Decided so far:**
  - One key: OpenRouter (D-19).
  - Claude writes the prompts (D-20; `prototype/prompts/`).
  - The starting models (Nano Banana Pro, with challengers).
- **To decide:**
  - a prompt for the distinctness tie-break (T-16) and for categories (T-04);
  - checker models;
  - the family rule.

## Stage 5: Running, cost and safety

### T-19 · How runs work · open
- **Depends on:** T-01, T-05, T-08.
- **To decide:**
  - on demand or scheduled (daily, like the pipeline);
  - resuming;
  - re-runs (Q-02);
  - the library's requests;
  - the run report;
  - notifications to your phone.
- **Linked:** RUN-01..RUN-07.

### T-20 · Spend · open
- **Depends on:** T-03, T-18, T-19.
- **To decide:**
  - the per-run cap ($250 for the first run, D-06);
  - a per-teacher cap, now that there can be 3 portraits;
  - the trial's budget (TRI-07).
- **Starting estimate:** about 17–25 cents per portrait processed, plus a few cents per candidate checked. With 182 teachers, most having 0–1 portraits, the first run is likely $50–120.

### T-21 · Security · open
- **Depends on:** T-01, T-08.
- **To decide:**
  - the library's API key;
  - where secrets live;
  - what is reachable from the internet (nothing on your PC, preferably);
  - backups.

### T-22 · The trial · open
- **Depends on:** T-14 – T-18, T-20.
- **To decide:**
  - the trial set, now including teachers with several portraits and known copies of the same photograph (to test T-16);
  - contenders (enhance models, with and without the blend);
  - the board;
  - "close" (Q-19).
- **Linked:** TRI-01..TRI-08, P0-4.

## Stage 6: Building it with the harness

### T-23 · Stack and architecture · open
- **Depends on:** T-01, T-06, T-08.
- **To decide:**
  - the language (Q-15, Python proposed);
  - the API framework and database (if T-01 chooses a hosted service);
  - hosting;
  - a refresh of `spec/architecture.md`.

### T-24 · Testing approach · mostly decided
- **Depends on:** T-23.
- **Decided so far:** the owner's standard (D-09): simple, offline fixtures, live tests only where needed.
- **To decide:** how to test the API, and what fixtures the distinctness check needs.

### T-25 · Feature cards for the harness · open
- **Depends on:** all topics above, and the harness's input format (from the other chat, D-15).
- **To decide:** rewrite `plan/features.md` from the decisions. The current 35 cards predate D-24..D-29.

### T-26 · Outside reviews and plan freeze · open
- **Depends on:** T-25.
- **To decide:**
  - review rounds by other AI tools (`reviews/`);
  - merge their points;
  - tag `plan-v1`;
  - hand over to the harness.

### T-27 · What the harness must do for a hosted app · open
- **Depends on:** T-01.
- **To decide, and pass to the harness chat (D-15):** a hosted build needs the harness to:
  - deploy a branch to staging without clicking;
  - run smoke tests against the live URL;
  - read the host's logs;
  - run database migrations;
  - manage secrets in the host (never in the repo);
  - wait for the owner's veto, then promote staging to production;
  - roll back a bad deploy;
  - keep live AI spend under the app's cap.
- **Relaxed by D-35:** a deploy may be the owner's one-tap step, announced in the digest. Deploying without clicking is a nice-to-have.
- **Output:** [handoffs/harness-throwaway-test.md](handoffs/harness-throwaway-test.md), the throwaway test's requirements (HT-01..HT-29) for the owner's harness planning. **Claude keeps it updated** whenever a decision changes what the hosted app needs, with a change-log line each time.

---

## Log (append-only)

- **2026-10-19 11:53.** Owner's new requirements recorded as D-24..D-30:
  - no book extraction (Internet Archive omitted);
  - plan the other picture sources and detail them at the formal review;
  - up to 3 different portraits per teacher, checked visually;
  - three versions per portrait;
  - organised by teacher;
  - an API for the library;
  - plan in dependency order with this tracker.
- **2026-10-19.** Tracker created with T-01..T-26. Topics already settled were folded in from decisions D-01..D-23.
- **2026-10-19.** Withdrawn because of D-24: rule R4, SRC-13, F-33 and Q-24. F-34 is narrowed to picture records.
- **2026-10-19.** The run-based delivery layout (OUT-01..OUT-10) and the Rev1 manifest hand-off are under review (T-06, T-08, T-09).
- **2026-10-19.** Next: T-01.
- **2026-10-19 12:08.** T-01 in discussion. The owner leans towards fully hosted, to test the harness on everything an app build needs. If hosted, the API is two-way. Claude's feasibility review is in `topics/T-01-where-it-runs.md`: feasible, build in layers, deploy spike to pick the host (Replit first). New topic T-27 added: what the harness must do for a hosted app.
- **2026-10-19 12:26.** T-01 mostly decided (D-31..D-35):
  - fully hosted, with a two-way API;
  - the authors list through GitHub (read-only token);
  - an admin page to browse;
  - extra keys are fine but kept to a minimum;
  - the owner can deploy by hand from Replit.

  Q-03 superseded, Q-25 resolved. Still open in T-01: which host (options beyond Replit in the notes).
- **2026-10-19 12:33.** T-01 host: the owner is exploring Railway, may move Library-AI there too, and wants the harness to deploy and test by itself. Claude looked at Railway in detail (notes: "Railway in detail"):
  - it covers every requirement, via environments, temporary copies per pull request, buckets, cron, Postgres backups, the CLI and an MCP server;
  - estimate: about $8–15/month on Hobby;
  - caveat: its config format changes on 2026-12-01.

  Recommendation: Railway (Hobby), after a one-hour spike.
- **2026-10-19 12:43.** At the owner's request, Claude wrote `handoffs/harness-throwaway-test.md` (HT-01..HT-29): what a throwaway hosted app must prove before feature work. The owner plans the test separately and is checking Railway hosting in the other chat. Claude keeps the file updated. T-01's host stays open until then.
- **2026-10-19 18:10.** Relayed from the library's planning:
  - **T-01 closed:** host Railway (D-36), Replit spike skipped. Rev1's `hosting-railway-review.md` is written for both projects, to be copied here once it's on GitHub; its latest commit there is still 2026-10-18.
  - **T-05 closed:** approval and the main portrait are decided in the library's queue and reported back (D-38).
  - **T-09 mostly decided:** this project owns the API and its OpenAPI file; the library adopts it, pulls, and sends decisions back; three-portrait scope adopted (D-37).

  Next: T-02.
- **2026-10-19 18:40.** T-02 opened. Mock-ups of the black-and-white version (A white line, B no line, C black edge) on light, dark and coloured pages (`prototype/versions.py`). Finding: inside the outline there is only one possible picture, so the choice is the edge. Proposals in `topics/T-02-three-versions.md`. Item 5 (working files) added. Waiting for the owner.
- **2026-10-19 19:00.** **T-02 decided** (D-39). The owner changed three of Claude's proposals:
  - black-and-white option C (black edge), not A;
  - a PNG viewing copy, not a JPEG;
  - 500 px copies as well as 1,000 px;
  - AI working files offered to the library, not internal only.

  Recipe 0.4.0 makes the versions; the white master is unchanged. Requirements STY-08, STY-09 and OUT-11 added, OUT-05 amended.
  - Carried forward: T-06 confirms the names, T-08 serves the eight files, T-13 sets each file's licence and credit (the AI copy included), and T-15 tunes the black-and-white version if needed.

  Next: T-03.
- **2026-10-19 19:20.** **T-03 decided** (D-40). The owner took Claude's proposals on what's different, which three, and better copies of approved portraits. On turn-downs the owner chose "only as a clearly better copy", not "never". PIP-14..PIP-17 added. Next: T-04.
- **2026-10-19 19:35.** **T-04 decided** (D-41): no category scheme ("this kind of detail isn't important for my needs"). An approximate date is kept for the spread across life; the library can correct it (PIP-18). T-05 was already decided, so next: T-06.
- **2026-10-19 19:50.** **T-06 decided** (D-42):
  - files in the tool's bucket, and the library keeps its own copies of what it pulls;
  - history kept;
  - database backups only, at first;
  - a read-only admin page.

  OUT-12 and OUT-13 added; OUT-01 and OUT-09 withdrawn. T-08 now needs a "changed since" listing with checksums. Next: T-07.
- **2026-10-19 20:00.** T-07 drafted in full as a proposal (`topics/T-07-records.md`), since it is mostly technical:
  - eight records;
  - stable ids;
  - turn-down reasons;
  - library decisions recognised if sent twice;
  - no personal details of library admins.

  Waiting for the owner's look.

