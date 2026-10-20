# Decisions

These are settled by the owner. Each entry gives the date, the source and the requirements it touches. Newest decisions go at the bottom, and an entry is never edited: when a decision changes, add a new entry and mark the old one *superseded by D-nn*.

## From the briefs

**D-01 · 2026-10-17 · A standalone tool, and the harness's first test** · B1
The portraits tool is built separately from Library-AI, as its own app in its own repo, and it is the first project the autonomous build harness runs end to end (Library-AI readiness gate G10).

**D-02 · 2026-10-19 · No dependency on the library** · B2 · *supersedes B1's API hand-off* · *input and output superseded by D-22/D-45 (the authors list) and D-31/D-37/D-42 (hosted, with an API); "no dependency on the library" stands (SCOPE-02)*
The tool's input is the owner's `teachers.csv`. Its output is a shared Drive folder. It no longer reads teachers or requests from the library's API, and no longer posts portraits to it. The library reads the folder later. → SCOPE-02, IN-01, OUT-01

**D-03 · 2026-10-17 · Sources and rights** · B1, B2 · *sources widened by D-21 and D-46; the rules stand*
- Originals come from Wikimedia Commons and the Library of Congress only.
- Public domain comes first (public domain, CC0, "no known restrictions"), then CC BY and CC BY-SA. Nothing else, ever.
- Only certain matches count, by three rules in order: the Wikidata image (P18), Commons depicts (P180), and Library of Congress name with dates.
- A full record is kept for every original.

→ SRC-01..10

**D-04 · 2026-10-17 · The style is the owner's and fixed** · B1, B2 · *amended by D-18 (the AI blend), D-39 (the other versions) and D-49 (code outline)*
- A one-colour halftone, made by code: round white dots on a 45° grid, about 110 across, with dark tones transparent.
- One thin, smooth white outline.
- A head-and-shoulders square crop with no background.
- The likeness is never made by an image model.
- One recipe for every teacher, recorded with each portrait.
- A 1,000 × 1,000 PNG, white on transparency.

→ STY-01..07

**D-05 · 2026-10-17 · Starting models** · B1, B2 · *cut-out provider superseded by D-19; outline models superseded by D-49 (code outline); checker by D-52*
- The outline starts with Gemini 3 Pro Image, with GPT Image 2 and FLUX.2 Pro as challengers.
- The draft check uses a vision model from a different family than the outline model.
- The cut-out uses Bria RMBG 2.0 or the like, with a direct fal key if OpenRouter has none.

→ PIP-03, PIP-07, PIP-09

**D-06 · 2026-10-17 · Spending** · B1, B2 · *numbers superseded by D-54*
- The tool has its own OpenRouter key.
- The cap for the first run is $250. The estimates are about 17 cents per attempt, $100 to $200 for the first run over a few hundred teachers, and about $30 for the trial.
- The tool stops at the cap and logs spend per attempt.

→ RUN-04, TRI-07

