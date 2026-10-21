"""Assemble review tables and compare the object-type repair with its saved input.

Usage: python -I finish_reviews.py --records-dir DIR --previous-dir DIR
  --checks-dir DIR --summary NEW_JSON --manual NEW_JSON --comparison NEW_JSON
  --cdli-cat CSV --cdli-atf ATF
"""
import argparse
from collections import Counter
import csv
import json
from pathlib import Path
import shutil

CORPORA=('sux-ur3','akk-sargonic','sux-sargonic','cuneiform-ur3-akkadian','cuneiform-language-unresolved')


def load(path):
    return [json.loads(line) for line in path.open(encoding='utf-8')]


def write(path,value):
    with path.open('x',encoding='utf-8') as f: f.write(json.dumps(value,ensure_ascii=False,indent=1)+'\n')


def jsonl(path,rows):
    with path.open('x',encoding='utf-8') as f:
        for r in rows: f.write(json.dumps(r,ensure_ascii=False)+'\n')


def main():
    ap=argparse.ArgumentParser()
    for key in ('records-dir','previous-dir','checks-dir','summary','manual','comparison','cdli-cat','cdli-atf'):
        ap.add_argument('--'+key,required=True,type=Path)
    a=ap.parse_args(); rows=[]; previous={}
    for name in CORPORA:
        rows.extend(load(a.records_dir/(name+'.jsonl')))
        previous.update({r['record_id']:r for r in load(a.previous_dir/(name+'.jsonl'))})
    changes,unexpected=Counter(),[]
    allowed={'object_kind','object_identity_status','object_identity_reason'}
    for r in rows:
        old=previous.pop(r['record_id'],None)
        if old is None: unexpected.append(dict(record_id=r['record_id'],reason='added')); continue
        keys={k for k in set(r)|set(old) if r.get(k)!=old.get(k)}
        changes.update(keys)
        if keys-allowed: unexpected.append(dict(record_id=r['record_id'],fields=sorted(keys-allowed)))
    unexpected.extend(dict(record_id=k,reason='removed') for k in previous)
    comparison=dict(records=len(rows),changes_by_field=dict(changes),unexpected_changes=len(unexpected),details=unexpected)
    write(a.comparison,comparison)
    assert not unexpected
    for source,target in [('language-conflicts.jsonl','cuneiform-language-conflicts.jsonl'),('period-review.jsonl','cuneiform-period-review.jsonl'),('object-review.jsonl','cuneiform-object-review.jsonl')]:
        dest=a.records_dir/target
        if dest.exists(): raise ValueError('review target already exists')
        shutil.copyfile(a.checks_dir/source,dest)
    identities=[r for r in rows if r.get('object_identity_status')]
    jsonl(a.records_dir/'cuneiform-identity-review.jsonl',identities)
    by_object={r['object_id']:r for r in rows if r['source']=='oracc-oakk'}
    gaps=[]
    for alt in load(a.records_dir/'cuneiform-edition-alternates.jsonl'):
        preferred=by_object.get(alt['object_id'])
        if preferred and not preferred['words'] and alt['group']['tokens']:
            gaps.append(dict(object_id=alt['object_id'],preferred_record_id=preferred['record_id'],preferred_completeness=preferred['completeness'],alternative=alt,
                reason='ORACC precedence retains an unreadable edition while CDLI supplies words'))
    jsonl(a.records_dir/'cuneiform-edition-gaps.jsonl',gaps)
    ambiguous={}
    with a.cdli_cat.open(encoding='utf-8-sig',newline='') as f:
        for meta in csv.DictReader(f):
            if 'Old Akkadian' in meta['period'] and not meta['period'].startswith('Old Akkadian'):
                identity='P'+meta['id_text'].zfill(6)
                ambiguous[identity]=dict(object_id=identity,metadata=meta,reason='period includes Old Akkadian as an alternative to another period',atf_lines=[])
    identity=None
    with a.cdli_atf.open(encoding='utf-8-sig') as f:
        for number,line in enumerate(f,1):
            if line.startswith('&'):
                identity=line[1:8]
                if identity in ambiguous: ambiguous[identity]['atf_file_line']=number
            if identity in ambiguous: ambiguous[identity]['atf_lines'].append(line.rstrip('\r\n'))
    jsonl(a.records_dir/'cuneiform-period-ambiguous.jsonl',ambiguous.values())
    packets=load(a.checks_dir/'packets.jsonl')
    notes={
        'P121084':'Catalogue envelope type now takes priority over generic tablet directive. The questioned office guide word remains a lexicon review item.',
        'P114450':'The office tag follows the editor N code and the questioned lexicon guide word; the contextual interpretation needs review.',
        'P462095':'ATF declares a composite text while the catalogue calls this a seal; physical identity remains unresolved.',
        'P462010':'ATF declares a composite text while the catalogue calls this a seal; physical identity remains unresolved.',
        'P225797':'ATF Akkadian declaration takes priority over the Sumerian catalogue label.',
        'P216946':'Catalogue bulla type now takes priority over generic tablet directive.',
        'P216947':'Catalogue bulla type now takes priority over generic tablet directive.',
        'P504813':'Blank provenience is null; two unlisted lexical spellings retain the required default-name assignment.',
        'P212829':'Sumerian token labels take priority over the Akkadian catalogue label.',
        'P456730':'Sumerian token labels take priority over the Akkadian catalogue label.',
        'P216811':'The preferred ORACC section has no readable words; its CDLI alternative is retained separately.'
    }
    manual=[]
    for packet in packets:
        r=packet['record']
        assert r['record_id'] in {x['record_id'] for x in rows}
        manual.append(dict(record_id=r['record_id'],corpus=r['corpus'],object_id=r['object_id'],source=r['source'],source_url=r.get('source_url'),
            status='archived-edition-compared-by-hand',text_and_lines='match after declared normalisation',
            unexplained_text_differences=0,notes=notes.get(r['object_id'],'No additional source discrepancy observed.')))
    write(a.manual,dict(seed='b-check',method='manual comparison of archived ORACC JSON and CDLI ATF with the normalised records',
        live_page_check='not performed; separate object-page URLs are outside the permitted acquisition URLs',
        reviewed_by='Codex GPT-6 family, exact model identifier not exposed; Codex API tool harness',
        records_by_corpus=dict(Counter(r['corpus'] for r in manual)),unexplained_text_differences=0,records=manual))
    summary=dict(records=len(rows),composite_identity_records=len(identities),composite_identity_by_corpus=dict(Counter(r['corpus'] for r in identities)),
        oracc_unreadable_cdli_readable_sections=len(gaps),oracc_unreadable_cdli_readable_objects=len({r['object_id'] for r in gaps}),
        language_conflicts=len(load(a.checks_dir/'language-conflicts.jsonl')),
        period_review_records=len(load(a.checks_dir/'period-review.jsonl')),
        ambiguous_period_catalogue_objects=len(ambiguous),
        object_review_records=len(load(a.checks_dir/'object-review.jsonl')),
        repaired_object_kind_records=changes['object_kind'],manual_records=len(manual),manual_text_differences=0)
    write(a.summary,summary)
    print(json.dumps(summary))


if __name__=='__main__': main()
