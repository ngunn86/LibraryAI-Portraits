# Contracts

These are the files the tool shares with the owner and with Library-AI. Each contract has one owner, the party that defines it; the others conform to it.

| Contract | File | Defined by | Written by | Read by | Status |
|---|---|---|---|---|---|
| Portrait manifest | `portraits.manifest.schema.json` plus its sample | Library-AI---Rev1 (copied here unchanged) | The tool | The library, the receiver stub | **Waiting for the copy (O-1).** Lands in `brain/reference/rev1/`, then `portraits/contracts/schemas/` |
| Manifest validator | `validate.py` | Library-AI---Rev1 (copied here unchanged) | n/a | The tool's tests | **Waiting for the copy (O-1)** |
| Teacher list | `teachers.csv` | This project ([teachers-csv.md](teachers-csv.md)) | The owner | The tool | Draft; parts proposed |
| Requests | `requests.json` | This project, to be confirmed against Rev1's PORT-060/061 ([requests-and-status.md](requests-and-status.md)) | The library | The tool | Draft (Q-09) |
| Status | `status.json` | Same as requests | The library | The tool | Draft (Q-09) |
| Delivery folder | Folder layout and write order ([delivery-folder.md](delivery-folder.md)) | This project, from B2 | The tool; the library writes requests and status | The library | Draft |
| Settings | `settings.toml` ([../spec/architecture.md](../spec/architecture.md)) | This project | The owner and the harness | The tool | Proposed |

## Rules

- **The manifest schema is used unchanged** (B2). If this project needs something the schema lacks (for example, the portrait's own licence, SRC-11 and Q-16), it is raised for Rev1 to decide. It is never added here on our own.
- **Every contract gets a JSON Schema** (or, for the CSV, a validator) in `portraits/contracts/schemas/`, plus fixtures in `tests/fixtures/`. These are built in features F-02 and F-03.
- Contracts this project defines are offered to Rev1 for adoption. The library's acceptance check is importing this project's sample run unchanged (OUT-10).