**D-07 · 2026-10-17 · The trial sits inside the first run, and nothing waits for the owner** · B1, B2 · *contenders superseded by D-49 and D-56 (the three enhance models)*
- The trial uses the owner's three originals plus about 20 found originals (screened prints, a tiny original, a group photo, an engraving, a damaged print).
- The three outline models are compared, and the best one wins (the cheaper one when they're close).
- A board goes to the owner for a veto.

→ TRI-01..08

**D-08 · 2026-10-17 · Failure policy** · B1, B2 · *limits superseded by D-40 and D-51 (6 drafted, 12 pre-checked per teacher per run; three slots)*
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

## The owner's new requirements (2026-10-19, 11:53)

**D-24 · 2026-10-19 · No portraits extracted from books** · owner · *withdraws rule R4 and SRC-13*
"Omit the Internet archive please. It's too much of a hassle to fetch and extract images from books unless it's absolutely necessary."
- The Internet Archive and book plates are dropped, and so are plates in LoC or Wellcome digitised books.
- This can be reopened only if coverage proves it's absolutely necessary.

→ SRC-03, SRC-13, F-33, Q-24

**D-25 · 2026-10-19 · Up to three different portraits per teacher** · owner
"Find and collect / process / categorize multiple different portraits of each teacher if they are available. For popular teachers like Charles Fillmore, we may have up to 3 different portraits."
- The tool must check, visually, that the portraits it keeps are actually different.
- What counts as different, and how it's checked, is tracker topics T-03 and T-16.

→ T-03, T-04, T-16

**D-26 · 2026-10-19 · Three versions of every portrait** · owner
1. The original file.
2. The processed version as designed so far: white halftone dots on transparency, with the white outline.
3. **A black-and-white halftone cropped to the outline:** black and white inside the outline, transparent outside.

The exact definitions are tracker topics T-02 and T-15.

**D-27 · 2026-10-19 · Portraits organised by teacher** · owner
"The app we are building will need to organize these portraits for us by teacher after processing." → T-06

**D-28 · 2026-10-19 · An API for the library** · owner
"We will also need to build API integration so the library can integrate with this tool, and pull the records."
This replaces or extends the file hand-off of B2. Where it runs and what it offers are tracker topics T-01, T-08 and T-09.

**D-29 · 2026-10-19 · Plan the other picture sources, detail them later** · owner · *answers part of Q-23*
"Build a plan to incorporate the other repositories you suggest for picture sources. For now, track that we need to do it. When we get to a formal planning review we will go over what is required in detail."
- Sources to plan: Wikidata/Commons, the Library of Congress, Wellcome Collection, Smithsonian Open Access, NYPL Digital Collections and DPLA (leads).
- The Internet Archive is omitted (D-24).
- The details are tracker topic T-11.

**D-30 · 2026-10-19 · Plan in dependency order, with a tracker** · owner
"Build a detailed plan for all the things we need to review and plan to make this app. We should be making those decisions first that later ones may depend on. Create a tracker that logs everything and tracks it as we go."
`brain/tracker.md` is the planning tracker. Topics are taken in its order.

## T-01: where the app runs (2026-10-19, 12:26)

**D-31 · 2026-10-19 · Fully hosted, with a two-way API** · owner · *T-01*
"Fully hosted yes."
- Processing, the API, the worker, the schedule, the database and file storage all run on a host, not on the owner's PC. The harness still builds on the owner's PC.
- The API serves records and files to the library, and takes the library's approvals and requests back ("you can build the API as you suggest").
- Supersedes the PC-run, Drive-delivered design of B2 (RUN-01, OUT-01..OUT-10, SCOPE-02).

**D-32 · 2026-10-19 · The authors list comes through GitHub** · owner
"Integration with GitHub is best for the authors list." "You can add GitHub integration to the scope."
The hosted app reads `collection/authors.csv` from the private library-pipeline repo through the GitHub API, with a read-only token limited to that repo. → IN-12, T-10, T-21

**D-33 · 2026-10-19 · An admin page to browse** · owner
"Yes, I want an admin page interface to browse."
The app has admin pages for browsing portraits by teacher; what else they show is decided at T-06. → T-06

**D-34 · 2026-10-19 · Extra keys are fine when needed; keep complexity low** · owner · *resolves Q-25*
"I am not opposed to adding other API keys as needed, just trying to keep the complexity to a minimum."
All AI still goes through OpenRouter (D-19). Other services (GitHub, data sources, the host) may have their own keys where needed, kept to a minimum.

**D-35 · 2026-10-19 · The owner can deploy by hand** · owner · *T-27* · *Replit superseded by D-36: the owner's own path is Railway's dashboard or app*
"I am also not opposed to having to deploy myself from Replit. I can access it from my phone if necessary, and the harness is going to keep me updated remotely."
A deploy may be a one-tap step by the owner, announced in the harness digest. Deploys without clicking are a nice-to-have, not a requirement for choosing the host.

## From the library's planning (relayed by the owner, 2026-10-19, 18:10)

**D-36 · 2026-10-19 · Host: Railway** · owner · *closes T-01*
"Take the host decision to Railway and skip the Replit spike; brain/reference/hosting-railway-review.md in Rev1 is written for both projects."
- The app is hosted on Railway. No Replit spike is run.
- Rev1's `brain/reference/hosting-railway-review.md` applies to both projects. It is copied here unchanged, with its commit, once it reaches GitHub.
- The harness's throwaway test (`handoffs/harness-throwaway-test.md`) stays the harness's own test, now on Railway for certain.

→ T-01, T-23, T-27

**D-37 · 2026-10-19 · The library adopts this project's API** · owner (library planning) · *settles T-09's direction*
"The library has adopted its D-28/D-31 API design and the three-portrait scope; the library expects to pull, to send decisions back, and to adopt its OpenAPI file."
- This project defines the API and publishes an OpenAPI file. The library adopts it, pulls records and files, and sends its decisions back.
- The library's earlier plan (a Drive door, and one manifest per run with one portrait per teacher) is replaced on its side.

→ T-08, T-09, OUT-*, Q-09

**D-38 · 2026-10-19 · Approval and the main portrait are decided in the library** · owner (library planning) · *closes T-05*
"Its T-05 (approval, main portrait) is answered on the library's side: approval happens in the library's queue and is reported back."
- Every portrait waits in the library's approval queue. The library reports each decision back to the tool through the API: approved, turned down, chosen as the teacher's main portrait, and requests such as Try again.
- The tool proposes; the library decides.

→ T-05, T-08, T-19, IN-06, IN-07

**D-39 · 2026-10-19 · The versions of a portrait, exactly** · owner · *closes T-02*
Answers to T-02's choices (mock-ups in `prototype/out/versions-board.png`):
1. **Original:** the file is kept exactly as downloaded. Its viewing copy for the admin page and previews is a **PNG**, not a JPEG: "make it PNG please to preserve transparency."
2. **White version:** "1000 px large, and 500px small versions."
3. **Black-and-white version:** **option C, black edge.** The gap and the line are black, so the figure sits on a thin black margin. It is clipped at the line's outer edge, which gives the same footprint as the white version. Same crop as the white version, at 1,000 px and 500 px.
4. **AI working files:** the AI-enhanced copy and the cut-out mask are kept **and offered to the library** through the API.

Claude's proposals carried with this decision (not objected to; the layout is confirmed at T-06):
- the version names;
- the portrait ids `<teacher_id>-<n>`, never reused;
- the viewing copy at most 1,600 px on the long side, never enlarged.

→ T-02, T-06, T-08, T-13, T-15, STY-08, STY-09, OUT-05, OUT-11

**D-40 · 2026-10-19 · Portraits per teacher, and what counts as different** · owner · *closes T-03*
1. **Different means a different photograph:** another sitting, age or pose. Other scans, crops, retouches or prints of the same photograph are **copies**. Only the best copy is kept; the others are logged as copies.
2. **Choosing three when there are more:** the teacher's best-known image (Wikidata's main image, P18) comes first, if it passes. Then come the best-quality photographs, spread across the teacher's life.
3. **A better copy of an approved portrait** is offered to the library as a new draft, marked as a better copy. The approved one stays until the library swaps them.
4. **A turned-down photograph comes back only as a clearly better copy.**

