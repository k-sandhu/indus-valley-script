"""Write the review note and final message from the checked tables."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from identity_io import ROOT, OUT, LOCAL, read_csv, write_json, sha


def run():
    summary = json.loads((OUT / 'match-summary.json').read_text(encoding='utf-8'))
    test = json.loads((OUT / 'selftest-3.json').read_text(encoding='utf-8'))
    assert test['passed']
    counts = summary['counts_by_site']
    total = counts[-1]
    rows = read_csv(OUT / 'objects-merged.csv')[1]
    moved = set(summary['newly_in_baseline_catalogue'])
    unlisted_total = sum(summary['local_unlisted_by_site'].values())
    same_part = read_csv(OUT / 'same-part-duplicates.csv')[1]
    reviews = read_csv(OUT / 'containment-review.csv')[1]
    summary['script_hashes'] = {p.relative_to(ROOT).as_posix(): sha(p) for p in sorted(OUT.glob('*.py'))}
    summary['coverage_change'] = {
        'new_source_assets': 0, 'corpus_records_changed': 0,
        'source_register_rows_combined': summary['source_register_rows'],
        'new_proposal_columns': ['provisional_row_id', 'cisi_in_baseline', 'local_match',
                                 'local_family_ids', 'match_basis', 'match_evidence'],
        'proposals_reviewed_by_coordinator': False}
    write_json(OUT / 'match-summary.json', summary)
    methods = """We preserve each of the 490 extraction rows and its provisional identifier. Final identifiers follow the site seed order, followed by new named sites in regional part order. Within a site, primary publication source identifiers sort first and extraction order breaks ties. Existing duplicate references point to the final identifiers. Shared registrations are flagged without combining rows.

The source register combines the two acquisition CSV registers, all five coordinator manifest records and both regional source supplements. Later nonempty values fill or update earlier values. The variants table preserves disagreements and their input paths. All primary locators, secondary-publication locators and regional merge-log locators use this combined register. Numeric PDF locators are checked against the supplied page extent where one is recorded. Printed locators are recorded without opening source pages.

The corpus pin is checked before matching. A selective JSON reader skips every unselected value without deserializing it. Its only retained top-level and metadata keys are listed in identity_io.py and in the local audit file. We group faces by object_family_id and map sites through the seed aliases. The named sites in the regional site notes are retained even when they have no rows. The regional summary labelled Other Pakistani sites has no individual site identity and is omitted from site totals.

Registrations are upper-cased, separated into letter and numeric parts, stripped of leading zeroes in each numeric part, joined without punctuation, and stripped of a leading site prefix. We test raw equality, normalised equality, a leading registration with an appended suffix, and a maximal long numeric item with the same preceding registration context. The known project label is allowed before a complete registration. Each successful comparison records its rule. A shared publication plate or figure citation can use the allowed excavation identifier field. We use no other corpus fields to seek such a citation.

For catalogue containment, we compare each eligible site's row registration with both the raw excavation cell and the parsed printed excavation items. Source qualifiers in parentheses are removed. A doubtful character prevents an automatic equality decision. Near comparisons leave the status unchanged and produce a review row containing the extraction registration, the CISI identifier and the comparison rule. No basic-data cell value is copied into the outputs. Publication citations of numbers in the CISI 3 absent-number list also establish catalogue containment.

A unique identifier join requires a compatible type and no comparable context conflict on any local face. Missing fields leave the comparison open. Named trench, grid and area tokens support findspot comparisons. Numeric period or phase labels permit Arabic and Roman equivalents and a broad period containing a named subperiod. We compare numeric depth ranges only when both sides state the same unit. Material is recorded as supporting evidence and does not exclude a family. Each row's evidence records the compared field names and agreement states without copying local context values.

We reserve identifier joins and identified baseline audit families before forming candidate sets. A row may reuse an assigned family only when the pair has a duplicate flag. A row with a differing usable registration excludes that family. Context-only similarity does not establish a match. The museum join table's three specified Dholavira absence records are checked separately; only registration 22198 occurs in these extraction tables, and its existing absence decision is retained as evidence.

The main count columns use stated post-catalogue rows. Uncertain-status rows, baseline audit rows and possible CISI 3 rows are separate. The upper absence bound is the eligible row count less matched rows. The lower bound is absent rows plus the excess of candidate rows over unassigned candidate families, computed separately at each site. These are the requested row bounds while duplicate flags await review. Best publication follows the protocol's source ranking among primary publications represented in the eligible rows; publication_basis lists every contributing primary publication and its row count.

Local-unlisted is the complement of every family named by any row, including direct catalogue identities on baseline audit rows. Repeated faces are combined within a family. Nine context cells have restricted unit expressions withheld to satisfy the output scan; their family and field identifiers are recorded in match-summary.json. The full source records remain in place. No source assets were acquired and no corpus record was changed.

Run from the repository root with Python 3.13, in this order:

    python -I -B experiments/2026-10-21-post-catalogue-finds/matching/run3.py
    python -I -B experiments/2026-10-21-post-catalogue-finds/matching/selftest_3.py
    python -I -B experiments/2026-10-21-post-catalogue-finds/matching/finish_3.py
    python -I -B experiments/2026-10-21-post-catalogue-finds/matching/selftest_3.py

