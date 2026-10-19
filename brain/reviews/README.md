# Reviews

Other AI tools review the plan before the build starts. This folder holds their feedback, so it's kept apart from the spec and every point can be traced back.

## For a reviewer

1. Read `CLAUDE.md`, then the files in `brain/` in the order given in `brain/README.md`.
2. Write **one file** named `YYYY-MM-DD-<reviewer>-round-<n>.md` (for example `2026-10-20-codex-round-1.md`).
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

> You are reviewing the plan for a small tool before an autonomous build harness builds it. The repo is LibraryAI-Portraits. Read CLAUDE.md, then brain/README.md, and follow its reading order. Then write your review as instructed in brain/reviews/README.md, in a single new file in brain/reviews/. Don't edit any other file. Focus on contradictions, requirements that can't be verified, features too big for one build step, missing failure cases, rights and licence gaps, and anything that would make an unattended build stall or waste money. Be concrete and cite IDs.
