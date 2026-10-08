"""Write living documentation from preserved completed-endpoint aggregates."""
from pathlib import Path
import json
import re

HERE = Path(__file__).resolve().parent
RECORD = HERE / 'repair/2026-10-08-endpoint-record-v1'
RUN = 'repair/2026-10-08-v3'
M = RUN + '/evaluation-2026-10-08-adjudicated/metrics.json'
D = RECORD.relative_to(HERE).as_posix() + '/diagnosis.json'
A = RECORD.relative_to(HERE).as_posix() + '/unit-window-audit.json'
C = RECORD.relative_to(HERE).as_posix() + '/reader-process-cost.json'


def read(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))


def base(name):
    return read(RECORD / 'documentation-snapshot.json')['files'][name]['text']


def write(name, value):
    p = HERE / name
    if isinstance(value, str) and name.endswith('.md'):
        value = polish(value)
    p.write_text(value if isinstance(value, str) else json.dumps(value, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')


def polish(text):
    """Space prose numbers without changing links, inline code or commands."""
    parts = re.split(r'(```[\s\S]*?```|`[^`\n]+`|\[[^\]\n]*\]\([^\)\n]*\))', text)
    words = 'row|rows|unit|units|PDF|on|of|in|at|and|or|to|from|with|over|below|all|sample|Brier|Sonnet|Reports|stress|pages|has|is|are|the|contains|contain|across|Wilson|for|its|labels|labelled|confidence|product|needs'
    suffixes = 'rows|row|units|unit|fields|field|counts|count|numbers|number|classifications|classification|crops|crop|tokens|token|tasks|task|files|file|pages|page|targets|target|drawings|drawing|readings|reading|columns|column|per|left|right|top|strict|own|source|centres|centers|seconds|hours|continuations|continuation'
    for i in range(0, len(parts), 2):
        s = parts[i]
        protected = []
        def protect(match):
            protected.append(match.group())
            return 'ZZWORD' + chr(65 + len(protected)-1) + 'ZZ'
        s = re.sub(r'\b(?:[Vv]\d+|ECE\d+|CISI\d+)\b', protect, s)
        s = re.sub(r'(?<=[A-Za-z])(?=\d)', ' ', s)
        s = re.sub(r'\b('+words+r')(?=\d)', r'\1 ', s)
        s = re.sub(r'(\d)(?=('+suffixes+r')\b)', r'\1 ', s)
        s = re.sub(r',(?=[A-Za-z])', ', ', s)
        s = re.sub(r',(?=\d{1,2}(?:\D|$))', ', ', s)
        s = re.sub(r'([%;])(?=\d)', r'\1 ', s)
        s = re.sub(r'([A-Za-z])(?=\*\*\d)', r'\1 ', s)
        s = s.replace('one,two orfive', 'one, two or five').replace('andtop-five', 'and top-five')
        s = s.replace('1,1,4 and2', '1, 1, 4 and 2').replace('top one and278', 'top one and 278')
        s = re.sub(r'(?<=[A-Za-z])(?=\(\d)', ' ', s)
        for j, original in enumerate(protected):
            s = s.replace('ZZWORD' + chr(65+j) + 'ZZ', original)
        for old in ['68,112,115,135,148,161','84,172,174','62,129,130','35,47,127,172','31,32,34,37,66']:
            s = s.replace(old, old.replace(',', ', '))
        parts[i] = s
    return ''.join(parts).replace('CC BY4.0', 'CC BY 4.0')


def measure(x):
    return f"{x['success']}/{x['total']} ({x['rate']*100:.1f}%; {x['ci95'][0]*100:.1f}–{min(1,x['ci95'][1])*100:.1f}%)"


def comparison_table():
    old = read(HERE / 'evaluation/2026-10-07-frozen-v1/metrics.json')['summary']
    v2 = read(HERE / 'repair/2026-10-07-v2/evaluation-2026-10-07-adjudicated/metrics.json')['summary']
    v3 = read(HERE / M)['summary']
    t = '| Outcome, Wilson 95% interval | First: 60 numbered rows, PDF31–79 | V2: 80 rows, three sections | V3: 80 fresh rows, three sections |\n|---|---|---|---|\n'
    for label, key in [('Crop acceptance', 'row_crop_correctness'), ('Drawing-unit count', 'drawn_unit_count_agreement'),
                       ('Literal inscription number', 'inscription_number_accuracy'), ('Five-position classification', 'classification_exact_accuracy'),
                       ('Whole row, top one', 'strict_top1'), ('Whole row, top five', 'strict_top5'),
                       ('Exact singleton-reference sequence', 'uniquely_resolved_exact_sequence')]:
        xs = [s[key]['whole_rows_all_sample'] if key in ['strict_top1', 'strict_top5'] else s[key] for s in [old, v2, v3]]
        t += f"| {label} | " + ' | '.join(measure(x) for x in xs) + ' |\n'
    return t


def main():
    diag = read(HERE / D); audit = read(HERE / A); cost = read(HERE / C)
    full = read(HERE / RUN / 'full-summary.json'); table = comparison_table()
    criteria = '| V3 frozen criterion, all 80 rows unless stated | Observed | Minimum passing numerator | Additional passing rows needed |\n|---|---|---|---|\n'
    for name, label in [('crop_90','Crop ≥90%'), ('number_90','Number ≥90%'), ('count_95','Count ≥95%'),
                        ('top5_rows_80','Top-five whole rows ≥80%'), ('random_page_recall_95','Random-page numbered recall ≥95%')]:
        x=diag['criterion_row_gaps'][name]
        criteria += f"| {label} | {x['observed']}/{x['total']} | {x['required_successes']}/{x['total']} | {x['additional_rows_needed']} |\n"
    report = f'''# Helsinki 1979: the completed v3 crop evaluation

V3 fails four of five frozen release criteria. In **80 fresh rows across the numbered, end-sorted and beginning-sorted sections (28/26/26), excluding both earlier samples by page**, it accepts 71 crops, reads 71 numbers and 72 classifications, matches 72 counts, and yields 38 top-one and 62 top-five compatible whole rows. Random-page numbered recall passes at 1,289/1,289. Cropping and unit segmentation still limit the proposals; every occurrence remains quarantined. [Frozen metrics]({M}), `summary`, `negative_result_criteria`; [diagnosis]({D}), `criterion_row_gaps`, `incompatible_whole_row_partitions`.

## Three frozen endpoints and their frames

{table}
The first endpoint contains **60 numbered-section rows from PDF31–79**, drawn from 3,460 of the original 11,369 detections, with no sorted-section target. V2 contains **80 rows across three sections (28/26/26)** with eligible pools 3,596/3,228/3,496. V3 contains **80 fresh rows across those sections (28/26/26)** from pools 572/2,004/2,004 on 8/28/28 eligible pages. V3 excludes every page carrying any first-60 or v2-80 target and the original ten development pages. The row comparisons have different source frames and references; they do not estimate a paired crop-repair effect or a section-weighted edition rate. [First metrics](evaluation/2026-10-07-frozen-v1/metrics.json), `summary`; [v2 metrics](repair/2026-10-07-v2/evaluation-2026-10-07-adjudicated/metrics.json), `frame`, `summary`; [v3 selection]({RUN}/blind/selection.json), `denominators`, `eligible_pages`, `excluded_pages`.

The first crop figure preserves its original annotator labels, including C's permissive judgments; the separate objective audit and later reference corrections remain in the [preserved earlier report]({RECORD.relative_to(HERE).as_posix()}/documentation-snapshot.json). Exact-sequence denominators retain only singleton-reference rows: 52,66,54. V3 has 369 reference units and 374 proposals; 28 units retain multiple strict candidates and three have empty strict sets. Those three rows remain in the 80-row whole-sequence denominator. The fully resolved-reference sensitivity is 62/77 top-five rows (80.5%; 70.3–87.8%), while the frozen criterion uses 62/80. [V3 metrics]({M}), `summary.reference_*`, `summary.strict_top5`.

{criteria}
The criterion gaps count passing rows required at the frozen point thresholds; they are not promises that repairing that many rows would validate a future method. The classification field and top-one sequence have reported scores but no separate global threshold. All four failures keep the global release gate closed. [Diagnosis]({D}), `criterion_row_gaps`.

## Unit recall and confidence calibration

| Outcome, stored row-bootstrap 95% interval | First: same 60 numbered rows | V2: same 80 three-section rows | V3: same 80 fresh three-section rows |
|---|---|---|---|
| Aligned strict top-one recall | 199/267 (74.5%; 66.3–81.7%) | 249/352 (70.7%; 64.2–76.8%) | 293/366 (80.1%; 73.6–86.2%) |
| Aligned strict top-five recall | 224/267 (83.9%; 76.0–90.6%) | 304/352 (86.4%; 81.1–91.2%) | 338/366 (92.3%; 87.8–96.4%) |
| Equal-count positional top one | 103/140 (73.6%; 58.4–85.3%) | 174/252 (69.0%; 61.0–76.2%) | 263/315 (83.5%; 77.0–88.9%) |
| Equal-count positional top five | 118/140 (84.3%; 68.7–95.7%) | 217/252 (86.1%; 79.2–92.1%) | 301/315 (95.6%; 91.6–98.8%) |
| Brier score | 0.1488 (0.107–0.197) | 0.1925 (0.158–0.231) | 0.1117 (0.095–0.131) |
| Ten-bin calibration error | 0.1056 (0.080–0.185) | 0.0755 (0.047–0.147) | 0.1153 (0.090–0.151) |

Aligned recall counts resolved strict units: the three v3 empty sets leave 366 of 369 units in that denominator. Extra proposals do not reduce aligned recall; their effects enter count and whole-row scores. Positional scores and calibration are conditional on equal counts and resolved strict positions (315 v3 units). V3 kept the original confidence coefficients and performed no refit. Its 43 units in the ≥0.9 confidence bin all match top one, within this conditional sample; that bin provides no row-release authorization. The stored v3 intervals use 2,000 row resamples within sections, seed 2026100881. [Three metric files](evaluation/2026-10-07-frozen-v1/metrics.json), [v2](repair/2026-10-07-v2/evaluation-2026-10-07-adjudicated/metrics.json), [v3]({M}), `summary`, `row_bootstrap_95`, `bootstrap`.

## Source-row and physical-line recall

| Independent count frame | V2 recall / precision, pooled Wilson 95% | V3 recall / precision, pooled Wilson 95% |
|---|---|---|
| 18 random pages, six per section | 1,242/1,286 (96.6%; 95.4–97.4%) / 1,242/1,242 (100%; 99.7–100%) | 1,289/1,289 for both (100%; 99.7–100%) |
| Stress pages 62,129,130 | 561/561 for both (100%; 99.3–100%) | 561/561 for both (100%; 99.3–100%) |
| Random-page physical lines, including unnumbered lines | Not a frozen v2 metric | 1,296/1,296 for both (100%; 99.7–100%) |

V3's 18 random pages are fresh relative to the previous count-page set. Its seven extra physical lines occur on pages 35,47,127,172 and175. Both readers agree on 1,850 numbered rows and 1,857 physical lines across all 21 pages and 52 columns; the stress pages contain no extra physical lines. Random-page bootstrap recall/precision intervals are 100–100% for v3, compared with 90.5–100% numbered recall for v2. A sampled zero-miss result does not establish complete edition coverage. The compact stress pages 129–130 remain development pages excluded from recognition sampling; this count test measures discovery, not sign recognition on those pages. Continuation parents in the count reference remain probable assignments to the numbered line above, supported by position rather than a printed link. [V3 metrics]({M}), `source_row_recall`, `physical_line_recall`; [adjudication]({RUN}/blind/adjudication-notes.json), `counts_comparison`; [reader B counts]({RUN}/blind/reader-b/counts.json), `notes`.

## Limiting stages, compared with v2

Of v3's **18 incompatible top-five rows**, eight fail the crop check, six have unequal counts despite an accepted crop, and four have accepted crops and equal counts. The four are row31 with four resolved unit misses and rows3,35,70 with one empty strict-reference set each. Inspecting row31 shows that the seven windows cut the U and adjacent fish drawings and assign overlapping underline slots. The refined diagnostic partition is therefore **8 crop, 7 segmentation/underline association, 3 unresolved strict-reference rows and 0 resolved graphic-proposal misses on inspected correct windows**. V2's corresponding inspected partition was **34 crop, 5 segmentation/underline association and 1 graphic-proposal miss** among 40 top-five failures. These are earliest observed failure stages, not counterfactual accuracy gains. [V3 diagnosis]({D}), `incompatible_whole_row_partitions`, `unresolved_strict_units`; [window audit]({A}), `refined_top5_counts`, `observations`; [v2 audit](follow-up/2026-10-07/endpoint-record-v1/unit-window-audit.json), `refined_top5_incompatible_rows`.

The six accepted-crop count failures are concrete: row14 promotes a speck to a unit; row32 emits an extra underline fragment and cuts a compound window; row41 splits one tick group into three; rows60 and65 promote remote specks; row68 merges two adjacent drawings. The seven inspected resolved segmentation failures include row31's equal-count window shifts. The 65 accepted-crop, equal-count rows have 247/282 strict resolved positional matches at top one and278/282 at top five. All four resolved top-five misses lie in row31. Equal counts remain a proxy for the other rows' boundaries; this inspection covers failed top-five cases, not every unit. Top-one whole-row failures partition into 9 crop,6 count and27 count-consistent candidate failures; the last group includes the same three unresolved rows and row31. [Diagnosis]({D}), `count_consistent_accepted_crop_proxy`, `accepted_crop_equal_count_top5_misses`; [audit]({A}), `observations`.

The nine rejected crops comprise six with neighbour-row ink (21,44,48,55,58,66) and three with cut drawings (30,76,77). Row77 also loses an own underline; rows76 and77 have field boxes overlapping the final drawing. Row30 retains a compatible top-five sequence despite its rejected crop. V2's overlapping tags named omitted own underlines in18 rows, neighbour ink in13, number ink in13 and cut ink in4. V3's residual crop problem concentrates at the lower row edge and the field boundary. The original reader strings are retained unchanged alongside these post-outcome tag families. [Diagnosis]({D}), `crop_issues`, per-row `adjudicated_crop_issues`; [audit]({A}), `crop_tag_families`; [v2 diagnosis](follow-up/2026-10-07/endpoint-record-v1/diagnosis.json), `crop_issues`.

Number reading fails in9/80 rows and classification-field reading in8/80, with15/80 having at least one wrong field. Seven wrong numbers (22,35,40,43,52,69,73) and four wrong classifications (17,25,34,57) remain within accepted-crop, equal-count rows. Those eleven rows are disjoint. V2 had18 wrong numbers,25 wrong classifications and30 rows with either wrong field; its accepted-crop, equal-count subset retained three wrong numbers and seven wrong classifications. Field errors are separate from drawing-code classification. [Diagnosis]({D}), `subsets`; [v2 diagnosis](follow-up/2026-10-07/endpoint-record-v1/diagnosis.json), `subsets`.

| V3 section, frame size | Crop failures | Count failures | Top-five row failures | Number failures | Classification-field failures |
|---|---|---|---|---|---|
| Numbered,28 | 1 | 1 | 3 | 1 | 2 |
| End-sorted,26 | 3 | 2 | 6 | 4 | 2 |
| Beginning-sorted,26 | 5 | 5 | 9 | 4 | 4 |

Beginning-sorted rows contribute half the top-five failures and five of the eight count failures. Neighbour ink occurs on PDF68,112,115,135,148,161; drawing cuts occur on84,172,174. Page87 contributes both the equal-count underline/window failure (31) and a count failure (32). End-sorted fields lie on the left (3/26 rejected crops); the other sections use the right (6/54). Even pages have6/44 rejected crops and odd pages3/36. These small groups do not isolate a parity or margin-side cause. V2 had similar crop/top-five failures across its three sections (13/12/11 and14/13/13), whereas v3's remaining failures cluster more in its sorted-section sample. No compact multi-column recognition row was evaluated. [Diagnosis]({D}), `by_section`, `by_page`, `by_margin_side`, `by_page_parity`; [v2 diagnosis](follow-up/2026-10-07/endpoint-record-v1/diagnosis.json), corresponding fields.

## Chart labels and future correction

| Chart cell | Frozen card label / observed printed code | Reference units by exact cell key | Top-one / any top-five proposal units |
|---|---|---|---|
| 20:4:1 | 506 / 508 | 3 (31:0,32:0,32:2) | 2 / 3 |
| 21:6:1 | 206 / 208 | 2 (60:6,67:4) | 2 / 6 |
| 20:4:13 | 360 / 350 | 0 | 0 / 0 |
| 21:6:31 | 285 / 286 | 0 | 0 / 1 |

The first two differences affect reference units and predictions in this sample; the fourth appears only as a non-top-one proposal (row46 unit1, rank4). This endpoint scores the shared card vocabulary, so the printed-label differences do not change its frozen codes or metrics. The adjudication notes additionally locate row58 unit0 at20:4:1, while the reference locates it at21:7:5, another card labelled506. The table uses exact reference keys and preserves that conflicting prose locator separately. It is unsafe to replace every occurrence of506 or206 globally because different cells share those codes. [Adjudication notes]({RUN}/blind/adjudication-notes.json), `card_label_observations`; [diagnosis]({D}), `chart_label_audit`, `chart_location_witness_disagreement`.

Post-outcome source inspection supports the reference's row58 locator: its first drawing is two overlapping circles with corner ticks, matching21:7:5;20:4:1 is a branched stem. This local observation preserves both witnesses and makes no new reference. [Locator inspection]({RECORD.relative_to(HERE).as_posix()}/chart-locator-inspection.json), `observation`, `source_hashes`.

[Package P](../2026-10-08-chart-reference-audit/PROTOCOL.md) owns the full chart audit. A future pipeline should take its reviewed, cell-keyed snapshot and explicit old-to-new mapping as new inputs, regenerate candidate-code labels and blind chart cards, retain unresolved and duplicate-code cases, and check confidence calibration under the new labels. Freeze those changes and their evaluator before a fresh source reference. Preserve this endpoint for comparison; a separate cell-remapping sensitivity can measure label effects but cannot replace its metrics. Package N's verification reference must declare its chart version and independently confirm the row58 cell identity before using that cell-specific mapping.

## Quarantine and package N handoff

All **11,769 v3 physical-line proposals (11,702 numbered occurrences and67 continuations) remain quarantined; zero are released**, as do the11,369 original occurrences. The full JSONL has54,384 unit windows, five unresolved empty windows, and159 source pages. Its106,190,599-byte payload stays local; [HOST-FILES.txt](HOST-FILES.txt) lists it for coordinator backup. No full inference was repeated while recording this endpoint. [Full summary]({RUN}/full-summary.json), `rows`, `numbered_occurrences`, `continuation_lines`, `units`, `nonfinite_units_unresolved`, `released_rows`.

An automatic route requires a separately frozen repair and fresh blind test passing all five global criteria, then complete geometry, resolved continuation/editorial state, singleton top-one codes, independent numeric-witness agreement, minimum unit confidence0.90 and confidence product0.90 for each eligible row. The chart correction also needs an explicit version and label validation. High confidence cannot bypass a failed global gate. The authorized option-B route uses the v3 inventory as proposals, with complete source-column coverage, reviewed line membership and missing-line recovery; its separately validated acceptance rule and human/expert source check remain required. [Freeze]({RUN}/freeze-manifest.json), `release_rule`; [proposal contract](OPTION-B-INTERFACE.md); [schema](option-b-schema.json).

[Package N's pilot](../2026-10-08-helsinki1979-row-verification/pilot/PILOT-RESULTS.md) used v2 proposals on216 target rows: readers agreed on185/216 (85.6%; Wilson80.3–89.7%), and31 went to adjudication. Each role passed16/18 all-field hidden controls (88.9%;67.2–96.9%), below its95% screening threshold; adjudication matched all18. It recommends clarified coincident-pair/unit-kind conventions, package P's reviewed chart and a second pilot with v3 before a full run. Seeing proposals saved no reader time in that pilot. Package M supplies immutable source coordinates, physical-line keys, suffix-preserving numbers, candidate sets, confidence and source/freeze hashes through the [option-B interface](OPTION-B-INTERFACE.md); N creates its own reviewed records under its [input contract](../2026-10-08-helsinki1979-row-verification/INPUT_CONTRACT.md). The original proposals and endpoint stay unchanged.

N's measured planning projection for two AI roles plus adjudication on11,702 numbered occurrences is336.4 million task tokens (bootstrap95%302.2–366.1 million) and346.0 summed agent-hours (276.1–462.3), before an unmeasured human/expert pass. Task tokens include cached context and are not a price. The pilot is three pages, so those planning intervals do not measure full-edition verification accuracy. A person checking every numbered occurrence would add195.0,390.1 or975.2 hours at assumed one,two orfive minutes per row, plus continuation, source-coverage and ledger work; human throughput has not been observed. [N projection](../2026-10-08-helsinki1979-row-verification/pilot/coordinator-cost-projection-v1.json), `full_run`; [cost record]({C}), `package_n_pilot`. L still requires independently reviewed carrier/surface concordances and imports none here.

## Development, provenance and reproduction

V3 reused all80 v2 targets and352 units, and21 old count pages, to select its crop method before freezing. Development scores were71 counts,69 numbers,67 classifications,33 top-one and60 top-five rows,327/352 aligned top-five units, and1,847/1,847 numbered recall. These Exploratory development results remain in the [development diagnosis](repair/2026-10-08-development-record-v1/diagnosis.json); they are separate from the fresh endpoint above. The old classifier, digits, chart and calibration were reused unchanged. The [freeze]({RUN}/freeze-manifest.json) and [prediction freeze]({RUN}/prediction-freeze.json) precede all new readings. The complete reader/adjudication process and deviations are recorded in [RETROSPECTIVE.md](RETROSPECTIVE.md) and [reader cost]({C}).

The new record reuses `record_repaired_endpoint.py`'s Wilson and diagnostic functions, the v2 diagnosis and window audit, the frozen scorer and all supplied reader witnesses. Reproduction commands are in [README.md](README.md). Source attribution: Kimmo Koskenniemi and Asko Parpola, *Corpus of Texts in the Indus Script* (1979), University of Helsinki, [handle](http://hdl.handle.net/10138/342677), [CC BY4.0](https://creativecommons.org/licenses/by/4.0/); raster cropping and annotations are modifications. No new source download, literature search, chart correction or ledger import was performed.
'''
    write('REPORT.md', report)
    readme = f'''# Package M: completed Helsinki 1979 v3 endpoint

V3 fails four of five frozen release criteria. On **80 fresh rows across three sections, excluding both earlier samples**, it has71 accepted crops,71 correct numbers,72 classifications,72 counts,38 top-one and62 top-five whole rows. Random-page numbered recall passes at1,289/1,289. Every proposal remains quarantined; zero are released. [Frozen metrics]({M}), `summary`, `negative_result_criteria`.

{table}
The first frame is60 numbered-section rows from PDF31–79, with no sorted row. V2 is80 rows across numbered/end-sorted/beginning-sorted sections(28/26/26). V3 is80 fresh rows across those sections(28/26/26), excluding all earlier target pages and development pages, from572/2,004/2,004 eligible occurrences. These frames and references differ. Exact-sequence subsets contain52/66/54 singleton-reference rows. [REPORT.md](REPORT.md) gives unit recall, calibration, source-count intervals and their denominators.

{criteria}
V3 random-page numbered recall and precision are1,289/1,289 (Wilson95%99.7–100%). Physical-line recall and precision are1,296/1,296 (99.7–100%); stress-page numbered and physical recall/precision are561/561 (99.3–100%). The count frame is18 fresh random pages plus stress62,129,130; the latter remain development pages for recognition. [Metrics]({M}), `source_row_recall`, `physical_line_recall`.

The18 top-five failures begin at8 crops,7 segmentation/underline defects and3 unresolved strict-reference rows; no resolved graphic-proposal miss remains on the inspected correct windows. Numbers or classifications fail in15/80 rows, overlapping those stages. Three chart-label differences appear in reference or proposal cells; the frozen card vocabulary is preserved, and [package P](../2026-10-08-chart-reference-audit/PROTOCOL.md) owns correction. [Diagnosis]({D}); [window audit]({A}); [REPORT.md](REPORT.md).

## Proposals and verification

The full inventory contains**11,769 physical-line proposals,11,702 numbered occurrences,67 continuations and54,384 unit windows**, including five unresolved empty windows, across159 pages(PDF22–180). All remain quarantined. [Full summary]({RUN}/full-summary.json), `rows`, `units`, `released_rows`; [HOST-FILES.txt](HOST-FILES.txt) lists the106,190,599-byte local JSONL for coordinator backup.

[Package N's pilot](../2026-10-08-helsinki1979-row-verification/pilot/PILOT-RESULTS.md) recommends a second pilot with v3 proposals, clarified conventions and P's reviewed chart before a full verification run. It has not established the human/expert acceptance route. Use the immutable [option-B contract](OPTION-B-INTERFACE.md) and [schema](option-b-schema.json), preserving physical-line keys, coordinates, continuation links, literal suffixes and source/freeze hashes. Complete source-page review must recover omissions and resolve continuation ownership. L's reviewed identity/surface joins remain separate. Release requires a new validated acceptance rule or a fresh pipeline passing every frozen criterion plus its per-row rule.

The80 v2 rows were used for v3 development, giving71 counts,69 numbers,67 classifications,33 top-one and60 top-five rows. They selected the method and remain Exploratory. [Development diagnosis](repair/2026-10-08-development-record-v1/diagnosis.json). Both older frozen endpoints and the frozen v3 files are unchanged.

## Repeat the small record from the repository root

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
& 'C:\\Users\\sandh\\.venvs\\indus-ml\\Scripts\\python.exe' experiments/2026-10-07-helsinki1979-digitization/record_v3_endpoint.py --out experiments/2026-10-07-helsinki1979-digitization/review/v3-endpoint-record-repeat
& 'C:\\Users\\sandh\\.venvs\\indus-ml\\Scripts\\python.exe' experiments/2026-10-07-helsinki1979-digitization/evaluate_crop_v3.py --out experiments/2026-10-07-helsinki1979-digitization/review/v3-evaluation-repeat
& 'C:\\Users\\sandh\\.venvs\\indus-ml\\Scripts\\python.exe' experiments/2026-10-07-helsinki1979-digitization/verify_v3_endpoint_record.py --out experiments/2026-10-07-helsinki1979-digitization/review/v3-record-check-repeat.json
python tools/review_prose.py --path experiments/2026-10-07-helsinki1979-digitization --no-write
```

Use new output paths; scripts refuse to overwrite prior runs. The evaluator replay is byte-identical to the coordinator's metrics. `inspect_v3_endpoint.py` renders ten small source/window overlays into a new local raw directory; `audit_v3_endpoint_windows.py` records the observed failure cases. `write_v3_endpoint_docs.py` regenerates these living documents from aggregates and their pre-record snapshots. Earlier inference and packet construction commands remain in the [preserved previous README]({RECORD.relative_to(HERE).as_posix()}/documentation-snapshot.json).

The [preservation check]({RECORD.relative_to(HERE).as_posix()}/preservation-check.json) covers520 frozen witnesses; [verification]({RECORD.relative_to(HERE).as_posix()}/verification-final.json) also checks replay, stage partitions, chart uses and costs. Inspect row31's seven shifted unit windows, the six accepted-crop count failures, unresolved rows3/35/70 and the row58 chart locator conflict. Every path changed for this follow-up is listed in [changed-paths.json]({RECORD.relative_to(HERE).as_posix()}/changed-paths.json).

Source attribution: Kimmo Koskenniemi and Asko Parpola, *Corpus of Texts in the Indus Script* (1979), Research Reports1, Department of Asian and African Studies, University of Helsinki; [handle](http://hdl.handle.net/10138/342677), [CC BY4.0](https://creativecommons.org/licenses/by/4.0/). Source crops, proposals and annotations are modifications. Raw renders and large exports remain local. [sources.json](sources.json) records access and rights; this follow-up downloaded nothing and changed no shared repository file.
'''
    write('README.md', readme)
    groups=cost['groups']
    cost_table='| Task group | Tasks | Recorded total tokens | Summed duration, seconds |\n|---|---|---|---|\n'
    for key,label in [('rows','Two readings of80 rows'),('counts','Two readings of21 count pages'),('adjudication','Third-reader adjudication'),('all','All tasks')]:
        x=groups[key];cost_table+=f"| {label} | {x['tasks']} | {x['tokens']:,} | {x['summed_duration_seconds']:,.3f} |\n"
    retro=base('RETROSPECTIVE.md')
    retro+=f'''

## Completed v3 endpoint, recorded 8 October 2026

The coordinator completed two independent Claude Sonnet5.5 readings of all80 fresh rows and21 count pages, then a third-reader adjudication. Four40-row tasks and two count tasks used separate source-only sessions and scratch folders. Readers rendered source pixels and compared position-chart cards under the frozen conventions; no prediction was supplied. The coordinator hash-checked all three evaluators and ran `evaluate_crop_v3.py` unchanged. This package recorded that outcome and reran the scorer into a new directory, without new inference or references. [Metrics]({M}); [evaluator replay]({RECORD.relative_to(HERE).as_posix()}/evaluator-replay/metrics.json).

The readers agree on all80 inscription numbers,classifications,counts and line memberships(320 fields),357/369 strict unit sets,79/80 crop judgments and369 underline flags. Twelve strict-set disagreements lie in12 rows; the crop disagreement is a thirteenth row. Adjudication keeps67/80 rows agreed on all compared fields, settles the twelve unit disagreements and rejects row21 for a small strip of neighbour ink. It also empties the strict set for row35 unit2, which both readers had filled with23: the source is a continuous high tick while that card shows a dot and gapped stroke. Three strict sets remain empty(3:5,35:2,70:4), and28 remain multi-code sets. Raw unit-kind labels differ in32/369 units and are standardized by the adjudicator. Shape-only lists use different reader conventions; after adding strict codes to both lists,165/369 agree exactly. None of those initial files was edited in this recording. [Adjudication notes]({RUN}/blind/adjudication-notes.json), `agreement_summary`, `disagreement_summary`, `policy`; [diagnosis]({D}), `readers`.

The two count readers agree on all52 per-column counts:1,850 numbered rows and1,857 physical lines, including seven unnumbered continuations. Adjudication compares3,707 centres, finds59 differing by at least1 pt(maximum4 pt), and records12 centre/extent overrides. Their continuation parents are probable preceding-line assignments, with no printed links. The80 sampled recognition targets have one physical line each, so the count pages supply the fresh continuation-discovery evidence. [Notes]({RUN}/blind/adjudication-notes.json), `counts_comparison`, `counts_centre_overrides`; [reader count notes]({RUN}/blind/reader-b/counts.json).

The process has disclosed deviations. Some readers listed other role folders or, for reader B's count task, names one level above BLIND including predictions/frame files; they report opening none. Reader A part2 used source renders up to24 pixels per point, above the suggested working scale. Reader B part2 stopped a hung helper append in its own scratch folder. The adjudicator opened wide context images by script without viewing those sheets, rendered original count pages instead of opening the supplied page PNGs, and used OCR only on chart-label raster strips. An unrelated-process listing exposed command lines from other projects; the adjudicator reports no experiment output exposure. It inspected155 chart-label OCR disagreements by eye while532 agreeing pairs had only the two OCR readings; that limited chart check is not the whole-chart audit. All readers report no prediction/other-reader exposure; these are declarations rather than independently logged access proofs. [Cost record]({C}), `reader_notes`, `adjudication_exposure`; [adjudication notes]({RUN}/blind/adjudication-notes.json), `files_opened`, `not_opened`, `card_label_observations`, `exposure`.

The four chart-label differences remain in the frozen vocabulary. Exact reference keys show five affected units, while the prose notes additionally name row58 unit0 at a different cell from the reference. This record keeps both witnesses and audits proposals by template key, avoiding a global code replacement. Package P owns the chart correction. Reader schema differences(`line`/`line_index`/`line_number`, `kind`/`line_kind`, explicit counts/`unit_orders`) are normalized only for the agreement computation; raw files remain intact. [Diagnosis]({D}), `chart_label_audit`, `chart_location_witness_disagreement`.

{cost_table}
The ledger records**2,486,666 task tokens and11,108.273 summed seconds(3.086 task-hours)** across seven tasks, including adjudication. The row tasks alone average9,403.025 tokens and43.846 seconds per reading across160 readings. All tasks combined use31,083.325 tokens per80-row target, also carrying count-page work. These totals include input,cached-context re-reads and output and establish no billed dollar amount or human throughput. Task durations are summed, not elapsed wall time. [Coordinator ledger]({RUN}/blind/coordinator-task-ledger.jsonl); [cost aggregate]({C}), `groups`, `row_tokens_per_reading`, `row_seconds_per_reading`.

The fresh endpoint passes source discovery but fails crop,number,count andtop-five criteria by1,1,4 and2 rows respectively. The post-outcome window inspection assigns18 top-five failures to8 crops,7 segmentation/underline defects and3 unresolved-reference rows. V2's inspected counterpart was34 crops,5 segmentation/underline defects and1 graphic-proposal miss. This narrows repair targets and does not release a row. Package N's separate three-page pilot projects336.4 million tokens and346 summed agent-hours for two AI roles plus adjudication; its first pilot failed its95% role screening threshold. It recommends a second pilot with v3 and corrected conventions/chart. Human/expert source checks and ledger joins remain unmeasured work. [REPORT.md](REPORT.md); [N pilot](../2026-10-08-helsinki1979-row-verification/pilot/PILOT-RESULTS.md).

The recorder first failed before writing outputs because packet hash paths were treated as package-relative; they are blind-directory-relative. A subsequent schema error exposed `line_kind`/`unit_orders` in one reader return. Normalizing those fields fixed the agreement check. A six-use chart assertion exposed the row58 locator conflict; the final analysis records five explicit reference-key uses and retains the conflicting sixth prose locator. Those recorder failures occurred before creating the endpoint-record directory and changed no frozen witness. The first verification reported a missing registry evidence path because its own output had not yet been written; allowing that expected output fixed the check, and the failed check file remains preserved. A read-only Git ignore check initially rejected repository ownership; an ephemeral command option permitted the check without changing configuration. Pre-record text snapshots are ignored, so a small hash-checked JSON snapshot also preserves the documents for portable regeneration. No source search, download, full transcription rerun or large replay copy was made. Preservation covers520 files; review paths and checks are in [README.md](README.md).
'''
    write('RETROSPECTIVE.md',retro)
    entry=json.loads(base('registry-entry.json'))
    entry.update(status='Failed',
        question='Does ink-aware v3 cropping pass the frozen Helsinki1979 release criteria on a fresh three-section sample?',
        outcome='First:60 numbered-section rows PDF31–79,33 counts,23 numbers,24 top-five rows. V2:80 three-section rows,44 crops,59 counts,62 numbers,55 classifications,20 top-one/40 top-five rows. V3:80 fresh three-section rows,71 crops,72 counts,71 numbers,72 classifications,38 top-one/62 top-five,28/54 singleton exact;338/366 resolved unit top-five recall. Fresh random numbered recall1289/1289 and physical1296/1296;stress561/561. Four of five criteria fail, gaps1 crop,1 number,4 count,2 top-five rows. All11769 v3 proposals and11369 original occurrences quarantined;zero released.',
        challenge='V3 top-five failures:8 rejected crops,7 segmentation/underline defects,3 unresolved strict-reference rows. Fields wrong in15/80. Four chart-card/printed-code differences remain frozen;row58 has conflicting cell locators. Compact stress pages have count evidence but no fresh recognition sample.',
        remedy='Preserved all three frozen endpoints,recorded intervals/threshold gaps,inspected failure windows,computed reader agreement and task costs,and documented cell-keyed future chart correction and package N handoff. Unchanged evaluator replay;no chart correction,reference edit or full inference rerun.',
        retry_when='Automatic release needs a separately frozen layout/unit/chart repair and fresh blind evaluation passing every global criterion plus each row rule. Package N needs a second screening pilot with v3,P-reviewed chart and clarified conventions,a validated acceptance rule,complete source-column coverage and human/expert checks. L additionally needs reviewed identity/surface concordances.')
    extra=[M,D,A,C,RUN+'/blind/adjudicated-reference.json',RUN+'/blind/adjudicated-counts.json',RUN+'/blind/adjudication-notes.json',RUN+'/blind/coordinator-task-ledger.jsonl',RECORD.relative_to(HERE).as_posix()+'/preservation-check.json',RECORD.relative_to(HERE).as_posix()+'/verification-final.json']
    entry['evidence']=list(dict.fromkeys(entry['evidence']+['experiments/2026-10-07-helsinki1979-digitization/'+x for x in extra]+['experiments/2026-10-08-helsinki1979-row-verification/pilot/PILOT-RESULTS.md','experiments/2026-10-08-chart-reference-audit/PROTOCOL.md']))
    write('registry-entry.json',entry)
    sources=json.loads(base('sources.json'))
    sources['recorded_date']='2026-10-08'
    sources['sources'] += [dict(id='v3-blind-evaluation-record',title='Helsinki1979 frozen v3 blind readings, adjudication and evaluation',authors=['Claude Sonnet5.5 readers A and B','Claude Sonnet5.5 adjudicator C','research coordinator'],year=2026,venue='Private research repository evaluation record',url=None,opened=True,seen_only_search_snippet=False,quoted_words=0,status='Frozen evaluation',source_locations=[RUN+'/blind/reader-a/rows-part1.json: notes and rows',RUN+'/blind/reader-a/rows-part2.json: notes and rows',RUN+'/blind/reader-a/counts.json: notes and pages',RUN+'/blind/reader-b/rows-part1.json: notes and rows',RUN+'/blind/reader-b/rows-part2.json: notes and rows',RUN+'/blind/reader-b/counts.json: notes and pages',RUN+'/blind/adjudication-notes.json',RUN+'/blind/coordinator-task-ledger.jsonl',M+': summary, rows, source_row_recall, physical_line_recall, negative_result_criteria']),
                           dict(id='package-n-pilot',title='Pilot results: two readers and an adjudicator on three pages',authors=['research coordinator'],year=2026,venue='Private research repository package N pilot',url=None,path='experiments/2026-10-08-helsinki1979-row-verification/pilot/PILOT-RESULTS.md',opened=True,seen_only_search_snippet=False,quoted_words=0,source_locations=['Accuracy on the hidden controls','Agreement and adjudication','Time and token use','Changes before a full run','Process notes'])]
    sources['v3_endpoint_record']=dict(date='2026-10-08',supplied_reference_opened=True,reference_created_by_this_followup=False,raw_source_overlays='data/raw/2026-10-07-helsinki1979-digitization/2026-10-08-endpoint-inspection-v1/',downloaded=False,literature_search=False,chart_corrected=False,package_P_protocol_opened=True,package_N_pilot_and_contract_opened=True)
    write('sources.json',sources)
    interface=base('OPTION-B-INTERFACE.md')
    interface=interface.replace('Fresh calibration awaits the blind\nreference.',f'The completed fresh evaluation reports Brier0.1117 and ECE10\n0.1153 on315 resolved equal-count positions; see [metrics]({M}),\n`summary.calibration`, with stored row-bootstrap intervals.')
    interface+=f'''

## Completed endpoint and package N, 8 October 2026

The fresh v3 endpoint fails four global criteria; all proposals remain
quarantined. The proposal hash and source geometry are immutable. Package N
should consume this inventory under its [contract](../2026-10-08-helsinki1979-row-verification/INPUT_CONTRACT.md),
keeping its own chart-versioned source readings, missing-line additions,
continuation adjudications and release decisions. Its [pilot](../2026-10-08-helsinki1979-row-verification/pilot/PILOT-RESULTS.md)
recommends a second screening pilot with v3, clarified coincident-code and
unit-kind conventions and package P's reviewed chart. The two-AI pilot has
not measured or completed the authorized human/expert source check.

Preserve alternative `template_key` values when adapting chart codes. The
four disclosed cell-label differences affect five explicit reference-key
units and10 top-five proposed units in this sample, across three cells.
The adjudication notes additionally name row58 unit0 at20:4:1 while its
reference records21:7:5, both labelled506. Resolve that locator against the
source in the verification record. Never remap repeated code506 or206 by a
global numeric substitution. The frozen proposals, cards and scored codes
remain unchanged; corrected mappings enter N's declared vocabulary and a
separately frozen future recognition pipeline. [Cell-use audit]({D}),
`chart_label_audit`, `chart_location_witness_disagreement`.
'''
    write('OPTION-B-INTERFACE.md',interface)
    print(json.dumps(dict(updated=['README.md','REPORT.md','RETROSPECTIVE.md','registry-entry.json','sources.json','OPTION-B-INTERFACE.md'])))


if __name__ == '__main__':
    main()
