"""Exploratory response to REVIEW.md. Run from the repository root with Python -B.

Reuses the review's independently written form, dictionary and shuffle definitions.
All per-object and per-assignment derivatives stay in the package's local raw tree.
No frozen or reviewer output is changed. Both output directories must be new.
"""
from pathlib import Path
import argparse, collections, hashlib, itertools, json, random, re, sys
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OWN = Path(__file__).resolve().parent
RAW = ROOT / 'data/raw/2026-10-08-bonta-review'

def read(p):
    return json.loads(p.read_text(encoding='utf-8'))

def write(p, x):
    p.write_text(json.dumps(x, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def forms(mapping, sequence):
    choices = []
    for i, role in enumerate(sequence):
        values = mapping[role]
        if i:
            values = [v for v in values if not v.lower().startswith('maha')]
        choices.append(values)
    return {''.join(p) for p in itertools.product(*choices)}

def summarize(scores, observed):
    tail = sum(s >= observed for s in scores)
    return {'observed': observed, 'assignments': len(scores),
            'histogram': dict(sorted(collections.Counter(scores).items())),
            'permutation_mean': sum(scores) / len(scores),
            'assignments_at_least_observed': tail, 'tail_fraction': tail / len(scores)}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-root', default=str(OWN / 'response-2026-10-08-v2'))
    parser.add_argument('--raw-output-root', default=str(RAW / 'response-2026-10-08-v2'))
    args = parser.parse_args()
    out, rawout = Path(args.output_root).resolve(), Path(args.raw_output_root).resolve()
    if not out.is_relative_to(OWN) or not rawout.is_relative_to(RAW):
        parser.error('outputs must stay in the owned and local raw directories')
    if out.is_relative_to(OWN / 'review') or out.is_relative_to(OWN / 'history'):
        parser.error('reviewer files and historical snapshots are read-only')
    if out.exists() or rawout.exists():
        parser.error('refusing to overwrite an existing output directory')
    inputs = [OWN / 'PROTOCOL.md', OWN / 'PROTOCOL-registered.md', OWN / 'selection.json',
              OWN / 'validation-audit.json', OWN / 'review/review_checks.py',
              OWN / 'review/review-checks.json', OWN / 'review/role-pair-census.json',
              RAW / 'acquisition-2026-10-08-v1/mw.txt', RAW / 'papers/page-segments.json',
              ROOT / 'data/normalized/lipi_clean_rtl_singleline.jsonl',
              ROOT / 'data/normalized/lipi_observed_faces.jsonl']
    protected = [OWN / 'REVIEW.md', OWN / 'selection.json', OWN / 'PROTOCOL-registered.md',
                 OWN / 'analyze-v1-frozen.py', OWN / 'analyze.py', OWN / 'validation-audit.json']
    for folder in ('review', 'run-2026-10-08-v1', 'run-replay-2026-10-08-01'):
        protected.extend(p for p in (OWN / folder).rglob('*') if p.is_file())
    out.mkdir(parents=True)
    rawout.mkdir(parents=True)
    write(out / 'manifest.json', {'status': 'Exploratory', 'amendment_date': '2026-10-08',
          'python': sys.version, 'numpy': np.__version__,
          'inputs': [{'path': p.relative_to(ROOT).as_posix(), 'sha256': digest(p)} for p in inputs],
          'protected_files': [{'path': p.relative_to(ROOT).as_posix(), 'sha256': digest(p)} for p in sorted(set(protected))],
          'method_reuse': 'review/review_checks.py: forms, k1 screen, normalization and fish shuffle; review/role-pair-census.json: conditioning evidence',
          'raw_output_root': rawout.relative_to(ROOT).as_posix()})

    selection = read(OWN / 'selection.json')
    vals, panel = selection['values_slp1'], selection['panel']
    roles = list(vals)
    heads = set()
    with (RAW / 'acquisition-2026-10-08-v1/mw.txt').open(encoding='utf-8') as f:
        for line in f:
            i = line.find('<k1>')
            if i >= 0:
                h = line[i + 4:line.find('<', i + 4)]
                if re.fullmatch('[A-Za-z]+', h):
                    heads.add(h)
    groups = ['aA', 'iI', 'uU', 'fF', 'xX', 'kKgG', 'cCjJ', 'wWqQ', 'tTdD', 'pPbB', 'sSz', 'nR']
    normalmap = {c: g[0] for g in groups for c in g}
    remaining = [p for p in panel if not {'PU', 'PATI'}.intersection(p['roles'])]
    assignments = list(itertools.permutations(roles))
    fixed = []
    anchors = ['MA', 'TRA', 'PALA', 'DHANA']
    for perm in itertools.permutations(anchors):
        a = roles.copy()
        for first, second in zip(anchors, perm):
            a[roles.index(first)] = second
        fixed.append(tuple(a))
    lex = {'status': 'Exploratory', 'test_id': 'L1-R', 'panel_size': len(panel),
           'strings_containing_PU_or_PATI': len(panel) - len(remaining),
           'drop_dictionary_derived_strings_retained_ids': [p['id'] for p in remaining],
           'drop_dictionary_derived_strings_removed_ids': [p['id'] for p in panel if p not in remaining],
           'normalization_broader_than_Table18_role_lists': True,
           'development_sources': ['B24 segments 69–75', 'L07 0:05:28–0:11:34'],
           'dictionary_alphabetic_headwords': len(heads), 'endpoints': {}}
    local_assignments = []
    for label, cmap in [('exact', {}), ('normalized', normalmap)]:
        normalize = lambda s: ''.join(cmap.get(c, c) for c in s)
        headclasses = {normalize(h) for h in heads}
        def score(assignment, strings):
            mapping = {r: vals[a] for r, a in zip(roles, assignment)}
            return sum(any(normalize(v) in headclasses for v in forms(mapping, p['roles'])) for p in strings)
        scores = {a: score(a, panel) for a in assignments}
        observed = scores[tuple(roles)]
        kept = [s for a, s in scores.items() if a[roles.index('PU')] == 'PU']
        moved = [s for a, s in scores.items() if a[roles.index('PU')] != 'PU']
        lex['endpoints'][label] = {
            'whole_panel': summarize(list(scores.values()), observed),
            'PU_held_fixed': summarize(kept, observed),
            'PU_moved': summarize(moved, observed),
            'PU_and_PATI_held_fixed': summarize([scores[a] for a in fixed], observed),
            'PU_and_PATI_strings_dropped_four_roles_permuted': summarize([score(a, remaining) for a in fixed], score(tuple(roles), remaining))}
        local_assignments.extend({'endpoint': label, 'assignment': dict(zip(roles, a)), 'whole_panel_score': scores[a],
                                  'dropped_panel_score': score(a, remaining)} for a in assignments)
    write(rawout / 'lexical-permutations.json', local_assignments)
    write(out / 'lexical-sensitivities.json', lex)

    rows = [json.loads(l) for l in (ROOT / 'data/normalized/lipi_clean_rtl_singleline.jsonl').read_text(encoding='utf-8').splitlines()]
    best = {}
    for r in rows:
        key = (-len(r['signs_reading_rtl']), r['record_id'])
        if r['object_family_id'] not in best or key < best[r['object_family_id']][0]:
            best[r['object_family_id']] = key, r
    selected = [r for _, r in best.values()]
    sequences = [r['signs_reading_rtl'] for r in selected]
    distribution = {'status': 'Exploratory', 'test_id': 'D1-R', 'objects': len(selected),
                    'tokens': sum(map(len, sequences)), 'signs': {}}
    exceptions = []
    for code in ('740', '520'):
        total = sum(s.count(code) for s in sequences)
        final = sum(s[-1] == code for s in sequences)
        following, sites = collections.Counter(), collections.Counter()
        object_count = 0
        for r in selected:
            s = r['signs_reading_rtl']
            positions = [i for i, c in enumerate(s[:-1]) if c == code]
            if positions:
                object_count += 1
                sites[r['site']] += 1
                following.update(s[i + 1] for i in positions)
                exceptions.append({'sign': code, 'record_id': r['record_id'], 'object_family_id': r['object_family_id'],
                                   'CISI': r['source_cisi'], 'site': r['site'], 'nonfinal_positions': positions,
                                   'following_codes': [s[i + 1] for i in positions]})
        distribution['signs'][code] = {'tokens': total, 'final_tokens': final, 'nonfinal_tokens': total - final,
            'nonfinal_fraction': (total - final) / total, 'objects_with_nonfinal': object_count,
            'objects_with_nonfinal_by_site': dict(sites.most_common()), 'following_sign_counts': dict(following.most_common()),
            'nonfinal_followed_by_400_or_090': following['400'] + following['090']}
    write(rawout / 'terminal-exceptions.json', exceptions)
    write(out / 'terminal-exceptions.json', distribution)

    fish = set(selection['fish_proxy_wells'])
    def runs(s):
        result, current = [], []
        for c in s + ['#']:
            if c in fish:
                current.append(c)
            elif current:
                result.append(current)
                current = []
        return result
    def adjacent(ss):
        return sum(a in fish and b in fish for s in ss for a, b in zip(s, s[1:]))
    multi = [s for s in sequences if sum(c in fish for c in s) >= 2]
    rng = random.Random(20261009)
    repeat_null, adjacency_null = [], []
    for _ in range(2000):
        shuffled = []
        for s in multi:
            t = s.copy()
            rng.shuffle(t)
            shuffled.append(t)
        repeat_null.append(sum(len(set(r)) < len(r) for s in shuffled for r in runs(s)))
        adjacency_null.append(adjacent(shuffled))
    allrows = [json.loads(l) for l in (ROOT / 'data/normalized/lipi_observed_faces.jsonl').read_text(encoding='utf-8').splitlines()]
    observed = adjacent(multi)
    f = {'status': 'Exploratory', 'test_id': 'D2-R', 'proxy_codes': sorted(fish), 'selected_objects': len(sequences),
         'observed_faces': len(allrows), 'maximum_fish_tokens_any_observed_face': max(sum(c in fish for c in r['signs_reading_rtl']) for r in allrows),
         'selected_texts_with_repeated_fish_code': sum(any(s.count(c) >= 2 for c in fish) for s in sequences),
         'selected_texts_with_at_least_two_fish_tokens': len(multi), 'observed_adjacent_pairs': observed,
         'shuffle_mean_adjacent_pairs': float(np.mean(adjacency_null)),
         'shuffle_reference_range_95': np.quantile(adjacency_null, [.025, .975]).tolist(),
         'shuffle_maximum': max(adjacency_null), 'shuffle_draws_at_least_observed': sum(v >= observed for v in adjacency_null),
         'add_one_tail_fraction': (1 + sum(v >= observed for v in adjacency_null)) / 2001,
         'shuffle_mean_repeating_runs': float(np.mean(repeat_null)),
         'shuffle_probability_zero_repeating_runs': sum(v == 0 for v in repeat_null) / 2000,
         'draws': 2000, 'seed': 20261009,
         'withdrawn_interpretation': 'Zero repeat and maximum-three run counts supply no structural support; text composition limits them.'}
    write(rawout / 'fish-shuffles.json', {'adjacent_pairs': adjacency_null, 'repeating_runs': repeat_null})
    write(out / 'fish-adjacency.json', f)

    audit = read(OWN / 'validation-audit.json')
    audit.update({'test_id': 'V1-R', 'supersedes': 'validation-audit.json', 'amendment_date': '2026-10-08',
                  'conflicting_label_overlaps': 0, 'parser_false_overlaps': 3,
                  'confirmed_ICIT_first_reading_entries': 1, 'confirmed_MH_first_alias_entries': 1,
                  'confirmed_iconography_only_mentions': 1})
    for obs in audit['observations']:
        if obs['ICIT'] == '3084':
            obs.update({'entry_type': 'MH_first_entry_with_ICIT_alias',
                        'observation': 'Segment 216 heads the entry MH2069/ICIT 3084/M-634. It is an ICIT alias inside an MH-first entry; segments 86, 94 and 147 already mention the object.'})
        elif obs['ICIT'] == '3656':
            obs.update({'entry_type': 'ICIT_first_reading_entry',
                        'observation': 'Segment 192 is an ICIT3656 reading entry for M-1357; MH2356 names the same object in segment 212. Segment 122 also mentions it.'})
        elif obs['ICIT'] == '2816':
            obs['entry_type'] = 'iconography_only_mention'
        elif obs['ICIT'] == '2717':
            obs.update({'classification': 'parser_false_overlap_multiple_aliases', 'entry_type': 'parser_attachment_error',
                        'correct_CISI': 'M-192', 'correct_ICIT_for_M1714': '2346',
                        'observation': 'Segment 185 pairs M-192 with ICIT2717, M-1714 with ICIT2346 and M-279 with ICIT2800. Segments 141 and 158 consistently pair M-1714 with ICIT2346. The parser attached the middle object to the first ICIT identifier.'})
        else:
            obs['entry_type'] = 'parser_attachment_error'
    audit['conclusion'] = 'Three repeated catalogue objects have three different entry types; only one is an ICIT-first reading entry. Three parser overlaps are false. Lecture validation membership and attempted/failure denominators remain unknown.'
    write(out / 'validation-audit-v2.json', audit)

    objects = []
    raw_objects = []
    for cisi, mh, number in [('M-1688', '2109', 1688), ('M-958', '2348', 958), ('M-979', '2564', 979)]:
        matches = [r for r in allrows if re.search(rf'(?<![A-Za-z])M[- ]?0*{number}(?!\d)', r['source_cisi'])]
        follow = collections.Counter()
        for r in matches:
            s = r['signs_reading_rtl']
            follow.update(b for a, b in zip(s, s[1:]) if a == '590')
            raw_objects.append(r)
        objects.append({'CISI': cisi, 'MH': mh, 'ICIT': sorted({r['object_family_id'] for r in matches}),
                        'observed_faces': len(matches), 'PU_following_codes': dict(follow),
                        'PU_followed_by_full_height_033': follow['033'], 'PU_followed_by_short_stroke_003': follow['003'],
                        'paper_location': 'B24 segments 95–96',
                        'source_limitation': 'The paper questions the tall sign shape at M-1688 and calls the short-stroke readings doubtful.'})
    write(rawout / 'PU-TRA-object-records.json', raw_objects)
    write(out / 'selection-errata.json', {'status': 'Exploratory', 'date': '2026-10-08',
          'unchanged_selection_sha256': digest(OWN / 'selection.json'), 'panel_id': 'A06',
          'corrections': [{'MH': '2109', 'old_CISI_annotation': 'M212', 'correct_CISI': 'M-1688'},
                          {'MH': '2348', 'old_CISI_annotation': 'M898', 'correct_CISI': 'M-958'}],
          'score_effect': 'None; roles and value lists are unchanged.', 'objects': objects})
    print(json.dumps({'output_root': out.relative_to(ROOT).as_posix(), 'lexical': lex['endpoints'],
                      'jar_nonfinal': distribution['signs']['740']['nonfinal_tokens'],
                      'arrow_nonfinal': distribution['signs']['520']['nonfinal_tokens'],
                      'fish_adjacency': f['observed_adjacent_pairs'], 'fish_shuffle_mean': f['shuffle_mean_adjacent_pairs']}, indent=2))

if __name__ == '__main__':
    main()
