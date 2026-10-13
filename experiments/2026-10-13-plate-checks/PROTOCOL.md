# Plate checks of 13 October 2026: protocol

Written on 13 October 2026 before any photograph or plate in this package was opened. Its SHA-256 is recorded in `PROTOCOL.sha256` in the same command that writes the hash, before the first image is viewed. Later changes go into dated amendments.

The package runs two visual checks on photographs held locally. Check 1 tests predictions P1 to P3 of conjecture [C-0004](../../knowledge/conjectures/C-0004-m895-office-text.md) on the Lothal sealings L-161 to L-170 and the Mohenjo-daro seal fragment M-895, and with them Shot A's prospective prediction 1 (PP1 of [C-0001](../../knowledge/conjectures/C-0001-rank-written-twice.md)). Check 2 tests the layout and direction rivals to Shot A's result on the seals whose legends end in 001, 595, 679 or 820 (PP3 of C-0001, prospective prediction 3 of [Shot A](../2026-10-12-conjecture-shots/shot-a-rank/PREDICTIONS.md)). Every judgement here is a visual reading of printed photographs by an AI model (Claude Opus 5.5). A reading becomes an observation of the objects only after a specialist confirms it on the same or better images; until then the decisions below are provisional decisions of the cards' rules on AI readings.

## What the reader knew before viewing

The reader had read the seal-text identity report, which describes L-161's photograph as showing a U-shaped sign, strokes inside brackets, a heart-shaped sign and a tall stem, and M-895's as showing a striated band below the text. The reader had seen the catalogue codes of the shared text (four signs, last sign 740), the catalogue's animal codes (`Elep` for the sealings, `Bull1` for M-895), the page heading of CISI 2 printed p. 85 in the scan's text layer ("unicorn IV"), and the statement of Frenez and Tosi 2005 (PDF 16) that L-161 to L-172 are impressions of one seal with an elephant and four signs. For Check 2 the reader had seen the CISI numbers of the set seals in Shot A's outputs and knows the four Wells numbers of the set, but has not looked up their graphic forms; an eye that recognises sign 820 or 740 on a crop can still infer the group. These exposures are why Check 1 asks a second reader who is told none of them (below), and why Check 2 hides group, CISI number and catalogue sign codes from the crops.

## Objects

Check 1 examines eleven objects: L-161 to L-170 (catalogue type `TAG:B`, the Lothal sealings) and M-895 (`SEAL:S`, fragment, 23.4 mm wide in the catalogue).

Check 2 examines the 29 seals in Shot A's size population, both halves, one per component, whose legend ends in one of the four signs: object type `SEAL:S` or `SEAL:R`, both face dimensions positive, preservation complete, slightly chipped, chipped or `complsete`, a completely observed single-line legend of at least two signs with no unknown sign, one face per object family and one family per component of the frozen split. [build_lists.py](build_lists.py) builds the list by importing Shot A's own `seal_table.py` and `rank_lib.py` read-only and reading the frozen split file directly, so it adds nothing to Shot A's confirmation-access log. It found the 18 discovery and 11 confirmation seals that Shot A reports.

The comparison set has one seal per set seal, chosen by the rule in `build_lists.py` before viewing. Candidates are seals of the same population ending in any other sign, with at least one Lipi crop, not already chosen; the first matching level of (same type, site and length), (same type and site, length ±1), (same type, site class and length) supplies the candidates, and the one nearest in log face area is chosen, ties broken by SHA-256. Matching on face size as well as type, site and length means that a difference in how the final sign sits cannot come from face size alone, and it keeps crop scale from revealing the group. All 29 pairs matched at the first level. The identifiers, groups and crop names are in [object-lists.json](object-lists.json); the sign sequences are local in `data/raw/2026-10-13-plate-checks/object-lists-with-sequences.json`.

