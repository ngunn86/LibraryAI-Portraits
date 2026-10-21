# Image sources (decided for the first build by D-46, 2026-10-19)

The owner asked for more sources than Wikimedia Commons and the Library of Congress: ones the tool can pull from automatically, with their metadata and rights tracked (D-21). This page proposes which sources to use, how each one proves a match, and what is kept.

> **Status after the formal review (T-11, D-46, 2026-10-19).** The review, with each source's access checked against its own documentation, is [../topics/T-11-picture-sources.md](../topics/T-11-picture-sources.md).
> - **First build:** Wikidata/Commons, the Library of Congress and Wellcome (no keys), plus the LoC name authority for identifying teachers.
> - **Smithsonian:** only if the coverage survey (SRC-14) shows gaps.
> - **Dropped:** NYPL (API retired 1 August 2026) and DPLA (D-46); the Internet Archive and book plates (D-24).

The list follows the owner's library-pipeline (`SPEC.md` §3), which already uses most of these repositories for books, so both projects treat a source the same way.

## The proposal at a glance

| # | Source | What it gives portraits | Key? | Rights come from | Match rule | Proposal |
|---|---|---|---|---|---|---|
| 1 | **Wikidata + Wikimedia Commons** | The teacher's Wikidata image; Commons files tagged as depicting the teacher (found by Commons search, `haswbstatement:P180=Q…`; the Commons Query Service needs a login) | none (an identifying User-Agent is required by the 2026 limits) | The file's licence template (Commons metadata) | R1, R2 | **adopted** (D-46) |
| 2 | **Library of Congress**: Prints & Photographs | Portrait photographs and prints | none (20 searches a minute) | The item's rights advisory ("No known restrictions…") | R3 | **adopted** (D-46). The LoC name authority (id.loc.gov) is adopted too, for identifying teachers (D-45) |
| 3 | ~~Internet Archive books (plates)~~ | — | — | — | — | **omitted** (D-24): extracting pictures from books is too much hassle unless absolutely necessary |
| 4 | **Wellcome Collection** (picture records) | Some healers and mind-cure figures; clean licences | none | The record's licence (pdm, CC0, CC BY) | R3 | **adopted** (D-46): small, but keyless and clean |
| 5 | Smithsonian Open Access (incl. the National Portrait Gallery) | A few nationally known figures, CC0 (files are given only for CC0 items) | free api.data.gov key | CC0 flag on the record | R3 | **later, only if the coverage survey shows gaps** (D-46) |
| 6 | ~~NYPL Digital Collections~~ | — | — | — | — | **dropped** (D-46): its API was retired on 1 August 2026, with no replacement |
| 7 | ~~DPLA~~ | — | — | — | — | **dropped** (D-46): it hosts no files, and leads to sites the tool may not fetch from |
| — | HathiTrust | — | — | — | — | **no**: its reading site blocks automated clients (the pipeline found this), and access controls are never worked around |
| — | Google Books | — | — | — | — | **no**: needs a key, and its terms ask for no automated querying |
| — | IAPSOP | — | — | — | — | **no**: its scans are CC BY-NC, and NC is never allowed (SRC-02) |
| — | Openverse, Flickr | — | — | — | — | **no**: uploaders' licence claims on old photos are often unreliable |

**Keys:** the adopted sources need none, so the only AI key stays OpenRouter's (D-19). Smithsonian would add a free data key, and only if the coverage survey shows gaps (D-46, SRC-14).

## Match rules (certain matches only; SRC-03)

A file counts only by one of these rules. Name-only, category-only and search-rank matches never count.

