# Protocol: open museum records for Indus inscribed objects, 13 October 2026

Written before any API was queried or any join computed. The package answers question cards Q-1018 and Q-1019 for data round 1 (`experiments/2026-10-13-data-round-1/COMMON.md`). Amendments made after acquisition starts are appended at the end with their date and reason; nothing above the amendment heading is edited afterwards.

## Questions

1. Which inscribed Indus objects (seals, sealings, tablets, inscribed pottery and other objects with Indus signs) do museums with open data or keyless APIs publish, and what accession, title, object type, material, dimensions, findspot or provenance, date, bibliography, other numbers, image URL and image licence does each record carry?
2. Which local objects (Lipi families in `data/normalized/lipi_observed_faces.jsonl`) do those records describe, and how good is the join?
3. Which of the 46 museum records that the evidence census left without a checked join (`data/raw/2026-10-06-evidence-census/synthesis/main-2026-10-07-v6/candidate-object-joins.json`) can now be joined, given candidates, or recorded as unjoinable?
4. How many local objects gain an accession, an openly licensed image URL, dimensions or a findspot, and how many museum objects are absent from the local corpus?

## Sources and routes

Each route is queried with the User-Agent `indus-valley-script-research/1.0 (+https://github.com/k-sandhu/indus-valley-script)`, no personal information, about one request per second (1.5 s for the Metropolitan Museum, whose firewall blocked an earlier session after about 80 calls), no account and no API key. Every response is cached under `data/raw/2026-10-13-museum-open-access/<museum>/` with the URL, retrieval time (UTC), HTTP status, byte count and SHA256 in `requests.jsonl`; a cached response is never fetched again. Terms pages are saved as witnesses.

| Museum | Route | Data terms to confirm |
|---|---|---|
| Metropolitan Museum of Art | Collection API v1.1 search (paginated), v1 object records | Open Access CC0 for objects with `isPublicDomain` true |
| Cleveland Museum of Art | Open Access API `/api/artworks/` | CC0 per `share_license_status` |
| Art Institute of Chicago | API `/api/v1/artworks/search` | Data CC0; images by `is_public_domain` |
| Smithsonian | Open Access API without a key; if refused, recorded as not harvested | CC0 |
| Penn Museum | Full collections CSV from the data download page, filtered locally | CC BY 4.0 for downloaded data |
| Victoria and Albert Museum | Collections API v2 search and object records | API terms page |
| British Museum | Collection online search and object pages, if reachable | Website terms; CC BY-NC-SA 4.0 only where marked |

Search terms: Indus, Harappan, Harappa, Mohenjo-daro and its spellings (Mohenjodaro, Mohenjo Daro), Lothal, Chanhu-daro (Chanhudaro, Chanhu Daro), Kalibangan, Dholavira, "Indus script", "Indus Valley", "stamp seal" combined with Pakistan, India or South Asia, and the culture, period and place facets each API offers. The exact query list and the hit count of every query are recorded.

## Scope and record classification

A record is **Indus-attributed** when its culture, period, place or description names the Indus or Harappan civilization or a Harappan site. Each Indus-attributed record is classified by object class (seal, sealing or impression, tablet, inscribed pottery, other), by inscription status as the record states it (`inscribed`, `uninscribed`, `not-stated`; a photograph inspected by us can upgrade `not-stated` to `inscribed-by-image`, recorded as our observation) and by originality (`original`, `cast-or-replica`, `modern-impression`). Casts and modern impressions are recorded and never counted as originals. Uninscribed seals returned by the same queries are kept and flagged. Seal-like records that the searches return but that the museum attributes to another culture (Dilmun, Mesopotamian, Bactrian) are logged with the reason for exclusion.

Fields extracted per record: museum, accession, record URL, title, object name, inscription text or note, material, dimensions as printed and parsed to millimetres with the unit of record, findspot or provenance, date, credit line, bibliography, other numbers (field, excavation, loan, CISI), image URLs, image licence, data licence, raw file path and SHA256.

## Join rules

The local object is the Lipi family. Joins use only identifiers and published or photographic evidence, never sign sequences chosen to fit.

- **exact**: the museum record cites an identifier (CISI number, excavation or field number) that resolves to one Lipi family after casefolding and removing non-alphanumeric characters, the site agrees, and no other family shares the normalized key.
- **confirmed**: the link passes through a published concordance (a CISI basic-data row, the Marshall 1931 or Mackay tables, an excavation plate number cited by the museum) or through a photograph comparison in which the museum image and the local CISI crop show the same object (same breaks, chips, motif details and sign shapes). The page, row or image pair is recorded, the site agrees and no recorded attribute contradicts the join.
- **ambiguous**: two or more local families remain possible, or one family agrees on description (site, motif, material, size, sign count) without identifier or photographic confirmation. All candidates are listed.
- **unmatched**: no local family is compatible. An unmatched inscribed original whose site and object class are covered by the local corpus, and for which a search of that site's families by motif, type and size finds no candidate, is a **candidate addition**; otherwise the reason is recorded (no site, site not covered, record too sparse).

