# Image sources (proposed, 2026-10-19)

The owner asked for more sources than Wikimedia Commons and the Library of Congress: ones the tool can pull from automatically, with their metadata and rights tracked (D-21). This page proposes which sources to use, how each one proves a match, and what is kept. **The owner picks which to adopt (Q-23).** Until then, only the sources marked *adopt now* are proposed for the build.

The list follows the owner's library-pipeline (`SPEC.md` §3), which already uses most of these repositories for books, so both projects treat a source the same way.

## The proposal at a glance

| # | Source | What it gives portraits | Key? | Rights come from | Match rule | Proposal |
|---|---|---|---|---|---|---|
| 1 | **Wikidata + Wikimedia Commons** | The teacher's Wikidata image; Commons files tagged as depicting the teacher | none | The file's licence template (Commons metadata) | R1, R2 | **adopt now** (in the brief) |
| 2 | **Library of Congress**: Prints & Photographs, plus digitised books | Portrait photographs and prints; plates in digitised books | none | The item's rights advisory ("No known restrictions…"); for books, the publication year | R3; R4 for books | **adopt now** (in the brief) |
| 3 | **Internet Archive books** (frontispieces and plates) | Portraits printed in the teachers' own books and in books about them. Many New Thought books open with a captioned portrait of the author | none | Publication before 1931 (US public domain), from the catalogue year | **R4** | **adopt now**: likely the biggest gain in coverage |
| 4 | **Wellcome Collection** (images and digitised books) | Some healers and mind-cure figures; clean licences | none | The record's licence (pdm, CC0, CC BY) | R3, R4 | **adopt now**: small, but keyless and clean |
| 5 | Smithsonian Open Access (incl. the National Portrait Gallery) | A few nationally known figures, CC0 | free api.data.gov key | CC0 flag on the record | R3 | later, if coverage is low (Q-25) |
| 6 | NYPL Digital Collections | Portrait files and periodical illustrations | free token | The record's "public domain" flag | R3 | later, if coverage is low (Q-25) |
| 7 | DPLA | Finds items held by many US libraries and historical societies | free key | rightsstatements.org URI on the record | leads only | later, as leads only (like the pipeline) |
| — | HathiTrust | — | — | — | — | **no**: its reading site blocks automated clients (the pipeline found this), and access controls are never worked around |
| — | Google Books | — | — | — | — | **no**: needs a key, and its terms ask for no automated querying |
| — | IAPSOP | — | — | — | — | **no**: its scans are CC BY-NC, and NC is never allowed (SRC-02) |
| — | Openverse, Flickr | — | — | — | — | **no**: uploaders' licence claims on old photos are often unreliable |

**Keys:** sources 1–4 need none. That fits the owner's wish for one key, which is the OpenRouter key for AI (D-19). Sources 5–7 need free data keys, which are not AI keys. They're worth adding only if the trial and first run show many teachers still blank (Q-25).

## Match rules (certain matches only; SRC-03)

A file counts only by one of these rules. Name-only, category-only and search-rank matches never count.

- **R1 (Wikidata image).** The image on the teacher's Wikidata item (P18).
- **R2 (Commons depicts).** A Commons file whose structured data says it depicts the teacher's Wikidata item (P180).
- **R3 (picture record with name and dates).** A picture record (LoC, Wellcome, Smithsonian, NYPL) whose subject or name heading equals the teacher's name or an alias, with life dates equal to the teacher's (SRC-05). A heading without dates never matches.
- **R4 (book plate), new.** All three conditions must hold:
  - **(a) the book.** It was published before 1931, by the catalogue year, judged as the pipeline judges years: a decade date like "192-" counts as 1929 and an uploader's placeholder date doesn't count.
  - **(b) the people.** Either the book's catalogue author is the teacher (name or alias; dates must agree where both sides give them), or the book is a history or biography whose record names the teacher as a subject.
  - **(c) the plate.** The plate's printed caption or facsimile signature names the teacher (name or alias). The vision pre-check reads the caption and quotes it in the record.

  An uncaptioned portrait at the front of the teacher's own book is very likely them, but it isn't certain. It's reported as a "likely" candidate for the owner, not used (Q-24).
- **Owner's link** (SRC-04): a pasted link to any adopted source, recorded as the owner's match.

Order of preference among candidates (SRC-07): licence tier (public domain first), then match strength (R1 > R2 > R3 > R4), then the pre-check's quality, then size.

## Rights, per kind of evidence

| Evidence | Sources | What decides | Allowed |
|---|---|---|---|
| A licence on the file | Commons, Wellcome, Smithsonian, NYPL | The licence string or flag, mapped by SRC-02 | Public domain marks, CC0, NoC-US, "no known restrictions", then CC BY and CC BY-SA. Nothing else |
| A rights advisory | LoC | The advisory text | "No known restrictions on publication" and public domain statements. Anything else is refused |
| A rightsstatements.org URI | DPLA providers | The URI | `NoC-US`, `NKC`, PDM, CC0. Refused: `InC*`, `UND`, `CNE`, `NoC-CR`, `NoC-NC`, `NoC-OKLR` |
| Publication of the book | IA, LoC, Wellcome books | Published before 1931 (95-year rule; nearly all of the library's readers are in the US) | The plate is public domain because the book is. The source's own rights field is recorded too, and a restrictive one (borrow-only, or "in copyright") refuses the item |

## What is kept for every original (SRC-08, SRC-12)

Every original that is considered, including the ones refused, gets a permanent row in the **rights log**, so nothing is researched twice and every portrait's credit can be traced. The row holds:

- **Source and location:** source, source id, record page link, file or IIIF link, and for book plates, the page number and the book's identifier.
- **Description as given:** title, creator or photographer, date, publisher and place.
- **Rights:** the rights evidence as given (licence string and URL, rights advisory, rights URI or publication year, quoted raw), the rule applied, the verdict (allowed tier, or refused with the reason), and the portrait's own licence (SRC-11).
- **Match:** `matched_by` (R1–R4 or owner_link), `matched_to` (the Wikidata id, name heading or caption text), and for R4 the book's author record.
- **Credit:** the credit line, built per source (for example "Portrait from *Lessons in Truth* (1896), Internet Archive, public domain").
- **The file and the check:** file size, pixel size and SHA-256, the date retrieved, and a saved copy of the raw source record (JSON) in the state store.

The log lives in the state store. Each run also exports it to `portraits/rights-log.csv` in the delivery folder, so the owner and the library can audit it (OUT-01, proposed).

## Finding plates in a book (R4, how)

1. **Find the books.** Search each adopted book source by author (name and aliases) for public domain books before 1931, the way the pipeline does. The teacher's key works (from `authors.csv`) are searched first.
2. **Spot pages that look like pictures.** Fetch small page images of the first 16 pages and any pages listed as plates. This is free: IA serves page images over IIIF with no key. Code finds pages that look like photographs (large areas of continuous tone or screened dots, little text).
3. **Confirm in the pre-check.** At most 3 candidate pages per book go to the vision pre-check (PIP-02). It also reads the caption and says whether it names the teacher.
4. **Download.** A confirmed plate is fetched at full resolution and becomes a candidate original like any other.

Politeness follows the pipeline's rules: official APIs only, published rate limits, an identifying User-Agent, timeouts, and no bulk scraping. Borrow-only or restricted items are skipped, never worked around.
