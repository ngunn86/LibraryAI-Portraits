# Requirements: Nexus Portraits

This file is normative. "Must" is required; "should" is the default unless a good reason is recorded. Every requirement has:

- **an ID**, which is permanent;
- **a status**: *fixed*, *proposed*, or *open (Q-nn)*;
- **an origin**: B2 = current brief, B1 = first brief, C = Claude's review, D-nn = a decision;
- **Verify**: how a machine (or, rarely, the owner) confirms it.

Conventions are in [../README.md](../README.md).

> **Rework pending (2026-10-19).** The owner's new requirements change what the tool produces and how it hands off:
>
> - up to 3 different portraits per teacher (D-25);
> - three versions of each (D-26);
> - organised by teacher (D-27);
> - an API for the library (D-28).
>
> T-02 is decided (D-39): the versions are STY-08, STY-09 and OUT-11, and OUT-05 is amended. T-03 is decided (D-40): PIP-14..PIP-17, with PIP-11 and SRC-07 amended. T-04 is decided (D-41): no category scheme, PIP-18. T-06 is decided (D-42): storage in the bucket (OUT-12) and the admin page (OUT-13); OUT-01 and OUT-09 withdrawn. T-08 is decided (D-44): the API (OUT-14); IN-06 and IN-07 amended. T-10 is decided (D-45): IN-12 and IN-13. T-11 is decided (D-46): SRC-01, SRC-09, SRC-14.
>
> The requirements they touch are under review until the matching tracker topics are decided: SCOPE-01, SCOPE-02, PIP-01, PIP-11, SRC-07, OUT-01..OUT-10, RUN-01, RUN-02, TRI-*, AC-02 and AC-03 (topics T-01..T-09 in [../tracker.md](../tracker.md)). Until then, read them as describing one portrait per teacher, delivered to a folder.

> **Reconciliation pending.** Library-AI---Rev1 holds the original `tool`-tagged requirement lines: PORT-001 to 022, PORT-040, PORT-070 to 081 and PORT-091.
>
> - Every one of those lines must map to at least one requirement here, and any difference becomes an open question.
> - Until that is done, every requirement below is provisional on it. The mapping table at the end is still empty.
> - Status: waiting on owner input O-1 (see [../plan/build-plan.md](../plan/build-plan.md)).

---

## 1. Scope

**SCOPE-01 · What the tool does** *fixed* · B2
For every teacher on the owner's list who has no approved portrait, the tool:

- finds a public-domain or openly licensed photograph that certainly shows them;
- makes a portrait in the owner's style;
- checks it;
- delivers it, with its rights record, to the delivery folder.

**SCOPE-02 · Independent of the library** *fixed* · B2
Nothing in the tool may depend on Library-AI running. The tool's only links to the library are:

- the files the library writes into the delivery folder: `requests.json` and `status.json`;
- the files the tool writes there: the runs.

**SCOPE-03 · Nothing goes live from the tool** *fixed* · B2
Every portrait is a draft that waits for an admin's approval in the library. The tool never serves images to readers.

**SCOPE-04 · Out of scope** *fixed* · B2
The following are Library-AI's build, not this project:

- the Drive door that reads the folder;
- the queue item;
- the people screen;
- the credits page;
- the blank portrait;
- choosing which teachers exist beyond the list;
- editing the library's records.

---

## 2. Inputs

**IN-01 · Teacher list** *fixed* · B2; source *proposed* · D-22
The tool reads `teachers.csv`: UTF-8, with a header row, one row per teacher. The columns are `teacher_id`, `name`, `born`, `died`, `wikidata_qid`, `aliases` and `notes`, as defined in [../contracts/teachers-csv.md](../contracts/teachers-csv.md).

The file is **generated** from the library-pipeline's `collection/authors.csv` (read-only) by `portraits teachers sync` (IN-12). The owner keeps one list of authors, and the portraits follow it.
*Verify:* unit tests over fixture lists.

**IN-02 · Bad rows are refused by name, the rest load** *fixed* · B2; details *proposed* · C
- A row is refused if it has any of these:
  - a bad slug;
  - an impossible date;
  - a malformed Wikidata id;
  - a missing name;
  - a duplicate `teacher_id`.
- Each refusal is named, with row number, `teacher_id` and reason, in both the command's output and the run report.
- The other rows load.
- The exact definitions are in the contract; some are *proposed* (Q-12, Q-13).

*Verify:* one fixture per refusal reason; each one is refused with its row named.

**IN-03 · A broken file stops the run before any spending** *proposed* · C
The tool refuses the whole file, before any network call, when:

- the file isn't UTF-8;
- it has no header;
- a required column (`teacher_id`, `name`, `born`, `died`) is missing;
- it has no valid rows.

*Verify:* fixtures; no network or model client is called.

**IN-04 · Which teachers can be searched, and by which rules** *fixed* in principle · B2; *open (Q-01)* in detail

| What the row has | Match rules that may be used | Notes |
|---|---|---|
| A Wikidata id | SRC-03 rules 1, 2 and 3 | Rule 3 needs both years, from the list or, failing that, from Wikidata (proposed) |
| Both years, no Wikidata id | Rule 3. Rules 1 and 2 only if the tool resolves a Wikidata id itself under SRC-06 (proposed, Q-01) | |
| Neither a Wikidata id nor both years | B2 says "only an authority match counts", but doesn't define one (Q-01). Proposal: the teacher is skipped and named in the report, with "add a Wikidata id" | |

**IN-05 · Notes are never used for matching** *fixed* · B2
The `notes` column is for the owner only. No code path may read it for searching or matching; it may be echoed in the report.
*Verify:* a test proves that a row's notes don't change its candidates.

**IN-06 · Requests** *fixed* · B2; format *proposed* · C
When `requests.json` is present in the delivery folder, the tool reads it. The format is in [../contracts/requests-and-status.md](../contracts/requests-and-status.md). The three kinds of request are:

- `try_again`: make a new draft from the same original, with the admin's note (what a note may change is Q-08).
- `another_original`: set aside the current original and use the next candidate.
- `try_link`: try a pasted Commons or Library of Congress link (SRC-04).

A request naming a teacher who isn't on the list is skipped and named in the report.
*Verify:* run fixtures (F-26).

*Amended by D-37, D-44:* requests now arrive through `POST /api/v1/requests` (OUT-14), not `requests.json`, and are handled right away. The three kinds keep their names.

**IN-07 · Status** *fixed* · B2; format *proposed* · C
When `status.json` is present, the tool reads it:

- **Approved** teachers are skipped.
- A **turned-down** original is set aside at once (PIP-11).
- **Waiting** teachers are handled as in RUN-02.

