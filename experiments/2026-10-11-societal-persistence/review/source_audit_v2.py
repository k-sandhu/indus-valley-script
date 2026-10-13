"""Check pinned local witnesses and selected-source locators; refuse old output."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

from bs4 import BeautifulSoup
from pypdf import PdfReader

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(f'Refusing existing output: {args.output}')
    ledger = json.loads((HERE / 'sources.json').read_text(encoding='utf-8'))
    checks = []

    def check(label, value):
        checks.append({'check': label, 'passed': bool(value)})
        if not value:
            raise AssertionError(label)

    check('seven distinct used works', len(ledger['works']) == 7)
    check('eight successful witnesses', len(ledger['witnesses']) == 8)
    check('one preserved unavailable lead', len(ledger['unavailable_leads']) == 1)
    works = {w['id']: w for w in ledger['works']}
    check('unique work identifiers', len(works) == 7)
    witness_ids = {w['id'] for w in ledger['witnesses']}
    check('unique witness identifiers', len(witness_ids) == 8)
    check('witness/work links', all(w['work'] in works for w in ledger['witnesses']))
    check('all acquired publications kept local', all(w['handling'] == 'local-only' for w in ledger['witnesses']))
    pdfs = {}
    html = {}
    xml = {}
    for w in ledger['witnesses']:
        p = ROOT / w['path']
        check(w['id'] + ' exists', p.is_file())
        check(w['id'] + ' bytes', p.stat().st_size == w['bytes'])
        check(w['id'] + ' SHA256', digest(p) == w['sha256'])
        if w['format'] == 'pdf':
            check(w['id'] + ' PDF signature', p.read_bytes().startswith(b'%PDF-'))
            pdfs[w['id']] = PdfReader(p)
            check(w['id'] + ' page count', len(pdfs[w['id']].pages) == w['pdf_pages'])
        elif w['format'] == 'JATS XML':
            xml[w['id']] = BeautifulSoup(p.read_bytes(), 'xml')
            check(w['id'] + ' article title', xml[w['id']].find('article-title').get_text(' ', strip=True) == works[w['work']]['title'])
            check(w['id'] + ' DOI', xml[w['id']].find('article-id', {'pub-id-type': 'doi'}).get_text(' ', strip=True) == works[w['work']]['doi'])
        else:
            html[w['id']] = BeautifulSoup(p.read_text(encoding='utf-8'), 'html.parser')

    check('Graham cover offset/title', 'Out of Order' in pdfs['W01'].pages[1].extract_text())
    check('Graham printed 4 apprenticeship locus', 'apprenticeships' in pdfs['W01'].pages[4].extract_text())
    check('Graham printed 6 nonidentical repair locus', 'exact restoration' in pdfs['W01'].pages[6].extract_text())
    check('Ostrom Nobel pagination begins 408', '408' in pdfs['W02'].pages[0].extract_text()[:100])
    check('Ostrom printed 411 polycentric locus', 'metropolitan' in pdfs['W02'].pages[3].extract_text())
    check('Ostrom printed 412 indirect-service locus', 'indirect services' in pdfs['W02'].pages[4].extract_text())
    check('Ostrom printed 414 precision locus', 'Models make precise assumptions' in pdfs['W02'].pages[6].extract_text())
    check('Ostrom printed 420 institutional rules locus', 'information rules' in ' '.join(pdfs['W02'].pages[12].extract_text().lower().split()))
    check('Cavdaroglu scheduling constraints locus', 'remainder of the horizon' in pdfs['W03'].pages[10].extract_text())
    author_text = html['W04'].get_text(' ', strip=True)
    check('Cavdaroglu online-first date locus', 'September 5, 2011' in author_text)
    check('Cavdaroglu journal date locus', 'March 2013' in author_text)
    marx_text = html['W05'].get_text(' ', strip=True)
    check('Marx selected section exists', 'II. The Two Departments' in marx_text)
    check('Marx fixed-capital locus', 'fixed capital' in marx_text.lower())
    check('Zhang selected restoration section exists', any(h.get_text(' ', strip=True) == 'Model of restoration process' for h in html['W06'].find_all(['h2', 'h3'])))
    check('Zhang CC BY 4.0 notice link', any('creativecommons.org/licenses/by/4.0/' in a.get('href', '') for a in html['W06'].find_all('a')))
    check('Smith selected definition section', xml['W07'].find('sec', {'id': 's1'}) is not None)
    smith = xml['W07'].find('sec', {'id': 's1'}).get_text(' ', strip=True)
    check('Smith four outcomes locus', all(q in smith for q in ['Persistence of occupation', 'Persistence of demographic scale', 'Persistence of institutions', 'Persistence of cultural practices']))
    check('Smith labeling locus', 'modern historical labeling' in smith)
    lawrence = xml['W08'].find('sec', {'id': 's8'}).find('p', recursive=False).get_text(' ', strip=True)
    check('Lawrence occupation episode locus', 'reoccupied' in lawrence)
    check('Lawrence ephemeral-phase locus', 'ephemeral' in lawrence)
    resolution = xml['W08'].find('sec', {'id': 's3'}).find('p', recursive=False).get_text(' ', strip=True)
    check('Lawrence dating-resolution locus', 'chipped stone' in resolution and 'tree ring' in resolution)
    check('Smith NC-ND rights locus', 'Attribution-NonCommercial-NoDerivatives' in xml['W07'].find('permissions').get_text(' ', strip=True))
    check('Lawrence CC BY rights locus', 'Attribution License 4.0' in xml['W08'].find('permissions').get_text(' ', strip=True))

    for d in ledger['derivatives']:
        p = ROOT / d['path']
        check(d['path'] + ' derivative SHA256', digest(p) == d['sha256'])
        check(d['path'] + ' parent SHA256', digest(ROOT / d['parent_path']) == d['parent_sha256'])
    lead = ledger['unavailable_leads'][0]
    fail = ROOT / lead['path']
    check('404 lead failure hash', digest(fail) == lead['sha256'])
    check('404 lead excluded from claims', lead['used_for_substantive_claims'] is False)

    observations = {o['id'] for w in ledger['works'] for o in w['observations']}
    claims = json.loads((HERE / 'claims.json').read_text(encoding='utf-8'))
    check('claim source identifiers resolve', all(o in observations for c in claims['claims'] for o in c['observations']))
    for c in claims['claims']:
        for output in c['outputs']:
            path = HERE / output.split('#', 1)[0]
            check(c['id'] + ' output ' + output, path.is_file())
    tests = json.loads((HERE / 'falsifiers.json').read_text(encoding='utf-8'))
    check('eight prospective tests', len(tests['tests']) == 8)
    check('prospective tests have rejection scopes', all(t['scope_of_rejection'] and t['remaining_limit'] for t in tests['tests']))
    args.output.mkdir(parents=True)
    result = {
        'created_utc': datetime.now(timezone.utc).isoformat(),
        'scope': 'Pinned witness integrity, selected text/rights locators and local claim links; semantic scope manually reviewed in REVIEW.md.',
        'source_ledger_sha256': digest(HERE / 'sources.json'),
        'claims_sha256': digest(HERE / 'claims.json'),
        'falsifiers_sha256': digest(HERE / 'falsifiers.json'),
        'code_sha256': digest(Path(__file__)),
        'checks_passed': len(checks),
        'checks': checks,
        'visual_inspection': [
            {'witness': 'W01', 'pdf_page': 7, 'printed_page': 6, 'observed': 'Printed footer and nonidentical-repair passage inspected in the local render.'},
            {'witness': 'W02', 'pdf_page': 5, 'printed_page': 412, 'observed': 'Printed footer and concentrated indirect-service passage inspected in the local render.'},
            {'witness': 'W03', 'pdf_page': 11, 'manuscript_page': 11, 'observed': 'Printed footer and constraints 14–18 discussion inspected in the local render.'},
        ],
    }
    (args.output / 'checks.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'checks_passed': len(checks)}))


if __name__ == '__main__':
    main()