A join that depends on reading a number in a scan, or on an image comparison, records who observed it (this package) and the file compared.

## Revisiting the 46 census records

Start from the census review (`experiments/2026-10-06-evidence-census/synthesis/review/museum-join-check.md`, section S2), which names concordance rows for several records. For each of the 46: re-read the saved record, look up any number it carries in Lipi `excavation-idno`, `source_cisi` and the CISI 1 basic data (local scan, printed pages 365–375), the Marshall 1931 tabulation (vol. II pp. 402–405) for British Museum seals, and any record harvested here; then assign one of the four classes above with its basis. Records whose institution has no images or no numbers we can reach are recorded as unjoinable with the sources searched.

## Accuracy

After all joins are assigned, draw a verification sample with a fixed seed: every exact and confirmed join if there are 30 or fewer, otherwise 30 at random plus every join that rests on a single source. For each sampled join the museum image (where reachable) is compared by eye with the local CISI crop, and the identifier evidence is re-read. Precision is the share of sampled joins that the check supports, reported with the count of joins it rejects or downgrades. Ambiguous joins are not counted in precision.

## Coverage

For each local family that gains a confirmed or exact join, record whether it newly gains a museum accession (none in the older website export's `MUSEUM` field and none among the census's 68 joins), an image URL under CC0, public domain or CC BY, dimensions (museum dimensions where Lipi has none, or where Lipi lacks one of the three), and a findspot finer than the site. Report counts before and after for the touched fields, the museum objects not in the local corpus (candidate additions) and the casts. Coverage uses the data inventory's usable-value rules (`experiments/2026-10-12-data-inventory/PROTOCOL.md`).

## Rights and tracked outputs

Records from CC0 sources (Metropolitan public-domain objects, Cleveland, Art Institute of Chicago, Smithsonian) are tracked as extracted metadata without images. Penn records are tracked under CC BY 4.0 with attribution. Records from the V&A and British Museum, and the census's Indian and Louvre records, are tracked only as identifiers, URLs, field-presence flags, our joins and our judgements; their values stay in the local directory. Images, if downloaded for comparison, stay local. Raw responses stay local.

## Outputs

Scripts in this directory, run from the repository root; `harvest/` (per-museum extracted records and query logs), `joins/` (join table, Q-1019 decisions, verification), `coverage/` (summary), `README.md`, `RETROSPECTIVE.md`, `DATA-UPDATE.md`, `manifest-additions.json`, `question-updates.md`, `registry-entry.json`.

## Amendments

### Amendment 1, 13 October 2026, during acquisition (before any join was assigned)

- **Smithsonian.** The Open Access API refused keyless requests (HTTP 403, `API_KEY_MISSING`). The same CC0 metadata is published without a key in the public bucket `s3://smithsonian-open-access` (AWS Open Data). The units most likely to hold Indus objects (`nmnhanthro`, `fsg`, `nmaa`; 770 files, 1.2 GB) were streamed once; each file's URL, bytes and SHA256 are logged and only matching lines are kept, because caching the whole anthropology unit would store 1.15 GB of unrelated records.
- **British Museum.** A scripted request returned a Cloudflare challenge (HTTP 403). The challenge is not bypassed. The British Museum part uses the search page and object page saved by the data inventory on 12 October, the census's saved observations and search-engine result text, recorded as such. Its `robots.txt` content signal (`search=yes, ai-train=no, use=reference`) is noted; nothing from the museum is used for training.
- **V&A.** The V&A API terms (section 9.3) forbid caching or storing API content for more than four weeks. Raw V&A responses stay local and are due for deletion by 10 November 2026; tracked files hold identifiers, URLs, field-presence flags and our classification.
- **Concordance sources for joins.** Besides the CISI 1 basic data (PDF 401–411, read by eye from 300 dpi renders; OCR used only to locate rows), joins may cite the Marshall 1931 tabulation (vol. II pp. 402–405, census copy) and the Mackay 1943 plates LI–LII (local scan) where a museum cites a Mackay plate number.
- **Descriptive candidates.** For records without identifiers, `candidates.py` lists local families with compatible site, type, motif code, face size (±1.5 mm unless stated) and sign count from our reading of the open museum photograph (±1). A single surviving candidate stays **ambiguous**; it is reported with the candidate count. No join is upgraded to confirmed on description alone.
- **Unjoinable records.** A record whose identifiers are present but match no local family and no published row is classified **unmatched**; when the record states an inscription and the site is in the local corpus, it is a candidate addition.