When the file is absent, nothing counts as approved.
*Verify:* run fixtures (F-26).

*Amended by D-38, D-44:* the library's decisions now arrive through `POST /api/v1/decisions` (OUT-14), not `status.json`. Approved, turned down (with a reason, PIP-17), main portrait and corrections are recorded as they arrive.

**IN-08 · Handled requests aren't redone** *proposed* · C (Q-02)
The tool records each request id it has acted on. A request already acted on isn't redone in a later run, even if the library hasn't removed it from `requests.json` yet.
*Verify:* the second of two runs over the same `requests.json` makes no draft for that request.

**IN-09 · The owner's examples** *fixed* · B2, D-13
`design/portraits/` holds the owner's three hand-made portraits (`targets/`), which are the style target, and their originals (`originals/`). These cover Charles Fillmore, Emilie Cady and Ernest Holmes. The trial also uses the originals (TRI-02). Their source is unknown, so they are test inputs and style targets only, and are **never delivered** (D-13). Sizes and notes are in `design/portraits/README.md`.

**IN-10 · Settings file** *fixed* · B2; layout *proposed* · C
One settings file, committed to the repo, holds everything except keys:

- the recipe settings and `recipe_version`;
- the model for each role;
- the spend cap;
- the delivery target;
- the paths to the list and the examples;
- the contact line for the tool's User-Agent.

An invalid setting stops the tool with a message naming the setting. The layout is in [architecture.md](architecture.md).
*Verify:* unit tests.