| Pair | Set seal | Half | Site | Type | Signs | Last sign | Image held | Comparison seal |
|---|---|---|---|---|---:|---|---|---|
| P01 | H-642 | confirmation | Harappa | R | 6 | 001 | yes | H-135 |
| P02 | H-645 | confirmation | Harappa | R | 4 | 595 | yes | H-164 |
| P03 | M-1764 | confirmation | Mohenjo-daro | S | 3 | 679 | no | M-862 |
| P04 | M-1761 | confirmation | Mohenjo-daro | S | 2 | 820 | no | M-180 |
| P05 | M-6 | confirmation | Mohenjo-daro | S | 4 | 820 | yes | M-672 |
| P06 | M-16 | confirmation | Mohenjo-daro | S | 4 | 820 | yes | M-662 |
| P07 | M-393 | confirmation | Mohenjo-daro | R | 8 | 679 | yes | M-1350 |
| P08 | M-649 | confirmation | Mohenjo-daro | S | 2 | 820 | yes | M-673 |
| P09 | M-792 | confirmation | Mohenjo-daro | S | 6 | 679 | yes | M-81 |
| P10 | M-998 | confirmation | Mohenjo-daro | S | 3 | 820 | yes | M-1197 |
| P11 | M-1052 | confirmation | Mohenjo-daro | R | 10 | 679 | yes | M-396 |
| P12 | C-56 | discovery | Chanhu-daro | S | 3 | 001 | no | C-2 |
| P13 | H-1708 | discovery | Harappa | R | 2 | 595 | no | H-679 |
| P14 | H-1 | discovery | Harappa | S | 4 | 820 | yes | H-405 |
| P15 | H-10 | discovery | Harappa | S | 6 | 820 | yes | H-6 |
| P16 | H-29 | discovery | Harappa | S | 3 | 595 | yes | H-47 |
| P17 | H-80 | discovery | Harappa | S | 7 | 595 | yes | H-61 |
| P18 | M-1989 | discovery | Mohenjo-daro | R | 5 | 679 | no | M-407 |
| P19 | M-1701 | discovery | Mohenjo-daro | S | 3 | 820 | no | M-1151 |
| P20 | M-1720 | discovery | Mohenjo-daro | S | 4 | 679 | no | M-63 |
| P21 | M-1 | discovery | Mohenjo-daro | S | 5 | 001 | yes | M-70 |
| P22 | M-74 | discovery | Mohenjo-daro | S | 4 | 595 | yes | M-257 |
| P23 | M-629 | discovery | Mohenjo-daro | S | 7 | 679 | yes | M-30 |
| P24 | M-653 | discovery | Mohenjo-daro | S | 5 | 679 | yes | M-14 |
| P25 | M-1103 | discovery | Mohenjo-daro | S | 6 | 001 | yes | M-670 |
| P26 | M-1134 | discovery | Mohenjo-daro | S | 4 | 820 | yes | M-1148 |
| P27 | M-1203 | discovery | Mohenjo-daro | S | 4 | 595 | yes | M-705 |
| P28 | M-1290 | discovery | Mohenjo-daro | R | 3 | 595 | yes | M-414 |
| P29 | Dholavira, no CISI number (Lipi family 4195) | discovery | Dholavira | S | 5 | 820 | no | Dlv-1 |

Eight set seals have no Lipi crop. Seven carry numbers outside the CISI 1 and 2 ranges or from sites those volumes may not cover (M-1701, M-1720, M-1761, M-1764, M-1989, H-1708, C-56), and the Dholavira seal has no CISI number. Before viewing any image the CISI 1 and CISI 2 scans are searched for them by caption text and page headings; any found are viewed on the plate without blinding and flagged, and the rest are recorded as having no held image.

## Image sources

