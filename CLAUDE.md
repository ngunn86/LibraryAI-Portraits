# CLAUDE.md: Nexus Portraits

Read this first. `AGENTS.md` and `GEMINI.md` point here, so every agent works from the same rules.

## What this project is

Nexus Portraits is a standalone hosted app on Railway (D-31, D-36). It reads the owner's list of New Thought teachers (library-pipeline's `authors.csv`, through GitHub). For each teacher it:

- finds up to 3 different public-domain or openly licensed photographs that certainly show them, from the adopted sources by strict match rules (`brain/spec/sources.md`);
- turns each into portraits in the owner's halftone style:
  - white dots and a thin white outline on transparency;
  - a black-and-white version with a black edge;
  - both at 1,000 and 500 px;
- checks the drafts;
- keeps each portrait, by teacher, with its original and a full rights record.

The Library-AI library pulls the portraits through this app's API (`brain/contracts/portraits-api.openapi.json`). It puts each one in an admin's approval queue and sends its decisions back (D-37, D-38).

The project serves two purposes:

1. It produces the portraits.
2. It is the **first project built end to end by the autonomous build harness**. Library-AI's readiness gate G10 is "one full harness run (plan, build, tests, digest, veto) completed on this project". So the plan is written to be built by agents with little human help.

## Where things stand

**Phase 0: planning.** There is no code yet. Everything lives in `brain/`. Planning follows [brain/tracker.md](brain/tracker.md) topic by topic; the current state is in [brain/status.md](brain/status.md).

**Owner's requirements of 2026-10-19 (D-24..D-30)** are being planned through the tracker:

- up to 3 different portraits per teacher;
- three versions of each (original, white dots, black-and-white);
- organised by teacher;
- an API for the library;
- no extraction from books.

T-01..T-08, T-10..T-14 and T-16..T-23 are decided (D-31..D-61); see the tracker. The requirements were consolidated on 2026-10-20, and no questions are open. The first outside review (Argon) is merged. The plan is being adapted to the Coding Harness (D-62..D-68, `harness.yaml`): a sample of cards is in format 1, and the rest follow once the harness chat has checked the sample. The app is built in **TypeScript on Node 24**, like the library (D-57); `brain/spec/architecture.md` v2 describes it, and `prototype/` (Python, recipe 0.5.0) is the reference implementation of the recipe.

## Repo map

| Path | What it holds |
|---|---|
| `brain/README.md` | Index of the notes and their conventions (IDs, status words, how to edit) |
| `brain/tracker.md` | **The planning tracker**: every topic to decide, in dependency order, with status and an append-only log |
| `brain/topics/` | Discussion notes for tracker topics that need more than a few lines (for example T-01) |
| `brain/handoffs/` | Documents for the owner's other chats. `harness-throwaway-test.md` is **kept updated** whenever a decision changes what the hosted app needs. `library-api.md` tells the library's planning what to adopt. `harness-questions.md` answers the harness chat's instructions and asks its questions |
| `brain/status.md` | Where planning stands, what's blocked, what's next, session log |
| `brain/brief/` | The owner's briefs, verbatim. v2 (2026-10-19) is current; v1 is superseded and kept for history |
| `brain/spec/requirements.md` | **The normative requirements**, with stable IDs. This is what gets built and tested |
| `brain/spec/architecture.md` | The hosted app (v2): TypeScript stack, Railway layout, modules, database, settings, secrets, porting risks |
| `brain/spec/sources.md` | Image sources: which to adopt, match rules, rights evidence, the rights log |
| `brain/contracts/` | Contracts shared with the owner and with Library-AI. **The portraits API** (`portraits-api.openapi.json`, owned by this project, D-37) replaces the earlier files (requests, status, delivery folder, manifest) |
| `brain/plan/build-plan.md` | Phases, gates, testing approach, spend plan and risks |
| `brain/plan/features.md` | **Feature cards in build order**: what the harness builds, one at a time, with machine-checkable acceptance checks |
| `brain/decisions.md` | Decision log (D-numbers): what the owner has settled, with dates |
| `brain/open-questions.md` | Open questions (Q-numbers), each with a proposal, waiting for the owner |
| `brain/reviews/` | Feedback from reviewing agents. See its README for the format |
| `brain/reference/rev1/` | *(to come)* Files copied from Library-AI---Rev1, unchanged, with the commit they came from |
| `design/portraits/` | The owner's three hand-made portraits (the style target) and their originals; see its README |
| `prototype/` | The Python reference recipe, its fixtures and outputs, the prompts, and `parity/` (per-operation references for the TypeScript port) |
| `models/` | The YuNet face detector (MIT), committed so the build and tests never download it; see its README |
| `harness.yaml` | The Coding Harness's settings for this project (format 1): cards, protected paths, commands, limits, deploys |
| `Coding Harness Instructions.md` | What the harness requires of this project, from the harness chat (it updates this file; D-65) |
| `brain/plan/release-checklist.md` | The owner's steps around the release |
| `brain/rulings.md`, `brain/gotchas/` | Written by the harness during the build: the Tech Lead's rulings (never owner decisions) and gotchas about the code |

