# Contract: `requests.json` and `status.json` (draft)

> **Superseded (D-37, D-38, D-44, 2026-10-19).** The library sends requests and decisions through this project's API (`portraits-api.openapi.json`: `POST /api/v1/requests`, `POST /api/v1/decisions`). There are no `requests.json` or `status.json` files. This page is kept for its history only.

Status: **draft, proposed** by Claude (C) from B2. Both files are written by the library into the delivery folder's root and read by the tool. Rev1's PORT-060 and PORT-061 may already define them. If so, Rev1's definition wins and this page is rewritten to match (Q-09). Until the library exists, these files appear only as test fixtures.

## `requests.json`

The admin's requests from the approval queue. The file is absent on the first run.

```json
{
  "written_at": "2026-11-02T14:00:00Z",
  "requests": [
    {
      "id": "req-0001",
      "teacher_id": "charles-fillmore",
      "kind": "try_again",
      "note": "Outline sits too far from the hair",
      "original": { "source": "commons", "source_id": "File:Example.jpg" },
      "created_at": "2026-11-02T13:55:00Z"
    },
    {
      "id": "req-0002",
      "teacher_id": "emma-curtis-hopkins",
      "kind": "another_original",
      "original": { "source": "loc", "source_id": "2016812345" },
      "created_at": "2026-11-02T13:56:00Z"
    },
    {
      "id": "req-0003",
      "teacher_id": "phineas-quimby",
      "kind": "try_link",
      "link": "https://commons.wikimedia.org/wiki/File:Example2.jpg",
      "created_at": "2026-11-02T13:57:00Z"
    }
  ]
}
```

The ids and links above are illustrations, not real records.

| Field | Required | Meaning |
|---|---|---|
| `id` | yes | Unique and stable; echoed back as the manifest record's `request_id` |
| `teacher_id` | yes | Must be on the list; otherwise the request is skipped and named in the report |
| `kind` | yes | `try_again`, `another_original` or `try_link` |
| `note` | for `try_again`, optional | The admin's words. What a note may change is Q-08 |
| `original` | for `try_again` and `another_original` | The original the request is about (`source` plus `source_id`) |
| `link` | for `try_link` | A Commons file page or a loc.gov item URL (SRC-04) |
| `created_at` | yes | ISO 8601 UTC |

**How a request ends** (*proposed*, IN-08): the tool records the request id when it acts on it, and puts the id in the delivered record's `request_id`. The library removes the request when that record arrives. The tool never acts twice on the same id.

## `status.json`

Each teacher's portrait status, as the library sees it. The file is absent until the library runs; while it's absent, nothing counts as approved.

```json
{
  "written_at": "2026-11-02T14:00:00Z",
  "teachers": {
    "charles-fillmore":    { "status": "approved",    "master_sha256": "…", "updated_at": "2026-11-01T10:00:00Z" },
    "emma-curtis-hopkins": { "status": "turned_down", "original": { "source": "loc", "source_id": "2016812345" }, "reason": "Not her", "updated_at": "…" },
    "phineas-quimby":      { "status": "waiting",     "master_sha256": "…", "updated_at": "…" }
  }
}
```

| `status` | What the tool does |
|---|---|
| `approved` | Skips the teacher (RUN-02) |
| `waiting` | Skips the teacher unless a request names them (RUN-02, *proposed*, Q-02) |
| `turned_down` | Sets the named original aside at once (PIP-11) and tries the next candidate in this run |
| `none`, or teacher absent | Normal processing |