Claude's proposals carried with this decision (marked *proposed* in PIP-14..PIP-17):
- the cap of 3 is a setting (`max_portraits_per_teacher`);
- what counts as "clearly better";
- a turn-down whose reason is "not this teacher" or "don't use this photograph" never comes back.

→ T-03, T-04, T-16, T-19, T-20, PIP-11, PIP-14..PIP-17, SRC-07

**D-41 · 2026-10-19 · No category scheme; the library may correct what's recorded** · owner · *closes T-04*
- Asked which labels each portrait should carry, the owner said: "This kind of detail isn't important for my needs." So there is **no category scheme**: no pose, medium or quality labels for their own sake.
- What D-25 meant by "categorize" is covered by organising the portraits by teacher (D-27).
- A portrait records only what the tool needs anyway:
  - its source (SRC-08);
  - whether it is the best-known image (PIP-16);
  - an **approximate date**, used to spread the three across the teacher's life (PIP-16, D-40). It comes from the source's date, or else from the pre-check's age estimate plus the birth year.
- **Set automatically; the library can correct it.** A correction sent back through the API replaces the tool's value and is never overwritten by a later run.

→ T-04, T-07, T-08, PIP-16, PIP-18

**D-42 · 2026-10-19 · Storage, history, backups and the admin page** · owner · *closes T-06*
1. **Where files live:** in the tool's own bucket on Railway. There is no Google Drive copy. The owner: "Library makes a local copy of all portraits it pulls through the api." So the library keeps its own copy of every portrait it pulls. The API must make that easy (T-08): a listing of what changed since a date, with each file's checksum.
2. **History:** the files of a replaced or turned-down portrait are kept as history, and its status is marked.
3. **Backups:** the database only, at first (Railway's Postgres backups). The bucket can be rebuilt from the rights log. Only the AI copies would cost again, and the library holds its own copies of everything it pulled.
4. **Admin page:** browse and run status, read-only. It shows:
   - portraits by teacher, with all versions, credits and the library's decisions;
   - runs, spend and errors.

   Approvals stay in the library (D-38).

Claude's proposals carried with this decision (not objected to):
- the layout `portraits/<teacher_id>/<portrait_id>/` with the eight files of OUT-11 and a `record.json`, the database being the source of truth;
- candidates that never become a portrait are logged in the rights log, not stored.

→ T-06, T-08, T-19, T-21, T-23, OUT-01, OUT-09, OUT-12, OUT-13

**D-43 · 2026-10-19 · The records, as proposed** · owner · *closes T-07*
The owner reviewed the T-07 proposal (`topics/T-07-records.md`), raised nothing, and moved on to the next step ("Please guide me to the next planning step"). So the proposal stands:
- teacher, candidate (the rights log), portrait, file, library decision, request, run and spend records, and each portrait's history;
- stable ids;
- turn-down reasons;
- library decisions applied once even if sent twice;
- no personal details of the library's admins.

→ T-07, T-08, T-13, T-19

**D-44 · 2026-10-19 · The library API: one key, pull only, requests at once** · owner · *closes T-08*
1. **One key** for the library, for reading and for sending decisions and requests. The owner can switch it off or replace it at any time.
2. **The library checks on its own schedule.** It reads the change feed; the tool never calls the library, and holds no library key.
3. **Requests are handled right away.** The worker picks them up within minutes, and the result shows in the change feed.

Claude's technical choices carried with this decision (OpenAPI draft 1, `contracts/portraits-api.openapi.json`):
- conventions copied from the library's own API;
- resending a decision or request is safe;
- signed 15-minute file links;
- additive changes within v1.

→ T-08, T-09, T-19, T-21, IN-06, IN-07, OUT-14

**D-45 · 2026-10-19 · The teacher list** · owner · *closes T-10; resolves Q-01, Q-26*
1. **Active authors only** (182 today), the same rule as the pipeline. A proposed author gets portraits once the owner makes them active in `authors.csv`.
2. **Missing life dates and Wikidata ids are filled automatically only when two sources agree:** Wikidata and the Library of Congress name authority (id.loc.gov). The rest are listed for the owner with the evidence, as a CSV of suggested additions for `authors.csv`. The tool never writes to library-pipeline.
3. **A teacher with no Wikidata id and no dates after that is skipped** and listed on the admin page. They get no portrait until the owner adds an id or dates to `authors.csv`.

Claude's choices carried with this decision:
- **Teachers and their stable ids live in the app's database.** There is no `data/teachers.csv` in the repo; Q-14 is superseded by D-31.
- **Date forms:** the `authors.csv` forms are read (`YYYY-YYYY`, `d. YYYY`, `b. YYYY`, blank). Any other form is treated as unknown and reported. This resolves Q-12.
- **Clashing ids:** a clashing slug gets a `-2` suffix and is reported. There are no duplicate names today. This resolves Q-13.

→ T-10, T-12, IN-12, IN-13, SRC-06, Q-01, Q-12, Q-13, Q-14, Q-26

**D-46 · 2026-10-19 · Picture sources for the first build** · owner · *closes T-11*
After the formal review (`topics/T-11-picture-sources.md`):
1. **First build: the three keyless sources.**
   - Wikidata with Wikimedia Commons;
   - the Library of Congress (Prints & Photographs);
   - Wellcome Collection;
   - plus the LoC name authority, which identifies teachers (D-45).

   No new keys.
2. **Smithsonian Open Access only if the coverage survey shows gaps.** It needs a free api.data.gov key.
3. **NYPL is dropped.** Its API was retired on 1 August 2026.
4. **DPLA is not used at all.** One less key and one less thing to build.

Claude's proposals carried with this decision:
- a coverage survey early in the build: a live run that searches, downloads nothing and spends nothing on AI;
- polite clients:
  - an identifying User-Agent, which Wikimedia's 2026 limits require;
  - pacing to each source's published limits (the LoC: 20 searches a minute);
  - backing off on 429 or a CAPTCHA page.

→ T-11, T-12, T-13, T-22, SRC-01, SRC-09, SRC-14, sources.md

**D-47 · 2026-10-19 · Match rules settled; any medium, the trial decides** · owner · *closes T-12; resolves Q-11*
- **Engravings, drawings and paintings** are accepted when they pass the pre-check, with the medium recorded. If engravings halftone badly in the trial, one setting (`allowed_media`) turns them off.

Claude's refinements carried with this decision:
- **R3 by catalogue id.** When a LoC or Wellcome record carries the person's LoC name id, and that id is the teacher's (found under D-45), the id alone is the match. Otherwise the name-and-dates rule applies (SRC-05).
- **Pasted links** (`try_link`) may point to any adopted source: Commons, the LoC or Wellcome.
- **SRC-06** follows D-45. A missing Wikidata id is accepted only when Wikidata and the LoC name authority agree; otherwise the teacher is skipped and listed.

→ T-12, SRC-03..SRC-06, PIP-02, Q-11

**D-48 · 2026-10-19 · Licences and credits** · owner · *closes T-13; resolves Q-16*
1. **Stylized portraits made from public-domain or CC0 originals are released as CC0** (public domain dedication). This matches the ministry's mission, and it sidesteps whether a code-made halftone can be copyrighted at all.
2. **Credit lines name New Thought Nexus as the maker:** "Portrait by New Thought Nexus, adapted from: <original credit>".

Claude's rules carried with this decision (`SRC-11`; background, not legal advice):
- The original and its viewing copy keep the original's own licence and credit.
- The adaptations (white and black-and-white versions, the AI copy, the mask) follow the original:
  - **public domain, CC0 or "no known restrictions" → CC0;**
  - **CC BY → CC BY 4.0**, crediting the original's author and licence, marked "adapted from";
  - **CC BY-SA → CC BY-SA 4.0.** ShareAlike requires it; 4.0 is allowed as a later version for 2.0 and up. Anything older is held for the owner.
- Each file records its licence, licence link and credit line.

→ T-13, SRC-11, OUT-11, OUT-14, Q-16

**D-49 · 2026-10-19 · The recipe is the starting point; the outline is drawn by code** · owner · *closes T-14; resolves Q-05*
1. **The board is close enough to build on.** Recipe 0.4.0 (`prototype/recipe.py`, its settings and `prototype/out/`) is the starting point the build reproduces (F-16). The trial may still tune it, under a new `recipe_version` (STY-05).
2. **The outline is drawn by code only,** from the cut-out. It is free and identical every run, and the prototype matches the owner's line (6 px, 2 px out). The image-model outline and its contenders are dropped from the method and from the trial.

Claude's proposal carried with this decision: **cut-out sanity limits** (PIP-19), from the examples' measurements. A draft breaking any of them is refused before the check.

→ T-14, T-22, STY-07, PIP-07, PIP-19, TRI-03, F-20, Q-05

**D-50 · 2026-10-19 · Telling photographs apart; when unsure, the same photograph** · owner · *closes T-16*
- **When even the vision model can't tell** whether two pictures are the same photograph, the tool treats them as the same, and keeps only the better copy.

Claude's method carried with this decision (PIP-20; prototype `prototype/same_photo.py`):
1. **A quick fingerprint** of the cropped face catches exact and near-exact duplicates.
2. **Feature matching:** SIFT points, a ratio test, and RANSAC on a similarity transform, also tried mirrored. At least 40 consistent points means the same photograph; 20 or fewer means different.
   - In the prototype, 30 doctored copies of the three originals scored 56–330: crops, rescans, reprints, blurred, darker, noisy and mirrored.
   - Different photographs scored at most 19.
3. **Between 20 and 40, the vision model decides.** If it is unsure too, they are the same photograph.

Every new candidate is compared with the teacher's other candidates and with all their portraits, turned-down ones included (PIP-17).
- The thresholds are confirmed on real pairs before the build relies on them: two sittings of the same teacher, collected by the coverage survey (SRC-14).

→ T-16, PIP-15, PIP-17, PIP-20, SRC-14

**D-51 · 2026-10-19 · Checks and failures** · owner · *closes T-17; resolves Q-06, Q-07*
1. **One remake with a fresh AI copy.** With the outline drawn by code, the AI-enhanced copy is the only step that can come out differently. A failed draft is remade once with a new copy. A second failure sets the original aside, and the next candidate is tried.
2. **The black-and-white version gets no AI check of its own.** It is made from the same layers as the checked white version, so code checks it (STY-08, STY-09).

Claude's proposals carried with this decision:
- The AI draft check (PIP-09) runs once per draft, on `white-1000`.
- A failure a new AI copy can't change sets the original aside at once: the crop, or a cut-out limit when there was no AI copy.
- Per teacher, per run: at most 6 originals reach drafting (two tries for each of three slots), and at most 12 are pre-checked. Pre-check failures don't count toward the 6.
- Turn-downs arrive through the API (D-44), not `status.json`.

→ T-17, PIP-09..PIP-12, Q-06, Q-07

**D-52 · 2026-10-19 · Checking models** · owner · *closes T-18*
- **Claude Haiku 5.5 for the pre-checks** (`anthropic/claude-haiku-5.5`), the many cheap calls.
- **Claude Sonnet 5.5 for the draft check and the same-photograph tie-break** (`anthropic/claude-sonnet-5.5`), where judgement matters.
- All are called through OpenRouter (D-19). They are a different family from the image models (Google, OpenAI), so the family rule holds.

OpenRouter prices on 2026-10-19:
- Haiku 5.5: $0.10 per million input tokens, $0.50 output;
- Sonnet 5.5: $2 in, $10 out.

`doctor` confirms the ids and prices at build time.

Claude's prompts carried with this decision:
- `same_photo.md` v1 (PIP-20);
- `precheck.md` v2, which adds the age estimate for PIP-18 and drops book plates;
- `outline.md` withdrawn (D-49).

The image model is unchanged: Nano Banana Pro, with Nano Banana 2 and GPT Image 2 as the trial's challengers.

→ T-18, PIP-02, PIP-09, PIP-20

**D-53 · 2026-10-19 · How runs work** · owner · *closes T-19; resolves Q-02, Q-08*
1. **Nightly, with requests at once.**
   - A nightly cron job syncs the teacher list and queues teachers with open slots.
   - The worker works through the queue.
   - The library's requests are queued as they arrive (D-44).
2. **Sources are searched again monthly** for teachers with open slots, so new uploads are picked up within a month.
3. **How the owner hears about it:**
   - the library's daily admin email mentions new portraits waiting (a request to the library's planning);
   - the tool's own errors, spend and runs are on its admin page (OUT-13);
   - Railway alerts on crashes and failed deploys.

   There is no email of the tool's own, and no extra key.
