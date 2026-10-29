"""Recorded one-time documentation source amendment for version 0.3.0."""
from pathlib import Path
from amend_release_v3 import replace
HERE=Path(__file__).resolve().parent

def main():
    p=HERE/'write_release_docs.py';text=p.read_text(encoding='utf8')
    text=text.replace('0.2.0','0.3.0')
    text=replace(text,"    card=f'''", "    total_rows=sum(s['rows'] for s in tables.values())\n    card=f'''")
    text=replace(text,'two frozen row-reading benchmarks of 60 and 80 rows','three frozen row-reading benchmarks of 60, 80 and 80 rows')
    text=replace(text,'Its 19 Parquet configurations contain 2,720 rows','Its {len(tables)} Parquet configurations contain {total_rows:,} rows')
    text=replace(text,'and v2 `context_image` and `exact_image`','and v2/v3 `context_image` and `exact_image`')
    start=text.index('`chart_reference` combines');end=text.index('The census selects',start)
    text=text[:start]+'''`chart_reference` uses reviewed numeric reference version 2.1 and the original 687 atlas crops from PDF pages 20–21. Eight primary codes and two upper classes were corrected; all 16 earlier lower-code ambiguities are provisionally settled. Thirty-six records change numeric fields, including confidence: 33 cells are medium and 654 high on an uncalibrated qualitative scale. Previous-value columns and `change_note` record each change. Status: **Exploratory, two AI readings and a pixel check, no expert review**. The second reader read 63 cells blind, followed by a whole-chart pixel sweep; it did not independently eye-read every cell. Crops may include neighbouring ink. [Chart changes](provenance/chart-changes.json) preserves the exact field deltas and consumer impact.

The row-reading task gives a system row context, a proposed target box and chart cards. It returns the printed inscription number, its five-position classification and a visual left-to-right sequence of units, each with ranked graphic-code candidate sets. The frozen baseline is a chart-only template matcher. Inventory codes are edition labels.

### Benchmark frames and reference provenance

v1 contains 60 numbered-section occurrences from 3,460 detections on PDF pages 31–79. Three AI readers supplied disjoint initial groups; six convenience repeat readings are separate records. v2 contains 80 targets across `number_order`, `end_sorted` and `beginning_sorted`, with quotas 28/26/26 and eligible pools 3,596/3,228/3,496; it excludes development pages and v1 targets. v3 contains 80 fresh targets with the same quotas from pools 572/2,004/2,004 on 8/28/28 eligible pages. It excludes every page carrying a v1 or v2 target and the ten original development pages. The 80 v2 targets were used for v3 development and are excluded from the v3 test. These frames differ; the reported changes are comparisons across samples, rather than paired repair effects or edition-wide rates.

Two Claude Sonnet 5.5 readers and a Claude adjudicator produced each repair reference from shared conventions and chart cards, with no human check. The v3 readers agree on all 80 numbers, classifications, counts and line memberships, and on 357/369 strict unit sets. Count-page readings use pixel scripts with the field-block cue also used by the pipeline and a printed-line-pitch cross-check; recall measures agreement with this reference. Shared scratch collisions and directory observations in v2 and declared directory exposure in v3 are retained in [reader metadata](benchmark/reader-metadata.json) and adjudication notes. Wilson intervals and section-stratified row bootstraps do not cluster by source page; v3's 28 numbered rows span only eight pages.

An **exposed OCR locator** means the original v1 locator contained OCR strings before the blinding correction, affecting 22/60 targets. The **eleven-code overlay** records eleven later source-based corrections, is Exploratory, and preserves the frozen v1 endpoint. A **compatible whole row** has nonempty strict reference sets at every unit and zero candidate-set edit distance to the prediction, with intersections at each aligned position. **Aligned unit recall** maximizes matching intersections among minimum-edit alignments and divides by resolved reference units.

| Frozen outcome | v1, 60 rows | v2, 80 rows | v3, 80 fresh rows |
|---|---:|---:|---:|
| Accepted crop | 23/60 | 44/80 | 71/80 |
| Unit count agreement | 33/60 | 59/80 | 72/80 |
| Literal inscription number | 23/60 | 62/80 | 71/80 |
| Five-position classification | 19/60 | 55/80 | 72/80 |
| Strict top-one whole row | 13/60 | 20/80 | 38/80 |
| Strict top-five whole row | 24/60 | 40/80 | 62/80 |
| Aligned strict top-five units | 233/267 | 304/352 | 338/366 |
| Random-page numbered recall | Not evaluated | 1,242/1,286 | 1,289/1,289 |

The five v2/v3 pass criteria are crop correctness ≥90% (72/80), inscription-number accuracy ≥90% (72/80), unit-count agreement ≥95% (76/80), strict top-five whole rows ≥80% (64/80), and random-page numbered recall ≥95%. Both fail four of five criteria; only numbered recall passes. V1 reports the first four thresholds on 60 rows and fails all four. The full provisional transcription remains excluded.

V3 physical-line recall includes continuation lines and is a separate completeness measure: 1,296/1,296 random-page lines, against 1,289 numbered occurrences. Numbered and physical stress-page recall are both 561/561. Its 18 random count pages are fresh against earlier count pages; eight carried earlier recognition targets. Stress pages 62, 129 and 130 are reused. [Expected metrics](benchmark/expected-metrics.json) contains all three frozen row records, intervals, criteria and repair recall outputs.

V3 strict top five is 62/80 (77.5%; Wilson 95% 67.2–85.3%). Restricting the denominator to fully resolved references gives 62/77. The frozen shape-only score is 65/80 (81.3%; 71.3–88.3%). An Exploratory reading-choice sensitivity accepting {{23}} at 35:2 and 70:4 gives 64/80 and reaches the top-five threshold; count and number still fail. [Sensitivity](benchmark/v3-reading-choice-sensitivity.json) records the modified units separately.

### Chart-label vocabulary

All benchmark cards, references and predictions retain their original card labels, including earlier chart errors. Frozen scores therefore reproduce that historical vocabulary; `chart_reference` uses corrected version 2.1. Separate per-unit flag columns identify changed cells, affected prediction alternatives, possible candidate identities and the v3 58:0 locator conflict. An identifiable cell can have a class/confidence update without a code change. [Chart changes](provenance/chart-changes.json) records 11/0/8 directly changed reference units in v1/v2/v3, and 0/18/31 units needing candidate-identity review. A corrected-label rescoring is deferred until those identities and the locator conflict are reviewed; replacing numbers globally would conflate different drawings.

The [v2 reading convention](benchmark/CONVENTIONS.md) and [v3 convention](benchmark/CONVENTIONS-v3.md) describe independent reading before predictions were opened. Their `position-chart/` means that version's rows in `benchmark_chart_cards`; `page-count-source/` means the page PNGs in `benchmark_count_pages` or `benchmark_count_pages_v3`. The original `predictions.json` is represented by `prediction_json`; `frame.json` was the full detector frame and is excluded. Row locators and the v3 selection retain the benchmark geometry and sampling frame.

'''+text[end:]
    text=text.replace('v2 requires `section`','v2 and v3 require `section`').replace('missing/invalid v2 section','missing/invalid v2/v3 section').replace('v2 source-row recall','v2/v3 source-row recall')
    text=text.replace('The 105 complete singleton benchmark reference rows','The original v1/v2 screen tested 105 complete singleton benchmark reference rows')
    text=text.replace('; none equalled a whole indexed sequence in either direction.', '; none equalled a whole indexed sequence in either direction. Version 0.3.0 extends the screen to v3; its counts and any independently sourced overlap are recorded in the validation record.')
    # Supply every new outer schema definition and keep common constraints together.
    text=replace(text,"    fields='''# Field definitions", """    d.update(reference_version='Reviewed chart numeric-reference version; 2.1 in this release.',
        previous_code='Original chart code when changed, otherwise null.',previous_rank='Original upper class when changed, otherwise null.',
        previous_alternatives='Original lower-code alternatives when changed; an empty list differs from null.',
        previous_rank_alternatives='Original upper-class alternatives when changed, otherwise null.',
        previous_numeric_confidence='Original qualitative confidence when changed, otherwise null.',
        changed_fields='Names of changed numeric fields relative to the original reference.',change_note='Short old-to-new numeric change description; null when unchanged.',
        chart_correction_flags_json='Per-unit chart-change flags for this reading, separate from the frozen reading JSON.',
        reference_chart_correction_flags_json='Per-reference-unit flags from the chart impact: corrected cells, field changes, candidate-identity warnings and locator conflict.',
        prediction_chart_correction_flags_json='Per-predicted-unit flags for alternatives whose template_key points to a changed chart cell.')
    fields='''# Field definitions""")
    text=text.replace('PNG in v2, exposed','PNG in v2/v3, exposed').replace("if name=='benchmark_count_pages'", "if name.startswith('benchmark_count_pages')")
    text=text.replace('false detection in v2.','false detection in v2/v3.').replace('v2 section supplies','v2/v3 section supplies')
    text=replace(text,'Reader metadata retains process disclosures,', 'V3 numbered recall uses the numbered anchor, while physical-line recall uses glyph-box centers and includes continuations. Per-unit correction flags never change frozen codes: corrected_cell identifies a linked changed record; candidate_identity_review flags possible unlocated identities; locator_conflict retains conflicting witnesses. Reader metadata retains process disclosures,')
    text=text.replace('Unresolved labels and editorial markers are retained.', 'Version 0.3.0 adopts reviewed chart labels and previous-value columns, retains the original frozen benchmark card vocabulary and editorial markers, and adds a third frozen evaluation and per-unit chart-impact flags.')
    text=replace(text,'Future verified rows require a separate addition.', 'Only the 60/80/80 frozen evaluation subsets are included. Future verified full-corpus rows require a separate addition. Corrected-label rescoring awaits candidate identity and locator review.')
    text=text.replace('No upload, repository creation or visibility change was performed.', 'The coordinator uploaded version 0.2.0 privately and reports all 19 configurations (2,720 rows) and images loading. Package O performs no upload, repository creation or visibility change.')
    text=replace(text,'api.create_repo(repo_id, repo_type="dataset", private=True, exist_ok=False)', '# The private preview repository already exists; inspect it before updating.')
    text=text.replace('Prepare reference benchmarks for private owner review','Update reference benchmarks to 0.3.0 for private owner review')
    start=text.index('If that ID exists, inspect');end=text.index('After owner approval',start)
    text=text[:start]+'''The existing private preview holds 0.2.0. Record the updated uploaded commit, download that private revision, compare every file against provenance/file-manifest.json and repeat loading/scoring. Inspect all configurations, including v3 and the corrected chart, and embedded images. Confirm the issues URL and CFF citation while still private. Hosted 0.3.0 checks remain for the coordinator after this local handoff.

'''+text[end:]
    p.write_text(text,encoding='utf8')

if __name__=='__main__':main()