- Lipi crops in `data/lipi/public/seal_images/`, named by CISI number and side (Lipi commit `fc8813a`). For Check 1: `L-161_A.jpg`, `L-162_A.jpg`, `L-162_B.jpg`, `L-164_A_L-165_A.jpg`, `L-166_A.jpg`, `L-167_A.jpg`, `L-168_C.jpg`, `L-169_A.jpg`, `L-170_A.jpg`, `M-895_A.jpg` and `M-895_imp_a.jpg`. L-163 has no crop. For Check 2, the impression of side A and the object photograph of side A as listed under `view_crops` in `object-lists.json`.
- CISI 1 (Joshi and Parpola 1987), `research/literature/sources/joshi_parpola_1987_cisi1.pdf`, first scan copy only (PDF page = printed page + 36). The Lothal sealings are on printed pp. 276–278 (PDF 312–314) according to the [physical-views report](../2026-10-02-source-recovery/physical-views/REPORT.md); their basic data on printed p. 373 (PDF 409); the introduction's statement on photographic scale is located in the front matter.
- CISI 2 (Shah and Parpola 1991), `data/raw/2026-10-06-evidence-census/sites-deep/a-pakistan-afghanistan/common-revision/cisi2-archive.pdf`. M-895 is on printed p. 85 (PDF 120), headed Mohenjo-daro 893–898, 'unicorn' IV; the basic data for M-788 to M-947 are on printed p. 436 (PDF 471); the scale policy is on printed pp. XXV–XXVI (PDF 28–29), which state that inscribed sides are printed at double size (2:1) whenever possible and that exceptions are marked.
- Frenez and Tosi 2005, `data/six-hour/lothal/frenez-tosi2005.pdf`, Figure 6 (PDF 39), which shows L-161, L-162, L-163 and L-165.

Page renders and crops are written to `data/raw/2026-10-13-plate-checks/` with their source page, pixel bounds and SHA-256. No image leaves that directory.

## What is recorded

For every Check 1 object: the photograph or photographs used (file or page and pixel bounds, photograph caption, seal or impression); the signs visible in order, described by form in the reader's words and read from an impression (the M-895 object photograph is read mirrored); for each sign whether it is clear, partly visible or not visible; the field animal and the features that identify it (trunk, tusks, ear, legs and feet, horn, collar folds, the object before the animal, body markings); the orientation of the animal and of asymmetric signs; the impression edges if visible; and the measurements below. The basic-data row of each object is transcribed from the plate's basic-data page (dimensions, material, findspot, museum and excavation numbers) and kept local, with the dimensions repeated in `observations.json`.

For every Check 2 seal: the number of signs visible in the band; the final sign under the catalogue's direction (on an impression of a right-to-left legend, the leftmost sign; on the object photograph, the rightmost); whether that sign stands on the band's line; its height against the median height of the other signs of the band (normal at two thirds or more, reduced below); its gap from the previous sign against the median gap between the other signs (normal, wide at twice or more, tight); at which end, if either, the signs are crowded or the band leaves unused space; whether the band starts flush with the edge at the catalogue's start or at its end; the animal's facing direction on the impression; legibility; and notes.

Measurements (Check 1). On each sealing and on M-895, the text span (horizontal distance between the outer edges of the first and last sign), the height of each sign, and the face width where both impression edges are visible, all in plate pixels converted to object millimetres. Pixel coordinates are read from renders with a ruled grid. The scale of each page is estimated in two ways: from the volume's 2:1 policy and the scan's page size, and from the photographed extent of the other objects on the same page against their basic-data dimensions (median of the page's objects). Both estimates and their spread are reported; for M-895 its own catalogue width gives a third estimate if both side edges survive.

## Decision rules for Check 1

**P1 (same four signs in the same order).** Signs are compared object to object, M-895's impression against the sealings, at the level of graphic sign type; fine differences of form are recorded for P3. P1 passes if all four positions are legible on M-895 and on at least one sealing, and every legible position on every sealing matches M-895's sign in that position. P1 fails if a legible position on M-895 or on any sealing shows a different sign type, or the order differs. A position that is damaged or unreadable is left open and never filled from the catalogue; if M-895's four signs, or all four on every sealing, cannot be read, P1 is unresolved.

**P2 (elephant on the sealings, unicorn on M-895).** The elephant is confirmed if at least one sealing shows a trunk, tusk, or the elephant's large ear, and no sealing shows features of another animal. The unicorn on M-895 is confirmed only by a feature specific to the unicorn: the single forward-curving horn, the standard or cult object before it, or the head with the decorated neck folds and the bovine body together. A striated band or a body fragment compatible with several animals leaves M-895 unresolved, and the catalogue's code and the page heading are reported as catalogue classification, not as an observation. P2 passes when both animals are confirmed; it fails ("shared animal") if M-895 shows an elephant feature or the sealings show a unicorn feature; otherwise it is unresolved.

**P3 (the impressing seal differs from M-895).** P3 passes if the text span or face width of the impressing seal, measured on the sealings, differs from M-895's by more than 10% beyond the spread of the scale estimates, or if a difference of carved form in a sign is visible on at least two sealings and clearly on M-895 and cannot be produced by impression depth or wear (a different number of strokes, a different proportion of a sign's parts by more than about 20%, a different angle or attachment). Clay shrinks as it dries, so a sealing smaller than M-895 by 10% to 18% counts as a pass only if a second criterion agrees; a sealing larger than M-895 by more than 10% counts on its own. An exact match, which lowers the card's credence, requires spans within 5% and no visible difference of carved form. Anything else is unresolved. A difference of animal decided under P2 is reported beside P3 but does not decide it.

