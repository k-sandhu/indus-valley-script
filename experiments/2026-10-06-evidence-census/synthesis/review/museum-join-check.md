# Museum join check

Reviewer notes, 7 October 2026, on ten of the 61 museum-to-corpus joins in `experiments/2026-10-06-evidence-census/collections-and-datasets`, one further join that rests on a concordance row alone (pair 11), and two side checks. No package file was changed.

## Basis

Paths are relative to the repository root. `F` is `data/raw/2026-10-06-evidence-census/collections-and-datasets/focused-pass-2026-10-07/`. `CISI1` is `data/raw/2026-10-06-evidence-census/sites-deep/c-north-india/cisi1.pdf`, where the PDF page number is the printed page plus 36. `Lipi` is `data/normalized/lipi_observed_faces.jsonl`.

Museum records are the saved page bodies in `F` (`object-*.body`, `penn-*.body`). The British Museum record is the saved search-provider text `F/web-search-01.json`; my own fetch of the live BM page returned HTTP 403. Corpus rows were read from Lipi directly. The copies in `F/paired-comparisons.json` equal the Lipi rows for all 67 faces (record id, source_cisi, site, excavation-idno, family), and every pair resolves to one family.

CISI rows were read on the package's saved page images and on fresh renders of `CISI1`; the two show the same rows. For collision counts I removed case and every character that is not a letter or digit and compared the result with `metadata.excavation-idno` over all sites. The package's own `norm` also folds leading zeros and gives the same counts for these pairs.

The Verdict column gives confirmed, qualified, discrepancy or unverifiable for the package's stated evidence, then supported, ambiguous or wrong for the join.

## Pairs

1. `Indian Museum, Kolkata|10376/A7703`
2. `National Museum, New Delhi|11583-38`
3. `National Museum, New Delhi|SRG-3017/1256`
4. `National Museum, New Delhi|DHR-10616`
5. `National Museum, New Delhi|DHR-6506`
6. `National Museum, New Delhi|DHR 2617`
7. `National Museum, New Delhi|dk-1023-55`
8. `Penn Museum|L-141-92`
9. `Penn Museum|L-141-159`
10. `British Museum|1947,0416.4`
11. `National Museum, New Delhi|s.65` (extra)

## Join table

