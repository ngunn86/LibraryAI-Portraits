# GEMINI.md

Every agent working in this repo (Gemini, Codex, Claude or any other) follows **[CLAUDE.md](CLAUDE.md)**. Read it first; it is the single source of working rules for this project.

## When you're a build agent run by the Coding Harness

If your prompt says so, CLAUDE.md's planning rules (reading the notes in order, recording decisions, updating status) don't apply to you. Read what your packet names, and any other file you need; change only the files your card's `Owns` lists (for a test author, the acceptance-test paths in `harness.yaml`); never edit `brain/`, the cards or any other protected path; commit only to the card's branch, and only when your prompt asks; never push or deploy. If a spec or a test looks wrong, stop and explain in `BLOCKED.md`. As a reviewer, you change nothing.
