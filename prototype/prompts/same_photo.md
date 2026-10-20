# same_photo v1 (PIP-20, tie-break)

Send: picture A, then picture B (both as images, each at about 800 px on the long side), then this text. Ask for JSON only. Used only when feature matching is between the two thresholds (PIP-20). If the answer is "unsure", the tool treats them as the same photograph (D-50).

---

You are comparing two old pictures of the same person. Decide whether they come from **the same original photograph** (or the same painting or engraving), or from **two different ones**.

The same original photograph can look very different after: cropping, rescanning, reprinting in a book or newspaper (with a dot pattern), retouching, colouring, fading, mirroring, or a change of contrast or size. These are still the same photograph.

Different photographs are different sittings or moments: the head is turned differently, the expression, hair, clothes or lighting differ, or the person is a different age. Two photographs taken minutes apart at the same sitting, with a slightly different pose, are **different**.

Look closely at small details that a copy keeps and a new photograph changes: the exact shape of the hair line, creases in the clothing, the position of a collar or tie, the catch-lights in the eyes, the shadow under the chin.

Answer only with JSON (leave out the comments), in exactly this shape:

{
  "verdict": "same" | "different" | "unsure",
  "evidence": ["short phrases naming the details you compared"],
  "differences_that_survive_copying": ["details that differ in a way no copy, crop or retouch would cause; empty if none"]
}
