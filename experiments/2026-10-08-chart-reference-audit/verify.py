"""Check saved witnesses, numbering coverage, deterministic output and input pins."""
from __future__ import annotations
import sys
sys.dont_write_bytecode = True
import ast
import collections
import importlib.metadata
import json
import platform
import subprocess
from audit import ROOT, OWN, RAW, read, write, sha, key
from PIL import Image


def main():
    checks = []
    def check(name, condition, detail=None):
        checks.append(dict(check=name, passed=bool(condition), detail=detail))
        assert condition, (name, detail)

    old = read(ROOT / 'research/chart_reference/manual_numeric_reference.json')
    new = read(OWN / 'chart-reference-v2.json')
    obs = read(OWN / 'cell-observations.json')['rows']
    manifest = read(RAW / 'render-manifest.json')
    check('All owned JSON files parse', all(isinstance(read(p), (dict, list)) for p in OWN.glob('*.json')))
    for path in OWN.glob('*.py'):
        ast.parse(path.read_text(encoding='utf-8'), filename=str(path))
    check('All Python files parse', True)
    keys = [key(r) for r in old['rows']]
    check('687 cell identities and preserved order', len(keys) == len(set(keys)) == 687 and keys == [key(r) for r in new['rows']])
    check('687 distinct saved pixel-reading records', set(keys) == {r['cell'] for r in obs} and len(obs) == 687)
    check('Complete 8x image coverage', len(manifest['cells']) == 687 and
          all((ROOT / r['path']).exists() and sha(ROOT / r['path']) == r['sha256'] for r in manifest['cells']))
    check('Full pages at 6 pixels per point', manifest['page_scale'] >= 6 and
          all((RAW / f'page-{p}-6x.png').exists() for p in (20, 21)))
    check('PDF unchanged since first rendering', sha(ROOT / manifest['source_pdf']) == manifest['source_sha256'])
    check('Atlas metadata unchanged since first rendering', sha(ROOT / 'output/chart_atlas/reference.json') == manifest['atlas_sha256'])
    check('Original numeric reference unchanged since first rendering', sha(ROOT / 'research/chart_reference/manual_numeric_reference.json') == manifest['original_reference_sha256'])
    check('Original row fields retained', all(set(a).issubset(b) for a, b in zip(old['rows'], new['rows'])))
    check('Auxiliary flags preserved', all(a['dashed_auxiliary'] == b['dashed_auxiliary'] for a, b in zip(old['rows'], new['rows'])))
    check('No final duplicate codes', len({r['code'] for r in new['rows']}) == 687)
    ranks = [r['rank'] for r in new['rows']]
    check('All classes 1 through 401 and no decreases', set(ranks) == set(range(1, 402)) and ranks == sorted(ranks))
    check('No unresolved alternatives', all(not r['alternatives'] and not r['rank_alternatives'] for r in new['rows']))
    selected = read(RAW / 'review-selection.json')
    check('Saved first-pass reading not replaced', sha(OWN / 'visual-readings.json') == selected['visual_readings_sha256'])
    check('All 57 reinspection evidence paths exist', sum(r['reinspected'] for r in obs) == 57 and
          all((ROOT / r['review_image']).exists() for r in obs if r['reinspected']))
    integrity = read(OWN / 'consumer-input-integrity.json')
    check('Consumer input hashes unchanged', integrity['unchanged'] and
          all(sha(ROOT / p) == value['sha256'] for p, value in integrity['inputs'].items()), integrity['files'])
    generated = ['chart-reference-v2.json', 'cell-observations.json', 'comparison.json', 'impact.json', 'consumer-input-integrity.json']
    before = {name: sha(OWN / name) for name in generated}
    for script, args in [('audit.py', ['compare']), ('impact.py', [])]:
        subprocess.run([sys.executable, '-B', str(OWN / script), *args], cwd=ROOT, check=True, capture_output=True, text=True)
    after = {name: sha(OWN / name) for name in generated}
    check('Comparison and impact rerun byte-identically', before == after, before)
    images = list(RAW.rglob('*.png'))
    for path in images:
        with Image.open(path) as im:
            im.verify()
    check('All saved PNG files decode', True, len(images))
    impact = read(OWN / 'impact.json')
    check('N reused cards are identical to M v2', bool(impact['N_charts']) and all(r['identical_to_M_v2_card'] for r in impact['N_charts']))
    check('Required written deliverables present', all((OWN / name).exists() for name in
          ('README.md', 'REPORT.md', 'PROTOCOL.md', 'RETROSPECTIVE.md', 'sources.json', 'registry-entry.json')))
    prose_path = RAW / 'prose-scan.txt'
    if prose_path.exists():
        payload = prose_path.read_bytes()
        encoding = 'utf-16' if payload.startswith((b'\xff\xfe', b'\xfe\xff')) else 'utf-8-sig'
        prose = json.loads(payload.decode(encoding))
        check('Prose scan completed with no flags', prose['files_scanned'] == 4 and not prose['flags'],
              dict(path=prose_path.relative_to(ROOT).as_posix(), sha256=sha(prose_path)))
    versions = {}
    for package in ('PyMuPDF', 'Pillow', 'pyarrow', 'numpy'):
        try:
            versions[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            versions[package] = None
    write(OWN / 'verification.json', dict(status='Verified computation', checks=checks, checks_passed=len(checks),
                                         environment=dict(python=sys.version, platform=platform.platform(), packages=versions),
                                         scope='Mechanical checks and reproducible joins; printed digit decisions remain Exploratory.'))
    inventory = []
    for folder, disposition in [(OWN, 'own-work'), (RAW, 'local-only-witness-or-extracted-record')]:
        for path in sorted(folder.rglob('*')):
            if path.is_file() and path != OWN / 'file-inventory.json':
                inventory.append(dict(path=path.relative_to(ROOT).as_posix(), bytes=path.stat().st_size,
                                      sha256=sha(path), disposition=disposition))
    write(OWN / 'file-inventory.json', dict(status='Verified computation', files=inventory,
          own_files_excluding_this_inventory=sum(r['disposition'] == 'own-work' for r in inventory),
          local_raw_files=sum(r['disposition'].startswith('local-only') for r in inventory),
          inventory_self='experiments/2026-10-08-chart-reference-audit/file-inventory.json (excluded from own hash list)'))
    print(dict(checks_passed=len(checks), raw_pngs=len(images), total_inventory_entries=len(inventory)))


if __name__ == '__main__':
    main()