| # | Method | Museum identifiers | Corpus identifiers | Evidence checked and where | Verdict | Note |
|---|---|---|---|---|---|---|
| 1 | published_CISI_concordance, M-197 | Accession 10376/A7703. The page has no excavation-number, other-number or bibliography field. Mohenjodaro; the title names a steatite seal; the text mentions an inscription. | 2722.1, family 2722, source_cisi M-197, Mohenjo-daro, idno DK10924371. | CISI1 printed p. 367 (PDF 403; `F/cisi1-data-403.png`) row M-197: DK 10924, IM A 7703. DK 10924 begins the Lipi idno and A7703 ends the accession. M-197 is on one Lipi row, and no other idno begins dk10924. Catalogue plate p. 53 (PDF 89) shows a unicorn seal with two signs, as in Lipi (length 2). | confirmed; supported | The row does not contain 10376, so the museum-side link is A7703 alone. The idno tail 371 is not explained by the row and the join does not use it. |
| 2 | published_CISI_concordance, H-221 | Accession 11583-38; no other identifier fields. Harappa; copper tablet; the description counts three pictograms. | 4629.1, family 4629, source_cisi H-221, Harappa, idno 11583. | CISI1 p. 371 (PDF 407; `F/cisi1-data-407.png`) row H-221: 11583, NMI 38, both numbers in the accession. H-221 is on one Lipi row, and the idno 11583 equals one row over all sites. Plate p. 214 (PDF 250), H-221 B: 11583 is written on the object. | confirmed; supported | The Lipi text is damaged (length 3 with two positions unidentified, text length 3+?). |
| 3 | published_CISI_concordance, L-1 | Accession SRG-3017/1256; Lothal; steatite seal; the description counts six pictograms. | 1984.1, family 1984, source_cisi L-1, Lothal, idno 03017(S001) CLIII-A. | CISI1 p. 372 (PDF 408; `F/cisi1-data-408.png`) row L-1: 3017, LTH SRG 1256, both in the accession. The package's string attempt (key SRG-3017) found no Lipi row because the idno has no SRG prefix, a leading zero and a suffix, so the join rests on the row and on Lipi's source_cisi. L-1 is on one Lipi row. Plate p. 238 (PDF 274): a square unicorn seal with a standard and six signs. | confirmed; supported | CISI gives the Lothal site-museum prefix and the portal gives the National Museum; the package already says so. |
| 4 | exact_excavation | Accession DHR-10616; Dholavira; steatite seal; two pictographs. | 4240.1, family 4240, no CISI number, Dholavira, idno DHR-10616. | The strings are identical. Normalized dhr10616 matches 1 Lipi row and 1 family over all sites. | confirmed; supported | join_evidence is blank in the audit row, so the shared identifier is the only evidence cited. |
| 5 | exact_excavation, two faces | Accession DHR-6506; Dholavira; terracotta sealing; two rows of script. | 4304.1 and 4304.2, family 4304, Dholavira, idno DHR-6506 on both. | The strings are identical. dhr6506 matches 2 rows and 1 family. | confirmed; supported | Lipi has two faces of three positions each (sides 2), which fits two rows. The type differs in wording (sealing, TAG). |
| 6 | normalized_excavation | Accession DHR 2617 (with a space); Dholavira; heading steatite; sealing piece; part of three pictographs. | 4310.1, family 4310, Dholavira, idno DHR-2617. | Equal after deleting the space and the hyphen (dhr2617). 1 row, 1 family. | qualified; supported | No rival candidate exists, but the number is the only link. Material (steatite, terracotta), type label and count (three, two) all differ. A steatite sealing is unusual, so the museum heading may be the wrong field; I could not test that. |
| 7 | normalized_excavation, CISI row also cited | Accession dk-1023-55 on the page; the URL and record id (nat_del-dk-1023-65-38476) say 65. Mohenjodaro; copper tablet; four graffiti. | 3024.1, family 3024, source_cisi M-552, Mohenjo-daro, idno DK1023. | The package key dk-1023 (accession cut at its first number) equals DK1023 after removing case and hyphen; dk1023 matches 1 row. Two other idnos begin with it, DK1023141 and DK1023790.23; CISI1 p. 368 row M-387 (DK 10231) and p. 369 row M-478 (DK 10237) show them to be other numbers. CISI1 p. 369 (PDF 405; `F/cisi1-data-405.png`) row M-552: DK 1023, NMI 55. Plate p. 138 (PDF 174): four signs and a hand label DK 1023/ whose last two digits the scan does not resolve. | qualified; supported | The page (55) and CISI (55) agree and the URL (65) differs. The method label is correct: the string match decides and the CISI row confirms it. |
| 8 | shared_field_and_published_plate | Object number L-141-92; Other Number 3493 (Field No SF) and MFA 36.0976; bibliography Mackay, Chanhu-daro Excavations, pp. 39 and 292, Pl. LI No. 12; steatite; Indus Script; five characters. | 81.1, family 81, source_cisi C-78, Chanhu-daro, idno CH 3493Pl. LI:12. | `F/penn-149372.body`. Field 3493 and Pl. LI No. 12 give CH 3493Pl. LI:12, equal to the idno after normalization; ch3493plli12 matches 1 row. The only other idno containing 3493 is DK8253493 (Mohenjo-daro). | confirmed; supported | CH comes from the site name; the Penn record does not carry it. C-78 lies outside CISI1's Chanhu-daro rows (C-1 to C-50) and was not checked. |
| 9 | shared_field_and_published_plate | Object number L-141-159; Other Number 3495 (Field No SF) and MFA 36.0972; bibliography p. 293, Pl. LI No. 17; heading Stone; Indus Script; a row of characters. | 5270.1, family 5270, source_cisi C-73, Chanhu-daro, idno CH 3495Pl. LI:17. | `F/penn-83829.body`. Same construction; ch3495plli17 matches 1 row. The other idno containing 3495 is the longer Harappa number 11349583. | confirmed; supported | The Lipi transcription is four unidentified positions. C-73 was not checked. |
| 10 | published_Marshall_composite | Registration 1947,0416.4; Miscellaneous number Hr 5635; findspot Mohenjo-daro; steatite stamp-seal 33 x 33 x 13 mm; inscription in Indus script (provider text). | 2478.1, family 2478, source_cisi M-1906, Mohenjo-daro, idno HR 5635345. | Marshall 1931, vol. II, printed p. 404 (`F/marshall-table-055.png`; PDF page 55 of `F/marshall-alt-pdf.body`), row 345: 1.3 x 1.3 in, steatite (Wh), serial HR 5635. The idno is the serial HR 5635 followed by plate number 345, and no other idno begins hr5635. In this scan the serial column drifts to about half a row below the plate numbers by row 345, so I fixed the pairing by counting (row 345 is the 65th of 70 and HR 5635 the 65th serial) and against Lipi: of the 70 serials I read on the page, 39 occur in Lipi as serial plus plate number, none under a one-row shift, and the Lipi sizes equal Marshall's inch sizes x 25.4 (the page gives 1.3 in for row 345 and 1.1 in for rows 344 and 346; Lipi has 33.0 mm for 2478.1 and 27.9 mm for HR 5971346). | confirmed; supported | The Lipi 33 mm is Marshall's own size, so its agreement with the BM figure is agreement with the same table. The museum side was checked in the saved provider text only; the live page returned HTTP 403. |
| 11 | published_CISI_concordance, M-573; no excavation number | Accession s.65; Mohenjodaro; copper tablet; the description counts six graffiti marks and names a rhino; no dimensions. | 3043.1, family 3043, source_cisi M-573, Mohenjo-daro, idno - (none). | CISI1 p. 369 (PDF 405; `F/cisi1-data-405.png`) row M-573: excavation ???, NMI S-65. M-573 is on one Lipi row. Plate p. 144 (PDF 180): M-573 A shows the object with S-65 written on it. | confirmed; supported | The photograph carries the museum number, so the join does not depend on the table alone. The museum text gives six marks where Lipi has nine (two lines of four and five), and names a rhino where CISI's page heading says composite animal (Lipi symbol Othr). |

