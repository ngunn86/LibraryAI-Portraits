# The portraits API (T-08)

**Status: draft 7 (2026-10-22).**
- Draft 2 added each file's `licence_url` (D-48).
- Draft 3 added the teacher's LoC name id, `lcnaf_id` (IN-13).
- Draft 4 unifies the original's `Source` record with SRC-08: `source`, `source_id`, `licence_tier`, `matched_by`, `matched_to` and `medium`. It also adds `ids_from`, the `skipped` search state, and the health fields, and defines `replaced` and `another_original`.
- Draft 5 merges the first outside review (Argon). No field was added or removed; the rules are stated more exactly:
  - `replaced` now means "superseded by the portrait in `replaced_by`". That can be a different photograph that ranks above one of a full teacher's three, offered with `replaces` (D-61).
  - The main portrait passes to the replacement on a swap, and is cleared when it's turned down.
  - A `correct` decision's `value` must suit its `field`, and a decision can't carry fields of another kind.
  - The change feed's cursor rules, the request life cycle and the accepted link forms for `try_link` are written out.
  - The sample `try_again` now ends with a new portrait (`charles-fillmore-4`).
  - A `try_again` on a waiting portrait replaces it; on an approved one, the new draft is offered with `replaces`. A request on a turned-down or replaced portrait answers 409.
  - `refused_reason` is one of eight codes (`crop_note`, `outline_note`, `licence_refused`, `licence_held`, `precheck_failed`, `draft_failed`, `no_candidates`, `cap_reached`).

- Draft 6 (2026-10-21) makes the health check mean "working" (RUN-12): it adds `database`, `bucket` and `failing`, and answers 503 when something fails. The harness checks it on staging after every merge and rolls staging back if it fails.
- Draft 7 (2026-10-22) adds `environment`, `database_name` and `bucket_name` to the health check (names only, never secrets), so the harness can confirm a pull-request copy isn't using production's data.

Defined by this project and adopted by the library (D-37). The machine contract is [portraits-api.openapi.json](portraits-api.openapi.json) (OpenAPI 3.1). [portraits-api.sample.json](portraits-api.sample.json) holds example payloads, and [check_api.py](check_api.py) checks the two against each other offline.

## In plain words

- **The library pulls** (D-44). It reads the change feed on its own schedule and fetches whatever changed. The tool never calls the library.
- **One key** (D-44), for reading and sending. The owner makes it and can switch it off or replace it; it's stored only as a hash.
- **The library keeps its own copy** of every file it pulls (D-42). Each file carries its SHA-256, so the library fetches only what changed.
- **Decisions come back** (D-38): approve, turn down (with a reason), choose the main portrait, correct a value. Approving a portrait that `replaces` another is the swap; the main portrait passes to it.
- **Requests are handled right away** (D-44): try again, another original, try a link. The answer is 202 (`queued`). The request then becomes `working`, and ends `done` with the new portrait, or `refused` with the reason. Each step appears in the change feed.
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
