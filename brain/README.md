# brain/: the project's notes

These notes hold everything the project knows: what to build, why, what's settled and what isn't. They're written so that a person, a reviewing agent and the build harness can all work from them without this chat.

## Reading order

1. [status.md](status.md): where things stand right now.
2. [brief/brief-v2-2026-10-19.md](brief/brief-v2-2026-10-19.md): the owner's brief (the source of truth for intent).
3. [spec/requirements.md](spec/requirements.md): the requirements, with IDs.
4. [plan/build-plan.md](plan/build-plan.md), then [plan/features.md](plan/features.md): how it gets built.
5. [open-questions.md](open-questions.md) and [decisions.md](decisions.md): what's open and what's settled.
6. [contracts/](contracts/README.md) and [spec/architecture.md](spec/architecture.md): formats and structure.

## Conventions

### Status words (used on requirements and contract fields)

| Word | Meaning |
|---|---|
| **fixed** | Settled by the owner (a brief or a decision). Don't change it without the owner. |
| **proposed** | Claude's suggestion, not yet confirmed by the owner. Open to challenge. |
| **open (Q-nn)** | Needs a decision; see that question. |
| **withdrawn** | No longer applies; kept so the ID is never reused. |

### Origins (where a requirement came from)

| Code | Source |
|---|---|
| B2 | Brief, second edition (2026-10-19), the current brief |
| B1 | Brief, first edition (2026-10-17), superseded where B2 differs |
| C | Claude's review (2026-10-17 and 2026-10-19) |
| D-nn | A decision in `decisions.md` |
| PORT-nnn | A `tool`-tagged line of Library-AI---Rev1's `brain/spec/portraits.md`. These are still to be reconciled; see status.md. |

### ID groups

| Prefix | Area | File |
|---|---|---|
| SCOPE | What's in and out | spec/requirements.md |
| IN | Inputs: teacher list, requests, status, examples, settings | spec/requirements.md |
| SRC | Sources, rights, matching, original records | spec/requirements.md |
| STY | The portrait style | spec/requirements.md |
| PIP | The per-teacher pipeline, checks and failure policy | spec/requirements.md |
| OUT | Delivery: folder, manifest, report, zip | spec/requirements.md |
| RUN | Running, state, spend, resume, CLI | spec/requirements.md |
| TRI | The trial | spec/requirements.md |
| AC | Project acceptance (done when) | spec/requirements.md |
| F | Features, in build order | plan/features.md |
| O | Inputs only the owner can supply | plan/build-plan.md |
| R | Risks | plan/build-plan.md |
| D | Decisions | decisions.md |
| Q | Open questions | open-questions.md |

### Editing

- Edit in place. Keep IDs stable (see CLAUDE.md, rule 2).
- When a question is settled:
  1. move the answer to `decisions.md`, with the date and who decided;
  2. mark the question *resolved → D-nn*;
  3. update the requirement's status.
- Reviews go in `reviews/` (see [reviews/README.md](reviews/README.md)), never as direct edits to the spec.
