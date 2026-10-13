"""Assign every file in the final inventory to one publication decision and write the decision record.

Rules are checked in order and the first match wins; a file matching no rule stops the build.
Evidence for each rule is summed from the three scan outputs over the files the rule received.
"""
from pathlib import Path
from collections import defaultdict
from fnmatch import fnmatchcase
import json

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
RAW = ROOT / 'data/raw/2026-10-13-publication-screen'
E = 'experiments/'
SHOT = E + '2026-10-12-conjecture-shots/'
CLAIMS = E + '2026-10-12-published-claim-tests/'
SAT = E + '2026-10-12-satellite-prospection/'
ANCHOR = E + '2026-10-12-anchor-expansion/'

CONDITION_NOTICES = ('THIRD_PARTY_NOTICES.md and knowledge/DATA.md section 7 describe twenty published Lipi windows; '
                     'update them to cover these 44 examples and keep them outside the CC0 dedication that REUSE.md '
                     'now applies to project material.')

RULES = [
    # Keep local.
    ([CLAIMS + 'allographs/run-2026-10-12/pairs_k1.csv', CLAIMS + 'allographs/run-2026-10-12/pairs_k3.csv',
      CLAIMS + 'allographs/run-2026-10-12/pairs_k5.csv'], 'keep-local',
     'Each row gives a sign pair with its root and letter value in the key from the Lipi repository (xlits.csv, '
     'yajnadevam/lipi commit fc8813a5). Together the rows reproduce that unlicensed key for 440 of its 681 lettered '
     'signs in pairs_k1.csv (roots agree for 412, letter values for 311); pairs_k3 and pairs_k5 are subsets. The '
     'tracked summary.json, verification.json and REPORT.md carry the aggregate results. REPORT.md links the three '
     'tables, so they join the public omission list.', None),
    # Track after an edit.
    ([E + '2026-10-12-seal-text-identity/review/REVIEW.md'], 'track-after-edit',
     'Line 32 gives a complete four-sign Lipi text with its CISI number (L-161). The October 11 rule allows complete '
     'texts of at most three signs. Replace the parenthesized four-code string after "for a four-sign text" with '
     '"(four signs; codes in the local Lipi record for CISI L-161)" and append "Publication note, 13 October 2026: one code sequence was replaced by a pointer; the '
     'original review is preserved locally." The original bytes are backed up under '
     'data/raw/2026-10-13-publication-screen/originals/.', None),
    # Track, with file-level evidence worth recording.
    ([E + '2026-10-12-structure-first/step3-segmentation/run-alternation-2026-10-12/summary.json'], 'track',
     'Frequency table of the commonest segmented units with their counts. One four-code unit that recurs 15 to 18 '
     'times also equals a complete Lipi text; it is reported as a recurrent formula count, not as a record, and the '
     'file holds no record identifiers.', None),
    ([ANCHOR + 'run-v*/example-provenance.json', ANCHOR + 'run-v*/catalogue-data.json'], 'track',
     'Per-code aggregates, Monier-Williams sense paraphrases with entry and line pointers (the October 11 practice) '
     'and 36 attributed Lipi examples per run, each a complete text or excerpt of two or three codes with CISI '
     'number, pin and stated purpose. Across both runs there are 44 distinct examples, 42 of them not among the '
     'twenty published on October 11. No embedded images.', CONDITION_NOTICES),
    ([ANCHOR + 'context/*summary.json', ANCHOR + 'context/run-v*/summary.json', ANCHOR + 'context/quantity-sensitivity-v1/summary.json'], 'track',
     'Per-code and per-family aggregate counts (positions, role scores, co-occurrence and substitution counts). '
     'The 38.2 MB files are below the GitHub 50 MB warning; context/summary.json and context/run-v2/summary.json are '
     'byte-identical and share one Git blob. The eight anchor-expansion files over 5 MB compress to about 5 MB in '
     'total. They are frozen endpoints computed from the local Lipi export and cannot be regenerated from a public '
     'checkout.', None),
    ([CLAIMS + 'sanskrit-key/stage4/demo.json'], 'track',
     'Twelve demonstration rows carry 115 first-gloss fragments (78 distinct, at most 60 characters each) copied from '
     'the Cologne digital Monier-Williams (csl-orig), which is licensed CC BY-SA 4.0 (licence witness '
     'data/raw/2026-10-08-bonta-review/acquisition-2026-10-08-v1/csl-LICENSE).',
     'Record the CC BY-SA 4.0 attribution and share-alike scope for these fragments in THIRD_PARTY_NOTICES.md and '
     'exclude them from the CC0 dedication in REUSE.md.'),
    ([CLAIMS + 'sanskrit-key/stage3f/summary.json'], 'track',
     'Lists twenty frequent signs with their letter in the published key under test: a bounded illustration of the '
     'claim, alongside aggregate fit statistics.',
     'These twenty Lipi key entries are source material under unresolved terms; keep them outside the CC0 '
     'dedication alongside the catalogue examples.'),
    ([SAT + 'atlas/vendor/**', SAT + 'atlas/viewer-v1/vendor/**', SAT + 'atlas/viewer-v1/geography-data.js'], 'track',
     'Leaflet 1.9.4 (BSD-2-Clause, LICENSE included) and Natural Earth 1:110m (public domain, NOTICE and acquisition '
     'record included). The only embedded images are Leaflet\'s own icons inside leaflet.js.', None),
    ([SAT + '*.geojson', SAT + '*/*.geojson', SAT + 'atlas/viewer-v1/atlas-data.*', SAT + 'atlas/viewer-v1/input-export.json',
      SAT + 'exports*/atlas-data-v*.json'], 'track',
     'Coordinates of screened spectral and terrain anomalies (30 m stated uncertainty), two reconnaissance prospects '
     'near Ganweriwala and eighteen published reference locations of known sites. Geometry is derived from '
     'Copernicus Sentinel-2, Copernicus GLO-30 and ESA WorldCover (CC BY 4.0) with notices in the package; no '
     'imagery is embedded. The package does not discuss whether precise candidate locations should be public.',
     'Owner decision: publish candidate coordinates at 30 m precision, or coarsen or withhold them. If tracked, '
     'REUSE.md should exclude the Copernicus and ESA WorldCover derivatives from the CC0 dedication and point to '
     'the package THIRD-PARTY-NOTICES.md.'),
    ([E + '2026-10-12-bronze-age-comparison/acquisition/*'], 'track',
     'Access logs (URL, status, byte count, SHA-256, local path, rights status "local-only") for ORACC, AES, AED-TEI, '
     'LiBER and DAMOS requests. Each is byte-identical to the request record in the local raw directory; no response '
     'content is included.', None),
    ([E + '2026-10-11-settlement-prospection/review/claude-opus55-v*/cli-*'], 'track',
     'Claude CLI result records: model, usage, cost, session and message UUIDs and the review text. No account '
     'identifiers or tokens; the stderr files are empty.', None),
    (['data/MANIFEST.json'], 'track',
     'Project-authored source manifest. The pending .gitignore exception admits it, but tools/audit_git_payload.py '
     'still treats every data/ path except data/README.md as a violation and currently reports review-required.',
     'Update the forbidden-path rule in tools/audit_git_payload.py (and any clean-history verifier reused for this '
     'push) to allow data/MANIFEST.json.'),
    (['tools/build_site.py', 'site/**', E + '2026-10-13-site-generator/**'], 'track',
     'Static website generator, templates and its test record. No credentials; committer addresses are placeholders '
     '(a users.noreply.github.com bot name and example.invalid). The --publish command writes a local gh-pages '
     'branch and does not push or add a workflow.',
     'Owner or coordinator decision: whether a gh-pages publishing command fits the AGENTS.md rule against '
     'deployment scaffolding.'),
    (['.github/ISSUE_TEMPLATE/*'], 'track', 'Issue forms only; no .github/workflows directory exists.', None),
    (['.claude/skills/**'], 'track', 'Project skill instructions. The adjacent .claude/worktrees holds two Git '
     'worktrees and is excluded only by the local .git/info/exclude.', None),
    (['output/pdf/*'], 'track', 'The settlement working paper (33 pages, ReportLab) embeds four images, all the '
     'project\'s own charts and editorial-rectangle maps; its .gitignore exception is in the pending change. The '
     'layout JSON belongs to the Sanskrit-key paper.', None),
    # Package-level groups.
    ([E + '2026-10-11-early-indian-continuity/**'], 'track', 'Authored protocols, reports, retention grids and '
     'checks; downloaded texts and renders stay in the local raw directory. baseline-v1.json is a workspace hash '
     'inventory (paths, sizes, hashes).', None),
    ([E + '2026-10-11-settlement-prospection/**'], 'track', 'Authored prose, registers, own figures and editorial '
     'maps with no basemap, review packets of our manuscript and registers; acquired witnesses stay local as the '
     'package ASSET-REVIEW.md records.', None),
    ([E + '2026-10-11-societal-persistence/**'], 'track', 'Authored observations with locators and inference '
     'limits, synthetic worlds, checks and source records; downloads stay local.', None),
    ([E + '2026-10-11-two-approaches/**'], 'track', 'Aggregates and synthetic checks. The frame audit hashes its '
     'anchor sequences; prototype lists contain only two-sign texts.', None),
    ([ANCHOR + '**'], 'track', 'Family ledgers, sense pointers, review records and verification; no sequence '
     'windows longer than three codes and no images.', None),
    ([E + '2026-10-12-bronze-age-comparison/**'], 'track', 'Protocols, aggregate category and structural results and '
     'census manifests whose examples are identifiers, URLs, counts and dates. Edition texts (ORACC, AES, AED-TEI, '
     'LiBER) stay local.', None),
    ([CLAIMS + '**'], 'track', 'Protocols, aggregate results, figures generated from those results and source '
     'records. Quoted wording is short and cited.', None),
    ([SAT + '**'], 'track', 'Code, protocols, review records, layout manifests and notices; raster windows and '
     'rendered panels are ignored by extension rules and stay local.', None),
    ([E + '2026-10-12-seal-text-identity/**'], 'track', 'Authored report and review record; no other sequence of '
     'four or more codes.', None),
    ([E + '2026-10-12-semantic-sign-comparison/**'], 'track', 'The project\'s own sign inventory and family '
     'crosswalk (three identical runs share one blob); acquired pages and token extracts stay local.', None),
    ([E + '2026-10-12-structure-first/**'], 'track', 'Aggregate outputs and short examples; sequences, glyph sheets '
     'and the map output stay local as the package states.', None),
    ([E + '2026-10-12-transmission-hypothesis/**'], 'track', 'Authored readings of textual and material sources '
     'with loci; source passages stay in local paired witnesses.', None),
    ([SHOT + '**'], 'track', 'Discovery and confirmation outputs are per-sign and per-unit aggregates; the split '
     'list and full legends stay local as the package states. Proximity matches are dictionary keys, not '
     'sequences.', None),
    ([E + '2026-10-12-data-inventory/**'], 'track', 'Counts and acquisition priorities; the full file list and '
     'harvested index stay local.', None),
    ([E + '2026-10-12-repo-restructure/**'], 'track', 'Restructure prompt, launcher and verification records. '
     'They contain the local Windows path with the user name, as do 89 files already published.', None),
    ([E + '2026-10-13-plate-checks/**'], 'track', 'Authored visual descriptions of CISI and Lipi photographs, '
     'image file names and hashes; no images, crops or code sequences. Transcribed basic-data rows stay local.', None),
    (['knowledge/**'], 'track', 'Cards, memos, registry entries and retrospectives. Conjecture cards cite '
     'two-sign phrases and short bibliographic titles.', None),
    (['papers/**'], 'track', 'Manuscripts, methods and the paper renderer.', None),
    (['CLAUDE.md', 'templates/*', 'tools/kb.py', 'tools/fetch_data.py'], 'track', 'Navigation and tooling.', None),
    (['.gitignore'], 'track', 'Pending change adds exceptions for the settlement figures, viewers, packets and PDF, '
     'data/MANIFEST.json and an /_site/ exclusion; it removes no existing exclusion.', None),
    (['AGENTS.md', 'CONTRIBUTING.md', 'README.md', 'knowledge/INDEX.md', 'knowledge/editorial/WRITING.md',
      'knowledge/experiments/README.md', 'knowledge/experiments/registry.json', 'knowledge/provenance/git-payload-review.json',
      'knowledge/provenance/SOURCES.md', 'knowledge/retrospectives/README.md', 'templates/EXPERIMENT.md',
      'tools/register_experiment.py'], 'track', 'Modified navigation, registry and tooling; no sequence, key, '
     'credential or address matches. git-payload-review.json records the data/MANIFEST.json violation above.', None),
]


