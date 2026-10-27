import sys,re,html,unicodedata,json
from pathlib import Path
from prepare import *
sys.path.insert(0,str(ROOT/'experiments/2026-10-22-lexical-source-review/code'))
import source_blocks as sb
sys.path.insert(0,str(ROOT/'experiments/2026-10-21-rebus-base-rate/code'))
import parse_dedr as dedr
def norm(x):return unicodedata.normalize('NFC',x)
def witness(path,block,span):return dict(logical_path=path.relative_to(ROOT).as_posix(),physical_path=str(path.resolve()),sha256=sha(path),character_span=list(span),raw_html=block,text=sb.plain(block))
def main():
 selected=read(RAW/'case-selection-v1.json');tl=rows(ROOT/'data/raw/2026-10-21-rebus-base-rate/derived-v1/tamil-lex-entries.jsonl');de=rows(ROOT/'data/raw/2026-10-21-rebus-base-rate/derived-v1/dedr-entries.jsonl')
 result=[]
 for case in selected:
  r=case['entry'];p=ROOT/r['source']['logical_path'];blocks=sb.exact_winslow_blocks(p.read_text(encoding='utf8'),r)
  assert len(blocks)==1
  queries={r['translit_plain']};queries.update([r['root']] if r.get('root') else [])
  queries.update(r['members'])
  for c in r['increment_candidates']:queries.update(c['lemma_candidates'])
  for s in r['lexicon_boundary_sources']:queries.update(s['members'])
  if r['translit_plain']=='murukkañcettal':queries.add('murukku')
  lex=[]
  for t in tl:
   if t['translit'] not in queries and t['head']!=r['head']:continue
   path=ROOT/f'data/raw/2026-10-21-rebus-base-rate/sources-v1/tamil-lex/page-{t["page"]:05d}.html'
   witnesses=[]
   for m in re.finditer(r'<div>\s*(.*?)</div>',path.read_text(encoding='utf8'),re.S):
    if any(x['head']==t['head'] and x['hom']==t['hom'] and x['translit']==t['translit'] for x in sb.winslow.parse_tamil_lex.parse_page('<div>'+m.group(1)+'</div>',t['page'])):
     witnesses.append(witness(path,m.group(1),m.span()))
   assert len(witnesses)==1,(t['head'],t['hom'])
   lex.append(dict(entry=t,witness=witnesses[0]))
  etym=[]
  for d in de:
   groups=[g for g in d['groups'] if g['lang']=='Ta' and any(norm(form) in queries for form in g['forms'])]
   if not groups:continue
   path=ROOT/f'data/raw/2026-10-21-rebus-base-rate/sources-v1/dedr/page-{d["page"]:05d}.html'
   hits=[]
   for m in dedr.ENTRY_RE.finditer(path.read_text(encoding='utf8')):
    num=html.unescape(m.group(1)).strip();num=('a'+num) if d['page']>=509 else num
    if num==d['num']:hits.append(witness(path,m.group(0),m.span()))
   assert len(hits)>=1,d['num']
   etym.append(dict(number=d['num'],page=d['page'],matched_tamil_groups=groups,languages=d['langs'],witnesses=hits))
  result.append(dict(case_id=case['case_id'],stratum=case['stratum'],entry=r,
   winslow_witness=dict(blocks[0],logical_path=p.relative_to(ROOT).as_posix(),physical_path=str(p.resolve()),sha256=sha(p)),
   exact_queries=sorted(queries),lexicon_entries=lex,dedr_entries=etym))
 save(RAW/'source-packets-v2.json',result)
 for c in result:
  print(json.dumps(dict(case_id=c['case_id'],form=c['entry']['translit_plain'],winslow=c['winslow_witness']['text'],
    lexicon=[dict(form=t['entry']['translit'],hom=t['entry']['hom'],page=t['entry']['page'],text=t['witness']['text']) for t in c['lexicon_entries']],
    dedr=[dict(number=d['number'],page=d['page'],groups=d['matched_tamil_groups'],text=' '.join(w['text'] for w in d['witnesses'])) for d in c['dedr_entries']]),ensure_ascii=False))
if __name__=='__main__':main()
