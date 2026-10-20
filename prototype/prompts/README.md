# Prompts (proposed, 2026-10-19; updated 2026-10-20)

Each file's *Send:* line says which image goes to the model. None ever gets the original file: models get 8-bit sRGB PNGs at most 1,600 px (PIP-22).

Starting prompt text for every model step. All of them run through OpenRouter, so the tool needs one key (D-19).

- The harness copies these into `src/models/prompts/`, each with a version number. The version is recorded with every attempt.
- The trial (F-28) tests them on real originals. Any prompt change bumps its version.

| File | Step | Model role | Output |
|---|---|---|---|
| `enhance_keyed.md` | PIP-13 and PIP-03 | Image editing | The original, subtly restored, in black and white, on a flat pure-green background. One call gives both the enhanced copy and the cut-out |
| `cutout_keyed.md` | PIP-03 fallback | Image editing | The original unchanged, on flat pure green. Used when the enhance call fails or is refused, or its cut-out fails PIP-19 |
| `precheck.md` (v2) | PIP-02, PIP-18 | Vision | JSON verdict on the candidate's preview, with medium and an age estimate |
| `draftcheck.md` | PIP-09 | Vision | JSON scores on the draft |
| `compare.md` | TRI-08 | Vision | JSON verdict: draft vs. the owner's hand-made portrait |
| `same_photo.md` | PIP-20 tie-break | Vision | JSON verdict: the same photograph, different ones, or unsure |
| `note_kind.md` (v2) | IN-06 | Text (Haiku) | JSON: what a Try-again note asks for (restoration, crop, outline, other). Cut-out faults count as restoration |
| ~~`outline.md`~~ | *withdrawn* (D-49: the outline is drawn by code) | — | — |

Why a green background rather than transparency: image models don't reliably output transparency. A flat, saturated green is trivial to separate from a black-and-white portrait (`key_mask` in `../recipe.py`). Because the copy and its cut-out come from one image, they line up with each other by construction.
