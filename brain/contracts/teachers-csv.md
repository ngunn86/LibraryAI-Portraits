# Contract: `teachers.csv`

The owner supplies the teacher list because the library's people records don't exist yet. The rules come from B2; items marked *proposed* are Claude's (C) and wait for the owner.

## Format

- UTF-8 (a UTF-8 byte-order mark is tolerated), comma-separated, standard CSV quoting.
- The first row is a header. Column order doesn't matter, and unknown extra columns are ignored with a warning.
- One row per teacher.

## Columns

| Column | Required | Rule | Status |
|---|---|---|---|
| `teacher_id` | yes | A stable slug the owner chooses (for example `charles-fillmore`). The library adopts it as the person's id or alias. Must match `^[a-z0-9]+(-[a-z0-9]+)*$`, at most 64 characters, unique in the file | Slug *fixed* (B2); exact pattern and length *proposed* |
| `name` | yes | The name as the library will show it. Not blank | *fixed* |
| `born` | column yes, value may be blank | `YYYY`, `YYYY-MM` or `YYYY-MM-DD`; blank when unknown | *fixed* (B2) |
| `died` | column yes, value may be blank | Same as `born` | *fixed* (B2) |
| `wikidata_qid` | no | Blank, or `^Q[1-9][0-9]*$`. Makes matching certain | *fixed* (B2) |
| `aliases` | no | Other names and spellings, separated by ` \| ` (space, bar, space) | *fixed* (B2) |
| `notes` | no | Free text for the owner. **Never used for matching** (IN-05) | *fixed* (B2) |

## When a row is refused

A refused row is named (row number, `teacher_id`, reason), and the other rows still load (IN-02).

| Reason | Rule | Status |
|---|---|---|
| Bad slug | Fails the pattern or the length limit | *fixed* in principle; pattern *proposed* |
| Missing name | `name` is blank | *proposed* |
| Impossible date | Any of these: not a valid calendar date in an accepted form; death before birth; either date in the future; a lifespan over 120 years | *fixed* in principle; definition *proposed* (Q-12) |
| Malformed Wikidata id | Not blank and fails the pattern | *proposed* |
| Duplicate id | **Every** row sharing a `teacher_id` is refused, because the tool can't tell which one is meant | *proposed* (Q-13) |

Not accepted as dates (*proposed*, Q-12): "c. 1850", "1850?", "1850s" and ranges. Leave the field blank and give a Wikidata id instead.

## When the whole file is refused (IN-03, *proposed*)

The whole file is refused, before any network call, when:

- it isn't UTF-8;
- it has no header;
- a required column (`teacher_id`, `name`, `born`, `died`) is missing;
- it has no valid rows.

## What a row allows (IN-04, SRC-06)

| The row has | Matching allowed |
|---|---|
| `wikidata_qid` | All three rules, after the id's sanity check (a human; years agree where given) |
| Both years, no id | Rule 3. *Proposed:* the tool may also resolve an id itself (SRC-06b), which opens rules 1 and 2 |
| Neither | Skipped and named in the report, "add a Wikidata id" (*proposed*, Q-01) |

## Example

```csv
teacher_id,name,born,died,wikidata_qid,aliases,notes
charles-fillmore,Charles Fillmore,1854,1948,,,"Unity co-founder"
emma-curtis-hopkins,Emma Curtis Hopkins,1849,1925,,"Emma Hopkins",
phineas-quimby,Phineas Parkhurst Quimby,1802,1866,,"P. P. Quimby | Phineas P. Quimby",
```

Wikidata ids are left blank in this example on purpose. Real ids go in the owner's list.

## Where the file lives, and where it comes from (*proposed*, Q-14, D-22)

- `data/teachers.csv` in this repo, so the list is versioned and the harness can see changes. Test fixtures live separately, in `tests/fixtures/`.
- **It is generated, not hand-written:** `portraits teachers sync` builds it from the library-pipeline's `collection/authors.csv`, which is read-only (IN-12). The owner keeps editing one authors list, for the books and the portraits alike.

| authors.csv (pipeline) | teachers.csv (portraits) |
|---|---|
| `name` | `name`, and a `teacher_id` slug made once and then kept (`data/teacher-ids.csv`) |
| `aliases` (`;`-separated) | `aliases` (` \| `-separated) |
| `dates` (`1802-1866`) | `born`, `died` (blank when missing or unreadable; reported) |
| `status` | only `active` rows are taken (Q-26) |
| `stream`, `tier` | `notes` (information only; never used for matching) |
| none | `wikidata_qid`: filled by enrichment (IN-13) or by the owner |

Enrichment results the tool isn't sure of go to `data/teachers-proposed.csv` with their evidence, for the owner to accept.
