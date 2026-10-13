"""Independently check source pairing, lineage, complete frame and decision scope."""
import datetime
import hashlib
import html
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
RAW=ROOT/'data/raw/2026-10-12-transmission-hypothesis/texts'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    sys.stdout.reconfigure(encoding='utf8')
    target=HERE/'run-v1/CHECKS.json'
    if target.exists():raise FileExistsError(target)
    result=json.loads((HERE/'run-v1/RESULTS.json').read_text('utf8'))
    source=json.loads((HERE/'SOURCES-v2.json').read_text('utf8'))
    observations=json.loads((HERE/'OBSERVATIONS.json').read_text('utf8'))['observations']+json.loads((HERE/'LEXICAL-SOURCE-OBSERVATIONS.json').read_text('utf8'))['observations']
    paired=json.loads((RAW/'paired-passages-v2.json').read_text('utf8'))
    checks=[]

    def check(name,ok,detail=''):
        checks.append(dict(check_id=name,passed=bool(ok),detail=detail))

    for f,expected in result['input_hashes'].items():check(f+' retained input',sha(HERE/f)==expected)
    for f,expected in result['dependency_hashes'].items():check(f+' declared dependency',sha(ROOT/f)==expected)
    freeze=json.loads((HERE/'freeze-v1.json').read_text('utf8'))
    moment=datetime.datetime.fromisoformat(freeze['frozen_at_utc'])
    for row in freeze['files']:check(row['path']+' frozen',sha(ROOT/row['path'])==row['sha256'])
    paths=set();support=set();srcids={s['source_id'] for s in source['sources']}
    check('source ids unique',len(srcids)==len(source['sources'])==10)
    for row in source['sources']:
        check(row['source_id']+' scope',bool(row['reading_scope']) and bool(row['chronology_axes']))
        check(row['source_id']+' rights',row['rights_status'] in ['own-work','explicit-license','permission-recorded','rights-unverified','mixed-assets'] and row['redistribution']=='local-only')
        for w in row['witnesses']+row['derivatives']:
            p=ROOT/w['path'];paths.add(w['path'])
            check(row['source_id']+' witness '+p.name,p.exists() and sha(p)==w['sha256'])
            if w.get('role') not in ['failed_or_wrong_locator_witness','repository_metadata']:support.add(w['path'])
        for attempt in row['access_attempts']:
            check(row['source_id']+' capture '+attempt['witness_id'],sha(ROOT/attempt['acquisition_manifest'])==attempt['acquisition_manifest_sha256'])
            check(row['source_id']+' freeze order '+attempt['witness_id'],datetime.datetime.fromisoformat(attempt['retrieved_at_utc'])>=moment)
            if attempt.get('tls_verification') is False:check(row['source_id']+' transport caveat '+attempt['witness_id'],bool(attempt.get('transport_caveat')))
    main={x['pair_id']:x for x in paired['main_pairs']}
    expected={f'RV{b}.{h}.{n}' for b,h,maximum in [(9,112,4),(10,71,11),(10,101,12)] for n in range(1,maximum+1)}
    check('main complete',set(main)==expected and len(paired['main_pairs'])==27)
    for pair in paired['main_pairs']:
        ident=pair['pair_id'];b,h,n=map(int,ident[2:].split('.'))
        p=ROOT/pair['source_parent']['path']
        raw=html.unescape(re.sub(r'<[^>]+>','\n',p.read_text('utf8')))
        pattern=rf'RV_{b},{h:03d}\.{n:02d}([a-z])\s+([^\n]+)'
        recovered={m.group(1):m.group(2).strip() for m in re.finditer(pattern,raw)}
        saved={x['pada_label']:x['text'] for x in pair['sanskrit_padas']}
        check(ident+' independent Sanskrit locus',recovered==saved and bool(recovered))
        for parent in ['source_parent','translation_parent']:
            w=pair[parent];check(ident+' '+parent,sha(ROOT/w['path'])==w['sha256'] and w['path'] in support)
        check(ident+' English',bool(pair['translation']) and f'stanza{n}' in pair['translation_locus'])
    old=json.loads((RAW/'paired-passages-v1.json').read_text('utf8'))
    check('only Greek pairing repaired',all(paired[k]==old[k] for k in ['main_pairs','iranian_pairs','pali_pairs']) and paired['greek_pair']!=old['greek_pair'])
    check('prior pairing lineage',paired['prior_output_sha256']==sha(RAW/'paired-passages-v1.json'))
    ns={'t':'http://www.tei-c.org/ns/1.0'}
    groot=ET.parse(RAW/'odyssey-greek-v2.bin').getroot();eroot=ET.parse(RAW/'odyssey-english-corrected-v3.bin').getroot()
    gb=next(x for x in groot.findall('.//t:div',ns) if x.get('n')=='17')
    eb=next(x for x in eroot.findall('.//t:div',ns) if x.get('n')=='17')
    gl=[dict(line=int(x.get('n')),text=' '.join(' '.join(x.itertext()).split())) for x in gb.findall('.//t:l',ns) if 382<=int(x.get('n','0'))<=386]
    ec=next(x for x in eb.findall('.//t:div',ns) if x.get('n')=='380')
    et=' '.join(' '.join(ec.itertext()).split())
    check('Greek book-qualified lines',paired['greek_pair']['source_lines']==gl and len(gl)==5)
    check('Greek book-qualified translation',paired['greek_pair']['translation']==et and all(t in et for t in ['prophet','healer','builder','minstrel']))
    check('wrong old Greek alignment detected',not all(t in old['greek_pair']['translation'] for t in ['prophet','healer','builder','minstrel']))
    pl=json.loads((RAW/'dn1-pali-v2.bin').read_text('utf8'));en=json.loads((RAW/'dn1-sujato-v2.bin').read_text('utf8'))
    keys=[]
    for group in paired['pali_pairs']:
        for seg in group['segments']:
            k=seg['segment_id'];keys.append(k)
            check(k+' direct Pali-English pairing',pl[k]==seg['source_text'] and en[k]==seg['translation'])
    check('Pali complete groups',len(paired['pali_pairs'])==7 and len(keys)==31 and len(set(keys))==31)
    check('Iranian complete loci',{x['pair_id'] for x in paired['iranian_pairs']}=={f'Y9.{n}' for n in range(1,9)}|{f'V3.{n}' for n in range(23,34)})
    groups={x.get('translation_group',x['pair_id']) for x in paired['iranian_pairs']}
    check('Iranian grouped translations retained',len(groups)==17,'19 source units;17 translation groups because26–27 and28–29 share English groups')
    lex=json.loads((HERE/'LEXICAL-RESULTS.json').read_text('utf8'))
    check('original lexical frame fixed',len(lex['original_lemmas'])==8 and 'bīja-postselection' not in lex['original_lemmas'])
    check('pasture false positive excluded','RV10.101.9' not in lex['matches']['yava'] and not lex['matches']['yava'])
    check('plow and seed applicability',lex['matches']['sīra']==['RV10.101.3','RV10.101.4'] and lex['matches']['bīja-postselection']==['RV10.101.3'] and not lex['matches']['lāṅgala'])
    ids={x['observation_id'] for x in observations};check('observation ids unique',len(ids)==len(observations)==43)
    pairids=set(main)|{x['pair_id'] for x in paired['iranian_pairs']}|{paired['greek_pair']['pair_id']}|{x['pair_id'] for x in paired['pali_pairs']}
    for row in observations:
        check(row['observation_id']+' source join',set(row['source_ids'])<=srcids and bool(row.get('locus',row.get('loci'))))
        if row.get('pair_ids'):check(row['observation_id']+' pair join',set(row['pair_ids'])<=pairids and row['paired_witness_sha256']==sha(RAW/'paired-passages-v2.json'))
    ro=json.loads((ROOT/'experiments/2026-10-12-transmission-hypothesis/review/observations-v2.json').read_text('utf8'))['observations']
    mo=json.loads((ROOT/'experiments/2026-10-12-transmission-hypothesis/material/observations.json').read_text('utf8'))['observations']
    external={f'review/{x["observation_id"]}' for x in ro}|{f'material/{x["observation_id"]}' for x in mo}
    allowed={'favored-for-a-component','compatible','conditionally-weakened','unresolved','excluded-by-specific-evidence'}
    for comp in result['component_results']:
        check(comp['comparison_id']+' complete rivals',set(comp['rivals'])=={'R1','R2','R3','R4','R5'} and all(x['status'] in allowed for x in comp['rivals'].values()))
        references=set(comp['text_observations']+comp.get('controls',[])+comp.get('material_observations',[]))
        check(comp['comparison_id']+' observation joins',references<=ids|external)
        check(comp['comparison_id']+' redaction scope',comp['earlier_text_reorganization_observed'] is False and bool(comp['endpoint_observed']))
    material_ids={x['observation_id'] for x in mo}
    for join in result['material_join_results']:
        check(join['join_id']+' source joins',set(join['text_observations'])<=ids and set(join.get('material_observations',[]))<=material_ids)
        check(join['join_id']+' testable limitation',bool(join['reason']) and bool(join['needed']))
    payload=b'\0'.join(p.encode('utf8') for p in sorted(paths))+b'\0'
    ignored=subprocess.run(['git','check-ignore','--no-index','-z','--stdin'],input=payload,cwd=ROOT,capture_output=True)
    got={p.decode('utf8') for p in ignored.stdout.split(b'\0') if p}
    check('all source witnesses ignored',paths<=got and ignored.returncode in [0,1])
    report=dict(status='pass' if all(x['passed'] for x in checks) else 'fail',scope='Independent source/locus reconstruction, hashes, complete frame and categorical-decision joins; not empirical origin validation',checks=len(checks),passed=sum(x['passed'] for x in checks),checker_sha256=sha(Path(__file__)),result_sha256=sha(HERE/'run-v1/RESULTS.json'),results=checks)
    target.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({k:report[k] for k in ['status','checks','passed']}))
    if report['status']!='pass':
        print(json.dumps([x for x in checks if not x['passed']],ensure_ascii=False,indent=2))
        raise SystemExit(1)


if __name__=='__main__':main()
