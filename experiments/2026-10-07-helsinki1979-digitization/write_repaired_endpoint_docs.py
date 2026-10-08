"""Update living package documents from preserved first/second endpoint records."""
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
REPAIR='repair/2026-10-07-v2'
EVAL=REPAIR+'/evaluation-2026-10-07-adjudicated/metrics.json'
RECORD='follow-up/2026-10-07/endpoint-record-v1'


def read(name):return json.loads((HERE/name).read_text(encoding='utf-8'))


def prop(d):return f"{d['success']}/{d['total']} ({d['rate']*100:.1f}%; {d['ci95'][0]*100:.1f}–{min(1,d['ci95'][1])*100:.1f}%)"


def recall(d,interval):return f"{d['correct']}/{d['total']} ({100*d['rate']:.1f}%; {100*interval[0]:.1f}–{100*interval[1]:.1f}%)"


def main():
    if (HERE/'repair/2026-10-08-v3/freeze-manifest.json').exists():
        import write_crop_v3_docs
        return write_crop_v3_docs.main()
    old=read('evaluation/2026-10-07-frozen-v1/metrics.json');new=read(EVAL);d=read(RECORD+'/diagnosis.json');cost=read(RECORD+'/review-workload.json')
    o=old['summary'];n=new['summary'];b=old['row_bootstrap_95'];c=new['row_bootstrap_95']
    before=lambda name:(HERE/RECORD/(name+'.before-record.txt')).read_text(encoding='utf-8')
    frames='''The first endpoint samples **60 numbered-section rows on PDF pages 31–79**, drawn from 3,460 of 11,369 first-run detections; it has no sorted-section target. The second samples **80 occurrences across numbered, end-sorted and beginning-sorted sections (28/26/26)**, excluding development pages and the old targets, with eligible denominators 3,596/3,228/3,496. Section quotas do not weight these headline rates to the full edition. The references also differ: one primary reading per first-endpoint row, then two independent readings and source-only adjudication for every repaired row. The comparison describes two frames; it does not estimate a paired treatment effect.'''
    specs=[('Crop acceptance','row_crop_correctness'),('Drawing-unit count','drawn_unit_count_agreement'),
        ('Inscription number, including suffix','inscription_number_accuracy'),('Five-position classification','classification_exact_accuracy')]
    table='| Outcome, 95% interval | First: 60 numbered rows, PDF31–79 | Repaired: 80 rows, three sections |\n|---|---|---|\n'
    for label,key in specs:table+=f'| {label} | {prop(o[key])} | {prop(n[key])} |\n'
    for label,key in [('Compatible whole row, top one','strict_top1'),('Compatible whole row, top five','strict_top5')]:
        table+=f"| {label} | {prop(o[key]['whole_rows_all_sample'])} | {prop(n[key]['whole_rows_all_sample'])} |\n"
    table+=f"| Exact sequence, singleton-reference subset | {prop(o['uniquely_resolved_exact_sequence'])} | {prop(n['uniquely_resolved_exact_sequence'])} |\n"
    table2='| Unit/calibration outcome, 95% interval | First: same 60-row frame | Repaired: same 80-row frame |\n|---|---|---|\n'
    for label,key,field in [('Aligned top-one recall','strict_top1','aligned_recall'),('Aligned top-five recall','strict_top5','aligned_recall'),
        ('Equal-count top-one positional accuracy','strict_top1','same_position_equal_count'),('Equal-count top-five positional accuracy','strict_top5','same_position_equal_count')]:
        suffix='_aligned_recall' if field=='aligned_recall' else '_same_position_equal_count'
        table2+=f"| {label} | {recall(o[key][field],b[key+suffix])} | {recall(n[key][field],c[key+suffix])} |\n"
    for label,key in [('Brier score','brier'),('Ten-bin calibration error','ece10')]:
        interval='calibration_'+key
        table2+=f"| {label} | {o['calibration'][key]:.4f} ({b[interval][0]:.3f}–{b[interval][1]:.3f}) | {n['calibration'][key]:.4f} ({c[interval][0]:.3f}–{c[interval][1]:.3f}) |\n"
    endpoint=f'''## Both frozen endpoints

{frames}

{table}
Row proportions use the stored Wilson intervals. The original crop acceptance includes annotator C's permissive labels; the objective audit below is separate. The exact-sequence row restricts each frame to singleton references. The repaired sample contains 352 reference drawings and 377 proposals, with 15 ambiguous reference units and none unresolved. Candidate compatibility accepts intersection with a reference set and does not authenticate a unique code. Exact evidence: [first metrics](evaluation/2026-10-07-frozen-v1/metrics.json), `summary`; [repaired metrics]({EVAL}), `summary` and `frame`.

{table2}
Aligned recall omits a penalty for extra proposals; whole-row scores include their count/order effects. Calibration and positional scores use only equal-count rows: 140 units originally and 252 after repair. The intervals above are the stored row bootstraps (2,000 draws; repaired resampling within sections, seed 2026100781). Five templates can propose more than five codes through ambiguous chart labels. All fields and interval arrays are in the two metric files, `summary` and `row_bootstrap_95`.

The repaired source-count frame has 18 random pages and three prespecified stress pages, separate from the 80-row recognition frame:

| Source-count frame | Recall, pooled Wilson 95% interval | Precision, pooled Wilson 95% interval |
|---|---|---|
| 18 random pages, six per section | {prop(new['source_row_recall']['random']['recall'])} | {prop(new['source_row_recall']['random']['precision'])} |
| Stress pages 62,129,130 | {prop(new['source_row_recall']['stress']['recall'])} | {prop(new['source_row_recall']['stress']['precision'])} |

The random-page bootstrap interval for recall is **90.5–100.0%**, wider than the pooled row interval because misses cluster by page. Page 66 loses five rows in its second column (31/36 detected); page 112 finds 18/36 and 15/36 in its two columns, losing 39 rows. Those two pages account for all 44 misses. The remaining 16 random pages have complete matched coverage. Matching uses source column bounds and a 9-point anchor tolerance. The source counts include 1,847 numbered occurrences in 52 columns and exclude ten unnumbered continuation lines; counting every physical line would give 1,857. Pages 129–130 were development pages excluded from the recognition sample, so their 288/288 and 201/201 recall results do not evaluate their glyph recognition. [Metrics]({EVAL}), `source_row_recall`; [count reference]({REPAIR}/blind/adjudicated-counts.json), `total_rows`, `total_columns`, `total_physical_lines`.

The frozen criteria use point rates: crop ≥90%, number ≥90%, count ≥95%, top-five whole rows ≥80%, and random-page recall ≥95%. Only recall passes. Four criteria fail, so the pipeline status is **Failed** and every occurrence remains quarantined. [Criteria]({EVAL}), `negative_result_criteria`.

'''
    report_before=before('REPORT.md')
    historical=report_before.split('Exact fields are ',1)[1].split('## Repair development, freezing and unfinished evaluation',1)[0]
    historical='## First-endpoint reference and extraction details\n\nExact fields are '+historical
    historical=historical.replace('An independent true-row denominator remains unfinished.','The first endpoint still has no edition-wide source denominator; the repaired 21-page count reference above now supplies a separate sampled denominator.')
    dev=report_before.split('## Repair development, freezing and unfinished evaluation\n\n',1)[1].split('| Evaluation component',1)[0]
    dev=dev.replace('These are detector outputs, pending independent source counts.','The subsequent source-count reference confirms the 72, 288 and 201 printed occurrences on stress pages 62,129,130; pages 30,100,145 remain development detector observations.')
    dev=dev.replace('precedes every new reference: none exists.','precedes the completed independent readings and adjudication supplied by the coordinator.')
    stage_table='| Section in the 80-row frame | Crop failures | Count failures | Top-five row failures | Number failures | Classification-field failures |\n|---|---|---|---|---|---|\n'
    for section,label in [('number_order','Numbered (28)'),('end_sorted','End-sorted (26)'),('beginning_sorted','Beginning-sorted (26)')]:
        v=d['by_section'][section]
        stage_table+=f"| {label} | {len(v['crop_failures'])} | {len(v['count_failures'])} | {len(v['top5_failures'])} | {len(v['number_failures'])} | {len(v['classification_field_failures'])} |\n"
    diagnosis=f'''## Limiting stages: Exploratory diagnosis of the 80-row endpoint

Row geometry and editorial-unit handling limit this endpoint. Of **40 incompatible top-five rows**, 34 first fail the crop check, three have unequal unit counts despite an accepted crop (indices 3,50,52), and three have candidate misses despite accepted crops and matching counts (25,58,72). For **60 incompatible top-one rows**, the corresponding partition is 35 crop, three count and 22 count-consistent candidate failures. These partitions use the earliest failed observable check; they do not attribute a counterfactual gain from repairing that check. [Diagnosis]({RECORD}/diagnosis.json), `incompatible_whole_row_partitions` and per-row `metric_fields`.

Across all 80 rows, 36 crops are rejected, including two with compatible top-five sequences. Eighteen of the 21 count failures occur inside rejected crops; three are additional segmentation failures in accepted crops. The adjudicated tags name omitted own underlines in 18 rows, neighbour ink in 13, number-field ink in 13 and cut target ink in four. Tags overlap. The loss rectangle is split into two units in row 3; a dash fragment becomes an extra tick in row 50; the high tick is absorbed into the following diamond window in row 52. [Source tags]({RECORD}/diagnosis.json), `crop_issues`, and [unit-window inspection]({RECORD}/unit-window-audit.json), `count_failure_rows`.

The 41 accepted-crop, equal-count rows contain 166 units. Strict positional matches are 134/166 at top one and 161/166 at top five; shape-only matches are 152/166 and 165/166. Equal counts are a segmentation proxy, so these are conditional observations. Inspection of all five residual strict top-five unit misses finds four underlined units in rows 25 and 58: their 5–9-point unit windows truncate part of the approximately 14-point underline, and the corresponding plain graphic is proposed. The remaining miss is row 72 unit 1, a complete figure whose code 244 lies outside the five proposals. Thus the inspected top-five failures have repair targets of **34 row crops, five rows with unit segmentation/underline association defects, and one row with a graphic proposal miss**. This inspection was made after predictions were visible and does not validate every other unit boundary. [Audit]({RECORD}/unit-window-audit.json), `units`, `refined_top5_incompatible_rows`; [source conventions]({REPAIR}/blind/reader-b/rows-part1.json), `notes` on dashed sign slots.

Number reading fails in 18/80 rows and classification-field reading in 25/80; 30/80 have at least one bad field. These overlap crop and unit errors. Among the 41 accepted-crop, matching-count rows, three still have wrong numbers (12,40,68) and seven wrong classifications (16,18,31,32,34,37,66). Those ten rows are disjoint. Glyph classification and the five-position classification field are separate outcomes. [Diagnosis]({RECORD}/diagnosis.json), `subsets`.

{stage_table}
Crop and whole-row failure rates are similar across the three sections. Field reading is worse in the end-sorted sample, where numbers/classifications sit to the left. The numbered and beginning-sorted fields sit to the right. Odd pages have 21/43 rejected crops and even pages 15/37; these small section/parity groups do not isolate a parity effect. Pages 41,105,165 and173 each have two sampled crop failures, but only two targets per page. The multi-column pages 129–130 have no evaluated recognition row. [Diagnosis]({RECORD}/diagnosis.json), `by_section`, `by_margin_side`, `by_page_parity`, `by_page` and `count_page_failures`.

## Quarantine, release requirements and review cost

**All 11,369 original occurrences remain quarantined; zero are released.** The original 9,584-row triage queue prioritizes work and does not certify its other 1,785 rows. The repaired sample failed four global criteria, so high confidence cannot release an individual row under the frozen rule. An automatic route would need a separate layout/editorial-unit repair, a new method freeze and fresh blind evaluation passing all five criteria. Each eligible row would still require resolved orientation and complete geometry, singleton codes, independent numeric-witness agreement, no unresolved editorial/boundary ambiguity, minimum unit confidence 0.90 and confidence product 0.90. Preserve variants and losses; the count reference excludes unnumbered continuations, so a complete transcription must explicitly attach those source lines to their numbered occurrence. L import additionally requires reviewed carrier identity and occurrence-surface alignment. [Frozen rule]({REPAIR}/freeze-manifest.json), `release_rule`; [import contract](IMPORT_INTERFACE.md).

A review route uses the recognizer to propose codes and requires a complete human source check plus a second independent AI reading for each occurrence, followed by adjudication and a separately specified, validated acceptance rule. That means at least **11,369 human readings and 11,369 AI readings**, before recovering missing rows or checking complete line/side coverage. Applying the repaired 80-row rates to that provisional occurrence count projects about **5,116 crop corrections**, **2,984 count corrections**, **8,527 top-one sequence corrections**, **5,685 rows with a top-five proposal miss**, **2,558 number corrections** and **3,553 classification corrections**. Corrections overlap and cannot be added. Crop and top-five planning ranges from the sample Wilson intervals are 3,931–6,353 and 4,468–6,901 respectively. The frames/section weights differ and these projections estimate work under stated assumptions, not an edition error census. [Workload]({RECORD}/review-workload.json), `projections` and `extrapolation_note`.

The two AI readings disagree on strict sets in 15/80 rows (19/352 units), projecting about **2,132 adjudication rows** (sample-based range 1,331–3,258). Human/AI disagreement has not been measured. The four 40-row task records sum to 13,810 elapsed seconds for 160 readings: 86.3 seconds per reading and about **272.6 summed task hours** for one AI pass through 11,369 rows. Six reading tasks including page counts sum to 16,037 seconds; their recorded wall span is 5,679 seconds because tasks overlap. These include tool latency and source inspection, and some start times are approximate. They are not human throughput measurements. At assumed human check times of one, two or five minutes per row, the human pass needs **189.5, 379.0 or 947.4 hours**, plus source recovery, adjudication, continuation checking and ledger joins. Adjudicator elapsed time, token usage and billed dollars are absent from the supplied records; monetary cost remains unknown. [Workload]({RECORD}/review-workload.json), `observed_reader_task_timing`, `human_scenarios` and cost-null fields.

'''
    portable=report_before.split('## Portable evidence and Package L',1)[1]
    report=f'''# Helsinki 1979 digitization: two failed frozen endpoints

The repaired pipeline fails four of five frozen reliability criteria. In its **80-row frame across numbered, end-sorted and beginning-sorted sections (28/26/26)**, it has 44 accepted crops, 59 matching counts, 62 exact numbers, 55 exact classifications and 40 top-five compatible whole rows. Random-page row recall passes at 1,242/1,286; crop and unit-window handling remain the main limits. All occurrences remain quarantined. [Frozen repaired metrics]({EVAL}), `summary`, `source_row_recall`, `negative_result_criteria`.

The first endpoint remains unchanged: **60 numbered-section rows on PDF pages 31–79**, 33 matching counts, 23 exact numbers and 24 top-five whole rows. Its references, review corrections and separate sensitivities remain preserved below. The coordinator subsequently completed the repaired source readings, adjudication and unchanged evaluator after this package's recorded disk stop. Diagnostic partitions and workload projections are Exploratory.

{endpoint}{historical}## Repair development and freeze chronology

{dev}{diagnosis}## Portable evidence and Package L{portable}'''
    readme_before=before('README.md')
    portable_readme=readme_before.split('## Portable first evaluation',1)[1].split('## Resume the repaired evaluation',1)[0]
    attribution=readme_before.split('## Attribution and reviewer checks',1)[1].split('- Check ignored-asset',1)[0]
    readme=f'''# Package M: Helsinki 1979 digitization

Both frozen endpoints fail their release criteria. **First frame: 60 numbered-section rows, PDF31–79**, sampled from 3,460/11,369 detected occurrences; no sorted-section row was evaluated. **Repaired frame: 80 rows across numbered, end-sorted and beginning-sorted sections (28/26/26)**, excluding development pages and the old targets. The reference and sampling differences make the comparison descriptive.

{table}
Intervals are the stored 95% Wilson intervals. The [report](REPORT.md) gives unit recall and calibration, source-count intervals and the stage diagnosis. Original frozen code, predictions, references and metrics are unchanged.

The repaired count evaluation finds **1,242/1,286 random-page rows (96.6%; pooled 95% interval 95.4–97.4%; page-bootstrap 90.5–100.0%)**, with **1,242/1,242 precision (100%; pooled interval 99.7–100.0%)**, across 18 pages. Stress pages 62,129,130 yield **561/561 recall and precision (100%; 99.3–100.0%)**. Only the row-recall criterion passes; four fail. [Metrics]({EVAL}), `source_row_recall`, `negative_result_criteria`.

Of 40 top-five whole-row failures in the repaired 80-row frame, 34 first fail crops, three unit counts, two underline-window association and one graphic proposal classification after source/window inspection. Number reading also fails in 18/80 and classification reading in 25/80. All **11,369** provisional occurrences stay quarantined, including the 1,785 outside the 9,584-row triage queue. A release needs a newly validated automatic rule or a separately validated human-plus-AI review route and adjudication; object imports additionally need identity/surface concordances.

## Main files and review workload

- [Protocol and dated recording amendment](PROTOCOL.md), [findings](REPORT.md), [process and cost](RETROSPECTIVE.md), [registry proposal](registry-entry.json), [source register](sources.json), [import contract](IMPORT_INTERFACE.md).
- [Frozen repaired metrics]({EVAL}), [freeze]({REPAIR}/freeze-manifest.json), [prediction freeze]({REPAIR}/prediction-freeze.json).
- [Reader A]({REPAIR}/blind/reader-a/rows-part1.json), [reader B]({REPAIR}/blind/reader-b/rows-part1.json), their part-2/count files in the same folders, [adjudicated rows]({REPAIR}/blind/adjudicated-reference.json), [counts]({REPAIR}/blind/adjudicated-counts.json), [decision notes]({REPAIR}/blind/adjudication-notes.json).
- [Machine-readable diagnosis]({RECORD}/diagnosis.json), [unit-window audit]({RECORD}/unit-window-audit.json), [workload]({RECORD}/review-workload.json), [preservation hashes]({RECORD}/preservation-check.json).
- [Original coverage](runs/2026-10-07-full-v1/coverage.json), [triage](follow-up/2026-10-07/analysis-v1/triage-queue.jsonl), [orientation overlay](follow-up/2026-10-07/analysis-v1/orientation-overlay.json), [first-reference adjudication overlay](follow-up/2026-10-07/analysis-v1/adjudication-overlay.json).

Reviewing 11,369 provisional occurrences requires at least that many human checks and independent AI checks. At assumed human times of one/two/five minutes per row, the human pass takes 189.5/379.0/947.4 hours, excluding adjudication and missing-row recovery. The recorded AI task timing projects 272.6 summed task hours for one pass. Reader disagreements project about 2,132 adjudication rows from 15/80 measured rows; a human/AI rate is unmeasured. Monetary cost is unknown without usage/billing records. These are Exploratory planning estimates with distinct source/task frames, detailed in `review-workload.json`.

## Portable first evaluation{portable_readme}## Reproduce the repaired record

Run from the repository root, with fresh output paths:

```powershell
& 'C:\\Users\\sandh\\.venvs\\indus-ml\\Scripts\\python.exe' experiments/2026-10-07-helsinki1979-digitization/record_repaired_endpoint.py --out experiments/2026-10-07-helsinki1979-digitization/review/repaired-record-repeat
& 'C:\\Users\\sandh\\.venvs\\indus-ml\\Scripts\\python.exe' experiments/2026-10-07-helsinki1979-digitization/audit_repaired_unit_windows.py --out experiments/2026-10-07-helsinki1979-digitization/review/unit-window-repeat.json
& 'C:\\Users\\sandh\\.venvs\\indus-ml\\Scripts\\python.exe' experiments/2026-10-07-helsinki1979-digitization/evaluate_repair.py --out experiments/2026-10-07-helsinki1979-digitization/review/repaired-evaluation-repeat
```

The recorder uses the standard library; the frozen evaluator needs NumPy and the retained reference, prediction and frame inputs. Unit-window observations are a post-outcome visual audit encoded in the audit script; rerunning it verifies inputs/calculations and does not replace source inspection. `write_docs.py` and `write_followup_docs.py` now delegate to `write_repaired_endpoint_docs.py`, which reads the preserved pre-record prose and current aggregates.

Do not rerun the construction/sampling helpers over either frozen endpoint. A future large-write gate must run inside the active process after library/model loading. Stop below 1,000,000,000 bytes free before writes over 50 MB. No full repaired extraction or release was run in this recording task. The prior disk-stop artifact remains historical evidence.

## Attribution and reviewer checks{attribution}- Rerun the frozen evaluator into a new directory and compare the complete metrics, ignoring no outcome fields.
- Verify both endpoint hashes, all six initial reader files and adjudication; inspect the disclosed scratchpad/directory-list deviations in reader notes.
- Reproduce the stage partitions; visually inspect exact rows 3,25,50,52,58,72 against the frozen unit windows.
- Check page 66/112 recall misses and the 52 source column counts, including continuation exclusions.
- Verify workload arithmetic and supply missing billing/adjudicator-time records before reporting money or total project effort.
- Confirm zero releases and preserve L's concordance requirements.
- Run `python tools/review_prose.py --path experiments/2026-10-07-helsinki1979-digitization --no-write`.
'''
    retro_before=before('RETROSPECTIVE.md')
    retro_before=retro_before.replace('No fresh reference or new accuracy outcome exists.','No fresh reference or accuracy outcome existed when this package stopped; the coordinator subsequently supplied them as recorded below.')
    retro_before=retro_before.replace('The following work remains:','At that stop the following work remained (items 1–3 have since been completed by the coordinator):')
    retrospective=retro_before+f'''
## Completed repaired evaluation, recorded 7 October 2026

The coordinator supplied six Sonnet reading files: each of readers A and B read rows 0–39, rows 40–79 and the 21 count pages. A third reader adjudicated without predictions, using page scans and the printed sign chart. The coordinator ran the unchanged frozen evaluator against the final references. All 320 row-level fields agree between readers (number, classification, unit count and crop status on all 80 rows). Strict unit sets agree in 333/352 positions; 19 disagreements span 15 rows. Both count readers agree on all 52 column counts, totaling 1,847 numbered occurrences, with ten unnumbered continuation lines recorded separately. [Initial readings]({REPAIR}/blind/reader-a/rows-part1.json) and [second readings]({REPAIR}/blind/reader-b/rows-part1.json), their part-2/count files; [reference]({REPAIR}/blind/adjudicated-reference.json); [counts]({REPAIR}/blind/adjudicated-counts.json).

The 222 adjudication notes contain 19 strict-code decisions, eight unit-kind decisions, 181 shape-only candidate-set decisions, one blank-gap distance decision and 13 count-coordinate/continuation-position decisions. Large shape-only sets reflect differing reader scope and were adjudicated separately from strict codes. The decisions preserve candidate sets for identical printed drawings. No original or repaired reference was edited during this recording. [Decision record]({REPAIR}/blind/adjudication-notes.json), `field`; [agreement calculation]({RECORD}/diagnosis.json), `readers`.

The repaired **80-row all-section frame (28/26/26)** yields 44/80 crops, 59/80 counts, 62/80 numbers, 55/80 classifications, 20/80 top-one and 40/80 top-five whole rows. Four global criteria fail. The separate 18-page count frame recalls 1,242/1,286 rows, with all 44 misses on pages 66 and112; stress pages recall 561/561. All occurrences remain quarantined. The [report](REPORT.md) presents intervals beside the unchanged **60 numbered-section rows on PDF31–79** and keeps the frames distinct.

Reader notes disclose shared-scratchpad failures. A's first-row task saw two helper-script lines in an error trace after `zoom.py` was overwritten; B's second-row task ran an overwritten helper once, producing an enlarged render in B1's temporary directory, then deleted it and isolated its scripts. B's count task read an overwritten `common.py` containing image-loading/run-merging functions but no counts or positions, then moved its scripts to a separate subdirectory. B's row tasks also listed primary-source, local-raw or scratchpad directory names without opening the prohibited contents. These departures reduce process isolation; the disclosed snippets/helpers contain no predictions or reference values, and the readers report no prediction exposure. A future protocol should assign unique helper directories before launching tasks. [A part 1]({REPAIR}/blind/reader-a/rows-part1.json), [B part 1]({REPAIR}/blind/reader-b/rows-part1.json), [B part 2]({REPAIR}/blind/reader-b/rows-part2.json), [B counts]({REPAIR}/blind/reader-b/counts.json), each `notes`. Temporary diagnostic overlays were deleted by the readers, so their inspection cannot be reconstructed from overlays alone; source images and final coordinates remain.

Recorded elapsed time is 13,810 seconds (230.2 minutes) for four row tasks and 2,227 seconds (37.1 minutes) for two count tasks, totaling 16,037 seconds (267.3 minutes). Their earliest start/latest finish span 5,679 seconds (94.7 minutes), with concurrent tasks and approximate start times. No adjudicator timing, token usage or billed dollars appears in the supplied files; those costs are unknown. A request for the billing witness was made during this task. The extrapolated review route needs at least 22,738 initial row readings, plus source recovery/adjudication. Human times are assumed scenarios; AI times are measured elapsed-task extrapolations. [Cost record]({RECORD}/review-workload.json), `observed_reader_task_timing`, `human_scenarios`, nullable billing/adjudicator fields.

The recording helper's first attempt failed before producing output because a dictionary constructor repeated the `pdf_page` key. Removing the duplicate fixed it. Reused the existing scorer outputs, frozen predictions, source images, chart conventions and original review; no model inference, downloads or new large renders were needed. A post-outcome inspection of the five accepted-crop/equal-count top-five unit misses separates four truncated underline windows from one graphic proposal miss. The six source rows inspected are preserved in [unit-window-audit.json]({RECORD}/unit-window-audit.json). Equal-count rows outside that inspection retain the stated segmentation-proxy limitation.

Remaining work is a validated release method, complete source/continuation coverage, human review and occurrence/carrier concordances. The completed failed endpoint does not authorize the proposed full repaired run. Frozen witnesses and both failed results remain available for a later separately frozen retry.
'''
    for name,text in [('README.md',readme),('REPORT.md',report),('RETROSPECTIVE.md',retrospective)]:
        (HERE/name).write_text(text,encoding='utf-8')
    interface=before('IMPORT_INTERFACE.md').replace('No repaired output has passed the pending blind evaluation, so no release is authorized by a result yet.','The completed repaired 80-row blind evaluation fails four of five global criteria. Every occurrence remains quarantined; no high-confidence row can bypass that frozen global rule. See [repaired metrics]('+EVAL+'), `negative_result_criteria`.')
    (HERE/'IMPORT_INTERFACE.md').write_text(interface,encoding='utf-8')
    entry=read(RECORD+'/registry-entry.json.before-record.txt')
    entry.update(status='Failed',
        outcome='First: 60 numbered-section rows on PDF31–79, 33/60 counts,23/60 numbers,24/60 top-five whole rows. Repaired:80 all-section rows(28/26/26),44/80 crops,59/80 counts,62/80 numbers,55/80 classifications,20/80 top-one and40/80 top-five whole rows;304/352 unit top-five recall. Random-page row recall1242/1286 and stress561/561;four of five criteria fail. All11369 occurrences remain quarantined.',
        challenge='Repaired layout still clips target underlines, includes neighbour/number ink, splits/merges units and truncates underline windows. Field reading fails independently. Missing rows cluster on two pages. Shared helper-script collisions reduce reader process isolation; billing/adjudicator-time witnesses absent.',
        remedy='Recorded both unchanged frozen endpoints with frames/intervals; two complete Sonnet readings and third-reader source adjudication; per-row stage partitions, source/window inspection and explicit review-workload scenarios. Maintained quarantine and carrier/surface requirements.',
        retry_when='A separately frozen repair and fresh blind evaluation pass all five reliability criteria and the row-level confidence rule, or a separately validated human-plus-independent-AI/adjudication acceptance route provides complete source/continuation coverage. Require at least1GB free before large writes and reviewed occurrence/carrier concordances for L.')
    entry['evidence']+=['experiments/2026-10-07-helsinki1979-digitization/'+p for p in [EVAL,REPAIR+'/blind/adjudicated-reference.json',REPAIR+'/blind/adjudicated-counts.json',REPAIR+'/blind/adjudication-notes.json',RECORD+'/diagnosis.json',RECORD+'/unit-window-audit.json',RECORD+'/review-workload.json',RECORD+'/preservation-check.json']]
    (HERE/'registry-entry.json').write_text(json.dumps(entry,indent=2,ensure_ascii=False),encoding='utf-8')
    sources=read(RECORD+'/sources.json.before-record.txt')
    sources['sources'].append(dict(id='repaired-v2-blind-evaluation-record',title='Helsinki 1979 repaired v2 blind readings, source adjudication and frozen evaluation',
        authors=['Claude Sonnet readers A and B','Claude Sonnet adjudicator C','research coordinator (evaluation execution)'],year=2026,
        venue='Private research repository evaluation record',url=None,opened=True,seen_only_search_snippet=False,quoted_words=0,
        status='Frozen evaluation',source_locations=[REPAIR+'/blind/reader-a/rows-part1.json: notes and rows',REPAIR+'/blind/reader-a/rows-part2.json: notes and rows',REPAIR+'/blind/reader-a/counts.json: notes and pages',REPAIR+'/blind/reader-b/rows-part1.json: notes and rows',REPAIR+'/blind/reader-b/rows-part2.json: notes and rows',REPAIR+'/blind/reader-b/counts.json: notes and pages',REPAIR+'/blind/adjudication-notes.json',EVAL+': summary, rows, source_row_recall, negative_result_criteria'],
        scope='Supplied completed source-only reference process; diagnostic/workload analyses are post-outcome Exploratory'))
    (HERE/'sources.json').write_text(json.dumps(sources,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps(dict(updated=['README.md','REPORT.md','RETROSPECTIVE.md','IMPORT_INTERFACE.md','registry-entry.json','sources.json'])))


if __name__=='__main__':main()
