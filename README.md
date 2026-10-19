# Nexus Portraits

A standalone tool that makes stylized portraits of New Thought teachers for the New Thought Nexus library.

For each teacher on the owner's list, the tool:

1. finds a public-domain or openly licensed photograph that certainly shows them (Wikimedia Commons or the Library of Congress only);
2. turns it into a portrait in the owner's halftone style;
3. checks the result;
4. delivers it, with its rights record, to a shared folder.

The library later picks the portrait up from that folder for an admin to approve. Nothing the tool makes goes live by itself.

This is also the first project built end to end by the autonomous build harness (Library-AI readiness gate G10).

**Status:** planning. There is no code yet.

- Agents (Claude, Codex, Gemini, reviewers): start at [CLAUDE.md](CLAUDE.md).
- People: start at [brain/README.md](brain/README.md).
