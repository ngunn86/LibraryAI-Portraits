# Reviews

Other AI tools review the plan before the build starts. This folder holds their feedback, so it's kept apart from the spec and every point can be traced back.

## What to review now (rounds from 2026-10-20)

The plan changed a lot on 2026-10-19 and 2026-10-20. The tool is now:
- a hosted Railway app in TypeScript, like the library;
- serving an API the library pulls from, with up to three portraits per teacher and three versions each.

The owner's decisions (D-24..D-57) are settled. Review how well the plan carries them out:

- [spec/requirements.md](../spec/requirements.md) (consolidated 2026-10-20) against the decisions: anything contradictory, missing or unverifiable;
- [plan/features.md](../plan/features.md): cards too big for one build step, wrong dependencies, checks that can't run offline, live steps without a cap;
- [contracts/portraits-api.openapi.json](../contracts/portraits-api.openapi.json): whether the library could build its side from it alone;
- [spec/architecture.md](../spec/architecture.md): the TypeScript port of the image steps (OpenCV.js) and its fallbacks; the Railway layout;
- rights, licences and credits (SRC-02, SRC-08, SRC-11);
- spend and failure paths: anything that could stall an unattended build or spend money unexpectedly.

The open question is Q-27. The Python prototype in `prototype/` is the reference, not the product.

## For a reviewer

1. Read `CLAUDE.md`, then the files in `brain/` in the order given in `brain/README.md`.
2. Write **one file** named `YYYY-MM-DD-<reviewer>-round-<n>.md` (for example `2026-10-20-codex-round-2.md`). If you can't write to the repo, give the file's full content in your reply, and the owner will add it.
3. **Don't edit any other file.**
4. Number your points: `<reviewer>-<n>` (for example `codex-3`). For each point, give:
   - **Refers to:** the IDs or files concerned (for example `PIP-10`, `F-20`).
   - **Severity:** `blocker` (it can't be built or will be wrong), `major` (likely bugs, rework or wasted spend), `minor` (it would be better) or `nit`.
   - **Problem:** what's wrong or missing, concretely.
   - **Suggestion:** what to change. Quote replacement text where you can.
5. Items marked **fixed** are the owner's. Challenge them only if you see a real conflict or a risk, and say so plainly.
6. Most useful:
   - contradictions between files;
   - requirements that can't be verified;
   - features too large for one harness step;
   - missing failure cases;
   - rights or licence gaps;
   - anything that would make an unattended build stall or spend money.

## For Claude (merging)

- Answer every point in a `## Responses` section added at the end of the review file: *accepted* (with what changed), *declined* (with why) or *for the owner* (added as a Q).
- Owner decisions go in `decisions.md`.

## A prompt the owner can paste into another tool

> You are reviewing the plan for a small hosted app before an autonomous build harness builds it. The repo is https://github.com/ngunn86/LibraryAI-Portraits (public).
>
> 1. Read CLAUDE.md, then brain/README.md, and follow its reading order. Read brain/reviews/README.md for what to focus on in this round.
> 2. Write your review as instructed there: a single new file in brain/reviews/, or its full content in your reply if you can't write to the repo. Don't edit any other file.
> 3. The owner's decisions (brain/decisions.md, D-24..D-57) are settled. Review how well the requirements, feature cards, API contract and architecture carry them out.
> 4. Focus on contradictions, requirements that can't be verified, feature cards too big for one build step, missing failure cases, rights and licence gaps, and anything that would make an unattended build stall or waste money.
> 5. Be concrete and cite IDs (requirements, F-cards, D-numbers).
