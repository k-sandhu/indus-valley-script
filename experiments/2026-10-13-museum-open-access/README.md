# Open museum records for Indus inscribed objects (Q-1018, Q-1019)

Data round 1, 13 October 2026. This package harvested the open or keyless museum routes listed in [Q-1018](../../knowledge/questions/Q-1018-museum-open-access-harvest.md), joined the records to local objects (Lipi families), and revisited the 46 museum records that the [evidence census](../2026-10-06-evidence-census/synthesis/join-summary.json) left without a checked join ([Q-1019](../../knowledge/questions/Q-1019-unjoined-museum-records.md)). The protocol, written before the first request, and its one amendment are in [PROTOCOL.md](PROTOCOL.md).

## Result

The open routes hold few inscribed Indus originals. The Metropolitan Museum has five (49.40.1–4 and 1984.482) and the Cleveland Museum of Art three (1964.104, 1973.160, 1973.161), all CC0 with photographs; signs are visible on all eight photographs. Penn's full collections CSV (430,871 rows, CC BY 4.0) contains five inscribed Chanhu-daro seals on loan from the Museum of Fine Arts, Boston, four uninscribed seal-amulets and 38 plaster casts or impressions. Review of the 12 V&A attribution flags retains four records: two seals, a modern impression and figurine head IS.9-1951, which is outside inscription scope. The V&A API returns one Mohenjo-daro seal (IS.8:1-1951), one bar-seal fragment (IS.8A-1951) and a modern impression of the first seal. The Art Institute of Chicago has no Indus object, and a scan of 539,615 Smithsonian Open Access records found only 20 casts, five of them seal casts. The British Museum blocked scripted access; its saved listing for "indus seal" names 27 stamp-seals labelled Indus Valley Civilisation, of which seven have a stated inscription in text we could read. Counts per museum are in [harvest/summary.csv](harvest/summary.csv).

The package decides 86 records and supplies 27 exact or confirmed joins, 19 new against the census. Joins now cover 87 museum records, up from the census's lower bound of 68. Of the census's 46 open records, 16 are confirmed through published rows or numbers written on the objects in the CISI photographs, 21 have candidate sets, 8 are unmatched and 1 is uninscribed (table below). Three newly harvested records also join: the V&A seal IS.8:1-1951 cites CISI M-1727 in its bibliography; British Museum 1947,0416.7 carries the field number DK 8528, which Mackay's 1938 seal table gives as seal 581 and the local corpus stores as `DK8528581`; and British Museum 123208 is the key the local corpus itself uses for family 6000. The eight census joins this package re-derived independently (five at Penn, three at the British Museum) agree with the census. None of the eight CC0 seals at the Met and Cleveland can be joined: their records give no findspot or number, and each matches between 10 and 102 local objects on motif, size and sign count.

| Q-1019 records | Confirmed | Ambiguous | Unmatched | Uninscribed |
|---|---:|---:|---:|---:|
| 13 failed string matches | 6 | 1 | 6 | 0 |
| 2 untried usable keys (Louvre) | 0 | 2 | 0 | 0 |
| 31 without a usable key | 10 | 18 | 2 | 1 |
| All 46 | 16 | 21 | 8 | 1 |

The joins change three fields of the object record. Objects with a museum accession from any source rise from 274 (5.84%, the older website export) and 324 (6.90%, adding the census joins) to 340 of 4,695 (7.24%); 16 families gain their first museum number ([coverage/museum-coverage.json](coverage/museum-coverage.json)). Six newly joined families gain an axis, including two that had no dimension before: L-166, a Lothal sealing, and M-614, an inscribed pot disc. The other four already had at least one axis. One family gains a finer provenance note (M-25, "site no IV"). No local object gains an image under an open licence, because the only CC0 photographs belong to the unjoined Met and Cleveland seals. Five museum objects are absent from the local corpus and are candidate additions: CISI H-224 (National Museum 12906-1296, catalogued in CISI 1 but missing from Lipi), Banawali seal 3714 (National Museum) and three Dholavira sealings or seals (DHR-22198, DHR-6032, DHR-7860).

The [independent check](verification/independent-check.md) read all 26 original joins: 26 supported, 0 qualified and 0 wrong, giving 100% precision with a one-sided 95% exact lower bound of 89%. Three joins carry weaker evidence: British Museum 1947,0416.1 retains size and sign-count differences; National Museum 3697-54 lacks a printed link to M-2053; and National Museum 1860/1239 joins through registration 1239 despite its excavation-number conflict. The reviewer found two Lipi faults at Lothal: family 2067 (L-122) carries the excavation identifier of L-100, so its identifier-linked fields need checking, and family 2084 (L-142) carries the excavation identifier of L-166. The reviewer also recovered Indian Museum 10377/A7252/C.2803 as family 2194 (M-1809) from Marshall 1931 vol. II p. 403 row 199; that join is now added. The check did not compare museum photographs, read CISI 3.1 or Mackay 1943 pp. 292-293, or obtain a full record for British Museum 123208. The 26-join precision result describes the original review set.

