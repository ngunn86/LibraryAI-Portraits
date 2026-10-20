# T-11 · Picture sources: the formal review

**Status:** in discussion (2026-10-19). Claude's review and proposals, waiting for the owner.
**Tracker:** [T-11](../tracker.md) · **Builds on:**
- D-21: more sources than Commons and LoC;
- D-24: no Internet Archive and no book plates;
- D-29: plan the others, detail them here;
- D-34: extra keys are fine, kept to a minimum;
- D-45: the LoC name authority helps identify teachers.

**Spec:** [../spec/sources.md](../spec/sources.md)

The access facts below were checked on 2026-10-19 against each source's own documentation (see Sources at the end). Field names marked *(confirm)* come from Claude's knowledge, not from the documentation read today. The coverage survey (proposal 3) confirms them before anything is built on them.

## Three findings that change the plan

1. **NYPL's API is gone.** Its Digital Collections ("Repo") API page says it "is being deprecated and will no longer be available starting August 1st, 2026", with "no public API replacement … planned". So NYPL can't be built in as planned. Many of its public-domain pictures also reach Wikimedia Commons, and NYPL's records reach DPLA.
2. **Wikimedia tightened its API limits in 2026.**
   - Anonymous traffic has had low limits since early March 2026.
   - Identified traffic gets higher limits from early April 2026: a User-Agent naming the app and a contact. Others measured about 10 requests a minute without contact details and about 200 a minute with them.
   - So the tool must send a proper User-Agent. No key is needed at our volume.
   - The Commons Query Service needs a login, so "depicts" searches go through the ordinary Commons search (`haswbstatement:P180=Q…`) instead.
3. **The Library of Congress allows 20 searches a minute,** and blocks for an hour above that. That's plenty for 182 teachers, but the client must pace itself and back off on a 429 or a CAPTCHA page.

## Source by source

| # | Source | Access, key and limits | Rights come from | Match rule | Proposal |
|---|---|---|---|---|---|
| 1 | **Wikidata + Wikimedia Commons** | Wikidata API and SPARQL, Commons API. No key. A proper User-Agent is required (2026 limits); OAuth would only be needed for much more volume | The file's licence on Commons (`extmetadata`: LicenseShortName, LicenseUrl, Artist, Credit) *(confirm)* | R1 (Wikidata image, P18), R2 (Commons file that depicts the teacher, P180) | **First build.** The best yield and the best-known image (PIP-16) |
| 2 | **Library of Congress**, Prints & Photographs | loc.gov JSON API (`fo=json`). No key. 20 requests/min for search and items; 150/min for images and media; 1-hour block if exceeded | The item's rights advisory, e.g. "No known restrictions on publication" *(confirm field name)* | R3 (a subject or name heading with the teacher's life dates) | **First build.** Keyless; strong on portraits of well-known Americans around 1890–1930 |
| 2a | **LoC name authority** (id.loc.gov) | No key | n/a (it identifies people; it has no pictures) | n/a | **First build**, as the second source for teachers' dates and identities (D-45) |
| 3 | **Wellcome Collection** | Catalogue API, no sign-up or key. A daily snapshot is offered for bulk use | Each image's licence (public domain mark, CC0, CC BY…) *(confirm field names)* | R3 | **First build.** Keyless and clean, but a small yield (mind-cure and healing figures) |
| 4 | **Smithsonian Open Access** (with the National Portrait Gallery) | api.si.edu with a free api.data.gov key *(limit: confirm)* | Media are given only for CC0 items; others come as metadata without a file | R3 | **Later, if the survey shows gaps.** Few New Thought figures expected, and many National Portrait Gallery portraits aren't CC0 |
| 5 | ~~NYPL Digital Collections~~ | API retired 1 August 2026, no replacement | — | — | **Drop** (finding 1). Its pictures may still arrive through Commons |
| 6 | **DPLA** | Free key by email; "not ordinarily rate-limited" | Rights fields on each record; links to the holding library (`isShownAt`) | Leads only | **Later, as leads.** DPLA hosts no files; it points to hundreds of other sites. See proposal 2 |
| — | Europeana | Free key; rights URIs on every record | — | R3 | **Not planned.** Possibly useful for British teachers (e.g. Troward); revisit only if the survey shows gaps |
| — | Internet Archive, HathiTrust, Google Books, IAPSOP, Openverse/Flickr | — | — | — | **No** (D-24; access rules; NC licences; unreliable uploader claims), as before |

## Proposals

1. **First build: the three keyless sources** (Wikidata/Commons, the Library of Congress, Wellcome) plus the LoC name authority. No new keys.
2. **DPLA leads are listed, not fetched.**
   - A DPLA record that points to a picture on one of the adopted sources becomes an ordinary candidate there.
   - Any other DPLA lead (a historical society, a university library) is shown on the admin page with its rights statement, for the owner to look at.
   - The tool never downloads from a site that isn't an adopted source (CLAUDE.md rule 5). An owner who finds a good picture can have the library send a `try_link`, which works only for adopted sources.
3. **A coverage survey early in the build.** This is a live feature, like library-pipeline's `discover --dry-run`.
   - It searches every active teacher on the adopted sources and records what each would find.
   - It downloads nothing, spends nothing on AI, and doesn't touch portraits.
   - Its report shows how many teachers each source covers. That decides whether Smithsonian, DPLA or Europeana are worth their keys.
4. **Polite clients everywhere** (from library-pipeline's rules):
   - official APIs only;
   - each source's published limit, paced, with backing off on 429 or a CAPTCHA page;
   - a User-Agent naming the app and a contact address (an address set for the app, never a personal one in the repo);
   - timeouts and retries;
   - no bulk scraping;
   - the network client refuses every host that isn't an adopted source or the model API (rule 5).
5. **Order of preference** is unchanged (SRC-07, PIP-16):
   - the best-known image first;
   - then by licence tier, match strength (R1 > R2 > R3), quality and size.

## Sources consulted (2026-10-19)

- [loc.gov API: working within limits](https://www.loc.gov/apis/json-and-yaml/working-within-limits/)
- [Wellcome Collection catalogue API](https://developers.wellcomecollection.org/docs/catalogue)
- [Smithsonian Open Access developer tools](https://www.si.edu/openaccess/devtools)
- [NYPL Digital Collections API](https://api.repo.nypl.org) (the deprecation notice)
- [DPLA API policies](https://pro.dp.la/developers/policies) and [field reference](https://pro.dp.la/developers/field-reference)
- [Wikitech-l: New global API rate limits](https://www.mail-archive.com/wikitech-l@lists.wikimedia.org/msg97202.html) (March 2026) and [a client's report of the measured limits](https://github.com/ProfessionalWiki/MediaWiki-MCP-Server/issues/625)
- [Wikimedia Analytics API access policy](https://doc.wikimedia.org/generated-data-platform/aqs/analytics-api/documentation/access-policy.html) (User-Agent format)
