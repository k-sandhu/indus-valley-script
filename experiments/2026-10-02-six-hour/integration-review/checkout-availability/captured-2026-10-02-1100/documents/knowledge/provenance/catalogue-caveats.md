# Catalogue conventions and matching record

This page collects the conventions needed to read the preserved data and audits. The [corpus retrospective](../retrospectives/corpus-and-transcription.md) explains how the issues were found; [SOURCES.md](SOURCES.md) gives the witnesses and pins.

## Shared assumptions

The unit of observation is a specified physical object, side, line and witness. Inventory codes are catalogue labels; crosswalk arrays retain graphic candidates. Reading order is a documented transformation of displayed order. Completeness, direction, class and context values remain attributed to their source unless a separate photographic or excavation audit establishes them. Visual annotations made here are qualitative AI annotations, with alternatives and source coordinates preserved for review.

Source-derived text classes belong among transcription metadata. Archaeological response labels must come from observations such as material, manufacture, findspot or associated context. Proposed function, interpretation and later cultural parallels have separate fields. Missingness has explicit reasons and denominators.

## Identifiers, witnesses and duplicates

| Field or convention | Meaning and evidence | Handling |
|---|---|---|
| Lipi numeric family | Current export family, e.g. `1786`; face record `1786.2` | Stable within the pinned export. Join across versions through physical references, side and raw/candidate sequence. |
| CISI reference | Published physical-object reference, sometimes with side or photographic suffix | Preserve raw string, parsed base, side and suffix. Keep compound or absent identities unresolved. |
| `bis`, `ter`, `quater` | CISI1 intro XXIV–XXV/PDF 28–29: second/third/fourth photographs of the same side | Extra witnesses share object and side; each gets its own image record. |
| Lowercase caption | Impression, according to CISI1 introduction | Record image polarity and relation to the seal. |
| Exact repeated text on distinct objects | Repeated sequence with distinct physical artifacts | Retain objects for archaeology; group textual dependence for predictive evaluation. |
| Official CISI1 PDF repetition | Each PDF 1–431 image set equals PDF 432–862 at offset 431 | Use first copy and record printed/PDF coordinates. The scan has 862 pages but one 431-page book scan repeated. |
| Excavation item versus lot | Kenoyer/Meadow 2010 excerpt distinguishes year/item identifiers from lot/context identifiers | Keep artifact identity and context identity in separate columns; record joins from primary tables. |

The physical-CISI join found 2,374 of 2,375 nonempty older-export references in Lipi. Of those, 2,243 matched at least one face exactly, increasing to 2,293 after omitting `000`. All 179 Mayig references were found, with 100 broad whole-face matches and 65 matches among 94 clear faces. These counts describe catalogue compatibility. Any-face matching leaves the side join open. Evidence: local-only `data/normalized/{old_lipi_cisi_audit,mayig_lipi_cisi_audit}.json` and [audit code](../../research/corpus/audit_crosscorpus.py).

The CISI1 corrigenda, printed 375/PDF 411, affect source selection. H266–H275 duplicate photographs are deleted/reserved for volume 2; H356A/B/C becomes H354A/B/C bis. M463A, H85A, H130A and H289A have mirrored printing; M464A/B are swapped. H76A's wrong mirrored impression on printed 186 is corrected in Addenda printed 364. The [literature counting notes](../../research/literature/cisi1_counting_and_errata.md) preserve the source reference.

## Order, boundaries and unknown content

| Convention | Source observation | Data rule |
|---|---|---|
| Fuls code string | Displayed glyphs enumerate visually left to right in the normalized right-to-left presentation | Keep `signs_visual_ltr`; reverse within a verified right-to-left single line for `signs_reading_rtl`. |
| Fuls fragment `]368-632-706-140+` | Chapter 3 printed 26–27 identifies rightmost 140 as the beginning | Computational order `[140,706,632,368]`. |
| M1088 labelled image | Visual jar 740, composite540, short pair 002, wheel 820 | Reading list `[820,002,540,740]`; [orientation evidence](../../research/corpus/orientation_clarification.json). |
| Direction `NR` | Fuls single-sign category; acronym expansion unverified | Preserve category without inventing an expansion. Other exceptional direction codes remain explicit. |
| Multiple lines/sides | Concatenated export and printed rows can combine boundaries | Use line/side records where verified. Eligibility for a single-line experiment requires the source rule and known exceptions. |
| Wells `000` | Eroded/illegible content | Preserve raw marker and count interpretation. Historical ICIT `++` can represent a lost text part of unknown extent; the pinned 5,680 current rows contain no internal `+`/`++`. |
| Wells `999` | Physical blank | Distinguish blank from erosion and from an inferred boundary. |
| Mayig `P000` | Damaged/lost section; may span multiple signs | Explicitly filter for clear-text analysis, even when damage/uncertainty defaults are zero. |
| 1979 dashed underline | Editorial uncertainty, §5.4 printed 15/PDF 16 and §6.6 printed 17/PDF 18 | Preserve auxiliary status separately from glyph strokes and stable codes. |
| 1979 rectangle/stacked-line auxiliaries | Editorial loss/inaccessibility graphics | Count as modern drawn units in font evaluation, with separate ancient-extent status. |

