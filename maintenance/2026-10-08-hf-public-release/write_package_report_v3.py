"""Write the 0.3.0 package reports from dated checks; no public upload."""
from build_release import HERE,ROOT,read,dump


def main():
    base=read(HERE/'validation-2026-10-08-v36.json')
    replay=read(HERE/'rebuild-comparison-2026-10-08-v37.json')
    rebuilt=read(HERE/'rebuild-validation-2026-10-08-v37.json')
    final_path=HERE/'validation-2026-10-08-v38.json'
    if final_path.exists():raise FileExistsError('Preserve the final dated validation.')
    final=dict(base,release_version='0.3.0',release_folder='experiments/2026-10-08-hf-public-release/release',
        build_records='experiments/2026-10-08-hf-public-release/build-records/r35',
        rebuild_validation='rebuild-validation-2026-10-08-v37.json',rebuild_comparison='rebuild-comparison-2026-10-08-v37.json',
        rebuild_checks=replay['checks'],rebuild=replay['rebuild'],chart_unit_flags=replay['details'],
        previous_public_preview=dict(version='0.2.0',configurations=19,rows=2720,images_decode=True,evidence='Coordinator report; no Hub calls by Package O.'))
    if replay['status']!='Verified computation' or rebuilt['status']!='Verified computation':final['status']='Failed'
    dump(final_path,final)
    tables=read(HERE/'release/provenance/table-manifest.json')
    overview='| Configuration | Rows |\n|---|---:|\n'+''.join(f"| `{n}` | {s['rows']} |\n" for n,s in tables.items())
    size=final['release_bytes'];files=final['release_files']
    readme=f'''# Package O: release version 0.3.0

The [release folder](release/README.md) contains **23 configurations, 3,308 rows and 1,142 images**. It adopts P's corrected chart reference 2.1 and adds the third frozen 80-row benchmark. Every local load, schema, source field and image check passes; v1/v2/v3 scoring has **zero mismatches**. [Final validation](validation-2026-10-08-v38.json), configurations, source_checks, images and benchmark_scores.

The chart has **687 cells, eight primary-code corrections, two class corrections and 16 provisionally settled ambiguities**. Previous-value fields document 36 changed numeric records; 33 cells have medium confidence. It remains Exploratory: two AI readings and a pixel check, no expert review. Benchmark payloads retain their earlier card labels. Separate unit flags preserve 11/0/8 direct candidate changes, 0/18/31 identity warnings and the v3 locator conflict. Corrected-label rescoring is deferred under [P's recommendation](../2026-10-08-chart-reference-audit/RECOMMENDED-USE.md).

Frozen strict top-five scores remain **24/60, 40/80 and 62/80**. V3 random-page physical-line recall is **1,296/1,296**; numbered recall is **1,289/1,289**. Both repair pipelines fail four of five criteria against AI references. The full transcription remains quarantined. [REPORT.md](REPORT.md) gives the frames, provenance and sensitivity.

The folder has **{files} files and {size:,} bytes**, with 1,067 embedded PNGs and 75 loose PNGs. A fresh build matches **136/136 files byte for byte**. Privacy has zero hits. Rights screening finds zero graphic-code runs; twelve generic hits are agreed-unit index lists. [Reviewer rerun](review-rerun-2026-10-08-v35.json) and [rebuild comparison](rebuild-comparison-2026-10-08-v37.json).

## Repeat from the repository root

Use fresh short names. The builder reuses local parent files and official licence texts; it runs no recognition or Hub query. Validation uses datasets, PyArrow, NumPy, Pillow, PyYAML and jsonschema from the existing indus-ml environment.

```powershell
$releasePython = 'C:\\Users\\sandh\\.venvs\\indus-ml\\Scripts\\python.exe'
$releasePackage = 'experiments/2026-10-08-hf-public-release'
& $releasePython -B "$releasePackage/build_release.py" --out "$releasePackage/check30"
& $releasePython -B "$releasePackage/validate_release.py" --release "$releasePackage/check30" --records "$releasePackage/build-records/check30" --out "$releasePackage/check30-validation.json" --raw-out data/raw/2026-10-08-hf-public-release/check30
& $releasePython -B "$releasePackage/check_review_fixes.py" --release "$releasePackage/check30" --out "$releasePackage/check30-input-check.json" --raw-out data/raw/2026-10-08-hf-public-release/check30-input
& $releasePython -B "$releasePackage/rerun_review.py" --release "$releasePackage/check30" --records "$releasePackage/build-records/check30" --out data/raw/2026-10-08-hf-public-release/check30-review
& $releasePython -B "$releasePackage/record_release_v3.py" --rebuild "$releasePackage/check30" --out "$releasePackage/check30-preservation.json"
python tools/review_prose.py --path $releasePackage --no-write
```

Reused inputs are P's current reference/comparison/impact, original atlas cells, M's frozen packets/crops/predictions/scorers, census synthesis v6 and trimmed registers, the independently cited museum supplement and reviewed metrology tables. No recognition, census query or mass fit was repeated. The standalone scorer uses only uploaded tables and NumPy/PyArrow; hosted examples are in the card.

The 0.2.0 folder and code are preserved in history/. Earlier validation files and review/ scripts are unchanged. [Changed-path inventory](created-paths-v0.3.0-2026-10-08-v2.json) enumerates new/changed files and preserved folders. [PROTOCOL.md](PROTOCOL.md), [RETROSPECTIVE.md](RETROSPECTIVE.md), [rights-audit.json](rights-audit.json), build-records/r35/ and [sources.json](sources.json) retain decisions, pins and access scope. The shared registry was not edited; [registry-entry.json](registry-entry.json) is the integration proposal.

Owner licences remain CC0 for project data/documentation/additions, Unlicense for code and CC BY 4.0 for edition content, with k-sandhu authorship. [Owner checklist](RELEASE-CHECKLIST.md) retains the issues repository, private-store Hub terms and final visibility decisions. The coordinator reports all 19 configurations and images loading for private 0.2.0. Hosted 0.3.0 checks follow its update; no upload occurred here. [Private-store card](private-store/README.md) retains restore and remote-verification instructions.

Repeat all 23 loads, three score/interval comparisons, 1,142 image hashes, correction joins, eight failing prediction cases, CFF/privacy checks and the 136-file rebuild. Sample medium chart cells and AI-reference disclosures. After updating the private preview, check v3 viewer images and the owner-selected issues link.

## Configuration counts

{overview}
'''
    (HERE/'README.md').write_text(readme,encoding='utf8')
    report=f'''# Version 0.3.0 findings and validation

All **23 configurations and 3,308 rows** load locally, and every one of **1,142 PNGs** matches its parent. The scorer reproduces all three frozen endpoints with zero numerical or structural differences at tolerance 1e-12, including v3 numbered and physical-line recall. [Final validation](validation-2026-10-08-v38.json), configurations, images, source_checks and benchmark_scores. Status: Verified computation for packaging and arithmetic; chart annotations and later interpretation remain Exploratory.

## Chart changes and preserved vocabulary

The chart uses [P's current reference 2.1](../2026-10-08-chart-reference-audit/chart-reference-v2.1.json). Eight primary codes and two upper classes change, and 16 earlier lower-code ambiguities are provisionally settled. Thirty-six records change numeric fields; 33 cells have medium and 654 high qualitative confidence. The second AI reader inspected 63 cells blind and checked the whole chart with pixels. It did not independently eye-read every cell, and no expert reviewed the labels. [Chart provenance](release/provenance/chart-changes.json), comparison_summary and changes; [chart table](release/data/chart_reference.parquet), previous_* and change_note.

Every earlier v1/v2 reference, prediction and locator field is preserved after resolving portable provenance labels back to its witness. The 91-file 0.2.0 archive retains its hashes. V3 uses M's frozen predictions and adjudicated reference without label remapping. [Rebuild comparison](rebuild-comparison-2026-10-08-v37.json), checks.v1_frozen_payloads_preserved, checks.v2_frozen_payloads_preserved and checks.v0_2_0_archive_preserved.

Unit flags match P's sample/unit joins. Direct candidate changes occur in 11/0/8 reference units in v1/v2/v3; unlocated affected identities occur in 0/18/31. Linked changed records, including class/confidence updates, touch 23/12/21 units. V3 preserves one locator conflict, 58:0. [Rebuild comparison](rebuild-comparison-2026-10-08-v37.json), details.*_chart_flags; [P impact](../2026-10-08-chart-reference-audit/impact-v2.1.json), M_references and M_v3_reported_location_conflicts. P asks for identity review before a mapped sensitivity; this release defers it and retains the original benchmark cards. The corrected chart is a separate vocabulary version.

## Frozen frames and AI-reference provenance

V1 evaluates 60 numbered-section occurrences on PDF 31–79 from 3,460 detections. V2 evaluates 80 numbered/end-sorted/beginning-sorted rows, 28/26/26, from pools 3,596/3,228/3,496. V3 evaluates 80 fresh rows with those quotas from pools 572/2,004/2,004 on 8/28/28 eligible pages, excluding previous target pages and ten development pages. These are separate samples; their differences do not estimate a paired repair effect. [Public card](release/README.md), Benchmark frames and reference provenance; [v3 selection](release/benchmark/v3-selection.json), denominators, eligible_pages and excluded_pages.

Two Claude Sonnet 5.5 readers and a Claude adjudicator produced the repair references from shared conventions/cards, with no human check. V3 readers agree on 80/80 numbers, classifications, counts and line memberships and 357/369 strict unit sets. Count references use pixel scripts with the field-block cue also used by the pipeline and a line-pitch cross-check. Row intervals do not capture page clustering; v3's numbered stratum spans eight pages. [M review](../2026-10-07-helsinki1979-digitization/REVIEW-V3.md), M3–M4; [reader metadata](release/benchmark/reader-metadata.json); [v3 notes](release/benchmark/v3-adjudication-notes.json), agreement_summary and counts_comparison.

| Frozen outcome | v1 | v2 | v3 |
|---|---:|---:|---:|
| Crops | 23/60 | 44/80 | 71/80 |
| Counts | 33/60 | 59/80 | 72/80 |
| Numbers | 23/60 | 62/80 | 71/80 |
| Classifications | 19/60 | 55/80 | 72/80 |
| Strict top one | 13/60 | 20/80 | 38/80 |
| Strict top five | 24/60 | 40/80 | 62/80 |
| Aligned strict top-five units | 224/267 | 304/352 | 338/366 |

[Expected metrics](release/benchmark/expected-metrics.json), v1/v2/v3.summary. V3 numbered random-page recall is 1,289/1,289 and physical-line recall 1,296/1,296; both stress-page recalls are 561/561. The 21 pages total 1,850 numbered occurrences and 1,857 physical lines. The 18 random pages are fresh relative to earlier count pages; eight carried earlier recognition targets. Stress pages are reused. [Expected metrics](release/benchmark/expected-metrics.json), v3.source_row_recall and physical_line_recall; [count table](release/data/benchmark_count_pages_v3.parquet), reference_json.

V3 falls short of crop/number/count/top-five thresholds 72/72/76/64 by 1/1/4/2 rows. Only ≥95% random-page numbered recall passes. Strict top five is 62/80; its fully resolved subset is 62/77 and shape-only is 65/80. Accepting code 23 for strict units 35:2 and 70:4 gives 64/80 in the separate Exploratory sensitivity; count and number still fail. [Sensitivity](release/benchmark/v3-reading-choice-sensitivity.json), altered_units and summary; [independent check](rebuild-comparison-2026-10-08-v37.json), checks.reading_choice_sensitivity. Full-edition proposals remain excluded.

## Rights, privacy and replay

The owner's licence/author decisions remain: CC BY 4.0 edition content, CC0 project additions/data/documentation, Unlicense code and k-sandhu without affiliation. Official licence texts match their preserved downloads; CFF validates against the official 1.2.0 schema. The museum table retains 49 independent identifier pairs and excludes 19 Lipi-only joins. [Checks](review-fixes-check-2026-10-08-v35.json), cff and official_license_texts_equal; [full owner audit](rights-audit.json); [public exclusions](release/EXCLUSIONS.md).

The whole-sequence screen tests **149 singleton reference rows with at least two units**, including 105 older and 44 v3 rows, against 6,878 sequences in both directions; zero match. The earlier basis has 3,506 distinct forward sequences. The six-derivative scan finds zero graphic-code runs of at least three positions. Twelve generic integer hits are agreed-unit index lists in six v3 records, repeated in the reference/adjudication tables. All 200 plain and 200 ambiguous planted controls are detected. Available-witness prose screens leave zero unexplained third-party matches. [Final validation](validation-2026-10-08-v38.json), sequence_screen and review_checks; [review disposition](review-rerun-2026-10-08-v35.json), sequence_dispositions and prose. The screens cover saved sources/numbering; recoded copying and unsaved prose are outside their reach.

Privacy has zero hits. Eight malformed v2/v3 prediction files fail loudly; two passing files have zero mismatches, finite intervals and calibration counts 252/315. All ten applicable reviewer scripts complete and retain their original hashes. Raw image materialization supports legacy checks; rights/privacy scans read the actual release. [Input checks](review-fixes-check-2026-10-08-v35.json), privacy and prediction_cases; [review rerun](review-rerun-2026-10-08-v35.json), checks and adaptations.

The release has **136 files, {size:,} bytes, 1,067 embedded and 75 loose PNGs**. A fresh build matches **136/136 files**, including manifests. [Fresh validation](rebuild-validation-2026-10-08-v37.json); [comparison](rebuild-comparison-2026-10-08-v37.json), rebuild. Owner records, full audits and raw overlap witnesses remain outside the upload folder.

Hosted 0.3.0 loading awaits the coordinator's private-preview update. The coordinator reports all 19 configurations/images loading for 0.2.0. The issues repository, private-store Hub terms and final visibility remain decisions in [RELEASE-CHECKLIST.md](RELEASE-CHECKLIST.md). No upload, repository creation or visibility change occurred.
'''
    (HERE/'REPORT.md').write_text(report,encoding='utf8')
    if '## 8 October 2026: version 0.3.0' not in (HERE/'RETROSPECTIVE.md').read_text(encoding='utf8'):
        with (HERE/'RETROSPECTIVE.md').open('a',encoding='utf8') as stream:
            stream.write('''
    ## 8 October 2026: version 0.3.0

    P's recommendation named reference v2.1, superseding the v2 snapshot in the coordinator's first summary. The build reused that reference/comparison/impact, original atlas images, M's v3 packet/predictions/evaluator and earlier census/metrology inputs. Separate flags show differences from the preserved benchmark vocabulary. Candidate-identity warnings prevented complete corrected-label rescoring, which remains deferred under P's recommendation. The separate reading-choice sensitivity recomputes as 64/80.

    Two partial builds failed on an overly broad edit adding unit flags to page readings and missing output directories. A completed first build passed all three score checks, but privacy found a bare excluded-directory phrase in v3 process notes. The input-format checker also used the v2 fixture for v3. Fixes narrowed the page schema, created directories, made excluded paths portable and selected the fixture by version. A copied v1 card numerator was corrected to its frozen 224/267. Partial/intermediate builds and the failed check remain preserved in raw history and dated reports; no frozen source endpoint changed.

    All 23 final configurations load (3,308 rows), all 1,142 images match parents and all three metrics reproduce. Eight malformed input cases fail; two passing cases reproduce calibration and finite intervals. The original sequence scanner also tests arbitrary integer lists: twelve new hits were agreement.strict_codes_agreed_units, containing zero-based positions. Exact locators and dispositions are recorded; every graphic-code run screen stayed clear. Prose overlaps belonged to project readings, bibliography and official licence text. Reviewer scripts stayed unchanged. A fresh build is byte-identical across 136 files, and the prior 91-file release is preserved. Final records are validation-2026-10-08-v38.json and rebuild-comparison-2026-10-08-v37.json.

    The coordinator's successful 0.2.0 preview is recorded as supplied evidence. This revision made no Hub call. Hosted 0.3.0 checks and three owner decisions remain outside this local package. Future mapped scoring needs reviewed candidate-cell identities, a declared chart vocabulary and separately frozen expectations.
    ''')
    prefix='experiments/2026-10-08-hf-public-release/'
    dump(HERE/'registry-entry.json',dict(id='O-2026-10-08-HF-PUBLIC-RELEASE',theme='licensed research data release',status='Verified computation',
        question='Can the licensed chart, three frozen benchmarks and authored census/aggregate tables form a reproducible public dataset?',
        outcome=f'0.3.0: 23 configs,3308 rows,1142 parent-matching PNGs,136 files/{size} bytes; all loads/schemas/three scores match,136/136 rebuild files equal,zero privacy hits. Chart:8 codes,2 classes corrected,16 ambiguities provisionally settled,33 medium confidence. Frozen top-five24/60,40/80,62/80;v3 numbered/physical recall1289/1289 and1296/1296 against AI reference. Full transcription excluded.',
        challenge='Chart and frozen benchmark labels differ;18 v2/31 v3 units need candidate-identity review and one v3 locator conflicts. AI references/shared count cues lack expert review. Issues,private-store terms and visibility remain open.',
        remedy='Preserved old payloads/cards/scores and0.2.0;added chart previous fields,unit-impact flags,v3 images/readings/geometry,exact scorer replay,rights/privacy/CFF checks and byte-identical rebuild. Corrected-label rescoring deferred;reading-choice sensitivity Exploratory.',
        evidence=[prefix+p for p in ['REPORT.md','PROTOCOL.md','validation-2026-10-08-v38.json','rebuild-comparison-2026-10-08-v37.json','review-rerun-2026-10-08-v35.json','rights-audit.json','release/provenance/chart-changes.json','release/benchmark/expected-metrics.json','RELEASE-CHECKLIST.md']],
        retry_when='After reviewed identities/labels, freeze separate mapped expectations; update private preview and complete owner issues/terms/visibility decisions before public release.'))
    dump(HERE/'build-attempts-v0.3.0-2026-10-08-v2.json',dict(date='2026-10-08',attempts=[
        dict(build='r30',outcome='Failed',error='NameError: kind is not defined in count-reading constructor; overly broad edit.'),
        dict(build='r31',outcome='Failed',error='FileNotFoundError writing code/score_recall_v3.py before making its directory.'),
        dict(build='r32',outcome='Exploratory',arithmetic='All three scores matched.',issues=['Bare local-directory phrase.','v3 test used v2 fixture.','Card v1 recall numerator.']),
        dict(build='r35',outcome='Verified computation',current_folder='release'),dict(build='r36',outcome='Verified computation',matching_files=136)],
        intermediate_builds='data/raw/2026-10-08-hf-public-release/v0.3.0-build-history/',new_downloads=0,new_searches=0))
    print(final['status'],size,files)

if __name__=='__main__':main()
