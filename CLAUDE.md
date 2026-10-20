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

T-01..T-08, T-10..T-14 and T-16 are decided (D-31..D-50); see the tracker. Spec sections still marked under rework wait for their topics. `brain/spec/architecture.md` still describes the earlier PC-run CLI until T-23.

## Repo map

| Path | What it holds |
|---|---|
| `brain/README.md` | Index of the notes and their conventions (IDs, status words, how to edit) |
| `brain/tracker.md` | **The planning tracker**: every topic to decide, in dependency order, with status and an append-only log |
| `brain/topics/` | Discussion notes for tracker topics that need more than a few lines (for example T-01) |
| `brain/handoffs/` | Documents for the owner's other chats. `harness-throwaway-test.md` is **kept updated** whenever a decision changes what the hosted app needs. `library-api.md` tells the library's planning what to adopt |
| `brain/status.md` | Where planning stands, what's blocked, what's next, session log |
| `brain/brief/` | The owner's briefs, verbatim. v2 (2026-10-19) is current; v1 is superseded and kept for history |
| `brain/spec/requirements.md` | **The normative requirements**, with stable IDs. This is what gets built and tested |
| `brain/spec/architecture.md` | Proposed stack, modules, state store, settings and CLI |
| `brain/spec/sources.md` | Image sources: which to adopt, match rules, rights evidence, the rights log |
| `brain/contracts/` | Contracts shared with the owner and with Library-AI. **The portraits API** (`portraits-api.openapi.json`, owned by this project, D-37) replaces the earlier files (requests, status, delivery folder, manifest) |
| `brain/plan/build-plan.md` | Phases, gates, testing approach, spend plan and risks |
| `brain/plan/features.md` | **Feature cards in build order**: what the harness builds, one at a time, with machine-checkable acceptance checks |
| `brain/decisions.md` | Decision log (D-numbers): what the owner has settled, with dates |
| `brain/open-questions.md` | Open questions (Q-numbers), each with a proposal, waiting for the owner |
| `brain/reviews/` | Feedback from reviewing agents. See its README for the format |
| `brain/reference/rev1/` | *(to come)* Files copied from Library-AI---Rev1, unchanged, with the commit they came from |
| `design/portraits/` | The owner's three hand-made portraits (the style target) and their originals; see its README |

## Rules for every agent

1. **The owner decides.**
   - Items marked **fixed** come from the owner. Don't change them; raise a question instead.
   - Items marked **proposed** are Claude's suggestions waiting for the owner. Reviewers are welcome to challenge them.
   - Items marked **open** point to a question in `brain/open-questions.md`.
2. **IDs are permanent.** Never renumber requirements (`IN-`, `SRC-`, `STY-`, `PIP-`, `OUT-`, `RUN-`, `TRI-`, `AC-`), features (`F-`), decisions (`D-`) or questions (`Q-`). Retire an ID by marking it *withdrawn*, and add new IDs at the end of their group.
3. **Library-AI---Rev1 and library-pipeline are separate projects and read-only from here.** Never write to them. Anything this project needs from Rev1 is copied into `brain/reference/rev1/` unchanged, with the source commit noted. The tool reads library-pipeline's `collection/authors.csv` (IN-12) and nothing else of it.
4. **Keys never go in the repo, chat, logs, reports or the delivery folder.** Keys are read from the environment or from a keys file outside the repo (see `brain/spec/architecture.md`).
5. **Originals come only from the adopted sources in `brain/spec/sources.md`, by the match rules in `SRC-03`.**
   - The tool never reads Library-AI's scans or the owner's reference shelf.
   - The tool's network client refuses every other host except the configured model APIs.
6. **Testing follows the owner's standard: features work reasonably well and without bugs.**
   - No scientific evaluation and no coverage targets.
   - Tests run offline on fixtures and stubs.
   - Live, paid calls happen only in features marked *live*, under the spend cap.
7. **Notes are edited in place.**
   - When the owner settles something, Claude records it in `brain/decisions.md` (dated) and updates the affected requirement's status.
   - `brain/status.md` is updated at the end of each working session.
   - `brain/handoffs/harness-throwaway-test.md` is updated, with a change-log line, whenever a decision changes the hosting, deploys, jobs, data, secrets or integrations.
8. **Reviewers write in `brain/reviews/` and don't edit the spec directly.** Claude merges accepted points and records the decisions.

## During the build (provisional until the harness, designed in a separate chat, settles its format; see D-15)

- Build **one feature at a time**, in the order of `brain/plan/features.md`, and respect each card's *Depends on*.
- A feature is done when every check on its card passes and the whole test suite still passes.
- **Live calls only where the card says *live*, and never past the spend cap in settings.** Stubbed features must not need a key.
- If a feature is stuck, park it only if its card says *Parkable: yes*. Otherwise stop and raise it in the digest.
- Never change a **fixed** requirement to make a check pass. Raise it instead.
