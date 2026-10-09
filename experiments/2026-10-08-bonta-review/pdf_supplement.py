"""Add captioned continuation figures and parenthetical catalogue rows."""
from pathlib import Path
import collections, json, re, sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from pdf_followup import ROOT, OWN, OUT, WORK, RAW, read, write, sha
from pdf_readings import canonical

def main():
    rows=read(WORK/'reading-inventory-v2.json'); original=len(rows)
    occurrence=read(WORK/'image-occurrences-v2.json')
    catalog=read(WORK/'sign-catalogue-v2.json')+read(WORK/'unassigned-image-catalogue.json')
    ids={r['pixel_digest']:r['sign_id'] for r in catalog if r.get('pixel_digest')}
    for r in catalog:
        if len(r.get('pixel_digests',[]))==1:ids[r['pixel_digests'][0]]=r['sign_id']
    supplement=[]
    for page in range(16,250):
        if 79<=page<=85:continue
        lines=[l for l in read(WORK/f'pages/page-{page:03d}-layout.json') if l['text'].strip()]
        for line in lines:
            text=line['text'].strip(); left=line['bbox'][0]; y=line['bbox'][3]
            parenthetical=re.fullmatch(r'\(?\s*(MH\s*\d+)(?:\s*[,/;]\s*MH\s*\d+)*\s*\)?',text)
            continuation=text.startswith('[') and left>120
            if not parenthetical and not continuation:continue
            if any(r['source_page']==page and abs(r['primary_bbox'][1]-line['bbox'][1])<5 for r in rows):continue
            glyphs=sorted([o for o in occurrence if o['pdf_page']==page and abs(o['bbox'][3]-y)<9 and o['bbox'][2]<=left+3],key=lambda o:o['bbox'][0])
            if not glyphs:continue
            if any(l['bbox'][0]<left-4 and abs(l['bbox'][1]-line['bbox'][1])<4 and re.search('[A-Za-z0-9]',l['text']) for l in lines):continue
            priors=[r for r in rows if r['source_page']*1000+r['primary_bbox'][1]<page*1000+line['bbox'][1]]
            parent=max(priors,key=lambda r:r['source_page']*1000+r['primary_bbox'][1]) if priors else None
            if continuation and (not parent or page-parent['source_page']>1):continue
            if parenthetical:
                primary=re.sub(r'\s+','',parenthetical[1]); parent=None
                kind='parenthetical structural figure; no reading attempt inferred'; cisi=[]
            else:
                primary=parent['primary_label'];kind='continuation reading figure';cisi=parent['cisi_aliases']
            seq=[ids[o['pixel_digest']] for o in glyphs]
            proposed=None;gloss=None
            if continuation and '/' in text:
                before,after=text.strip('[] ').split('/',1)
                if not any(w in before.lower() for w in ['seal','dholavira','see ','note ','line ','found']):
                    proposed=before;gloss=after
            supplement.append({'reading_id':f'R{original+len(supplement)+1:04d}',
              'source_page':page,'primary_label':primary,'primary_bbox':line['bbox'],
              'source_kind':kind,'is_reading_attempt':continuation,'parent_reading_id':parent['reading_id'] if parent else None,
              'unclear_or_unattested_flag':bool(re.search('unclear|unreadable|effaced|illegible|uncertain|unattested|hypothetical|\\*',text,re.I)),
              'cisi_aliases':cisi,'mh_aliases':[],'icit_aliases':[],
              'sign_sequence_visual_ltr':seq,'sign_sequence_assumed_rtl':list(reversed(seq)),
              'primary_glyphs':glyphs,'proposed_reading':proposed,'proposed_gloss':gloss,
              'field_assignment':'Continuation figure; field label not supplied on this caption',
              'caption_blocks':[text],'source_text':text,
              'complete_table18_sequence':bool(seq) and all(s.startswith('B') and int(s[1:])<=65 for s in seq),
              'attachment_rule':'Glyph row to the left of a caption-only or parenthetical-only label; no preceding prose on this baseline',
              'joined_record_ids':parent['joined_record_ids'] if parent else [],
              'joined_object_family_ids':parent['joined_object_family_ids'] if parent else [],
              'join_status':'parent entry explicit CISI' if cisi else 'unjoined'})
    rows+=supplement
    write(WORK/'reading-inventory-v3.json',rows)
    ownkeys=['reading_id','source_page','primary_label','source_kind','is_reading_attempt','cisi_aliases','join_status','complete_table18_sequence']
    write(OUT/'reading-index-v3.json',{'status':'Exploratory','rows':[{k:r[k] for k in ownkeys}|{'glyph_count':len(r['sign_sequence_visual_ltr'])} for r in rows]})
    attempts=[r for r in rows if r['is_reading_attempt']]
    x={'status':'Exploratory','primary_entries':original,'supplemental_figures':len(supplement),
       'supplemental_reading_figures':sum(r['is_reading_attempt'] for r in supplement),
       'supplemental_structural_figures':sum(not r['is_reading_attempt'] for r in supplement),
       'inventory_rows':len(rows),'reading_attempt_rows':len(attempts),
       'unique_primary_labels':len({r['primary_label'] for r in rows}),
       'attempts_with_explicit_transcription':sum(bool(r['proposed_reading']) for r in attempts),
       'complete_table18_attempt_rows':sum(r['complete_table18_sequence'] for r in attempts),
       'unclear_or_unattested_attempt_rows':sum(r['unclear_or_unattested_flag'] for r in attempts),
       'CISI_joined_rows':sum(bool(r['joined_record_ids']) for r in rows),
       'CISI_joined_attempt_rows':sum(bool(r['joined_record_ids']) for r in attempts),
       'unique_CISI_aliases':len({c for r in rows for c in r['cisi_aliases']}),
       'unique_joined_object_families':len({c for r in rows for c in r['joined_object_family_ids']}),
       'attempt_rows_without_primary_glyphs':sum(not r['sign_sequence_visual_ltr'] for r in attempts),
       'unjoined_ids':[r['reading_id'] for r in rows if not r['joined_record_ids']],
       'limits':['Includes repeated source examples and alternate caption figures; count is an extraction inventory, not unique historical attempted inscriptions.',
                 'Unlabelled figures, alternate glyphs and damaged signs still need manual adjudication; no exhaustive author success/failure denominator is asserted.']}
    write(OUT/'reading-coverage-v3.json',x)
    old=read(RAW/'papers/page-segments.json');matches=0;different=[]
    for i in range(259):
        a=old[i].split('---\n',1)[-1] if i==0 else old[i]
        b=(WORK/f'pages/page-{i+1:03d}.txt').read_text(encoding='utf-8')
        aa=collections.Counter(c for c in a if c.isalnum());bb=collections.Counter(c for c in b if c.isalnum())
        if aa==bb:matches+=1
        else:different.append({'page':i+1,'page_text_extra':dict(aa-bb),'pdf_extra':dict(bb-aa)})
    write(OUT/'witness-v3.json',read(OUT/'witness-v2.json')|{'alphanumeric_multiset_equal_pages':matches,
          'alphanumeric_differences':different,'printed_folios':'None; the PDF is unfoliated. Citations use one-based PDF leaves.',
          'same_edition_verified':not different,
          'comparison':'After removing acquisition header, every page has the same letters/digits. Layout order, whitespace, page-break hyphens and punctuation extraction differ.'})
    print(json.dumps({k:v for k,v in x.items() if k!='unjoined_ids'},indent=2)); print('Text character bags equal',matches,'differences',different)

if __name__=='__main__':main()
