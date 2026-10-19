# T-02 · The three versions of a portrait, exactly

**Status: decided (2026-10-19, D-39).** The owner's answers:

| Item | Claude proposed | Owner decided |
|---|---|---|
| Black-and-white edge | A, white line | **C, black edge** |
| Original | exact file + JPEG viewing copy | exact file + **PNG** viewing copy ("to preserve transparency") |
| Sizes | 1,000 px only | **1,000 px and 500 px** |
| AI working files | kept, internal | kept **and offered to the library** |

Names and ids stay Claude's proposals, confirmed at T-06. What follows is the discussion as it was put to the owner.
**Tracker:** [T-02](../tracker.md) · **Decided so far:** D-26 (the three versions)
**Pictures:** `prototype/out/versions-board.png` (all options on a light, a dark and a coloured page) and `prototype/out/versions-zoom.png` (the edge, enlarged). Made by `prototype/versions.py` from the recipe 0.3.1 outputs.

## What D-26 says

1. The original file.
2. The processed version as designed so far: white halftone dots on transparency, with the white outline.
3. A black-and-white halftone cropped to the outline: black and white inside the outline, transparent outside.

## What the mock-ups show

- **The white version needs a dark page.** On a light page it almost disappears (board, first column). That is presumably why the black-and-white version is wanted: it works on any page.
- **Inside the outline there is only one possible picture.** It is white where the white version has dots and black everywhere else. "White dots on black" and "black dots on white" give the same pixels with a round-dot screen: in the shadows you see white dots, in the highlights black ones. So the black-and-white version needs no new screen or tone settings.
- **The only real choice is the edge.** Three options were drawn:

| Option | Edge | On a light page | On a dark page |
|---|---|---|---|
| **A · White line** | The white version's 2 px gap (now black) and 6 px white line; clipped at the line's outer edge | Clean black edge; the white line shows only on a page that isn't white | Looks like the white version, filled in |
| **B · No line** | Clipped at the figure's own edge | Dots run right to the edge, so the edge looks ragged where it's light (hair, collar) | Same ragged edge; dark clothes merge into the page |
| **C · Black edge** | The gap and the line are both black: an 8 px black margin round the figure | Smooth, crisp black silhouette, like a printed cut-out | The margin merges into the page; looks like B with a smooth edge |

- D-26's words "black and white **in the outline**" fit A and C, which are clipped at the outline. B drops the outline altogether.
- File sizes at 1,000 × 1,000 px: white 144–156 KB; black-and-white 155–174 KB. Storage is negligible.

## Proposals

### 1. Original

- **Proposed:** keep the file exactly as downloaded, byte for byte, in its own format (JPEG, TIFF, PNG…). Its SHA-256 goes in the rights record (SRC-12). It is never re-encoded.
- **Proposed:** also make a **viewing copy**: JPEG, sRGB, long side at most 1,600 px. The admin page and the library use it for previews. Library of Congress masters are often TIFFs of tens of MB, too heavy for a phone.

### 2. White version

- **Proposed:** as designed. 1,000 × 1,000 PNG, 8-bit RGBA; every visible pixel pure white; the outline is part of the image (STY-01..STY-07).
- **Proposed:** **no other sizes.** The library scales down as needed; 1,000 px is sharp at 500 CSS px on a high-density screen.

### 3. Black-and-white version

- **Proposed: option A (white line).**
  - It is exactly the white version on a black ground, cut at the outline's outer edge. Both versions then have the same silhouette, the same line and the same footprint, so the library can swap one for the other without moving anything.
  - It works on light, dark and coloured pages.
  - Option C is the second choice, if a print-like black edge on light pages matters more than matching the white version.
- **Proposed:**
  - same crop and size as the white version, pixel-aligned (1,000 × 1,000);
  - PNG, 8-bit RGBA;
  - visible pixels are black or white, with grey only where the edges of dots, line and figure are smoothed (as in the white version);
  - transparent outside the outline.
- The style details (and any later tuning of this version) are T-15.

### 4. Names and formats

- **Proposed:**
  - each portrait gets an id: `<teacher_id>-<n>` (for example `charles-fillmore-1`). `n` counts up in the order portraits are found and is never reused, even if a portrait is turned down;
  - storage keys: `portraits/<teacher_id>/<portrait_id>/<version>.<ext>`;
  - versions: `original.<ext as downloaded>`, `original-view.jpg`, `white.png`, `bw.png`;
  - download name for people: `Charles Fillmore - portrait 1 - white.png`.
- How storage is organised by teacher is settled at T-06, and the API paths at T-08. This only fixes the version names.

### 5. Working files (new item)

- **Proposed:** also keep, for each portrait, the AI-enhanced copy (PIP-13) and the cut-out mask. They are internal, not a fourth version, and the library doesn't get them by default.
- Reasons:
  - the admin page can show what the AI changed;
  - a re-run with a new recipe needn't pay for the AI call again;
  - the rights record can point to them when it says AI-assisted restoration was used (T-13).

## What was built after the decision

- Recipe 0.4.0 makes the versions: `bw_version` (option C), `small` (500 px), and `check_bw`. The white master is unchanged.
- The chosen versions for the three examples are in `prototype/out/versions/<teacher>/` (`white-1000`, `white-500`, `bw-1000`, `bw-500`). File sizes: 87–171 KB each.
- Requirements: STY-08, STY-09 and OUT-11 added; OUT-05 amended.

## Affects

STY-01..STY-07 (a new STY requirement for the black-and-white version), OUT-*, T-06 (organisation), T-08 (API), T-13 (each version's licence and credit), T-15 (style details), F-16 (reference outputs).
