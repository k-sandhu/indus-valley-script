"""Record v3 outputs in living documents; preserve the pre-v3 prose separately."""
import json
from pathlib import Path
import shutil

HERE=Path(__file__).resolve().parent
RUN=HERE/'repair/2026-10-08-v3'
RECORD=HERE/'repair/2026-10-08-record-v1'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def write(p,data):Path(p).write_text(json.dumps(data,indent=2,ensure_ascii=False),encoding='utf-8')
def prop(p):return f"{p['success']}/{p['total']} ({100*p['rate']:.1f}%; {100*p['ci95'][0]:.1f}–{100*min(1,p['ci95'][1]):.1f}%)"

def main():
    full=read(RUN/'full-summary.json');dev=read(HERE/'repair/2026-10-08-development-record-v1/diagnosis.json')
    sel=read(RUN/'blind/selection.json');freeze=read(RUN/'freeze-manifest.json');pf=read(RUN/'prediction-freeze.json')
    old=read(HERE/'evaluation/2026-10-07-frozen-v1/metrics.json')['summary'];v2=read(HERE/'repair/2026-10-07-v2/evaluation-2026-10-07-adjudicated/metrics.json')['summary'];v3=dev['development_summary']
    RECORD.mkdir(parents=True,exist_ok=True)
    names=['README.md','REPORT.md','RETROSPECTIVE.md','IMPORT_INTERFACE.md','registry-entry.json','sources.json','TRACK-EXCEPTIONS.txt']
    for name in names:
        backup=RECORD/(name+'.before-v3.txt')
        if not backup.exists():shutil.copyfile(HERE/name,backup)
    base=lambda n:(RECORD/(n+'.before-v3.txt')).read_text(encoding='utf-8')
    table='| Outcome, descriptive 95% Wilson interval | First frozen: 60 numbered rows, PDF31–79 | V2 frozen: 80 rows, 28/26/26 sections | V3 development: same 80 v2 targets |\n|---|---|---|---|\n'
    for label,key in [('Matching unit count','drawn_unit_count_agreement'),('Literal inscription number','inscription_number_accuracy'),('Five-position classification','classification_exact_accuracy')]:
        table+=f'| {label} | {prop(old[key])} | {prop(v2[key])} | {prop(v3[key])} |\n'
    for label,key in [('Compatible whole row, top one','strict_top1'),('Compatible whole row, top five','strict_top5')]:
        table+=f'| {label} | {prop(old[key]["whole_rows_all_sample"])} | {prop(v2[key]["whole_rows_all_sample"])} | {prop(v3[key]["whole_rows_all_sample"])} |\n'
    table+=f'| Crop acceptance | {prop(old["row_crop_correctness"])} | {prop(v2["row_crop_correctness"])} | No new independent crop labels |\n'
    fulltext=f"{full['rows']:,} physical-line proposals, {full['numbered_occurrences']:,} numbered occurrences, {full['continuation_lines']:,} continuation lines and {full['units']:,} proposed unit windows ({full['nonfinite_units_unresolved']} unresolved) across {full['pages']} pages (PDF22–180)"
    intro=f'''# Package M: Helsinki 1979 cropping v3

V3 is frozen and supplies **{fulltext}**. Every proposal remains quarantined; **zero are released**. The fresh blind packet contains 80 numbered occurrences, 18 new random count pages and three stress pages. No fresh reference or v3 evaluation outcome exists. The coordinator will obtain two independent readings, adjudication and the frozen evaluation; a separate option-B package will check every source row. [Full inventory](repair/2026-10-08-v3/full-summary.json), `rows`, `numbered_occurrences`, `continuation_lines`, `units`, `pages`; [packet](repair/2026-10-08-v3/blind/selection.json).

The 80 v2 rows are development data for v3. Their 28/26/26 section quotas and 352 reference units are reused unchanged; they selected the crop method. The intervals below describe these rows and do not estimate fresh v3 accuracy. The first frame contains 60 numbered-section rows from PDF31–79, sampled from 3,460/11,369 detections, with no sorted-section row. The v2 frozen frame contains 80 rows across numbered, end-sorted and beginning-sorted sections.

{table}
The new numbered-row detections match **1,847/1,847** source occurrences on the 21 reused count pages (descriptive Wilson interval 99.8–100.0%; precision also 1,847/1,847). All five earlier segmentation/underline failure rows (3,25,50,52,58) now have matching counts and compatible top-five sequences in development. [Development diagnosis](repair/2026-10-08-development-record-v1/diagnosis.json), `development_summary`, `development_numbered_recall`, `prior_five_segmentation_underline_failures`. The two earlier frozen endpoints remain unchanged and failed their release criteria.

## Freeze, fresh packet and complete verification

The [method freeze](repair/2026-10-08-v3/freeze-manifest.json) records code, parameters, chart, evaluator, unchanged model/digits/calibration and source hashes at {freeze['created_utc']}. The [prediction freeze](repair/2026-10-08-v3/prediction-freeze.json) follows at {pf['created_utc']}, before any fresh reference. The [source-only conventions](repair/2026-10-08-v3/blind/CONVENTIONS.md) specify continuation checks, complete underline slots, the 597/598 spacing rule, separate reader scratch directories and both numbered/physical-line counts.

The fresh 80-row quotas are 28 numbered,26 end-sorted,26 beginning-sorted. The eligible pools are **572,2,004,2,004 numbered occurrences on 8,28,28 pages**. Page exclusions remove every page with any of the first 60 or v2 80 targets, plus the original ten development pages. All sampled targets happen to have no detected continuation, so the recognition test has limited direct continuation evidence. The 18 random count pages exclude the old count pages; stress pages 62,129,130 remain development checks. [Selection](repair/2026-10-08-v3/blind/selection.json), `denominators`, `eligible_pages`, `excluded_pages`, `random_count_pages`, `stress_pages`; [protocol](PROTOCOL.md).

The large JSONL is local, named with its byte count and SHA256 in [HOST-FILES.txt](HOST-FILES.txt) for coordinator backup. Its [option-B contract](OPTION-B-INTERFACE.md) and [schema](option-b-schema.json) retain one record per physical line, source boxes, provisional continuation links, literal field proposals, candidate sets, inherited-calibration confidence and quarantine. Existing object-ledger identity/surface requirements remain in force. [Import contract](IMPORT_INTERFACE.md).

## Reproduce from the repository root

Use the recorded Python environment and a new output directory for each replay. Construction refuses to overwrite a freeze, packet or full output. The acquired source PDF and original chart crops are needed for inference.

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
& 'C:\\Users\\sandh\\.venvs\\indus-ml\\Scripts\\python.exe' experiments/2026-10-07-helsinki1979-digitization/develop_crop_v3.py --out experiments/2026-10-07-helsinki1979-digitization/review/development-v3-repeat
& 'C:\\Users\\sandh\\.venvs\\indus-ml\\Scripts\\python.exe' experiments/2026-10-07-helsinki1979-digitization/record_crop_v3.py --development experiments/2026-10-07-helsinki1979-digitization/repair/2026-10-08-development-v3h/development.json --out experiments/2026-10-07-helsinki1979-digitization/review/development-record-repeat
& 'C:\\Users\\sandh\\.venvs\\indus-ml\\Scripts\\python.exe' experiments/2026-10-07-helsinki1979-digitization/prepare_crop_v3.py freeze --run experiments/2026-10-07-helsinki1979-digitization/review/v3-reconstruction
& 'C:\\Users\\sandh\\.venvs\\indus-ml\\Scripts\\python.exe' experiments/2026-10-07-helsinki1979-digitization/prepare_crop_v3.py packet --run experiments/2026-10-07-helsinki1979-digitization/review/v3-reconstruction
& 'C:\\Users\\sandh\\.venvs\\indus-ml\\Scripts\\python.exe' experiments/2026-10-07-helsinki1979-digitization/complete_crop_v3_full.py --run experiments/2026-10-07-helsinki1979-digitization/review/v3-reconstruction --raw-output data/raw/2026-10-07-helsinki1979-digitization/reviewer-v3-full --reuse data/raw/2026-10-07-helsinki1979-digitization/reviewer-no-reuse
```

The reconstruction's new freeze timestamp/hash changes its embedded provenance fields; compare geometry, selected source targets and proposals separately. The separate transport helper marks non-finite windows unresolved without changing frozen inference. A stopped full run can resume only from intact hash-checked page files with `--resume`. After coordinator references are present, run the frozen scorer into a new owned directory:

```powershell
& 'C:\\Users\\sandh\\.venvs\\indus-ml\\Scripts\\python.exe' experiments/2026-10-07-helsinki1979-digitization/evaluate_crop_v3.py --out experiments/2026-10-07-helsinki1979-digitization/review/v3-evaluation-repeat
```

The scorer currently stops because references are absent. It retains all five original global criteria, Wilson row intervals, stratified row bootstraps, equal-count calibration and numbered recall, and adds physical-line recall. It creates no reference. For both older endpoint replay commands and their reader-process disclosures, see the [preserved earlier README](repair/2026-10-08-record-v1/README.md.before-v3.txt).

## Limits, rights and checks

Known development boxes 27,53,76 still include field ink or cut a final drawing. Short-component-only continuations can be missed. Number reading, graphic variants and inherited calibration remain limits beside the crop repair; [REPORT.md](REPORT.md) links their measured results. The full detection count is not an independently verified complete corpus denominator. Complete source-page inspection belongs to the option-B package.

Source-derived crops and proposals are modifications of Kimmo Koskenniemi and Asko Parpola, *Corpus of Texts in the Indus Script* (1979), Research Reports 1, Department of Asian and African Studies, University of Helsinki; [handle](http://hdl.handle.net/10138/342677), [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). The 1980 source rights remain unresolved. The coordinator must integrate the listed image exceptions in [TRACK-EXCEPTIONS.txt](TRACK-EXCEPTIONS.txt); no shared ignore file was changed.

Repeat [verification](repair/2026-10-08-record-v1/verification.json), verify both old endpoints and the v3 freeze/packet hashes, inspect development boxes 27,53,76 and all five segmentation repairs, check full JSONL schema/continuation ownership, and have the coordinator complete both blind readers plus adjudication before scoring. Every created or changed path is listed in [changed-paths.json](repair/2026-10-08-record-v1/changed-paths.json).
'''
    (HERE/'README.md').write_text(intro,encoding='utf-8')
    report=f'''# Cropping v3: development and prepared blind endpoint, 8 October 2026

V3 produces **{fulltext}**, with zero releases. Its new blind endpoint is prepared, and its accuracy awaits coordinator readings. The method was selected on all 80 v2 rows and the 21 existing count pages. [Full summary](repair/2026-10-08-v3/full-summary.json), `rows`, `numbered_occurrences`, `continuation_lines`, `units`, `pages`; [freeze](repair/2026-10-08-v3/freeze-manifest.json); [selection](repair/2026-10-08-v3/blind/selection.json).

## Development findings and scope

{table}
The first endpoint's 60-row frame covers the numbered section on PDF31–79 and no sorted row. V2's 80-row frame covers all three sections (28/26/26), and those same 80 targets and 352 units are reused for v3 development. The old predictions, references and metrics are preserved. Parameter selection prevents interpreting the v3 development intervals as held-out accuracy.

V3 aligned strict unit recall is {v3['strict_top1']['aligned_recall']['correct']}/352 at top one and {v3['strict_top5']['aligned_recall']['correct']}/352 at top five. On matching-count rows, the same-position figures are {v3['strict_top1']['same_position_equal_count']['correct']}/{v3['strict_top1']['same_position_equal_count']['total']} and {v3['strict_top5']['same_position_equal_count']['correct']}/{v3['strict_top5']['same_position_equal_count']['total']}. Calibration uses those {v3['calibration']['n']} aligned positions: Brier {v3['calibration']['brier']:.6f}, ECE10 {v3['calibration']['ece10']:.6f}. It reuses the original coefficients without fitting on these rows. These development bins and bootstrap intervals are in [diagnosis.json](repair/2026-10-08-development-record-v1/diagnosis.json), `development_summary`, `development_intervals`. Fresh v3 calibration remains unmeasured.

The 21 reused page counts yield 1,847/1,847 numbered recall and precision (Wilson 99.8–100.0%). That recovers the v2 omissions on pages 66 and 112 and retains 288 numbered rows on the eight-column page 129 and 201 on the compact page 130. The reference also records ten unnumbered continuations on these pages. V3 locates all 10 and agrees with all 10 preceding-numbered-row links (Wilson 72.2–100.0% for each measure); its 1,857 physical detections equal the old source count. This is development corroboration on the reused pages. [Continuation check](repair/2026-10-08-development-record-v1/continuation-check.json), `continuation_recall`, `continuation_precision`, `preceding_numbered_parent_agreement`, `physical_lines_detected`; [development file](repair/2026-10-08-development-v3h/development.json), `development_count_pages`, `pages`.

## Diagnosis and crop changes

The earlier 80-row endpoint rejected 36 crops; 34 of those are among the 40 top-five whole-row failures. The 34-row target set is therefore a failure-stage subset. Both full reader tag lists and their exact source locations are retained in [diagnosis.json](repair/2026-10-08-development-record-v1/diagnosis.json), `v2_rejected_crops`, `v2_top5_failure_starts_at_crop`, `crop_issue_observations`. The text-search families overlap and are a way to locate observations, not independent error labels.

The field detector pairs print components and refines its horizontal band from repeated classification lines. It rejects components cut by the field-search boundary, masks every column's field and clamps row padding. Glyph components define each row's ink bounds; dashed underline components belong to the preceding drawing body. Unanchored tall components create explicit continuation lines without imposing a pitch or row count. Compact columns use the inherited print-column detector. Body segmentation removes underline groups temporarily, retains loss-rectangle strokes and separates short ticks next to tall units; matching restores each whole underline slot. The original CNN, template costs, code candidates and calibration are unchanged. [Implementation](crop_v3.py); [frozen parameters](repair/2026-10-08-v3/freeze-manifest.json), `parameters`, `inherited_column_parameters`, `code_hashes`.

All five previously diagnosed unit-window failures (rows 3,25,50,52,58) now have matching counts and compatible top-five rows in development. Row72 retains a top-five graphic-code miss under the unchanged recognizer and chart labels. Known source/window defects remain on development rows 27 (field/next-row ink and incomplete final patch),53 (classification digit at the glyph edge),76 (final patch clipped by the field boundary). Their source contexts are local in `data/raw/2026-10-07-helsinki1979-digitization/2026-10-08-v3/2026-10-08-development-v3h/row_027.png`, `row_053.png`, `row_076.png`; the observations are recorded in [development inspection](repair/2026-10-08-development-record-v1/visual-inspection.json). Independent crop acceptance on v3 boxes awaits the fresh source readers.

Development top-five compatible rows are 25/28 numbered,18/26 end-sorted,17/26 beginning-sorted. Count agreement is26/28,23/26,22/26. Field and graphic errors therefore remain after the principal crop repairs. These selected development strata supply no edition-level error census. [Diagnosis](repair/2026-10-08-development-record-v1/diagnosis.json), `development_by_section`.

## Fresh reference and verification handoff

The method froze at {freeze['created_utc']} and predictions at {pf['created_utc']}. The fresh selection has 80 numbered targets drawn from 572/2,004/2,004 section pools on 8/28/28 eligible pages. Page exclusions contain every earlier evaluation target page and the original ten development pages. Source-only exact/context images, 12 chart cards and21 count pages are frozen with hashes. All selected targets happen to have no detected continuation, so the physical-line count test and complete source pass supply the planned continuation check. [Selection](repair/2026-10-08-v3/blind/selection.json); [prediction freeze](repair/2026-10-08-v3/prediction-freeze.json), `packet_hashes`; [conventions](repair/2026-10-08-v3/blind/CONVENTIONS.md).

Two source-only readers and a third adjudicator are required. No new reference or metrics were created here. The frozen evaluator reports the old metrics and both numbered/physical-line recall, with pooled and bootstrap intervals. It retains the original five criteria and prevents a pass on an incompletely scored crop/number/count frame. Every full proposal remains quarantined for the separate human-plus-independent-AI verification package. Its [contract](OPTION-B-INTERFACE.md) requires complete source-page coverage and explicit continuation review. Large output is listed in [HOST-FILES.txt](HOST-FILES.txt) for coordinator backup. L's carrier/surface concordance remains separate.

## Earlier frozen endpoints, preserved record

'''
    (HERE/'REPORT.md').write_text(report+base('REPORT.md'),encoding='utf-8')
    retro=f'''# V3 cropping work, 8 October 2026

The new work produces a frozen source-only packet and {fulltext}, all quarantined. Development reuses the 80 v2 targets and all 21 existing count pages; no reader was asked to annotate the fresh packet. The coordinator will run both independent readers and adjudication. Their future timing, billed cost and deviations are unknown. [Full summary](repair/2026-10-08-v3/full-summary.json); [development record](repair/2026-10-08-development-record-v1/diagnosis.json).

Initial print-line clustering merged number/classification bands and located only 9/80 targets in trial v3a. Subsequent component-center pairing and repeated horizontal-field bounds located all 80 targets. Trials v3a–v3h remain in separate development directories; their JSONs and source inspection renders are preserved. Trial v3e finished while the crop source file had been edited, so its end-of-run code hash does not identify the loaded module. It is a diagnostic trial with incomplete code provenance. Final v3h captures the starting hash and confirms that the implementation stayed unchanged during the run. The freeze uses only v3h. [Final development](repair/2026-10-08-development-v3h/development.json), `code_sha256`, `code_unchanged_during_run`, `summary`; [trial v3e](repair/2026-10-08-development-v3e/development.json).

Source inspection found that a field search window could cut a drawing into small components that looked like digits. Excluding those clipped components and masking actual field bounds improved several page fields. Whole underline slots were restored after body segmentation, fixing the five named segmentation/association rows. Known rows 27/53/76 geometry defects remain, and the inherited matcher still proposes incorrect graphic variants on some complete units. No model, chart label or calibration was refitted. [Development inspection](repair/2026-10-08-development-record-v1/visual-inspection.json); [diagnosis](repair/2026-10-08-development-record-v1/diagnosis.json).

The stronger page exclusion resolves ambiguous old inverted or two-line target geometry and leaves 8/28/28 eligible section pages. The seeded sample has 80 targets and no detected continuation; the 21 fresh count pages therefore request both numbered and physical-line centers. The conventions add continuation-membership checks, the 597/598 neighbouring-cell rule and unique reader scratch directories. This task used one working process per script and no shared annotator helper; no fresh reader/adjudicator cost was incurred by this package. Earlier reader timing/deviations remain in the preserved record below.

The full run first completed 17 pages in 254.0 recorded seconds, then stopped on page 39 when strict JSON export rejected a non-finite score from an empty two-pixel unit window. Completed page files and the partial page 39 output are preserved. A separately recorded transport helper continued unchanged inference, marking {full['nonfinite_units_unresolved']} invalid unit windows unresolved with empty alternatives and null confidence, and retaining their original payloads as local string-valued witnesses. The resumed pass records {full['seconds']:.1f} seconds; failed-page time was not separately measured. [Transport manifest](repair/2026-10-08-v3/full-transport-manifest.json); [full summary](repair/2026-10-08-v3/full-summary.json), `reused_pages`, `original_completed_inference_seconds`, `seconds`, `nonfinite_units_unresolved`.

Available disk space before the large run was 135,483,957,248 bytes. The coordinator withdrew the 500 MB cap; source inspection renders and full page payloads stay local. Output is {full['bytes']:,} bytes, listed with its hash and page files for coordinator backup. No backup, publication, ledger mutation or repository-history action was performed. [Full summary](repair/2026-10-08-v3/full-summary.json), `bytes`, `path`, `sha256`; [HOST-FILES.txt](HOST-FILES.txt).

Incorrect-cwd read-only lookups returned missing-file errors and were corrected using the repository/package root. No source download, web search, package installation or new concordance acquisition was attempted. The existing PDF, original recognizer, digit library, chart snapshot, source-count reference and frozen evaluators were reused. Old frozen outputs are covered by the preservation checks in [verification.json](repair/2026-10-08-record-v1/verification.json). The prose scan and transport/schema checks are recorded there; fresh accuracy and edition-wide completeness remain for the coordinator and option-B package.

## Earlier process record, preserved

'''
    (HERE/'RETROSPECTIVE.md').write_text(retro+base('RETROSPECTIVE.md'),encoding='utf-8')
    (HERE/'IMPORT_INTERFACE.md').write_text('''# V3 proposal transport, 8 October 2026

The new physical-line JSONL and continuation links are specified in [OPTION-B-INTERFACE.md](OPTION-B-INTERFACE.md). Every row is quarantined and unreviewed. After complete verification, an adapter may supply L's source-qualified edition, literal letter-suffixed number, segment identifier and reviewed glyph/auxiliary fields. Reviewed carrier identity and surface concordance remain required. No ledger file changed and no new occurrence was imported. The large proposals and hashes are listed in [HOST-FILES.txt](HOST-FILES.txt).

## Preserved first/v2 import record

'''+base('IMPORT_INTERFACE.md'),encoding='utf-8')
    entry=json.loads(base('registry-entry.json'));entry.update(status='Frozen evaluation',question='Does ink-aware cropping improve Helsinki 1979 proposals on a fresh source-only blind test?',
        outcome=f"Earlier endpoints Failed and unchanged. V3 development on 80 reused v2 targets:71 counts,69 numbers,67 classifications,33 top-one and60 top-five whole rows;{v3['strict_top5']['aligned_recall']['correct']}/352 top-five unit recall. Reused 21 count pages:1847/1847 numbered recall/precision. Fresh80-row packet(28/26/26) and21 count pages prepared without references. Full:{full['rows']} physical-line proposals,{full['units']} unit windows,{full['nonfinite_units_unresolved']} unresolved,all quarantined;zero released.",
        challenge='Residual field ink and clipped final patches on development rows 27/53/76; number reading and graphic variants still fail. Short-only continuation detection and fresh calibration unverified. Fresh frame limited to8/28/28 eligible pages after strong exclusions.',
        remedy='Froze ink-aware field/row/unit windows with unchanged recognizer, chart and calibration; retained all development trials, sampled new source-only materials, added physical-line recall and provisional continuation transport for complete option-B review.',
        retry_when='Coordinator supplies two independent source readings and adjudication, then runs the unchanged v3 evaluator. Separate option-B package checks every source line with a person and independent AI; release needs its validated acceptance rule and complete source coverage. L additionally needs reviewed identity/surface concordances.')
    entry['evidence']+=['experiments/2026-10-07-helsinki1979-digitization/'+p for p in ['repair/2026-10-08-development-record-v1/diagnosis.json','repair/2026-10-08-v3/freeze-manifest.json','repair/2026-10-08-v3/prediction-freeze.json','repair/2026-10-08-v3/blind/selection.json','repair/2026-10-08-v3/full-summary.json','OPTION-B-INTERFACE.md','HOST-FILES.txt']]
    write(HERE/'registry-entry.json',entry)
    sources=json.loads(base('sources.json'));sources['reused_records']+=['repair/2026-10-07-v2/blind/adjudicated-reference.json (all 80 targets now development)','repair/2026-10-07-v2/blind/adjudicated-counts.json (all 21 pages now development)','repair/2026-10-07-v2/blind/reader-a/rows-part1.json and rows-part2.json: exact crop_issues','repair/2026-10-07-v2/blind/reader-b/rows-part1.json and rows-part2.json: exact crop_issues','follow-up/2026-10-07/endpoint-record-v1/unit-window-audit.json','experiments/2026-10-07-object-ledger/HELSINKI-INTERFACE.md (opened8October2026; no external concordance opened)']
    sources['v3_source_access']=dict(date='2026-10-08',opened_local_1979_PDF=True,downloaded=False,new_literature_search=False,fresh_reference_created=False,rights='1979 CC BY4.0 with attribution; raw renders/large proposals local',reuse_scope='Source image development; frozen v2 references unchanged. New blind packet contains source crops/cards only.')
    write(HERE/'sources.json',sources)
    existing=base('TRACK-EXCEPTIONS.txt').splitlines();new=[p.relative_to(HERE.parents[1]).as_posix() for p in (RUN/'blind').rglob('*.png')]
    (HERE/'TRACK-EXCEPTIONS.txt').write_text('\n'.join(dict.fromkeys(existing+sorted(new)))+'\n',encoding='utf-8')
    host=f"Coordinator backup requested; no backup performed by Package M.\n{full['path']}\nbytes={full['bytes']}\nsha256={full['sha256']}\nfreeze_sha256={full['freeze_sha256']}\n{full['raw_page_directory']}/ (new completed page files; all 159 source page hashes and paths in full-summary.json page_results)\nReused17 page files: data/raw/2026-10-07-helsinki1979-digitization/2026-10-08-v3/full-v1/pages/ (preserve partial page 39 too)\nInvalid unit witnesses: {str(Path(full['path']).parent/'invalid-unit-witnesses.jsonl').replace(chr(92),'/')}\nRaw inspection renders: data/raw/2026-10-07-helsinki1979-digitization/2026-10-08-v3/ (local only; source-derived CC BY4.0)\n"
    (HERE/'HOST-FILES.txt').write_text(host,encoding='utf-8')
    print(json.dumps(dict(updated=names+['HOST-FILES.txt'],rows=full['rows'],quarantined=full['rows'])))
if __name__=='__main__':main()