## Recorded comparison statuses

Each cell gives the package value and then my reading after looking at the saved record and the Lipi row. Type statuses are agreement in all pairs except 5 and 6, where sealing against TAG is a difference in wording.

| # | Site | Material | Dimensions | Inscription count |
|---|---|---|---|---|
| 1 | agreement; agree | uninformative_or_missing; agree for the heading Others, though the title names steatite, as Lipi does | outside_tolerance; agree (19 x 19 x 10 mm against 20.1 x 20.1 x 7.1) | not comparable; agree (no count in the museum text) |
| 2 | agreement; agree | uninformative_or_missing; agree (Lipi has -) | incomplete; agree (Lipi 0/0/0) | count_agreement; qualified: three positions in both, two unidentified in Lipi |
| 3 | agreement; agree | agreement; agree | outside_tolerance; agree as computed (39 against 38.1 mm on one axis, 17 against 38.1 on the other); the plate shows a square face, so 17 mm is probably thickness, which I did not verify | count_agreement; agree (six) |
| 4 | agreement; agree | agreement; agree | incomplete; qualified: Lipi's thickness cell is the range 0 - 11, and with 11 read as thickness, 21 and 11 mm match the museum's 2.1 x 1.1 cm | count_agreement; agree (two) |
| 5 | agreement; agree | agreement; agree (terracotta) | incomplete; agree (Lipi zeros) | not comparable; agree (two rows, two Lipi faces) |
| 6 | agreement; agree | disagreement; agree (steatite against terracotta) | incomplete; agree | count_disagreement; qualified: the museum counts part of three pictographs on a fragment, Lipi has two positions with open ends (2+?) |
| 7 | agreement; agree | agreement; agree (copper) | within_tolerance; agree (24 x 35 mm in both) | count_agreement; agree (four) |
| 8 | agreement; agree | agreement; agree | museum_missing; agree (no measurement on the page) | count_agreement; agree (five; Lipi text is lines of three and two) |
| 9 | agreement; agree | broader_museum_term; agree (heading Stone, description says baked steatite) | museum_missing; agree | not comparable; agree (no number given; Lipi has four unidentified positions) |
| 10 | agreement; agree | agreement; agree | incomplete; qualified: the two axes both records give agree at 33 mm; the museum adds a 13 mm depth and Lipi has none | not comparable; agree |
| 11 | agreement; agree | agreement; agree | museum_missing; agree | count_disagreement; agree as computed (six against nine) |

