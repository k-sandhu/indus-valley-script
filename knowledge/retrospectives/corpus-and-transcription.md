# Corpus and transcription retrospective

The October 1–2, 2026 corpus work acquired pinned observational exports, recovered three primary Helsinki editions, inspected photographic witnesses and built a manually annotated chart reference. It also documented catalogue disagreements, unsuccessful acquisition paths, unsuitable restoration cases and a failed font-transcription pipeline. The useful outputs are source constraints, reproducible inputs and evaluation records. Linguistic meanings, sound values and a decipherment remain unresolved.

This account covers externally observable approaches and outcomes. The original evidence remains under `research/corpus/`, `data/normalized/` and the related root/methods/literature directories. It distinguishes our source annotations from the parent agent's models and the literature agent's acquisitions. The [experiment registry](../experiments/registry.json) and [root](root-investigation.md)/[methods](methods.md)/[literature](literature.md) retrospectives cover the other workstreams.

## Reading the record

The [source inventory](../provenance/SOURCES.md) provides URLs, pins, hashes, access routes and rights status. [Catalogue caveats](../provenance/catalogue-caveats.md) collects conventions used throughout: physical object/side/witness identities, visual versus reading order, unknown spans, inventory candidate sets and editorial auxiliaries. Photographic judgments here are qualitative AI annotations; expert review and fresh blinded samples remain the next evidence for transcription accuracy. The primary/derivative distinction concerns provenance, while catalogue compatibility concerns an explicitly recorded graphic comparison.

The new repository imported 16,284 files and 1,523,734,911 bytes from the original workspace. The [import manifest](../../archive/2026-10-01-investigation/import-manifest.json) lists preserved paths, excluded runtime folders and mismatching copies quarantined before restoration. Original outputs were preserved. Bulk inputs and unresolved-rights witnesses are local-only. Imported upstream folders omit their `.git` directories; original pins survive in summaries/manifests. Future normalization needs fresh pinned clones or an explicit source-pin implementation, since the old normalizers obtain commit IDs with `git -C ... rev-parse HEAD`.

## Finding a usable observational corpus

The initial search sought machine-readable inscriptions with graphic codes and archaeological metadata from Mahadevan, Wells, ICIT/ISI and research supplements. An open complete independently coded EBUDS/Mahadevan/Wells research corpus was not acquired. ICIT bulk access required registration. Rao's Science/PNAS papers, Yadav's n-gram work and Mukhopadhyay's articles supplied methods and examples, but the searched supplements did not yield a usable independent full token corpus. The literature archive records the publication-level search; our primary folder retains the Rao PDFs and the acquisition scripts.