- **R1 (Wikidata image).** The image on the teacher's Wikidata item (P18).
- **R2 (Commons depicts).** A Commons file whose structured data says it depicts the teacher's Wikidata item (P180).
- **R3 (picture record with name and dates, or the teacher's LoC name id; D-47).** A picture record (LoC, Wellcome; Smithsonian if added) whose subject or name heading equals the teacher's name or an alias, with life dates equal to the teacher's (SRC-05). A heading without dates never matches.
- ~~**R4 (book plate)**~~, *withdrawn* by D-24. Kept for reference only. All three conditions had to hold:
  - **(a) the book.** It was published before 1931, by the catalogue year, judged as the pipeline judges years: a decade date like "192-" counts as 1929 and an uploader's placeholder date doesn't count.
  - **(b) the people.** Either the book's catalogue author is the teacher (name or alias; dates must agree where both sides give them), or the book is a history or biography whose record names the teacher as a subject.
  - **(c) the plate.** The plate's printed caption or facsimile signature names the teacher (name or alias). The vision pre-check reads the caption and quotes it in the record.

  An uncaptioned portrait at the front of the teacher's own book is very likely them, but it isn't certain. It's reported as a "likely" candidate for the owner, not used (Q-24).
- **Owner's link** (SRC-04): a pasted link to any adopted source (Commons, the LoC, Wellcome), recorded as the owner's match. The link is read without fetching its page. Accepted forms:
  - Commons: `commons.wikimedia.org/wiki/File:<title>`, or a file or thumbnail link on `upload.wikimedia.org` (a thumbnail's title is the folder before its last part);
  - LoC: `(www.)loc.gov/item/<id>`, `(www.)loc.gov/pictures/item/<id>` or `(www.)loc.gov/resource/<id>`;
  - Wellcome: `wellcomecollection.org/works/<id>`, or `api.wellcomecollection.org/catalogue/v2/works/<id>`.
- **Any medium** (D-47): photographs, paintings, drawings and engravings that pass the pre-check, with the medium recorded. A setting (`allowed_media`) can turn engravings off after the trial.

Order of preference among the copies of one photograph (SRC-07): licence tier (public domain first), then size, then the pre-check's damage rating. Which photographs fill a teacher's three slots is PIP-16: the best-known image first, then a spread across the teacher's life. The order of these steps, and the small previews used to group copies before any full download, are PIP-21.

## Rights, per kind of evidence

| Evidence | Sources | What decides | Allowed |
|---|---|---|---|
| A licence on the file | Commons, Wellcome (Smithsonian if added) | The licence string or flag, mapped by SRC-02 | Public domain marks, CC0, then CC BY and CC BY-SA 2.0 or later. CC BY-SA 1.0 is held for the owner before anything is spent (SRC-02, SRC-11). Nothing else |
| A rights advisory | LoC | The advisory text | "No known restrictions on publication" and public domain statements. Anything else is refused |
| ~~A rightsstatements.org URI~~ | ~~DPLA providers~~ | *Withdrawn with DPLA* (D-46) | — |
| ~~Publication of the book~~ | — | *Withdrawn with R4* (D-24) | — |

## What is kept for every original (SRC-08, SRC-12)

Every original that is considered, including the ones refused, gets a permanent row in the **rights log**, so nothing is researched twice and every portrait's credit can be traced. The row holds:

- **Source and location:** source, source id, record page link, file or IIIF link, and the preview link (at most 1,600 px) used to group and pre-check copies (PIP-21).
- **Description as given:** title, creator or photographer, date, publisher and place.
- **Rights:** the rights evidence as given (licence string and URL, or the LoC rights advisory, quoted raw), the verdict (tier 1, tier 2, `held` for CC BY-SA 1.0, or refused with the reason), and the licences of the portrait's files (SRC-11).
- **Match:** `matched_by` (`wikidata_p18`, `commons_p180`, `name_dates`, `lcnaf_id` or `owner_link`), `matched_to` (the Wikidata id, LoC name id or name heading) and the evidence.
- **Credit:** the credit line, in SRC-11's format (for example "Charles Fillmore, c. 1895. Photographer unknown. Library of Congress, Prints & Photographs Division. No known restrictions on publication.").
- **The file and the check:** file size, pixel size and SHA-256, the date retrieved, and a saved copy of the raw source record (JSON) in the database.

The log lives in the app's database (T-07). The admin page offers it as a CSV download, and each portrait's API record carries its own original's rights (OUT-14). The delivery folder is withdrawn (D-42).

## Being a polite client (SRC-09, D-46)

- **Official APIs only.** No bulk scraping, and access controls are never worked around.
- **An identifying User-Agent on every request:** the app's name, version and a contact address. Wikimedia has limited unidentified clients much more tightly since March 2026.
- **Paced to each source's published limit:**
  - the LoC: 20 search or item requests a minute, and 150 a minute for images, with a 1-hour block above that;
  - Wikimedia and Wellcome: one request at a time.
- **Back off** on 429, 5xx, or an HTML CAPTCHA page. Use timeouts and a few retries.
- **The network client refuses every other host** (SRC-01, CLAUDE.md rule 5). The sources' own hosts are:

  | Source | Hosts |
  |---|---|
  | Wikidata and Commons | `www.wikidata.org`, `commons.wikimedia.org`, `upload.wikimedia.org` (files and thumbnails) |
  | Library of Congress | `www.loc.gov`, `loc.gov`, `tile.loc.gov` (images), `id.loc.gov` (the name authority) |
  | Wellcome | `api.wellcomecollection.org`, `iiif.wellcomecollection.org` (images) |

  Redirects are followed by hand, and each target is checked against the same list.
- **Previews before downloads** (PIP-21): copies are grouped and pre-checked on reduced images, at most 1,600 px, from each source's own sized-image service (Commons' standard thumbnail widths; IIIF `!1600,1600` at the LoC and Wellcome). Only the chosen copies' full files are downloaded.

## Finding plates in a book (R4): *withdrawn* by D-24, kept for reference only

1. **Find the books.** Search each adopted book source by author (name and aliases) for public domain books before 1931, the way the pipeline does. The teacher's key works (from `authors.csv`) are searched first.
2. **Spot pages that look like pictures.** Fetch small page images of the first 16 pages and any pages listed as plates. This is free: IA serves page images over IIIF with no key. Code finds pages that look like photographs (large areas of continuous tone or screened dots, little text).
3. **Confirm in the pre-check.** At most 3 candidate pages per book go to the vision pre-check (PIP-02). It also reads the caption and says whether it names the teacher.
4. **Download.** A confirmed plate is fetched at full resolution and becomes a candidate original like any other.

Politeness follows the pipeline's rules: official APIs only, published rate limits, an identifying User-Agent, timeouts, and no bulk scraping. Borrow-only or restricted items are skipped, never worked around.
