"""Recover PDF example headings, primary glyph rows and explicit object aliases.

Run from repository root. Full author transcriptions/glosses and corpus joins are
local-only. Entry records distinguish structural examples from reading attempts.
"""
from pathlib import Path
import collections, hashlib, json, re, sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from pdf_followup import ROOT, OWN, RAW, OUT, WORK, read, write, sha

def canonical(s):
    m=re.fullmatch(r'(M|H|L|K|C|B|Sktd|Blk|Ad|Ns|Krs)-0*(\d+)',s)
    return f'{m[1]}-{int(m[2])}' if m else s

def brackets(s):
    stack=[]; result=[]
    for i,c in enumerate(s):
        if c=='[':stack.append(i)
        elif c==']' and stack:
            start=stack.pop()
            if not stack:result.append(s[start+1:i])
    if stack:result.append(s[stack[0]+1:])
    return result

def main():
    assert sha(OUT/'mapping-v1-frozen.json')==read(OUT/'mapping-freeze.json')['sha256']
    if (OUT/'reading-coverage-v2.json').exists():raise SystemExit('Refusing existing reading endpoint')
    catalog=read(WORK/'sign-catalogue-v2.json');occ=read(WORK/'image-occurrences-v2.json')
    digestid={r['pixel_digest']:r['sign_id'] for r in catalog if 'pixel_digest' in r}
    for r in catalog:
        if r.get('pixel_digests') and len(r['pixel_digests'])==1:digestid[r['pixel_digests'][0]]=r['sign_id']
    # Additional drawings get stable neutral IDs; no inferred phonetic value.
    unknown={d:f'U{i+1:03d}' for i,d in enumerate(sorted({o['pixel_digest'] for o in occ}-set(digestid)))}
    digestid.update(unknown)
    write(WORK/'unassigned-image-catalogue.json',[
      {'sign_id':sid,'pixel_digest':d,'first_occurrence':next(o for o in occ if o['pixel_digest']==d)} for d,sid in unknown.items()])
    lines=[]
    for page in range(1,260):
        for l in read(WORK/f'pages/page-{page:03d}-layout.json'):
            if l['text'].strip():lines.append(dict(l,page=page,pos=page*1000+l['bbox'][1]))
    lines.sort(key=lambda l:(l['page'],round(l['bbox'][1]/3),l['bbox'][0]))
    headings=[]
    for i,l in enumerate(lines):
        m=re.match(r'^\s*(MH\s*\d+|ICIT\s*\d+)\b',l['text'])
        if m and l['bbox'][0]<90 and 16<=l['page']<=249:
            headings.append({'line':i,'primary':re.sub(r'\s+','',m[1]),'page':l['page'],'bbox':l['bbox'],'pos':l['pos']})
    observations=[]
    for hindex,h in enumerate(headings):
        limit=headings[hindex+1]['pos'] if hindex+1<len(headings) else 250000
        group=[l for l in lines if h['pos']-5<=l['pos']<limit-5]
        # A following value section terminates the preceding example.
        stop=next((l['pos'] for l in group[1:] if l['text'].strip().startswith(('a. Comments:','b. Inscriptions:','V. ','VI. ','VII. '))),limit)
        group=[l for l in group if l['pos']<stop]
        group.sort(key=lambda l:(l['page'],round(l['bbox'][1]/5),l['bbox'][0]))
        text=' '.join(l['text'].strip() for l in group)
        pairs=brackets(text)
        aliasgroups=[b for b in pairs if re.match(r'^\s*(?:(?:MH|ICIT)\s*\d+\s*/|(?:M|H|L|K|C|B|Sktd|Blk|Ad|Ns|Krs)\s*-\s*\d+)',b)]
        code_pattern=r'\b(M|H|L|K|C|B|Sktd|Blk|Ad|Ns|Krs)\s*-\s*(\d+)\b'
        # Only explicit catalogue blocks or slash-separated primary headings.
        aliastext=' '.join(aliasgroups)+' '+lines[h['line']]['text']
        cisi=sorted({canonical(f'{m[1]}-{m[2]}') for m in re.finditer(code_pattern,aliastext)})
        mh_aliases=sorted({f'MH{m[1]}' for m in re.finditer(r'\bMH\s*(\d+)\b',aliastext)})
        icit_aliases=sorted({f'ICIT{m[1]}' for m in re.finditer(r'\bICIT\s*(\d+)\b',aliastext)})
        # Glyphs between primary label and the first caption text on its baseline.
        baseline=[l for l in group if abs(l['bbox'][1]-h['bbox'][1])<4 and l['bbox'][0]>h['bbox'][0]+10]
        right=min((l['bbox'][0] for l in baseline if '[' in l['text']),default=540)
        glyphs=[o for o in occ if o['pdf_page']==h['page'] and
                abs(o['bbox'][3]-h['bbox'][3])<9 and
                o['bbox'][0]>=h['bbox'][2]-2 and o['bbox'][2]<=right+3]
        glyphs.sort(key=lambda o:o['bbox'][0])
        # Tight primary-line extraction excludes drawings embedded in later commentary.
        seq=[digestid[o['pixel_digest']] for o in glyphs]
        captions=[b for b in pairs if b not in aliasgroups]
        def reading_caption(b):
            if '/' not in b:return False
            left=b.split('/',1)[0].strip()
            if any(x in left.lower() for x in ['seal','dholavira','karanpura','altyn','tell ','see ','note ','line ','above','preced','found','also ','important','likely']):return False
            if any(c in left for c in '‘’\";'):return False
            return len(left)<110 and bool(re.search('[A-Za-z]',left))
        reading=next((b for b in captions if reading_caption(b)),None)
        display=reading.split('/',1)[0].strip() if reading else None
        gloss=reading.split('/',1)[1].strip() if reading else None
        isattempt=bool(reading) or (86<=h['page']<=226 and bool(glyphs))
        uncertain=bool(re.search(r'unclear|unreadable|effaced|illegible|uncertain|unattested|hypothetical|\*',text,re.I))
        status='derivation' if h['page']<79 else ('illustration' if h['primary'].startswith('MH') else 'ICIT-first illustration; historical check status unresolved')
        observations.append({'reading_id':f'R{len(observations)+1:04d}','source_page':h['page'],
          'primary_label':h['primary'],'primary_bbox':h['bbox'],'source_kind':status,
          'is_reading_attempt':isattempt,'unclear_or_unattested_flag':uncertain,
          'cisi_aliases':cisi,'mh_aliases':mh_aliases,'icit_aliases':icit_aliases,
          'sign_sequence_visual_ltr':seq,'sign_sequence_assumed_rtl':list(reversed(seq)),
          'primary_glyphs':glyphs,'proposed_reading':display,'proposed_gloss':gloss,
          'field_assignment':'Not individually labelled in this entry; source classification pending explicit field boundary',
          'caption_blocks':captions,'source_text':text,'complete_table18_sequence':bool(seq) and all(s.startswith('B') and int(s[1:])<=65 for s in seq),
          'attachment_rule':'Primary baseline, between catalogue label and caption bracket; later prose drawings excluded'})
    faces=[json.loads(l) for l in (ROOT/'data/normalized/lipi_observed_faces.jsonl').read_text(encoding='utf-8').splitlines()]
    bycisi=collections.defaultdict(list)
    for f in faces:
        code=f.get('source_cisi')
        if isinstance(code,str):bycisi[canonical(code)].append(f)
    for r in observations:
        joins=[f for c in r['cisi_aliases'] for f in bycisi[c]]
        r['joined_record_ids']=sorted({f['record_id'] for f in joins})
        r['joined_object_family_ids']=sorted({f['object_family_id'] for f in joins})
        r['join_status']='ambiguous aliases' if len(r['cisi_aliases'])>1 else ('joined explicit CISI' if joins else 'unjoined')
    write(WORK/'reading-inventory-v2.json',observations)
    # Identifiers and own coverage annotations can be tracked; full readings stay raw.
    ownrows=[{k:r[k] for k in ['reading_id','source_page','primary_label','source_kind','is_reading_attempt',
        'unclear_or_unattested_flag','cisi_aliases','mh_aliases','icit_aliases','join_status','complete_table18_sequence']}|
      {'glyph_count':len(r['sign_sequence_visual_ltr']),'table18_glyph_count':sum(s.startswith('B') and int(s[1:])<=65 for s in r['sign_sequence_visual_ltr']),
       'joined_objects':len(r['joined_object_family_ids'])} for r in observations]
    write(OUT/'reading-index-v2.json',{'status':'Exploratory','rows':ownrows})
    attempts=[r for r in observations if r['is_reading_attempt']]
    x={'status':'Exploratory','scope':'All leading primary MH/ICIT entries on pages 16–249, with primary-line glyph extraction. Parenthetical structural-table labels and additional inscription lines are supplementary witnesses, not silently promoted to readings.',
       'primary_entries':len(observations),'unique_primary_labels':len({r['primary_label'] for r in observations}),
       'reading_attempt_entries':len(attempts),'derivation_entries':sum(r['source_page']<79 for r in observations),
       'entries_with_primary_glyphs':sum(bool(r['sign_sequence_visual_ltr']) for r in observations),
       'complete_table18_entries':sum(r['complete_table18_sequence'] for r in observations),
       'attempts_with_explicit_transcription':sum(r['proposed_reading'] is not None for r in attempts),
       'unclear_or_unattested_attempts':sum(r['unclear_or_unattested_flag'] for r in attempts),
       'entries_with_CISI_alias':sum(bool(r['cisi_aliases']) for r in observations),
       'entries_joined_by_explicit_CISI':sum(bool(r['joined_record_ids']) for r in observations),
       'unique_CISI_aliases':len({s for r in observations for s in r['cisi_aliases']}),
       'unique_joined_object_families':len({s for r in observations for s in r['joined_object_family_ids']}),
       'unjoined_entry_ids':[r['reading_id'] for r in observations if not r['joined_record_ids']],
       'unjoined_CISI_aliases':sorted({s for r in observations for s in r['cisi_aliases'] if not bycisi[s]}),
       'limitations':['Primary baseline image attachments need independent sampling; source entry counts are not unique attempted historical readings.',
                     'Continuation lines, parenthetical-only table examples and unlabeled Dholavira figures remain in the full placement manifest but need separate manual attachment.']}
    write(OUT/'reading-coverage-v2.json',x)
    print(json.dumps({k:v for k,v in x.items() if not k.startswith('unjoined')},indent=2))

if __name__=='__main__':main()