4. **A Try-again note guides a fresh AI copy.**
   - The note goes to the enhance prompt and to the draft check.
   - A note about the crop or the outline can't change one portrait under one recipe (STY-05). The tool answers that it can't, and suggests `another_original`.

Claude's choices carried with this decision:
- a database-backed queue, so a redeploy or crash resumes without paying twice (RUN-03);
- teachers whose three slots are full (approved or waiting) are skipped. The tool knows what's waiting from its own records and the library's decisions (this resolves Q-02);
- run reports live on the admin page.

→ T-19, RUN-01, RUN-02, RUN-08, RUN-09, IN-06, Q-02, Q-08

**D-54 · 2026-10-20 · Spending caps** · owner · *closes T-20; replaces D-06's numbers*
1. **The first full run is capped at $100.** The estimate is $40–80. At the cap the run stops cleanly and carries on the next night.
2. **After that: $30 a month and $10 a night.**
3. **The trial's budget is $30.** The estimate is $5–10, since the trial now compares only the three image models on about ten originals.

Claude's estimate (2026-10-19 prices, AI only; hosting about $8–15 a month on top):
- about $0.17 per portrait, or up to about $0.35 with a remake:
  - an AI copy about $0.14;
  - a Sonnet check about $0.02;
  - Haiku pre-checks a fraction of a cent each;
