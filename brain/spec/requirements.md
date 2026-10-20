# Requirements: Nexus Portraits

This file is normative. "Must" is required; "should" is the default unless a good reason is recorded. Every requirement has:

- **an ID**, which is permanent;
- **a status:** *fixed* (the owner's), *proposed* (Claude's, open to review), *open (Q-nn)* or *withdrawn*;
- **an origin:** B2 = the current brief, B1 = the first brief, C = Claude, D-nn = a decision in [../decisions.md](../decisions.md);
- **Verify:** how a machine, or rarely the owner, confirms it. `F-nn` names the feature card that builds the check ([../plan/features.md](../plan/features.md)).

Conventions are in [../README.md](../README.md).

> **Consolidated 2026-10-20** after tracker topics T-01..T-23 (D-31..D-57). Each requirement now states what is to be built, and its origin names the decisions behind it. The history of each change is in [../decisions.md](../decisions.md) and in git.
>
> **The owner settled the two questions of the consistency pass on 2026-10-20:**
> - D-58 (Q-27): the zip is dropped, and B2's checks are restated for the API;
> - D-59 (Q-28): full teachers are searched monthly too, and the first-run cap is a total for the first pass.
>
> **Argon's review (2026-10-20)** is merged: PIP-21..PIP-23 and TRI-09 are new; D-60 and D-61 record the owner's two calls. The responses are in `reviews/2026-10-20-argon-round-2.md`.
>
> **One thing is still open:**
> - **PORT reconciliation (section 10):** Library-AI---Rev1's `tool`-tagged lines must each map to a requirement here. This waits for the library's latest planning to reach GitHub (O-1, tracker T-09).

---

## 1. Scope

**SCOPE-01 · What the tool does** *fixed* · B2, D-25, D-26, D-27, D-28
For every teacher on the owner's list, the tool:

- finds up to three different public-domain or openly licensed photographs that certainly show them;
- makes three versions of each: the original, the white version and the black-and-white version, the last two at 1,000 and 500 px;
- checks each portrait;
- keeps everything by teacher, with a full rights record, and offers it to the library through its API.

**SCOPE-02 · Independent of the library** *fixed* · B2, D-37, D-44
- Nothing in the tool depends on Library-AI running.
- The only link between them is this tool's API, which the library calls (pull only). The tool never calls the library and holds no library key.

**SCOPE-03 · Nothing goes live from the tool** *fixed* · B2, D-38
- Every portrait waits for an admin's approval in the library.
- The tool never serves images to the library's readers.

**SCOPE-04 · Out of scope** *fixed* · B2, D-37, D-53
These are Library-AI's build, not this project:

- the library's side of the API (pulling, its own copies, sending decisions);
- the approval queue and the main-portrait choice;
- the people screen, the credits page and the blank portrait;
- the library's daily admin email;
- choosing which teachers exist beyond the list, and editing the library's records.

---

## 2. Inputs

