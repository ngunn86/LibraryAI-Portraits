# note_kind v2 (IN-06; v2 counts cut-out faults as restoration, argon-12)

Send: the library admin's Try-again note, then this text. Ask for JSON only. Model: Claude Haiku (D-52). Stubbed in tests.

---

A library admin asked for a portrait to be made again, with this note. A new attempt makes a fresh restored copy of the same photograph, and with it a fresh cut-out of the person from the background. The portrait's framing (zoom and position) and the style of its white outline are the same for every teacher, so a note can't change those. Decide what the note asks for.

Answer only with JSON, in exactly this shape:

{
  "kind": "restoration" | "crop" | "outline" | "other",
  "summary": "the request in a few plain words"
}

"restoration" covers how the photograph is restored (clarity, damage, tone, the face looking wrong or unlike the original) and how the person is cut out: part of the person cut away by the line (an ear, hair, a shoulder), or background left inside the line. These can all change with a fresh attempt.
"crop" covers only changing the framing: zooming in or out, moving the head, making the head bigger or smaller, or showing more or less of the shoulders.
"outline" covers only the style of the white line itself: its thickness, colour or smoothness, or having no line.
"other" covers anything else, such as "wrong person" or "use a different photo".
