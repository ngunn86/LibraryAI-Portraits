# Status

**Phase 0: planning.** There is no code yet. Last updated 2026-10-19 by Claude.

**Planning now follows [tracker.md](tracker.md)** (D-30): 27 topics in dependency order. **Now: T-01**, mostly decided: fully hosted, two-way API, authors list through GitHub, an admin page (D-31..D-35). **Picking the host** (`topics/T-01-where-it-runs.md`). Next: T-02.

## Where things stand

The planning notes now exist. The plan is drafted, but it isn't ready for review rounds yet: three inputs are missing (below), and the questions marked *now* are open.

| Piece | State |
|---|---|
| Briefs | v1 (2026-10-17) and v2 (2026-10-19), in `brief/`. v2 is current |
| Requirements | Drafted with IDs from B2 plus Claude's review. **Not yet reconciled with Rev1's PORT lines** (needs O-1) |
| Architecture | Proposed (Python 3.12, uv, SQLite, one CLI) |
| Contracts | Teacher list (now generated from library-pipeline's `authors.csv`, D-22), requests and status, and the delivery folder are drafted. The manifest schema waits for O-1 |
| Sources | Planned (D-29): Wikidata/Commons, LoC, Wellcome, Smithsonian, NYPL, DPLA leads. Internet Archive omitted (D-24). Details at the formal review (tracker T-11) |
| Build plan and features | 35 feature cards across phases 1–6, with checks, dependencies, live/stub, parkable |
| Decisions | D-01..D-35 |
| Open questions | Q-01..Q-26. Still open and marked *now*: Q-09, Q-16 (both need O-1), **Q-23 (which image sources)**. Resolved: Q-04, Q-10, Q-17, Q-18, Q-20, Q-21, Q-22 |
| Examples | The three targets and their originals are in `design/portraits/`. Test use only (D-13) |
| Style prototype | Recipe 0.3.1 (local drift check, blur on the AI copy): descreen (D-17), AI-enhanced blend with the cut-out from its green background (D-18, D-19), and prompts for every model step (D-20). Real AI copies are first tried in F-27 and F-28 |
| Reviews | Format ready (`reviews/README.md`). No reviews yet |

## Waiting on the owner (*now*)

1. **O-1:** copy Rev1's `brain/spec/portraits.md`, `brain/contracts/portraits.manifest.schema.json` with its sample, and `validate.py` into `brain/reference/rev1/`, and note the Rev1 commit.
2. **Tracker topic T-01** (next), then the rest of the tracker in order.
3. The *build* questions, in one pass (each is linked from its tracker topic): Q-01..Q-03, Q-05..Q-08, Q-12, Q-15.

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
- **2026-10-19 (later):** Style prototype (P0-3), recipe 0.1.0.
  - Measured the owner's portraits: 45° grid, 110 cells across, line 6 px with a 2 px gap at 1,000 px, crop by eye-to-mouth distance.
  - Built the recipe in code and reproduced all three: figure overlap 0.88–0.97, tone error 0.05–0.07.
  - The code-drawn line matches the owner's, which supports Q-05.
  - Known gap: the stand-in cut-out is weak on a dark suit against a dark background (Holmes).
  - Fixtures and reference outputs saved for F-16.
- **2026-10-19 (later):** Owner feedback on the board:
  - Fillmore and Cady are book prints with a dot pattern, so descreen with an edge-preserving blur (D-17).
  - The owner's own method blended a subtly AI-enhanced copy at about 50% before the halftone.
  - The owner's AI cut-out did better than the stand-in.
  Recipe 0.2.0 adds descreening: a screen is detected in Fillmore and Cady, not in Holmes, and the texture is cleaner. The enhanced blend is added as PIP-13 and F-30 (align, then blend), pending Q-21, since it changes STY-04. The owner's cut-out tool becomes a trial contender (Q-18, Q-22).
- **2026-10-19 (later):** The owner adopted the AI-enhanced blend with the safeguards (D-18). All AI goes through OpenRouter with one key (D-19). There are no in-between files, so Claude proposes the prompts (D-20).
  - Recipe 0.3.0: one OpenRouter image call per original gives a restored copy on flat green, which supplies both the 50% blend (aligned, in the frame) and the cut-out.
  - Proposed models: Nano Banana Pro to start, with Nano Banana 2 and GPT Image 2 as challengers.
  - Mechanics checked on synthetic copies. Prompts are in `prototype/prompts/`.
- **2026-10-19 (later):** The owner asked how the larger AI copy is aligned. Claude explained, drew `prototype/out/alignment-explainer.png`, and added a local face-drift check (recipe 0.3.1).
  - The edge-preserving blur stays (D-23), and the AI copy now gets it too.
  - Claude read library-pipeline read-only (commit 363aa14). Its `collection/authors.csv` (182 active authors, 71 with dates, no Wikidata ids) becomes the source of `data/teachers.csv`, with stable ids and enrichment (D-22, IN-12, IN-13).
  - Sources widened at the owner's request (D-21). `spec/sources.md` proposes Wikidata/Commons, LoC, Internet Archive book plates (new rule R4: a pre-1931 book by or about the teacher, with a caption naming them) and Wellcome now; Smithsonian, NYPL and DPLA later. It also adds a permanent rights log (SRC-12).
  - New cards F-31 to F-35.
- **2026-10-19 (later):** Owner's new requirements (D-24..D-30):
  - no book extraction (Internet Archive omitted);
  - plan the other picture sources and detail them at the formal review;
  - up to 3 different portraits per teacher, checked visually;
  - three versions (original, white dots, black-and-white clipped to the outline);
  - organised by teacher;
  - an API for the library;
  - plan in dependency order with a tracker.
  Claude created `brain/tracker.md` (T-01..T-26), withdrew R4, SRC-13, F-33 and Q-24, and marked the run-based delivery as under rework. Next: T-01.
- **2026-10-19 (later):** T-01 discussion. The owner leans towards fully hosted, for the harness test. Claude's feasibility review is in `topics/T-01-where-it-runs.md`: feasible, since the AI runs at OpenRouter and the code steps need a small instance; build in layers; a deploy spike picks the host (Replit first, Railway or Render as the fallback). Tracker T-27 added (the harness's deploy duties).
- **2026-10-19 (later):** T-01 decisions D-31..D-35:
  - fully hosted, with a two-way API;
  - the authors list through GitHub (read-only token);
  - an admin page;
  - extra keys are fine, kept to a minimum;
  - the owner can deploy by hand from Replit (phone).

  Host options beyond Replit compared against ten requirements (Railway, Render, DigitalOcean, Cloud Run). Recommendation: Replit (the Rev1 rehearsal), or Railway for automatic deploys and staging.
