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
| Decisions | D-01..D-12 |
| Open questions | Q-01..Q-20. The ones marked *now*: Q-04, Q-09, Q-10, Q-16, Q-17, Q-20 |
| Reviews | Format ready (`reviews/README.md`). No reviews yet |

## Waiting on the owner (*now*)

1. **O-1:** copy Rev1's `brain/spec/portraits.md`, `brain/contracts/portraits.manifest.schema.json` with its sample, and `validate.py` into `brain/reference/rev1/`, and note the Rev1 commit.
2. **O-2:** put the three hand-made portraits and their originals in `design/portraits/`, with where each original came from (Q-10).
3. **O-6:** install the Claude GitHub App on this repo, so Claude can push (Q-20).
4. Answers to Q-04 (style prototype first?) and Q-17 (where the harness is planned).

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
