"""Write corrected prose; preserve original numerical endpoints and source labels."""
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
FOLLOW='follow-up/2026-10-07'
ANALYSIS=FOLLOW+'/analysis-v1'
REPAIR='repair/2026-10-07-v2'


def read(name):return json.loads((HERE/name).read_text(encoding='utf-8'))


def main():
    if (HERE/'repair/2026-10-07-v2/evaluation-2026-10-07-adjudicated/metrics.json').exists():
        import write_repaired_endpoint_docs
        return write_repaired_endpoint_docs.main()
    first=read('evaluation/2026-10-07-frozen-v1/metrics.json');s=first['summary']
    cal=read(ANALYSIS+'/calibration-upright-only.json');q=read(ANALYSIS+'/triage-summary.json')
    freeze=read(REPAIR+'/freeze-manifest.json');pf=read(REPAIR+'/prediction-freeze.json')
    interface=read(FOLLOW+'/ledger-interface-v2.json');selection=read(REPAIR+'/blind/selection.json')
    c=cal['calibration'];changes=read(ANALYSIS+'/adjudication-overlay.json')['changes']
    change_rows='\n'.join(f"| {r['sample_index']} | {r['unit_index_zero_based']} | {r['old']} | {r['adjudicated']} | {r['reason']} |" for r in changes)
    def proportion(item):return f"{item['success']}/{item['total']} ({100*item['rate']:.1f}%; 95% CI {100*item['ci95'][0]:.1f}–{100*item['ci95'][1]:.1f}%)"
    report=f'''# Helsinki 1979 digitization: corrected first endpoint and repair status

The first pipeline failed all four reliability criteria. Its **60-row evaluation covers only numbered-section targets from PDF pages 31–79, drawn from 3,460 of the 11,369 detected occurrences; no sorted-section row was evaluated**. In that frame it has 33 matching unit counts, 23 exact numbers and 24 compatible whole rows within five templates. These original outcomes and references remain unchanged. The [Sonnet review](REVIEW.md) confirmed all 43 checked headline numbers and diagnosed page geometry as the main limitation.

The repair now has a frozen method and 80-row sample across all three sections. Its two independent readings, source-count reference, adjudication and evaluation remain unfinished after the disk cutoff was triggered. No repaired accuracy is reported and no row has been released from quarantine. [Stop record]({FOLLOW}/storage-stop-v2.json).

## First endpoint: numbered-section frame only

Every figure in this table uses the original 60 numbered-section rows from PDF 31–79 (detected frame 3,460/11,369; zero sorted-section targets). The code metrics compare the original AI reference labels, including the errors subsequently found by review.

| Original outcome in that frame | Result |
|---|---|
| Annotator crop acceptance | {proportion(s['row_crop_correctness'])} |
| Drawing-unit count agreement | {proportion(s['drawn_unit_count_agreement'])} |
| Exact inscription number, with suffix | {proportion(s['inscription_number_accuracy'])} |
| Exact classification, with blank positions | {proportion(s['classification_exact_accuracy'])} |
| Compatible whole row, top one | {proportion(s['strict_top1']['whole_rows_all_sample'])} |
| Compatible whole row, top five | {proportion(s['strict_top5']['whole_rows_all_sample'])} |
| Exact sequence on singleton-reference rows | {proportion(s['uniquely_resolved_exact_sequence'])} |

Exact fields are [metrics.json](evaluation/2026-10-07-frozen-v1/metrics.json), `summary`. The same 60-row frame contains 267 reference drawings (229 glyphs and 38 editorial units) against 288 proposals. Aligned compatible recall is 199/267 at top one and 224/267 at top five; candidate-set edits total 95 and 71. Equal-count same-position accuracy is 103/140 and 118/140 on 33 rows. The stored row-bootstrap intervals are `row_bootstrap_95`. Aligned recall does not penalize extra proposals; whole-row compatibility requires equal counts and ordered candidate intersections. Five templates can carry more than five codes when the chart has an ambiguous lower label: the mean is 5.208 codes and maximum eight in this sample.

The crop labels need a narrower interpretation. A accepted 4/20 boxes and B 3/20, together 7/40; C accepted 16/20. Nine of C's accepted boxes fail the review's edge/fragment tests even with a 1 PDF-point crossing tolerance; eleven fail with no tolerance. The post-outcome objective audit passes 14/60 boxes without tolerance (95% CI 14.4–35.4%) and 21/60 with a 1-point tolerance (24.2–47.6%). Those are additional Exploratory observations in the same numbered-section frame, and do not replace the frozen 23/60. See [crop-and-frame.json]({ANALYSIS}/crop-and-frame.json), `per_annotator`, and [review crop audit](review/reviewer-check/diagnosis/crop-audit-summary.json), `variants`.

Source OCR strings were exposed in 22 original locators. Excluding those rows gives 13/38 exact numbers (95% CI 21.2–50.1%) within the same numbered-section frame. Glyph predictions and proposed counts were withheld from the annotators. The review independently reread 30 rows and matched all 30 for count, number and classification. Its rereading was post-outcome; it audits the reference rather than supplies a new blind estimate.

## Reference adjudication and calibration

The following **zero-based unit positions** are review adjudications, recorded on 7 October 2026. Frozen references have not been edited. Sources are [unit-adjudication.json](review/reviewer-check/unit-adjudication.json), [tick-position-check.json](review/reviewer-check/diagnosis/tick-position-check.json) and the review's source images. The [overlay]({ANALYSIS}/adjudication-overlay.json) stores the original and adjudicated code sets.

| Sample | Unit | Original set | Adjudicated set | Source observation |
|---|---|---|---|---|
{change_rows}

The chart places code 25's two short strokes high in its sign box and code 2's pair near the middle. Tight chart crops removed this distinguishing position. The repair's source-reading cards retain the original cell position. The narrow/wide hatched variants and uncertainty underlines also need separate labels. The review found the repeat reader correct on both previously reported candidate-set disagreements.

The six repeats were fixed convenience indices 5, 13, 30, 35, 42 and 51, two in each 20-row primary group. No RNG or probability-selection rule was recorded. The original protocol calls them prespecified before annotation; its paragraph-level timing cannot be independently isolated. Their count/number/classification agreement of 6/6, candidate agreement of 4/6 and four crop disagreements describe those six rows only.

Calibration uses the original references and coefficients. In the original numbered-section 60-row frame, 140 same-position units in equal-count rows give Brier score 0.1488 (row-bootstrap 95% CI 0.107–0.197) and ten-bin error 0.1056 (0.080–0.185). Excluding all three inverted selected rows leaves 57 sampled rows and 126 scored units: Brier {c['brier']:.4f} (0.096–0.164) and ten-bin error {c['ece10']:.4f} (0.074–0.179). This sensitivity is Exploratory, uses 2,000 row-bootstrap draws with seed 2026100707, applies no adjudications and refits no model. [Calibration output]({ANALYSIS}/calibration-upright-only.json), `calibration` and `ci95`. These quantities are conditional on matching counts and do not qualify clipped rows or object identity. The [original figure](figures/validation.png) still plots the original 60-row numbered-section endpoint, not this sensitivity or the repaired sample.

## Full first extraction and row-recall evidence

The full first run attempted PDF 22–180: 159 pages, 11,369 detected occurrences, 57,426 unit proposals, 10,425 recognized number strings and three unmatched units. Section totals are 4,036 numbered, 3,743 end-sorted and 3,590 beginning-sorted occurrences; the sorted sections contain 64.5% of that extraction and had no original evaluated row. [Coverage](runs/2026-10-07-full-v1/coverage.json), `counts` and `pages`.

**All 17 pages rotated by the heuristic are upright in the source.** Their 1,223 inverted occurrences are flagged `orientation_unreliable` in the separate [orientation overlay]({ANALYSIS}/orientation-overlay.json). The original payload has not been changed. The affected sorted-section proportions are 575/3,743 (15.4%) and 576/3,590 (16.0%); 72 numbered-section rows are also affected. The review verified 13 page orientations from header content and four by viewing.

Twenty pages have fewer than 72 detections. Their numbers and counts are in [row-recall-evidence.json]({ANALYSIS}/row-recall-evidence.json), `short_pages`. The review counted 36 printed rows in page 62 column 0, where the first pipeline found 21: count coverage 21/36 (58.3%; Wilson 95% CI 42.2–72.9%). This is a count comparison, not a corpus-wide matched-row recall estimate. Pages 129–130 print five to eight columns; the first method searched two. Fewer than 72 detections can also reflect a partial page, so it does not establish a missing-row count by itself. An independent true-row denominator remains unfinished.

The active [triage queue]({ANALYSIS}/triage-queue.jsonl) contains {q['queued_rows']:,} rows, leaving {q['not_in_triage']:,} outside triage. Priorities contain 1,352 orientation/column/recall cases, 4,324 clipping/fragment cases, 723 field/order cases and 3,185 remaining repeat-disagreement cases. It uses native edge crossings of at least one point, narrow number-edge units, unresolved fields, unmatched ink, numbering violations and candidate disagreements between unverified number groups. It omits the universal boundary/classification flag and the old confidence cutoff that queued every row. **All 11,369 remain quarantined**, including rows outside triage. [Summary]({ANALYSIS}/triage-summary.json), `reason_counts` and `priorities`.

## Repair development, freezing and unfinished evaluation

The review measured mean field drift of +7.4 PDF points on even pages and −3.2 on odd pages, with offsets from −11 to +18. It found the correct code among five proposals for all 198 size-consistent units examined; its resolution tests found no benefit from increasing the working render above two pixels per point. The native scan is 601 dpi bilevel. These are conditional, post-outcome diagnoses. Its offset/orientation rerun on the old numbered-section 60-row frame yielded 44 matching counts, 40 numbers and 35 top-five whole rows, compared with the frozen 33, 23 and 24. It supplies development evidence and no fresh accuracy estimate.

The new layout localizes field coordinates from OCR word boxes without trusting their digit strings, checks compact multi-column pages through print projections and internal whitespace, and uses source-header content for upright orientation. It detects vertical field bands and intervening glyph whitespace without fixing row counts. On development pages the detector found 72 rows on pages 30, 62, 100 and 145, eight columns/288 rows on 129 and six columns/201 rows on 130. These are detector outputs, pending independent source counts. The known page-30 development reference gives 17/20 matching counts, 19/20 numbers, 6/20 top-one and 12/20 top-five whole rows. [Development output]({FOLLOW}/development-recognition-v1.json).

The first repair candidate's unlabelled frame exposed false field columns from glyph-like OCR. It was superseded before any independent reading, with all artifacts preserved in `repair/2026-10-07-v1/`. The replacement adds a 35-point margin-neighbourhood restriction on ordinary two-column page types; compact printed columns remain detected separately. Its [freeze]({REPAIR}/freeze-manifest.json) at {freeze['created_utc']} includes layout, sampling and evaluator hashes plus the unchanged original recognizer, digits, chart and calibration. Its [prediction freeze]({REPAIR}/prediction-freeze.json) at {pf['created_utc']} precedes every new reference: none exists.

| Evaluation component | First endpoint | Repaired endpoint |
|---|---|---|
| Frame | 60 numbered-section rows, PDF 31–79; 3,460/11,369 detected rows; no sorted target | 80 rows: 28 numbered, 26 end-sorted, 26 beginning-sorted; eligible denominators 3,596 / 3,228 / 3,496 |
| Independent readings | One primary reader per row; six convenience repeats | Two readings per row and source-only adjudication required; not started |
| Counts / numbers / top-five whole rows | 33/60 / 23/60 / 24/60 in the stated first frame | Pending |
| Row recall | No overall true-row denominator | 18 seeded pages plus stress pages 62,129,130 prepared; source count pending |
| Calibration | Original and upright-only sensitivity above | Pending |
| Quarantine | All 11,369 occurrences | No release allowed before evaluation and the frozen rule |

The 80-row sample uses seed 2026100780, excludes development pages and the old 60 targets, and includes both sorted sections. The prepared count frame has 21 pages. Two readers must independently annotate all rows and visually count/match every source column; a third source-only reader adjudicates before scoring. The [convention sheet]({REPAIR}/blind/CONVENTIONS.md) preserves vertical tick position and editorial distinctions. Thresholds remain 90% crop/number accuracy, 95% count agreement and 80% top-five whole rows, with a new 95% random-page row-recall criterion. The frozen release rule further requires singleton codes, numeric-witness agreement, no unresolved geometry/auxiliaries, minimum unit confidence 0.90 and confidence product 0.90. It permits transcription eligibility only; a carrier import still needs reviewed identity and surface alignment.

Disk checks are in [storage-preframe-check-v2.json]({FOLLOW}/storage-preframe-check-v2.json) and [storage-stop-v2.json]({FOLLOW}/storage-stop-v2.json). Free space fell to 917,327,872 bytes and then 256,331,776 while the helper was active. The 60,522,244-byte frame had already been written by the failed gate check; the helper completed before interruption. This exposed a missing in-process pre-write gate. The completed artifacts are retained; no further evaluation or full run was started. Space recovered after the helper exited. This does not erase the recorded cutoff failure.

## Portable evidence and Package L

The unchanged evaluator can now read the exact frozen predictions from an owned portable input root. The existing digit NPZ, all 60 source crops and nine chart sheets are listed with hashes in [portable-input-manifest.json]({ANALYSIS}/portable-input-manifest.json) and [TRACK-EXCEPTIONS.txt](TRACK-EXCEPTIONS.txt). Tracking exceptions still require coordinator integration. The [retrospective freeze supplement]({ANALYSIS}/freeze-supplement.json) records the evaluator hash without backdating it. The portable rerun is byte-identical to the original metrics: SHA256 `5cd4b8df754a4284b8bdb7e333f9b2b860cdb377b1f47698533e613c0fcc8c06`.

Package L's available [contract](../2026-10-07-object-ledger/HELSINKI-INTERFACE.md) and review-response amendment are now implemented by `import_helsinki1979_v2.py`. Its requested `IMPORT_INTERFACE.md` is absent. A read-only check exercised 63 existing provisional occurrences, including three letter-suffixed strings: all schema checks passed, zero were accepted and all 63 were quarantined without identity/surface concordances. [Interface check]({FOLLOW}/ledger-interface-v2.json). No Package L file or ledger was changed. The four inspected 1980 Finnish-to-Mahadevan pairs remain local and supply no verified CISI/carrier join.
'''
    readme=f'''# Package M: Helsinki 1979 digitization

**First endpoint:** 60 numbered-section rows from PDF pages 31–79, drawn from 3,460 of 11,369 detected occurrences; no sorted-section row was evaluated. In that frame the frozen pipeline has 33/60 matching counts, 23/60 exact numbers and 24/60 top-five compatible whole rows. It fails all four criteria. The corrected [report](REPORT.md) gives the per-annotator crop labels, objective audit, adjudication overlays and orientation findings.

**Repair status:** method and 80 predictions are frozen across the whole edition (28 numbered, 26 end-sorted, 26 beginning-sorted). Two independent readings, source-count adjudication and new metrics remain pending after the disk cutoff. All 11,369 original occurrences remain quarantined. The active triage subset has 9,584 rows and flags all 1,223 inverted occurrences. The original frozen files and references are unchanged.

## Main files

- [Original protocol and dated amendments](PROTOCOL.md).
- [Original 60-row metrics](evaluation/2026-10-07-frozen-v1/metrics.json), `summary`; the frame above qualifies every accuracy figure.
- [Original full coverage](runs/2026-10-07-full-v1/coverage.json): 159 attempted pages, 11,369 occurrences, 57,426 candidates.
- [Corrections and adjudication]({ANALYSIS}/adjudication-overlay.json); [crop audit restatement]({ANALYSIS}/crop-and-frame.json).
- [Active triage]({ANALYSIS}/triage-queue.jsonl); [orientation flags]({ANALYSIS}/orientation-overlay.json); [row-recall evidence]({ANALYSIS}/row-recall-evidence.json).
- [Upright-only calibration sensitivity]({ANALYSIS}/calibration-upright-only.json): 126 units in the original numbered-section frame, Brier 0.1262 and ten-bin error 0.1183.
- [Repaired freeze]({REPAIR}/freeze-manifest.json), [prediction freeze]({REPAIR}/prediction-freeze.json), [source-only locator]({REPAIR}/blind/selection.json) and [reading conventions]({REPAIR}/blind/CONVENTIONS.md).
- [Disk stop and exact remaining work]({FOLLOW}/storage-stop-v2.json), [retrospective](RETROSPECTIVE.md), [registry proposal](registry-entry.json), [source register](sources.json) and [import contract](IMPORT_INTERFACE.md).

## Portable first evaluation

The coordinator must apply every path in [TRACK-EXCEPTIONS.txt](TRACK-EXCEPTIONS.txt), including the digit NPZ and images. The exact owned prediction copy and image hashes are in [portable-input-manifest.json]({ANALYSIS}/portable-input-manifest.json). JSON references and frozen code are already owned. The evaluator hash is in a [dated supplement]({ANALYSIS}/freeze-supplement.json); the original freeze manifests remain unchanged. The portable command uses only NumPy and no original PDF, GPU, model inference or local raw predictions. [requirements.txt](requirements.txt) pins NumPy 2.5.3. The original recognition replay additionally needs the acquired PDF, PyTorch and recorded environment.

Run from the repository root with a fresh output directory:

```powershell
& 'C:\\Users\\sandh\\.venvs\\indus-ml\\Scripts\\python.exe' experiments/2026-10-07-helsinki1979-digitization/portable_evaluate.py --out experiments/2026-10-07-helsinki1979-digitization/review/reviewer-portable-v3
```

Both local portable replays reproduce the original metrics byte-for-byte. Recompute corrections with `respond_to_review.py --out <new-owned-directory>` and the L check with `check_ledger_followup.py --out <new-owned-file>`; these need the preserved local full extraction and reviewer diagnostics. They preserve the first endpoint. `write_docs.py` now delegates to `write_followup_docs.py` for the corrected prose.

## Resume the repaired evaluation

Use the existing v2 freeze and source-only sample; do not regenerate it over the endpoint. Assign two independent readers every row and count page under the convention sheet, then a third reader the disagreements without predictions. Required final reference files are `repair/2026-10-07-v2/blind/adjudicated-reference.json` and `adjudicated-counts.json`. Preserve both initial readings and the adjudication. Only then run:

```powershell
& 'C:\\Users\\sandh\\.venvs\\indus-ml\\Scripts\\python.exe' experiments/2026-10-07-helsinki1979-digitization/evaluate_repair.py --out experiments/2026-10-07-helsinki1979-digitization/review/repaired-evaluation-v1
```

`prepare_repair_v2.py` created the replacement code once; it is a historical construction helper and must not be rerun over frozen files. `freeze_repair_v2.py` refuses existing freeze/prediction endpoints. A methodological repair after reference requires a separate dated freeze and new sample.

Before any operation writing more than 50 MB, check free space **inside the active process immediately before serialization**, after library/model loading. If below 1,000,000,000 bytes, stop and record unfinished work. A caller-only check proved inadequate during this run. Render source pages one at a time in memory. The repaired full run and confidence-based release are unfinished. Package L still requires a reviewed carrier concordance and occurrence-surface alignment.

## Attribution and reviewer checks

Source-derived crops, chart cards and transcription: Kimmo Koskenniemi and Asko Parpola, *Corpus of Texts in the Indus Script* (1979), Research Reports 1, Department of Asian and African Studies, University of Helsinki; [handle](http://hdl.handle.net/10138/342677), [institutional licence](https://researchportal.helsinki.fi/en/publications/corpus-of-texts-in-the-indus-script/), [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Changes are raster cropping, card arrangement, numerical recognition and source annotation. The 1980 copied table rows and images remain local because their licence is unverified. This source licence does not assign a blanket licence to our code.

- Check ignored-asset exceptions and run portable evaluation from a checkout without local raw predictions.
- Confirm every first-endpoint hash against the preservation check, and that references still carry the original labels.
- Inspect the eleven adjudication entries and high/centered tick convention in untrimmed chart cells.
- Verify the 1,223 orientation flags, subset triage and the source-count limits on pages 62,129,130.
- Complete the two blinded readings and adjudication before opening repaired predictions for scoring.
- Confirm suffixes and occurrence segments pass L's schema while unsupported joins stay quarantined.
- Run `python tools/review_prose.py --path experiments/2026-10-07-helsinki1979-digitization --no-write`.
'''
    retrospective=f'''# Retrospective: Helsinki 1979 digitization

The first pipeline failed its frozen test of **60 numbered-section rows from PDF 31–79 (3,460/11,369 detected occurrences; no sorted target)**: 33 matching counts, 23 exact numbers and 24 top-five compatible whole rows. The full first run preserved 11,369 provisional occurrences across 159 pages. Its source witnesses, predictions, references and numerical endpoints remain unchanged. Original prose is retained in `{FOLLOW}/*.before-follow-up.txt`.

## First run and review evidence

The first run replaced fixed vertical pitch with observed number bands and glyph whitespace, reused the 687-cell chart and known page-30 reference, and combined sparse chamfer distances with chart-only CNN augmentation. A dense development matcher was interrupted for speed; a sparse implementation was frozen before source reading. The final development counts were 17/20 with 6/20 and 12/20 top-one/five whole rows. Static horizontal regions and a density-based orientation score remained.

Three readers supplied disjoint primary groups; original OCR strings accidentally remained in 22 locators. Those strings were removed from a separate copy, exposure was disclosed and the initial references retained. Six fixed convenience repeats, two per primary group, exposed glyph and crop disagreements; no random selection rule was recorded.

The Sonnet review confirmed 43 headline numbers and independently matched 30 source rows for count, number and classification. It found all 17 rotated pages upright, 1,223 inverted strips, asymmetric field drift and missing/fragmented crops. A/B accepted 7/40 crops; C accepted 16/20, including nine with objective defects under a 1-point tolerance. The objective audits pass 14/60 and 21/60 with that tolerance in the same original numbered-section frame. These results are appended as corrections, not substituted into the frozen evaluation.

## Coordinator corrections, 7 October 2026

Copied the frozen prediction bytes into an owned portable input root, retained digits/crops/chart sheets, listed tracking exceptions and added a retrospective evaluator-hash supplement. Two portable replays match the original metrics SHA256 exactly. Replaced the active universal queue with 9,584 triaged rows, retaining 1,785 outside triage and all 11,369 in quarantine. The separate orientation overlay flags all 1,223 inverted occurrences. The row-recall record lists 20 short pages, page 62 column 0's 21 detections against 36 printed rows and the compact multi-column pages 129–130.

The review's eleven code corrections are a dated overlay. Codes 2/25 need vertical position; narrow/wide hatching and underlines need separate labels. Original references were not edited. Calibration excluding three inverted selected rows uses 126 positions and yields Brier 0.1262 and ten-bin error 0.1183, with row-bootstrap intervals, without refitting or applying adjudications. These are Exploratory sensitivities of the original numbered-section frame.

## Repair attempts and preserved problems

The layout repair measures field coordinates from OCR boxes and print components, keeps pages upright from header content, and detects observed row bands without fixed counts. The first compact-column attempt discarded columns where no field/glyph gap was visible; retaining those columns with a flagged page-level gap estimate produced eight columns/288 rows on page 129 and six/201 on 130. An OCR batch exceeding Tesseract's image-height limit failed; batches of 96 rows fixed it. Development page 30 has 17/20 matching counts, 19/20 numbers, 6/20 top-one and 12/20 top-five whole rows. These are development observations.

The v1 candidate was frozen and sampled, then its unlabelled frame exposed glyph-like OCR strings as extra columns on ordinary pages. No reader received it. Its full artifacts remain under `repair/2026-10-07-v1/`, marked Superseded. The v2 replacement restricts ordinary margin clusters to a 35-point neighbourhood while retaining native compact-column discovery. Its code and evaluator were frozen at {freeze['created_utc']}; 80 predictions were frozen at {pf['created_utc']}. The seeded frame includes 28 numbered, 26 end-sorted and 26 beginning-sorted rows, excluding development pages and previous targets. It also retains 21 source-count pages. No fresh reference or new accuracy outcome exists.

A shell-quoting attempt to prepare v2 failed before creating files; a small Python construction helper replaced it. Shared Windows volume/process queries were denied. No dependency was installed in this follow-up, and no other package or repository history was changed. The revised L importer was exercised on 63 existing occurrences, including three provisional letter-suffixed strings: all schema checks passed and all remained quarantined without concordances.

## Disk stop and exact unfinished work

The first check found 896,548,864 bytes free, below the user's 1 GB cutoff. Free space subsequently recovered to about 2.65 GB and development resumed. During v2 sampling it fell to 917,327,872 and then 256,331,776 bytes. The helper had already serialized its 60,522,244-byte frame by the failed pre-frame check, and finished before interruption could take effect; CIM process inspection was denied. Space recovered after the helper exited. The cause of the fluctuations is unverified. A future gate must run inside the active process after library/model loading and immediately before each large serialization; checking outside that process was insufficient.

Further repair/evaluation work stopped at that trigger. The completed freeze, sample, predictions, positional chart cards and source-count pages are preserved. The following work remains:

1. Two independent readers must read all 80 rows and count/match all 21 source pages without predictions or OCR numbers.
2. A third source-only reader must adjudicate disagreements, preserving both initial readings and final source counts.
3. Run the frozen evaluator for row segmentation/counts, exact sequences, candidates, numbers, classification, row recall and calibration with intervals, beside the first endpoint and its different frame.
4. If every criterion passes, implement a fresh full transcription with an in-process disk gate and the frozen confidence release rule. If any stage fails, preserve quarantine and report the limiting stage.
5. A reviewed identity concordance and per-occurrence surface alignment are still required for actual Package L imports; the local 1980 lookup supplies no verified carrier join.

The coordinator must also apply the listed tracking exceptions before claiming clean-checkout recovery. Finish small documentation and integrity checks without starting another large write or deleting frozen evidence.
'''
    interface_text='''# Source-qualified occurrence import, corrected 7 October 2026

The existing staging preserves the Finnish 1979 edition, exact recognized text-number string, occurrence coordinates and per-occurrence `segment_id`, inventory/version, candidate tokens, auxiliaries, visual order, boundary status, digitization version and CC BY attribution. Every first-run occurrence remains quarantined. The orientation overlay must accompany any use of those original rows.

Package L's current contract is [HELSINKI-INTERFACE.md](../2026-10-07-object-ledger/HELSINKI-INTERFACE.md) and [the review-response amendment](../2026-10-07-object-ledger/AMENDMENT-2026-10-07-review-response.md). The requested `IMPORT_INTERFACE.md` does not exist. `import_helsinki1979_v2.py` now accepts letter-suffixed strings and requires occurrence segments. Its text-level crosswalk adapter expands a relation only with reviewed occurrence-surface alignment. Our [read-only check](follow-up/2026-10-07/ledger-interface-v2.json) passed the schema on 63 real provisional rows, including three recognized suffix strings, and quarantined all 63 without a concordance. Those suffix readings are unverified, not authenticated numbers. No Package L file was changed.

`prepare_import.py` remains the preserved first-run adapter. A supplied crosswalk needs source edition/number, target scheme/value, concordance source/page, rights and review status. For the revised L adapter, also supply opened-primary-source access, `same_physical_object` relation, reviewed identity and occurrence-specific surface alignment; preserve `segment_id` or explicit `occurrence_surfaces` mappings. Neither numeric equality nor duplicate text proves carrier identity. The available L importer also supports source-qualified reviewed surfaces on catalogue-only carriers. No such assertion was made here.

The 1980 Finnish-to-Mahadevan table is a catalogue lead. Its four inspected pairs and source crop stay local because the edition's reuse licence is unverified. The CISI 1 p. 365 Finnish Concordance column is a lead named by Package L, not opened or verified in this follow-up. Ancient lost-sign extent and physical side/line boundaries remain unresolved.

The repaired freeze's confidence rule concerns transcription eligibility. Object import still requires reviewed identity and surface evidence. No repaired output has passed the pending blind evaluation, so no release is authorized by a result yet.
'''
    for name,text in [('README.md',readme),('REPORT.md',report),('RETROSPECTIVE.md',retrospective),('IMPORT_INTERFACE.md',interface_text)]:
        (HERE/name).write_text(text,encoding='utf-8')
    entry=dict(id='M-2026-10-07-helsinki1979-digitization',theme='licensed corpus font digitization',status='Failed',
      question='Can a source-layout repair supply a reliable complete Helsinki 1979 numerical transcription?',
      outcome='Original 60 numbered-section targets (PDF31–79; detected frame 3460/11369; no sorted target): 33 counts, 23 numbers, 24 top-five whole rows; all criteria fail. Objective crop audits 14/60 and 21/60 with one-point tolerance. All 1223 inverted occurrences flagged; 9584 rows in active triage. Repaired method and 80 all-section predictions frozen; reference, row recall and evaluation unfinished after disk cutoff.',
      challenge='Field drift, incorrect orientation, extra/missing field columns, omitted underline/edge ink, position-dependent chart codes, locator OCR exposure and unstable free disk during active helpers.',
      remedy='Preserved all endpoints; portable prediction copy and tracking list; dated adjudication/orientation overlays; objective subset triage; upright-only calibration; positional chart cards; print/OCR layout repair and new pre-reference freeze; revised L schema/quarantine check.',
      evidence=[f'experiments/2026-10-07-helsinki1979-digitization/{p}' for p in ['REPORT.md',ANALYSIS+'/preservation-check.json',ANALYSIS+'/calibration-upright-only.json',REPAIR+'/freeze-manifest.json',REPAIR+'/prediction-freeze.json',FOLLOW+'/storage-stop-v2.json']],
      retry_when='Apply portable-input tracking exceptions; complete two source-only readings and source-count matching plus adjudication; run frozen metrics. Check at least 1 GB free inside active process before writes over 50 MB. Preserve all candidates and require reviewed carrier/surface concordance before L import.')
    (HERE/'registry-entry.json').write_text(json.dumps(entry,indent=2),encoding='utf-8')


if __name__=='__main__':main()
