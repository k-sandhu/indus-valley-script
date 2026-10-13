# Retrospective

Data round 1, package `museum-open-access`, 13 October 2026. The protocol was written before the first request; one dated amendment recorded the route changes forced by the Smithsonian, British Museum and V&A terms before any join was assigned.

## Harvest

The Metropolitan Museum's v1.1 search answered every query in one page, and the 176 object records came through at two-second spacing without the firewall block that stopped the 12 October check after about 80 calls. Two accession neighbours of the Dodge Fund seals, 49.40.5 and 49.40.7, were fetched directly because no search returned them; they are Hittite and Kushan. The automatic classifier marked only 49.40.3 as inscribed, since the other titles do not mention an inscription; looking at the five CC0 photographs showed signs on all of them.

Cleveland's API was straightforward. The Art Institute of Chicago's simple `q` parameter returned 133,165 records for "Indus", most of them famous paintings, so the search was rewritten with Elasticsearch phrase queries and two control queries showing that the place and date filters work; no Indus object exists there. The Smithsonian API refused keyless requests, and the protocol forbids requesting a key. The same CC0 metadata sits in a public bucket, so three units were streamed (770 files, 1.2 GB), keeping only matching lines and a hash per file; the result repeats the 12 October finding of casts only.

Penn's CSV has no field-number or bibliography columns, which the joins need, so the nine original seals' object pages were read for them. The first filter counted plaster casts of figurines as seal-like because the word "cast" was in the seal pattern; narrowing the pattern removed 14 of them. The V&A search parameter `q_place_name` did not filter, so one query returned 8,586 records and about 100 full records were fetched to classify seal-like hits; the V&A's terms then turned out to forbid storing API content beyond four weeks, which set the tracked-file rule and a deletion date for the raw cache.

The British Museum served a Cloudflare challenge. Its `robots.txt` allows general agents but names Anthropic's crawlers among those disallowed and signals `ai-train=no`; the package did not attempt to get round the challenge and used the witnesses saved on 12 October, the census's observations and search-engine result text instead. That limits the British Museum to identifiers for most records.

## Joins

OCR of the CISI 1 basic-data pages missed most of the numbers needed, so the eleven pages were rendered at 300 dpi and read by eye in half-page views. This settled the Lothal records through LTH SRG numbers and showed that the National Museum's accession pattern is excavation number followed by the site-museum number. Two Lothal joins were decided by numbers painted on the objects in the CISI photographs, which also showed that the National Museum's "989/128" truncates SRG 1281 and that a local motif code (Bull1:O for a seal the museum calls a goat) does not by itself refute a join.

The British Museum's field numbers DK 8528 and Dk 7665 matched the start of local excavation strings with an unexplained suffix. The parallel package acquiring the Mackay and Marshall tables had a scan of Mackay 1938 and a CC BY transcription locally; reading the two rows on the scan by eye gave seal numbers 581 and 686C, explaining the suffixes. The scan's right-hand columns drift half a row, as the census found for Marshall, so the pairing was fixed by counting rows.

The eight CC0 seals at the Met and Cleveland stayed unjoined. Their records give no findspot or number, and motif, size and sign count leave 10 to 102 local candidates each. Cleveland 1964.104 came from the MFA Boston, which points to Chanhu-daro and narrows it to eight local seals, but the Mackay 1943 plate scan is binarized too heavily for a confident photograph comparison. The first version of the candidate list for this seal omitted one Chanhu-daro seal with four signs; the list was aligned with the search output before the join table was frozen.

The first coverage count used a crude number count for dimensions that turned "1 1/16 in" into three numbers; it was replaced by an axis count that treats a fraction as one value and prefers the metric figure in parentheses.

## Verification

An independent reviewer, given the join table and the local evidence paths, re-derived each of the 26 joins and checked six non-joins; the results are in `verification/`.

## Outcome

Q-1018 has a dated harvest for all seven institutions, and every one of the 46 Q-1019 records has a decision with its basis. The confirmed museum-join lower bound rises from 68 to 86, and 15 local objects gain their first museum number. The open-access routes add no openly licensed image to any local object, because the only CC0 photographs belong to seals without provenance; that gap now depends on CISI 3.1, the British Museum's pages or comparison against better plate copies.


## After review, 13 October 2026

The original report above describes the acquisition endpoint. The numerical audit and independent join review led to the dated corrections in [REVIEW-CHANGES.md](REVIEW-CHANGES.md), with 49 starting files preserved locally under `data/raw/2026-10-13-museum-open-access/pre-review-2026-10-13/` and verified SHA256 lists. The protocol and reviewer-owned verification files were left intact.

All 69 restricted-source decision rows were rewritten as project classifications and saved-record locators, and both join tables were rebuilt. A ledger and idempotent applier record 45 field changes, including later-period exclusions, the V&A seal/impression distinction and existing inscription observations needed for count replay. Eight of the 12 V&A attribution flags belonged to later photographs, paintings or textiles; four remain attributed, with two inscribed originals, one modern impression and a head outside inscription scope. The summary now derives classification totals from reviewed flags. Penn's 942 broad pattern matches are separated from its 47 reviewed retained rows. The inventory type-group rule fixes pottery and other denominators to 630 and 187.

The independent reviewer supported all 26 original joins, with 0 qualified and 0 wrong, and recovered Indian Museum 10377/A7252/C.2803 as family 2194 through Marshall 1931 vol. II p. 403 row 199. The original exact-match search missed the DK- prefix. Joins rise from 26 to 27, new joins from 18 to 19, the cumulative record lower bound from 86 to 87 and census-scope joins from 83 to 84. Accession coverage rises from 339 to 340 families (7.22% to 7.24%); first-number gains rise from 15 to 16. Six newly joined families gain an axis, including two with no dimension before; the other four already had an axis.

The offline recall search of the remaining 59 decision rows found identifier hits for 10 records, four confined to one family, and saved 92 candidate rows with locators. It added no join. The post-fix independent combined count is 542/4,695 including bracketed readings, 519 with whole cells unbracketed and 534 with any definite number. The original combined-coverage.json remains intact.

During implementation, the first summary replay failed because an eagerly evaluated Penn note used another museum's query schema; selecting that note only for Penn fixed the failure before any summary was written. The first recall replay encountered a saved failed-response row without an accession; skipping that non-record allowed all decision rows to be searched. Final checks replay the output generators, confirm override idempotence and compare all type classifications to the inventory. Source comparison details stay local. The reviewer CSV still carries a Lipi sign sequence at line 15, which the coordinator must redact or keep local before publication.

The recovered join supports the view that composite identifiers conceal further museum links. Reading the recall candidates against their printed rows will decide how many of those links hold.