Fuls's direction field was retained. Chapter 2.2 takes seal texts from impressions, so the image's polarity must be established from its witness rather than inferred solely from the field name. The 2010 help search example is on PDF 5; an earlier source-definition reference to PDF 6 is corrected in the orientation addendum.

The 1980 documentation, printed 13–14, explains that some physical boundaries are expressed only by classification or omitted with parallel-text support. Layout codes distinguish intended gaps, multiple lines and multiple sides. A printed 1979 row and its blank gaps therefore need a boundary audit before becoming an ancient sequence.

## Inventory and class scope

P, Wells and stable Finnish chart codes remain distinct namespaces. The 1979 upper number is a rank shared by graphic variants; the lower number is the stable Finnish code. The numerical reference has 687 chart cells, including repeated ranks/codes and 16 lower-label ambiguities. Store cell identity as `(PDFpage,column,row)`, retain candidate unions and link historical corrections. Repeated numbers remain source facts.

Mayig's P→W arrays are direct compatibility lists from its schema. Whole-class scoring ignores feature vectors. Preserve alternatives per token or class without transitive merging through overlapping lists. Examples include P385/W817–861, P086/W390–405 and P316/W705–706. P118 includes W777/778/782 and M362/363/364; the `flower` feature does not preserve the inner-foot variants needed for a strict glyph comparison.

| Source label | Verified definition | Remaining scope |
|---|---|---|
| `TAB:B`, `TAB:I`, `TAB:C` | Bas-relief, incised and copper tablet | Manufacture/object type; function needs separate evidence. |
| Wells SP/LP | Short patterned3–5; long patterned6+ | Sequence-derived class in the 2008 chapter. |
| Wells SS/MS | Single segments2–5; multiple segments5+ | Sequence-derived class. |
| Wells SC/LC/TS/VN | Short complex2–5; long complex6+; too short1–2; sign700+numeral, length2 | PP/PN/UC were not defined in the acquired 2008 edition. |

Definitions are in local-only `data/normalized/source_definitions.json`. Original object-type spellings include typos and variants; preserve raw values and place normalized categories in separate fields.

## Cases that require an explicit source note

| Case | Established observation | Remaining issue |
|---|---|---|
| M141 | Primary plate has two visual rows; Mayig assigns line1 and includes P000 | Source-based single-line eligibility differs from the annotator feature. |
| M73 | Broken section is visible | Complete-text eligibility needs review. |
| M81 | Grid/compound segmentation and adjacent stem differ between catalogues | Fine-code and token-boundary correspondence open. |
| M140 and M62 | Photographs support short paired strokes where one catalogue uses the tall-pair code | Preserve both raw transcriptions; candidate recoding remains a separate adjudication. |
| M181 | Decorated triangle in source corresponds to a crosswalk feature omission | Broad feature compatibility needs review. |
| M91 | Both short and tall paired strokes occur on one face | Supports graphic distinction within that object. |
| H697 | Primary Parpola 2011 reproduces reverse B with U and two tall bars | Obverse A candidate frame lacks an acquired primary photo. |
| H2238/H95-2613/6560-01 | Primary middle face shows three short bars plus diamond-like unit | Opposite long-bar count remains unresolved; no-ID group photographs stay cohort observations. |
| H904/current 1786 | Vats Plate XCVI477 and table J213(D) identify the coarse paired-face pattern | Historical Fuls ICIT3786 join awaits Fig 16; current 3786 points to M1540. |
| M1383 | Fuls Fig 15 names M-1383; current CISI-labelled row is reported as clay tag MN82a | Object/material/content-count join and unit premise remain unresolved. |
| M61/M62 restoration candidates | Bounded surviving motif/U respectively; existing Mayig candidates W081/W700 | Use as historical reading/recoding comparisons. The audited search produced zero new certified one-slot restorations. |

For new work, freeze the witness, physical identity, eligibility and annotation version before model scoring. Record later source reinspection as an overlay with its date and reason. The [experiment registry](../experiments/registry.json) links frozen, superseded and development outputs.
