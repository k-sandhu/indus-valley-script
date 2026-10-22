"""Inspect local acquisition metadata without executing acquired content. Run with python -I."""
import datetime as dt
import hashlib
import json
from pathlib import Path

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
RAW=ROOT/'data/raw/2026-10-21-town-orientations-verification/dating'
now=dt.datetime.now(dt.timezone.utc).isoformat()

# The failed disk-full attempt created an empty file before metadata could be written.
partial=RAW/'navinal2025.pdf'
record=partial.with_name(partial.name+'.acquisition.json')
if partial.exists() and not record.exists():
    data=partial.read_bytes()
    record.write_text(json.dumps(dict(path=partial.relative_to(ROOT).as_posix(),
        url='https://www.frontiersin.org/journals/environmental-archaeology/articles/10.3389/fearc.2025.1517351/pdf',
        retrieved_utc=dt.datetime.fromtimestamp(partial.stat().st_mtime,dt.timezone.utc).isoformat(),
        retrieval_time_basis='failed attempt file modification time; acquisition metadata recovered after the write error',
        byte_count=len(data),sha256=hashlib.sha256(data).hexdigest(),content_type=None,
        rights_notice_observed='No content written; no licence notice in this failed file. Publisher article was marked open access.',
        status='failed: disk full; empty local artifact; not source evidence',handling='local-only; never executed'),indent=2)+'\n',encoding='utf-8')

observed={
 'khirsara2017.pdf':'p. 1: Creative Commons Attribution; copyright Pokharia et al. 2017.',
 'navinal2025-retry.pdf':'p. 1: copyright Abhayan et al. 2025; Creative Commons Attribution (CC BY).',
 'bhirrana2016.html':'Copyright and License information: copyright Macmillan Publishers Limited 2016; Creative Commons Attribution 4.0.',
 'puratattva34-full.pdf':'PDF p. 4: copyright Indian Archaeological Society, New Delhi, 2004.',
 'kunal2008.pdf':'PDF pp. 2-3: Puratattva 24 (1993-94); copyright Indian Archaeological Society 1994. Not the Kunal report suggested by transport filename.',
 'banawali-asi.pdf':'Title/copyright pages identify ASI Inventory of Monuments and Sites of National Importance, Chandigarh Circle; no open licence observed.',
 'kotada2024-mpg-rest.pdf':'Publisher states Open Access; institutional PDF is the article. Rights remain as its publisher notice; local-only copy.',
 'dholavira2015.pdf':'ASI preliminary report; archive transport copy. No open redistribution permission established.',
 'rangpur1963.pdf':'Ancient India 18-19, ASI; no open reuse licence observed.',
}
checks=[]
for f in sorted(RAW.glob('*.acquisition.json')):
    a=json.loads(f.read_text(encoding='utf-8'))
    p=(ROOT/a['path']).resolve()
    if not p.is_relative_to(RAW.resolve()): raise ValueError('Acquisition path outside owned raw directory')
    b=p.read_bytes()
    typ=('empty' if not b else 'PDF' if b.lstrip().startswith(b'%PDF-') else
         'PNG' if b.startswith(b'\x89PNG\r\n\x1a\n') else
         'HTML or text' if b.lstrip()[:200].lower().startswith((b'<!doctype',b'<html',b'<?xml')) or b'<html' in b[:1000].lower() else 'other bytes')
    expected=p.suffix.lower() in ('.pdf','.png','.doc','.docx')
    wrapper=expected and typ not in ('PDF','PNG')
    checks.append(dict(path=a['path'],metadata_path=f.relative_to(ROOT).as_posix(),
        byte_count_matches=len(b)==a['byte_count'],sha256_matches=hashlib.sha256(b).hexdigest()==a['sha256'],
        actual_content_class=typ,unexpected_wrapper_or_empty=wrapper,
        use_status='not the requested source; excluded as evidence' if wrapper else 'inspect bibliography for evidence use',
        rights_notice_observed_on_review=observed.get(p.name,'No additional rights notice established during this review; the acquisition record retains the access-route observation.')))

derivatives=[dict(path=(RAW/'harappa2005-table2.png').relative_to(ROOT).as_posix(),
    kind='locally rendered table image, not a network download',
    parent_path='data/raw/2026-10-12-transmission-hypothesis/material/acquisition-v2/kenoyer2005-harappa.pdf',
    locator='Meadow and Kenoyer 2005, Excavations at Harappa 2000-2001: New Insights on Chronology and City Organization, p. 209, Table 2',
    sha256=hashlib.sha256((RAW/'harappa2005-table2.png').read_bytes()).hexdigest())]
for p,parent,page in [
 ('kotada2024-page8.png','data/raw/2026-10-21-town-orientations-verification/dating/kotada2024-mpg-rest.pdf','Chakraborty et al. 2024, p. 8, Fig. 5'),
 ('farmana2011-page847.png','data/raw/2026-10-21-post-catalogue-finds/run1a/sources/farmana-2006-08/Excavations at Farmana, 2006-08 - V Shinde et al.pdf','Paleo-Labo AMS dating group 2011, p. 833, Table 13.2'),
 ('farmana2011-page848.png','data/raw/2026-10-21-post-catalogue-finds/run1a/sources/farmana-2006-08/Excavations at Farmana, 2006-08 - V Shinde et al.pdf','Paleo-Labo AMS dating group 2011, p. 834, Table 13.2')]:
    x=OUT/'review'/p
    derivatives.append(dict(path=x.relative_to(ROOT).as_posix(),parent_path=parent,locator=page,
        kind='locally rendered page image, not a network download',sha256=hashlib.sha256(x.read_bytes()).hexdigest()))
result=dict(checked_utc=now,acquisition_checks=checks,local_derivatives=derivatives,
            all_hashes_and_sizes_match=all(x['byte_count_matches'] and x['sha256_matches'] for x in checks))
(OUT/'acquisition-review.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(acquisitions=len(checks),unexpected_wrappers_or_empty=sum(x['unexpected_wrapper_or_empty'] for x in checks),all_hashes_and_sizes_match=result['all_hashes_and_sizes_match'])))