- then a few dollars in a normal month.

Claude's proposals carried with this decision:
- a per-teacher cap of $2 per run;
- **the owner sets a credit limit on the OpenRouter key itself** as a backstop (owner input O-4).

→ T-20, RUN-04, TRI-07

**D-55 · 2026-10-20 · Security** · owner · *closes T-21*
1. **The admin page uses one password.** It is long, kept in the owner's password manager, stored only as a hash, and gives a 30-day session on the phone. Login attempts are rate-limited.
2. **The same OpenRouter key is used in every environment.**

Claude's choices carried with this decision (RUN-10):
- **Transport and files:** HTTPS only. The bucket is private; files go out through 15-minute signed links.
- **The library's key:** random, at least 32 bytes, stored as a hash, made and switched off by a command, and shown once (D-44).
- **Secrets:** Railway variables per environment, never in the repo, logs or API answers. A test scans for them.
- **Rate limits** on the API and the login.
- **Outbound calls** only to the adopted sources and OpenRouter (SRC-01).
- **Environment caps:** since the key is shared, staging and pull-request copies get their own low caps ($2 a night), and spend is recorded with the environment's name. The key's credit limit (O-4) is the backstop across them all.

→ T-21, RUN-10, IN-11, OUT-13, OUT-14

**D-56 · 2026-10-20 · The trial** · owner · *closes T-22; resolves Q-19*
1. **The checker's scores pick the winning image model, and the owner can veto** (as B2). The run doesn't wait for the owner.
2. **The board also shows each portrait without the AI blend** (the same layers at 0%), so the owner can see what the blend adds. It costs nothing.

