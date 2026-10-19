# Requirements: Nexus Portraits

This file is normative. "Must" is required; "should" is the default unless a good reason is recorded. Every requirement has:

- **an ID**, which is permanent;
- **a status**: *fixed*, *proposed*, or *open (Q-nn)*;
- **an origin**: B2 = current brief, B1 = first brief, C = Claude's review, D-nn = a decision;
- **Verify**: how a machine (or, rarely, the owner) confirms it.

Conventions are in [../README.md](../README.md).

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

**IN-01 · Teacher list** *fixed* · B2
The tool reads `teachers.csv`: UTF-8, with a header row, one row per teacher. The columns are `teacher_id`, `name`, `born`, `died`, `wikidata_qid`, `aliases` and `notes`, as defined in [../contracts/teachers-csv.md](../contracts/teachers-csv.md).
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

**IN-07 · Status** *fixed* · B2; format *proposed* · C
When `status.json` is present, the tool reads it:

- **Approved** teachers are skipped.
- A **turned-down** original is set aside at once (PIP-11).
- **Waiting** teachers are handled as in RUN-02.

When the file is absent, nothing counts as approved.
*Verify:* run fixtures (F-26).

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

**IN-11 · Keys live outside the repo** *fixed* · B2
- The OpenRouter key, the fal key if needed and any Drive credential are read only from environment variables, or from a keys file outside the repo.
- They are never written to logs, reports, the state store or the delivery folder.

*Verify:* a test scans every file a stubbed run writes and finds no key value.

---

## 3. Sources, rights and matching

**SRC-01 · Two sources, enforced in code** *fixed* · B2; enforcement *proposed* · C
- Originals come only from Wikimedia Commons, through Wikidata for rule 1, and from the Library of Congress's Prints and Photographs collections.
- The tool's source client may contact only the Wikidata, Wikimedia Commons, Wikimedia upload and loc.gov hosts.
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

**SRC-03 · Certain matches only, in order** *fixed* · B2
A file counts as showing the teacher only by one of these rules, tried in this order:

1. The image on the teacher's Wikidata item (property P18).
2. Commons files whose structured data says they depict the teacher's Wikidata item (property P180).
3. Library of Congress Prints and Photographs records that name the teacher with matching dates (SRC-05).

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

**SRC-09 · Polite access** *proposed* · C
- Every request to Wikimedia and loc.gov carries a descriptive User-Agent with the contact line from settings.
- Requests are rate-limited, retried with backoff on 429 and 5xx responses, and cached on disk so a resumed run doesn't fetch twice.

*Verify:* unit test of the client's headers and retry behaviour.

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

**STY-04 · The likeness is the photo's own** *fixed* · B2
- The dots are made by code from the photo's tones.
- No image model ever produces or alters the dots or the face.
- An image model, if one is used (PIP-07), draws only the outline line, which code extracts and lays over the dots.

*Verify:* by construction. The halftone function's only input is the cropped photo, and a test checks that the model output never reaches the dot layer.

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
- It returns a structured verdict: pass or fail, reasons, an approximate face box, and whether the original is a photograph or another medium (Q-11).
- A failing original is set aside with its reason. Nothing else is spent on it.

*Verify:* stubbed model responses drive the pass and fail paths. Live behaviour is judged in the trial.

**PIP-03 · Cut-out** *fixed* · B2; provider *open (Q-18)*
- A background-removal model makes the cut-out: Bria RMBG 2.0 or the like, with a direct fal key if OpenRouter has none.
- The cut-out is kept in the state store and reused for every later try on the same original.

*Verify:* a stub test proves the second try doesn't call the model again.

**PIP-04 · Crop, by code** *fixed* · B2; method *proposed* · C
Code crops to STY-03 with a similarity transform from five face landmarks (eyes, nose, mouth corners):

- Scale comes from the eye-to-mouth distance, which holds steady when the head turns. The eye line sits at a set height, and the face box is centred.
- The landmarks come from a local face detector. YuNet is proposed; it is permissively licensed and gives a box plus five landmarks.
- If the detector finds no face, as can happen with engravings, the pre-check's box is used and the eye line is estimated from it.

*Verify:* synthetic and fixture images.

**PIP-05 · Descreen, by code** *fixed* · B2
- Code detects a printed dot pattern by frequency analysis, notch-filters its peaks, applies an edge-preserving blur and restores contrast.
- This is skipped when no pattern is found.
- Whether it was applied is recorded.

*Verify:* a synthetic screened image is detected and cleaned (its peaks are reduced by a set factor). A clean image is left untouched.

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
- A vision model of a different family from the outline model checks the draft. The family rule is checked when settings load; with the code outline, any family may check.
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
- A turn-down from the library (`status.json`) sets that original aside at once.
- At most three originals per teacher reach drafting in one run. After that, the teacher keeps the library's blank portrait for now.
- Originals failed by the pre-check (PIP-02) don't count toward the three. There is a separate cap per teacher per run on pre-checks; the proposed starting value is 8.
- On a later run, the tool tries the teacher again only if new candidates exist.

*Verify:* scenario tests (F-23).

**PIP-12 · Set-asides are remembered** *proposed* · C
- Every set-aside (original, reason, date, run) persists in the state store across runs.
- A set-aside original is never tried again, unless the owner pastes its link in a `try_link` request.
- Set-asides are listed in the manifest record's set-aside field, as the schema allows, and in the report.

*Verify:* a two-run fixture.

---

## 6. Output and delivery

**OUT-01 · Delivery folder layout** *fixed* · B2
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

**OUT-05 · Originals copy for comparison** *fixed* · B2
Each delivered original is downsized to at most 1,600 px on the long side. It is for the admin's comparison only.
*Verify:* unit test.

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

**OUT-08 · Bulk-upload zip on request** *fixed* · B2; location *proposed* · C
`portraits zip <run-id>` writes the run's masters plus `manifest.json` into one zip, for the library admin's Imports page. It is written to a local path, not into the delivery folder, so the library's Drive door never picks it up.
*Verify:* the stub accepts the unzipped contents.

**OUT-09 · Delivery target** *open (Q-03)*
- B2 gives a Drive folder id and a Drive credential.
- The proposal is a local folder path that Google Drive for desktop syncs. That means no credential and no Drive code, and works on any machine with Drive for desktop. The Drive API becomes a later option, behind the same interface.

**OUT-10 · Sample run for the library** *fixed* · B2
- The repo keeps a small sample run (fixtures: a few masters, originals, `manifest.json` and `report.md`) that validates against the schema.
- Library-AI's acceptance check of the hand-off is to import this sample unchanged.

*Verify:* the stub accepts it, and the schema validates it.

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
- The tool uses its own OpenRouter key, and its own fal key if needed.
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
| AC-06 | Nothing in the tool reads the library's reference shelf or scans. Originals come only from the two sources, by the three match rules | SRC-01 test, SRC-03 fixtures |

---

## 10. PORT reconciliation table (to fill in once O-1 arrives)

| PORT line | Summary | Requirement(s) here | Difference / question |
|---|---|---|---|
| PORT-001 … 022 | | | |
| PORT-040 | | | |
| PORT-070 … 081 | | | |
| PORT-091 | | | |
| PORT-090 (hand-off; library side) | | OUT-01, OUT-02, OUT-10 | |
