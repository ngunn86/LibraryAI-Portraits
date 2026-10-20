# Open questions

Each question waits for the owner and carries Claude's proposal. **The order we take them in is set by the [planning tracker](tracker.md)**: each question belongs to a tracker topic. When one is settled it is marked *resolved → D-nn*, the answer goes into [decisions.md](decisions.md), and the affected requirements are updated.

**Priority:**

| Priority | Meaning |
|---|---|
| **now** | Planning can't finish without it |
| **build** | Needed before the harness starts |
| **trial** | Needed before the trial |
| **later** | Can wait |

## Summary

| Q | Question | Priority | Proposal in one line | Status |
|---|---|---|---|---|
| Q-01 | What is an "authority match"? | — | — | resolved → D-45 (two sources must agree: Wikidata and the LoC name authority; otherwise skip and list) |
| Q-02 | Re-runs: skip teachers whose draft is already waiting? | build | Yes, using the tool's own delivery record until `status.json` exists | open |
| Q-03 | Deliver through a synced folder or the Drive API? | — | — | superseded by D-31 (hosted app; the library pulls through the API; storage is T-06) |
| Q-04 | Prove the style in planning, before the harness builds? | — | Yes: prototype the recipe here against the three examples | resolved → D-16 |
| Q-05 | Add a code-drawn outline as a fourth trial contender? | build | Yes, and make it the default: the prototype shows it reproduces the owner's line | open |
| Q-06 | What does "remake" mean when most steps are deterministic? | build | Re-run only the steps that can change; otherwise set aside | open |
| Q-07 | Do pre-check rejections count toward the three originals? | build | No, but cap pre-checks at 8 per teacher per run | open |
| Q-08 | What can a Try-again note change? | build | It guides a fresh attempt and the check; it never changes recipe settings | open |
| Q-09 | Who defines `requests.json` and `status.json`? | — | — | superseded by D-37 (decisions come back through this project's API, defined in its OpenAPI file) |
| Q-10 | Where did the owner's three originals come from, and are those teachers delivered? | — | Use them as style targets only | resolved → D-13 (source unknown; never delivered) |
| Q-11 | Are engravings and drawings acceptable originals? | — | — | resolved → D-47 (yes; the trial decides, and a setting can turn them off) |
| Q-12 | How are dates validated? | — | — | resolved → D-45 (the `authors.csv` forms; anything else is unknown and reported) |
| Q-13 | What happens to duplicate `teacher_id`s? | — | — | resolved → D-45 (a clashing slug gets `-2` and is reported) |
| Q-14 | Where does `teachers.csv` live? | — | — | superseded by D-31, D-45 (teachers live in the app's database, synced from `authors.csv`) |
| Q-15 | Which stack? | build | Python 3.12 + uv, in WSL | open |
| Q-16 | Does the manifest carry the portrait's own licence (CC BY-SA share-alike)? | **now** | Check the schema; if it's missing, raise it with Rev1 | open |
| Q-17 | Where is the harness planned and built, and what format does it read? | — | Its own repo; this repo supplies feature cards in a fixed format | resolved → D-15 (a separate chat; format provisional) |
| Q-18 | Which cut-out provider? | — | An OpenRouter image model, with the cut-out from the enhanced copy's keyed background | resolved → D-19 (method proposed in PIP-03) |
| Q-19 | In the trial, what counts as "close"? | trial | Total score within 5% of the best | open |
| Q-20 | Can Claude push to this repo? | — | Install the Claude GitHub App on this repo | resolved 2026-10-19 (app installed; push works) |
| Q-21 | Adopt the owner's AI-enhanced blend, which changes STY-04's "no image model on the likeness"? | — | Yes, with safeguards | resolved → D-18 |
| Q-22 | Which AI tools and prompts did the owner use, and are the in-between files still available? | — | Claude proposes them | resolved → D-20 (no files; prompts in `prototype/prompts/`) |
| Q-23 | Which image sources to adopt? | — | — | resolved → D-24 (no Internet Archive) and D-29 (plan the others; details at the formal review, tracker T-11) |
| Q-24 | Accept uncaptioned portraits at the front of a teacher's own book? | — | — | withdrawn (D-24: no book plates) |
| Q-25 | Free data keys (Smithsonian, NYPL, DPLA) later, if coverage is low? | — | — | resolved → D-34 (keys are fine where needed, kept to a minimum) |
| Q-26 | Which authors become teachers: `active` only, or `proposed` too? | — | — | resolved → D-45 (`active` only) |

---

## Details

### Q-01 · What is an "authority match"? · resolved → D-45
- **Background.** B2 says a teacher with neither a Wikidata id nor both years "can still be searched, but only an authority match (below) counts". Nothing below defines one.
  - Rules 1 and 2 need a Wikidata id.
  - Rule 3 needs both years.
  - So such a teacher has no rule that can match.
- **Proposal (SRC-06):**
  - **(a)** Check every given id: the item must be a human, and its years must agree with the list's.
  - **(b)** With both years and no id, the tool may resolve the id itself, but only when exactly one human on Wikidata matches the name or an alias and both years. The resolved id is reported for the owner to add to the list.
  - **(c)** With neither an id nor both years, skip the teacher and name them in the report.
- **Alternative.** "Authority" could mean a Library of Congress name authority record (id.loc.gov), which also carries dates. That adds a third service for little gain, since Wikidata items usually link to it anyway.

### Q-02 · Re-runs before the library exists · build
- **Background.** Until the library writes `status.json`, nothing counts as approved. Read literally, a second run would remake and pay again for every teacher it already delivered.
- **Proposal.** The tool keeps its own delivery record and skips any teacher with a draft waiting, unless a request names them. Once `status.json` exists, its `waiting` status takes over.

### Q-03 · Synced folder or Drive API · superseded by D-31
- **Background.** B2 gives a Drive folder id plus a Drive credential. But Google Drive for desktop is already installed on the owner's PC.
- **Proposal.** The delivery target is a folder path that Drive for desktop syncs:
  - no credential and no Drive code;
  - it works on any machine with Drive for desktop;
  - WSL may need a one-line mount of the Drive letter.

  The API stays a later option behind the same interface.
- **Cost of the alternative.** OAuth or service-account setup, a credential to keep safe, and upload code with retries.

### Q-04 · Prove the style before the harness builds it · resolved → D-16
- **Background.** Matching the three hand-made portraits is open-ended tuning judged by eye. That is the hardest kind of task for an unattended harness, and a poor first test of one.
- **Proposal.** In Phase 0, in this chat, Claude prototypes the code recipe (crop, descreen, halftone, code outline) against the three examples and their originals, side by side, until the owner says it's close. The output is:
  - starting settings (`recipe_version` 0.1.0);
  - a reference output for each example;
  - the code metrics' thresholds (TRI-08).

  The harness then builds the machinery around a recipe that is already known to work, and F-16 locks it in with a regression test.
- **Needs:** O-2 (the examples and their originals).

### Q-05 · A code-drawn outline as a fourth contender · build
- **Background.** The cut-out already gives the figure's exact shape. Widening and smoothing that mask, then tracing its edge, gives a line that:
  - sits exactly on the dots;
  - costs nothing;
  - comes out the same every run.

  Image models tend to shift the figure slightly when they redraw it, so a model-drawn line needs an alignment step to sit on the halftone.
- **Proposal.** Add the code method as a fourth contender (PIP-07, TRI-03). Nothing in the style changes; only the drawing method could. The trial rule decides: the best wins, the cheaper when close.
  - If code wins, most of the roughly 17 cents per attempt goes away.
  - If code wins, the "different family" rule for the checker becomes moot.
- **Evidence from the prototype (2026-10-19).** The owner's line is exactly what code produces: a 6 px band 2 px outside a smoothed silhouette, with the dots clipped to the same silhouette. The code line reproduces it on all three examples (`prototype/out/board.png`).
- **Updated proposal.** Make the code line the default (recipe 0.1.0). Keep the three image-model lines as trial contenders, to confirm or overturn that.

### Q-06 · What "remake" means · build
- **Background.** If code draws the outline, every step except the cut-out and the checks is deterministic. Remaking a failed draft with the same inputs gives the same draft, and asking the checker again until it says yes would just be gaming it.
- **Proposal (PIP-10).**
  - A remake re-runs only the steps that can come out differently: a new image-model outline, or the cut-out from another provider if one is configured.
  - When the failing criterion is one code would only repeat (likeness, damage, moiré, crop, or anything under the code outline), the original is set aside after one failure.

### Q-07 · Pre-check rejections and the three-original limit · build
- **Background.** The pre-check costs very little. Group photos and tiny originals are common, so counting them toward the three originals would leave many teachers blank for no good reason.
- **Proposal.** Pre-check rejections don't count toward the three. There is a separate cap of 8 pre-checks per teacher per run, to bound spend.

### Q-08 · What a Try-again note can change · build
- **Background.** The recipe is one set of settings for every teacher (STY-05), so an admin's note such as "crop lower" can't change settings for one teacher.
- **Proposal.**
  - A note triggers a fresh attempt: a new model outline, or the next cut-out provider.
  - It is passed to the outline model's prompt and to the checker as an extra criterion, and it is quoted in the report.
  - If the code outline wins the trial, a Try-again on the same original can only re-cut. In that case the tool says so in the report and suggests "Find another original".
- **Alternative.** Allow a small, recorded set of per-teacher adjustments, such as crop offset. That would break "one set of settings for every teacher", so it's the owner's call.

### Q-09 · Who defines `requests.json` and `status.json` · superseded by D-37
- **Background.** Rev1's PORT-060/061 may already define them.
- **Proposal.** If they do, copy the definitions here unchanged. If not, this repo's draft ([contracts/requests-and-status.md](contracts/requests-and-status.md)) is offered to Rev1. Resolved when O-1 arrives.

### Q-10 · The owner's three originals · resolved → D-13
- **Update, 2026-10-19:** the three targets and their originals arrived. They are now in `design/portraits/` (see its README).
- **Still needed:** where each original came from (the Commons file page or loc.gov item, or elsewhere) and its licence.
- **Proposal:**
  - If an original meets SRC-01..03, its teacher is delivered normally.
  - If not, it's used only as a style target, and the teacher goes through normal sourcing.

### Q-11 · Engravings and drawings · resolved → D-47
- **Background.** B2 says "photograph", but the trial set includes an engraving on purpose.
- **Proposal.** Accept any medium that passes the pre-check, and record the medium. The trial shows whether engravings halftone well. If they don't, a setting turns them off.

### Q-12 · Dates · resolved → D-45
- **Proposal ([contracts/teachers-csv.md](contracts/teachers-csv.md)).**
  - Accept `YYYY`, `YYYY-MM` or `YYYY-MM-DD`.
  - "Impossible" means any of: an invalid calendar date, death before birth, a date in the future, or a lifespan over 120 years.
  - Reject circa and approximate forms. Leave the field blank and give a Wikidata id instead.

### Q-13 · Duplicate `teacher_id`s · resolved → D-45
- **Proposal.** Refuse every row that shares the id, and name them all, because the tool can't know which row is meant.

### Q-14 · Where `teachers.csv` lives · superseded by D-31, D-45
- **Proposal.** `data/teachers.csv` in this repo, so it is versioned and its changes are visible. Alternative: in the Drive folder, beside `requests.json`.

### Q-15 · Stack · build
- **Proposal.** Python 3.12 with uv, in WSL Ubuntu. Details in [spec/architecture.md](spec/architecture.md).

### Q-16 · The portrait's own licence · now
- **Background.**
  - A portrait made from a CC BY-SA original is an adaptation, so it must itself be shared under CC BY-SA, with credit.
  - CC BY needs credit and a note that changes were made.
  - Public-domain and CC0 originals need neither.
- **Proposal (SRC-11).**
  - The credit line says "adapted from".
  - The record carries the portrait's licence.
  - If the Rev1 schema has no field for it, raise it with Rev1 rather than changing the schema here.

### Q-17 · The harness · resolved → D-15
- **Background.** This project is the harness's first run, but the harness doesn't exist yet, and its input format isn't fixed.
- **Proposal.**
  - The harness gets its own repo, because it will be reused for Library-AI and later projects.
  - This repo supplies feature cards in the fixed field format of [plan/features.md](plan/features.md), and the conductor reads them.
  - The harness's own plan is made in a separate thread, so it doesn't crowd this one.
- **Questions:** where the harness is planned, and whether that work has started.

### Q-18 · Cut-out provider · resolved → D-19
- **Background.** B2 names Bria RMBG 2.0 through OpenRouter, or fal directly.
- **Update, 2026-10-19.** The owner's own method used an AI tool for the cut-out, and it did better than the prototype's free stand-in.
- **Option.** A free local model (for example BiRefNet, MIT licence) could run on the owner's PC with no key and no cost.
- **Proposal.** The trial compares the owner's tool (once named, Q-22) with Bria. The free local model is an optional extra. The best cut-out wins, and the cheaper one when they're close.

### Q-19 · "Close" in the trial's winner rule · trial
- **Proposal.** A contender is close when its total check score is within 5% of the best. Among close contenders, the cheapest per attempt wins.

### Q-20 · Claude pushing to this repo · resolved 2026-10-19
The owner installed the Claude GitHub App on this repo, and Claude's push works. Claude pushes planning notes directly to `main` during Phase 0.

### Q-21 · The AI-enhanced blend and STY-04 · resolved → D-18
- **Background.** The owner's own method: an AI tool made a subtly enhanced copy, which was laid over the original scan at about 50% before the halftone. The brief's STY-04 says the dots come from the photo's tones and no image model ever alters the face. A 50% blend means an image model shapes half of the tones the dots are made from.
- **Why it matters.** The portraits show real people. An image model can quietly change a face: eye shape, jaw, age. Done at 50% this is subtle, but it is a change to the likeness.
- **Proposal: adopt it as PIP-13, with safeguards.**
  - A light-touch prompt ("clean up, don't change the face").
  - Align before blending; refuse the copy if the alignment is poor.
  - The blend share is a recipe setting (0.5).
  - The likeness is checked against the original.
  - Everything is recorded with the attempt.
  - The trial runs every item with and without the enhancement, so the board shows whether it earns its cost.
  - STY-04 becomes: "the dots are made by code; an image model may contribute at most `enhance_blend` of the tones, through an aligned blend, and never draws the dots."
- **Alternative.** Keep STY-04 as written and get the same clarity from code: descreen plus sharpening, as in recipe 0.2.0.

### Q-22 · The owner's tools and in-between files · resolved → D-20
- **Questions:**
  - Which AI tool, and which prompt, made the enhanced copies?
  - Which tool removed the background?
  - Are the enhanced copies and cut-outs for Fillmore, Cady and Holmes still available?
- **Proposal.** Put them in `design/portraits/enhanced/<teacher_id>.*` and `design/portraits/cutouts/<teacher_id>.png`. The prototype can then test the blend on real enhanced copies and compare cut-outs. The prompts become the recipe's prompt text.

### Q-23 · Which image sources to adopt · resolved → D-24, D-29 (details: tracker T-11)
- **Background.** The owner asked for more sources than Commons and LoC (D-21). The full comparison is in [spec/sources.md](spec/sources.md).
- **Proposal: adopt now** these four, all keyless, which fits the one-key wish (D-19):
  - Wikidata with Commons;
  - the Library of Congress (picture records and digitised books);
  - **Internet Archive book plates**: portraits printed in the teachers' own pre-1931 books. Many New Thought books open with a captioned portrait of the author, so this is likely the biggest gain;
  - Wellcome Collection.
- **Later, only if the first run leaves many teachers blank:** Smithsonian Open Access, NYPL and DPLA (leads only). These need free data keys (Q-25).
- **Never:**
  - HathiTrust, which blocks automated clients;
  - Google Books, whose terms rule out automated use;
  - IAPSOP, whose scans are NC-licensed;
  - Openverse and Flickr, where licence claims are unreliable.

### Q-24 · Uncaptioned author frontispieces · withdrawn (D-24)
- **Background.** A portrait at the front of a teacher's own book is very likely the teacher. Without a caption or signature, though, it could be a founder, a spouse or a patron.
- **Proposal.** Don't use them automatically. List them in the report as "likely" candidates with their links; the owner can accept one with a `try_link` request.
- **Alternative.** Accept them when the book is by the teacher and was published in their lifetime, marked as a weaker match. The trial would show how often that's wrong.

### Q-25 · Free data keys later · resolved → D-34
- **Proposal.** Don't add Smithsonian, NYPL or DPLA until the first run's report shows how many teachers stay blank. Each key is a free registration and is kept outside the repo like the OpenRouter key.

### Q-26 · Which authors become teachers · resolved → D-45
- **Background.** `authors.csv` has 406 rows: 182 active, 146 proposed, 46 undecided, 32 excluded (2026-10-19).
- **Proposal.** Take `active` only, as the pipeline does. A proposed author gets a portrait once the owner makes them active.