## Findings

All eleven joins hold. For each pair the saved record shows the stated accession and mentions an inscription, the Lipi rows exist with the stated source_cisi, site and idno and form one family, the cited page and row are correct (CISI1 pp. 367, 369, 371 and 372; Marshall p. 404 row 345), and no other Lipi row or museum record has an equal claim. Of the ten sampled pairs eight are confirmed and two qualified (6 and 7), with no discrepancy. The one unverifiable item is the live British Museum page for pair 10, which returned HTTP 403 to my fetch, so that museum side rests on the saved provider text. Pair 11 is confirmed. The join verdicts are eleven supported, none ambiguous and none wrong.

The institution, method and comparison-status totals recounted from `paired-comparisons.json` reproduce the figures in the collections report (46, 9, 5 and 1 joins by institution; 36, 13, 6, 5 and 1 by method). The package's CISI transcription agrees with the printed pages and with Lipi. The five rows I read (M-197, H-221, L-1, M-552, M-573) match both the transcription and the package's images. Of the 42 transcribed rows, 41 occur in Lipi under their CISI number; the transcribed excavation string equals the Lipi idno in 11 and begins it in 25, and the five others have visible causes (DKi read as DK1 for M-543 and M-582, a leading zero and suffix for L-1 and L-45, a DK- prefix and numeric tail for M-155). H-224 is absent from Lipi, as the package says. Object labels in the CISI plates add evidence that does not depend on the table: H-221 B shows 11583 and M-573 A shows S-65, and the S1 record below shows DKi 838/56.

Two points concern the evidence descriptions. Portal URL slugs differ from the displayed accession in at least one digit for 11 of the 94 National Museum and Indian Museum records, 8 of them among the 61 joins (dk-1023-65 against dk-1023-55 is one). The package keys on the displayed accession; the transcribed CISI rows for the eight joined records carry the displayed numbers, and I re-read only M-552. Separately, the CISI1 data table runs from p. 365 to p. 375, while the package states pp. 366-372, the span it transcribed. Page 373 holds rows that bear on S2.

## Side checks

**S1, rejected collision.** The single record is `National Museum, New Delhi|dki-838-56` (nat_del-dki-838-56-38477), stored with rejected_direct_collision true in `paired-comparisons.json`; no entry in `unconfirmed-join-candidates.json` carries one. The normalized key dki-838 selected Lipi 3750.1 (source_cisi M-1485, idno DK-i 838, copper tablet, symbol Elep, four signs, 36 x 25 mm). CISI1 p. 369 row M-543 reads DKi 838, NMI 56, the same two numbers as the museum accession, and Lipi 3015.1 carries source_cisi M-543 (idno DK1838, symbol Goat:8, six signs, 36 x 25 mm). The museum record describes a goat with a vessel and measures 2.5 x 3.5 cm, which fits 3015.1, and plate p. 136 (PDF 172), M-543 B, shows the tablet labelled DKi 838/56. The rejection was justified. A string lookup alone would have joined the wrong row, because Lipi writes the M-543 number as DK1838. The two Lipi rows carry the same excavation number (DK-i 838 in one spelling, DK1838 in the other) and the same 36 x 25 mm size; I did not resolve why.

