# The portraits API (T-08)

**Status: draft 4 (2026-10-20).**
- Draft 2 added each file's `licence_url` (D-48).
- Draft 3 added the teacher's LoC name id, `lcnaf_id` (IN-13).
- Draft 4 unifies the original's `Source` record with SRC-08: `source`, `source_id`, `licence_tier`, `matched_by`, `matched_to` and `medium`. It also adds `ids_from`, the `skipped` search state, and the health fields, and defines `replaced` and `another_original`. Defined by this project and adopted by the library (D-37). The machine contract is [portraits-api.openapi.json](portraits-api.openapi.json) (OpenAPI 3.1). [portraits-api.sample.json](portraits-api.sample.json) holds example payloads, and [check_api.py](check_api.py) checks the two against each other offline.

## In plain words

- **The library pulls** (D-44). It reads the change feed on its own schedule and fetches whatever changed. The tool never calls the library.
- **One key** (D-44), for reading and sending. The owner makes it and can switch it off or replace it; it's stored only as a hash.
- **The library keeps its own copy** of every file it pulls (D-42). Each file carries its SHA-256, so the library fetches only what changed.
- **Decisions come back** (D-38): approve, turn down (with a reason), choose the main portrait, correct a value. Approving a better copy is the swap.
- **Requests are handled right away** (D-44): try again, another original, try a link. The answer is 202, and the result appears in the change feed.
- Portraits still being made, or that failed, are never shown. Nothing is ever removed: a portrait's status says what became of it.

## Routes

| Route | What |
|---|---|
| `GET /api/v1/health` | Is it up (no key) |
| `GET /api/v1/teachers` | All teachers, with portrait counts, the main portrait and where the search stands |
| `GET /api/v1/teachers/{teacher_id}` | One teacher and their portraits |
| `GET /api/v1/portraits` | Portraits, by teacher or status |
| `GET /api/v1/portraits/{portrait_id}` | One portrait: status, date, best-known flag, the original's source and rights, and its files (eight, or seven without an AI copy) with checksums, licences and credits |
| `GET /api/v1/portraits/{portrait_id}/files/{kind}` | Redirects to a 15-minute signed download of one file |
| `GET /api/v1/portraits/{portrait_id}/history` | Everything that happened to it |
| `GET /api/v1/changes` | What changed since a time or cursor (kept 30 days) |
| `POST /api/v1/decisions` | Approve, turn down, set main, correct |
| `POST /api/v1/requests` · `GET /api/v1/requests[/{id}]` | Ask for work on a teacher, and follow it. Accepted with 202; an unknown teacher gets 404 and a bad link 422 |

## Conventions (Claude's choices)

They copy the library's own API (Rev1 `brain/contracts/api.openapi.json` at 3e444eb), so its builders meet the same patterns:
- bearer keys;
- the `Error` object with the same kinds (`key_off`, `out_of_scope`, `not_found`, `invalid`, `cursor_too_old`, `rate_limited`), plus `conflict` for a decision that can't apply;
- the change feed's `since` / `after` / `next_cursor` / `more`.

Further conventions:
- **Resending is safe.** Ids given by the library (`decision_id`, `request_id`) make a repeated call harmless.
- **Changes are additive.** Within v1 they are additive only, and readers ignore fields they don't know.
- **Request bodies are strict.** An unknown field (an email, say) is refused.
