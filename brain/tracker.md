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
| T-07 | The records: what we keep about teachers, portraits, versions and sources | 2 Data | T-02 – T-05 | **decided** (D-43): as proposed ([notes](topics/T-07-records.md)) |
| T-08 | The library API | 2 Data | T-01, T-06, T-07 | **decided** (D-44): one key, pull only, requests at once; [OpenAPI draft 1](contracts/portraits-api.openapi.json) |
| T-09 | The contract with Library-AI (Rev1) | 2 Data | T-08 | **mostly decided** (D-37): this project owns the API and its OpenAPI file; the library adopts it |
| T-10 | The teacher list (from the pipeline's authors) | 3 Finding | none | **decided** (D-22, D-45): active only; two sources must agree; unknowns skipped and listed |
| T-11 | Picture sources | 3 Finding | T-07 | **decided** (D-46): Commons, LoC, Wellcome; Smithsonian only if the survey shows gaps; NYPL and DPLA dropped ([notes](topics/T-11-picture-sources.md)) |
| T-12 | Match rules: when a picture certainly shows the teacher | 3 Finding | T-10, T-11 | **decided** (D-47): three rules, LoC name ids, any medium (trial decides) |
| T-13 | Rights, licences and credits | 3 Finding | T-02, T-07, T-11 | **decided** (D-48): CC0 for portraits of public-domain originals; "Portrait by New Thought Nexus" |
| T-14 | The white-dot version: processing recipe | 4 Processing | T-02 | **decided** (D-49): recipe 0.4.0 is the starting point; code-drawn outline only |
| T-15 | The black-and-white version: style and recipe | 4 Processing | T-02, T-14 | **mostly decided** (D-39: option C, made from the master's layers) |
| T-16 | Telling portraits apart (same photo or a different one) | 4 Processing | T-03, T-14 | **decided** (D-50): fingerprint, feature matching, model tie-break; unsure means the same |
| T-17 | Checks and failure rules | 4 Processing | T-02, T-03, T-14, T-15 | **decided** (D-51): one remake with a fresh AI copy; one AI check per draft |
| T-18 | Models and prompts | 4 Processing | T-14 – T-17 | **decided** (D-52): Haiku pre-checks, Sonnet draft checks and tie-breaks; Nano Banana Pro enhances |
| T-19 | How runs work | 5 Running | T-01, T-05, T-08 | **decided** (D-53): nightly, requests at once, monthly re-search, library email + admin page |
| T-20 | Spend | 5 Running | T-03, T-18, T-19 | **decided** (D-54): first run $100; then $10 a night, $30 a month; trial $30 |
| T-21 | Security | 5 Running | T-01, T-08 | **decided** (D-55): one admin password; the same AI key everywhere, with low caps off production |
| T-22 | The trial | 5 Running | T-14 – T-18, T-20 | **decided** (D-56): three enhance models; the checker picks, the owner can veto; no-blend shown beside |
| T-23 | Stack and architecture | 6 Build | T-01, T-06, T-08 | **decided** (D-57): TypeScript like the library; [architecture v2](spec/architecture.md) proposed |
| T-24 | Testing approach | 6 Build | T-23 | **proposed in full** (D-09; [build plan §5](plan/build-plan.md)): node:test, PGlite, contract tests, smoke tests on PR copies |
| T-25 | Feature cards for the harness | 6 Build | all above; the harness format (D-15) | **next** |
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

### T-07 · The records: what we keep · **decided**
- **Depends on:** T-02 – T-05.
- **To decide:**
  1. **Teacher:** id, names, dates, Wikidata id, link to the authors list.
  2. **Portrait:** id, teacher, approximate date and best-known flag (D-41, with the library's corrections), status, main or not, `replaces` (for a better copy), history.
  3. **Version:** the file, its size, checksum and recipe version.
  4. **Source and rights:** from the rights log (SRC-12).
  5. **Checks and costs.**
  6. **Ids:** stable across runs.
- **Decided so far:** complete credit metadata for every portrait (D-14). Every original considered is logged (SRC-12, proposed).
- **Decided (D-43), as proposed** in [topics/T-07-records.md](topics/T-07-records.md): the teacher, candidate (rights log), portrait, file, library decision, request, run and spend records, and the portrait history.
- **Linked:** OUT-02 (the Rev1 manifest schema, probably replaced; see T-09), SRC-08, SRC-11, SRC-12.

### T-08 · The library API · **decided**
- **Depends on:** T-01, T-06, T-07.
- **To decide:**
  1. **What the library can read:** teachers; portraits by teacher; the eight files of each portrait (OUT-11, D-39, the AI-enhanced copy and mask included); credits and rights; what's changed since a date.
  2. **What the library can send** (if T-01 allows): approvals, turn-downs, requests, the main-portrait choice.
  3. **Access:** a key per client, and read-only versus read and write.
  4. Versioning of the API, and its documentation (an OpenAPI file).
  5. Whether the tool tells the library when something is new, or the library only pulls. *(Added 2026-10-19.)*
  6. How quickly the library's requests are handled: at once, or at the next scheduled run. *(Added 2026-10-19; it shapes the API's answer to a request.)*
- **Decided so far:**
  - an API, for the library to pull records (D-28);
  - the library adopts this project's OpenAPI file, pulls, and sends decisions back (D-37);
  - it keeps its own copy of what it pulls, so a change listing with checksums is needed (D-42).
- **Claude's choices** (technical), mirroring the library's own API (Rev1 `brain/contracts/api.openapi.json` at 3e444eb) so its builders find the same patterns:
  - OpenAPI 3.1, paths under `/api/v1/`;
  - bearer keys stored only as hashes;
  - the same error object (`kind`, `message`) and error kinds;
  - a change feed with `since` / `after` / `next_cursor` / `more`, kept for 30 days;
  - files served by short-lived signed links;
  - within v1, changes are additive only.
- **Decided (D-44):**
  - one key for reading and sending;
  - the library checks the change feed on its own schedule, and the tool never calls it;
  - requests are handled right away.
- **Written into:**
  - `contracts/portraits-api.openapi.json` (draft 1), with samples, a plain-words page and an offline check;
  - OUT-14; IN-06 and IN-07 amended.

### T-09 · The contract with Library-AI (Rev1) · **mostly decided**
- **Depends on:** T-08.
- **To decide:**
  1. ~~Who owns the contract now~~. **Decided (D-37):** this project defines the API and the records and publishes an OpenAPI file. The library adopts it, pulls, and sends its decisions back. The library has also adopted the three-portrait scope.
  2. ~~What to tell the Rev1 planning~~. **Done:** [handoffs/library-api.md](handoffs/library-api.md), for the owner to pass to the library chat.
  3. **Whether we still need Rev1's portrait files (O-1).** Probably only to see which of the PORT requirements still apply. Rev1 is now readable here, so Claude copies them once the library's latest planning is pushed (Rev1's GitHub is still at 3e444eb, 2026-10-18, before it adopted this API).
  4. **OUT-08, the bulk-upload zip:** still needed now that the library pulls through the API? Proposed: withdraw it.
- **Linked:** Q-09, Q-16, O-1, OUT-10, AC-02, AC-03.

## Stage 3: Finding pictures

### T-10 · The teacher list · **decided**
- **Depends on:** nothing.
- **Decided so far:**
  - The list comes from library-pipeline's `authors.csv`, read-only (D-22).
  - The sync keeps stable ids (IN-12).
  - Missing dates and Wikidata ids are filled when two sources agree (IN-13).
- **To decide:**
  1. `active` authors only? (Q-26)
  2. Date forms (Q-12) and duplicate ids (Q-13).
  3. With book plates dropped (D-24), what fills dates for the ~110 active authors without them? Wikidata, plus the LoC name authority (Q-01)?
- **Decided (D-45):**
  - active authors only;
  - gaps filled only when Wikidata and the LoC name authority agree. The rest are listed with evidence, as a CSV of suggestions for `authors.csv`;
  - a teacher still without an id or dates is skipped and listed;
  - teachers live in the app's database (Claude's choice). Date forms and id clashes are Claude's choices too.
- **Resolved:** Q-01, Q-12, Q-13, Q-26; Q-14 superseded. **Written into:** IN-12, IN-13.

### T-11 · Picture sources · **decided**
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
- **The review:** [topics/T-11-picture-sources.md](topics/T-11-picture-sources.md) (2026-10-19). Findings:
  - NYPL's API was retired on 1 August 2026;
  - Wikimedia's 2026 limits require an identifying User-Agent;
  - the Library of Congress allows 20 searches a minute.
- **Proposed:**
  - first build on the three keyless sources plus the LoC name authority;
  - DPLA as listed leads later;
  - a coverage survey early in the build to decide the keyed sources.
- **Decided (D-46):**
  - first build: Wikidata/Commons, the Library of Congress and Wellcome, with no keys, plus the LoC name authority;
  - Smithsonian only if the coverage survey shows gaps;
  - NYPL dropped (API retired);
  - DPLA not used at all.
- **Written into:** SRC-01, SRC-09, SRC-14 (coverage survey); `spec/sources.md` updated.
- **Linked:** [spec/sources.md](spec/sources.md), SRC-01, SRC-02, Q-23, Q-25.

### T-12 · Match rules · **decided**
- **Depends on:** T-10, T-11.
- **Decided so far:**
  - Certain matches only (D-03): R1 Wikidata image, R2 Commons depicts, R3 a picture record with name and dates.
  - Owner's links are accepted (SRC-04).
  - Book plates (R4) are withdrawn (D-24).
- **To decide:**
  - checking and finding Wikidata ids (SRC-06, Q-01);
  - the R3 details for each new source;
  - engravings and drawings (Q-11).
- **Decided (D-47):**
  - any medium that passes the pre-check, with the trial deciding about engravings;
  - R3 also matches on the teacher's LoC name id;
  - pasted links may point to any adopted source;
  - SRC-06 follows D-45.

### T-13 · Rights, licences and credits · **decided**
- **Depends on:** T-02, T-07, T-11.
- **Decided so far:**
  - The allowed licence tiers (D-03).
  - Complete credits (D-14).
  - A permanent rights log (SRC-12, proposed).
- **To decide:**
  1. The licence of each derived version, especially from CC BY-SA originals (Q-16, SRC-11). This now includes the AI-enhanced copy and the mask, which are offered to the library too (D-39).
  2. Whether the original file may be shown by the library, and with what credit.
  3. The credit-line format for each source.
- **Decided (D-48):**
  - portraits made from public-domain or CC0 originals are CC0;
  - credit lines say "Portrait by New Thought Nexus, adapted from: <original credit>";
  - CC BY originals give CC BY 4.0 adaptations, and CC BY-SA originals give CC BY-SA 4.0 (Claude's rules, SRC-11);
  - whether the library shows originals is the library's own rule.
- **Written into:** SRC-11; the API's `File` gains `licence_url` (draft 2). Q-16 resolved.

## Stage 4: Processing and checking

### T-14 · The white-dot version: processing recipe · **decided**
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
- **Decided (D-49):**
  - the board is close enough to build on: recipe 0.4.0 is the starting point, and the trial may tune it;
  - the outline is drawn by code only;
  - cut-out sanity limits (PIP-19) are Claude's proposal.
- **Written into:** STY-07, PIP-07, PIP-19, TRI-03; F-20 withdrawn; Q-05 resolved.

### T-15 · The black-and-white version · **mostly decided**
- **Depends on:** T-02, T-14.
- **Decided (D-39, at T-02):**
  - option C, black edge, prototyped and chosen (`recipe.bw_version`, STY-08);
  - it is made from the master's own layers, so it shares the white version's tones, crop, cut-out and footprint by construction.
- **Left:** a look at it on real AI-enhanced copies (F-27, F-28), along with T-14's verdict.

### T-16 · Telling portraits apart · **decided**
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
- **Decided (D-50):**
  - when even the model is unsure, it's the same photograph;
  - the method is Claude's three layers (PIP-20). The prototype separates copies (56–330 matching points) from different photographs (19 or fewer);
  - real pairs, including two sittings of one teacher, come from the coverage survey before the thresholds are relied on.

### T-17 · Checks and failure rules · **decided**
- **Depends on:** T-02, T-03, T-14, T-15.
- **To decide:**
  - which checks run on which version (does the black-and-white version need its own draft check?);
  - remaking a draft (Q-06) and limits (Q-07), now that there can be several portraits per teacher;
  - the cut-out sanity check.
- **Decided (D-51):**
  - one remake with a fresh AI copy, then set aside;
  - no separate AI check for the black-and-white version;
  - per run, at most 6 drafted and 12 pre-checked per teacher (Claude's);
  - the cut-out sanity check is PIP-19.

  Q-06 and Q-07 resolved.
- **Linked:** PIP-02, PIP-09, PIP-10, PIP-11.

### T-18 · Models and prompts · **decided**
- **Depends on:** T-14 – T-17.
- **Decided so far:**
  - One key: OpenRouter (D-19).
  - Claude writes the prompts (D-20; `prototype/prompts/`).
  - The starting models (Nano Banana Pro, with challengers).
- **To decide:**
  - a prompt for the distinctness tie-break (T-16) and for categories (T-04);
  - checker models;
  - the family rule.
- **Decided (D-52):**
  - Claude Haiku 5.5 for pre-checks;
  - Claude Sonnet 5.5 for draft checks and the same-photograph tie-break;
  - the family rule holds against the Google and OpenAI image models;
  - prompts: `same_photo.md` added, `precheck.md` v2 (age estimate), `outline.md` withdrawn. Categories need no prompt (D-41).

## Stage 5: Running, cost and safety

### T-19 · How runs work · **decided**
- **Depends on:** T-01, T-05, T-08.
- **To decide:**
  - on demand or scheduled (daily, like the pipeline);
  - resuming;
  - re-runs (Q-02);
  - the library's requests;
  - the run report;
  - notifications to your phone.
- **Decided (D-53):**
  - nightly, with requests handled at once;
  - sources searched again monthly;
  - you hear through the library's daily email, the admin page and Railway's alerts;
  - a Try-again note guides a fresh AI copy.

  Q-02 and Q-08 resolved. **Written into:** RUN-01, RUN-02, RUN-07, RUN-08, RUN-09, IN-06; and a request in `handoffs/library-api.md`.
- **Linked:** RUN-01..RUN-07.

### T-20 · Spend · **decided**
- **Depends on:** T-03, T-18, T-19.
- **To decide:**
  - the per-run cap ($250 for the first run, D-06);
  - a per-teacher cap, now that there can be 3 portraits;
  - the trial's budget (TRI-07).
- **Starting estimate:** about 17–25 cents per portrait processed, plus a few cents per candidate checked. With 182 teachers, most having 0–1 portraits, the first run is likely $50–120.
- **Decided (D-54):**
  - first full run $100 (estimate $40–80);
  - then $10 a night and $30 a month;
  - trial $30 (estimate $5–10);
  - $2 per teacher per run (Claude's);
  - a credit limit on the OpenRouter key as the owner's backstop.

### T-21 · Security · **decided**
- **Depends on:** T-01, T-08.
- **To decide:**
  - the library's API key;
  - where secrets live;
  - what is reachable from the internet (nothing on your PC, preferably);
  - backups.
- **Decided (D-55):**
  - one admin password;
  - the same OpenRouter key in every environment, with $2-a-night caps off production (Claude's);
  - the rest is Claude's (RUN-10): hashed keys, HTTPS, a private bucket, signed links, rate limits, outbound allowlist, no PC exposure;
  - backups as D-42.

### T-22 · The trial · **decided**
- **Depends on:** T-14 – T-18, T-20.
- **To decide:**
  - the trial set, now including teachers with several portraits and known copies of the same photograph (to test T-16);
  - contenders (enhance models, with and without the blend);
  - the board;
  - "close" (Q-19).
- **Decided (D-56):**
  - the checker's scores pick the winning enhance model, and the owner can veto;
  - the board shows each result without the blend too;
  - the trial set, contenders, "close" (within 5%) and the board on the admin page are Claude's.
- **Linked:** TRI-01..TRI-08, P0-4.

## Stage 6: Building it with the harness

### T-23 · Stack and architecture · **decided**
- **Depends on:** T-01, T-06, T-08.
- **To decide:**
  - the language (Q-15, Python proposed);
  - the API framework and database (if T-01 chooses a hosted service);
  - hosting;
  - a refresh of `spec/architecture.md`.
- **Decided (D-57):** TypeScript on Node 24, like the library, so the harness rehearses its toolchain. The image steps are ported from the Python prototype to OpenCV.js and `sharp`, with a porting spike first. **Written:** `spec/architecture.md` v2 (hosted, proposed). Q-15 resolved.

### T-24 · Testing approach · **proposed in full**
- **Depends on:** T-23.
- **Decided so far:** the owner's standard (D-09): simple, offline fixtures, live tests only where needed.
- **To decide:** how to test the API, and what fixtures the distinctness check needs.
- **Proposed** (`plan/build-plan.md` §5, rewritten for TypeScript):
  - `npm test` with `node:test`, offline;
  - PGlite for the database;
  - fixtures including the Python reference outputs and same-photograph pairs;
  - API contract tests with `ajv` against the OpenAPI file;
  - smoke tests on PR copies and staging;
  - live tests only on *live* cards.

  Nothing here needs the owner unless a reviewer objects.

### T-25 · Feature cards for the harness · **next**
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
- **2026-10-19 21:05.** **T-07 decided** (D-43): the owner raised nothing on the proposal and moved on. T-08 opened. Claude's technical choices mirror the library's own API conventions. Owner choices asked: keys, notifying the library, and how fast requests are handled.
- **2026-10-19 21:20.** **T-08 decided** (D-44): one key, pull only, requests at once.
  - OpenAPI draft 1 written (11 routes, 23 schemas). Its conventions copy the library's own API.
  - Samples and an offline check are included, and the check passes, refused payloads included.
  - The T-07 note is aligned: the request kinds take IN-06's names, and approving a better copy is the swap.
  - Hand-off note for the library chat: `handoffs/library-api.md`.
  - T-09 waits on Rev1's push for O-1.

  Next: T-10.
- **2026-10-19 21:35.** **T-10 decided** (D-45):
  - active only;
  - two sources must agree (Wikidata and the LoC name authority);
  - unknowns skipped and listed, with a CSV of suggestions for `authors.csv`.

  Q-01, Q-12, Q-13 and Q-26 resolved; Q-14 superseded. Next: T-11, the formal review of the picture sources.
- **2026-10-19 21:55.** T-11 review written (`topics/T-11-picture-sources.md`), with each source's access checked against its own documentation:
  - NYPL's API was retired on 1 August 2026, so it is proposed dropped;
  - Wikimedia's 2026 limits need a proper User-Agent;
  - the LoC allows 20 searches a minute;
  - Wellcome is keyless; Smithsonian and DPLA need free keys.

  Waiting for the owner.
- **2026-10-19 22:05.** **T-11 decided** (D-46):
  - the three keyless sources;
  - Smithsonian only if the survey shows gaps;
  - NYPL dropped;
  - DPLA not used.

  SRC-01 and SRC-09 updated, SRC-14 (coverage survey) added, `spec/sources.md` revised. Next: T-12.
- **2026-10-19 22:15.** **T-12 decided** (D-47): any medium, with the trial deciding (Q-11 resolved). Claude's refinements: R3 by LoC name id, Wellcome links accepted, SRC-06 aligned with D-45. Next: T-13.
- **2026-10-19 22:30.** **T-13 decided** (D-48): CC0 for portraits made from public-domain originals; credit "Portrait by New Thought Nexus, adapted from …"; BY and BY-SA rules per SRC-11. API draft 2 adds `licence_url`. Next: T-14.
- **2026-10-19 22:45.** **T-14 decided** (D-49): the board is good enough to build on (recipe 0.4.0 is the starting point), and the outline is drawn by code only. Model-drawn outlines are dropped from the method and the trial (F-20 withdrawn, TRI-03 amended). PIP-19 cut-out limits proposed. Next: T-16.
- **2026-10-19 22:55.** **T-16 decided** (D-50): when unsure, it's the same photograph. The method (PIP-20) was prototyped in `prototype/same_photo.py`: copies scored 56–330 and different photographs at most 19. Next: T-17.
- **2026-10-19 23:05.** **T-17 decided** (D-51): one remake with a fresh AI copy; the black-and-white version is checked by code only. Per teacher per run, 6 drafts and 12 pre-checks at most. Q-06 and Q-07 resolved. Next: T-18.
- **2026-10-19 23:15.** **T-18 decided** (D-52): Haiku 5.5 pre-checks, Sonnet 5.5 draft checks and tie-breaks, all through OpenRouter. Prompts updated. Next: T-19.
- **2026-10-19 23:25.** **T-19 decided** (D-53): nightly runs with requests at once; monthly re-search; updates through the library's daily email, the admin page and Railway alerts; Try-again notes guide a fresh AI copy. Q-02 and Q-08 resolved. Next: T-20.
- **2026-10-20 00:05.** **T-20 decided** (D-54): $100 first run; $10 a night and $30 a month after; trial $30. The owner-input list is updated for the hosted app: O-4 is now a Railway variable with a credit limit; O-5 is withdrawn; O-8..O-11 added (Railway account, GitHub token, User-Agent contact, the library's key). Next: T-21.
- **2026-10-20 00:15.** **T-21 decided** (D-55): one admin password; the same OpenRouter key everywhere, with low caps for staging and pull-request copies. RUN-10 added. Next: T-22.
- **2026-10-20 00:25.** **T-22 decided** (D-56): the three enhance models compete; the checker picks the winner and the owner can veto; no-blend versions are shown beside each result. Q-19 resolved. Next: T-23, the stack and architecture rewrite for the hosted app.
- **2026-10-20 00:40.** **T-23 decided** (D-57): TypeScript, like the library, against Claude's recommendation of Python. That's a fair trade for the harness's purpose. Architecture v2 written for the hosted app:
  - Express, Drizzle, Postgres queue, S3 bucket;
  - `sharp` plus OpenCV.js;
  - a porting spike with fallbacks;
  - the Python prototype as the reference.

  Next: T-24.
- **2026-10-20 00:50.** T-24 proposed in full (build plan §5, for TypeScript): `node:test`, PGlite, contract tests against the OpenAPI file, smoke tests on deployed copies, live tests only on live cards. Next: T-25, rewriting the feature cards. It needs the harness's card format if the harness chat has settled one (D-15).