**S2, the 53 unjoined records** (30 National Museum, 9 Indian Museum, 5 Met, 5 British Museum, 4 Louvre). One has an accession equal to a Lipi idno after casefolding and removing non-alphanumerics: National Museum BNL-1-5026 and Lipi 28.1 (B-3, idno BNL1 5026, Banawali). The package's key extractor cut the accession at BNL-1, so the full string was never tried. A second, BNL-1-170-84-1145, equals Lipi 43.1 (B-25, BNL1 170/84) once the trailing registration number is dropped. None of the 53 has a CISI-style key in its record. Two pattern hits are not keys: L-24 is the dimension "L-24 cm" of NM 75 NM-1-240-88-2512, and C-2803 is part of Indian Museum 10377/A7252/C.2803.

A published concordance reaches further than those two counts. The package transcribed only L-1 and L-45 from the Lothal rows. The other Lothal rows on p. 372 (to L-98) and all of p. 373 (L-99 to L-266) were not transcribed, and they carry the numbers of all nine unjoined National Museum Lothal accessions to some degree. Eight of the nine have usable_identifier false in `unconfirmed-join-candidates.json`, so the report's 80-record denominator excludes them. Five examples, by identifier:

| Unjoined record | Published row | Lipi row | What agrees |
|---|---|---|---|
| NM 1878/1165 | CISI1 p. 373, L-143: 1878, LTH SRG 1165 | 2085.1, idno 01878 | both numbers; Lothal |
| NM 6742/1174 | CISI1 p. 373, L-144: 6742, LTH SRG 1174 | 2086.1, idno 06742(T037) | both numbers; Lothal |
| NM 13051/1157 | CISI1 p. 373, L-220: 13051, LTH SRG 1157 | 2136.1, idno 13051(T031) CLXIV-B | both numbers; Lothal |
| NM BNL-1-5026 | CISI1 p. 375, B-3: BNL1 5026 | 28.1, idno BNL1 5026 | string equality |
| BM 1947,0416.2 (Misc. VS 823) | Marshall p. 402, row 3: VS 823, 1.85 in | 2526.1, idno VS 823003 | serial plus plate number 003; Lipi 47 x 47 mm; BM width 1.87 in |

The first three and the fifth meet the package's own standard, since a published table supplies both identifiers. The same Marshall page lists HR 629 at plate number 53 (row 53, 1.25 in), matching BM 1947,0416.3 (Misc. Hr 629) and Lipi 2484.1 (idno HR 629053, 31.8 mm; BM 3.0 x 3.1 cm). The collections report says the BM suffixes are unexplained; two of the three are explained by p. 402. The fourth example depends on reading BNL-1- as part of the Banawali number, which CISI's B-3 row supports.

Four more Lothal accessions match a single LTH SRG number only (1217 at L-166, 1273 at L-48 on p. 372, 2845 at L-122, 2862 at L-146), and 1860/1239 matches L-169 on 1239 with the CISI excavation number 1869 against the museum's 1860. Two candidates are weaker: SRG-989/128 matches L-29 on 989, but CISI gives registration 1281 and Lipi codes a unicorn where the museum text names a mountain goat; BM 1947,0416.1 (Dk 7665) begins Lipi 2364.1 (DK7665686C), with five characters and 37 mm in the BM record against four signs and 35.1 mm in Lipi.

At least five more of the 53 would join under the package's own rules (L-143, L-144, L-220 and the two BM seals), which makes 61 of 114 a lower bound.

## Not found and not checked

Not found, after looking: a second Lipi row for any of the eleven joins' identifiers (counts are in the table); an H-224 row in Lipi; a CISI-style key in any unjoined record; a hit for the nine unjoined Indian Museum registration numbers (A7252, A7253, A7255, A6679, A6686, A6689, A6700, A6721, NS 6045) in an OCR search of CISI1 pp. 366-375, though I did not read those pages by eye for them.

Not checked: the CISI volume 3 entries behind source_cisi M-1906, C-73 and C-78 (`F/cisi3-stream.pdf` opens with no readable pages, and CISI1's Chanhu-daro rows end at C-50); Mackay's plate LI, figures 12 and 17; the last two digits of the hand label on plate M-552 A, which the scan (810 x 1158 pixels per page) does not resolve; the live portal and Penn pages (the saved copies were read) and the live BM page (HTTP 403 to my fetch); museum images; site, material and sign comparisons for the S2 candidates; and the other 50 joins beyond the transcription consistency noted above.
