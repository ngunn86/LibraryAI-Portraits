# precheck v1 (PIP-02)

Send: the original (as an image), then this text. Ask for JSON only.

---

You are checking whether this image can be used as the source for a small head-and-shoulders portrait of one specific person. It may be a photograph, or a page or plate from an old book. Answer only with JSON (the comments after // explain the fields; leave them out of your answer), in exactly this shape:

{
  "one_person": true | false,              // exactly one person clearly the subject (others cut off or tiny count as false)
  "face_fully_visible": true | false,      // whole face in frame, not covered, not turned away more than three-quarters
  "face_box": [x0, y0, x1, y1],            // the face, as fractions 0..1 of width and height
  "caption_text": "…" | null,              // any printed caption or facsimile signature under or near the portrait, as written
  "caption_names": "…" | null,             // the person the caption names, if it names one
  "damage": "none" | "light" | "heavy",    // heavy = tears, stains or losses across the face
  "medium": "photograph" | "engraving" | "drawing" | "painting" | "other",
  "printed_dot_pattern": true | false,     // reproduced in print with a visible halftone screen
  "verdict": "pass" | "fail",              // pass only if one_person, face_fully_visible and damage != "heavy"
  "reasons": ["short phrases, empty if pass"]
}
