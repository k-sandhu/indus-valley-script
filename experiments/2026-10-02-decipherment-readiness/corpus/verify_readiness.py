"""Manual scope, count, preservation and navigation checks for this readiness audit."""
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def write(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')


def main():
    if (BASE / 'verification.json').exists() or (BASE / 'artifact-manifest.json').exists():
        raise RuntimeError('Preserve prior readiness verification.')
    inventory = read(BASE / 'inventory-final-2026-10-02/evidence-inventory.json')
    supplement = read(BASE / 'filter-supplement-2026-10-02/results.json')
    registry = read(ROOT / 'knowledge/experiments/registry.json')['experiments']
    covered = read(BASE / 'inventory-final-2026-10-02/coverage.json')
    checks = []

    def check(name, passed, detail=None):
        checks.append(dict(check=name, passed=bool(passed), detail=detail))

    check('all 101 registry IDs covered', covered['registry_ids_read'] == [row['id'] for row in registry] and covered['registry_entries'] == 101)
    source_ids = ['ROOT-01', 'ROOT-13', 'ROOT-19', 'CONTEXT-01', 'ARCH-01', 'ARCH-02', 'ARCH-03', 'KANMER-01', 'KANMER-02']
    write(BASE / 'coverage.json', dict(registry_path='knowledge/experiments/registry.json', registry_sha256=digest(ROOT / 'knowledge/experiments/registry.json'), registry_entries=len(registry), registry_ids_read=covered['registry_ids_read'], directly_reviewed_corpus_or_source_frame_ids=source_ids, scope='Registry metadata and retrospective scope map cover every entry; direct record inspection concentrates on the named actual corpus/source frames. Synthetic method controls are excluded from actual Indus counts.'))
    check('named direct source IDs exist', set(source_ids).issubset({row['id'] for row in registry}))
    for relative, expected in inventory['input_hashes'].items():
        check('preserved input ' + relative, digest(ROOT / relative) == expected)
    check('protocol unchanged', inventory['protocol_sha256'] == digest(BASE / 'PROTOCOL.md'))
    check('inventory code snapshot identifies execution', inventory['code_sha256'] == digest(BASE / 'inventory-final-2026-10-02/code_snapshot.py'))
    for relative, n in [('inventory-final-2026-10-02/verification.json', 10), ('filter-supplement-2026-10-02/verification.json', 6)]:
        result = read(BASE / relative)
        check('accepted endpoint passes ' + relative, result['checks_total'] == result['checks_passed'] == n)
    partial = read(BASE / 'inventory-refined-2026-10-02/verification.json')
    check('earlier failed accounting retained', partial['checks_total'] == 10 and partial['checks_passed'] == 9)
    check('initial schema failure retained', (BASE / 'inventory-2026-10-02/failure.json').is_file())
    # Independent count reconstruction uses raw lines and the captured index.
    observed = [json.loads(line) for line in (ROOT / 'data/normalized/lipi_observed_faces.jsonl').read_text(encoding='utf-8').splitlines()]
    nominated = [row for row in observed if row['metadata']['class'] == 'VN']
    counted = sum(row['clean_rtl_singleline'] and row['length'] >= 3 for row in nominated)
    check('VN independent scalar count', len(nominated) == 355 and counted == 2 and Counter(row['length'] for row in nominated) == Counter({2:336,1:17,3:2}))
    index = read(ROOT / 'data/lipi/src/assets/data/seal_id_and_image_mapping.json')
    image_root = ROOT / 'data/lipi/public/seal_images'
    actual_names = {p.name for p in image_root.iterdir() if p.is_file()}
    indexed_names = {name for values in index.values() for name in values}
    check('image index independent set accounting', len(actual_names) == 8722 and len(indexed_names) == 6570 and len(actual_names-indexed_names) == 2152 and not indexed_names-actual_names)
    mapped = [row for row in observed if row['source_cisi'] in index and any(name in actual_names for name in index[row['source_cisi']])]
    check('exact-key image join independent count', len(mapped) == 2944 and len({row['object_family_id'] for row in mapped}) == 2507 and sum(row['clean_rtl_singleline'] and row['length'] >= 3 for row in mapped) == 1400)
    check('no semantic answer keys in analytical schemas', all(not row['supplied_interpretive_keys_found'] for row in inventory['corpus_schemas'].values()))
    check('G01 has four independently located trace records', inventory['lothal']['recurring_groups'][0]['selected_trace_ids'] == ['L-124','L-126','L-193','L-206'])
    check('reported tablet stroke count histogram', inventory['direct_tablet_stroke_counts']['histogram'] == {'3':5,'4':2})
    check('three local pixel inspections preserve hashes', len(supplement['visual_samples']) == 3 and all(digest(ROOT / row['path']) == row['sha256'] for row in supplement['visual_samples']))
    editorial = read(BASE / 'editorial-review.json')
    check('five owned prose files reviewed', editorial['files_scanned'] == 5 and not editorial['flags'])
    for path in BASE.glob('*.md'):
        for target in re.findall(r'\]\(([^)]+)\)', path.read_text(encoding='utf-8')):
            if '://' not in target and not target.startswith('#'):
                check('navigation ' + path.name + ': ' + target, (path.parent / target.split('#')[0]).exists())
    for path in BASE.glob('*.py'):
        compile(path.read_text(encoding='utf-8'), str(path), 'exec')
        check('helper syntax ' + path.name, True)
    result = dict(completed_utc=datetime.now(timezone.utc).isoformat(), checks_total=len(checks), checks_passed=sum(row['passed'] for row in checks), checks=checks, scope='Actual corpus inventory, filter/source accounting, preserved inputs and own navigation; no semantic or model performance claim.')
    write(BASE / 'verification.json', result)
    files = sorted(path for path in BASE.rglob('*') if path.is_file() and path.name != 'artifact-manifest.json' and '__pycache__' not in path.parts)
    write(BASE / 'artifact-manifest.json', dict(scope='Own prose, source locators, schemas, aggregate counts and code; no copied inscription inventory, translation values or pixels', files=[dict(path=path.relative_to(ROOT).as_posix(), bytes=path.stat().st_size, sha256=digest(path)) for path in files]))
    print(json.dumps(dict(checks=result['checks_total'], passed=result['checks_passed'], failures=[row for row in checks if not row['passed']], artifacts=len(files))))


if __name__ == '__main__':
    main()