Claude's proposals carried with this decision:
- **The trial set:**
  - the owner's three originals, test only (D-13);
  - about 20 originals picked from the coverage survey (SRC-14): dot-screened book prints, a tiny original, a group photo, an engraving and a damaged print;
  - teachers with several photographs, including copies of one photograph and two sittings of one teacher. These set PIP-20's thresholds on real pairs.
- **The contenders** are the three enhance models: Nano Banana Pro, Nano Banana 2 and GPT Image 2.
- **"Close"** means a total score within 5% of the best; the cheaper model then wins.
- **The board** goes on the admin page, and the harness digest links to it for the veto. There is no Drive copy (D-42).
- **Engravings** are turned off by the owner's veto if they look bad on the board (D-47).
- **Cost:** about $11 of the $30 budget (D-54).

→ T-22, TRI-02..TRI-06, PIP-20, Q-19

**D-57 · 2026-10-20 · TypeScript, like the library** · owner · *closes T-23; resolves Q-15*
- Asked whether to build in Python (where the image work is native and the prototype already is) or in TypeScript like Library-AI, **the owner chose TypeScript**. The harness then rehearses the library's exact toolchain.
- **The cost:** the image steps are ported from the Python prototype to OpenCV.js (WebAssembly) and `sharp`. A porting spike comes first, and fallbacks are planned for each known gap.
- The Python prototype stays as the reference implementation. The TypeScript port must reproduce its outputs within tolerances (F-16).

