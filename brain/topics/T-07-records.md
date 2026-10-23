# T-07 · The records: what we keep

**Status:** accepted as proposed (D-43, 2026-10-19), with the additions below (2026-10-20).
**Tracker:** [T-07](../tracker.md) · **Builds on:** D-14 (complete credits), D-22 (teacher ids), D-38 (the library's decisions come back), D-39 (the files of a portrait), D-40 (photographs and copies), D-41 (approximate date), D-42 (storage, history)

The database (Postgres, a Northflank add-on since D-70) is the source of truth. The API (T-08) exposes these records, and `record.json` in the bucket is a copy of each portrait's (OUT-12). Every id is stable across runs and never reused.

## Additions since D-43 (2026-10-20)

The requirements and the API contract win where this page says less. Since D-43, the records also carry:

- **Teacher:** `lcnaf_id` (IN-13), `ids_from` and `dates_from` (where the ids and years came from: the list, found by the tool, or none), and `key_works` (IN-12, used only to tell apart people who share a name, SRC-06b). The ids can come from the authors list's optional columns (D-60). Also `suggestion` (IN-13): for a teacher whose id or dates the tool couldn't settle, what it suggests adding to `authors.csv` (`name`, `aliases`, `dates`, `wikidata_qid`, `lcnaf_id`) and its evidence; empty otherwise. The admin site lists them and makes the CSV (F-35, F-46).
- **Candidate:** the preview link, its SHA-256, and the original's full width and height from the source (PIP-21); the verdict `held` for CC BY-SA 1.0 (SRC-02, SRC-12).
- **Photograph:** each copy's stored fingerprint (a 64-bit difference hash) and feature points, computed once (PIP-20).
- **Portrait:** `replaces` as in the table below (D-61, PIP-14); `failed` portraits set their candidate aside (OUT-04).
- **Request:** `refused_reason` as one of IN-06's codes.
- **Run and spend:** each spend line's budget (`trial`, `trial_examples`, `first_pass`, `regular`), and `first_pass_state` in the stored settings (RUN-04).
- **Step cache:** keyed on the images sent, the step, the model, the prompt version, the note and the attempt (RUN-03).
- **Trial:** `trial_runs` and `trial_items`, apart from the portraits (TRI-09).

## The records

### Teacher

From library-pipeline's `collection/authors.csv` (IN-12, IN-13), read through GitHub (D-32).

| Field | What |
|---|---|
| `teacher_id` | Stable slug (D-22), e.g. `charles-fillmore` |
| `name`, `aliases` | As in the authors list |
| `born`, `died` | Years, each with where it came from (the list, Wikidata, or both agreeing) |
| `wikidata_qid` | Resolved by the tool, with how it was matched (IN-13) |
| `list_row` | The authors-list row it came from, and the commit it was read at |
| `on_list` | False if the teacher has since left the list. Their portraits are kept, and the API says so |
| `first_seen`, `last_seen` | When the tool first and last saw the teacher on the list |

### Candidate (the rights log, SRC-12)

Every original the tool has considered, whether used or not. Permanent: never deleted.

| Field | What |
|---|---|
| `candidate_id` | Stable: made from the source and the source's own item id |
| `photograph_id` | The photograph this is a copy of (PIP-15). All copies of one photograph share it |
| Source fields | Source, item link, file link, title, creator, date, licence, licence link, credit line (SRC-08, D-14) |
| Match | The match rule and its evidence (SRC-03) |
| File facts | Size in pixels, format, SHA-256 (when downloaded) |
| `precheck` | The pre-check's verdict, reasons, face box, medium, estimated age (PIP-02) |
| `outcome` | Used for a portrait · a copy of one (and which) · failed the pre-check (why) · set aside (why) |
| `first_seen`, `last_checked` | When it was found, and when its source was last checked |

### Portrait

One per photograph the tool turned into a portrait (up to 3 live per teacher, PIP-14).

| Field | What |
|---|---|
| `portrait_id` | `<teacher_id>-<n>`, never reused (OUT-11) |
| `teacher_id`, `photograph_id`, `candidate_id` | Whose it is, which photograph, and which copy was used |
| `status` | `making` · `waiting` (in the library's queue) · `approved` · `turned_down` · `replaced` · `failed` |
| `main` | True if the library chose it as the teacher's main portrait |
| `replaces`, `replaced_by` | `replaces`: set only on an offer in place of an approved portrait (a better copy, a `try_again` remake, or a higher-ranked photograph, D-61; PIP-14). `replaced_by`: set when this portrait is superseded |
| `approx_date` | Value, precision (year, circa, decade) and where it came from: source, estimate or library (PIP-18) |
| `best_known` | Wikidata's main image or a copy of it (PIP-16); set by the tool or corrected by the library |
| `recipe_version`, `settings_hash` | How it was made (STY-05) |
| `checks` | The draft check's verdicts per attempt (PIP-09), and whether the AI copy was used, with its scores (PIP-13) |
| `created`, `updated` | Timestamps |

### File

One per file of a portrait: the eight of OUT-11.

| Field | What |
|---|---|
| `portrait_id`, `kind` | `original`, `original-view`, `white-1000`, `white-500`, `bw-1000`, `bw-500`, `enhanced`, `mask` |
| `key` | Its place in the bucket (OUT-12) |
| `bytes`, `width`, `height`, `format`, `sha256` | File facts; the SHA-256 lets the library check its own copy (D-42) |
| `licence`, `credit` | Each file's own licence and credit line (T-13) |
| `created` | When it was written |

### Library decision

Everything the library sends back through the API (D-38). Append-only.

| Field | What |
|---|---|
| `decision_id` | Given by the library, so a repeated send is recognised and not applied twice |
| `portrait_id` | The portrait it's about |
| `kind` | `approve` · `turn_down` · `set_main` · `correct` (date or best-known flag). Approving a better copy is the swap (refined at T-08) |
| `reason` | For a turn-down: `not_this_teacher` · `do_not_use` · `quality` · `other`, with an optional note (PIP-17) |
| `value` | For a correction: the new value |
| `by` | A label for the library admin who decided, never an email or other personal detail |
| `at`, `received_at` | When it was decided, and when the tool received it |

### Request

The library's asks (IN-06, IN-07), now through the API instead of `requests.json`.

| Field | What |
|---|---|
| `request_id` | Given by the library |
| `teacher_id`, `portrait_id` | Who it's about, and which portrait if any |
| `kind` | `try_again` (with an optional note, Q-08) · `another_original` · `try_link` (a pasted link, checked by the same match rules); IN-06's names |
| `status`, `result` | `queued`, `working`, `done` or `refused` (and why); the portrait it produced |

### Run and spend

| Record | What |
|---|---|
| Run | `run_id`, trigger (schedule, manual or request), start and end, counts, errors, whether it stopped at the cap (OUT-06) |
| Spend | One line per model call: run, teacher, candidate or portrait, step, model, cost (RUN-04) |
| Portrait history | An append-only list of every change to a portrait (status, main, corrections): what, when and by whom (tool or library). This is the history D-42 keeps |

## What isn't kept

- No personal details of the library's admins: only a label (`by`).
- No keys anywhere in the records (IN-11).
- No files for candidates that never became a portrait: their rights-log entry is enough (D-42).

## Left for later topics

- The API's shape and paths, and the OpenAPI file: T-08.
- Each file's licence and credit-line format: T-13.
- The run's order, and when requests are handled: T-19.