Three GitHub exports supplied practical inputs. [Mayig](https://github.com/mayig/indus-valley-script-corpus), pinned at `ad2f1e218a34b8c33c57de0d6cb8d99272765bbb`, contained 179 Mohenjo-daro unicorn seal faces, 186 lines and 1,003 P-class tokens. Its 396-class schema linked to 498 Wells IDs through feature-dependent catalogue candidates. The actual license was MIT, Michael Carlson 2024. The README's license discussion and the photographs' source rights were recorded separately.

[Lipi](https://github.com/yajnadevam/lipi), pinned at `fc8813a52e183d19c441631dc26c33a4dccbea39`, contained 5,680 rows, 4,695 numeric families, 5,804 parts and 19,946 tokens across 714 codes. The raw CSV hash is `c36d0c26becb00b12b509cb2f5a35ffab1b5332e2e438cda308a272f77dba62c`. Its 3,504 distinct observed sequences left 2,176 repeated-row excess. The export also contained proposed decipherment fields and interpretation tables. We retained observational columns, raw graphic strings, physical references and metadata; translations, Sanskrit fields, notes and decipherment tables were excluded. No license was found at that pin, so the raw and normalized sequence files remain local-only.

The earlier [Indus website export](https://github.com/yajnadevam/indus-website), pinned at `2434249618b1e74de3f26d28b90dfde093c3dd94`, supplied 2,543 rows, 11,135 tokens and 1,903 unique sequences in a GPL-3.0 repository. Its SQL hash is `04d5a2c0f239458e4151d006b10c6ace638ee63f961083cf0331fd23309d2a24`. The SQL contained `DROP` statements; it was parsed as text. It shared Lipi's maintainer and served as a version audit.

The [Lipi](../../research/corpus/normalize_lipi.py), [Mayig](../../research/corpus/normalize_mayig.py) and [older-export](../../research/corpus/normalize_indus_website.py) normalizers wrote stable JSONL with raw and transformed order, family/face/part identities, missingness flags and metadata. The derived tables and summaries are in local-only `data/normalized/`. Complete right-to-left single-line filtering produced 2,930 Lipi rows, 1,859 unique texts and 1,596 unique texts of length at least3 for the parent analysis. Raw direction counts remained visible: R/L4,269; L/R215; unspecified776; NR386; T/B16; BUS10; SYM8.

### Early data issues and their fixes

| Issue encountered | Check and change | Evidence |
|---|---|---|
| Numeric IDs disagreed across exports | An early same-number comparison produced 449 first-face mismatches. Insertions can renumber objects, so the audit switched to physical CISI identity and retained side/raw-sequence evidence. | [Cross-corpus code](../../research/corpus/audit_crosscorpus.py); local-only `old_lipi_cisi_audit.json`. |
| A zero damage/uncertainty flag admitted damaged Mayig sections | `P000` was filtered explicitly. The resulting clear set has94 faces. The 100 zero-default faces included six P000 cases. | `mayig_summary.json`; [source report](../../research/corpus/CORPUS_REPORT.md). |
| Annotator line features could misstate physical layout | M141's plate has two rows although all annotated tokens have line1. The source exception was recorded without changing raw data. | [Plate adjudications](../../research/corpus/plate_audit/adjudications.json). |
| Candidate mappings overlapped | Direct P→W arrays were retained; graph closure through overlap was rejected for exact graphic conversion. Feature-based and whole-class compatibility were distinguished. | [Crosswalk builder](../../research/corpus/build_sign_crosswalk.py); `mayig_wells_class_crosswalk.json`. |
| Historical ICIT unknown-part notation could alter extent | The pinned5,680 raw strings were checked for internal `+`/`++`; none were present. Historical `++` remains documented as an unknown-length part convention. | `source_definitions.json`, [orientation/source notes](../../research/corpus/orientation_clarification.json). |
| Derived text classes looked like archaeological variables | Fuls and Wells definitions were checked. SP/LP/SS/MS/SC/LC/TS/VN are text-structure categories; manufacture/object type was kept separate. | `source_definitions.json`; Airavati 2008, Wells printed 275–288. |

Physical joining found 2,374 of 2,375 nonempty older CISI references in Lipi, with 2,243 matching at least one face exactly and 2,293 compatible after omitting 000. All 179 Mayig physical references were found; 100 whole faces were compatible with the broad Wells arrays, including 65/94 clear faces. Any-face matching did not settle side correspondence. The pinned export had no simple CISI base assigned to multiple numeric families; absent and compound references remained unresolved.

## Resolving direction from documentation and photographs

The phrase “normalized for right-to-left reading” initially left two serialization interpretations: initial-sign-first versus visually left-to-right listing of a right-to-left drawing. The methods agent raised this ambiguity before terminal/initial claims were finalized. We read the source convention and checked a labelled photograph.

Fuls 2022 Chapter 3, printed 26–27, uses `]368-632-706-140+` and identifies rightmost 140 as the beginning. Fuls 2010's search example `%-585-___-231+`, PDF 5, begins with 231, followed by the unknown and 585 to its left. The public M1088 example has jar 740 at visual left, then540, short pair 002 and wheel 820 at visual right. It therefore supports reading `[820,002,540,740]`. The computational transformation reverses a verified single line's stored visual list.

The catalogue direction field was retained. Fuls Chapter 2.2 explicitly uses seal impressions, which makes image polarity part of the witness record. Multiline/multiside concatenations needed separate boundaries. The [clarification](../../research/corpus/orientation_clarification.json) reconciled the shortened metadata phrase without changing normalized data or analytical sequences and corrected the 2010 help page reference from 6 to 5.

## Acquiring primary editions

The 1979 Helsinki corpus was the main route to source material independent of the modern GitHub transcriptions. Direct requests to the old portal PDF returned 403 and a public-link `downloadMedia` call timed out. Ordinary Chrome navigation through the official entry initiated a HELDA download. The completed `indus_corpus_1979.pdf` was copied unchanged from Downloads, checked for PDF structure/title/pages and hashed. Direct `urllib` access to the HELDA download-page URL returned HTML, which was recorded as an access-route issue.

The 1979 file has180 PDF pages including the repository cover,179 book pages, and explicit CC BY4.0 on the official entry. The 1980 documentation downloaded directly from a public Helsinki link,98 pages; its reuse license was unverified. The 1982 concordance also downloaded directly,201 pages, with official CC BY4.0. Their separate manifests and hashes are listed in [SOURCES.md](../provenance/SOURCES.md).

Ordinary prose in1979 had a usable but fallible OCR layer. Glyph OCR was punctuation, Latin letters and digits. The corpus printed plotted drawings rather than numerical sequences beside each inscription. The 1982 scan was image-only, with native extraction yielding page separators. We preserved extracted text as a source aid and rendered pages for manual checks; OCR glyph strings were excluded from tokenization.

The [extraction assessment](../../research/corpus/primary/1979_extraction_assessment.md) and structured source definitions settled several questions before template matching. The chart's upper number is a rank shared by variants; the lower number is the stable Finnish code. Dashed lines beneath chart drawings are uncertainty annotations under §5.4/§6.6, rather than glyph components. The font came from plotted subroutines using CalComp1039/BurroughsB6700 machinery, with Seppo Koskenniemi credited for subroutines. Standardized source drawings made image-template digitization worth testing, but the editorial marks required separate treatment.

The 1980 volume clarified that original line/side boundaries were sometimes indicated only through classification or omitted using parallel texts. Its printed 13–14 conventions cover intended gaps and multiple lines/sides. Printed 54–57 already distinguishes strict duplicate processing within object/iconography groups from loose whole-corpus matching, including conservative fragment compatibility. The primary-source acquisition supplied both a future digitization route and prior methodology for repetition controls.

### Other access attempts

| Route | Outcome and preserved consequence |
|---|---|
| Parpola 2011 Harappa PDF | Direct request 403; visible PDF download succeeded. Completed temporary download bytes were checked and copied. Acquired 65-page source supplied H697B Fig 15. |
| Kenoyer/Meadow 2010 *Inscribed Objects* PDF | Same ordinary browser route after 403. Acquired 15-page text excerpt has no figures; source context/identifier prose was usable. |
| Parpola 2020 bone rods | Public HELDA/TUHAT content acquired, 7 pages. URL-year2019 was separated from publication-year2020. H697 comparison remains a prose witness. |
| HARP gallery images | Public caption/image links acquired through supported browser media controls after failed direct requests. Captions lack object IDs for the grouped specimens. |
| Fuls 2022 corpus | Public 35-page view-inside excerpt inspected; complete numerical corpus not acquired. |
| Fuls 2012/2020 author routes, coordinated with literature | Academia route reached a login agreement and stopped. ResearchGate text was indexed, but direct PDF acquisition failed; Fig 16 pixels/historical ID remained unavailable. |
| CISI2/3 | Complete primary volumes remained unacquired; later Harappa/Mohenjo plates could not be checked merely by finding a derivative image. |

Literature maintained the broader acquisition log. An early guessed Sproat 2010 ACL URL retrieved an unrelated NLP book review; title inspection identified it and the correct J10-3012 source was acquired. The older RMRL bulletin URL returned 404 before the official 2025 S3 link was found. Yadav 2017 returned a PDF but text extraction failed with `DescendantFonts`, so download success and parser success were separate outcomes. Airavati 2008 was acquired through its publisher HTTP link after an HTTPS certificate issue. RMRL flipbook configurations/pages were retained as source files, not relabelled as our JavaScript. Those witnesses remain in the local literature archive with identities and hashes.

## Primary plate audit

The literature agent acquired the official IGNCA CISI1 scan. Its862 PDF pages contain two identical431-page copies of the book, with every page's extracted-image hash set matching at offset 431. Printed pages in the first copy follow PDFpage−36. The introduction and corrigenda established extra-photo suffixes, impression labels, deleted duplicates, mirrors and swapped sides. These were carried into catalogue caveats.

Our seeded plate audit selected 25 Mayig objects using seed 20261001 from an initial zero-default/single-line frame. It deliberately retained the subsequently discovered damaged/layout cases. The object list was M8, M16, M34, M58, M65, M73, M77, M81, M93, M94, M107, M115, M129, M132, M135, M140, M141, M144, M147, M150, M152, M173, M178, M181 and M183. Source captions were located, images rendered, and a descriptive shape pass saved before catalogue-informed adjudication. The [selection](../../research/corpus/plate_audit/selection.json), [blind notes](../../research/corpus/plate_audit/blind_visual_notes.json), [comparisons](../../research/corpus/plate_audit/comparisons.json) and [adjudications](../../research/corpus/plate_audit/adjudications.json) preserve the stages.

Seventeen of 24 source-complete cases were broadly compatible across catalogues; seven had segmentation, allograph, crosswalk or damage discrepancies, with M141 as a layout negative control. The sample tested particular provenance problems rather than estimating population accuracy. The first descriptive pass made mistakes; its records remain beside the revisions.

M81 showed two grid units where Mayig/Wells segmentation differed and a caret/stem code difference. M140's photograph supported a short pair against Mayig's tall code. M181's decorated triangle exposed an omitted crosswalk feature. M152's small strokes decorated a compound U-type glyph instead of constituting separate units. M115's844/845, M173's900/920 and M150's832 fine variants remained unresolved. M73 had visible breakage despite eligibility flags. These cases informed later source-quality sensitivities through explicit lists, while raw transcriptions stayed unchanged.

### Fish-adjacent short and tall stroke pairs

The [targeted audit](../../research/corpus/plate_audit/fish_strokes/README.md) selected 13 physical objects and 14 fish-adjacent pair events: M7,35,42,43,46,81,86,89,91,107,140,144,147. M46 supplied two fish events. Ten pairs were clearly short, two tall (M89/M91), and one short pair had grouping uncertainty (M43). M91 included both short and tall pairs on one face.

Image-height ratios relative to the nearby glyph ranged .291–.500 for short and .883–1.139 for tall. A conservative±20-pixel exercise left short upper bounds at .608 and tall lower bounds at .743/.973. These were source-image measurements with stated crop uncertainty; no archaeological unit or numeric coefficient was fitted. M140 showed one catalogue disagreement; the later M62 inspection showed the reverse catalogue disagreement. The [observations](../../research/corpus/plate_audit/fish_strokes/observations.json) and crop manifest preserve the measured graphics.

### W176/W904, H697, H2238 and H904

Methods exported eight rows spanning six sequences and three identical-whole contexts for W176/W904. The sources were H2200/H1897; M289/H697 plus a no-CISI row/H1100; H2139/Ad3. M289's CISI1 printed 70/PDF 106 photograph confirmed the five broad glyph positions and tiger/trough motif. Exact fine variants remained open. H697A and Ad3 were available through derivative Lipi images. Parpola 2011 Fig 15 independently reproduced H697B, U motif plus two tall bars and two horned animals; its obverse A was absent. H2200, H1897, H2139 and H1100 primary plates remained missing.

Literature found that the exact Ad3/H2139 contrast was already diagrammed in RMRL 2025 Fig 6, printed 17/PDF 23. The source comparison was added to the novelty review. The [original status file](../../research/corpus/plate_audit/pair_176_904/audit_status.json) predates acquisition of the B reproduction; the [B addendum](../../research/corpus/plate_audit/pair_176_904/H-697B_primary_reproduction.json) and final report give the later state. Their dates explain the apparent discrepancy.

For H2238, Meadow/Kenoyer 2000 Fig 4 specimen 18 and its caption identify H95-2613/6560-01. The middle face clearly shows three short bars and a diamond-like unit. The dense opposite-face hatching prevented a confident three/four long-bar count. Public HARP photographs separately show four bars in Group 1 and three in Group 2 beside a joined two-armed motif, but provide no specimen IDs. The [individual audit](../../research/corpus/plate_audit/H2238_face_audit.json) and [gallery observations](../../research/corpus/plate_audit/H2238_gallery/gallery_provenance_observations.json) therefore retain individual and cohort observations separately.

A bounded query for W700/W900 with W032 or 033 produced one current Lipi face, 1786.2/H904, preserving both raw faces. Literature then acquired Vats 1940 Plate XCVI no 477 and printed 349 table J213, area D. Three long strokes on the U face and two next to circles were visible; short marks were less clear. Fuls's historical ICIT3786 correspondence remained unconfirmed without Fig 16, and current 3786 refers to M1540. The [H904 query record](../../research/corpus/plate_audit/H904_current_pattern_candidate.json) preserves the candidate identity and source strings. The parent numerical audit carries the conditional equation results and the unresolved M1383 object/count/unit join.

## Searching for a photo-constrained missing slot

The parent restoration benchmark hides exactly one known code by construction. We searched primary photographs for a real damaged case whose extent independently supports that assumption, keeping model predictions out of selection.

All 17 Mayig faces with exactly one P000 were inspected. None securely fixed the lost extent at one glyph. M169 was initially tentative, then rejected after a wider crop showed room for multiple units and historical Lipi used two000 positions. The [blind observations](../../research/corpus/plate_audit/restoration_slots/primary_blind_observations.json) and [adjudication](../../research/corpus/plate_audit/restoration_slots/adjudication.json) preserve the change.

A second exhaustive frame selected seven Lipi M1–M650 rows with one internal000: M61,62,167,168,477,636,646. Five had acquired CISI1 plates, whose original Mohenjo photographic sequence ends at M620. M636/M646 lacked acquired primary plates. M167 had broad spalling, M168 edge loss and M477 extensive weathering. M61 preserved a bounded motif, already assigned MayigP251/W081 with damage30/uncertainty90. M62 preserved a U, already P310/W700, and showed the short/tall catalogue issue beside its fish graphic.

The result was zero new certified one-slot restorations. M61 offers comparison to an uncertain historical reading; M62 offers a catalogue recoding comparison. [Candidate frame](../../research/corpus/plate_audit/restoration_slots/lipi_internal/candidate_frame.json), [blind source notes](../../research/corpus/plate_audit/restoration_slots/lipi_internal/primary_blind_observations.json) and [historical adjudication](../../research/corpus/plate_audit/restoration_slots/lipi_internal/historical_reading_adjudication.json) record every selected case. A useful retry needs a new primary witness with photo-constrained extent or independent later resolution.

## Building the numerical chart reference

The parent image prototype extracted templates from the standardized 1979 chart, but OCR numeric labels were poor. Our first blind task read the 35 lower codes in PDF 20 column 0 from the original image, retaining upper ranks and confidence. An early automatic label comparison recovered27/35. Numerical-font experiments preceded the decision to annotate the entire 687-cell chart manually across agents.

We owned PDF 20 columns 0–4, 175 cells. Literature owned the other PDF 20 columns and later independently checked PDF 21; root read PDF 21. Our 140 new cells were read at 6×, rechecked at 12× and ambiguous digits inspected at 20×. The original first-column reference was preserved; reinspection corrected row 4 from 585 to 586 and marked14 dashed auxiliary underlines. Row34's solid platform belongs to the glyph. Other within-source fixes included356→366,358→368,352→382 and 475→476 in their recorded cells.

Cross-annotator comparison prompted subsequent source reinspection. PDF 20 c2r1 changed 359→369 and c4r13 changed 350→360. At c4r21 literature preferred 465 while this annotation retained 486; the consolidated union is 465/485/486. Literature's later upper-rank 85 reading at c4r1 was corrected to 86 through a 24× source crop, while lower 506 was retained even though repeated elsewhere. These changes are explicit overlays in [subsequent adjudication](../../research/corpus/primary/chart_complete/subsequent_adjudication.json), with old references and drafts preserved.

The final [reference](../../research/chart_reference/manual_numeric_reference.json) contains 687 unique expected chart cells and 16 lower-code ambiguities. Our [consolidated atlas audit](../../research/corpus/primary/chart_complete/consolidated_atlas_audit.json) checked source/overlay correspondence, exact coverage, all 687 PNG crop pixels, PDF hash and frozen-file pins. It found no mismatch. The atlas crops include context ink in some cells; pixel provenance and numerical annotation are separate checks. The final reference SHA256 is `09cc31162ff68ddb908953a612df3505a64c93b1ae5a472f236a0b52df240b29`.

## Font-transcription pilots and acquisition failure

The first pilot used PDF 30 columns 0/1 rows 3–7, printed IDs1018–1022 and 1054–1058. We compared each drawing with the original chart, preserving candidates, underlines and auxiliaries. The reference had 61 drawn units, 57 single-code assignments and four fine-code ambiguities. Original physical side/line boundaries remained unknown.

A partial description of row 1020 reached root before predictions froze. This occurred while root corrected a template-crop contamination: the left edge included the last digit of a numeric label. The full reference was released after the corrected predictions froze. All four penalty endpoints remain preserved; the ten-row sample is development. An accidental broad text search later exposed small machine-output fragments after this reference had been released; no source assignment changed, and it was disclosed. Fresh20 annotations stayed source-only.

The fresh20 sample used seed 20261015 over PDF 30 columns 0/1 rows 8–34. We withheld every code/count/detail until root reported the fixed-penalty 1 predictions frozen. All 20 rows were retained. The [reference](../../research/corpus/primary/font_fresh20/manual_reference.json) contains 96 modern drawn units: 91 glyph drawings plus five editorial auxiliaries. Two rows are whole-loss rectangles, four contain loss/inaccessibility, ten units retain fine-code ambiguity, and six underlines are recorded. Its SHA256 is `061130347c5feb52acb79427e672fade16b553e10aab00fb6c1fca493172e279`.

| Endpoint | Predicted units / reference | Correct row counts | Strict top1 summed candidate-set edits / whole-compatible rows | Top5 edits / whole-compatible rows |
|---|---:|---:|---:|---:|
| First10, corrected templates, penalties0.5/1 | 61/61 | 10/10 | 15 / 2 | 4 / 6 |
| First10 excluding partially disclosed1020 | 52 reference units | Recorded in audit | 11 / 2 | 3 / 6 |
| Frozen fresh20, penalty 1 | 107/96 | 14/20 | 69 / 2 | 60 / 5 |
| Post-reference fresh20 clean-crop development, unchanged matcher/chart/penalty | 96/96 | 18/20 | 24 / 6 | 6 / 16 |

The [methods audit](../../research/methods/FONT_PILOT_AUDIT.md) independently recomputed candidate-set distances and file pins. Top1 means one image template with its retained numerical alternatives; top5 means five template alternatives. The counts are drawn units, including editorial graphics. Original rows can combine ancient boundaries.

After the failed frozen endpoint, root noticed cut-off glyphs and neighbouring ink. We audited all 20 frozen crops against the original source, without consulting predicted codes. All stored PNGs exactly matched frozen coordinates. Eighteen crops cut into target upper ink: 14 clear cuts of 1.5–8.75 points and four marginal .25-point cuts. Fourteen contained the following row's upper ink; none cut target bottoms or included preceding-row ink. Only 1023/1024 were complete with margin. The fixed 40.25-pixel pitch at 2× drifted against roughly 39.6-pixel source spacing and column offsets.

The [geometry findings](../../research/corpus/primary/font_fresh20/geometry_audit/manual_geometry_findings.json) retain each row diagnosis and context. We supplied source-only [clean vertical bounds](../../research/corpus/primary/font_fresh20/geometry_audit/recommended_clean_bounds.json), preserving original horizontal limits. Methods reran the unchanged matcher, penalty and frozen14-ambiguity chart in a separately labelled post-reference development diagnostic. Its improvements locate a substantial acquisition defect; residual24 top1 edits and six whole-compatible rows leave fine-code recognition unfinished. The [evaluation](../../research/methods/results/font_geometry_sensitivity/evaluation_post_reference.json) preserves both endpoint summaries. Fresh validation requires new rows and a crop procedure frozen before annotation/output.

## Reviewing alternate-annotation provenance

Root tested all 94 clear Mayig faces rather than choosing only matches to Lipi. Eligibility left 86 single-line texts of length at least 3; 81 mapped through direct candidate sets and 74 had supported events, representing 73 unique P texts. Source and compatible-whole-text exclusion removed 170 of 1,596 training texts. The reported candidate-event gain was +0.7248 bits, CI [0.551, 0.899]. Methods reviewed the probability calculation; we reviewed source order, maps, clear flags and identity matching.

The [provenance review](../../research/corpus/independent_annotator_provenance_review.json) found zero direct-mapping, reversal or clear-flag errors and no conflicting numeric-family assignment for simple physical bases. The full export contained195 M1–199 families versus155 in clean eligible data; the 40 omitted families contributed no retained eligible rows, so the narrower identity scan caused no observed training overlap at this pin. We recommended discovering source identities in the full register before filtering. The evaluation concerns another annotation of shared photographs with shared catalogue candidates; its supported-event and coverage denominators stay explicit.

## What to carry into the next run

| Unresolved path | New evidence or method that justifies another run | Existing record to read first |
|---|---|---|
| Complete independent coded corpus | Newly accessible primary token data, licensed corpus, or expert-validated digitization block | Acquisition manifests, extraction assessment, source inventory. |
| Font digitization | Fresh source rows; crop algorithm, chart snapshot and matcher frozen before reference; original-boundary audit | Fresh20 reference, frozen predictions and geometry diagnosis. |
| Exact graphic crosswalk | Feature-aware token-level expert adjudication on primary photographs | P→W schema, seeded plates, fish-stroke disagreements. |
| One-slot restoration | Photographically bounded one-glyph extent and later independent resolution, with rare-code calibration | Both exhaustive candidate frames and rejected cases. |
| Numerical anchors | Fuls Fig 16 physical-ID witness, M1383 object/content join and independent unit/count evidence | H904 query, Vats/Vidale source-premise audit, numerical methods retrospective. |
| Context prediction | Primary item/context joins and adequate within-site/phase label variation | [Context data plan](../directions/context-data-plan.md), metadata summaries. |

Preserve the original failed crop endpoint and numerical references when testing improvements. Avoid rerunning same-number cross-version joins, OCR glyph tokenization, whole-face reversal of unknown boundaries, or P000-as-one-slot selection. Their defects have named source evidence. Better primary plates, improved acquisition geometry, independent annotation and physical context joins are the remaining routes to a source-tested advance.