Claude's architecture carried with this decision (`spec/architecture.md` v2, proposed):
- Node 24 LTS, Express, zod, Drizzle with SQL migrations, Postgres and a Postgres-backed queue;
- the Railway bucket through the S3 SDK;
- `sharp` and OpenCV.js; YuNet for faces;
- server-rendered admin pages;
- `node:test`;
- Railway configured as code (`.railway/railway.ts`).

→ T-23, T-24, T-25, RUN-01, RUN-05, RUN-06, F-16, Q-15

## After the consistency pass (2026-10-20)

**D-58 · 2026-10-20 · The bulk-upload zip is dropped; B2's checks restated for the API** · owner · *resolves Q-27*
"To question 27 - yes drop the bulk upload."
- **OUT-08 (the zip) is withdrawn.** The library pulls everything through the API.
- The "yes" is taken as accepting Q-27's proposal as a whole:
  - OUT-10's acceptance check becomes the library pulling from a seeded staging copy and sending one decision of each kind;
  - AC-01..AC-03 are the restated versions in requirements §9.

→ OUT-08, OUT-10, AC-01..AC-03, F-05

**D-59 · 2026-10-20 · Full teachers are searched monthly too; the first-run cap is a total for the first pass** · owner · *resolves Q-28*
"To question 28 - yes."
1. **Teachers whose three slots are full are searched again monthly too,** but only for clearly better copies and higher-ranked photographs (PIP-17). It's a setting (`researchFullTeachers`, on). This reconciles D-40 with D-53.
2. **"$100 for the first full run" (D-54)** is a total for the first pass over the list, from the release until the queue first empties, across the nights it takes.
   - The $10 night cap doesn't apply during it.
   - If $100 is reached, the rest of the pass carries on from the next night under the regular caps.
   - The pass's spend doesn't count toward a month.