def load(name):
    return json.loads((HERE / name).read_text(encoding='utf-8'))


def main():
    inv = json.loads((RAW / 'inventory-final.json').read_text(encoding='utf-8'))
    seq = {r['path']: r for r in load('sequence-scan.json')['files']}
    key = {r['path']: r for r in load('lipi-key-scan.json')['files']}
    pay = {r['path']: r for r in load('payload-scan.json')['files']}
    assigned = defaultdict(list)
    unmatched = []
    for f in inv['files']:
        for i, (patterns, *_rest) in enumerate(RULES):
            if any(fnmatchcase(f['path'], p) for p in patterns):
                assigned[i].append(f)
                break
        else:
            unmatched.append(f['path'])
    if unmatched:
        raise SystemExit('Unclassified files: ' + json.dumps(unmatched[:20]))
    decisions = []
    for i, (patterns, decision, reason, condition) in enumerate(RULES):
        files = assigned.get(i, [])
        if not files:
            continue
        ev = {'files': len(files), 'bytes': sum(f['bytes'] or 0 for f in files),
              'lipi_4code_windows_strict': sum(seq.get(f['path'], {}).get('strict', {}).get('matched_windows', 0) for f in files),
              'lipi_full_texts_ge4_strict': sum(seq.get(f['path'], {}).get('strict', {}).get('distinct_full_texts', 0) for f in files),
              'proximity_only_windows': sum(seq.get(f['path'], {}).get('stream', {}).get('matched_windows', 0) for f in files),
              'max_distinct_short_texts_in_a_file': max([seq.get(f['path'], {}).get('short_complete_texts', {}).get('distinct', 0) for f in files] or [0]),
              'lipi_key_pairs_max_in_a_file': max([key.get(f['path'], {}).get('distinct_key_pairs', 0) for f in files] or [0]),
              'credential_pattern_files': sum(1 for f in files if 'credential_patterns' in pay.get(f['path'], {})),
              'email_files': sum(1 for f in files if 'emails_masked' in pay.get(f['path'], {})),
              'owner_address_files': sum(1 for f in files if pay.get(f['path'], {}).get('owner_address_or_local_part_present')),
              'long_quote_candidate_files': sum(1 for f in files if 'long_quote_candidates' in pay.get(f['path'], {})),
              'largest_file_bytes': max(f['bytes'] or 0 for f in files),
              'files_over_50MB': sum(1 for f in files if (f['bytes'] or 0) > 50 * 2**20)}
        entry = {'id': f'D{i + 1:02d}', 'decision': decision,
                 'path' if len(files) == 1 and len(patterns) == 1 and '*' not in patterns[0] else 'glob': patterns if len(patterns) > 1 else patterns[0],
                 'reason': reason, 'evidence': {k: v for k, v in ev.items() if v or k in ('files', 'bytes')}}
        if condition:
            entry['condition'] = condition
        if decision != 'track' or len(files) <= 3:
            entry['matched_paths'] = [f['path'] for f in files]
        decisions.append(entry)
    totals = defaultdict(lambda: {'files': 0, 'bytes': 0})
    for d in decisions:
        totals[d['decision']]['files'] += d['evidence']['files']
        totals[d['decision']]['bytes'] += d['evidence']['bytes']
    record = {'inventory': {'path': 'data/raw/2026-10-13-publication-screen/inventory-final.json', 'frozen_at_utc': inv['frozen_at_utc'],
                            'head': inv['head'], 'untracked_files': inv['untracked_files'],
                            'modified_tracked_files': inv['modified_tracked_files'], 'bytes': inv['bytes']},
              'scans': ['sequence-scan.json', 'lipi-key-scan.json', 'payload-scan.json'],
              'rule': 'First matching entry wins; every inventoried file matched exactly one entry.',
              'decisions': decisions}
    (HERE / 'decisions.json').write_text(json.dumps(record, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
    keep = [p for d in decisions if d['decision'] == 'keep-local' for p in d['matched_paths']]
    edit = [p for d in decisions if d['decision'] == 'track-after-edit' for p in d['matched_paths']]
    conditions = [{'id': d['id'], 'condition': d['condition']} for d in decisions if 'condition' in d]
    summary = {'inventory': record['inventory'], 'per_decision': dict(totals),
               'distinct_blob_bytes': sum(f['bytes'] for f in {f['sha256']: f for f in inv['files'] if f['sha256']}.values()),
               'keep_local': keep, 'track_after_edit': edit, 'conditions': conditions,
               'outside_scope_findings': [
                   'Five files already published at HEAD (experiments/2026-10-08-hf-public-release privacy scanners and '
                   'check_review_fixes.py, including two history copies) contain the local part of the owner\'s personal '
                   'address next to the word gmail inside regular expressions; the full address does not appear.']}
    (HERE / 'summary.json').write_text(json.dumps(summary, indent=1) + '\n', encoding='utf-8')
    print(json.dumps({'per_decision': dict(totals), 'entries': len(decisions), 'keep_local': keep, 'track_after_edit': edit}, indent=1))


if __name__ == '__main__':
    main()