**IN-12 · Teacher list from the pipeline's authors** *fixed* · D-22, D-45; details *proposed* · C
- `portraits teachers sync` reads `authors.csv` from the private library-pipeline repo through the GitHub API (D-32), with a read-only token limited to that repo. It is never written to.
- **Which authors:** only `active` rows (182 on 2026-10-19, the same rule the pipeline uses; Q-26).
- **How it builds or updates `data/teachers.csv`:**
  - `name` comes from `name`.
  - `aliases` comes from `aliases`, splitting on `;` (pen names and spellings), which are also used for matching.
  - `born` and `died` come from `dates` (`1802-1866`; forms the tool can't read are left blank and reported).
  - `notes` comes from stream and tier.
- **Stable ids:** a `teacher_id` is made once, as a slug of the name, and kept in `data/teacher-ids.csv`. A renamed author keeps their id. Authors no longer active are flagged in the report, not deleted.
- **Enrichment (IN-13)** fills `wikidata_qid` and missing dates. Only 71 of the 182 active authors have dates.

*Amended by D-45 (hosted app):*
- the sync writes the app's database, not `data/teachers.csv`, and the stable ids live there too;
- `active` rows only;
- dates are read in the `authors.csv` forms (`YYYY-YYYY`, `d. YYYY`, `b. YYYY`). Any other form is unknown and reported;
- a clashing slug gets `-2` and is reported.

*Verify:* a fixture `authors.csv` syncs to the expected teachers. A rename keeps the id. A second sync changes nothing.

**IN-13 · Finding missing dates and Wikidata ids** *fixed* · D-45; method *proposed* · C
- For each teacher without them, the tool proposes a Wikidata id and life dates from two independent places:
  - the Wikidata search under SRC-06b;
  - the author headings in the catalogue records of the teacher's own books (for example `Fillmore, Charles, 1854-1948`).
- It accepts them automatically only when both agree on the person and both years (D-45). The second source is the **LoC name authority** (id.loc.gov), whose headings carry life dates. Other catalogue headings may support it, but never come from books (D-24).
- Anything else is listed on the admin page with the evidence. It can be downloaded as a CSV of suggested additions for `authors.csv`, which the owner makes there. The tool never writes to library-pipeline.
- **A teacher still without a Wikidata id or both years is skipped** and listed. Once the owner adds them to `authors.csv`, the next sync picks them up (D-45).

*Verify:* fixtures where both sources agree (accepted), disagree (proposed only), or only one has data (proposed only).

**IN-11 · Keys live outside the repo** *fixed* · B2
- The OpenRouter key (the tool's only AI key; D-19), and any Drive credential, are read only from environment variables, or from a keys file outside the repo.
- They are never written to logs, reports, the state store or the delivery folder.

*Verify:* a test scans every file a stubbed run writes and finds no key value.

---

## 3. Sources, rights and matching

**SRC-01 · Adopted sources only, enforced in code** *fixed* · B2, widened by D-21; which sources *fixed* · D-46
- Originals come only from the sources marked adopted in [sources.md](sources.md).
- **Adopted for the first build (D-46):**
  - Wikidata with Wikimedia Commons;
  - the Library of Congress (Prints & Photographs);
  - Wellcome Collection;
  - plus the LoC name authority (id.loc.gov), which identifies teachers and supplies no pictures.
- Smithsonian Open Access is added only if the coverage survey (SRC-14) shows gaps.
- **Not used:** NYPL (its API was retired on 1 August 2026), DPLA (D-46), and the Internet Archive and book plates (D-24).
- The tool's source client may contact only the hosts of the adopted sources (listed in settings).
- The model client may contact only the configured model API hosts.
- Any other host is refused. This is also how SRC-10 is enforced.

*Verify:* a unit test shows a request to any other host fails before leaving the process.

**SRC-02 · Allowed licences, in two tiers** *fixed* · B2; edge cases *proposed* · C
- **Tier 1:**
  - public domain (any Commons public-domain mark);
  - CC0;
  - the Library of Congress's "No known restrictions on publication".
- **Tier 2:** CC BY and CC BY-SA, any version.
- **Refused, always:**
  - NC and ND licences;
  - fair use or non-free;
  - unknown or missing rights;
  - GFDL alone;
  - custom "attribution" terms that aren't CC BY;
  - the Library of Congress's "rights status not evaluated" or any restriction.
- A file under more than one licence is taken under the most open allowed one: for example, GFDL with CC BY-SA becomes CC BY-SA.
- Anything the classifier can't map is refused and logged with the raw licence text.

*Verify:* a table test over real licence strings collected from Commons and LoC responses (fixtures).

**SRC-03 · Certain matches only, in order** *fixed* · B2; rule 3 widened and rule 4 added *proposed* · D-21 (details in [sources.md](sources.md))
A file counts as showing the teacher only by one of these rules, tried in this order:

1. **R1:** the image on the teacher's Wikidata item (property P18).
2. **R2:** Commons files whose structured data says they depict the teacher's Wikidata item (property P180).
3. **R3:** picture records (LoC Prints and Photographs, and other adopted picture sources) that name the teacher with matching dates (SRC-05).
4. ~~**R4 (book plate)**~~: *withdrawn* by D-24. Portraits are not extracted from books unless that proves absolutely necessary.

These never count:

- membership of a Commons category;
- a filename or caption that only mentions the name;
- a name match without dates;
- any search-result ranking.

*Verify:* recorded-response fixtures for each rule, plus negative fixtures: a category-only file, a name-only LoC record, and a record with the wrong dates.

**SRC-04 · An owner's link is the owner's match** *fixed* · B2; limits *proposed* · C
- A link pasted in a `try_link` request is accepted as the owner's own match, recorded as `matched_by: owner_link`.
- It must still point to a Commons file or a Library of Congress item, and its licence must pass SRC-02.
- A link to anywhere else, or one that fails the licence check, is refused and named in the report.

*Verify:* fixtures.

**SRC-05 · The Library of Congress match, precisely** *proposed* · C
A Library of Congress record matches when **both** of these hold:

- one of its name headings (for example `Fillmore, Charles, 1854-1948`), reordered to forename and surname and normalised (case, accents, punctuation), equals the teacher's name or one of the aliases, normalised the same way;
- the heading's dates equal the teacher's birth and death years.

A heading without dates never matches.
*Verify:* fixtures with matching, near-miss and undated headings.

**SRC-06 · Checking and finding Wikidata ids** *proposed* · C (Q-01)
- **(a) Sanity check of a given id.** The item must be a human (instance of Q5). Where the list gives years, the item's birth and death years must equal them.
  - On a mismatch the teacher is skipped and named in the report ("the Wikidata id may be wrong").
  - This guards against a typo producing a confident wrong portrait.
- **(b) Resolving a missing id, only when both years are known.** The tool searches Wikidata. It accepts an item only when exactly one human has:
  - a label or alias equal to the name or an alias (normalised);
  - birth and death years equal to the list's.

  The resolved id is recorded as `resolved_by_tool`, and the report lists it so the owner can add it to the list.
- **(c) No match.** With no id and fewer than two years, the teacher is skipped and named in the report.

*Verify:* fixtures for a good id, a wrong-years id, a non-human id, one candidate, two candidates and no candidates.

**SRC-07 · Choosing among candidates** *fixed* · B2; method *proposed* · C
- Candidates are ordered by licence tier first, then by pixel count, largest first.
- "Clearest" is judged by the pre-check (PIP-02), which runs in that order until one original passes.
- Duplicates are merged, keeping the strongest match rule. A duplicate is the same file reached by two rules, or the same SHA-256.
- Candidates set aside earlier (PIP-12) are excluded.
- *Since D-40:* this order picks the best copy **within** each photograph's copies (PIP-15). Which photographs fill the three slots is PIP-16.

*Verify:* unit tests.

**SRC-08 · The original's record** *fixed* · B2, D-14
Its purpose (D-14): enough to credit every portrait properly in the library. Every original used, or set aside after download, keeps:

- source (`commons` or `loc`);
- source id;
- page link and file link;
- title, author and date as given;
- licence, its tier and its link;
- credit line;
- `matched_by` (`wikidata_p18`, `commons_p180`, `loc_name_dates` or `owner_link`) and `matched_to` (the Wikidata id or LoC heading);
- file size in bytes, pixel dimensions and SHA-256.

The manifest carries the fields its schema asks for (OUT-02).

The author may be recorded as unknown when the source says so. The source, page link, licence, licence link and credit line are **never blank**; a candidate without them is refused, not delivered (*proposed* · C, from D-14).
*Verify:* every manifest record in the end-to-end fixture run is complete, and a candidate with no credit line is refused.

**SRC-09 · Polite access** *proposed* · C; User-Agent and limits *fixed* · D-46
- Every request to every source carries a descriptive User-Agent: the app's name, version and a contact address from settings.
  - Wikimedia's 2026 limits give unidentified clients far less.
  - The contact is an address set for the app, never a personal one in the repo.
- Each source is paced to its published limit:
  - the LoC JSON API: 20 requests a minute (a 1-hour block above that); 150 a minute for images and media;
  - Wikimedia: one request at a time, well under the identified limit;
  - Wellcome: one request at a time.
- Requests are retried with backoff on 429 and 5xx responses. An HTML CAPTCHA page counts as a 429.
- Responses are cached, so a resumed run doesn't fetch twice.

*Verify:* unit tests of the client's headers, pacing (a burst of 30 LoC calls takes at least a minute) and retry behaviour (429 and a CAPTCHA page both back off).

**SRC-10 · Never the library's own scans or the reference shelf** *fixed* · B2
The tool has no setting, path or code that reads Library-AI's scans or the owner's reference shelf. This is enforced by SRC-01.
*Verify:* SRC-01's test, plus code review in the harness's checks.

**SRC-11 · Derived-work rights travel with the portrait** *proposed* · C (Q-16)
- A portrait is an adaptation of its original. For CC BY and CC BY-SA originals:
  - the credit line says the portrait is adapted from the original;
  - a portrait made from a CC BY-SA original carries CC BY-SA itself.
- The tool records the portrait's licence, so the library's credits page can show it.
- Whether the manifest schema already has a field for this is part of Q-16.

*Verify:* fixture records for each tier.

**SRC-12 · The rights log** *proposed* · C, from D-21 ("pull the metadata and rights etc with these files, and keep track of them")
- Every original considered, **including the ones refused**, gets one permanent row. The row holds:
  - source, ids and links;
  - the description as given;
  - the rights evidence as given, quoted raw;
  - the rule applied, the verdict and the reason;
  - the match rule and what it matched to;
  - the credit line and the portrait's licence;
  - the file's size, pixel size and SHA-256;
  - the date retrieved.
- The raw source record (JSON) is saved in the state store. Nothing is researched twice.
- Each run exports the log to `portraits/rights-log.csv` in the delivery folder (*proposed*).

*Verify:* the end-to-end fixture run (F-26) leaves one row per original considered, refusals included, and a second run adds no duplicate rows.

**SRC-13 · Finding plates in books** *withdrawn* (D-24). Kept below for reference only, in case book plates ever become necessary.
- For each teacher, search the adopted book sources by author (name and aliases; key works first) for books before 1931.
- From small page images of the first 16 pages plus any pages listed as plates, code picks the pages that look like photographs. At most 3 per book go to the pre-check, which confirms a single portrait and reads its caption.
- A confirmed plate is downloaded at full resolution, through IIIF where offered.
- Borrow-only or restricted items are skipped, never worked around.

*Verify:* recorded fixtures for one book with a captioned author frontispiece, one with an uncaptioned one and one with no plates. Code picks the plate page; a text-only page is never picked.


**SRC-14 · Coverage survey** *proposed* · C (D-46) · *live*
- Early in the build, a survey run searches every active teacher on every adopted source, and reports what each would find:
  - candidates by match rule;
  - their licence tier;
  - their size.
- It downloads no files, makes no AI calls, and creates no portraits.
- Its report shows how many teachers each source covers, and which have nothing. That decides whether Smithsonian Open Access is worth its key (D-46).
- The same run later serves as a dry run (`--dry-run`) before a real run.

*Verify:* offline, on recorded source responses, the report counts match the fixtures; live, it completes for all active teachers within the sources' limits.
---

## 4. The style

**STY-01 · Halftone** *fixed* · B2
- A one-colour halftone of the photo: round white dots on a 45° grid.
- About 110 dots across the square. *Measured* (prototype, recipe 0.1.0): `dots_across` = side ÷ dot-cell pitch along the 45° grid = 110 (the owner's Fillmore 109, Holmes 111).
- Dot size follows tone. Dark tones are left transparent, so the page's colour shows through as the shadows.
- Contrast is lifted a little, so the face reads in dots. *Prototype rule:* levels from the face's own tones (white point at the face's p98, shadows dropping out well above black), then a gamma and a light unsharp mask. The numbers are in `prototype/README.md`.

*Verify:* a synthetic-gradient test checks the dot pitch and the 45° angle by frequency analysis, and that dots grow with brightness.

**STY-02 · Outline** *fixed* · B2; bottom edge *proposed* · C
- One thin, smooth white line just outside the head and shoulders, following the hair's overall shape rather than single strands.
- Where the shoulders run off the bottom of the square, the line runs off with them. It doesn't trace along the bottom edge.
- *Measured* (prototype): 6 px wide, 2 px outside a smoothed silhouette, on the 1,000 px master. The dots are clipped to the same silhouette. The head is smoothed gently (hair keeps its overall shape) and the shoulders harder.

*Verify:* on fixtures, the line is one connected piece, its width stays within settings, and it sits a set distance outside the figure.

**STY-03 · Crop** *fixed* · B2
- A square, head and shoulders, with the head near the top.
- The face fills most of the width, and the shoulders run off the bottom.
- No background at all.

The geometry settings come from the style prototype. *Measured* (recipe 0.1.0): eye-to-mouth distance 0.237 of the side, eye line at 0.443 of the height, face centred.
*Verify:* on fixtures, the eye line, eye-to-mouth distance and face centre fall inside the setting ranges.

**STY-04 · The likeness stays the photo's own** *fixed* · B2, amended by D-18
- The dots are always made by code.
- They're made from the tones of the original, blended with an aligned, AI-enhanced copy that contributes at most `enhance_blend` (0.5) of the tones (PIP-13). The owner chose this because many originals are poor and the halftone loses more detail; the copy adds detail back while staying close to the original.
- No image model ever draws the dots. No AI image reaches the portrait except through that aligned, recorded blend.
- The likeness is always checked against the original (PIP-09).
- An image model, if used for the outline (PIP-07, trial contenders only), draws only the line, which code extracts.

*Verify:* by construction. The halftone function's only input is the cropped (and, if used, blended) tone image. A test checks that no model output reaches the dot layer except through the PIP-13 blend, at the set share.

**STY-05 · One recipe for every teacher** *fixed* · B2
- One set of settings applies to every teacher.
- Each portrait records `recipe_version` and the full `settings` it was made with.
- Changing any recipe setting requires a new `recipe_version`.

*Verify:* a config test fails if the recipe settings' hash changes without a version change.

**STY-06 · The master file** *fixed* · B2; exact test *proposed* · C
The master is a 1,000 × 1,000 PNG with an alpha channel:

- every pixel with any opacity is pure white (255, 255, 255), and the shape is carried by alpha alone;
- the corners and everything outside the figure and line are fully transparent.

*Verify:* a checker function, run on every master in every test and inside the tool before delivery.

**STY-07 · The target** *fixed* · B2, D-16; numbers *proposed* (recipe 0.1.0, waiting for the owner's look)
The owner's three hand-made portraits are the target.

- The recipe's starting numbers were set by matching them in Phase 0 (D-16). See `prototype/README.md` and `prototype/out/board.png`.
- The harness builds the real modules to reproduce `prototype/out/` from `prototype/fixtures/` (F-16).

**STY-08 · The black-and-white version** *fixed* · D-26, D-39; exact test *proposed* · C
Made by code from the same layers as the master (STY-06), with nothing new to tune:

- inside the figure: white where the master has dots, black everywhere else;
- the master's gap and line are drawn **black** (option C, `bw_edge = "black"`), so the figure sits on an 8 px black margin;
- transparent outside the line's outer edge, so its footprint is exactly the master's;
- 1,000 × 1,000 PNG, 8-bit RGBA, the same crop as the master.

*Verify:* `check_bw` (prototype `recipe.py`):
- every visible pixel is grey (R = G = B), black or white except where edges are smoothed;
- the top corners are transparent;
- it is opaque everywhere the master shows.

**STY-09 · Small copies** *fixed* · D-39; method *proposed* · C
- The master and the black-and-white version each also come at 500 × 500 px (`small_px`).
- They are scaled down from the 1,000 px files by area averaging with premultiplied alpha, so the edges stay clean.

*Verify:* the master's checker (STY-06) and `check_bw` pass at 500 px.

---

## 5. The pipeline, per teacher

**PIP-01 · Choose** *fixed* · B2
Take the best candidate that hasn't been set aside (SRC-07).

**PIP-02 · Pre-check the original before spending more** *fixed* · B2; output *proposed* · C
- A vision model confirms all of these:
  - exactly one person;
  - the face fully in view;
  - the face large enough: a face-box width of at least `min_face_px` = 90 source pixels. The owner's own originals measure 108–183 px;
  - not badly damaged.
- It returns a structured verdict: pass or fail, reasons, an approximate face box, whether the original is a photograph or another medium (Q-11), and any caption or facsimile signature as written, with the person it names (recorded; a caption naming someone else fails the pre-check).
- A failing original is set aside with its reason. Nothing else is spent on it.

*Verify:* stubbed model responses drive the pass and fail paths. Live behaviour is judged in the trial.

**PIP-03 · Cut-out** *fixed* · B2, D-19 (through OpenRouter, one key); method *proposed* · C
- OpenRouter has no dedicated background-removal model (checked 2026-10-19), so an image-editing model does it:
  - **By default, the cut-out comes from the enhanced copy (PIP-13).** That call returns the person on a flat pure-green background, and code reads the mask from the green (`key_mask`). One call gives both the copy and its cut-out, and they line up by construction.
  - **Fallback:** if that mask fails a simple sanity check (figure share of the frame out of range, or more than one large piece), a separate "background to green, change nothing else" call is made on the same model (`cutout_keyed` prompt).
  - A free local model (no key, no cost) is an optional trial contender only.
- The owner's own method used an AI tool for the background, and it did better than the prototype's free stand-in, which struggled with a dark suit against a dark background (2026-10-19).
- The cut-out is kept in the state store and reused for every later try on the same original.

*Verify:* a stub test proves the second try doesn't call the model again.

**PIP-04 · Crop, by code** *fixed* · B2; method *proposed* · C
Code crops to STY-03 with a similarity transform from five face landmarks (eyes, nose, mouth corners):

- Scale comes from the eye-to-mouth distance, which holds steady when the head turns. The eye line sits at a set height, and the face box is centred.
- The landmarks come from a local face detector. YuNet is proposed; it is permissively licensed and gives a box plus five landmarks.
- If the detector finds no face, as can happen with engravings, the pre-check's box is used and the eye line is estimated from it.

*Verify:* synthetic and fixture images.

**PIP-05 · Descreen, by code** *fixed* · B2, D-17; method *proposed* (prototype, recipe 0.2.0)
- It runs on the original, before cropping, because a print screen's spacing is defined in the original's pixels.
- Code detects a printed dot pattern by frequency analysis and notch-filters its peaks, plus their first harmonics. A screen counts when compact spectral peaks stand well above their surroundings in at least two directions.
- **Every original gets an edge-preserving blur** (bilateral) before the halftone (D-17). It is stronger when a screen was found. Its size is set in dot cells and converted to original pixels, so it suits any original size.
- Contrast is restored by the tone step (STY-01), whose levels come from the face's own tones.
- What was found and what was applied are recorded with the attempt.

*Verify:* the owner's Fillmore and Cady originals (book prints) are detected as screened and Holmes is not (prototype result). A synthetic screened image has its peaks reduced by a set factor. A clean image gets only the mild blur.

**PIP-06 · Halftone, by code** *fixed* · B2
The halftone is made straight onto transparency, to STY-01.
*Verify:* STY-01 and STY-06 checks.

**PIP-07 · Outline** *fixed* · B2 for the image-model method; *proposed* · C (Q-05) for the code method
The method is a setting.

- **Image model** (starting setting Gemini 3 Pro Image; challengers GPT Image 2 and FLUX.2 Pro):
  1. The model gets the cut-out on black and draws one white contour around it.
  2. Code keeps only the line: threshold, keep the main connected stroke, re-stroke it at the set width.
  3. Code aligns the line to the figure, because image models can shift or rescale what they redraw.
- **Code** *(proposed)*:
  1. Code widens the cut-out mask by the set offset.
  2. It smooths the mask so the line follows the hair's overall shape.
  3. It traces the edge and strokes it at the set width.

  This is deterministic and free.

*Verify:* the code method is tested on fixtures. For the model method, extraction and alignment are tested on synthetic "model output" images that are shifted and scaled.

**PIP-08 · Composite** *fixed* · B2
Code lays the line over the dots and writes the master (STY-06).

**PIP-09 · Check the draft** *fixed* · B2; output *proposed* · C
- A vision model checks the draft. Its family must differ from the image models used on the draft: the enhance model and, for trial contenders, the outline model. The family rule is checked when settings load. A Claude model via OpenRouter satisfies it against Google, OpenAI and other image models.
- The criteria are:
  - the outline hugs the figure;
  - the cut-out is clean;
  - no moiré;
  - the face reads and matches the original;
  - the crop matches the examples.
- The model sees the draft on the library's page colour, the original and the three examples.
- It returns, for each criterion, pass or fail with a 1–5 score, plus short notes. A draft passes only when every criterion passes.
- The notes go into the manifest record.

*Verify:* stubbed responses. Live behaviour is judged in the trial.

**PIP-10 · Remaking a failed draft** *fixed* · B2; semantics *proposed* · C (Q-06)
- A failing draft is remade.
- A remake re-runs only the steps that can come out differently: the image-model outline, or the cut-out with a different provider if configured. It never re-asks the checker about the same draft.
- When the failing criterion is one that code would only repeat, the original is set aside after that failure instead of being remade. Those criteria are likeness, damage, moiré, crop, and any criterion under the code outline.

*Verify:* failure-policy scenario tests (F-23).

**PIP-11 · Failure policy** *fixed* · B2; counting *proposed* · C (Q-07)
- Two failed drafts set an original aside.
- A turn-down from the library (`status.json`) sets that original aside at once. *Amended by D-40:* it sets aside every copy of that photograph, and a clearly better copy may come back once (PIP-17).
- At most three originals per teacher reach drafting in one run. After that, the teacher keeps the library's blank portrait for now.
- Originals failed by the pre-check (PIP-02) don't count toward the three. There is a separate cap per teacher per run on pre-checks; the proposed starting value is 8.
- On a later run, the tool tries the teacher again only if new candidates exist.

*Verify:* scenario tests (F-23).

**PIP-12 · Set-asides are remembered** *proposed* · C
- Every set-aside (original, reason, date, run) persists in the state store across runs.
- A set-aside original is never tried again, unless the owner pastes its link in a `try_link` request.
- Set-asides are listed in the manifest record's set-aside field, as the schema allows, and in the report.

*Verify:* a two-run fixture.

**PIP-13 · Blend in an AI-enhanced copy** *fixed* · D-18 (the owner's method, with the safeguards below); details *proposed* · C
The owner's own portraits were made this way: an AI tool made a subtly enhanced copy of the portrait, the copy was laid over the original scan at about 50%, and only then was the halftone made. The proposal:
- After descreening (PIP-05), an image model makes a subtly enhanced copy of the original, through OpenRouter (D-19). The prompt is `prototype/prompts/enhance_keyed.md`: clean up and clarify, keep the face and framing exactly, black and white, background flat pure green.
- Starting model: `google/gemini-3-pro-image` (Nano Banana Pro). Challengers: `google/gemini-3.1-flash-image` (Nano Banana 2, cheaper) and `openai/gpt-image-2`. The trial decides (TRI-04). Model ids were checked on OpenRouter on 2026-10-19 and are confirmed again by `doctor`.
- Code **aligns** the copy to the original before blending, because image models often shift or rescale what they redraw. Without alignment, the blend shows double edges.
  - If the alignment is poor (below a set correlation), the copy is discarded and the original is used alone. This is recorded.
  - **Local drift check.** The overall alignment can't undo a local change, such as an eye or the mouth moved slightly. So after aligning, code measures (by dense optical flow) how far details inside the face still sit apart. If the 95th percentile exceeds `enhance_max_drift_cells` (0.7 of a dot cell), the copy is discarded.
    - Prototype: good copies measure 0.32–0.46 cells.
    - Copies with the eyes and mouth moved by about 1.2 cells measure 0.90–1.09 and are refused.
- The copy gets the same edge-preserving blur as the original (PIP-05, D-23), in the frame, so its own fine texture can't clash with the dots.
- Code blends the aligned copy with the original at `enhance_blend` (0.5), **in the portrait's own frame** (after cropping), so the copy's extra resolution survives. It is usually 2–4× the original's size. The dots are still made by code from the blended tones.
- The draft check's "face matches the original" criterion (PIP-09) compares against the **original**, not the enhanced copy.
- The copy is cached per original, and its model, prompt version, blend share and alignment score are recorded with the attempt.
- Cost: one image-model call per original, not per attempt.

*Verify:* synthetic keyed copies (2.8× the size, sharpened, rescaled by 2%, shifted, with a green background) are aligned (correlation ≥ 0.99 in the prototype) and blended without double edges (edge agreement 0.98–1.00). Their keyed cut-out matches the stand-in's (overlap 0.94–0.99). A copy that can't be aligned is refused. The second try on an original makes no new call.

**PIP-14 · Up to three portraits per teacher** *fixed* · D-25, D-40; setting *proposed* · C
- A teacher has at most `max_portraits_per_teacher` (3) portraits: approved, waiting in the library's queue, or being made.
- Portraits turned down by the library don't count; their slot is filled from the next candidate.

*Verify:* scenario test: a teacher with 5 different photographs gets 3 portraits; a turn-down frees a slot for the 4th.

**PIP-15 · Different photographs, not copies** *fixed* · D-40; method *open* (T-16)
- Each portrait is a **different photograph**: another sitting, age or pose.
- Other scans, crops, retouches or prints of the same photograph are **copies** of it. They are grouped with it by the visual check (T-16).
- Of each group, only the **best copy** is used. It is chosen in SRC-07's order: licence tier, then size, then the pre-check's damage rating.
- The other copies are kept in the rights log (SRC-12) as copies of that portrait, with their links, so a better copy is recognised later.

*Verify:* fixtures of the same photograph (cropped, rescanned, retouched) group together; two sittings of one teacher don't.

**PIP-16 · Choosing which three** *fixed* · D-40; spread *proposed* · C (uses T-04)
When more different photographs pass the pre-check than there are free slots:

1. The teacher's **best-known image** comes first: Wikidata's main image (P18), or a copy of it, if it passes.
2. Then the best-quality photographs, **spread across the teacher's life**, using the approximate age or date (T-04).

*Verify:* unit test on fixture candidates: P18 kept; of two similar-quality photographs from the same years and one from another decade, the other decade's is chosen.

**PIP-17 · Later runs: better copies and turn-downs** *fixed* · D-40; details *proposed* · C
- **A clearly better copy of an approved portrait** is offered as a new draft, marked as a better copy of that portrait. The approved portrait stays until the library swaps them, and the library reports the swap back (D-38).
- *Proposed:* a clearly better copy of a portrait still waiting in the queue replaces the waiting draft (OUT-07).
- *Proposed:* when all slots are filled, a new photograph that ranks above one of them (PIP-16) is offered as a draft to replace it. The library decides.
- **A turned-down photograph** (every copy of it) is set aside. It may come back **only as a clearly better copy**, offered once.
  - *Proposed:* never if the library's reason is "not this teacher" or "don't use this photograph". The reason comes with the turn-down (T-08).
- *Proposed:* **clearly better** means one of:
  - a face at least 1.5× larger in pixels, with no lower licence tier;
  - the same size, with the pre-check rating it clearly less damaged.

  The threshold is tuned at T-16.

*Verify:* scenario tests: better copy of an approved portrait → marked draft, approved one untouched; turned down for quality → a 2× copy offered once; turned down as "not this teacher" → never again.

**PIP-18 · Approximate date, and the library's corrections** *fixed* · D-41; method *proposed* · C
- There is no category scheme (D-41). Each portrait records an approximate date, for the spread in PIP-16:
  - the source's own date, exact or circa, when it has one;
  - otherwise the pre-check's age estimate (PIP-02) added to the teacher's birth year, marked as estimated;
  - otherwise unknown. Unknown dates don't block choosing; they rank after dated ones in the spread.
- Life stage (early, middle or late, by thirds of the teacher's adult life) is worked out from the date when needed. It isn't stored.
- **The library can correct** the date and the best-known flag through the API. A correction replaces the tool's value and is never overwritten by a later run.

*Verify:* unit tests: a source date wins over an estimate; an estimate uses the birth year; a library correction survives a re-run.

---

## 6. Output and delivery

**OUT-01 · Delivery folder layout** *withdrawn* (2026-10-19, D-31, D-42: files live in the tool's bucket and the library pulls through the API; storage is OUT-12) · B2
The layout is in [../contracts/delivery-folder.md](../contracts/delivery-folder.md):

- `portraits/runs/<run-id>/` holds `manifest.json`, `masters/<teacher_id>.png`, `originals/<teacher_id>.jpg` and `report.md`;
- `requests.json` and `status.json` sit at the folder's root.

*Verify:* the receiver stub (F-05) accepts the run.

**OUT-02 · Manifest** *fixed* · B2
`manifest.json` follows `portraits.manifest.schema.json` unchanged (copied from Rev1, pending O-1). It holds one record per portrait delivered in the run:

- the teacher: `person_id` is the `teacher_id`, plus `name`, `born` and `died`, so the record stands on its own;
- the master's file name and SHA-256;
- the original's source, link, title, creator, date, licence, licence link, credit and how it was matched;
- the attempt number;
- the check's notes;
- any originals set aside, with reasons;
- `request_id`, when the draft answers a request.

The run's `tool_run` block records the run id, start time, tool version and the settings used.
*Verify:* schema validation in every run, by the tool and the stub.

**OUT-03 · Write order and atomic updates** *proposed* · C
- For each portrait, the tool writes the original's copy and the master first. Only then does it add the record to `manifest.json`.
- The manifest is rewritten after each record: write a temporary file, then rename it. A stopped run therefore still delivers every finished portrait, and the library never sees a record whose files aren't there yet.
- With a synced folder, files can arrive out of order. The library's Drive door should wait rather than fail when a record's file hasn't arrived (a note for Rev1).

*Verify:* kill the run mid-way in a test; the folder holds a valid manifest whose files all exist.

**OUT-04 · Bad records are never written** *fixed* · B2
- A record whose teacher isn't on the list, whose licence is missing, or that fails the schema is not written.
- The validator names the failing field, and the report names the record.

*Verify:* fixture with a record missing its licence, refused with the field named (AC-02).

**OUT-05 · Originals copy for comparison** *fixed* · B2, amended by D-39
- The original is kept exactly as downloaded (OUT-11).
- Its viewing copy is a **PNG**, which keeps any transparency the original has. It is at most 1,600 px on the long side and never enlarged.
- It is for the admin page and previews.

*Verify:* unit test: a large fixture comes out at 1,600 px and a small one keeps its size; a fixture with transparency keeps it.

**OUT-06 · Run report** *fixed* · B2; contents *proposed* · C
`report.md` says, in plain words:

- what was done;
- what was spent, in total and per teacher;
- what was set aside, and why;
- which teachers were skipped, and why (no candidates, wrong Wikidata id, no id or years, approved, waiting);
- which requests were handled;
- which rows or records were refused;
- any Wikidata ids the tool resolved, for the owner to add to the list;
- errors;
- whether the run stopped at the cap.

*Verify:* a snapshot test of the report from the fixture run.

**OUT-07 · Re-delivery** *fixed* · B2
A later run's draft for a teacher replaces the draft that teacher has waiting; the library handles this by `teacher_id`. The tool never deletes or edits earlier runs' files.

**OUT-08 · Bulk-upload zip on request** *fixed* · B2; location *proposed* · C · *under review at T-09:* with the library pulling through the API (D-37, D-42) this may no longer be needed; the owner confirms there.
`portraits zip <run-id>` writes the run's masters plus `manifest.json` into one zip, for the library admin's Imports page. It is written to a local path, not into the delivery folder, so the library's Drive door never picks it up.
*Verify:* the stub accepts the unzipped contents.

**OUT-09 · Delivery target** *withdrawn* (2026-10-19, D-31, D-42: no Drive folder; Q-03 superseded)
- B2 gives a Drive folder id and a Drive credential.
- The proposal is a local folder path that Google Drive for desktop syncs. That means no credential and no Drive code, and works on any machine with Drive for desktop. The Drive API becomes a later option, behind the same interface.

**OUT-10 · Sample run for the library** *fixed* · B2
- The repo keeps a small sample run (fixtures: a few masters, originals, `manifest.json` and `report.md`) that validates against the schema.
- Library-AI's acceptance check of the hand-off is to import this sample unchanged.

*Verify:* the stub accepts it, and the schema validates it.

**OUT-11 · The files of a portrait** *fixed* · D-26, D-39; names *proposed* · C (layout confirmed at T-06)
Each portrait has an id, `<teacher_id>-<n>` (for example `charles-fillmore-1`). `n` counts up in the order portraits are found and is never reused. The portrait's files are:

| File | What | Offered to the library |
|---|---|---|
| `original.<ext>` | The original, byte for byte as downloaded; SHA-256 in the rights log (SRC-12) | yes |
| `original-view.png` | Viewing copy (OUT-05) | yes |
| `white-1000.png`, `white-500.png` | The master (STY-06) and its small copy (STY-09) | yes |
| `bw-1000.png`, `bw-500.png` | The black-and-white version (STY-08) and its small copy | yes |
| `enhanced.png` | The AI-enhanced copy (PIP-13), as the model returned it, with its alignment and drift scores in the record. Kept even when the safeguards refused it, marked as not used, with the reason | yes (D-39) |
| `mask.png` | The cut-out mask: 8-bit grey, white is the person, at the original's size and position | yes (D-39) |

- Download names for people: `Charles Fillmore - portrait 1 - white 1000.png`.
- The licence and credit of each file are T-13; the API paths are T-08.

*Verify:* the fixture run produces all eight files per portrait, and each passes its own check.

**OUT-12 · Storage** *fixed* · D-42; layout *proposed* · C
- Files live in the tool's own storage bucket (Railway, S3-compatible), one bucket per environment. There is no Drive copy.
- Layout: `portraits/<teacher_id>/<portrait_id>/` holds the files of OUT-11 and a `record.json`.
  - The database is the source of truth.
  - `record.json` is rewritten from it whenever the portrait changes, so the bucket alone describes every portrait.
- **History is kept.** A replaced or turned-down portrait keeps its files, marked with its status. Nothing is deleted automatically.
- **Candidates that never become a portrait are logged, not stored:** the rights log (SRC-12) keeps the link, credit and SHA-256.
- **The library keeps its own copy** of every portrait it pulls (D-42). The API therefore lists changes since a date, with each file's SHA-256 (T-08).
- **Backups:** the database only, at first (Railway's Postgres backups). The bucket isn't copied elsewhere. Everything in it can be rebuilt from the rights log and the recipe, except the AI copies, which would be made again at cost.

*Verify:* fixture run: the layout and `record.json` match the database; a turned-down portrait's files are still there; a failed candidate has a rights-log entry and no files.

**OUT-13 · Admin page** *fixed* · D-33, D-42; contents *proposed* · C
- A read-only admin page behind a login (T-21). It works on a phone.
- **Teachers:** each teacher's portraits, with all versions, the credit and rights record, and the library's decisions (waiting, approved, turned down, main portrait, replaced).
- **Runs:** what each run did, spend, errors, and the candidates set aside, with reasons.
- No approvals here: they happen in the library (D-38).

*Verify:* a smoke test against the deployed app opens the teacher list, one teacher and the run list, and finds no form that changes data.

**OUT-14 · The library API** *fixed* · D-28, D-37, D-44; details *proposed* · C
- The tool serves the API in [../contracts/portraits-api.openapi.json](../contracts/portraits-api.openapi.json), explained in plain words in [../contracts/portraits-api.md](../contracts/portraits-api.md). The library adopts it.
- **One library key**, for reading and sending, stored only as a hash. It can be switched off or replaced without a deploy.
- **Pull only:** the library reads `/api/v1/changes` on its own schedule. The tool never calls the library.
- **Decisions and requests** come in through `POST /api/v1/decisions` and `POST /api/v1/requests`. Resending one is safe. Requests are queued for the worker at once.
- **Files** are served through short-lived signed links, with each file's SHA-256 in the portrait record.
- Within v1, changes are additive only.

*Verify:*
- `check_api.py` passes on the contract and its samples;
- contract tests run each route against the samples;
- a smoke test on the deployed app gets 401 without the key and 200 with it (HT-20).

---

## 7. Running, state and spend

**RUN-01 · Where it runs** *fixed* · B2
It runs as a command-line tool on the owner's PC (WSL Ubuntu), or on any machine with its keys and settings.

**RUN-02 · What a run does, in order** *fixed* · B2; waiting drafts *proposed* · C (Q-02)
A run works in this order:

1. Requests, first.
2. Teachers without an approved portrait.

It skips:

- approved teachers;
- teachers with a draft already waiting (from `status.json` if present, otherwise from the tool's own delivery record), unless a request names them;
- teachers already given up on, unless new candidates exist.

Teachers are processed one at a time.
*Verify:* run fixtures (F-25, F-26).

**RUN-03 · Resumable without paying twice** *fixed* · B2
- Each teacher is a job in the tool's own queue.
- Every paid step's result is cached. The cache key is the original's SHA-256, the step, the model and a hash of the relevant settings.
- A run stopped part-way and started again resumes without repeating any paid call.

*Verify:* kill-and-resume test with stubbed models counts calls.

**RUN-04 · Spend cap and ledger** *fixed* · B2; method *proposed* · C
- The tool uses its own OpenRouter key. That is the only AI key (D-19).
- The cap per run comes from settings: $250 for the first run.
- Before each paid call, the client checks that the spend so far plus that call's estimated maximum fits under the cap. If it doesn't, the run stops cleanly, delivers what's finished and says so in the report.
- The actual cost of every call is logged per attempt, from the provider's usage data where given, otherwise from the estimate in settings, and totalled in the report.

*Verify:* stubbed costs cross the cap mid-run; no call is made past it, and the report says so.

**RUN-05 · Commands** *proposed* · C
The tool has these commands:

- `doctor`: checks settings, keys, models, folder and list; spends nothing or next to nothing.
- `teachers check`: validates the list.
- `run`: options `--limit N`, `--teacher ID` and `--dry-run`. A dry run shows the plan and the estimated spend, and spends nothing.
- `trial`
- `validate <manifest>`
- `zip <run-id>`
- `status`: what's in the queue, set aside or delivered.

*Verify:* each command has at least one test.

**RUN-06 · Offline mode for tests** *proposed* · C
- Every network and model call goes through clients that can be swapped for fixtures and stubs.
- The whole suite runs with no keys and no network.

*Verify:* the CI or harness test command runs with networking disabled.

**RUN-07 · Logs** *proposed* · C
Each run writes a detailed log to the state directory. It stays local and is never delivered, and it holds no keys (IN-11).

---

## 8. The trial

**TRI-01 · Before the first full run, inside it** *fixed* · B2
The trial runs first. The first full run then uses its defaults. Nothing waits for the owner.

**TRI-02 · The trial set** *fixed* · B2; curation *proposed* · C
The set is:

- the owner's three originals (whose targets are the hand-made portraits). These are test inputs only and are never delivered (D-13);
- about 20 originals found by the match rules, including:
  - scanned prints with a dot pattern;
  - a tiny original;
  - a group photo;
  - an engraving;
  - a damaged print.

*Proposed:* the set is curated during planning into a fixture file listing each item and its expected outcome, for example "group photo: refused at pre-check". That way the trial doubles as a test.

**TRI-03 · Contenders** *fixed* · B2; fourth contender *proposed* · C (Q-05)
The three outline models each run with the same cut-out and the same code. The proposal adds the code-drawn outline as a fourth contender.

**TRI-04 · Choosing the winner** *fixed* · B2; "close" *open (Q-19)*
The check (PIP-09) scores every result, and the best contender wins. If two are close, the cheaper one wins. The proposal for "close" is a total score within 5% of the best.

**TRI-05 · The board** *fixed* · B2; format *proposed* · C
- A board shows every result beside its original and the examples, with scores and cost per contender.
- It goes to the owner for a veto: as `board.pdf`, readable on a phone through Drive, and as `board.html`, in `portraits/trial/<run-id>/`.
- That folder is outside `runs/`, so the library never imports trial drafts.

**TRI-06 · Defaults come from the trial** *fixed* · B2; mechanism *proposed* · C
- The trial writes its winner to settings, with a new `recipe_version`, and commits it, through the harness, with a note in the digest.
- The owner's veto reverses it.
- The full run then reuses every cached paid step from the trial.

**TRI-07 · Trial spend** *fixed* · B2; sub-cap *proposed* · C
The estimate is about $30, inside the first run's cap. *Proposed:* a trial sub-cap of $40, so the trial can't eat the run.

**TRI-08 · The examples are reproduced** *fixed* · B2; metrics *proposed* · C
- The pipeline's output for the owner's three originals passes the check when compared against the hand-made targets, in the check's "compare with target" mode.
- *Proposed:* simple code measures sit alongside the check. At the owner's framing, compared at 500 px, they need: figure overlap ≥ 0.85, mean tone error ≤ 0.08, dots across 110 ± 2, and no STY-06 problems. The prototype scores 0.88–0.97, 0.053–0.071 and 110.5.

---

## 9. Project acceptance ("done when", from B2)

| ID | Done when | Checked by |
|---|---|---|
| AC-01 | The owner's `teachers.csv` loads, and a row with a bad slug or an impossible date is refused with the row named | F-02 tests, plus `teachers check` on the owner's list |
| AC-02 | A run writes a complete `runs/<run-id>/` to the delivery folder, and its `manifest.json` validates against the schema (Rev1's `validate.py` or the same check in the tool). A record with no licence is refused, naming the field | F-03, F-24, F-26 |
| AC-03 | The receiver stub accepts the run, and fixtures of `requests.json` and `status.json` change what the next run does: a request is handled first, an approved teacher is skipped, a turned-down original is set aside | F-05, F-26 |
| AC-04 | The owner's three examples are reproduced closely enough that the check passes them against the hand-made targets | F-29 (TRI-08) |
| AC-05 | The trial's board exists, the defaults are set from it, and one full harness run (plan, build, tests, digest, veto) has completed on this project | F-28, plus the harness's own record |
| AC-06 | Nothing in the tool reads the library's reference shelf or scans. Originals come only from the adopted sources (two in the brief; widened by D-21, see `sources.md`), by the match rules of SRC-03 | SRC-01 test, SRC-03 fixtures |

---

## 10. PORT reconciliation table (to fill in once O-1 arrives)

| PORT line | Summary | Requirement(s) here | Difference / question |
|---|---|---|---|
| PORT-001 … 022 | | | |
| PORT-040 | | | |
| PORT-070 … 081 | | | |
| PORT-091 | | | |
| PORT-090 (hand-off; library side) | | OUT-01, OUT-02, OUT-10 | |
