"""Export the review disposition and inventory without altering source witnesses."""
import csv
import hashlib
import json
from pathlib import Path
import re
import runpy

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RAW = ROOT/'data/raw/2026-10-06-field-recommendations'

def save(name, value):
    (HERE/name).write_bytes((json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))

def main():
    coded = runpy.run_path(str(HERE/'curation.py'))
    rows = json.loads((HERE/'recommendations.json').read_text(encoding='utf-8'))
    roster = [
        ('Jonathan Mark Kenoyer','KENOYER-2020'),('Asko Parpola','PARPOLA-2008'),
        ('Bryan Wells','WELLS-2015'),('Andreas Fuls','FULS-2023'),('Massimo Vidale','VIDALE-2007'),
        ('Gregory Possehl','POSSEHL-PAGE-1996'),('Iravatham Mahadevan','GANESAN-ETAL-2010'),
        ('Rajesh Rao','RAO-2009'),('Nisha Yadav','YADAV-2013'),('Mayank Vahia','VAHIA-2025'),
        ('Richard Sproat','SPROAT-2010'),('Steve Farmer','FSW-2004'),('Michael Witzel','FSW-2004'),
        ('Bahata Ansumali Mukhopadhyay','MUKHOPADHYAY-2023'),('Marta Ameri','AMERI-2013'),
        ('Adam Green','GREEN-2021'),('Cameron Petrie','PETRIE-LYNAM-2020'),('Rita Wright',None),
        ('Shereen Ratnagar',None),('Randall Law','LAW-2011'),
        ('Heather Miller','MILLER-PROJECT-2025'),('Vasant Shinde',None),('R. S. Bisht',None),
        ('K. Rajan','RAJAN-SIVANANTHAM-2025'),('Dennys Frenez','FRENEZ-TALK-2026')]
    coverage = []
    for name,sid in roster:
        ids = [r['id'] for r in rows if r['source_id']==sid] if sid else []
        coverage.append(dict(researcher=name,source_id=sid,recommendation_ids=ids,
                             status='Exploratory',disposition='Recommendation admitted' if ids else 'No recommendation admitted; see coverage.json'))
    save('roster-coverage.json',coverage)
    old = json.loads((HERE/'first-pass/recommendations.json').read_text(encoding='utf-8-sig'))
    replacement = [
        'F01','F02','F03','F04','F13','F11','F05 F06','F09 F10','F22',
        'F16 F17 F18','F19 F20','F47 F48','F21','F27 F28 F29 F30','F23 F24 F25 F26',
        'F36 F37','F36 F37','F40','F57 F58 F59', 'F41 F42','', 'F55','F49 F50 F51',
        'F32 F33 F34 F35','F52','', 'F53 F54','', 'F46','F39','','F43 F44 F45','']
    assert len(old)==len(replacement)==33
    ledger=[]
    for i,(prior,new) in enumerate(zip(old,replacement),1):
        researcher=prior['researcher'].replace('M\x3fry','M\u00e9ry')
        rec_ids=[rid for rid in new.split() if any(r['id']==rid for r in rows)]
        moved=[rid for rid in new.split() if rid in {'F04','F53','F55'}]
        ledger.append(dict(first_pass_row=i,researcher=researcher,replacement_ids=rec_ids,
                           retained_outside_recommendations=moved,
                           disposition='Rebuilt from newly read passage; original claim is not carried forward automatically.' if new else 'Dropped: no qualifying recommendation in opened material or source unavailable.'))
    save('row-rebuild.json',ledger)
    save('coverage-counts.json',dict(required_roster=len(roster),with_admitted_recommendation=sum(bool(x['recommendation_ids']) for x in coverage),
                                    no_admitted_recommendation=sum(not x['recommendation_ids'] for x in coverage),
                                    first_pass_rows=len(ledger),replaced_rows=sum(bool(x['replacement_ids']) for x in ledger),
                                    dropped_rows=sum(not x['replacement_ids'] and not x['retained_outside_recommendations'] for x in ledger),
                                    retained_only_outside_recommendations=sum(not x['replacement_ids'] and bool(x['retained_outside_recommendations']) for x in ledger)))
    acquisitions=json.loads((RAW/'rebuild-2026-10-07/acquisition-log.json').read_text(encoding='utf-8'))
    checked=0
    for item in acquisitions:
        if item.get('path'):
            assert hashlib.sha256((ROOT/item['path']).read_bytes()).hexdigest()==item['sha256'], item['path']
            checked+=1
    markdown_links=[]
    for path in sorted(HERE.glob('*.md')):
        if path.name in {'REVIEW.md','REVIEW-2.md'}:
            continue
        for target in re.findall(r'\]\(([^)]+)\)',path.read_text(encoding='utf-8')):
            if target.startswith(('https://','http://')):
                continue
            target=target.split('#')[0]
            if not target:
                continue
            assert (path.parent/target).exists(), f'Broken Markdown link: {path.name}: {target}'
            markdown_links.append(dict(file=path.name,target=target))
    save('audit-checks.json',dict(status='Verified computation',acquisition_records=len(acquisitions),
                                acquisition_paths_hash_checked=checked,markdown_links_checked=len(markdown_links),
                                markdown_links=markdown_links,scope='File integrity and local links; attribution remains Exploratory.'))
    inventory=[]
    for base in [HERE,RAW]:
        for path in sorted(base.rglob('*')):
            if path.is_file() and path.name!='FILE-MANIFEST.json':
                inventory.append(dict(path=str(path.relative_to(ROOT)).replace('\\','/'),bytes=path.stat().st_size,
                                      sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                                      role='preserved historical/reviewer witness' if 'first-pass' in path.parts or 'review' in path.parts or 'review-2' in path.parts or path.name in {'REVIEW.md','REVIEW-2.md'}
                                           else 'local-only third-party/source acquisition' if base==RAW else 'active authored deliverable'))
    save('FILE-MANIFEST.json',inventory)
    print('Wrote coverage,33-row disposition, acquisition/link checks and two-directory inventory.')

if __name__=='__main__':
    main()
