# Contract: the delivery folder

> **Withdrawn (D-31, D-42, 2026-10-19).** There is no delivery folder. Files live in the tool's bucket (OUT-12), and the library pulls them through the API (OUT-14). This page is kept for its history only.

This is one shared Google Drive folder, laid out so the library's Drive door can read it the same way it reads library-pipeline's deliveries: hourly, taking a file only once its manifest record exists. The layout is *fixed* (B2). The run id format, write order and trial location are *proposed* (C).

## Layout

```
portraits/
  runs/<run-id>/manifest.json                  one manifest per run (the contract; OUT-02)
  runs/<run-id>/masters/<teacher_id>.png       1,000 × 1,000 PNG, white on transparency (STY-06)
  runs/<run-id>/originals/<teacher_id>.jpg     the original, at most 1,600 px on the long side (OUT-05)
  runs/<run-id>/report.md                      plain-words report (OUT-06)
  trial/<run-id>/board.pdf                     the trial board, readable on a phone (TRI-05) [proposed]
  trial/<run-id>/board.html                    the same board in a browser [proposed]
  trial/<run-id>/…                             trial drafts and scores; never read by the library [proposed]
  requests.json                                written by the library; read by the tool (absent at first)
  status.json                                  written by the library; read by the tool (absent at first)
```

- **Run id** (*proposed*): the run's start time in UTC as `YYYYMMDDTHHMMSSZ` (for example `20261102T140000Z`). It sorts by time and is safe in Windows and Drive paths.
- **One run, one folder.** A run never writes into another run's folder, and never deletes or edits earlier runs (OUT-07).

## Write order (OUT-03, *proposed*)

For each portrait:

1. Write `originals/<teacher_id>.jpg`.
2. Write `masters/<teacher_id>.png`.
3. Add the record to `manifest.json`, by writing a temporary file in the same folder and renaming it over the old one.

`report.md` is rewritten at the end of the run, and also when the run stops at the cap or on an error. A run that stops part-way therefore leaves a valid manifest whose files all exist.

**A note for Library-AI's Drive door:** Drive sync doesn't guarantee that files arrive in the order they were written. If a manifest record arrives before its PNG, the door should wait and retry on its next pass, not fail.

## Delivery target (Q-03)

- **Proposed:** `paths.delivery` in settings is a local path to a folder that Google Drive for desktop syncs. On the owner's PC, WSL may need `F:` mounted (for example at `/mnt/f`) to see the Drive letter. No Drive credential and no Drive code are needed.
- **Alternative (B2):** a Drive folder id and a Drive credential, using the Drive API. This is kept as a later option behind the same interface.

## Re-deliveries

A later run's record for the same `teacher_id` replaces the earlier waiting draft. The library handles this by `teacher_id` (OUT-07).
