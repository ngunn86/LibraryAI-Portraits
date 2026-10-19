# draftcheck v1 (PIP-09)

Send, in this order: (1) the original photograph; (2) the draft portrait on the library's dark page colour; (3)–(5) the owner's three example portraits on the same page colour. Then this text. Ask for JSON only. The checker's model family must differ from the image models used on this draft.

---

Image 1 is a historical photograph. Image 2 is a white dot (halftone) portrait made from it. Images 3–5 show the house style the portrait must match.

Judge image 2 on five criteria. Score each from 1 (bad) to 5 (as good as the examples), and give pass or fail (pass means 4 or 5):

1. "outline": one thin, smooth white line just outside the head and shoulders. It follows the hair's overall shape and runs off the bottom edge with the shoulders. There are no gaps, blobs or stray lines.
2. "cutout": no background is left inside the line and no part of the person is cut away (an ear, hair, a shoulder).
3. "texture": the dots are even and round; no moiré, banding, herringbone or blotches.
4. "likeness": the face reads clearly in dots and is recognisably the same person as image 1, with the same features, expression and age. Compare with image 1, not with what the person might be expected to look like.
5. "crop": framed like images 3–5: head near the top, face filling most of the width, shoulders running off the bottom.

Answer only with JSON (the comment after // explains the field; leave it out of your answer):

{
  "outline":  {"score": 1-5, "pass": true|false, "note": "short"},
  "cutout":   {"score": 1-5, "pass": true|false, "note": "short"},
  "texture":  {"score": 1-5, "pass": true|false, "note": "short"},
  "likeness": {"score": 1-5, "pass": true|false, "note": "short"},
  "crop":     {"score": 1-5, "pass": true|false, "note": "short"},
  "pass": true|false,          // true only if all five pass
  "notes": "one or two sentences for the admin"
}
