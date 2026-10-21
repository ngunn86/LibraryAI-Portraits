# precheck v2 (PIP-02; v2 adds the age estimate for PIP-18, and drops book plates, D-24)

Send: the candidate's preview (at most 1,600 px, from the source's sized-image service; PIP-21), re-encoded as an 8-bit sRGB PNG, never the original file (PIP-22), then this text. Ask for JSON only. Code turns `face_box` into the original's pixels and checks `minFacePx` itself, since the model doesn't know the picture's size.

---

You are checking whether this image can be used as the source for a small head-and-shoulders portrait of one specific person. It may be a photograph, or an engraving, drawing or painting. Answer only with JSON (the comments after // explain the fields; leave them out of your answer), in exactly this shape:

{
  "one_person": true | false,              // exactly one person clearly the subject (others cut off or tiny count as false)
  "face_fully_visible": true | false,      // whole face in frame, not covered, not turned away more than three-quarters
  "face_box": [x0, y0, x1, y1],            // the face, as fractions 0..1 of width and height
  "caption_text": "…" | null,              // any printed caption or facsimile signature under or near the portrait, as written
  "caption_names": "…" | null,             // the person the caption names, if it names one
  "damage": "none" | "light" | "heavy",    // heavy = tears, stains or losses across the face
  "medium": "photograph" | "engraving" | "drawing" | "painting" | "other",
  "printed_dot_pattern": true | false,     // reproduced in print with a visible halftone screen
  "estimated_age": 0 | null,               // the person's apparent age in years, a whole number; null if you can't judge
  "age_range": [0, 0] | null,              // your plausible low and high for that age
  "verdict": "pass" | "fail",              // pass only if one_person, face_fully_visible and damage != "heavy"
  "reasons": ["short phrases, empty if pass"]
}
