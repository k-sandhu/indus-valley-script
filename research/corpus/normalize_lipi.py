"""Extract observed-code/metadata fields from a pinned derivative corpus.

The source's translations and decipherment assignments are deliberately excluded.
This is a local research extraction, with upstream bulk-redistribution terms unresolved.
"""
from pathlib import Path
import json,csv,re,collections,hashlib,subprocess

ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/'data'/'lipi'
P=SRC/'src/assets/data/inscriptions.csv'
OUT=ROOT/'data'/'normalized'
OUT.mkdir(exist_ok=True)

def write(name,value):
    (OUT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

FIELDS=['cisi','region','site','area-section','block-house','room-grid','excavation-idno','time','period','phase','depth','boss','material','color','shape','cross-section','preservation','symbol','cult','type','sides','condition','complete','dir.','class','text length','signs','h','v','th','horizontal(mm)','vertical(mm)','thickness(mm)']
raw=list(csv.DictReader(P.open(encoding='utf-8-sig',newline='')))
rows,parts,errors=[],[],[]
for r in raw:
    code=r['text']
    codes=re.findall(r'\d+',code)
    tokens=[s.zfill(3) for s in codes]
    direction=r['dir.'].strip().upper()
    family=r['id'].split('.')[0]
    line_parts=code.strip('+[]').split('/')
    unknown='000' in tokens
    blank_space='999' in tokens
    complete=r['complete'].strip().upper()=='Y' and '[' not in code and ']' not in code and not unknown
    clean_rtl=complete and not blank_space and direction=='R/L' and len(line_parts)==1 and all(len(s)==3 for s in codes)
    row={'record_id':r['id'],'object_family_id':family,'source_record_id':r['id'],
         'source_cisi':r['cisi'],'text_code_visual_ltr':code,'signs_visual_ltr':tokens,
         'signs_reading_rtl':tokens[::-1], 'length':len(tokens),'direction':direction,
         'single_line':len(line_parts)==1,'complete_observed':complete,'has_unknown_sign':unknown,'has_blank_space':blank_space,
         'clean_rtl_singleline':clean_rtl,'metadata':{k:r[k] for k in FIELDS},
         'site':r['site'],'region':r['region'],'object_type':r['type'],'symbol':r['symbol'],
         'orientation_basis':'ICIT codes are normalized to reading right-to-left; direction field describes original physical artifact (Fuls2022 ch3 key)'}
    if len(set(r))<1:
        errors.append({'id':r['id'],'issue':'empty row'})
    if not re.fullmatch(r'[+\[\]0-9/\-]+',code):
        errors.append({'id':r['id'],'issue':'unexpected code syntax','text':code})
    if '+' in code.strip('+'):
        errors.append({'id':r['id'],'issue':'internal part marker; do not concatenate','text':code})
    rows.append(row)
    for idx,part in enumerate(line_parts,1):
        pt=[s.zfill(3) for s in re.findall(r'\d+',part)]
        parts.append({'record_id':r['id']+':part'+str(idx),'face_id':r['id'],'object_family_id':family,
                      'site':r['site'],'region':r['region'],'object_type':r['type'],'symbol':r['symbol'],
                      'direction':direction,'part_index':idx,'text_code_visual_ltr':part,
                      'signs_visual_ltr':pt,'signs_reading_rtl':pt[::-1],'length':len(pt),
                      'complete_observed':complete,'has_unknown_sign':'000' in pt,'has_blank_space':'999' in pt,
                      'metadata':row['metadata']})
for name,data in [('lipi_observed_faces.jsonl',rows),('lipi_observed_parts.jsonl',parts),('lipi_clean_rtl_singleline.jsonl',[r for r in rows if r['clean_rtl_singleline']])]:
    (OUT/name).write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in data),encoding='utf-8')
ids=collections.Counter(r['record_id'] for r in rows)
seqs=collections.Counter(tuple(r['signs_visual_ltr']) for r in rows)
clean=[r for r in rows if r['clean_rtl_singleline']]
metadata_missing={k:sum(r['metadata'][k] in {'','-','--','Unknown'} for r in rows) for k in FIELDS}
summary={'source_url':'https://github.com/yajnadevam/lipi','commit':subprocess.check_output(['git','-C',str(SRC),'rev-parse','HEAD'],text=True).strip(),
         'source_path':'src/assets/data/inscriptions.csv','source_sha256':hashlib.sha256(P.read_bytes()).hexdigest(),
         'source_bytes':P.stat().st_size,'rows':len(rows),'object_families':len(set(r['object_family_id'] for r in rows)),
         'parts':len(parts),'tokens':sum(r['length'] for r in rows),'distinct_sign_codes':len(set(s for r in rows for s in r['signs_visual_ltr'])),
         'unique_observed_sequences':len(seqs),'duplicate_sequence_excess':sum(n-1 for n in seqs.values()),
         'duplicate_record_ids':{k:v for k,v in ids.items() if v>1},'directions':dict(collections.Counter(r['direction'] for r in rows)),
         'object_types':dict(collections.Counter(r['object_type'] for r in rows)), 'sites':dict(collections.Counter(r['site'] for r in rows)),
         'clean_rtl_singleline_rows':len(clean),'clean_rtl_unique_sequences':len(set(tuple(r['signs_visual_ltr']) for r in clean)),
         'unknown_sign_rows':sum(r['has_unknown_sign'] for r in rows),'blank_space_rows':sum(r['has_blank_space'] for r in rows),'multiline_rows':sum(not r['single_line'] for r in rows),
         'metadata_missing':metadata_missing,'syntax_issues':errors,
         'license':'No LICENSE file in this pinned lipi repository. Source availability does not establish bulk redistribution permission; local research extraction only.',
         'excluded_columns':['sanskrit','translation','notes'],
         'excluded_files':['xlits.csv','decipher.csv','words.csv','translations.csv'],
         'warnings':['Derivative export associated with a disputed decipherment; observational transcription accuracy unverified against full primary corpus.',
                     'Do not derive canonical sign merging from xlits.csv: its canonical assignments are associated with the source interpretation.',
                     'Numeric id before decimal is conservative object-family grouping; verify against CISI and excavation IDs where available.',
                     'R/L restriction excludes exceptional directions. Neither reverse order nor source direction resolves multiline continuity.',
                     '000 is eroded/illegible. 999 is a physical blank space between signs, not a semantic sign; clean subset conservatively excludes both.',
                     'The raw complete/direction/class metadata may contain curatorial decisions and should not be treated as independent ground truth without audit.']}
write('lipi_summary.json',summary)
print(json.dumps({k:v for k,v in summary.items() if k not in {'object_types','sites','metadata_missing','syntax_issues','warnings'}},indent=2))
print('syntax issues',len(errors))
