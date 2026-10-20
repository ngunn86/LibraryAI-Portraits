# Status

**Phase 0: planning.** There is no code yet. Last updated 2026-10-19 by Claude.

**Planning now follows [tracker.md](tracker.md)** (D-30): 27 topics in dependency order. **T-01 decided:** fully hosted on Railway, two-way API (D-31..D-36). **T-05 decided** in the library (D-38). **T-09 mostly decided:** this project owns the OpenAPI contract (D-37). **T-02 decided** (D-39): the original and a PNG viewing copy; white and black-and-white (black edge) versions at 1,000 and 500 px; AI files offered to the library. **T-03 decided** (D-40): up to 3 different photographs, best-known first, then spread across life; better copies offered to the library. **T-04 decided** (D-41): no category scheme; an approximate date for the spread, correctable by the library. **Now: T-06, storage and organisation by teacher.** Throwaway test requirements for the harness: `handoffs/harness-throwaway-test.md` (kept updated).

## Where things stand

The planning notes now exist. The plan is drafted, but it isn't ready for review rounds yet: three inputs are missing (below), and the questions marked *now* are open.

| Piece | State |
|---|---|
| Briefs | v1 (2026-10-17) and v2 (2026-10-19), in `brief/`. v2 is current |
| Requirements | Drafted with IDs from B2 plus Claude's review. **Not yet reconciled with Rev1's PORT lines** (needs O-1) |
| Architecture | Being rewritten: hosted on Railway (web, worker, cron, Postgres, bucket); the old CLI and SQLite proposal is superseded in part (rewrite at T-23) |
| Contracts | Teacher list (now generated from library-pipeline's `authors.csv`, D-22), requests and status, and the delivery folder are drafted. The manifest schema waits for O-1 |
| Sources | Planned (D-29): Wikidata/Commons, LoC, Wellcome, Smithsonian, NYPL, DPLA leads. Internet Archive omitted (D-24). Details at the formal review (tracker T-11) |
| Build plan and features | 35 feature cards across phases 1–6, with checks, dependencies, live/stub, parkable |
| Decisions | D-01..D-41 |
| Open questions | Q-01..Q-26. Still open and marked *now*: Q-16 (needs O-1). Resolved: Q-04, Q-10, Q-17, Q-18, Q-20, Q-21, Q-22, Q-23, Q-25. Superseded: Q-03, Q-09 |
| Examples | The three targets and their originals are in `design/portraits/`. Test use only (D-13) |
| Style prototype | Recipe 0.4.0 adds the black-and-white version (option C) and the 500 px copies (D-39). Recipe 0.3.1 added the local drift check and the blur on the AI copy: descreen (D-17), AI-enhanced blend with the cut-out from its green background (D-18, D-19), and prompts for every model step (D-20). Real AI copies are first tried in F-27 and F-28 |
| Reviews | Format ready (`reviews/README.md`). No reviews yet |

## Waiting on the owner (*now*)

1. **O-1:** copy Rev1's `brain/spec/portraits.md`, `brain/contracts/portraits.manifest.schema.json` with its sample, and `validate.py` into `brain/reference/rev1/`, and note the Rev1 commit. Rev1 is now readable here through GitHub, so Claude can copy them once the latest Rev1 work is pushed, including `brain/reference/hosting-railway-review.md`.
2. **Tracker topic T-06** (now), then the rest of the tracker in order.
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
- **2026-10-19 (later):** Railway explored in depth (notes in T-01). The owner may move Library-AI there too. Claude wrote `handoffs/harness-throwaway-test.md` (HT-01..HT-29), the throwaway hosted app the harness must build, deploy, test and tear down before feature work, and will keep it updated. The owner is checking Railway in the other chat.
- **2026-10-19 (evening):** Relayed from the library's planning:
  - host Railway, Replit spike skipped (D-36);
  - the library adopts this project's API, OpenAPI file and three-portrait scope (D-37);
  - approval and the main portrait are decided in the library and reported back (D-38).

  T-01 and T-05 closed, T-09 mostly decided, Q-09 superseded. Rev1's shared hosting review isn't on GitHub yet (latest Rev1 commit 2026-10-18), so it's copied once pushed. Next: T-02.
- **2026-10-19 (evening):** T-02 opened. Mock-ups of the black-and-white version's edge (A white line, B no line, C black edge) on light, dark and coloured pages. Proposals in `topics/T-02-three-versions.md`: original byte for byte plus a viewing copy; the white version at 1,000 px only; the black-and-white version as option A; version names; working files kept internally.
- **2026-10-19 (evening):** **T-02 decided** (D-39).
  - Black-and-white version: option C, black edge.
  - Original: kept byte for byte, with a PNG viewing copy.
  - The white and black-and-white versions come at 1,000 and 500 px.
  - The AI-enhanced copy and the cut-out mask are offered to the library.

  Recipe 0.4.0 makes them, and the outputs are in `prototype/out/versions/`. STY-08, STY-09 and OUT-11 added, OUT-05 amended, T-15 mostly decided. Next: T-03.
- **2026-10-19 (evening):** **T-03 decided** (D-40).
  - A different portrait means a different photograph; only the best copy of a photograph is kept.
  - Which three: the best-known image (Wikidata P18) first, then the best quality spread across life.
  - A better copy of an approved portrait is offered to the library.
  - A turned-down photograph returns only as a clearly better copy.

  PIP-14..PIP-17 added. Next: T-04.
- **2026-10-19 (evening):** **T-04 decided** (D-41): no category scheme. Only an approximate date is kept, to spread the three across life, and the library can correct it. PIP-18 added. Next: T-06.

