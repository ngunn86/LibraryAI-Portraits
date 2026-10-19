# CLAUDE.md: Nexus Portraits

Read this first. `AGENTS.md` and `GEMINI.md` point here, so every agent works from the same rules.

## What this project is

Nexus Portraits is a standalone command-line tool. It reads the owner's list of New Thought teachers. For each teacher without an approved portrait it:

- finds a public-domain or openly licensed photograph that certainly shows them (Wikimedia Commons or the Library of Congress only, by three strict match rules);
- turns that photograph into a 1,000 × 1,000 portrait in the owner's halftone style (white dots and a thin white outline on transparency);
- checks the draft;
- delivers it with a full rights record to a shared folder.

Later, the Library-AI library reads that folder and puts each portrait in an admin's approval queue.

The project serves two purposes:

1. It produces the portraits.
2. It is the **first project built end to end by the autonomous build harness**. Library-AI's readiness gate G10 is "one full harness run (plan, build, tests, digest, veto) completed on this project". So the plan is written to be built by agents with little human help.

## Where things stand

**Phase 0: planning.** There is no code yet. Everything lives in `brain/`. Current state, blockers and next steps are in [brain/status.md](brain/status.md).

## Repo map

| Path | What it holds |
|---|---|
| `brain/README.md` | Index of the notes and their conventions (IDs, status words, how to edit) |
| `brain/status.md` | Where planning stands, what's blocked, what's next, session log |
| `brain/brief/` | The owner's briefs, verbatim. v2 (2026-10-19) is current; v1 is superseded and kept for history |
| `brain/spec/requirements.md` | **The normative requirements**, with stable IDs. This is what gets built and tested |
| `brain/spec/architecture.md` | Proposed stack, modules, state store, settings and CLI |
| `brain/contracts/` | File formats shared with the owner and with Library-AI (teacher list, requests, status, delivery folder, manifest) |
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
3. **Library-AI---Rev1 is a separate project and read-only from here.** Never write to it. Anything this project needs from it is copied into `brain/reference/rev1/` unchanged, with the source commit noted.
4. **Keys never go in the repo, chat, logs, reports or the delivery folder.** Keys are read from the environment or from a keys file outside the repo (see `brain/spec/architecture.md`).
5. **Originals come only from Wikimedia Commons and the Library of Congress, by the match rules in `SRC-03`.**
   - The tool never reads Library-AI's scans or the owner's reference shelf.
   - The tool's network client refuses every other host except the configured model APIs.
6. **Testing follows the owner's standard: features work reasonably well and without bugs.**
   - No scientific evaluation and no coverage targets.
   - Tests run offline on fixtures and stubs.
   - Live, paid calls happen only in features marked *live*, under the spend cap.
7. **Notes are edited in place.**
   - When the owner settles something, Claude records it in `brain/decisions.md` (dated) and updates the affected requirement's status.
   - `brain/status.md` is updated at the end of each working session.
8. **Reviewers write in `brain/reviews/` and don't edit the spec directly.** Claude merges accepted points and records the decisions.

## During the build (provisional until the harness's own format is settled; see Q-17)

- Build **one feature at a time**, in the order of `brain/plan/features.md`, and respect each card's *Depends on*.
- A feature is done when every check on its card passes and the whole test suite still passes.
- **Live calls only where the card says *live*, and never past the spend cap in settings.** Stubbed features must not need a key.
- If a feature is stuck, park it only if its card says *Parkable: yes*. Otherwise stop and raise it in the digest.
- Never change a **fixed** requirement to make a check pass. Raise it instead.