The dated corrections and before/after counts are in [REVIEW-CHANGES.md](REVIEW-CHANGES.md). The identifier recall search found hits for 10 of the remaining 59 non-joined rows, four confined to one family, and wrote 92 candidate rows with locators to [recall-candidates.csv](joins/recall-candidates.csv). It added no joins; each candidate needs its printed row checked.

## How the joins were made

The local object is a Lipi family in `data/normalized/lipi_observed_faces.jsonl`. A join is **exact** when the museum record cites an identifier that resolves to one family after normalization, and **confirmed** when the link passes through a published row (CISI 1 basic data, Marshall 1931 or Mackay 1938 seal tabulations, Mackay 1943 plate numbers) or a number written on the object in the CISI photograph, with site and object type agreeing. Records that match on description alone stay **ambiguous**, with the candidate count produced by [candidates.py](candidates.py); records whose identifiers match nothing local are **unmatched**. Every decision, with its page or row locator and any conflicting detail, is in [joins/decisions.py](joins/decisions.py); [joins/join-table.csv](joins/join-table.csv) adds candidate lists, licence classes and coverage flags, and [joins/q1019-decisions.csv](joins/q1019-decisions.csv) is the Q-1019 subset.

The CISI 1 basic-data pages (printed pp. 365–375) were rendered at 300 dpi and read by eye; OCR only located rows. That reading resolved most Lothal records through the Lothal site-museum numbers (LTH SRG) that the National Museum uses as the second half of its accession, and two of them through numbers painted on the objects: the CISI photograph L-29 B shows "SRG 989" and L-122 B shows "2845". The same pages place the Indian Museum's jasper seal N.S.6045 at M-25 and the National Museum's pipal-tree seal (NMI 74) at M-296. The National Museum record DK12995 shares its number with CISI H-13, but H-13 is a Harappa unicorn seal and the museum describes a Mohenjo-daro man with two tigers, so that candidate was rejected. Conflicts kept with confirmed joins include a one-digit difference between the National Museum's 1860 and CISI's 1869 for L-169, sign counts in museum descriptions that differ from the local transcription by one, and a 1.9 mm size difference for British Museum 1947,0416.1.

