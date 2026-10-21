"""Validate every record against the cuneiform schema requirements independently.

Usage: python -I validate_outputs.py --records-dir DIR --counts JSON
  --schema SCHEMA_MD --out NEW_JSON
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import unicodedata

CORPORA=('sux-ur3','akk-sargonic','sux-sargonic','cuneiform-ur3-akkadian','cuneiform-language-unresolved')
REQUIRED={'record_id','corpus','source','source_locator','object_id','object_kind','genre','aliases','site','language','language_basis','script','rights','legend_as_printed','lines','line_division_basis','words','members','units','word_units','line_of_word','tags','tag_source','completeness','reading_doubtful','transcription','gold'}
TAGS={'NAME','DIVINE','PLACE','TITLE','KIN','NUMBER','GRAM','OTHER'}
KINDS={'seal-die','cylinder-seal','stamp-seal','ring','coin','clay-sealing','sealed-tablet','sealed-envelope','bulla','other'}
COMPLETE={'complete','restored','damaged-edge','damaged-internal','illegible','no-legend'}


def strings(value):
    if isinstance(value,str): yield value
    elif isinstance(value,list):
        for v in value: yield from strings(v)
    elif isinstance(value,dict):
        for k,v in value.items(): yield k; yield from strings(v)


def main():
    ap=argparse.ArgumentParser()
    for key in ('records-dir','counts','schema','out'): ap.add_argument('--'+key,required=True,type=Path)
    a=ap.parse_args(); ids=set(); checks=Counter(); errors=[]; totals={}
    counts=json.loads(a.counts.read_text(encoding='utf-8'))
    def check(test,name,r):
        checks[name]+=1
        if not test: errors.append(dict(record_id=r.get('record_id'),check=name))
    for corpus in CORPORA:
        rows=[]
        with (a.records_dir/(corpus+'.jsonl')).open(encoding='utf-8') as f:
            for line in f:
                r=json.loads(line); rows.append(r)
                check(REQUIRED<=r.keys(),'required_fields',r)
                check(r['record_id'] not in ids,'unique_record_id',r); ids.add(r['record_id'])
                check(bool(re.fullmatch(r'P\d{6}',r['object_id'])),'physical_object_id',r)
                check(r['corpus']==corpus,'corpus_matches_file',r)
                check(isinstance(r['source_locator'],dict) and bool(r['source_locator']),'source_locator',r)
                check(isinstance(r['aliases'],list) and all(isinstance(x,str) for x in r['aliases']),'aliases',r)
                check(r['units']==[u for us in r['word_units'] for u in us],'concatenated_units',r)
                check(r['words']==[w for ln in r['lines'] for w in ln],'flattened_lines',r)
                n=len(r['words'])
                check(all(len(r[k])==n for k in ('word_units','line_of_word','members','tags','tag_source','gold')),'word_array_lengths',r)
                check(all(isinstance(x,int) and 0<=x<len(r['lines']) for x in r['line_of_word']),'line_indices',r)
                expected=[i for i,line_words in enumerate(r['lines']) for _ in line_words]
                check(expected==r['line_of_word'],'line_membership',r)
                check(all(len(m)==len(t)==len(s) for m,t,s in zip(r['members'],r['tags'],r['tag_source'])),'member_array_lengths',r)
                check(all(t in TAGS for ts in r['tags'] for t in ts),'tag_values',r)
                check(all(t in {'editor-pos','editor-translation','lexicon','default-name'} for ts in r['tag_source'] for t in ts),'tag_source_values',r)
                check(r['object_kind'] in KINDS and r['genre'] in {'seal','sealing','coin'},'object_values',r)
                check(r['completeness'] in COMPLETE,'completeness_values',r)
                check(r['line_division_basis'] in {'atf','edition','none'},'line_basis_values',r)
                check(r['site'] is not None or bool(r.get('site_unknown_reason')),'null_site_reason',r)
                check(r['language_basis'] in {'editor','token-language','catalogue'},'language_basis',r)
                check(isinstance(r['language'],str) and bool(r['language']),'language_present',r)
                check(isinstance(r['reading_doubtful'],bool),'doubt_type',r)
                check(r['transcription'].get('method')=='digital-edition' and bool(r['transcription'].get('by')),'transcription',r)
                check(all(unicodedata.is_normalized('NFC',s) for s in strings(r)),'unicode_nfc',r)
                check(all(isinstance(w,str) for w in r['words']) and all(isinstance(u,str) for u in r['units']),'unit_types',r)
                if corpus in CORPORA[:3]: check(r['language'] in {'Sumerian','Akkadian','mixed'},'corpus_language',r)
        totals[corpus]=len(rows)
        expected=counts['corpora'].get(corpus,counts['outside_corpora'].get(corpus))
        check(expected['records']==len(rows),'record_counts',dict(record_id=corpus))
        seq={tuple(r['units']) for r in rows}
        check(expected['distinct_sign_unit_sequences']==len(seq),'distinct_sign_counts',dict(record_id=corpus))
        check(expected['distinct_sequences_at_least_two_signs']==sum(len(s)>=2 for s in seq),'two_sign_counts',dict(record_id=corpus))
        check(expected['distinct_sequences_at_least_two_words']==len({tuple(r['units']) for r in rows if len(r['words'])>=2}),'two_word_counts',dict(record_id=corpus))
    result=dict(records_by_file=totals,records=sum(totals.values()),checks=dict(checks),total_assertions=sum(checks.values()),
        failures=len(errors),errors=errors,schema_sha256=hashlib.sha256(a.schema.read_bytes()).hexdigest())
    with a.out.open('x',encoding='utf-8') as f: f.write(json.dumps(result,indent=1)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in {'checks','errors'}}))
    if errors: raise SystemExit(1)


if __name__=='__main__': main()
