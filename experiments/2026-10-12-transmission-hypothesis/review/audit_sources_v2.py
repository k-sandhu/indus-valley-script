"""Independent documentary pins and locus checks, without historical scoring."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
from acquire_controls import REPO, RAW

HERE = Path(__file__).resolve().parent
DERIVATIVE_KEYS = {
    'R01': 'jamison2014-1-15', 'R02': 'oldavestan2006',
    'R03': 'boyce2003', 'R04': 'narasimhan2019',
    'R05': 'witzel1997', 'R07': 'skjaervo-kayanian',
}


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def clean(text):
    text = re.sub(r'(?<=\w)-[ \t]*\n[ \t]*(?=\w)', '', text)
    return re.sub(r'\s+', ' ', text).casefold()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, default=HERE / 'source-checks-v2')
    out = parser.parse_args().out.resolve()
    if not out.is_relative_to(HERE):
        raise SystemExit('Output must be within the owned review directory')
    if out.exists():
        raise SystemExit('Refusing existing output directory')
    out.mkdir()
    checks = []

    def check(label, condition):
        checks.append({'check': label, 'passed': bool(condition)})
        if not condition:
            raise AssertionError(label)

    try:
        source_path = HERE / 'sources-v2.json'
        observation_path = HERE / 'observations-v2.json'
        sources = read(source_path)['sources']
        observations = read(observation_path)['observations']
        by_id = {s['source_id']: s for s in sources}
        check('seven distinct target records', len(sources) == 7 and len(by_id) == 7)
        check('six primary works at declared scopes', sum(s['selected_primary_work'] for s in sources) == 6)
        check('19 distinct observation IDs', len(observations) == 19 and
              len({o['observation_id'] for o in observations}) == 19)
        witness_paths = set()
        for source in sources:
            check(f"{source['source_id']} selected reading scope explicit", bool(source['reading_scope']))
            for witness in source['witnesses']:
                path = REPO / witness['path']
                witness_paths.add(path)
                check(f"witness hash {witness['path']}", sha(path) == witness['sha256'])
                check(f"witness bytes {witness['path']}", path.stat().st_size == witness['bytes'])
                check(f"local handling {witness['path']}", witness['redistribution'] == 'local-only')
                check(f"retrieval time {witness['path']}", bool(witness.get('retrieved_utc')))
                if path.suffix == '.pdf':
                    check(f"actual PDF signature {witness['path']}", path.read_bytes().startswith(b'%PDF'))
        check('Old Avestan mirrors have identical bytes',
              len({w['sha256'] for w in by_id['R02']['witnesses']}) == 1)
        check('unavailable Pollock target has no substantive observations', not by_id['R06']['selected_primary_work'] and
              not any(o['source_id'] == 'R06' for o in observations))

        derivative_doc = read(RAW / 'extraction-v1.json')
        derivatives = {r['source_key']: r for r in derivative_doc['derivatives']}
        for row in derivatives.values():
            path = REPO / row['path']
            check(f"derivative hash {row['path']}", sha(path) == row['sha256'])
            check(f"derivative parent {row['parent_path']}", sha(REPO / row['parent_path']) == row['parent_sha256'])
        for observation in observations:
            oid, sid = observation['observation_id'], observation['source_id']
            check(f'{oid} included source join', sid in by_id and by_id[sid]['selected_primary_work'])
            check(f'{oid} kind and inference scope', bool(observation['kind']) and bool(observation['inference_limit']))
            key = DERIVATIVE_KEYS[sid]
            if oid in {'O-R01-2', 'O-R01-3'}:
                key = 'jamison2014-13-22'
            path = REPO / derivatives[key]['path']
            if path.suffix == '.json':
                doc = read(path)
                n = observation['pdf_page_one_based']
                check(f'{oid} page in witness', isinstance(n, int) and 1 <= n <= doc['page_count'])
                text = doc['pages'][n - 1]['text']
            else:
                text = path.read_text(encoding='utf-8')
            check(f'{oid} source anchor at declared locus', clean(observation['source_anchor']) in clean(text))

        attempts = [row for version in [1, 2, 3] for row in read(RAW / f'acquisition-v{version}.json')]
        check('all12 distinct acquisition routes retained', len(attempts) == 12 and
              len({r['route_id'] for r in attempts}) == 12)
        for row in attempts:
            if 'path' in row:
                check(f"attempt response pin {row['route_id']}", sha(REPO / row['path']) == row['sha256'])
            else:
                check(f"failed route explicit {row['route_id']}", bool(row.get('error')))

        renders = read(RAW / 'renders-v2.json')
        check('earlier render-manifest correction preserved', bool(renders['correction']) and
              sha(RAW / 'renders-v1.json') == renders['preserved_first_manifest_sha256'])
        check('eight inspected-page renders', len(renders['renders']) == 8)
        for row in renders['renders']:
            check(f"render pin {row['path']}", sha(REPO / row['path']) == row['sha256'])
            check(f"render parent {row['path']}", sha(REPO / row['parent_path']) == row['parent_sha256'])

        controls = read(HERE / 'counterexamples-v1/results.json')
        check('six hypothetical countercases and ten simple consistency assertions', len(controls['cases']) == 6 and
              controls['checks_passed'] == 10 and all(c['passed'] for c in controls['checks']))
        check('countercase code pin', controls['code_sha256'] == sha(HERE / 'counterexamples.py'))
        check('countercase protocol pin', controls['protocol_sha256'] == sha(HERE / 'COUNTEREXAMPLES-PROTOCOL.md'))
        fixture = read(HERE / 'validator-scope-v2/interpretation.json')
        check('negative semantic fixture demonstrates declaration limit', fixture['expected_limitation_observed'] is True)
        check('fixture reviewer code pin', fixture['reviewer_code_sha256'] == sha(HERE / 'check_validator_scope_v2.py'))
        check('fixture result pin', fixture['validator_result_sha256'] == sha(HERE / 'validator-scope-v2/validator-output/audit.json'))
        check('failed wrapper retained', (HERE / 'validator-scope-v1/failure.json').is_file())

        raw_paths = {p for p in RAW.rglob('*') if p.is_file()} | witness_paths
        names = sorted(p.relative_to(REPO).as_posix() for p in raw_paths)
        ignored = subprocess.run(['git', 'check-ignore', '--', *names], capture_output=True,
                                 text=True, encoding='utf-8')
        check('every owned raw and reused witness path ignored', ignored.returncode == 0 and
              set(ignored.stdout.splitlines()) == set(names))
        result = {'created_utc': datetime.now(timezone.utc).isoformat(),
                  'scope': 'Documentary identity, declared source loci, hypothetical-control scope and local handling; no historical truth or route likelihood test',
                  'checks_passed': len(checks), 'checks': checks,
                  'input_sha256': {name: sha(HERE / name) for name in ['sources-v2.json', 'observations-v2.json',
                                    'PROTOCOL.md', 'CONTROL-LOCI.md', 'AMENDMENT-source-access.md',
                                    'SOURCE-CHECK-PROTOCOL.md', 'AMENDMENT-source-anchor.md']},
                  'code_sha256': sha(Path(__file__)),
                  'source_counts': {'target_records': 7, 'scoped_primary_works': 6, 'observations': 19,
                                    'access_attempts': 12, 'visually_inspected_page_renders': 8},
                  'raw_paths_checked': names,
                  'failed_attempts_preserved': ['validator-scope-v1/failure.json', 'source-checks-v1/failure.json'],
                  'source_scope_note': 'Source author arguments, modern editions and sampling findings remain distinct from observed ancient carriers.'}
        (out / 'checks.json').write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
        print(json.dumps({'checks_passed': len(checks), 'sources': 6, 'observations': 19,
                          'raw_paths_ignored': len(names), 'endpoint': str(out / 'checks.json')}))
    except Exception as exc:
        (out / 'failure.json').write_text(json.dumps({'status': 'failed; preserved', 'error': repr(exc),
                                                    'checks': checks}, indent=2) + '\n', encoding='utf-8')
        raise


if __name__ == '__main__':
    main()
