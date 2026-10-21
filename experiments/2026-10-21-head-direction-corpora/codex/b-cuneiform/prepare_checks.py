"""Prepare independent archived-edition packets and metadata review tables.

Usage: python -I prepare_checks.py --sample JSONL --ur3-archive ZIP
  --oakk-archive ZIP --cdli-atf ATF --cdli-cat CSV --records-dir DIR --out NEW_DIR

The packet is prepared mechanically. A separate manual review records what was
checked. No network request is made and no normaliser function is imported.
"""
import argparse
from collections import Counter
import csv
import json
from pathlib import Path, PurePosixPath, PureWindowsPath
import re
import zipfile


def nodes(items):
    for item in items:
        yield item
        yield from nodes(item.get('cdl',[]))


def source_oracc(archive, row, cat):
    loc=row['source_locator']; data=json.loads(archive.read(loc['entry']))
    target=loc['seal_section']; active=False; objnum=0; lines=[]; forms=[]; pos=[]; raw_words=[]
    for n in nodes(data.get('cdl',[])):
        if n.get('node')=='d':
            if n.get('type')=='object':
                objnum+=1; active=target==f"{n.get('subtype','object')}:{objnum}"
            if n.get('type')=='surface':
                if target.startswith('seal:'): active=target=='seal:'+n.get('ref','')
            if active: lines.append({k:v for k,v in n.items() if k!='cdl'})
        if n.get('node')=='l' and active:
            f=n.get('f',{}); forms.append(f.get('form',n.get('frag',''))); pos.append(f.get('pos'))
            lines.append(dict(word=n.get('frag',f.get('form','')),line_ref=n.get('ref'),pos=f.get('pos'),language=f.get('lang'),citation=f.get('cf'),guide=f.get('gw')))
            raw_words.append(dict(f=f,frag=n.get('frag')))
    return dict(edition_lines=lines,source_forms=forms,forms_equal=forms==row['words'],source_gold=pos,gold_equal=pos==row['gold'],
                catalogue=cat['members'].get(data['textid'],{}),raw_words=raw_words)


def write_jsonl(path,rows):
    with path.open('x',encoding='utf-8') as f:
        for r in rows: f.write(json.dumps(r,ensure_ascii=False)+'\n')


def main():
    ap=argparse.ArgumentParser()
    for key in ('sample','ur3-archive','oakk-archive','cdli-atf','cdli-cat','records-dir','out'):
        ap.add_argument('--'+key,required=True,type=Path)
    a=ap.parse_args(); a.out.mkdir(parents=True,exist_ok=False)
    sample=[json.loads(line)['record'] for line in a.sample.open(encoding='utf-8')]
    archives={}
    for key,path in [('sumerian-ur3-v1',a.ur3_archive),('oracc-oakk',a.oakk_archive)]:
        z=zipfile.ZipFile(path)
        for name in z.namelist():
            if PurePosixPath(name).is_absolute() or PureWindowsPath(name).drive or '..' in PurePosixPath(name.replace('\\','/')).parts: raise ValueError('unsafe archive member')
        cat=json.loads(z.read(next(n for n in z.namelist() if n.endswith('/catalogue.json'))))
        archives[key]=(z,cat)
    wanted={r['object_id'] for r in sample if r['source']=='cdli-data'}
    blocks={}; current=None; block=[]
    with a.cdli_atf.open(encoding='utf-8-sig') as f:
        for line in f:
            if line.startswith('&'):
                if current in wanted: blocks[current]=block
                current=line[1:8]; block=[line.rstrip('\r\n')]
            else: block.append(line.rstrip('\r\n'))
        if current in wanted: blocks[current]=block
    meta={}
    with a.cdli_cat.open(encoding='utf-8-sig',newline='') as f:
        for row in csv.DictReader(f):
            identity='P'+row['id_text'].zfill(6)
            if identity in wanted: meta[identity]=row
    packet=[]
    for r in sample:
        if r['source'] in archives:
            z,cat=archives[r['source']]; source=source_oracc(z,r,cat)
        else: source=dict(edition_lines=blocks.get(r['object_id'],[]),catalogue=meta.get(r['object_id'],{}))
        packet.append(dict(record=r,source=source))
    write_jsonl(a.out/'packets.jsonl',packet)
    rows=[]
    for name in ('sux-ur3','akk-sargonic','sux-sargonic','cuneiform-ur3-akkadian','cuneiform-language-unresolved'):
        rows.extend(json.loads(line) for line in (a.records_dir/(name+'.jsonl')).open(encoding='utf-8'))
    conflicts=[]
    for r in rows:
        declared=r.get('source_language','').lower()
        majority=r.get('majority_language','')
        edition=r.get('atf_edition_language')
        if (declared=='akkadian' and majority=='Sumerian') or (declared=='sumerian' and majority=='Akkadian') or (edition not in (None,'sux','akk') and edition):
            conflicts.append(r)
    write_jsonl(a.out/'language-conflicts.jsonl',conflicts)
    ur3_ids={r['object_id'] for r in rows if r['period']=='Ur III'}
    period_review=[r for r in rows if r['period']=='Old Akkadian' and (r['object_id'] in ur3_ids or re.search(r'Šulgi|Amar-Suen|Šu-Suen|Ibbi-Suen|Ur-Namma',r.get('date_as_printed','')))]
    write_jsonl(a.out/'period-review.jsonl',period_review)
    object_review=[r for r in rows if re.search(r'Fake|cast|Reproduction|\?',r.get('source_object_type',''),re.I)]
    write_jsonl(a.out/'object-review.jsonl',object_review)
    summary=dict(sample_records=len(packet),oracc_source_forms_equal=sum(p['source'].get('forms_equal',False) for p in packet),
        oracc_source_gold_equal=sum(p['source'].get('gold_equal',False) for p in packet),sample_sources=dict(Counter(r['source'] for r in sample)),
        language_conflict_records=len(conflicts),period_review_records=len(period_review),object_review_records=len(object_review),
        period_review_objects=len({r['object_id'] for r in period_review}))
    (a.out/'summary.json').write_text(json.dumps(summary,indent=1)+'\n',encoding='utf-8')
    print(json.dumps(summary))


if __name__=='__main__': main()
