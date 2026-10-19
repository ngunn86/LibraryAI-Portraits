# The owner's examples: the style target

These are the three hand-made portraits that define the style (STY-07), with the originals they were made from. They are used by:

- the style prototype (P0-3);
- the recipe regression test (F-16);
- the trial (TRI-02);
- the "examples reproduced" check (F-29, AC-04).

The owner added them on 2026-10-19 in a folder called `Sample Portraits/`. Claude moved them here and renamed them to their teacher ids, so code and agents never have to handle spaces or brackets in paths. The file bytes are unchanged.

| teacher_id | Target (hand-made) | Original | Owner's file names |
|---|---|---|---|
| `charles-fillmore` | `targets/charles-fillmore.png` | `originals/charles-fillmore.jpg` | `Fillmore_Charles.png`, `Charles_Fillmore_(Unity_Church) (1).jpg` |
| `emilie-cady` | `targets/emilie-cady.png` | `originals/emilie-cady.jpg` | `Cady_Emilie.png`, `H_Emilie_Cady (2).jpg` |
| `ernest-holmes` | `targets/ernest-holmes.png` | `originals/ernest-holmes.webp` | `Holmes_Ernest.png`, `holmes-young (2).webp` |

## Where the originals came from: unknown, so they're never delivered (D-13)

The owner supplied these originals so the processing steps can be worked out and tested. Their sources aren't known, so they are style targets and test inputs only. The tool never delivers them, and Fillmore, Cady and Holmes are sourced normally, like every other teacher.

## What the files are (measured 2026-10-19)

| File | Size | Notes |
|---|---|---|
| `targets/charles-fillmore.png` | 500 × 500, RGBA | About 63% transparent. **Not pure white:** some visible pixels are dark (semi-transparent edge pixels) |
| `targets/emilie-cady.png` | 500 × 501, RGBA | About 64% transparent; pure white |
| `targets/ernest-holmes.png` | 500 × 500, RGBA | About 67% transparent; pure white |
| `originals/charles-fillmore.jpg` | 250 × 350, greyscale | 23 KB |
| `originals/emilie-cady.jpg` | 263 × 378, colour (sepia) | 21 KB |
| `originals/ernest-holmes.webp` | 340 × 496, colour | 12 KB |

## Notes for the prototype (P0-3)

- **The targets are 500 px, and the masters are 1,000 px (STY-06).** Compare at 500 px by downscaling the master. "About 110 dots across" holds at either size.
- **The originals are small:** 250–340 px wide, so the faces are roughly 100–150 px across.
  - The owner's own examples show the style works from originals this small.
  - So `min_face_px` (PIP-02) must be set low enough to accept them, or the tool would refuse originals like the owner's own.
- **Compare by shape (alpha), not colour.** One target has dark edge pixels; the tool's masters must still be pure white (STY-06).
- **What the targets show, by eye:**
  - **Crop:** a tight crop, with the head close to the top edge and the face filling roughly half to two-thirds of the width.
  - **Dots:** highlights merge into near-solid white, and the dark clothing is almost entirely transparent.
  - **Outline:** a thin line a few pixels outside the hair. It follows the hair's overall shape, including Cady's curls as bumps rather than single strands, and runs down the shoulders and off the bottom edge.
- The prototype has now measured all of this (2026-10-19). The numbers and results are in `prototype/README.md`.