→ RUN-02, RUN-04, RUN-08, PIP-17, F-17, F-25, F-47

## From the first outside review (Argon, 2026-10-20)

**D-60 · 2026-10-20 · Optional id columns in the authors list** · owner · *from argon-5*
- The tool reads two optional columns in library-pipeline's `collection/authors.csv`: `wikidata_qid` and `lcnaf_id`.
- The owner adds the ids the tool suggests (IN-13) there; dates go in the existing `dates` column.
- Claude checked that this is safe for library-pipeline: it reads `authors.csv` by column name and rewrites it keeping every existing column (`pipeline/collection.py`, `pipeline/propose.py`).

→ IN-01, IN-02, IN-12, IN-13, F-02, F-31

**D-61 · 2026-10-20 · A full teacher can be offered a higher-ranked different photograph** · owner · *from argon-13; confirms D-59*
- When a teacher's three slots are full and a clearly higher-ranked **different** photograph turns up (for example their best-known image), it is offered with `replaces` set to the portrait it would displace. The library decides.
- So `replaced` now means **"superseded by the portrait in `replaced_by`"**: a better copy or a higher-ranked photograph the library approved in its place, or a newer draft that replaced a waiting one.

→ PIP-16, PIP-17, OUT-07, IN-07, the API contract, F-48

