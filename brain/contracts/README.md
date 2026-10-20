# Contracts

These are the files the tool shares with the owner and with Library-AI. Each contract has one owner, the party that defines it; the others conform to it.

| Contract | File | Defined by | Written by | Read by | Status |
|---|---|---|---|---|---|
| **The portraits API** | [portraits-api.openapi.json](portraits-api.openapi.json), [plain words](portraits-api.md), [samples](portraits-api.sample.json), [check](check_api.py) | This project (D-37) | The tool serves it; the library sends decisions and requests | The library | **Draft 3** (T-08, D-44; 2026-10-20). Replaces the manifest, requests, status and delivery folder below |
| Portrait manifest *(replaced by the API, D-37)* | `portraits.manifest.schema.json` plus its sample | Library-AI---Rev1 | — | — | Not used. Copied into `brain/reference/rev1/` for the PORT reconciliation only (O-1) |
| Manifest validator *(replaced, D-37)* | `validate.py` | Library-AI---Rev1 | — | — | Not used; the API contract check is `check_api.py` |
| Teacher list *(superseded, D-45)* | `teachers.csv` | ([teachers-csv.md](teachers-csv.md), history only) | — | — | Teachers are synced from `authors.csv` into the database (IN-12) |
| Requests *(superseded by the API, D-37, D-44)* | `requests.json` | This project, to be confirmed against Rev1's PORT-060/061 ([requests-and-status.md](requests-and-status.md)) | The library | The tool | Draft (Q-09) |
| Status *(superseded by the API's decisions, D-38, D-44)* | `status.json` | Same as requests | The library | The tool | Draft (Q-09) |
| Delivery folder *(withdrawn, D-42)* | Folder layout and write order ([delivery-folder.md](delivery-folder.md)) | This project, from B2 | The tool; the library writes requests and status | The library | Draft |
| Settings | `src/config/settings.ts` ([../spec/architecture.md](../spec/architecture.md)) | This project | The owner and the harness | The tool | Proposed |

## Rules

- **The API contract is this project's** (D-37). The library adopts it unchanged; changes the library wants come back here.
- **It changes additively within v1:** new optional fields and new routes only. A breaking change is a v2.
- **The contract file is the source.** The app's types and validators follow it, and contract tests check every answer against it (OUT-14, F-03).
- `check_api.py` checks the contract against its samples offline. Run it after any change to either.
