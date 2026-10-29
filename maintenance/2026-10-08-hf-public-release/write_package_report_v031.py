"""Write owner-facing 0.3.1 findings from the new validation witnesses."""
from pathlib import Path
import shutil
from build_release import HERE,read,dump,sha

def main():
    final=read(HERE/'validation-2026-10-08-v45.json');review=read(HERE/'review-rerun-2026-10-08-v41.json');rebuild=read(HERE/'rebuild-comparison-2026-10-08-v42.json')
    assert final['status']==review['status']==rebuild['status']=='Verified computation'
    files=final['release_files'];size=final['release_bytes'];script_count=len(review['source_script_records'])
    counts='| Configuration | Rows |\n|---|---:|\n'+''.join(f"| `{r['config'] if 'config' in r else r['name']}` | {r['rows']} |\n" for r in final['configurations'])
    root_readme=f'''# Package O: release version 0.3.1

The [release folder](release/README.md) contains **23 configurations, 3,308 rows and 1,142 images**. All loads, schemas, source values and images pass; the scorer reproduces v1/v2/v3 with **zero mismatches**. A fresh build matches **{files}/{files} files**, totaling **{size:,} bytes**. [Final validation](validation-2026-10-08-v45.json), configurations, images, benchmark_scores, review_checks and rebuild.

Prediction files can use the card's `printed_inscription_id` and `classification_literal` keys or the frozen aliases. The scorer rejects missing keys, conflicting values and numeric values supplied where strings are required; null is allowed. Minimal card-only files reproduce **23/19 of 60, 62/55 of 80 and 71/72 of 80** correct numbers/classifications. All **27 new format cases** pass: nine valid files and eighteen rejected files. [Prediction-format check](prediction-format-2026-10-08-v41.json), cases.

The independent readings now flag P's **26 definite changes**: six v1 A, five v1 B and fifteen v2 A units. V3 has **eight per reader**. V2 reader B's 20 corrected-cell units include eight additional shape-only-location joins; its class-metadata count is seven rather than the strict-location count six. [Flag check](reading-flags-2026-10-08-v41.json), group_counts and v2_reader_b_additional_shape_only_units. Frozen payloads and default scores remain unchanged.

The card distinguishes Claude Sonnet in earlier evaluations from Claude Sonnet 5.5 in v3, explains the frames and census/process terms, and includes public chart review priorities. CFF version 0.3.1 validates against the official schema without an alternative-licence list. Licences remain CC BY 4.0 for edition content, CC0 for project additions/data/documentation and Unlicense for code; author alias k-sandhu. [REPORT.md](REPORT.md) gives the results and their limits.

## Repeat from the repository root

Choose unused short names for outputs and caches. The builder reuses local parent files and official licence texts; it repeats no recognition, census query or mass fit. Ordinary builds write their public folder and separate build records. `--update-owner-records` explicitly refreshes the checklist, private-store card and root audit; it is unnecessary for a review rebuild.

```powershell
$releasePython = 'C:\\Users\\sandh\\.venvs\\indus-ml\\Scripts\\python.exe'
$releasePackage = 'experiments/2026-10-08-hf-public-release'
& $releasePython -B "$releasePackage/build_release.py" --out "$releasePackage/check31"
& $releasePython -B "$releasePackage/validate_release.py" --release "$releasePackage/check31" --records "$releasePackage/build-records/check31" --out "$releasePackage/check31-validation.json" --raw-out data/raw/2026-10-08-hf-public-release/check31
& $releasePython -B "$releasePackage/check_prediction_format.py" --release "$releasePackage/check31" --out "$releasePackage/check31-format.json" --raw-out data/raw/2026-10-08-hf-public-release/check31-format
& $releasePython -B "$releasePackage/check_reading_flags.py" --release "$releasePackage/check31" --out "$releasePackage/check31-flags.json"
& $releasePython -B "$releasePackage/check_review_fixes.py" --release "$releasePackage/check31" --out "$releasePackage/check31-rights-cff.json" --raw-out data/raw/2026-10-08-hf-public-release/check31-cff
& $releasePython -B "$releasePackage/compare_release_v031.py" --rebuild "$releasePackage/check31" --out "$releasePackage/check31-preservation.json" --review-out data/raw/2026-10-08-hf-public-release/check31-rebuild-review.json
& $releasePython -B "$releasePackage/rerun_review_v031.py" --out data/raw/2026-10-08-hf-public-release/check31-review
python tools/review_prose.py --path $releasePackage --no-write
```

The reviewer rerun reads the working release folder. Its Hub loader/snapshot calls use local substitutes; it makes no network request. The coordinator's private **0.3.0** preview was verified at commit **541766d5ea8a4c3b3ec5fcc416ee764af8763afb**: 23 configurations, 3,308 rows and 136 matching files. [REVIEW-0.3.0.md](REVIEW-0.3.0.md). Hosted 0.3.1 and the public viewer remain coordinator checks after upload; the private viewer returned HTTP 501.

Reused inputs are chart audit reference/comparison/impact 2.1, original atlas crops, M's three frozen packets/scorers, census consolidation and trimmed registers, independently cited museum supplements, metrology aggregates and protected reviewer scripts. The full reviewed folder and code are preserved in history/. Earlier validations, review/ and review-0.3.0/ remain unchanged. [Changed-path inventory](created-paths-v0.3.1-2026-10-08.json) enumerates every created/changed file. [PROTOCOL.md](PROTOCOL.md), [RETROSPECTIVE.md](RETROSPECTIVE.md), [rights-audit.json](rights-audit.json), build-records/r41/ and [sources.json](sources.json) retain decisions, hashes and access scope. The shared registry is unchanged; [registry-entry.json](registry-entry.json) is the proposal.

The [owner checklist](RELEASE-CHECKLIST.md) retains three decisions: public issues repository, private-store Hub terms and final visibility. No upload, repository creation, visibility change or other package edit occurred. The [private-store card](private-store/README.md) retains recovery instructions.

Reviewers should repeat the 23 loads, 1,142 image checks, three score/interval comparisons, card-only prediction tests, 26 earlier and 16 v3 independent flags, CFF/privacy scans and {files}-file rebuild. Inspect the eight additional v2 reader B joins and chart expert-review priorities. After private upload, repeat hosted loads and snippets; check all image-bearing viewer tables and 23 selectors after approved public visibility.

## Configuration counts

{counts}
'''
    (HERE/'README.md').write_text(root_readme,encoding='utf8')
    report=f'''# Version 0.3.1 findings and validation

All **23 configurations, 3,308 rows and 1,142 images** pass local validation. V1/v2/v3 summaries, row records, bootstrap intervals and recall outputs reproduce the frozen metrics with **zero mismatches** at tolerance 1e-12. A second fresh build matches **{files}/{files} files** and **{size:,} bytes**. [Final validation](validation-2026-10-08-v45.json), configurations, images, benchmark_scores, review_checks and rebuild. Packaging arithmetic has Verified computation status; correction flags remain Exploratory.

## Prediction interface

The scorer accepts the public keys printed_inscription_id and classification_literal and the frozen aliases inscription_number and classification_code. Both fields must be present under either name; null values are accepted. Conflicting aliases or non-string values fail before an output is created. FIELD-DEFINITIONS.md defines the fields alongside unit confidence and section membership. [Public instructions](release/README.md#score-a-new-row-reader); [scorer](release/code/score_benchmark.py), validate_predictions.

Minimal files use only the fields listed in the card, unit confidence and ranked code sets, plus section in v2/v3. Their values come from the frozen predictions. Both key formats preserve the baseline summaries, row records and intervals. The new check runs 27 cases: nine valid files, including nullable values, and eighteen missing/conflicting/type errors. [Format test](prediction-format-2026-10-08-v41.json), documented_row_fields and cases.

| Benchmark | Correct numbers | Correct classifications | Calibration observations |
|---|---:|---:|---:|
| v1 | 23/60 | 19/60 | 140 |
| v2 | 62/80 | 55/80 | 252 |
| v3 | 71/80 | 72/80 | 315 |

The preserved reviewer script also tests both minimal key formats and rejects all eighteen malformed confidence/section/unit/row-count cases. [Reviewer rerun](review-rerun-2026-10-08-v41.json), local_card_snippets.minimal_format and failing_cases. This verifies the documented interface with baseline values; it does not evaluate a new reader.

## Reading flags and frozen evidence

Independent candidate_fields_would_change now uses the chart audit's field-specific mapping rule: join a candidate's explicit location to its original cell membership, derive reviewed labels, and flag a changed resulting set. Missing candidate-cell identities receive warnings. The flags recover **26** definite earlier independent units: v1 A six, v1 B five and v2 A fifteen. V3 derives **eight** for A and **eight** for B; its eight adjudicated flags remain unchanged. [Flag check](reading-flags-2026-10-08-v41.json), group_counts, v3_definite_units and definite_units; [P impact](../2026-10-08-chart-reference-audit/impact-v2.1.json), public_readings.unit_changes.

corrected_cell joins the union of chart_locations, chart_references and shape_only_chart_locations. V2 reader B consequently has **20** changed-cell units against the impact's strict-location **12**, and **seven** class-metadata units against **six**. The eight additional units have explicit shape-only joins; one adds the class change. [Flag check](reading-flags-2026-10-08-v41.json), v2_reader_b_additional_shape_only_units records each sample, unit and cell; [field rules](release/FIELD-DEFINITIONS.md), nested benchmark fields.

All 23 schemas and original table values match reviewed 0.3.0 after excluding only the separate reading flag columns from comparison. The 687-cell chart remains reference 2.1: eight primary codes and two classes corrected, sixteen ambiguities provisionally settled and 33 medium-confidence cells. Benchmark cards, references, predictions and locators keep their original vocabulary. Frozen strict top-five scores remain **24/60, 40/80 and 62/80**; v3 numbered/physical random-page recall remains **1,289/1,289 and 1,296/1,296**. Corrected-label rescoring remains deferred until the 18 v2 and 31 v3 unlocated identities and v3 58:0 locator conflict are reviewed. [Preservation](rebuild-comparison-2026-10-08-v42.json), table_preservation and checks; [metrics](release/benchmark/expected-metrics.json), summary and v3 recall; [chart changes](release/provenance/chart-changes.json), reference_impact and locator_conflicts.

## Public documentation and provenance

The card now puts the three benchmark frames in a table and states AI-reference provenance once. Earlier readers are Claude Sonnet, with the v2 version unrecorded; v3 readers are Claude Sonnet 5.5. It defines CISI, face, provisional family, field-block cue and the disclosed scratch/directory incidents, and gives distinct benchmark, census and metrology component descriptions. The chart review note names expert inspection priorities and publicly available cell/table witnesses. [Card](release/README.md#benchmark-frames-and-reference-provenance); [review priorities](release/docs/CHART-REVIEW.md).

CFF version 0.3.1 validates against the official 1.2.0 schema. It omits license because a list denotes alternative terms; its message directs readers to the per-component LICENSE. Owner decisions remain CC BY 4.0 edition content, CC0 project additions/data/documentation, Unlicense code and author alias k-sandhu. The three official legal texts match their saved witnesses. [CFF and rights check](review-fixes-check-2026-10-08-v41.json), cff and official_license_texts_equal; [citation](release/CITATION.cff); [full owner audit](rights-audit.json).

## Rights, privacy and reproducibility

The reviewer rerun completes **{script_count} scripts**, with a fifteenth protected script comparing the rebuild. Outputs and scratch locations are redirected without editing the scripts; Hub loading/snippets use local substitutes. The image audit finds all 1,142 parent hashes. The whole-sequence screen tests **149 complete singleton rows** (43 v1, 62 v2 and 44 v3) against **6,878 directional sequences**; zero match. The earlier forward index has **3,506** sequences. The six-derivative run screen detects all 200 plain and 200 ambiguous planted controls and finds zero graphic-code runs. Its twelve generic integer hits are preserved agreed-unit position lists. [Reviewer rerun](review-rerun-2026-10-08-v41.json), checks, images, sequence_scan and sequence_dispositions; [base screen](validation-2026-10-08-v41.json), sequence_screen.

Prose comparisons leave zero unexplained third-party passages after location/witness review. Exact bibliography and official legal text are permitted; other matches are project readings, process notes and independently supported identifier citations. The strict privacy scan has zero hits. The broad reviewer scan additionally matches authorized public account names, a generic directory phrase in frozen reader metadata and the access label Research/archive pages; their dispositions are recorded. These screens cover saved witnesses and numbering. [Reviewer rerun](review-rerun-2026-10-08-v41.json), prose and privacy.

The release stores 1,067 PNGs embedded and 75 loose, totaling {files} files. Its rebuilt bytes are identical and the reviewed 0.3.0 archive and {rebuild['protected_reviewer_files']} reviewer files retain their hashes. All earlier validation files remain unchanged. [Rebuild comparison](rebuild-comparison-2026-10-08-v42.json), checks and rebuild; [changed-path inventory](created-paths-v0.3.1-2026-10-08.json).

## Hosted status and remaining decisions

The 0.3.0 review verifies private Hub commit 541766d5ea8a4c3b3ec5fcc416ee764af8763afb: 23 configurations, 3,308 rows and 136 files equal to the earlier local folder. This revision makes no Hub call. Hosted 0.3.1 remains a coordinator check after upload; the public viewer remains unchecked after the private server returned HTTP 501. Expert epigraphic review is pending. [REVIEW-0.3.0.md](REVIEW-0.3.0.md), Hosted loading and Method and scope; [owner checklist](RELEASE-CHECKLIST.md) retains the issues repository, private-store terms and final visibility decisions. No upload, repository creation, visibility change or other package edit occurred.
'''
    (HERE/'REPORT.md').write_text(report,encoding='utf8')
    retro=HERE/'RETROSPECTIVE.md';text=retro.read_text(encoding='utf8')
    if '\n\n## 8 October 2026: version 0.3.1' in text:text=text.split('\n\n## 8 October 2026: version 0.3.1')[0]
    text=text.replace('Final records are validation-2026-10-08-v34.json and rebuild-comparison-2026-10-08-v33.json.','Those interim records are validation-2026-10-08-v34.json and rebuild-comparison-2026-10-08-v33.json; the later final 0.3.0 summary is v38 with rebuild v37.')
    text=text.replace('Hosted 0.3.0 checks and three owner decisions remain outside this local package.','At that handoff, hosted 0.3.0 checks were pending. The subsequent REVIEW-0.3.0.md verifies the private preview; three owner decisions remain open.')
    text+=f'''\n\n## 8 October 2026: version 0.3.1\n\nThe private-preview review confirmed the chart, frozen content, images and scores, then reproduced a silent interface mismatch: predictions using the card's key names scored zero numbers and classifications. The scorer now normalizes the card keys to the original internal aliases and rejects absent/conflicting/type-invalid values. Twenty-seven new format cases pass; minimal files using either pair reproduce 23/19, 62/55 and 71/72 correct numbers/classifications with zero metric mismatches.\n\nThe independent-reading flag builder had left definite candidate-field changes empty. Field-specific cell joins recover P's 26 earlier independent units and derive eight for each v3 reader. The wider corrected_cell union was retained and documented: v2 reader B includes eight shape-only units beyond the strict-location impact, with one additional class change. Frozen payloads and scores stay unchanged.\n\nCFF's licence list was removed because its schema gives alternatives; the per-component terms remain in LICENSE and the citation message. Model attribution now follows the recorded precision. The card uses a frame table, shared reference-provenance note, defined census/process terms and public expert-review priorities. The builder refreshes owner files only with an explicit flag, so an ordinary reproducibility run preserves later owner edits.\n\nThe first scripted documentation replacement stopped on an inherited field-definition phrase that lives in a separate module. Moving that replacement into field rendering fixed it before building. One exploratory inspection command also failed under Windows native quoting; subsequent helpers were run from files. Neither attempt changed a frozen file or output. The protocol now distinguishes the original 0.3.0 plan record from retrospective repairs without inferring its original timing; the new plan has a UTC record and preserved text.\n\nThe final checks load 23 configurations (3,308 rows), verify 1,142 images and reproduce all three metrics. The protected reviewer scripts were reused with redirected outputs and local Hub substitutes. A fresh build matches {files}/{files} files ({size:,} bytes); privacy and unexplained third-party prose/graphic runs are clear. Final records are validation-2026-10-08-v45.json, review-rerun-2026-10-08-v41.json and rebuild-comparison-2026-10-08-v42.json. Reviewed 0.3.0 files, code and prior validations remain preserved.\n\nHosted 0.3.0 is now verified through the review. The coordinator still needs to upload and check 0.3.1 privately, and the owner retains issues-repository, private-store-terms and visibility decisions. Public viewer checks follow approved visibility; private datasets-server returned 501. This revision performed no external write.\n'''
    retro.write_text(text,encoding='utf8')
    protocol=HERE/'PROTOCOL.md';snapshot=HERE/'history/2026-10-08-protocol-plan-v031.md'
    if not snapshot.exists():shutil.copyfile(protocol,snapshot)
    text=protocol.read_text(encoding='utf8')
    heading='### Version 0.3.0 amendment: 8 October 2026, before the new build'
    if heading not in text:heading='### Version 0.3.0 amendment: 8 October 2026, plan and repair record'
    begin=text.index(heading);end=text.index('### Version 0.3.1 amendment:',begin)
    section=text[begin:end].replace(heading,'### Version 0.3.0 amendment: 8 October 2026, plan and repair record')
    paragraphs=section.split('\n\n')
    for i,paragraph in enumerate(paragraphs):
        if not paragraph.strip() or paragraph.startswith(('###','**8 October 2026;')):continue
        kind='post-build repair, recorded retrospectively' if paragraph.startswith(('The first build attempts','Final prose inspection')) else 'planned work; original timing unverified'
        paragraphs[i]='**8 October 2026; '+kind+'.** '+paragraph
    text=text[:begin]+'\n\n'.join(paragraphs)+text[end:]
    begin=text.index('### Version 0.3.1 amendment:');paragraphs=text[begin:].split('\n\n')
    for i,paragraph in enumerate(paragraphs):
        if paragraph.strip() and not paragraph.startswith(('###','**8 October 2026;')):paragraphs[i]='**8 October 2026; 0.3.1 plan.** '+paragraph
    text=text[:begin]+'\n\n'.join(paragraphs)
    protocol.write_text(text,encoding='utf8')
    sources=read(HERE/'sources.json');sources['release_review_0_3_1']=dict(title='Review of public release 0.3.0',authors=['Claude Sonnet reviewer'],year=2026,venue='Private project review',url=None,opened=True,search_snippet_only=False,exact_location='REVIEW-0.3.0.md; review-0.3.0/ scripts and JSON; new redirected reruns in data/raw/2026-10-08-hf-public-release/rr41',failed_searches=[],failed_downloads=[],access_scope='Read full local review and reuse scripts; no new literature acquisition or Hub call.')
    dump(HERE/'sources.json',sources)
    prefix='experiments/2026-10-08-hf-public-release/'
    registry=read(HERE/'registry-entry.json');registry.update(status='Verified computation',outcome=f'0.3.1: 23 configurations, 3308 rows, 1142 parent-matching PNGs, {files} files/{size} bytes. All three frozen scores match; {files}/{files} rebuild files match. Card-only number/classification counts 23/19, 62/55, 71/72; 27 new format cases pass. Independent flags recover 26 earlier units and 16 v3 units; zero strict privacy hits.',challenge='Public prediction keys differed from scorer aliases; independent flags omitted definite changes and used a broader location union than the impact summary. AI references lack expert review; mapped identities and three owner decisions remain open.',remedy='Accept canonical public keys and frozen aliases, reject missing/conflicting/type-invalid values, fill field-specific candidate flags and document the eight extra shape-only joins. Preserve every frozen payload and reviewer file. Correct CFF/model attribution, clarify public documentation and reproduce a byte-identical rebuild.',evidence=[prefix+x for x in ['REPORT.md','PROTOCOL.md','validation-2026-10-08-v45.json','prediction-format-2026-10-08-v41.json','reading-flags-2026-10-08-v41.json','review-rerun-2026-10-08-v41.json','rebuild-comparison-2026-10-08-v42.json','rights-audit.json','RELEASE-CHECKLIST.md']],retry_when='Coordinator uploads and checks 0.3.1 privately; owner confirms issues, private-store terms and final visibility. Check public viewer after approval. Mapped scoring requires reviewed candidate identities and separately frozen expectations.')
    dump(HERE/'registry-entry.json',registry)
    print('Owner-facing 0.3.1 reports written')

if __name__=='__main__':main()