The last check includes the generated prose in its content scan. The independent recount checks row coverage, family identity, reservations, counts, bounds, input hashes and source-register coverage. Source-page verification and coordinator decisions remain the next review steps.
"""
    (OUT / 'METHODS.md').write_text(methods, encoding='utf-8')
    retro = {
        'authors': ['OpenAI GPT-6, Codex desktop API harness, run 3'],
        'approach': 'Standard-library scripts merged the frozen extraction tables, projected allowed corpus fields, compared registrations and context, and recounted eligible rows independently.',
        'challenges': [
            'Parsed excavation entries in the basic-data files are dictionaries, not strings.',
            'Some local identifiers carry site prefixes, project labels or appended catalogue numbers.',
            'Some source records supply no PDF page extent.',
            'The output rule also catches unit expressions in allowed depth fields.',
            'The first independent recount accidentally treated empty reservation entries as assigned families.'
        ],
        'fixes': [
            'Used the parsed printed excavation item alongside the raw cell, retaining only the CISI identifier in containment outputs.',
            'Recorded separate equality and containment rules and left context conflicts open for review.',
            'Marked unavailable extents in the locator audit.',
            'Repaired the preview filter and scanned every owned text file; withheld restricted expressions in nine unlisted context cells.',
            'Corrected the recount to count only reservation entries with actual row users; all checks then passed.'
        ],
        'outcome': {'merged_rows': len(rows), 'eligible_rows': total['rows_total'],
                    'matched': total['matched'], 'candidate': total['candidate'], 'absent': total['absent'],
                    'absent_bounds': [total['absent_lower_bound'], total['absent_upper_bound']],
                    'local_unlisted': unlisted_total},
        'deviations': [
            'An early tool preview contained depth-unit expressions from allowed context fields before the filter repair. No such expression is retained in the deliverables.',
            'Added a same-part duplicate table for three shared-registration pairs so the coordinator can review them alongside the requested cross-part table.',
            'Included named zero-row sites from the supplied seed and site notes so their unlisted local families remain visible.'
        ],
        'source_pages_read': 0, 'page_images_opened': 0,
        'writes': ['experiments/2026-10-21-post-catalogue-finds/matching/',
                   'data/raw/2026-10-21-post-catalogue-finds/run3/'],
        'next_review': 'Review all candidates, all joins beyond raw equality, absence proposals at sites with local families, the duplicate flags and the two containment comparisons.'}
    write_json(OUT / 'retrospective-3.json', retro)
    lines = [f"We merged {len(rows)} rows. The main count includes {total['rows_total']} stated post-catalogue rows: {total['matched']} matched, {total['candidate']} candidate and {total['absent']} absent, with absence bounds {total['absent_lower_bound']}–{total['absent_upper_bound']}. The other rows comprise {total['rows_uncertain_status']} uncertain-status rows, {total['rows_in_baseline_catalogue']} baseline audit rows and {total['rows_possibly_in_cisi3']} possible CISI 3 row.",
             '', 'All rows includes the audit and uncertain rows. Eligible, matched, candidate, absent and bounds use the main count. Unlisted counts local families named by no row.', '',
             '| Site | All rows | Eligible | Matched | Candidate | Absent | Absent bounds | Unlisted |',
             '|---|---:|---:|---:|---:|---:|---:|---:|']
    for row in counts[:-1]:
        site = row['site']
        lines.append(f"| {site} | {summary['counts_by_site_all_rows'][site]['rows']} | {row['rows_total']} | {row['matched']} | {row['candidate']} | {row['absent']} | {row['absent_lower_bound']}–{row['absent_upper_bound']} | {summary['local_unlisted_by_site'][site]} |")
    lines += [f"| TOTAL | {len(rows)} | {total['rows_total']} | {total['matched']} | {total['candidate']} | {total['absent']} | {total['absent_lower_bound']}–{total['absent_upper_bound']} | {unlisted_total} |", '']
    moved_text = '; '.join(f"{r['row_id']} ({r['site']}; {r['cisi_in_baseline']})" for r in rows if r['row_id'] in moved)
    lines += [f"Catalogue containment moved {len(moved)} row to in-baseline-catalogue: {moved_text}. The combined source register contains {summary['source_register_rows']} source IDs.", '',
              f"There are {summary['cross_part_duplicate_pairs']} cross-part duplicate pairs. The three same-part pairs are " +
              '; '.join(f"{r['row_id_a']} / {r['row_id_b']}" for r in same_part) + '.', '',
              'The two containment reviews are ' + '; '.join(f"{r['row_id']} / {r['cisi']}" for r in reviews) + '. Both retain their prior catalogue status.', '',
              f"Selftest: {test['checks_passed']}/{test['checks_total']} checks passed. Corpus SHA256: {summary['corpus_sha256']}.", '',
              'The locator audit checks every cited source against the combined register. Supplied PDF extents are unavailable for some sources; those checks are labelled in locator-checks.csv. We opened no source page or page image.', '',
              'The run added the same-part duplicate audit and retained named zero-row sites. An early tool preview missed the depth-unit filter; the filter was repaired, and the deliverables pass the full content scan. Nine unlisted context cells have restricted expressions withheld. Duplicate flags and all join proposals await coordinator review.', '',
              'Outputs are in experiments/2026-10-21-post-catalogue-finds/matching/: objects-merged.csv, site-counts.csv, cross-part-duplicates.csv, containment-review.csv, local-unlisted.csv, source-register.csv, match-summary.json, selftest-3.json and the scripts. METHODS.md, retrospective-3.json, locator-checks.csv, same-part-duplicates.csv, identifier-collisions.csv and source-register-variants.csv record the method and review details. The local audit is data/raw/2026-10-21-post-catalogue-finds/run3/identity-run-audit.json. This message is saved as matching/final.md.', '']
    (OUT / 'final.md').write_text('\n'.join(lines), encoding='utf-8')
    print(json.dumps({'final_rows': len(counts)-1, 'unlisted': unlisted_total,
                      'report': (OUT / 'final.md').relative_to(ROOT).as_posix()}))


if __name__ == '__main__':
    run()
