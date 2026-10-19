# Decisions

These are settled by the owner. Each entry gives the date, the source and the requirements it touches. Newest decisions go at the bottom, and an entry is never edited: when a decision changes, add a new entry and mark the old one *superseded by D-nn*.

## From the briefs

**D-01 · 2026-10-17 · A standalone tool, and the harness's first test** · B1
The portraits tool is built separately from Library-AI, as its own app in its own repo, and it is the first project the autonomous build harness runs end to end (Library-AI readiness gate G10).

**D-02 · 2026-10-19 · No dependency on the library** · B2 · *supersedes B1's API hand-off*
The tool's input is the owner's `teachers.csv`. Its output is a shared Drive folder. It no longer reads teachers or requests from the library's API, and no longer posts portraits to it. The library reads the folder later. → SCOPE-02, IN-01, OUT-01

**D-03 · 2026-10-17 · Sources and rights** · B1, B2
- Originals come from Wikimedia Commons and the Library of Congress only.
- Public domain comes first (public domain, CC0, "no known restrictions"), then CC BY and CC BY-SA. Nothing else, ever.
- Only certain matches count, by three rules in order: the Wikidata image (P18), Commons depicts (P180), and Library of Congress name with dates.
- A full record is kept for every original.

→ SRC-01..10

**D-04 · 2026-10-17 · The style is the owner's and fixed** · B1, B2
- A one-colour halftone, made by code: round white dots on a 45° grid, about 110 across, with dark tones transparent.
- One thin, smooth white outline.
- A head-and-shoulders square crop with no background.
- The likeness is never made by an image model.
- One recipe for every teacher, recorded with each portrait.
- A 1,000 × 1,000 PNG, white on transparency.

→ STY-01..07

**D-05 · 2026-10-17 · Starting models** · B1, B2
- The outline starts with Gemini 3 Pro Image, with GPT Image 2 and FLUX.2 Pro as challengers.
- The draft check uses a vision model from a different family than the outline model.
- The cut-out uses Bria RMBG 2.0 or the like, with a direct fal key if OpenRouter has none.

→ PIP-03, PIP-07, PIP-09

**D-06 · 2026-10-17 · Spending** · B1, B2
- The tool has its own OpenRouter key.
- The cap for the first run is $250. The estimates are about 17 cents per attempt, $100 to $200 for the first run over a few hundred teachers, and about $30 for the trial.
- The tool stops at the cap and logs spend per attempt.

→ RUN-04, TRI-07

**D-07 · 2026-10-17 · The trial sits inside the first run, and nothing waits for the owner** · B1, B2
- The trial uses the owner's three originals plus about 20 found originals (screened prints, a tiny original, a group photo, an engraving, a damaged print).
- The three outline models are compared, and the best one wins (the cheaper one when they're close).
- A board goes to the owner for a veto.

→ TRI-01..08

**D-08 · 2026-10-17 · Failure policy** · B1, B2
- Two failures set an original aside.
- A turn-down in the library sets it aside at once.
- At most three originals per teacher.
- After that, the teacher keeps the blank portrait until new candidates appear on a later run.

→ PIP-11

## From the owner, in planning

**D-09 · 2026-10-17 · Testing standard** · owner, stated for Library-AI and applied here
"I just need to make sure the features work reasonably well without bugs." There is no scientific evaluation, and the testing scheme stays simple. → build-plan §Testing, CLAUDE.md rule 6

**D-10 · 2026-10-19 · Where the planning lives** · owner
All planning and notes for this project live in this repo (LibraryAI-Portraits). Library-AI---Rev1 is read-only for Claude. → CLAUDE.md rule 3

**D-11 · 2026-10-19 · Planned for the harness, reviewed by other agents first** · owner
The plan is structured so the autonomous build harness can build from it. Other AI tools review the plan before any building starts. → plan/, reviews/

## Context: the owner's standing decisions about the harness

These were settled for the harness project rather than this repo. They are recorded here because this project is the harness's first run and the plan must fit them.

**D-12 · 2026-10 · How the harness works** · owner
- A conductor script guides the build.
- Opus makes the judgment calls and tries to solve stuck features before parking them.
- Claude, OpenAI Codex and Gemini code and check each other's work. An "A" grade means every check passes across several models.
- One feature at a time, with reliability over speed: it's fine to run for days within subscription usage limits.
- No required human checkpoints: the owner gets a digest they can veto, plus notifications and a way to send feedback and new directions from their phone.
- It runs locally on the owner's Windows PC, in WSL, using subscription usage rather than API pricing.

→ plan/build-plan.md §Working with the harness, Q-17
