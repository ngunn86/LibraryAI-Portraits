# note_kind v1 (IN-06)

Send: the library admin's Try-again note, then this text. Ask for JSON only. Model: Claude Haiku (D-52). Stubbed in tests.

---

A library admin asked for a portrait to be made again, with this note. The portrait's crop (framing) and its white outline are made the same way for every teacher, so a note can only change how the photograph is restored (clarity, damage, tone, the face looking wrong or unlike the original). Decide what the note asks for.

Answer only with JSON, in exactly this shape:

{
  "kind": "restoration" | "crop" | "outline" | "other",
  "summary": "the request in a few plain words"
}

"crop" covers framing, zoom, position, head size, cutting off part of the head or shoulders. "outline" covers the white line around the figure. "other" covers anything else, such as "wrong person" or "use a different photo".
