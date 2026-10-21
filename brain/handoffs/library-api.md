# Hand-off to the library's planning: the portraits API

**From:** Nexus Portraits planning, 2026-10-19 (night). **For:** the Library-AI (Rev1) chat, relayed by the owner.
**Contract:** `brain/contracts/portraits-api.openapi.json` in ngunn86/LibraryAI-Portraits (draft 6, 2026-10-21), with `portraits-api.md` (plain words), `portraits-api.sample.json` and `check_api.py`. Copy them unchanged, with the commit, as you would any outside contract.

## What was decided here that the library needs

| Decision | What it means for the library |
|---|---|
| D-37 | The library adopts this project's OpenAPI file, pulls, and sends decisions back |
| D-38 | Approval and the main portrait are decided in the library's queue and sent back through `POST /api/v1/decisions` |
| D-39 | Every portrait has eight files (seven when the AI copy couldn't be made): the original (byte for byte), a PNG viewing copy, the white version and the black-and-white version (black edge) at 1,000 and 500 px, the AI-enhanced copy and the cut-out mask. Each carries its own licence, credit and SHA-256 |
| D-40 | Up to 3 portraits per teacher, each a different photograph. A better copy of an approved portrait arrives as a new waiting portrait with `replaces` set; approving it is the swap |
| D-41 | No categories. Each portrait has an approximate date and a best-known flag, which the library may correct (`kind: correct`) |
| D-42 | The library keeps its own copy of every file it pulls. The tool's own storage is backed up only through its database |
| D-44 | One key for reading and sending; **the library pulls** the change feed on its own schedule (the tool never calls the library); requests (`try_again`, `another_original`, `try_link`) are handled right away |
| D-61 | When a teacher's three slots are full, a different photograph that clearly ranks above one of them can arrive as a waiting portrait with `replaces` set. Approving it is the swap, as for a better copy |

## What changes on the library's side

Rev1 at commit 3e444eb (2026-10-18) still has the earlier design: the tool pushed to the library. These parts are replaced:

| Rev1 at 3e444eb | Now |
|---|---|
| `POST /api/v2/portraits` (the tool sends one manifest record and the master) | The library reads `GET /api/v1/changes`, then `GET /api/v1/portraits/{id}`, and fetches the files it wants through `/files/{kind}` |
| `GET /api/v2/portraits/requests` (the tool reads Try-again notes from the library) | The library sends `POST /api/v1/requests` |
| The tool's key, `toolKey` (API-063), and the tool reading `GET /api/v2/teachers` | Retired: the tool holds no library key. Teachers come from library-pipeline's `authors.csv`. The library matches the tool's teachers to its people by `wikidata_qid`, `lcnaf_id` (the LoC name id), name and dates (`GET /api/v1/teachers`). `ids_from` and `dates_from` say where those came from |
| `portraits.manifest.schema.json` (one record, one master per teacher) | The portrait record in the OpenAPI file (`Portrait`, `File`, `Source`) |

Unchanged:
- Readers see only an approved stylized portrait, or the blank one.
- Credits go on the Image credits page.

## Statuses worth knowing

- **`replaced`** means superseded by the portrait in `replaced_by` (D-61): a better copy or a higher-ranked photograph you approved in its place, or a newer draft that replaced a waiting one.
- **The main portrait** passes to the replacement on a swap. Turning down the main portrait clears it, and the teacher has none until you set one.
- **A request** answers 202 (`queued`), then becomes `working`, and ends `done` with `result_portrait_id` (always a new portrait) or `refused` with a `refused_reason` code. A `try_again` on a waiting portrait replaces it; on an approved one, the new draft arrives with `replaces` set, and your approval is the swap. A request on a turned-down or replaced portrait answers 409.
- **A `try_link`** can be any of the links an admin copies from a browser: a Commons file page or file link, a LoC item or resource page, or a Wellcome work page (SRC-04).
- **`another_original`** turns the current portrait down (reason `other`) and fills the slot from the next photograph.
- A teacher's `portrait_search.state` can be `skipped`, when the teacher has no Wikidata id, LoC name id or dates. The owner adds them to `authors.csv`.

## Turn-down reasons

`not_this_teacher` and `do_not_use` stop that photograph for good. `quality` and `other` allow one clearly better copy later (PIP-17). The queue's turn-down action should ask which.

Teachers are searched again monthly, even when all three slots are full (D-59). So a better copy of an approved portrait, or a better photograph (D-61), can turn up later as a new waiting portrait with `replaces` set.

## What this project would like back

1. **Push Rev1's latest planning to GitHub**, including `brain/reference/hosting-railway-review.md`, so it can be copied here unchanged (D-36) and the PORT lines reconciled (O-1).
2. **How often the library will read the change feed** (hourly or nightly), for the cost and run planning (T-19).
3. ~~Whether the library still wants the bulk-upload zip~~. **Settled (D-58):** the owner dropped it; the API replaces it.
4. Anything in the contract the library's builders would change. Changes go through this project, because it owns the contract (D-37).
5. **Mention new portraits waiting in the library's daily admin email** (D-53). This tool sends no email of its own; its errors and spend are on its own admin page.
