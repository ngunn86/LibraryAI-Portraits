# Nexus Portraits

A standalone tool that makes stylized portraits of New Thought teachers for the New Thought Nexus library.

For each teacher on the owner's list, the tool:

1. finds a public-domain or openly licensed portrait that certainly shows them, from a few open collections with reliable rights records (Wikimedia Commons, the Library of Congress, plates in old books on the Internet Archive, and others; see `brain/spec/sources.md`);
2. turns it into a portrait in the owner's halftone style;
3. checks the result;
4. delivers it, with its rights record, to a shared folder.

The library later picks the portrait up from that folder for an admin to approve. Nothing the tool makes goes live by itself.

This is also the first project built end to end by the autonomous build harness (Library-AI readiness gate G10).

**Status:** planning. There is no code yet.

- Agents (Claude, Codex, Gemini, reviewers): start at [CLAUDE.md](CLAUDE.md).
- People: start at [brain/README.md](brain/README.md).