**IN-01 · Teacher list** *fixed* · B2, D-22, D-45, D-60
- The tool's teachers come from library-pipeline's `collection/authors.csv`, read-only (IN-12). They are stored in the tool's database.
- Each teacher has:
  - `teacher_id`;
  - `name` and `aliases`;
  - `born` and `died`;
  - `wikidata_qid` and `lcnaf_id`, from the authors list's optional columns of the same names (D-60), or found by the tool (IN-13);
  - `key_works` (from the authors list's column of that name), used only to tell apart people who share a name (SRC-06b);
  - `notes` (from the authors list's stream and tier).

*Verify:* F-02, F-31 fixtures.

**IN-02 · Bad rows are reported by name, the rest load** *fixed* · B2; details *proposed* · C
- An active row that can't make a teacher is reported with its row number and reason, and the other rows load. The reasons are:
  - a missing name;
  - a date form that can't be read (only `YYYY-YYYY`, `d. YYYY`, `b. YYYY` or blank are read, D-45);
  - impossible dates (death before birth, a lifespan over 120 years, a future year);
  - a malformed `wikidata_qid` (not `Q` followed by digits) or `lcnaf_id` (not like `n79021164`) in the optional columns (D-60).
- Refusals appear on the admin page and in the run report (OUT-06).

*Verify:* one fixture per reason; each is reported with its row, and the other rows load (F-02).

**IN-03 · A broken list stops the sync before anything is spent** *proposed* · C
- The sync stops, keeps the previous teachers unchanged and reports why, before any search or model call, when `authors.csv`:
  - isn't UTF-8;
  - has no header;
  - lacks the `name`, `status` or `dates` column;
  - has no active rows.

*Verify:* fixtures: the read stops before any other client is called (F-02); the previous teachers stay unchanged (F-31).

**IN-04 · Which teachers can be searched, and by which rules** *fixed* · B2, D-45, D-47

| The teacher has | Match rules that may be used |
|---|---|
| A Wikidata id (checked, SRC-06) | R1, R2, R3 |
| A LoC name id, or both years | R3 |
| Neither, after IN-13 | None: skipped and listed on the admin page, with what to add to `authors.csv` |

*Verify:* F-31, F-35 fixtures.

**IN-05 · Notes are never used for matching** *fixed* · B2
`notes` is for the owner only. No code path reads it for searching or matching.
*Verify:* a test proves that changing a teacher's notes doesn't change their candidates (F-11).

**IN-06 · Requests from the library** *fixed* · B2, D-44, D-53; format *proposed* · C
- Requests arrive through `POST /api/v1/requests` (OUT-14) and are queued for the worker at once. There are three kinds:
  - `try_again`: a new draft from the same original. The note guides a fresh AI copy, through the enhance prompt and the draft check. A note about the crop or the outline can't change one portrait under one recipe (STY-05), so such a request is answered `refused` with that reason, suggesting `another_original`.
    - The note's kind (restoration, crop, outline or other) is judged by Claude Haiku with the prompt `note_kind.md` v2, stubbed in tests.
    - **A cut-out or silhouette fault counts as restoration,** because a fresh AI copy brings a new cut-out. Examples: an ear, hair or a shoulder cut off, or background left inside the line.
    - "Crop" means changing the zoom, centring or framing; "outline" means changing the line's style, thickness or colour.
  - `another_original`: the portrait becomes `turned_down` (reason `other`), its photograph is set aside, and the slot is filled from the next photograph.
  - `try_link`: try a pasted link on an adopted source (SRC-04).
- **Rejected at once:**
  - an unknown teacher or portrait: 404;
  - a link outside the adopted sources, or `try_again` or `another_original` without a portrait: 422.
- **The request's life cycle:**
  1. The web service validates the request (404 or 422 as above), writes it as `queued`, queues a priority job and answers 202.
  2. The worker classifies the note and does the work. Meanwhile the request is `working`.
  3. It ends `done`, with `result_portrait_id` set to the **new** portrait it published. A remake always gets a new portrait id, and the old portrait becomes `replaced` (OUT-07).
  4. Or it ends `refused`, with `refused_reason`:
     - a crop or outline note;
     - a refused licence;
     - a failed pre-check or draft;
     - no candidates left;
     - a cap reached.

  Each change of state appears in the change feed.

*Verify:* API and scenario tests (F-45, F-26).

**IN-07 · Decisions from the library** *fixed* · B2, D-38, D-44
- Decisions arrive through `POST /api/v1/decisions` (OUT-14):
  - **approve:** the portrait becomes `approved`. Approving a portrait with `replaces` set is the swap: the old portrait becomes `replaced` (PIP-17, D-61).
  - **turn_down,** with a reason (`not_this_teacher`, `do_not_use`, `quality`, `other`): the portrait becomes `turned_down`, and its photograph is set aside (PIP-11, PIP-17).
  - **set_main:** an approved portrait becomes the teacher's main one, and the previous main is unset.
  - **correct:** the approximate date or the best-known flag is replaced, and never overwritten by a later run (PIP-18).
- A decision that can't apply in the portrait's state answers `conflict`.
- **Main-portrait rules** (argon-13):
  - only an approved portrait may be `main`, and a teacher has at most one;
  - when a swap replaces the main portrait, `main` passes to the new portrait;
  - when the main portrait is turned down, `main` is cleared, and the teacher has none until the library sets one.

*Verify:* API and scenario tests, including both main-portrait cases (F-45, F-26).

**IN-08 · Requests and decisions are applied once** *proposed* · C
A request or decision sent again with the same `request_id` or `decision_id` changes nothing. A reused id with different content answers `conflict`.
*Verify:* resend tests (F-45).

**IN-09 · The owner's examples** *fixed* · B2, D-13
- `design/portraits/` holds the owner's three hand-made portraits (`targets/`, the style target) and their originals (`originals/`), for Charles Fillmore, Emilie Cady and Ernest Holmes.
- Their source is unknown, so they are test inputs and style targets only, and are **never published** (D-13).

**IN-10 · Settings** *fixed* · B2; layout *proposed* · C
- One committed settings module, `src/config/settings.ts`, holds everything except keys:
  - the recipe and `recipeVersion`;
  - the model for each role;
  - the caps;
  - the schedule;
  - the sources and their pacing;
  - the User-Agent contact.
- An invalid setting stops the service at start-up, naming the setting.
- See [architecture.md](architecture.md).

*Verify:* unit tests (F-01).

**IN-11 · Keys live outside the repo** *fixed* · B2, D-55
- Keys are Railway variables per environment (RUN-10): the OpenRouter key, the GitHub token, the session secret, and the database and bucket credentials. The admin password's hash is stored in the database (RUN-10).
- They are never written to the repo, logs, reports, the admin page or API answers.

*Verify:* a test scans every file and answer a stubbed run produces and finds no key value (F-01, F-26).

**IN-12 · Teacher list from the pipeline's authors** *fixed* · D-22, D-32, D-45, D-60; details *proposed* · C
- The sync reads `authors.csv` from the private library-pipeline repo through the GitHub API, with a read-only token limited to that repo's contents. It never writes there.
- **Only `active` rows** are read: 182 on 2026-10-19, the pipeline's own rule.
- **Mapping:**
  - `name` → `name`;
  - `aliases` → `aliases`, split on `;` and used for matching;
  - `dates` → `born` and `died` (IN-02);
  - the optional `wikidata_qid` and `lcnaf_id` columns → the same fields, with `ids_from = list` (D-60);
  - `key_works` → `key_works`, split on `;`, with each title's bracketed year and edition note removed;
  - stream and tier → `notes`.
- **Stable ids:** a `teacher_id` is made once, as a slug of the name, and kept in the database.
  - A renamed author keeps their id. There's no id column in `authors.csv`, so rows are matched to existing teachers in this order, never by row position:
    1. the same `wikidata_qid` or `lcnaf_id`;
    2. the same normalised name;
    3. a name or alias of the row matching a name or alias of the teacher, with compatible years where both have them.
  - A clashing slug gets `-2` and is reported.
  - An author no longer active is marked `on_list = false`, never deleted, and their portraits are kept.
- The sync runs nightly (RUN-08) and by command.

*Verify:* a fixture `authors.csv` syncs to the expected teachers; a rename keeps the id; a second sync changes nothing (F-31).

**IN-13 · Finding missing dates and ids** *fixed* · D-45; method *proposed* · C
- For a teacher without a Wikidata id or dates, the tool looks in two independent places:
  - Wikidata (SRC-06b);
  - the LoC name authority (id.loc.gov), whose headings carry life dates.
- It accepts an id and dates **only when both agree** on the person and both years. It then also records the LoC name id (`lcnaf_id`). This works for teachers with no dates at all, the ~110 who need it most. The method is SRC-06b.
- Anything less is listed on the admin page with its evidence, and can be downloaded as a CSV of suggested additions for `authors.csv`. The owner makes them there; the tool never writes to library-pipeline.
- A teacher still without a Wikidata id, a LoC name id or both years is skipped and listed (IN-04).

*Verify:* fixtures where both agree (accepted), disagree (listed only) and only one has data (listed only) (F-35).

---

## 3. Sources, rights and matching

**SRC-01 · Adopted sources only, enforced in code** *fixed* · B2, D-21, D-46
- Originals come only from the adopted sources:
  - Wikidata with Wikimedia Commons;
  - the Library of Congress (Prints & Photographs);
  - Wellcome Collection;
  - the LoC name authority, which identifies teachers and supplies no pictures.
- Smithsonian Open Access is added only if the coverage survey (SRC-14) shows gaps.
- **Not used:** NYPL (its API was retired on 1 August 2026), DPLA, the Internet Archive and book plates (D-24, D-46).
- The outbound client may contact only these hosts, listed in settings:
  - the adopted sources' hosts, including those that serve their files:
    - `www.wikidata.org`, `commons.wikimedia.org` and `upload.wikimedia.org`;
    - `www.loc.gov`, `loc.gov`, `tile.loc.gov` and `id.loc.gov`;
    - `api.wellcomecollection.org` and `iiif.wellcomecollection.org`;
  - `openrouter.ai`;
  - `api.github.com`, for the teacher list only (IN-12);
  - the environment's own bucket endpoint (from Railway's variables, OUT-12).

  Any other host is refused before a request leaves the process. This also enforces SRC-10.
- **Redirects** are followed by hand, and each target is checked against the same list (argon-11).

*Verify:* a request to any other host fails without network access (F-06).

**SRC-02 · Allowed licences, in two tiers** *fixed* · B2; edge cases *proposed* · C
- **Tier 1:**
  - public domain (any Commons public-domain mark);
  - CC0;
  - the Library of Congress's "No known restrictions on publication";
  - Wellcome's public domain mark.
- **Tier 2:** CC BY (any version) and CC BY-SA 2.0 or later.
- **Held for the owner, never processed:** CC BY-SA 1.0. Its adaptations can't be relicensed under a later version (SRC-11), so it's stopped here, before any paid step, and listed on the admin page.
- **Refused, always:**
  - NC and ND licences;
  - fair use or non-free;
  - unknown or missing rights;
  - GFDL alone;
  - custom "attribution" terms that aren't CC BY;
  - the LoC's "rights status not evaluated" or any restriction.
- A file under several licences is taken under the most open allowed one (GFDL with CC BY-SA becomes CC BY-SA).
- Anything the classifier can't map is refused and logged with the raw licence text.

*Verify:* a table test over real licence strings recorded from Commons, the LoC and Wellcome (F-07).

**SRC-03 · Certain matches only, in order** *fixed* · B2, D-24, D-47
A file counts as showing the teacher only by one of these rules, in this order:

1. **R1:** the image on the teacher's Wikidata item (P18).
2. **R2:** a Commons file whose structured data says it depicts the teacher's Wikidata item (P180).
3. **R3:** a picture record on the LoC or Wellcome that names the teacher with matching life dates (SRC-05), or carries the teacher's LoC name id.

These never count:
- membership of a Commons category;
- a filename or caption that only mentions the name;
- a name match without dates or id;
- any search-result ranking.

R4 (book plates) is *withdrawn* (D-24); see `sources.md`.

*Verify:* recorded-response fixtures for each rule, plus negatives: a category-only file, a name-only LoC record and a record with the wrong dates (F-09, F-10, F-34).

**SRC-04 · A pasted link is the owner's match** *fixed* · B2, D-47; limits *proposed* · C
- A link in a `try_link` request is accepted as the owner's own match (`matched_by: owner_link`).
- It must point to an adopted source, and its licence must pass SRC-02.
- **The link is read without fetching the web page.** These forms are accepted:
  - **Commons:** `commons.wikimedia.org/wiki/File:<title>` or an `upload.wikimedia.org/…/<title>` file link, giving `File:<title>`;
  - **LoC:** `(www.)loc.gov/(pictures/)item/<id>` or `loc.gov/resource/<id>`, giving the item `<id>`;
  - **Wellcome:** `(api.)wellcomecollection.org/(catalogue/v2/)works/<id>`, giving the work `<id>`.
- Anything else is refused with 422.

*Verify:* fixtures (F-45).

**SRC-05 · The name-and-dates match, precisely** *proposed* · C, D-47
A LoC or Wellcome record matches when either of these holds:

- **its name heading carries a LoC name id equal to the teacher's** `lcnaf_id`; or
- **both of these hold:**
  - a name heading (for example `Fillmore, Charles, 1854-1948`), reordered to forename and surname and normalised (case, accents, punctuation), equals the teacher's name or an alias;
  - its dates equal the teacher's birth and death years.

A heading without dates or id never matches.
*Verify:* fixtures with an id match, a matching heading, a near miss and an undated heading (F-10, F-34).

**SRC-06 · Checking and finding Wikidata ids** *fixed* · D-45; checks *proposed* · C
- **(a) A given id is checked:** the item must be a human (Q5), and where the teacher has years, the item's must equal them. On a mismatch the teacher is skipped and listed ("the Wikidata id may be wrong").
- **(b) A missing id is found** (IN-13) like this, for teachers with or without years:
  1. **Wikidata:** humans whose label or alias equals the teacher's name or an alias, normalised, with both a birth and a death year. Their years must match any the teacher already has.
  2. **The LoC name authority:** a name record for the same name, with life dates.
  3. **The two must name the same person:**
     - the Wikidata person's LoC id (P244) is that name record;
     - their years agree in both places.
  4. **When several Wikidata people qualify** (names collide; there's a linguist called Charles J. Fillmore, for one), the teacher's key works from `authors.csv` must pick out exactly one. That one must have a notable work (P800), or be the author (P50) of a work, whose title matches a key work. Otherwise nothing is accepted.

  An accepted id is recorded as `resolved_by_tool` and offered for `authors.csv`.
- **(c) Otherwise** the teacher is skipped and listed (IN-04).

*Verify:* fixtures for a good id, wrong years, a non-human id, an undated teacher resolved by the P244 link, two same-name people resolved by key works, two not resolvable, and none (F-08, F-35).

**SRC-07 · The best copy of a photograph** *fixed* · B2, D-40; method *proposed* · C
- Among the copies of one photograph (PIP-15), the order is:
  1. licence tier;
  2. then pixel count, largest first;
  3. then the pre-check's damage rating, once known.
- The best copy is pre-checked first. If it fails for damage, the next copy is tried (PIP-21).
- Exact duplicates (the same SHA-256, or the same file reached by two rules) are merged, keeping the strongest rule.
- Set-aside photographs are excluded (PIP-12).
- Which photographs fill the slots is PIP-16.

*Verify:* unit tests (F-11).

**SRC-08 · The original's record** *fixed* · B2, D-14
Every original considered keeps, enough to credit it properly:

- `source` (`commons`, `loc` or `wellcome`), `source_id` (the source's own id), the item link and the file link;
- title, creator and date as given;
- the licence as given, its link and its tier (1 or 2);
- the credit line (SRC-11);
- `matched_by` (`wikidata_p18`, `commons_p180`, `name_dates`, `lcnaf_id` or `owner_link`), `matched_to` and the match evidence;
- the medium (from the pre-check, D-47);
- size in bytes, pixel dimensions and SHA-256.

These are the field names of the API's `Source` record (OUT-14).

The creator may be recorded as unknown when the source says so. The source, item link, licence and credit line are **never blank**; a candidate without them is refused.
*Verify:* every record in the end-to-end run is complete, and a candidate without a credit line is refused (F-32, F-26).

**SRC-09 · Polite access** *fixed* · D-46 (User-Agent, limits); details *proposed* · C
- Every request carries a User-Agent with the app's name, version and a contact address from settings (O-10). It's an address set up for the app, never a personal one in the repo. Wikimedia's 2026 limits give unidentified clients far less.
- Each source is paced to its published limit:
  - the LoC JSON API: 20 requests a minute (a 1-hour block above that), and 150 a minute for images and media;
  - Wikimedia and Wellcome: one request at a time.
- Retries back off on 429 and 5xx. An HTML CAPTCHA page counts as a 429.
- Responses are cached, so a resumed run doesn't fetch twice. Tests replay recorded responses.

*Verify:*
- the client's headers;
- pacing: calls to the LoC are spaced evenly, one every 3 seconds, so 30 calls take at least 87 seconds on a fake clock;
- retries: a 429 and a CAPTCHA page both back off (F-06).

**SRC-10 · Never the library's own scans or the reference shelf** *fixed* · B2
The tool has no setting, path or code that reads Library-AI's scans or the owner's reference shelf. SRC-01 enforces this.
*Verify:* SRC-01's test (F-06).

**SRC-11 · Licences and credits of every file** *fixed* · D-48
Every file of a portrait (OUT-11) records its own `licence`, `licence_url` and `credit`.

| Original's licence | `original`, `original-view` | Adaptations: `white-*`, `bw-*`, `enhanced`, `mask` |
|---|---|---|
| Public domain, CC0, "no known restrictions" | As the source gives it | **CC0 1.0** (D-48) |
| CC BY (any version) | As the source gives it | **CC BY 4.0**, crediting the original's author and licence |
| CC BY-SA 2.0 or later | As the source gives it | **CC BY-SA 4.0** (ShareAlike; a permitted later version) |
| CC BY-SA 1.0 | As the source gives it | Held for the owner, never published automatically |

**Credit lines:**
- **Original:** "<title or the teacher's name>, <date>. <Creator, or Photographer unknown>. <Holder and collection>. <Licence>."
  - Example: "Charles Fillmore, c. 1895. Photographer unknown. Library of Congress, Prints & Photographs Division. No known restrictions on publication."
- **Adaptations:** "Portrait by New Thought Nexus, adapted from: <original credit>" (D-48). The AI copy and the mask read "AI-assisted restoration by …" and "Cut-out mask by …".
- **CC BY and CC BY-SA:** the line also carries the original's title, author, source link and licence link, as the licences require.

*Verify:*
- fixtures for each row;
- a CC BY-SA 1.0 original is held;
- every file of every fixture portrait has a licence, a link (null only where the source gives none) and a credit (F-24).

**SRC-12 · The rights log** *proposed* · C, D-21
- Every original considered, **including the refused ones**, gets one permanent row in the database. The row holds:
  - SRC-08's fields;
  - the rights evidence quoted raw;
  - the verdict and its reason;
  - the outcome: used, a copy of another, failed the pre-check, or set aside.
- The raw source record (JSON) is kept. Nothing is researched twice.
- The admin page offers the log as a CSV download (OUT-13).

*Verify:* the end-to-end run leaves one row per original considered, refusals included, and a second run adds no duplicates (F-32, F-26).

**SRC-13 · Finding plates in books** *withdrawn* (D-24). The method is kept in `sources.md`, in case plates are ever needed.

**SRC-14 · Coverage survey** *proposed* · C, D-46 · *live (free)*
- A survey run searches every active teacher on every adopted source, and reports what each would find:
  - candidates by match rule;
  - licence tier;
  - size.
- It downloads no files, makes no AI calls and creates no portraits.
- Its report shows each source's coverage and the teachers with nothing. That decides whether Smithsonian is worth its key (D-46), and it supplies the trial set (TRI-02) and real same-photograph pairs (PIP-20).
- The same code serves as `run --dry-run`.

*Verify:* offline, the report's counts match recorded fixtures; live, it completes for all active teachers within the sources' limits (F-38).

---

## 4. The style

**STY-01 · Halftone** *fixed* · B2
- A one-colour halftone: round white dots on a 45° grid, about 110 across the square (measured on the owner's portraits: Fillmore 109, Holmes 111).
- Dot size follows tone. Dark tones are left transparent, so the page shows through as the shadows.
- **Contrast is lifted a little,** so the face reads in dots:
  - levels come from the face's own tones;
  - then a gamma;
  - then a light unsharp mask.

  The numbers are in `prototype/recipe.py`.

*Verify:* on a synthetic gradient, frequency analysis finds the dot pitch and the 45° angle, and dots grow with brightness (F-14).

**STY-02 · Outline** *fixed* · B2; bottom edge *proposed* · C
- One thin, smooth white line just outside the head and shoulders, following the hair's overall shape rather than single strands.
- Where the shoulders run off the bottom, the line runs off with them.
- 6 px wide, 2 px outside a smoothed silhouette, at 1,000 px. The dots are clipped to the same silhouette. The head is smoothed gently, the shoulders harder.

*Verify:* on fixtures, the line is one connected piece, within its width, a set distance outside the figure (F-15).

**STY-03 · Crop** *fixed* · B2; measured values *proposed* · C
- A square, head and shoulders, with the head near the top.
- The face fills most of the width, the shoulders run off the bottom, and there's no background.
- Measured on the owner's three portraits with YuNet's landmarks (recipe 0.5.0): eye-to-mouth distance 0.221 of the side, eye line at 0.449 of the height, face centred. (Recipe 0.4.0 had 0.237 and 0.443, measured with a different detector, SCRFD, which places the mouth corners differently. The owner's framing is the same; only the landmarks it's measured from changed.)

*Verify:* on fixtures, the eye line, the eye-to-mouth distance and the centre fall within the settings' ranges (F-12).

**STY-04 · The likeness stays the photo's own** *fixed* · B2, D-18, D-49
- The dots and the outline are always made by code.
- The dots come from the original's tones, blended with an aligned, AI-enhanced copy that contributes at most `enhanceBlend` (0.5) of the tones (PIP-13).
- No image model draws the dots or the line. No AI image reaches the portrait except through that aligned, checked and recorded blend.
- The likeness is always checked against the original (PIP-09).

*Verify:* by construction: the halftone's only input is the cropped, blended tone image. A test checks the blend share (F-30).

**STY-05 · One recipe for every teacher** *fixed* · B2
- One set of settings applies to every teacher.
- Each portrait records `recipeVersion` and a hash of the recipe settings.
- Changing any recipe setting requires a new `recipeVersion`.

*Verify:* a test fails if the recipe's hash changes without a version change (F-01).

**STY-06 · The white version (master)** *fixed* · B2; exact test *proposed* · C
`white-1000.png` is a 1,000 × 1,000 PNG with an alpha channel:
- every pixel with any opacity is pure white, and the shape is carried by alpha alone;
- the corners and everything outside the figure and line are fully transparent.

*Verify:* a checker run on every master in every test and before publishing (F-15).

**STY-07 · The target** *fixed* · B2, D-16, D-49
- The owner's three hand-made portraits are the target.
- The starting recipe is the Python prototype's recipe (`prototype/recipe.py`, `prototype/out/`). The owner accepted 0.4.0 as close enough to build on (D-49), and the trial may tune it.
- **Recipe 0.5.0** (2026-10-20) keeps 0.4.0's look and changes two things the port needed (`prototype/README.md`):
  - the crop's constants are measured with YuNet, the detector the app uses (STY-03);
  - the drift check (PIP-13) is measured inside the inner face, so a box edge on the hair can't count as drift.

*Verify:* the TypeScript port reproduces `prototype/out/` from `prototype/fixtures/` within the tolerances in [architecture.md](architecture.md) (F-16).

**STY-08 · The black-and-white version** *fixed* · D-26, D-39; exact test *proposed* · C
Made by code from the master's own layers, with nothing new to tune:
- inside the figure: white where the master has dots, black everywhere else;
- the master's gap and line are drawn **black** (option C), so the figure sits on an 8 px black margin;
- transparent outside the line's outer edge, so its footprint is exactly the master's;
- 1,000 × 1,000, 8-bit RGBA PNG, the same crop as the master.

*Verify (`check_bw` in `prototype/recipe.py`):*
- every visible pixel is grey (R = G = B);
- the top corners are transparent;
- it is opaque everywhere the master shows (F-41).

**STY-09 · Small copies** *fixed* · D-39; method *proposed* · C
- The master and the black-and-white version also come at 500 × 500 px.
- They are scaled down from the 1,000 px files by area averaging with premultiplied alpha.

*Verify:* STY-06's checker and `check_bw` pass at 500 px (F-41).

---

## 5. The pipeline, per teacher

**PIP-01 · Choose** *fixed* · B2, D-40
For each open slot (PIP-14), take the next photograph by PIP-16 that hasn't been set aside, and its best copy by SRC-07, in the step order of PIP-21.
*Verify:* F-23 scenarios.

**PIP-02 · Pre-check the original before spending more** *fixed* · B2, D-52; output *proposed* · C
- A vision model confirms:
  - exactly one person;
  - the face fully in view;
  - a face box at least `minFacePx` (90) source pixels wide (the owner's originals: 108–183);
  - no heavy damage.
- It returns a structured verdict with the reasons:
  - an approximate face box;
  - the medium;
  - an age estimate (PIP-18);
  - any printed dot pattern;
  - any caption, as written, with the person it names. A caption naming someone else fails.
- A failing original is set aside with its reason, and nothing more is spent on it.
- **The face box comes back as fractions** (0..1) of the width and height. Code turns it into pixels and checks `minFacePx` itself, since the model doesn't know the picture's size.
- **Model:** Claude Haiku 5.5 through OpenRouter (D-52); prompt `precheck.md` v2. It is sent the viewing copy (PIP-22).
- **Medium:** any medium that passes is used (D-47). A setting (`allowedMedia`) can turn engravings off after the trial.

*Verify:* stubbed responses drive the pass and fail paths (F-18). The live behaviour is judged in the trial.

**PIP-03 · Cut-out** *fixed* · B2, D-19; method *proposed* · C
- The cut-out comes from the AI-enhanced copy (PIP-13). That one call returns the person on flat pure green, and code reads the mask from the green. The copy and its cut-out line up by construction.
- **Fallback:** a separate "background to green, change nothing else" call (`cutout_keyed.md`) is made when:
  - the enhance call fails or errors;
  - the AI copy is refused by its safeguards (PIP-13);
  - its mask fails PIP-19's limits.

  The fallback's image is aligned to the original exactly as the AI copy is.
- The mask is mapped back onto the original's own size and position (through the alignment), kept as `mask.png` (OUT-11), and reused for every later try on the same original.

*Verify:* a stub test proves the second try makes no new call (F-19).

**PIP-04 · Crop, by code** *fixed* · B2; method *proposed* · C
- A similarity transform from five face landmarks (eyes, nose, mouth corners).
- The scale comes from the eye-to-mouth distance, which holds steady when the head turns. The eye line sits at a set height, with the face centred.
- The landmarks come from YuNet, a local face detector with a permissive licence (MIT), committed in `models/`.
  - YuNet finds faces of about 10 to 300 px, so an original over 640 px on its long side is searched on a copy reduced to 640 px, and the results are scaled back.
  - YuNet reports boxes as x, y, width and height; code turns them into corners (x0, y0, x1, y1), the form the recipe uses.
- **If no face is found,** as can happen with engravings, five landmarks are estimated from the pre-check's face box. With width w, height h and centre cx, the proportions are where YuNet's landmarks sit inside its own box on the owner's three originals (`landmarks_from_box` in `prototype/recipe.py`):
  - eyes at (cx ± 0.22 w, y0 + 0.39 h);
  - nose at (cx, y0 + 0.58 h);
  - mouth corners at (cx ± 0.19 w, y0 + 0.74 h).

  The crop then runs unchanged. On the three originals, a crop made this way from YuNet's box puts the eye line within 0.03 of the side of the real crop's, at a scale within 10%.

*Verify:* synthetic and fixture images (F-12).

**PIP-05 · Descreen and edge-preserving blur, by code** *fixed* · B2, D-17, D-23; method *proposed* · C
- It runs on the original, before cropping, since a print screen's spacing is in the original's pixels. It works on the working region of PIP-23.
- **A printed dot pattern is detected by frequency analysis.** It counts when compact peaks stand well above their surroundings in at least two directions. Its peaks and their first harmonics are notch-filtered.
- **Every original gets an edge-preserving (bilateral) blur,** stronger when a screen was found. Its size is set in dot cells, so it suits any original size.
- What was found and applied is recorded.

*Verify:* the owner's Fillmore and Cady originals are detected as screened and Holmes isn't; a synthetic screen's peaks drop by a set factor (F-13).

**PIP-06 · Halftone, by code** *fixed* · B2
The halftone is made straight onto transparency, to STY-01.
*Verify:* STY-01 and STY-06 checks (F-14, F-15).

**PIP-07 · Outline, by code** *fixed* · D-49
- Code smooths the cut-out mask (gently for the head, harder for the shoulders), widens it by the gap and strokes the line at the set width.
- It is deterministic and free.
- B2's image-model outline is *withdrawn* (D-49).

*Verify:* fixtures (F-15).

**PIP-08 · Composite** *fixed* · B2
Code lays the line over the dots and writes the master (STY-06).
*Verify:* F-15.

**PIP-09 · Check the draft** *fixed* · B2, D-51, D-52; output *proposed* · C
- A vision model checks each draft once, on `white-1000`. The other versions are checked by code (STY-08, STY-09).
- **Model:** Claude Sonnet 5.5 through OpenRouter. Its family must differ from the enhance model's, which settings check at start-up.
- **The criteria are:**
  - the outline hugs the figure;
  - the cut-out is clean;
  - no moiré;
  - the face reads and matches the **original**;
  - the crop matches the examples.
- **What it sees, in this order** (as `draftcheck.md` says):
  1. the original's viewing copy (PIP-22);
  2. the draft on the dark page colour;
  3. the three examples, on the same colour.

  The colour is `checkPageRgb` (28, 30, 38) in settings.
- **What it returns:** per criterion, pass or fail with a 1–5 score and short notes. A draft passes only when every criterion passes.
- The notes go into the portrait's record.
- A "compare with target" mode scores a draft against a hand-made portrait (TRI-08).

*Verify:* stubbed responses (F-21).

**PIP-10 · Remaking a failed draft** *fixed* · B2, D-51
- A failed draft is remade **once, with a fresh AI-enhanced copy**, which brings a new cut-out too. That is the only step that can come out differently.
- A remake never re-asks the checker about the same draft.
- A failure a new copy can't change sets the original aside at once: the crop, or a cut-out limit (PIP-19) when there was no AI copy.

*Verify:* failure-policy scenarios (F-23).

**PIP-11 · Failure policy** *fixed* · B2, D-40, D-51; counting *proposed* · C
- Two failed drafts set an original aside.
- **Per teacher, per run:**
  - at most **6** originals reach drafting (two tries for each of three slots);
  - at most **12** are pre-checked. Pre-check failures don't count toward the 6.
- Slots still empty stay empty until a later run.
- A turn-down from the library (IN-07) sets aside every copy of that photograph. A clearly better copy may come back once (PIP-17).
- On a later run, only new candidates are tried. The monthly search (RUN-08) is what finds them.

*Verify:* scenarios (F-23).

**PIP-12 · Set-asides are remembered** *proposed* · C
- Every set-aside (photograph, copy, reason, date, run) persists in the database.
- A set-aside photograph is never tried again, except:
  - as a clearly better copy (PIP-17);
  - or through a library `try_link`.
- Set-asides are shown on the admin page.

*Verify:* a two-run scenario (F-23).

**PIP-13 · Blend in an AI-enhanced copy** *fixed* · D-18, D-19, D-56; details *proposed* · C
- **The copy.** After descreening, an image model makes a subtly enhanced copy of the original through OpenRouter:
  - prompt `enhance_keyed.md`: clean up and clarify, keep the face and framing exactly, black and white, background flat pure green;
  - starting model `google/gemini-3-pro-image` (Nano Banana Pro);
  - the trial compares it with `google/gemini-3.1-flash-image` and `openai/gpt-image-2` (TRI-03), and the winner becomes the default.
- **Alignment.** Code aligns the copy to the original first (ECC on a similarity or affine transform), because image models shift and rescale what they redraw.
  - Below `enhanceMinAlign` (0.90) the copy isn't used, and the original is used alone.
- **Local drift check.** After aligning, dense optical flow measures how far details inside the face still sit apart. It's measured inside the face box shrunk by `driftBoxInset` (0.15) on each side, so the box's edge on hair or background can't count as drift (recipe 0.5.0).
  - Above `enhanceMaxDriftCells` (0.7 of a dot cell, 95th percentile) the copy isn't used.
  - Prototype (0.5.0): good copies 0.14–0.31; copies with features moved by about 1.2 cells 0.95–1.08.
- **Blend.** The copy gets the same edge-preserving blur as the original, then is blended at `enhanceBlend` (0.5) **in the portrait's own frame**, so its extra resolution survives.
- **Records.** The copy is kept (`enhanced.png`) even when not used, with:
  - the model;
  - the prompt version;
  - the alignment and drift scores;
  - whether it was used, and why not.
- **Cost:** one call per original. A remake is the only second call (PIP-10).

*Verify:* synthetic keyed copies (larger, sharpened, rescaled, shifted, on green) align (correlation ≥ 0.99 in the prototype) and blend without double edges; a moved-feature copy is refused (F-30).

**PIP-14 · Up to three portraits per teacher** *fixed* · D-25, D-40; setting *proposed* · C
- A teacher has at most `maxPortraitsPerTeacher` (3) portraits that are being made, waiting or approved.
- Turned-down and replaced portraits don't count; their slot is filled from the next photograph.
- A waiting portrait with `replaces` set (an offer under PIP-17) doesn't count either. If the library approves it, the portrait it replaces becomes `replaced`, so the count stays at most 3.

*Verify:* scenario: 5 different photographs give 3 portraits; a turn-down frees a slot for the 4th (F-23).

**PIP-15 · Different photographs, not copies** *fixed* · D-40, D-50
- Each portrait is a **different photograph**: another sitting, age or pose.
- Scans, crops, retouches and prints of one photograph are **copies**. They are grouped by PIP-20, and only the best copy is used (SRC-07).
- The other copies stay in the rights log as copies, so a better copy is recognised later.

*Verify:* fixtures: copies group together; two sittings don't (F-11, F-42).

**PIP-16 · Choosing which three** *fixed* · D-40; spread *proposed* · C
When more different photographs pass than there are free slots:
1. The teacher's **best-known image** comes first: Wikidata's main image (P18), or a copy of it. Without one, the best-quality photograph comes first.
2. Then the best quality, **spread across the teacher's life**, by approximate date (PIP-18).

**The rule, step by step** (argon-13):
- Quality order is licence tier, then damage rating, then pixel count.
- Each further slot takes the best-quality dated photograph at least `minSpreadYears` (10) from every photograph already chosen.
- If none is that far, it takes the dated one whose nearest chosen year is furthest away (ties go to quality).
- With no dated photographs left, it takes the best undated one.

*Verify:* unit test: P18 is kept; of two similar photographs from the same years and one from another decade, the other decade's wins (F-23).

**PIP-17 · Later runs: better copies and turn-downs** *fixed* · D-40, D-59, D-61; details *proposed* · C
- **A clearly better copy of an approved portrait** is offered as a new waiting portrait with `replaces` set. The approved one stays until the library approves the new one, which is the swap. Finding one needs the teacher to be searched again even when their slots are full, which they are, monthly (RUN-08, D-59).
- *Proposed:* a clearly better copy of a portrait still waiting replaces it (OUT-07).
- **When all slots are full,** a different photograph that clearly ranks above one of them is offered as a draft with `replaces` set to the one it would displace (D-61). Examples: the best-known image, or a much better photograph from an uncovered part of life. The library decides; if it approves, the displaced portrait becomes `replaced`.
- **A turned-down photograph** may come back only as a clearly better copy, offered once. It never comes back when the reason was `not_this_teacher` or `do_not_use`.
- *Proposed:* **clearly better** means either:
  - a face at least 1.5× larger in pixels, with no lower licence tier;
  - or the same size, rated clearly less damaged by the pre-check.

*Verify:* scenarios:
- a better copy of an approved portrait gives a marked draft and leaves the approved one untouched;
- turned down for `quality`, a 2× copy is offered once;
- turned down as `not_this_teacher`, it never returns (F-48).

**PIP-18 · Approximate date, and the library's corrections** *fixed* · D-41; method *proposed* · C
- There is no category scheme. Each portrait records an approximate date, used by PIP-16:
  - the source's date (exact or circa);
  - otherwise the pre-check's age estimate plus the birth year, marked as estimated;
  - otherwise unknown, which ranks after dated photographs.
- **The library can correct** the date and the best-known flag (IN-07). A correction is never overwritten.

*Verify:* a source date beats an estimate and an estimate uses the birth year (F-23); a correction survives a re-run (F-48).

**PIP-19 · Cut-out sanity limits** *proposed* · C, D-49
Before the draft check, code refuses a draft whose figure (inside the outline, at 1,000 px) breaks any of these:
- it fills 35–80% of the square (the examples: 53–64%);
- the largest connected piece holds at least 98% of it. This is measured on the raw cut-out in the frame, **before** smoothing: smoothing keeps only the largest piece, so a fragment would otherwise never be seen (argon-4). The other three limits are measured on the smoothed figure;
- the face box lies inside it;
- it meets the bottom edge across at least 40% of the width (the examples: 68–96%).

A refusal counts as a failed draft and names the limit.
*Verify:* the three example masters pass; a floating fragment, a figure cut off above the shoulders and a full square are refused, each naming its limit (F-15).

**PIP-20 · Same photograph or a different one** *fixed* · D-50; method and thresholds *proposed* · C
Each new candidate is compared with the teacher's other candidates and with all their portraits, turned-down ones included.

1. **Fingerprint:** a 64-bit difference hash of the whole picture, with at most 2 bits different, or the same SHA-256. It catches only exact, re-encoded or resized duplicates. A loose face hash could merge two different frontal sittings, since the crop aligns every face the same way (argon-17).
2. **Feature matching:**
   - SIFT points at about 600 px;
   - a 0.75 ratio test;
   - RANSAC on a similarity transform (4 px), also tried mirrored.
   - `sameMinInliers` (40) or more means the same photograph; `diffMaxInliers` (20) or fewer means different.
3. **In between, the vision model decides** (Sonnet, `same_photo.md`).
4. **If it is unsure, they are the same photograph** (D-50).

Each picture's feature points are computed once and kept. A new candidate is compared with one representative of each existing photograph group, not with every copy.

The prototype (`prototype/same_photo.py`) scored doctored copies 56–330 and different photographs 19 or less. The thresholds are checked on the survey's real pairs, two sittings of one teacher included, before the build relies on them. They assume SIFT. If the porting spike (F-39) has to fall back to another detector, the thresholds are measured again on the same fixtures, and the change is recorded as a recipe change (STY-05).

*Verify:*
- copies (crop, rescale, rotation, JPEG, blur, reprint screen, mirror, noise) are the same;
- different photographs are different;
- a pair in between goes to the model stub;
- "unsure" gives "same" (F-42, F-43).

**PIP-21 · The order of steps for one teacher** *proposed* · C (argon-1)
Each step uses only what earlier steps produced:

1. **Gather** candidates from every adopted source, by R1–R3 (SRC-03).
   - Classify their licences (SRC-02) and log refusals.
   - Merge exact duplicates (same source and id, or same file link).
2. **Fetch previews:** a small image, about 800 px on the long side, from each source's own sized-image service (Commons thumbnails, LoC derivatives, Wellcome IIIF), for at most `maxCandidatesPerTeacher` (24) candidates, ordered by rule and size. Record each preview's SHA-256. Full originals aren't downloaded yet.
3. **Group copies into photographs** (PIP-20), on the previews, and order each photograph's copies (SRC-07).
4. **Pre-check** the best copy of each photograph not set aside (PIP-02), within the per-run cap of 12 (PIP-11). This gives the damage rating, medium, face box and age estimate.
5. **Choose** which photographs fill the open slots (PIP-16), from those that passed.
6. **Download the full original** of each chosen copy, check its SHA-256, and make the portrait (PIP-03..PIP-13, up to 6 drafts per run).

*Verify:* a scenario where a candidate's pre-check fails picks the next photograph; no full original is downloaded for a photograph that isn't chosen; previews are never sent to the bucket (F-11, F-23).

**PIP-22 · What the models are sent** *proposed* · C (argon-2)
- AI models never get the original file: Library of Congress masters can be 40 MB TIFFs, which the models refuse.
- **The pre-check and the draft check** get the 8-bit sRGB PNG viewing copy (OUT-05), at most 1,600 px.
- **The enhance call and the cut-out fallback** get the descreened working region (PIP-23; the whole descreened original when it's 2,000 px or less), as an 8-bit sRGB PNG at most 1,600 px on the long side.
- **The same-photograph check** gets 800 px images.
- Every image sent is under 5 MB. A larger one is re-encoded smaller before sending.

*Verify:* request-shape tests for each model step: PNG only, size limits, never `image/tiff` (F-18, F-19, F-21, F-43).

**PIP-23 · Working resolution** *proposed* · C (argon-7)
- **An original up to `maxWorkingPx` (2,000 px) on its long side** is processed whole, as the prototype does.
- **A larger one** is processed as a **working region:** the crop's square plus a margin of 25% on each side, cut from the original at full resolution and reduced by area averaging to at most 2,000 px on its long side. Every size the steps use (dot cells, blur radii, landmarks) is in the region's own pixels.
- A 13-megapixel LoC scan is therefore never processed whole, while the crop square keeps more pixels than the 1,000 px frame needs.
- The original itself is kept untouched in the bucket (OUT-11).
- The halftone's threshold map depends only on the recipe, so it is computed once per recipe and reused.

*Verify:* a 4,000 × 5,000 synthetic original finishes within a time and memory limit set in the card; the owner's examples, already small, are unaffected (F-13, F-14, F-16).

---

## 6. Output, storage and the API

**OUT-01 · Delivery folder layout** *withdrawn* (D-31, D-42). Files live in the tool's bucket (OUT-12), and the library pulls through the API (OUT-14).

**OUT-02 · The portrait's record** *fixed* · B2, D-14, D-37
- Every published portrait has one record, the API's `Portrait` (OUT-14). It replaces Rev1's manifest, which is no longer used (D-37). It holds:
  - the teacher (`teacher_id`);
  - the portrait's id, status, `main`, `replaces` and `replaced_by`;
  - the photograph id;
  - the approximate date and best-known flag (PIP-18);
  - the original's record (SRC-08);
  - its files with their sizes, SHA-256, licences and credits (OUT-11, SRC-11);
  - whether the AI copy was used;
  - the recipe version.
- The check's notes, the attempts and any set-asides are in its history and on the admin page.

*Verify:* every record in the end-to-end run validates against the OpenAPI schema (F-03, F-24).

**OUT-03 · A portrait appears only when complete** *proposed* · C
- A portrait's files are written to the bucket first.
- Its record and its change-feed entry are then written in one database transaction.
- A run stopped part-way never exposes a portrait with missing files.

*Verify:* kill the work mid-portrait in a test; the API shows no portrait whose files are missing (F-24).

**OUT-04 · Bad records are never published** *fixed* · B2
A portrait whose record fails the schema, or lacks a licence or credit, isn't published. It is marked `failed`, its candidate is set aside so later runs don't retry it, and it is named on the admin page with the failing field.
*Verify:* a fixture missing its licence is refused, naming the field (F-24).

**OUT-05 · Viewing copy of the original** *fixed* · B2, D-39
- The original is kept exactly as downloaded (OUT-11).
- Its viewing copy is a **PNG**, keeping any transparency, at most 1,600 px on the long side and never enlarged.

*Verify:* a large fixture comes out at 1,600 px, a small one keeps its size, and transparency is kept (F-41).

**OUT-06 · Run report** *fixed* · B2, D-53; contents *proposed* · C
Each run's report is a page on the admin site (RUN-09). It says, in plain words:

- what was done;
- what was spent, in total and per teacher;
- what was set aside, and why;
- which teachers were skipped, and why;
- which requests and decisions were handled;
- which authors-list rows were reported (IN-02);
- the ids and dates suggested for `authors.csv` (IN-13);
- errors;
- whether a cap was reached.

*Verify:* a snapshot test of the fixture run's report (F-25).

**OUT-07 · Replacing a waiting draft** *fixed* · B2, D-40, D-42, D-61
- A new draft of the same photograph replaces the one still waiting (a remake on a library `try_again`, or a better copy under PIP-17).
- The old one becomes `replaced`, with `replaced_by` set, and keeps its files.
- `replaced` always means **"superseded by the portrait in `replaced_by`"** (D-61). That is one of:
  - a better copy, or a higher-ranked photograph, the library approved in its place;
  - a newer draft that replaced a waiting one.
- The library sees both changes in the change feed.

*Verify:* scenario (F-48, F-26).

**OUT-08 · Bulk-upload zip on request** *withdrawn* (D-58): the library pulls everything through the API (D-37, D-42).

**OUT-09 · Delivery target** *withdrawn* (D-31, D-42): there is no Drive folder.

**OUT-10 · Samples for the library** *fixed* · B2, D-37, D-58; mechanism *proposed* · C
- The repo keeps sample payloads for every route (`contracts/portraits-api.sample.json`). They validate against the contract (`check_api.py`).
- A staging copy, seeded with fixture portraits in stub mode, lets the library's builders pull end to end before any real portrait exists.
- The library's acceptance check of the hand-off is to pull from staging and send one decision of each kind (D-58).

*Verify:* `check_api.py` passes (F-03); the library stub completes against the seeded staging copy (F-05, F-27).

**OUT-11 · The files of a portrait** *fixed* · D-26, D-39; names *proposed* · C
Each portrait's id is `<teacher_id>-<n>` (for example `charles-fillmore-1`). `n` counts up as portraits are made and is never reused.

| File | What |
|---|---|
| `original.<ext>` | The original, byte for byte as downloaded |
| `original-view.png` | Its viewing copy (OUT-05) |
| `white-1000.png`, `white-500.png` | The master (STY-06) and its small copy (STY-09) |
| `bw-1000.png`, `bw-500.png` | The black-and-white version (STY-08) and its small copy |
| `enhanced.png` | The AI copy as the model returned it, kept even if refused (PIP-13) |
| `mask.png` | The cut-out mask: 8-bit grey, white is the person, mapped back onto the original's size and position through the alignment (PIP-03) |

- All are offered to the library (D-39).
- Seven are always present. `enhanced.png` is missing only when the AI copy couldn't be made at all; `enhanced_used` is then false, and the history says why.
- Download names for people read like `Charles Fillmore - portrait 1 - white 1000.png`.

*Verify:* the fixture run produces every file per portrait, each passing its own check, and a fixture whose enhance call failed has the other seven (F-24).

**OUT-12 · Storage** *fixed* · D-42; layout *proposed* · C
- Files live in the tool's own private bucket (Railway, S3-compatible), one per environment. There is no Drive copy.
- **Layout:** `portraits/<teacher_id>/<portrait_id>/` holds the files and a `record.json`, rewritten from the database whenever the portrait changes.
- **History is kept.** Replaced and turned-down portraits keep their files. Nothing is deleted automatically.
- **Candidates that never become portraits** are logged in the rights log, not stored.
- **The library keeps its own copies** of what it pulls (D-42).
- **Backups:** the database only, at first (Railway). The bucket can be rebuilt from the rights log and the recipe, except the AI copies.

*Verify:* the layout and `record.json` match the database; a turned-down portrait's files remain; a failed candidate has a log row and no files (F-24, F-37).

**OUT-13 · Admin page** *fixed* · D-33, D-42; contents *proposed* · C
- A read-only site behind one password (RUN-10). It works on a phone.
- **Teachers:** each teacher's portraits, with all versions, the rights record and the library's decisions; teachers skipped or unidentified, with suggestions for `authors.csv` (IN-13) as a CSV download.
- **Runs:** each run's report (OUT-06), spend and errors.
- **The rights log** as a CSV download (SRC-12).
- **The trial board** (TRI-05).
- **API keys:** the list, by label and last use. Keys are made and switched off by command.
- No approvals here: they happen in the library (D-38).

*Verify:* offline, each page renders from a fixture database and has no form that changes data except logging in and out (F-46); on staging, a smoke test logs in and opens the teacher list (F-27).

**OUT-14 · The library API** *fixed* · D-28, D-37, D-44; details *proposed* · C
- The tool serves the API in [../contracts/portraits-api.openapi.json](../contracts/portraits-api.openapi.json), explained in [../contracts/portraits-api.md](../contracts/portraits-api.md). The library adopts it.
- **One library key**, for reading and sending, stored as a hash. It can be switched off or replaced without a deploy.
- **Pull only:** the library reads `/api/v1/changes` on its own schedule.
- **Decisions and requests** come in through their routes (IN-06, IN-07). Resending is safe (IN-08).
- **Files** go out through 15-minute signed links, with each file's SHA-256 in the record.
- Portraits being made, or that failed, never appear. Nothing is removed; a portrait's status says what became of it.
- Within v1, changes are additive only.

*Verify:*
- `check_api.py` passes;
- every route's answers validate against the contract;
- the library's flows run in-process (F-03, F-44, F-45);
- on the deployed app, 401 without the key and 200 with it (F-27).

---

## 7. Running, state and spend

**RUN-01 · Where it runs** *fixed* · D-31, D-36, D-57
- It runs on Railway:
  - a web service (API and admin site);
  - a worker (the queue);
  - a nightly cron job;
  - Postgres;
  - a bucket.
- There are three kinds of environment: production, staging, and one per pull request.
- It is built in **TypeScript on Node 24**, like the library (D-57). See [architecture.md](architecture.md).
- A command-line tool runs steps by hand for the harness and the owner (`railway run`, RUN-05).

**RUN-02 · What a run does, in order** *fixed* · B2, D-44, D-53, D-59
1. The library's requests come first, as they arrive.
2. Then the queued teachers.

**Who is queued:**
- A teacher is queued when they haven't been searched in the last month. That covers:
  - teachers with an open slot (PIP-14, D-53);
  - teachers whose slots are full, but only to look for better copies and higher-ranked photographs (PIP-17, D-59), behind the setting `researchFullTeachers` (on).
- A request queues its teacher at once, whenever they were last searched.

**What a queued teacher gets:** the sources are searched, and only new candidates are tried (PIP-11). Set-aside photographs aren't tried, except as PIP-17 allows. Teachers are processed one at a time.

*Verify:* run scenarios (F-25, F-26).

**RUN-03 · Resumable without paying twice** *fixed* · B2
- Each teacher or request is a job in the database queue. A job survives a crash or redeploy and resumes.
- Every paid step's result is cached. The key is made of:
  - the SHA-256 of the image the step was sent;
  - the step and the model;
  - the step's prompt version;
  - the `try_again` note, if any.

  It does **not** include `recipeVersion` or other settings. So changing the recipe after the trial (TRI-06) doesn't throw away the trial's paid results (argon-14).
- A job stopped part-way resumes without repeating any paid call.

*Verify:* a kill-and-resume test counts stubbed calls (F-04, F-25).

**RUN-04 · Spend caps and ledger** *fixed* · B2, D-54; method *proposed* · C
- One OpenRouter key, the only AI key (D-19). The owner sets a credit limit on it as a backstop (O-4).
- **Caps in production** (D-54):
  - **$100 for the first full run** (D-59). The first full run is the first pass over the list, from the release (F-47) until the queue first empties. Its $100 is a total across the nights it takes, and the night cap doesn't apply during it. If it reaches $100, the rest of the pass carries on from the next night under the regular caps.
  - **After the first pass: $10 a night and $30 a calendar month**, whichever comes first. The first pass's spend doesn't count toward a month.
  - **$2 per teacher per run** (proposed).

  The library's requests count toward the night and the month.
- **The trial** has its own budget of $30 (TRI-07), split into named sub-budgets that the client enforces: $27 for F-28 and $3 for F-29.
- **Other environments** (RUN-10): pull-request copies make no paid calls at all; staging has $2 a night and $10 a month.
- Before each paid call, the client checks that the spend so far, plus the call's estimated maximum, fits under every cap that applies. If it doesn't, the work stops cleanly, finished portraits are published, and the report says so.
- **Each call's actual cost is logged.**
  - Every request asks OpenRouter to report usage (`"usage": {"include": true}`). Where no cost comes back, the settings' estimate is used, marked as estimated.
  - Each line records its environment and its **budget:** `trial`, `trial_examples`, `first_pass` or `regular`. The month cap counts only `regular`.
- **The first pass's state** (`not_started`, `active` or `done`) is stored in the database:
  - F-47 sets it `active` when it switches the schedule on;
  - it becomes `done` when the queue first empties, or when the first pass's spend reaches $100.

*Verify:* stubbed costs cross each cap and sub-budget; no call is made past it, and the report says so (F-17).

**RUN-05 · Commands** *proposed* · C
`portraits <command>`:

- `doctor`: settings, keys present, models and prices, sources reachable. It spends nothing.
- `sync`: the teacher list (IN-12).
- `survey [--teacher ID]`: SRC-14.
- `run [--limit N] [--teacher ID] [--dry-run]`: queue work. A dry run shows the plan and the estimated spend.
- `trial`: TRI-01..TRI-09.
- `keys new|off|list`: the library's keys (RUN-10).
- `password set`: the admin password.
- `status`: the queue, recent runs and spend.

*Verify:* each command has a test (F-22; `trial` in F-28).

**RUN-06 · Offline tests** *proposed* · C
- Every network and model call goes through clients that can be swapped for recorded responses and stubs.
- The whole suite runs with no keys and no network, on PGlite for the database (`plan/build-plan.md` §5).

*Verify:* `npm test` runs with outbound calls refused (F-01).

**RUN-07 · Logs** *proposed* · C
- Logs go to Railway's log stream, and each run is summarised on the admin page.
- They hold no keys (IN-11).

*Verify:* F-26's key scan covers the logs.

**RUN-08 · Schedule** *fixed* · D-53, D-59
- **Nightly, in production,** the cron job:
  - syncs the teacher list;
  - queues the teachers due a search (RUN-02);
  - exits.
- The worker works through the queue. **The library's requests** are queued as they arrive.
- **Each teacher is searched again monthly:** those with an open slot (D-53), and those whose slots are full, for better copies (D-59).
- The schedule is off until the release (F-47) and in every other environment. Staging and pull-request copies run only by hand.

*Verify:* fake-clock scenarios (F-25):
- searched 10 days ago, not queued; searched 35 days ago, queued;
- a full teacher queued only when `researchFullTeachers` is on;
- a request queued at once;
- the cron job exits;
- with the schedule off, nothing is queued.

**RUN-09 · How the owner hears about it** *fixed* · D-53
- **The admin page** shows each run (OUT-06).
- **The library's daily admin email** mentions new portraits waiting. That's the library's side; it's asked for in `handoffs/library-api.md`.
- **Railway's alerts** cover crashes and failed deploys.
- The tool sends no email of its own.

*Verify:* the admin page shows the fixture run's report; a dependency check finds no mail-sending package or SMTP code (F-46).

**RUN-10 · Security** *fixed* · D-55; details *proposed* · C
- **Admin login:** one password, stored in the database only as a slow hash (Argon2 or bcrypt).
  - A secure, HTTP-only, SameSite session lasts 30 days, signed with the session secret (a Railway variable).
  - Attempts are rate-limited, with a short lockout.
  - The password is set by command (`password set`).
- **The library's key:** random, at least 32 bytes, stored as a hash. It is made and switched off by command and shown once.
- **Transport and files:** HTTPS only. The bucket is private; files leave only through 15-minute signed links.
- **Secrets** are Railway variables (IN-11). The OpenRouter key is the same in every environment (D-55).
- **Rate limits:** about 600 API calls a minute per key, plus the login limit.
- **Outbound calls** go only to the adopted sources, OpenRouter and (for the teacher list) GitHub (SRC-01).
- **Environments, since the key is shared** (D-55):
  - **pull-request copies** run in stub mode only: no paid calls, no cron;
  - **staging** has no cron, runs by hand, and spends at most $2 a night and $10 a month;
  - **production** has the caps of RUN-04.
- The environment is read from Railway's `RAILWAY_ENVIRONMENT_NAME`, and its rules come from settings. The key's credit limit (O-4) is the backstop across all of them.

*Verify:*
- a scan of the repo, test logs and sample answers finds no secret;
- wrong passwords lock out;
- a switched-off key gets 401;
- a pull-request environment refuses every paid call, and staging stops at its caps (F-17, F-44, F-46).

---

## 8. The trial

**TRI-01 · The trial comes first** *fixed* · B2
The trial runs before the first full run, which then uses its defaults. Nothing waits for the owner, who can veto (TRI-06).

**TRI-02 · The trial set** *fixed* · B2, D-56; curation *proposed* · C
- The owner's three originals: test inputs only, never published (D-13).
- **About 20 originals picked from the coverage survey** (SRC-14):
  - dot-screened book prints;
  - a tiny original;
  - a group photo;
  - an engraving;
  - a damaged print.
- **Teachers with several photographs,** including copies of one photograph and two sittings of one teacher. These set PIP-20's thresholds on real pairs.
- The set is a fixture file listing each item and its expected outcome (for example "group photo: refused at pre-check"), so the trial doubles as a test.

**TRI-03 · Contenders** *fixed* · D-49, D-56
- The three enhance models of PIP-13, each with the same code.
- Each result is also shown without the blend, at no extra cost.
- There are no outline contenders (D-49).

**TRI-04 · Choosing the winner** *fixed* · B2, D-56
- The draft check (PIP-09) scores every result, and the best model wins.
- If two are within 5% of the best total score, the cheaper wins.

**TRI-05 · The board** *fixed* · B2, D-56; format *proposed* · C
- **A page on the admin site,** readable on a phone and linked from the harness digest for the owner's veto. It shows every result:
  - beside its original, its no-blend version and the examples;
  - with scores and cost per contender.
- Trial drafts are never shown to the library.

**TRI-06 · Defaults come from the trial** *fixed* · B2; mechanism *proposed* · C
- The trial writes the winning model, and any engraving verdict, into `src/config/settings.ts` with a new `recipeVersion`. The harness commits it, with a note in the digest.
- The owner's veto reverses it.
- **The trial runs in production before the release.** Production is deployed with its schedule off and no library key (F-47 switches both on), and trial drafts never appear in the API. So the first full run reuses every cached paid step from the trial, since the cache lives in production's database.

**TRI-07 · Trial budget** *fixed* · B2, D-54
$30, separate from the run caps: $27 for the trial (F-28) and $3 for the examples (F-29), each enforced by the client. The estimate is about $11 (about 23 originals × 3 models, with their checks).

**TRI-08 · The examples are reproduced** *fixed* · B2; measures *proposed* · C
- The output for the owner's three originals passes the draft check's "compare with target" mode against the hand-made portraits.
- **Code measures,** at the owner's framing at 500 px:
  - figure overlap ≥ 0.85;
  - mean tone error ≤ 0.08;
  - dots across 110 ± 2;
  - no STY-06 problems.

  The prototype scores 0.88–0.97 overlap, 0.053–0.071 tone error and 110.5 dots across.

*Verify:* F-29.

**TRI-09 · Trial results are kept apart** *proposed* · C (argon-14)
- **The trial writes only to its own tables** (trial runs and trial items: label, example or not, model, blend used, scores, cost), plus the shared cache and the spend ledger.
- **Its files live under `trial/<trial_run_id>/`** in the bucket.
- **It never creates portraits, candidates or change-feed entries,** so it never uses a portrait id, never appears in the API, and the owner's examples never enter the rights log (D-13).

*Verify:* after a stubbed trial run, the portraits, candidates and changes tables are unchanged (F-28).

---

## 9. Project acceptance ("done when", from B2)

AC-01..AC-03 restate B2's checks for the hosted API (D-58).

| ID | Done when | Checked by |
|---|---|---|
| AC-01 | The teacher sync loads the active rows of `authors.csv`; a row with an unreadable or impossible date is reported with its row; a second sync changes nothing | F-02, F-31 |
| AC-02 | Every published portrait's record validates against the OpenAPI contract, with its files present and checked (all eight, or seven when the AI copy couldn't be made); a record missing its licence is refused, naming the field | F-03, F-24, F-26 |
| AC-03 | The library stub, run against staging, pulls the change feed, fetches portraits and files (SHA-256 checked) and sends one decision and one request of each kind. The next run then: handles the request first; skips a teacher whose slots are full; sets aside a turned-down photograph; publishes a swap | F-05, F-26, F-27 |
| AC-04 | The owner's three examples are reproduced closely enough that the check passes them against the hand-made targets | F-29 (TRI-08) |
| AC-05 | The trial's board exists and the defaults are set from it. One full harness run (plan, build, tests, digest, veto) has completed on this project | F-28, plus the harness's own record |
| AC-06 | Nothing reads the library's scans or reference shelf. Originals come only from the adopted sources (SRC-01), by the match rules of SRC-03 | F-06, F-09, F-10, F-34 |

---

## 10. PORT reconciliation table (to fill in once O-1 arrives)

Rev1's latest planning (which adopted this project's API, D-37) isn't on GitHub yet. Rev1 at 3e444eb (2026-10-18) still has the earlier design, in which the tool pushed to the library. The table is filled from the newer version once it's pushed.

| PORT line | Summary | Requirement(s) here | Difference / question |
|---|---|---|---|
| PORT-001 … 022 | | | |
| PORT-040 | | | |
| PORT-070 … 081 | | | |
| PORT-091 | | | |
| PORT-090 (hand-off; library side) | | OUT-02, OUT-10, OUT-14 | |