**Shot A prospective prediction 1 (C-0001 PP1).** The text's last sign in the catalogue is 740, outside the set, so the prediction is that the impressed face measures between 19.9 and 35.4 mm. It is met if the measured face width of the impressing seal, or M-895's width if P3 finds an exact match, falls in that range; not met if it falls outside; undecided if no impression shows both edges.

**Second reader.** A separate model instance receives copies of the Check 1 images renamed to neutral labels, with no object numbers, no catalogue readings, no animal codes and no statement of what is expected. It describes each image's signs in order, its animal and the features seen. P1 and P2 are decided as above on the first reader's record; where the second reader disagrees on a sign type or an animal that the decision depends on, that part is reported as unresolved.

## Decision rules for Check 2

The crops of the seals with images in both groups are copied by `blind.py` into `data/raw/2026-10-13-plate-checks/blind/` under random labels drawn from the operating system's generator, impression and object photograph of one seal together, with only the photograph kind, the catalogue's number of signs and its direction code shown. The key is written to a separate file that is not opened until every blinded seal has a recorded reading. Seals viewed on a plate are read after the blinded set and flagged as unblinded.

Each seal receives one verdict, by the first rule that applies:

1. **Undecided, no image or illegible**: no held image, or the band's end cannot be located.
2. **Supports direction**: the spacing reverses the catalogue's direction, meaning the band is flush with the edge at the catalogue's end while unused space or crowded signs lie at the catalogue's start.
3. **Supports layout**: the final sign is set apart (gap at least twice the median gap of the other signs), off the band's line (raised or lowered by half a sign height or more, or placed in the field), or reduced below two thirds of the median height and fitted into leftover space outside the band's line.
4. **Supports the grade reading**: the final sign sits on the band's line at normal size and spacing, and the spacing does not reverse the direction.
5. **Undecided**: anything else, for example a reduced final sign on the band's line or a crowded end that does not reverse direction.

For comparison seals the same rules name the same visual patterns; "supports the grade reading" there means an ordinary closing.

Group decisions. Prospective prediction 3 of Shot A (C-0001 PP3) passes if a majority of the set seals with images receive "supports the grade reading"; it fails, removing the textual half of the claim, if a majority receive "supports layout"; a majority receiving "supports direction" favours the direction rival; otherwise it is unresolved. The groups are compared by a one-sided Fisher exact test of rival verdicts (layout or direction) against the rest, set seals against comparison seals with images; p < 0.05 means the rival patterns are more frequent among set seals than among matched ordinary seals. Counts are also given for the seals ending in 820, the narrowed claim of Shot A's amendment.

## Outputs

`observations.json` holds every reading with its image locator, `decisions.json` the decisions under these rules, `README.md` the report, `RETROSPECTIVE.md` and `registry-entry.json`. Scripts are kept in this directory and write images only under `data/raw/2026-10-13-plate-checks/`.
