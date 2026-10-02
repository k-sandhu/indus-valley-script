"""Freeze the bounded source amendment and check every preserved source hash."""
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re

import fitz

ROOT = Path(__file__).resolve().parents[2]
FRAME = ROOT / 'experiments/2026-10-02-six-hour/kanmer-physical-use'
BASE = FRAME / 'source-continuation-2026-10-02'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def main():
    for name in ['results.json', 'verification.json', 'artifact-manifest.json']:
        if (BASE / name).exists():
            raise RuntimeError(f'Preserve frozen {name}.')
    checks = []

    def check(name, passed, details=None):
        checks.append(dict(check=name, passed=bool(passed), details=details))

    protocol_hash = sha(BASE / 'PROTOCOL.md')
    check('Protocol hash preserved', protocol_hash == '6cafea69bf8681731a0983735b5c6167a6256a99ca7f05d3877c48805077ac87')
    access = []
    for folder in sorted(BASE.glob('acquisition-*')):
        entries = json.loads((folder / 'access.json').read_text(encoding='utf-8'))
        access.extend(entries)
        for entry in entries:
            if 'sha256' in entry:
                check(f"Acquired witness {folder.name}/{entry['id']} hash", sha(ROOT / entry['local_path']) == entry['sha256'])
    cv = BASE / 'local-witness/inspection-v1/seth-public-cv.docx'
    check('Original downloaded CV hash', sha(cv) == 'f64fb94b9fa759d500d95bf1308763d170c19af6b8bd497ad9f792626414f77d')
    paragraphs = json.loads((BASE / 'local-witness/inspection-v1/seth-public-cv-paragraphs.json').read_text(encoding='utf-8'))
    check('CV chapter coordinates and range', '2012' in paragraphs[86] and '749-760' in paragraphs[87] and '978-4-902325-72-0' in paragraphs[88])
    check('CV early-use title coordinates and year', '2010' in paragraphs[229] and 'Harappan Passport from Kanmer' in paragraphs[230] and 'Monthly : 3' in paragraphs[230])
    parpola = json.loads((BASE / 'local-witness/inspection-v3/parpola2018-authorproof-pages.json').read_text(encoding='utf-8'))
    check('Author-proof overview citation', '2012: 484-490' in parpola[2]['text'])
    check('Author-proof pass paragraph citation', '2012: 487' in parpola[18]['text'] and 'Arthaśāstra' in parpola[18]['text'])
    contents = json.loads((BASE / 'local-witness/inspection-v3/journal39-contents-pages.json').read_text(encoding='utf-8'))
    check('Journal file is four-page contents witness', len(contents) == 4 and '147' in contents[1]['text'] and '165' in contents[1]['text'] and 'Kanmer' in contents[1]['text'])
    draft = FRAME / 'local-witness/acquisition-remaining-chapter-pages/chapter8-page10-text.txt'
    draft_text = draft.read_text(encoding='utf-8')
    check('Earlier draft links use interpretation to 2009 citation', 'passports or identity cards (Kharakwal et al. 2009)' in draft_text)
    original_manifest = json.loads((FRAME / 'artifact-manifest.json').read_text(encoding='utf-8'))
    for entry in original_manifest['files']:
        check('Main-frame preserved: ' + entry['path'], sha(ROOT / entry['path']) == entry['sha256'])
    original_checks = json.loads((BASE / 'inspection-v3/checks.json').read_text(encoding='utf-8'))
    for item in original_checks:
        check('Reviewed PDF acquisition: ' + item['check'], item['passed'])
    detailed = [
        dict(id='KC01', basis='journal contents pixels', source='journal39-contents', pdf_page=2, printed_page=2, observation='Kanmer entry starts 147; following Badali entry starts 165; article body unacquired'),
        dict(id='KC02', basis='institutional bibliography pixels', source='rhin-annual2009', pdf_page=183, printed_page=181, observation='Original-paper second entry dates Puratattva article December 2009, pages 147–164'),
        dict(id='KC03', basis='existing public draft text', source='chapter8-draft', draft_page=10, source_sha256=sha(draft), observation='Conclusion cites Kharakwal et al. 2009 for business-family and passport/identity-card proposal'),
        dict(id='KC04', basis='original public author CV XML', source='seth-public-cv', paragraph_numbers=[230, 231], observation='2010 coauthored Hindi passport article in Jan Mangal, page 3; no issue/month specified'),
        dict(id='KC05', basis='original public author CV XML', source='seth-public-cv', paragraph_numbers=[87, 88, 89], observation='Final script-material chapter listed as 749–760 with final-volume ISBN; previous source 749–759 retained'),
        dict(id='KC06', basis='original author-proof pixels and text', source='parpola2018-authorproof', pdf_pages=[1, 3, 19, 27], printed_page_mapping=None, observation='June 2016 proof for 2018 chapter: explicit final-book citations 484–490 and 487; pass proposal with Arthaśāstra analogy'),
        dict(id='KC07', basis='institutional bibliography pixels', source='rhin-annual2011', pdf_page=52, printed_page=50, observation='Editing/Coediting second entry gives final volume March 2012, 844 pages'),
        dict(id='KC08', basis='original institutional catalogue and public rendered detail', source='rhin-book-detail', observation='Archives (Library), call mark P015-Z000-1748, material 5000375, x + 844 pages and one CD-ROM; no scan displayed'),
    ]
    raw = BASE / 'local-witness/amendment-v1'
    raw.mkdir(parents=True, exist_ok=False)
    write(raw / 'source-derived-amendment.json', dict(observations=detailed, new_object_joins=[], new_physical_observations=[], original_frame_changed=False))
    with fitz.open(BASE / 'local-witness/acquisition-final-leads/parpola2018-authorproof.pdf') as doc:
        bounds = {str(page): [list(rect) for rect in doc[page - 1].search_for(term)] for page, term in [(3, '2012: 484-490'), (19, '2012: 487')]}
    write(raw / 'proof-citation-bounds.json', dict(coordinate_units='PDF points', pdf_page_base=1, source_sha256=sha(BASE / 'local-witness/acquisition-final-leads/parpola2018-authorproof.pdf'), bounds=bounds))
    statuses = Counter(str(a.get('http_status', 'transport-failure')) for a in access)
    results = dict(completed_utc=datetime.now(timezone.utc).isoformat(), protocol_sha256=protocol_hash,
                   design='bounded original-source continuation; main physical frame unchanged',
                   http_requests=len(access), http_status_counts=dict(statuses), browser_downloads_successful=1,
                   source_amendment_observations=len(detailed), new_object_joins=0, new_physical_observations=0,
                   original_targets=[dict(target=t, acquired=False) for t in ['Puratattva 39 article body, pages 147–164', 'Final excavation report printed page 487', 'Final excavation report printed page 832', 'Explicit registration for photographed fourth specimen']],
                   new_acquisition_leads=['Hindi 2010 Jan Mangal article, page 3, issue/month unresolved', 'RIHN book and CD-ROM holding P015-Z000-1748, material 5000375', 'Final-volume chapter range 749–760 to resolve citation disagreement'],
                   source_detail_ledger=(raw / 'source-derived-amendment.json').relative_to(ROOT).as_posix(),
                   source_detail_ledger_sha256=sha(raw / 'source-derived-amendment.json'))
    write(BASE / 'results.json', results)
    write(BASE / 'verification.json', dict(checks_total=0, checks_passed=0, checks=[]))
    for path in BASE.glob('*.md'):
        for target in re.findall(r'\]\(([^)]+)\)', path.read_text(encoding='utf-8')):
            if '://' not in target and not target.startswith('#'):
                check(f'Navigation {path.name}: {target}', (path.parent / target.split('#')[0]).exists())
    write(BASE / 'verification.json', dict(completed_utc=datetime.now(timezone.utc).isoformat(), checks_total=len(checks), checks_passed=sum(c['passed'] for c in checks), checks=checks))
    paths = [p for p in BASE.rglob('*') if p.is_file() and 'local-witness' not in p.relative_to(BASE).parts and p.name != 'artifact-manifest.json']
    paths += sorted((ROOT / 'src/six_hour').glob('kanmer_continuation*.py'))
    write(BASE / 'artifact-manifest.json', dict(scope='Own eligible artifacts, including code and source metadata; raw witnesses excluded', files=[dict(path=p.relative_to(ROOT).as_posix(), bytes=p.stat().st_size, sha256=sha(p)) for p in sorted(paths)]))
    print(json.dumps(dict(results=results, checks_total=len(checks), checks_passed=sum(c['passed'] for c in checks), failures=[c for c in checks if not c['passed']])))


if __name__ == '__main__':
    main()
