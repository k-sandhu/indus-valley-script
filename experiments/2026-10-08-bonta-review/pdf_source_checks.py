"""Table 21 inventory, source consistency and alternate Mayig field annotations."""
from pathlib import Path
import collections, itertools, json, re, sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from pdf_followup import ROOT, OWN, OUT, WORK, read, write
from pdf_fields import classify, FISH, O1, O2, OAMB, MA
from pdf_lexical import roman

def main():
    rows=read(WORK/'reading-inventory-v3.json');occ=read(WORK/'image-occurrences-v2.json')
    catalog=read(WORK/'sign-catalogue-v2.json')+read(WORK/'unassigned-image-catalogue.json')
    ids={r['pixel_digest']:r['sign_id'] for r in catalog if r.get('pixel_digest')}
    for r in catalog:
        if len(r.get('pixel_digests',[]))==1:ids[r['pixel_digests'][0]]=r['sign_id']
    mhcodes=collections.defaultdict(set);donors=collections.defaultdict(list)
    for r in rows:
        if r['primary_label'].startswith('MH') and r['cisi_aliases']:
            mhcodes[r['primary_label']].update(r['cisi_aliases']);donors[r['primary_label']].append(r)
    table=[]
    for page in [249,250,251]:
        lines=read(WORK/f'pages/page-{page:03d}-layout.json')
        for line in lines:
            m=re.fullmatch(r'\s*\(\s*(MH\d+)\s*\)\s*',line['text'])
            if not m:continue
            label=m[1];bottom=line['bbox'][3]
            available=[o for o in occ if o['pdf_page']==page and bottom-60<=o['bbox'][3]<=bottom+5]
            if not available:continue
            anchor=max(o['bbox'][3] for o in available)
            glyphs=sorted([o for o in available if abs(o['bbox'][3]-anchor)<6],key=lambda o:o['bbox'][0])
            # Caption runs until the next parenthetical figure label or paragraph.
            following=[l for l in lines if line['bbox'][1]+3<l['bbox'][1]<line['bbox'][1]+180]
            caption=' '.join(l['text'].strip() for l in following if l['text'].strip())
            existing=next((r for r in rows if r['source_page']==page and r['primary_label']==label),None)
            if existing:
                r=existing;r['is_reading_attempt']=True
            else:
                r={'reading_id':f'R{len(rows)+1:04d}','source_page':page,'primary_label':label,
                   'primary_bbox':line['bbox'],'is_reading_attempt':True};rows.append(r)
            codes=sorted(mhcodes[label]);joined=sorted({i for d in donors[label] for i in d['joined_record_ids']})
            objects=sorted({i for d in donors[label] for i in d['joined_object_family_ids']})
            seq=[ids[o['pixel_digest']] for o in glyphs]
            r.update({'source_kind':'Table 21 full patterned interpretation','unclear_or_unattested_flag':False,
              'cisi_aliases':codes,'mh_aliases':[],'icit_aliases':[],'sign_sequence_visual_ltr':seq,
              'sign_sequence_assumed_rtl':list(reversed(seq)),'primary_glyphs':glyphs,
              'proposed_reading':caption,'proposed_gloss':caption,
              'field_assignment':'Author-labelled Table 21 P/M/C/T arrangement; explanatory caption starts with predicate',
              'caption_blocks':[caption],'source_text':caption,'complete_table18_sequence':False,
              'attachment_rule':'Image row immediately preceding parenthetical Table 21 catalogue label',
              'alias_basis':'Same MH label elsewhere in this manuscript, joined through its explicit CISI alias',
              'alias_donor_reading_ids':[d['reading_id'] for d in donors[label]],
              'joined_record_ids':joined,'joined_object_family_ids':objects,
              'join_status':'joined through explicit same-manuscript MH/CISI alias' if joined else 'unjoined'})
            table.append({'reading_id':r['reading_id'],'page':page,'primary_label':label,'glyph_count':len(seq),
                          'cisi_aliases':codes,'scoring_status':'Unvalued metrological span; whole-headword score unavailable'})
    assert len(table)==7,table
    write(WORK/'reading-inventory-v4.json',rows)
    attempt=[r for r in rows if r['is_reading_attempt']]
    coverage=read(OUT/'reading-coverage-v3.json')|{'inventory_rows':len(rows),'reading_attempt_rows':len(attempt),
      'Table21_interpreted_rows':7,'attempts_with_explicit_transcription':sum(bool(r['proposed_reading']) for r in attempt),
      'CISI_joined_rows':sum(bool(r['joined_record_ids']) for r in rows),
      'CISI_joined_attempt_rows':sum(bool(r['joined_record_ids']) for r in attempt),
      'Table21_rows':table,'lexically_selected_occurrences':640,'lexical_excluded_attempt_rows':len(attempt)-640,
      'scope':'Leading primary examples, captioned continuations, parenthetical structural figures and all seven Table 21 interpreted examples; some unlabelled/damaged figures still require manual attachment.'}
    write(OUT/'reading-coverage-v4.json',coverage)
    keys=['reading_id','source_page','primary_label','source_kind','is_reading_attempt','cisi_aliases','join_status','complete_table18_sequence']
    write(OUT/'reading-index-v4.json',{'status':'Exploratory','rows':[{k:r[k] for k in keys}|{'glyph_count':len(r['sign_sequence_visual_ltr'])} for r in rows]})
    # Alternate clear Mayig annotations. Every candidate must share a grammar category.
    schema=read(ROOT/'data/normalized/mayig_sign_schema.json')['signs']
    ml=[json.loads(l) for l in (ROOT/'data/normalized/mayig_lines.jsonl').read_text(encoding='utf-8').splitlines()]
    clear=[r for r in ml if not r['has_unknown_sign'] and r['max_damage']==0 and r['max_uncertainty']==0]
    def category(c):
        for name,group in [('F',FISH),('O1',O1),('O2',O2),('OA',OAMB),('MA',MA),('J',{'001','002','060'}),('T',{'740','520'}),('TRA',{'033'}),('COMB',{'415'}),('VI',{'032'})]:
            if c in group:return name
        return 'X'
    decisions=[];cnt=collections.Counter(); ambiguous=0
    for r in clear:
        seq=[];uncertain=False
        for sid in r['signs_reading_rtl']:
            codes=[s[1:].zfill(3) for s in schema[sid]['wells_graphemes']]
            if len({category(c) for c in codes})>1:uncertain=True
            seq.append(codes[0] if codes else sid)
        if uncertain:status='indeterminate';why=['candidate codes cross grammar categories'];ambiguous+=1
        else:status,why,_=classify(seq)
        cnt[status]+=1;decisions.append({'record_id':r['record_id'],'status':status,'reasons':why})
    write(WORK/'mayig-field-annotations.json',decisions)
    write(OUT/'mayig-fields.json',{'status':'Exploratory','clear_lines':len(clear),'objects':len({r['object_family_id'] for r in clear}),
       'tokens':sum(r['length'] for r in clear),'classification':dict(cnt),'candidate_category_ambiguous_lines':ambiguous,
       'basis':'Same canonical operational rule; direct Mayig candidates are used only when their grammar categories agree. These objects overlap the Lipi population.'})
    # Source consistency: printed first reading versus the literal Table variants.
    selection=read(WORK/'lexical-selection-v2.json');byid={r['reading_id']:r for r in rows}
    bundles={int(k):v for k,v in selection['table18_role_variants_slp1'].items()}
    cmap={c:g[0] for g in ['aA','iI','uU','fF','xX','kKgG','cCjJ','wWqQ','tTdD','pPbB','sSz','nR'] for c in g}
    normalize=lambda s:''.join(cmap.get(c,c) for c in s)
    checks=[]
    for s in selection['readings']:
        r=byid[s['reading_id']];g=r.get('proposed_gloss')
        if not g:continue
        first=re.split(r'[,;(‘\[\]]|\bOR\b',g)[0].strip(' -.*')
        first=re.sub(r'^\d+\.\s*','',first)
        if not first or len(first)>90 or not re.fullmatch(r'[A-Za-zāīūṛṝḷṅñṭḍṇśṣṃḥ\s\-*?]+',first):continue
        target=roman(re.sub(r'[\s\-*?]','',first))
        choices=[]
        for i,role in enumerate(s['roles']):
            v=bundles[role]
            if i:v=[w for w in v if w not in selection['initial_only_slp1'].get(str(role),[])]
            choices.append(v)
        words={''.join(v) for v in itertools.product(*choices)}
        checks.append({'reading_id':r['reading_id'],'first_printed_reading':first,'exact_fixed_variant_consistent':target in words,
                       'normalized_fixed_variant_consistent':normalize(target) in {normalize(v) for v in words}})
    write(WORK/'reading-consistency-rows.json',checks)
    write(OUT/'reading-consistency.json',{'status':'Exploratory','caption_targets_checked':len(checks),
       'exact_literal_consistent':sum(r['exact_fixed_variant_consistent'] for r in checks),
       'normalized_literal_consistent':sum(r['normalized_fixed_variant_consistent'] for r in checks),
       'meaning':'Literal first-reading consistency with finite Table variants. Contractions, geminate feminine readings, additional variants and word-order interpretations are outside this check; discrepancies are not automatically contradictory sign values.',
       'excluded_source_variant_id':'U149','excluded_source_variant_pages':[159,170],
       'Table18_comparator_page':81})
    print(json.dumps({k:v for k,v in coverage.items() if k not in ['unjoined_ids','Table21_rows']},indent=2))
    print('Mayig',dict(cnt),'literal consistency',len(checks),sum(r['exact_fixed_variant_consistent'] for r in checks),sum(r['normalized_fixed_variant_consistent'] for r in checks))

if __name__=='__main__':main()
