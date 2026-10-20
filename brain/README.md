# brain/: the project's notes

These notes hold everything the project knows: what to build, why, what's settled and what isn't. They're written so that a person, a reviewing agent and the build harness can all work from them without this chat.

## Reading order

1. [status.md](status.md): where things stand right now.
2. [tracker.md](tracker.md): every planning topic, in the order we decided them, and where each stands.
3. [brief/brief-v2-2026-10-19.md](brief/brief-v2-2026-10-19.md): the owner's brief. Decisions D-24 onwards extend and in places replace it (for example, hosting and the API).
4. [spec/requirements.md](spec/requirements.md): the requirements, with IDs. This is what gets built.
5. [spec/architecture.md](spec/architecture.md) and [contracts/portraits-api.openapi.json](contracts/portraits-api.openapi.json): the structure and the API.
6. [plan/build-plan.md](plan/build-plan.md), then [plan/features.md](plan/features.md): how it gets built.
7. [decisions.md](decisions.md) and [open-questions.md](open-questions.md): what's settled and what's open.
8. [topics/](topics/) for the longer discussions (hosting, versions, records, sources).

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
| C | Claude's proposals (2026-10-17 onwards) |
| D-nn | A decision in `decisions.md` |
| PORT-nnn | A `tool`-tagged line of Library-AI---Rev1's portrait spec, still to be reconciled (requirements §10) |

### ID groups

| Prefix | Area | File |
|---|---|---|
| SCOPE | What's in and out | spec/requirements.md |
| IN | Inputs: the teacher list, the library's requests and decisions, examples, settings, keys | spec/requirements.md |
| SRC | Sources, rights, matching, original records | spec/requirements.md |
| STY | The portrait style | spec/requirements.md |
| PIP | The per-teacher pipeline, checks and failure policy | spec/requirements.md |
| OUT | Output: the portrait's files and record, storage, the admin site, the API | spec/requirements.md |
| RUN | Running: hosting, schedule, queue, spend, commands, security | spec/requirements.md |
| TRI | The trial | spec/requirements.md |
| AC | Project acceptance (done when) | spec/requirements.md |
| F | Features, in build order | plan/features.md |
| O | Inputs only the owner can supply | plan/build-plan.md |
| R | Risks | plan/build-plan.md |
| D | Decisions | decisions.md |
| Q | Open questions | open-questions.md |
| T | Planning topics | tracker.md |
| HT | The harness's throwaway-test requirements | handoffs/harness-throwaway-test.md |

### Editing

- Edit in place. Keep IDs stable (see CLAUDE.md, rule 2).
- When a question is settled:
  1. move the answer to `decisions.md`, with the date and who decided;
  2. mark the question *resolved → D-nn*;
  3. update the requirement's status.
- Reviews go in `reviews/` (see [reviews/README.md](reviews/README.md)), never as direct edits to the spec.
