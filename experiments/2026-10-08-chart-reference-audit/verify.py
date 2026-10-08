"""Check saved witnesses, numbering coverage, deterministic output and input pins."""
from __future__ import annotations
import sys
sys.dont_write_bytecode = True
import ast
import collections
import importlib.metadata
import json
import argparse
import platform
import subprocess
from audit import ROOT, OWN, RAW, read, write, sha, key
from PIL import Image


def verify_revision():
    checks=[]
    def check(name, condition, detail=None):
        checks.append(dict(check=name, passed=bool(condition), detail=detail))
        assert condition, (name, detail)
    parent=read(OWN/'chart-reference-v2.json'); current=read(OWN/'chart-reference-v2.1.json')
    comparison=read(OWN/'comparison-v2.1.json'); observations=read(OWN/'cell-observations-v2.1.json')['rows']
    preserved=read(OWN/'preserved-inputs-v2.1.json')['inputs']
    check('V2, legacy outputs and every reviewer file unchanged', all(sha(ROOT/p)==h for p,h in preserved.items()), len(preserved))
    check('All current own JSON files parse', all(isinstance(read(p),(dict,list)) for p in OWN.glob('*.json')))
    for p in OWN.glob('*.py'): ast.parse(p.read_text(encoding='utf8'))
    check('Own Python files parse', True)
    check('687 ordered cells and original row fields retained', len(current['rows'])==687 and
          [key(r) for r in current['rows']]==[key(r) for r in parent['rows']] and
          all(set(a).issubset(b) for a,b in zip(parent['rows'],current['rows'])))
    check('No code or alternative changed from v2', all(a['code']==b['code'] and a['alternatives']==b['alternatives'] for a,b in zip(parent['rows'],current['rows'])))
    rank_changes=[key(b) for a,b in zip(parent['rows'],current['rows']) if a['rank']!=b['rank']]
    check('Only added class correction is p20_c3_r33, 85 to 86', rank_changes==['p20_c3_r33'] and
          next(r['rank'] for r in current['rows'] if key(r)=='p20_c3_r33')==86)
    check('687 unique codes', len({r['code'] for r in current['rows']})==687)
    ranks=[r['rank'] for r in current['rows']]
    check('Complete nondecreasing classes 1 to 401', ranks==sorted(ranks) and set(ranks)==set(range(1,402)))
    check('Auxiliary flags preserved', all(a['dashed_auxiliary']==b['dashed_auxiliary'] for a,b in zip(parent['rows'],current['rows'])))
    medium={key(r) for r in current['rows'] if r['numeric_confidence']=='medium'}
    required={'p20_c4_r13','p21_c0_r1','p21_c0_r18','p21_c3_r4','p21_c5_r34','p21_c6_r1'}
    check('Required cells medium and all medium reasons recorded', required.issubset(medium) and
          medium==set(comparison['summary']['medium_confidence_cells']) and len(medium)==33)
    check('15 first-pass reader errors and 630 once-read cells documented', comparison['summary']['first_pass_reader_errors']==15 and
          comparison['summary']['original_audit_once_read_cells']==630)
    reviewer=read(OWN/'review/independent-readings.json')['cells']
    bycell={key(r):r for r in current['rows']}
    check('Reviewer final blind sample agrees on all 63 codes and classes', len(reviewer)==63 and
          all(bycell[r['cell']]['rank']==r['class_number'] and bycell[r['cell']]['code']==r['code'] for r in reviewer))
    check('Reviewer nearest-neighbor witness reused unchanged', read(OWN/'review/knn-5-6-8-check.json')['summary']==
          {'digits':939,'counts':{'5':368,'8':282,'6':289},'agree':938,'disagree':1})
    manifest=read(RAW/'render-manifest.json')
    check('Original PDF, atlas and reference pins unchanged', sha(ROOT/manifest['source_pdf'])==manifest['source_sha256'] and
          sha(ROOT/'output/chart_atlas/reference.json')==manifest['atlas_sha256'] and
          sha(ROOT/'research/chart_reference/manual_numeric_reference.json')==manifest['original_reference_sha256'])
    check('First-pass observations preserved', sha(OWN/'visual-readings.json')==read(RAW/'review-selection.json')['visual_readings_sha256'])
    native=read(RAW/'revision-2026-10-08-v2.1/native-render-manifest.json')
    check('Eight native inspection crops retain recorded hashes', len(native['cells'])==8 and
          all(sha(ROOT/r['path'])==r['sha256'] for r in native['cells']))
    integrity=read(OWN/'consumer-input-integrity-v2.1.json')
    check('Current consumer pins unchanged', integrity['unchanged'] and all(sha(ROOT/p)==v['sha256'] for p,v in integrity['inputs'].items()),integrity['files'])
    generated=['chart-reference-v2.1.json','cell-observations-v2.1.json','comparison-v2.1.json','impact-v2.1.json','consumer-input-integrity-v2.1.json']
    before={n:sha(OWN/n) for n in generated}
    subprocess.run([sys.executable,'-B',str(OWN/'amend-reference.py'),'apply'],cwd=ROOT,check=True,capture_output=True)
    subprocess.run([sys.executable,'-B',str(OWN/'impact.py'),'--reference',str(OWN/generated[0]),
                    '--comparison',str(OWN/generated[2]),'--out',str(OWN/generated[3]),'--integrity-out',str(OWN/generated[4]),
                    '--raw-subdir','revision-2026-10-08-v2.1'],cwd=ROOT,check=True,capture_output=True)
    check('Amendment and impact replay byte-identically',before=={n:sha(OWN/n) for n in generated})
    check('Preserved witnesses unchanged after replay',all(sha(ROOT/p)==h for p,h in preserved.items()))
    images=list((RAW/'revision-2026-10-08-v2.1').glob('*.png'))
    for p in images:
        with Image.open(p) as im:im.verify()
    check('All nine new PNGs decode',len(images)==9)
    check('Current guidance and reports present',all((OWN/n).exists() for n in
          ('README.md','REPORT.md','RETROSPECTIVE.md','PROTOCOL.md','RECOMMENDED-USE.md','registry-entry.json')))
    payload=(RAW/'revision-2026-10-08-v2.1/prose-scan.txt').read_bytes()
    encoding='utf-16' if payload.startswith((b'\xff\xfe',b'\xfe\xff')) else 'utf-8-sig'
    prose=json.loads(payload.decode(encoding))
    check('Prose scan completed with no flags',not prose['flags'],prose['files_scanned'])
    write(OWN/'verification-v2.1.json',dict(status='Verified computation',checks_passed=len(checks),checks=checks,
          scope='Mechanical replay and immutable witness checks. V2.1 numbering remains Exploratory, two AI readings, no expert review.'))
    inventory=[]
    for folder in (OWN,RAW):
        for p in sorted(folder.rglob('*')):
            if p.is_file() and p!=OWN/'file-inventory-v2.1.json':
                disposition='reviewer-owned-readonly' if p.is_relative_to(OWN/'review') or p==OWN/'REVIEW.md' else ('own-work' if p.is_relative_to(OWN) else 'local-only')
                inventory.append(dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p),bytes=p.stat().st_size,disposition=disposition))
    write(OWN/'file-inventory-v2.1.json',dict(files=inventory,inventory_self='experiments/2026-10-08-chart-reference-audit/file-inventory-v2.1.json',
          status='Verified computation'))
    print(dict(checks_passed=len(checks),preserved_files=len(preserved),new_raw_pngs=len(images)))


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
    parser=argparse.ArgumentParser();parser.add_argument('--version',choices=['2','2.1'],default='2')
    args=parser.parse_args()
    verify_revision() if args.version=='2.1' else main()
