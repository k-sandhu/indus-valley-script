# Proposed changes to knowledge/DATA.md

From the museum open-access package of 13 October 2026 ([README](README.md)). Each block names the section it belongs in and gives the replacement or added text. Numbers come from [coverage/summary.json](coverage/summary.json), [coverage/museum-coverage.json](coverage/museum-coverage.json) and [harvest/summary.csv](harvest/summary.csv).

The 13 October post-review corrections are listed in [REVIEW-CHANGES.md](REVIEW-CHANGES.md). Join precision on the original review set is 26/26 supported (100%, one-sided 95% lower bound 89%); the recovered join is reported separately. The recall search leaves 10 records with identifier hits, four confined to one family, for printed-page checks.

## Opening paragraph (headline coverage sentence)

Replace "5.8% a museum number" with "5.8% a museum number in the older export (7.2% once the museum joins of 7 and 13 October are counted)". The source link stays as it is, with a second link to `experiments/2026-10-13-museum-open-access/coverage/museum-coverage.json`.

## Section 1, "Project registers, frames and releases" (add a row after the evidence census row)

| Source | Size | Where | Notes |
|---|---|---|---|
| [Museum open-access harvest](../experiments/2026-10-13-museum-open-access/README.md) (13 October) | 7 institutions queried; 86 museum records decided; 27 exact or confirmed joins, 19 of them new; 5 candidate additions | Tracked tables and CC0 or CC BY metadata; raw responses local | Raises the confirmed museum-join lower bound from 68 to 87; V&A raw responses to be deleted by 10 November 2026 under the V&A API terms |

In the evidence census row, change "114 museum originals, 68 confirmed joins" to "114 museum originals, 68 confirmed joins (84 after the 13 October review of the 46 open records)" and "46 records unresolved" to "46 records reviewed on 13 October: 16 confirmed, 21 with candidate sets, 8 unmatched, 1 uninscribed".

## Section 2, "Metadata coverage", table footnote

After the sentence defining museum ("museum means a `MUSEUM` value in the older export for the same CISI key"), add: "Counting also the confirmed joins to museum records (census and 13 October package), 340 objects (7.2%) have a museum accession: seals 11.1%, copper tablets 19.5%, tags and sealings 6.1%, pottery 1.3%."

## Section 2, "Museum records" paragraph (replace)

**Museum records.** The census saved 114 online records of original objects (National Museum New Delhi 76, Indian Museum Kolkata 18, British Museum 6, Penn 5, Metropolitan 5, Louvre 4) and confirmed 68 joins to local objects. On 13 October the 46 open records were revisited against the CISI 1 basic data read by eye, the Marshall 1931 and Mackay 1938 seal tables and the numbers written on objects in CISI photographs: 16 are now confirmed, 21 have candidate sets, 8 are unmatched and 1 is uninscribed. The independent review added Indian Museum 10377/A7252/C.2803 as family 2194 (M-1809), through Marshall 1931 vol. II p. 403 row 199. Newly harvested records added three joins (V&A IS.8:1-1951 to CISI M-1727, British Museum 1947,0416.7 to M-1883, British Museum 123208 to family 6000), so 87 museum records are joined. Sixteen local objects gain their first museum number. Six newly joined families gain an axis, including two that had no dimension before; the other four already had at least one axis. No family gained an openly licensed image, because the only CC0 photographs (eight seals at the Metropolitan and Cleveland museums) belong to seals without findspot or number that match 10 to 102 local objects each ([join table](../experiments/2026-10-13-museum-open-access/joins/join-table.csv)). Five museum objects are missing from the local corpus: CISI H-224, Banawali seal National Museum 3714 and Dholavira DHR-22198, DHR-6032 and DHR-7860.

## Section 3, "Museum collections and image archives" (replace the first rows of the table)

| Source (check) | Indus inscribed objects found | Terms | Card |
|---|---|---|---|
| Metropolitan Museum, Collection API v1.1 (W17) | Five inscribed seals (49.40.1–4, 1984.482), all public domain with photographs; no findspot or field number; harvested 13 October, not joinable on description | CC0 | [Q-1018](questions/Q-1018-museum-open-access-harvest.md) |
| Cleveland Museum of Art, Open Access API (W24) | Three inscribed seals (1964.104, 1973.160, 1973.161) with photographs; 1964.104 came from the MFA Boston and so probably from Chanhu-daro; harvested 13 October | CC0 | [Q-1018](questions/Q-1018-museum-open-access-harvest.md) |
| Penn Museum, collections data download (W19) | Full CSV held locally (430,871 rows, 2026-10-07 edition): five inscribed Chanhu-daro seals (all joined), four uninscribed seal-amulets, 38 casts or impressions | Data CC BY 4.0 (attribution: Penn Museum Collections Data, Penn Museum); images non-commercial | [Q-1018](questions/Q-1018-museum-open-access-harvest.md) |
| British Museum Collection Online (W18) | 27 stamp-seals labelled Indus Valley Civilisation in the "indus seal" listing, 7 with a stated inscription, 6 joined; scripted access blocked by a Cloudflare challenge on 13 October | CC BY-NC-SA 4.0 only where marked | [Q-1018](questions/Q-1018-museum-open-access-harvest.md) |
| Victoria and Albert Museum API (W28) | Four reviewed attributed records: seal IS.8:1-1951 (cites CISI M-1727; joined), bar-seal fragment IS.8A-1951, modern impression IS.8:2-1951 and figurine head IS.9-1951 (outside inscription scope) | Non-commercial; API content may not be stored beyond four weeks | [Q-1018](questions/Q-1018-museum-open-access-harvest.md) |
| Art Institute of Chicago API (new) | None | CC0 data (description field CC BY 4.0) | [Q-1018](questions/Q-1018-museum-open-access-harvest.md) |

Replace the Smithsonian row with: "Smithsonian Open Access (W23) | 20 casts in NMNH Anthropology, 5 of them seal casts (A482805–A482808, A482815); the keyless bulk bucket was scanned in full for three units (539,615 records) on 13 October; the API needs a key | CC0 | None".

## Section 4, target record table

In the `museum` row, change "5.8% (older export); 68 census joins" to "5.8% (older export); 7.2% with the 87 confirmed museum joins".

## Section 5, priorities

Ranks 7 (Q-1018) and 19 (Q-1019): mark done on 13 October and point to the package. Suggested follow-ups, if the coordinator agrees: read the Miscellaneous numbers of British Museum 1947,0416.5, .6, .8 and the 20 other listed seals in a browser; compare Cleveland 1964.104 with a better copy of Mackay 1943 pl. LII; add the five candidate additions to the object register (Q-1030); delete the raw V&A responses by 10 November 2026.

## Section 7, Rights (museum records row; replace)

| Museum records | Mixed: Metropolitan, Cleveland, Art Institute of Chicago and Smithsonian metadata CC0; Penn downloadable data CC BY 4.0 (images non-commercial); V&A API content non-commercial and not to be stored beyond four weeks; Louvre record text Etalab; British Museum images CC BY-NC-SA 4.0 only where marked; Indian and Pakistani museum records rights reserved or unverified | CC0 and CC BY metadata tracked in the 13 October package with attribution; other records local, with identifiers, flags and joins tracked |