The Met and Cleveland seals were compared on motif, size and the number of signs visible on their CC0 photographs. Cleveland 1964.104 came from the Museum of Fine Arts, Boston by exchange, and the MFA's Indus seals come from the 1935–36 Chanhu-daro excavation; eight Chanhu-daro unicorn seals of 23–27 mm are its candidates, with C-64 (Mackay pl. LII no. 15, six signs) the closest, but the plate scan is too high in contrast to confirm it by eye. The Louvre's three seals from Susa and Girsu each have one compatible local family among the few foreign finds in the corpus, and British Museum 1892,1210.1 (Cunningham's 1875 Harappa seal) has one plausible candidate, H-1048; these stay ambiguous until a photograph or catalogue number decides them.

## Sources and licences

| Source | Route and date | Licence | Tracked here |
|---|---|---|---|
| Metropolitan Museum of Art | Collection API v1.1 search and v1 object records, 13 Oct 2026, 199 requests at 2 s spacing | CC0 for objects flagged `isPublicDomain` ([API documentation](https://metmuseum.github.io/)) | Full metadata of Indus-attributed public-domain records ([met-records.json](harvest/met-records.json)) |
| Cleveland Museum of Art | Open Access API, 43 requests | CC0 ([API page](https://openaccess-api.clevelandart.org/)) | Full metadata ([cleveland-records.json](harvest/cleveland-records.json)) |
| Art Institute of Chicago | API with Elasticsearch phrase queries, 23 requests | CC0, except the description field, CC BY 4.0 ([API docs](https://api.artic.edu/docs/)) | Query log and three non-Indus hits |
| Smithsonian Institution | API refused without key (HTTP 403); bulk bucket `s3://smithsonian-open-access`, units `nmnhanthro`, `fsg`, `nmaa`, 770 files, 1.2 GB | CC0 | The 22 matching records ([smithsonian-records.json](harvest/smithsonian-records.json)) |
| Penn Museum | `Penn_Museum_Collections_Data.csv` (updated 2026-10-07; 151,266,760 bytes; SHA256 `a24614d5…a3778`) and nine object pages | Data CC BY 4.0 ([download page](https://collections.penn.museum/collections/objects/data.php)); images non-commercial | The 47 seal-like Indus rows ([penn-records.json](harvest/penn-records.json)). Attribution: Penn Museum Collections Data, Penn Museum, CC BY 4.0 |
| Victoria and Albert Museum | Collections API v2, 14 searches and object records | V&A terms section 9: non-commercial; API content may not be stored for more than four weeks | Identifiers, field-presence flags, classification |
| British Museum | Saved search page (12 Oct, data inventory), saved object page for 1947,0416.7, census observations, search-engine results; live site behind a Cloudflare challenge | CC BY-NC-SA 4.0 only where marked; `robots.txt` content signal `search=yes, ai-train=no, use=reference` | Identifiers and Miscellaneous numbers |
| CISI 1, Marshall 1931, Mackay 1943 | Local scans already held; Mackay 1938 vol. I scan held by the parallel package `2026-10-13-mackay-marshall-tables` (read only) | Rights unverified | Page and row locators only |

Every request is logged with URL, UTC time, status, bytes and SHA256 under `data/raw/2026-10-13-museum-open-access/<museum>/requests.jsonl`, summarized in [harvest/acquisition-record.json](harvest/acquisition-record.json). Requests used the project User-Agent and no key, account or personal information. Images were downloaded only for the Met and Cleveland CC0 records, kept local, and used to count signs.

## Limits

The British Museum part rests on a listing from 12 October and a few saved pages; 20 of its 27 Indus seals have no reachable description, and five of the British Museum seals cannot be joined until someone reads their Miscellaneous numbers in a browser. Penn's image terms and the V&A, British Museum, Louvre and Indian museum records are not open, so their images and text stay out of the repository. Raw V&A responses must be deleted by 10 November 2026 under the V&A's terms. Joins that rest on CISI 3.1 numbers (M-1727, M-1883, M-1893, M-1919, M-2053, H-1048) cannot be checked against that volume, which the project does not hold. The Smithsonian scan covered three units; other units were not scanned. Candidate counts depend on the local corpus's motif codes and sizes, which are missing for many objects, so a count of one means one compatible object among those with recorded values.

## Reproducing

From the repository root, in order (each harvest reuses its cache and writes only under `data/raw/2026-10-13-museum-open-access/` and `harvest/`):

```text
python experiments/2026-10-13-museum-open-access/harvest_met.py
python experiments/2026-10-13-museum-open-access/harvest_cleveland.py
python experiments/2026-10-13-museum-open-access/harvest_aic.py
python experiments/2026-10-13-museum-open-access/harvest_smithsonian.py nmnhanthro fsg nmaa
python experiments/2026-10-13-museum-open-access/harvest_smithsonian.py --summarize
python experiments/2026-10-13-museum-open-access/harvest_penn.py
python experiments/2026-10-13-museum-open-access/harvest_vam.py
python experiments/2026-10-13-museum-open-access/harvest_bm.py
python experiments/2026-10-13-museum-open-access/apply_review_overrides.py
python experiments/2026-10-13-museum-open-access/build_joins.py
python experiments/2026-10-13-museum-open-access/coverage_museum.py
python experiments/2026-10-13-museum-open-access/harvest_summary.py
python experiments/2026-10-13-museum-open-access/acquisition_record.py
python experiments/2026-10-13-museum-open-access/write_manifest_additions.py
python experiments/2026-10-13-museum-open-access/recall_search.py
```

`cisi1_locate.py` crops CISI 1 table rows for reading, `lipi_index.py` looks up local families by CISI number or excavation-number prefix, and `candidates.py` lists descriptive candidates.

For an offline post-review rebuild from saved inputs, start at `apply_review_overrides.py` in this command list. The correction run made no network request. Penn's `indus_attributed_records` count in the summary now describes the 47 reviewed retained rows; its 942 broad pattern matches remain in the note and query log.

## Files

- [PROTOCOL.md](PROTOCOL.md), [RETROSPECTIVE.md](RETROSPECTIVE.md), [REVIEW-CHANGES.md](REVIEW-CHANGES.md)
- `harvest/`: per-museum records and query logs, [summary.csv](harvest/summary.csv), [acquisition-record.json](harvest/acquisition-record.json)
- `joins/`: [decisions.py](joins/decisions.py), [join-table.csv](joins/join-table.csv), [q1019-decisions.csv](joins/q1019-decisions.csv)
- `coverage/`: [summary.json](coverage/summary.json), [museum-coverage.json](coverage/museum-coverage.json)
- `verification/`: the independent check of every join
- Proposals for shared files: [DATA-UPDATE.md](DATA-UPDATE.md), [manifest-additions.json](manifest-additions.json), [question-updates.md](question-updates.md), [registry-entry.json](registry-entry.json)
