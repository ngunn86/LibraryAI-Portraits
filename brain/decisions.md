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

**D-05 · 2026-10-17 · Starting models** · B1, B2 · *cut-out provider superseded by D-19*
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

## From the owner, in planning (continued)

**D-13 · 2026-10-19 · The examples are for evaluating the processing only** · owner · *resolves Q-10*
- The source of the three example originals in `design/portraits/` is unknown. The owner supplied them so Claude can work out and test the processing steps.
- They are style targets and test inputs only, and are **never delivered** as portraits.
- Charles Fillmore, Emilie Cady and Ernest Holmes go through normal sourcing like every other teacher.

→ IN-09, TRI-02

**D-14 · 2026-10-19 · The tool keeps everything needed to credit each portrait** · owner
"When you build the portraits tool, you will need to track relevant metadata so we can credit appropriately in the library."
- Every delivered portrait carries the full rights and credit record of its original.
- A record that can't support a proper credit is never delivered.

→ SRC-08, SRC-11, OUT-02, OUT-04

**D-15 · 2026-10-19 · The harness is designed in a separate chat** · owner · *resolves Q-17*
- The owner designs the build harness in another chat.
- This repo's interface to it is the feature-card format in `plan/features.md` and "Working with the harness" in `plan/build-plan.md` §4. Both stay provisional until the harness design fixes its input format.

→ CLAUDE.md, plan/

**D-16 · 2026-10-19 · Prototype the style before the build** · owner · *resolves Q-04*
The owner supplied the examples "so you can evaluate the steps you need to process the image". Claude prototypes the processing steps against them in Phase 0 (P0-3), before the harness builds anything.

→ STY-07, F-16

**D-17 · 2026-10-19 · Descreen book prints with an edge-preserving blur** · owner
"Two of my portraits, Fillmore and Cady, come from books and already have a dot pattern... You need to apply a filter with an edge preserving blur before applying the new halftone texture."
Every original gets an edge-preserving blur before the halftone, stronger with a notch filter when a printed screen is found. → PIP-05, F-13

**D-18 · 2026-10-19 · Adopt the AI-enhanced blend, with safeguards** · owner · *resolves Q-21; amends STY-04*
"So many of the ones we have are bad quality, and applying the halftone filter reduces the quality further. Using a 50% blend with the safeguards you suggest adds detail back into the image, while staying close to the original portrait."
The safeguards are:
- a light-touch prompt;
- align before blending, and refuse the copy if it won't align;
- a 50% blend share, kept as a setting;
- the likeness checked against the original;
- everything recorded;
- the trial compares with and without the blend.

→ PIP-13, STY-04, F-30

**D-19 · 2026-10-19 · All AI through OpenRouter, one key** · owner · *resolves Q-18 (provider)*
"I want the AI accessible from open router so I only have to enter one key."
Every model call (pre-check, enhance, cut-out, draft check, outline contenders) goes through OpenRouter, and there is no fal key. OpenRouter has no dedicated background-removal model, so the cut-out comes from an image-editing model's keyed background (PIP-03). → PIP-03, IN-11, RUN-04, architecture

**D-20 · 2026-10-19 · Claude proposes the prompts** · owner · *resolves Q-22*
The owner's in-between files from months ago no longer exist, and the owner asked Claude to suggest the tools and prompts. The proposals are in `prototype/prompts/` and are tested in the trial. → PIP-02, PIP-03, PIP-09, PIP-13

**D-21 · 2026-10-19 · Look beyond Commons and LoC, with rights tracked** · owner · *widens D-03*
"You will have to suggest sources we can pull the files from automatically. I know about wikimedia commons, but there are others. You will also need to pull the metadata and rights etc with these files, and keep track of them."
Claude proposes the sources, their match rules and the rights evidence in `spec/sources.md`; the owner picks which to adopt (Q-23). Every original considered is kept in a permanent rights log. → SRC-01, SRC-03, SRC-12, SRC-13, AC-06

**D-22 · 2026-10-19 · The teacher list comes from the pipeline's authors list** · owner
The owner pointed to `collection/authors.csv` in library-pipeline ("an authors list ... I am pulling books for the library project"), which Claude reads read-only. The portraits tool takes its teachers from it, so there is one list. The sync and enrichment method is proposed (IN-12, IN-13). → IN-01, IN-12, IN-13, contracts/teachers-csv.md

**D-23 · 2026-10-19 · The edge-preserving blur stays** · owner
"Still do the edge preserving blurring you already committed on the original image etc to prevent weird artifacts from the halftone filter."
It is kept on every original, as in D-17. *Proposed* (C): the AI copy gets the same blur before blending. → PIP-05, PIP-13

