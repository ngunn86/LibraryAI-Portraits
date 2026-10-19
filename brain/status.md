# Status

**Phase 0: planning.** There is no code yet. Last updated 2026-10-19 by Claude.

## Where things stand

The planning notes now exist. The plan is drafted, but it isn't ready for review rounds yet: three inputs are missing (below), and the questions marked *now* are open.

| Piece | State |
|---|---|
| Briefs | v1 (2026-10-17) and v2 (2026-10-19), in `brief/`. v2 is current |
| Requirements | Drafted with IDs from B2 plus Claude's review. **Not yet reconciled with Rev1's PORT lines** (needs O-1) |
| Architecture | Proposed (Python 3.12, uv, SQLite, one CLI) |
| Contracts | Teacher list, requests and status, and the delivery folder are drafted. The manifest schema waits for O-1 |
| Build plan and features | 29 feature cards across phases 1–6, with checks, dependencies, live/stub, parkable |
| Decisions | D-01..D-16 |
| Open questions | Q-01..Q-20. Still open and marked *now*: Q-09, Q-16 (both need O-1). Resolved: Q-04, Q-10, Q-17, Q-20 |
| Examples | The three targets and their originals are in `design/portraits/`. Test use only (D-13) |
| Reviews | Format ready (`reviews/README.md`). No reviews yet |

## Waiting on the owner (*now*)

1. **O-1:** copy Rev1's `brain/spec/portraits.md`, `brain/contracts/portraits.manifest.schema.json` with its sample, and `validate.py` into `brain/reference/rev1/`, and note the Rev1 commit.
2. The *build* questions, in one pass: Q-01..Q-03, Q-05..Q-08, Q-12, Q-15.

## Next planning steps, in order

1. Reconcile the PORT lines (P0-1), then settle Q-09 and Q-16.
2. Owner answers the *now* and *build* questions (P0-2).
3. Style prototype with the examples (P0-3).
4. Curate the trial set from a first partial teacher list (P0-4, needs O-3).
5. Contract schemas and a sample run (P0-5).
6. Review rounds by other AI tools (P0-6).
7. Freeze plan v1 and hand it to the harness (P0-7).

## Session log

- **2026-10-17:** Brief v1. Claude reviewed it and proposed a stand-in library server, a style prototype first, and a code-drawn outline contender.
- **2026-10-19:** Brief v2: no dependency on the library; input is `teachers.csv`, output a Drive folder.
  - Claude reviewed it: authority match undefined; re-runs could pay twice; deliver through a synced folder.
  - Repo created. The GitHub connection was made, but pushes are refused until the Claude app is installed on the repo.
  - Claude wrote the planning notes: rules, requirements, architecture, contracts, decisions, questions, build plan and feature cards.
- **2026-10-19 (later):** The owner installed the Claude GitHub App; Claude's push to `main` works.
  - The owner's sample portraits arrived (in `Sample Portraits/`, committed on the owner's PC only). Claude moved them to `design/portraits/targets/` and `originals/`, under teacher-id names, and noted their sizes.
  - The targets are 500 px; the originals are small (250–340 px wide).
- **2026-10-19 (later):** The owner answered three questions:
  - the example originals are of unknown source, for evaluating the processing only (D-13);
  - credit metadata must be complete (D-14);
  - the harness is designed in a separate chat (D-15).
  The examples are to be used to evaluate the processing steps, so the style prototype goes ahead (D-16). Claude started the prototype (P0-3).
