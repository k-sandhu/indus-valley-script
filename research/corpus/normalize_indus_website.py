"""Parse only observational INSERT statements from the GPL-3.0 older corpus.

No SQL is executed. GLYPHSEQUENCE 0 is a displayed line break in this export,
not an eroded Indus sign (see its GLYPH mapping to <br>).
"""
from pathlib import Path
import re,csv,json,hashlib,collections,subprocess

ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/'data'/'indus_website'
OUT=ROOT/'data'/'normalized'
P=SRC/'population-script.sql'
sql=P.read_text(encoding='utf-8-sig')

def table(name):
    m=re.search(r'INSERT INTO '+name+r'\s*\(([^)]*)\)\s*VALUES\s*(.*?);',sql,re.S)
    if not m: raise ValueError('missing table '+name)
    fields=[x.strip() for x in m.group(1).split(',')]
    rows=[]
    # SQL uses double-quoted values. CSV handles commas within those values.
    for item in re.findall(r'\(((?:"(?:[^"]|"")*"|[^()"])*?)\)',m.group(2)):
        vals=next(csv.reader([item],skipinitialspace=True))
        if len(vals)!=len(fields): raise ValueError((name,item))
        rows.append(dict(zip(fields,[None if v=='NULL' else v for v in vals])))
    return rows

sites={r['SITEID']:r['NAME'] for r in table('SITE')}
objects={r['SEALID']:r for r in table('SEAL')}
insc={r['SEALID']:r for r in table('INSCRIPTION')}
icons={r['SEALID']:r['DESCRIPTION'] for r in table('ICONOGRAPHY')}
q_names={r['QUALITYID']:r['QUALITY'] for r in table('FEATURE')}
qualities=collections.defaultdict(list)
for r in table('ICONOGRAPHYFEATURES'):
    qualities[r['SEALID']].append(q_names.get(r['QUALITYID']))
seqs=collections.defaultdict(list)
for r in table('GLYPHSEQUENCE'):
    seqs[r['SEALID']].append((int(r['IDX']),int(r['GLYPHID'])))
rows=[]
for k,items in sorted(seqs.items(),key=lambda kv:int(kv[0])):
    indexes=[i for i,g in sorted(items)]
    if indexes!=list(range(len(indexes))): raise ValueError('noncontiguous '+k)
    tokens=[str(g).zfill(3) for i,g in sorted(items)]
    meta=objects[k]
    split=[]
    for token in tokens:
        if token=='000': split.append([])
        else:
            if not split: split.append([])
            split[-1].append(token)
    rows.append({'record_id':k,'object_family_id':k,'source_cisi':meta['CISI'],
                 'site':sites[meta['SITEID']],'direction':insc[k]['DIRECTION'],
                 'complete_observed':insc[k]['ISCOMPLETE']=='Y','symbol':icons.get(k),
                 'qualities':qualities[k],'material':meta['MATERIAL'],
                 'signs_visual_ltr':[s for s in tokens if s!='000'],
                 'parts_visual_ltr':split,'parts_reading_rtl':[x[::-1] for x in split],
                 'length':sum(len(x) for x in split),'single_line':len(split)==1,
                 'metadata':meta,
                 'license':'GPL-3.0; preserve upstream LICENSE',
                 'orientation_basis':'Matches ICIT visual LTR convention; GLYPHID 0 maps to <br> and splits lines'} )
(OUT/'indus_website_observed.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows),encoding='utf-8')
lipi={json.loads(line)['record_id']:json.loads(line) for line in (OUT/'lipi_observed_faces.jsonl').read_text(encoding='utf-8').splitlines()}
matches,missing,diff=[],[],[]
for r in rows:
    new=lipi.get(r['record_id']+'.1')
    if not new:
        missing.append(r['record_id']);continue
    if new['signs_visual_ltr']!=r['signs_visual_ltr']:
        diff.append({'id':r['record_id'],'old':r['signs_visual_ltr'],'new':new['signs_visual_ltr'],'old_parts':r['parts_visual_ltr'],'new_raw':new['text_code_visual_ltr']})
    else:matches.append(r['record_id'])
summary={'source_url':'https://github.com/yajnadevam/indus-website','source_commit':subprocess.check_output(['git','-C',str(SRC),'rev-parse','HEAD'],text=True).strip(),
         'source_sha256':hashlib.sha256(P.read_bytes()).hexdigest(),'license':'GPL-3.0','rows':len(rows),
         'tokens':sum(r['length'] for r in rows),'unique_sequences':len(set(tuple(r['signs_visual_ltr']) for r in rows)),
         'directions':dict(collections.Counter(r['direction'] for r in rows)), 'multiline_rows':sum(not r['single_line'] for r in rows),
         'exact_lipi_first_face_matches':len(matches),'no_lipi_first_face':missing,'different_from_lipi_first_face':diff,
         'limitations':['Derivative associated with disputed decipherment; exclude DECIPHERMENT and GLYPHSIMILARITY tables.',
                        'Published repo GPL does not settle permissions for every archaeological image, which are not copied here.',
                        '2543 rows selected by upstream; filtering criterion not assumed. Independent primary data still required.',
                        'The misleading SEAL table contains several artifact types; use archaeological metadata in larger lipi extraction for type.']}
(OUT/'indus_website_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in summary.items() if k not in ['no_lipi_first_face','different_from_lipi_first_face','limitations']},indent=2))
print('different sequences',len(diff),'missing',len(missing))