## When you're a build agent run by the Coding Harness

If your prompt says you're a build agent, this file's planning rules (reading the notes in order, recording decisions, updating status) don't apply to you (D-65):
- read what your packet names, and any other file you need;
- change only the files your card's `Owns` lists. Never edit `brain/`, the cards or any other protected path in `harness.yaml`;
- commit only to the card's branch, and only when your prompt asks; never push or deploy;
- if a spec or a test looks wrong, stop and explain in `BLOCKED.md`. The Tech Lead rules, or asks the owner.

The rest of this file (the rules below, and the build section at the end) still applies.

## Rules for every agent

1. **The owner decides.**
   - Items marked **fixed** come from the owner. Don't change them; raise a question instead (a build agent writes `BLOCKED.md`).
   - Items marked **proposed** are Claude's suggestions waiting for the owner. Reviewers are welcome to challenge them.
   - Items marked **open** point to a question in `brain/open-questions.md`.
2. **IDs are permanent.** Never renumber requirements (`IN-`, `SRC-`, `STY-`, `PIP-`, `OUT-`, `RUN-`, `TRI-`, `AC-`), features (`F-`), decisions (`D-`) or questions (`Q-`). Retire an ID by marking it *withdrawn*, and add new IDs at the end of their group.
3. **Library-AI---Rev1 and library-pipeline are separate projects and read-only from here.** Never write to them. Anything this project needs from Rev1 is copied into `brain/reference/rev1/` unchanged, with the source commit noted. The tool reads library-pipeline's `collection/authors.csv` (IN-12) and nothing else of it.
4. **Keys never go in the repo, chat, logs, reports or API answers.** Keys are Railway variables, read from the environment (see `brain/spec/architecture.md`, RUN-10).
5. **Originals come only from the adopted sources in `brain/spec/sources.md`, by the match rules in `SRC-03`.**
   - The tool never reads Library-AI's scans or the owner's reference shelf.
   - The tool's network client refuses every other host except the configured model API (OpenRouter) and GitHub for the teacher list (SRC-01).
6. **Testing follows the owner's standard: features work reasonably well and without bugs.**
   - No scientific evaluation and no coverage targets.
   - Tests run offline on fixtures and stubs.
   - Live, paid calls happen only in checks marked *live*, on cards whose side effects allow them, under the spend cap.
7. **Notes are edited in place.**
   - When the owner settles something, Claude records it in `brain/decisions.md` (dated) and updates the affected requirement's status.
   - `brain/status.md` is updated at the end of each working session.
   - `brain/handoffs/harness-throwaway-test.md` is updated, with a change-log line, whenever a decision changes the hosting, deploys, jobs, data, secrets or integrations.
8. **Reviewers write in `brain/reviews/` and don't edit the spec directly.** Claude merges accepted points and records the decisions.

## During the build (the Coding Harness, format 1; `harness.yaml`, D-65)

- The harness builds **one card at a time**, in the order of `brain/plan/features.md`, once every card in its *Depends on* is merged. Each card's acceptance tests are written first, by Codex, and locked.
- A card is done when every blocking check on it passes, both reviews pass and the whole suite still passes, for one commit. It then merges at once (D-62), with its evidence on the control issue (D-63).
- **Paid calls only in checks marked *live*, on cards whose side effects allow them, and never past the spend cap.** Stubbed cards must not need a key.
- If a card is stuck, it's parked only if it says *Parkable: yes*. Otherwise the build stops and alerts the owner on the control issue.
- Never change a **fixed** requirement, the API contract or the style rules to make a check pass. A build agent writes `BLOCKED.md` instead.
