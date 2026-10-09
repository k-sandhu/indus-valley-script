"""PDF follow-up. Source payloads and rendered images remain local-only."""
from pathlib import Path
import argparse, collections, difflib, hashlib, json, re, shutil, sys

ROOT = Path(__file__).resolve().parents[2]
OWN = Path(__file__).resolve().parent
RAW = ROOT / 'data/raw/2026-10-08-bonta-review'
OUT = OWN / 'pdf-2026-10-09-v1'
WORK = RAW / 'pdf-2026-10-09-v1'
PDF = RAW / 'papers/A_Partial_Decipherment_of_the_Indus_Vall.pdf'

def read(p): return json.loads(p.read_text(encoding='utf-8'))
def write(p, x):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(x, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def register():
    """Preserve current editorial state; register before any PDF calculation."""
    history = OWN / 'history/2026-10-09-before-pdf'
    if history.exists(): raise SystemExit('Snapshot exists; refusing to overwrite')
    history.mkdir(parents=True)
    names = ['README.md','REPORT.md','RETROSPECTIVE.md','PROTOCOL.md','sources.json',
             'registry-entry.json','claims.jsonl','claims.md','ledger-coverage.json',
             'completion.json','FILES.json','RESPONSE-FILES.json','concordance.json']
    for name in names:
        if (OWN/name).exists(): shutil.copyfile(OWN/name, history/name)
    protected = []
    for base in [OWN, RAW]:
        for p in sorted(base.rglob('*')):
            if p.is_file() and 'history' not in p.relative_to(base).parts:
                protected.append({'path':p.relative_to(ROOT).as_posix(), 'sha256':sha(p)})
    write(history/'baseline-files.json', protected)
    with (OWN/'PROTOCOL.md').open('a', encoding='utf-8') as f:
        f.write('''
## PDF amendment, 9 October 2026 (registered on 8 October Toronto time)

The owner supplied the complete 259-page second edition. Earlier endpoints, review files and response outputs stay frozen. New calculations use `pdf-2026-10-09-v1/`, with source text, images, reading rows and per-assignment predictions in the matching local raw directory. The sign inventory contributor's 58 manuscript entries and chart audit v2.1 are reused starting annotations. A PDF source observation is Verified computation after extraction checks; every result depending on this author's visual mapping is **Exploratory**, pending independent coding.

| ID | Data and statistic | Null/comparison | Decision and negative result |
|---|---|---|---|
| P-W | Verify supplied SHA-256, PDF metadata/page count; compare normalized page text with each retained form-feed segment. Record footer labels and segment-to-printed-page map. | Exact normalized text equality plus token sequence similarity for layout differences; inspect mismatches and table renders. | Same edition requires identical section/table order and no substantive text revision; report extraction differences separately. An unresolved printed label is explicitly null. |
| P-S | Catalogue every Table 18 glyph variant, other value/anchor/field figures, and every inscription figure occurrence. Count labelled assignments, distinct image forms, allograph groups and field-only forms separately. | Compare with Bonta's stated 55 and the contributor's 58 labelled entries. Image hashes are extraction checks, never archaeological sign classes. | Explain which counting unit yields each total. Unvalued field signs and alternate drawings cannot inflate the assignment count. Unresolved compounds remain explicit. |
| P-C | Independently map neutral glyph IDs to Mayig classes, direct Wells candidate sets and Helsinki v2.1 cells. Record visual basis, candidates and confidence. | Compare only source/reference images and descriptions; no lexical or corpus outcome used to choose a candidate. Freeze mapping JSON SHA-256 before building the neutral packet and running corpus tests. | High confidence requires a visually distinguishing form; ambiguous groups retain all candidates. No forced bijection. Mapping coverage counts singleton, ambiguous and unmapped separately. |
| P-R | Inventory each manuscript reading/attempt, including unclear examples, source identifiers, glyph IDs in printed order, proposed transcription/gloss, field and derivation/illustration/check status. Report complete/partial glyph coverage and unique identifier counts. | Reconcile image/text attachment with PDF coordinates, primary entry headings and earlier parser locators. Object joins require explicit CISI/excavation aliases. | Never join by equal ICIT numbers across editions. An alias is not a separate attempt; duplicate citations stay identified. Missing signs or unclear reading boundaries prevent complete scoring and stay in the denominator. |
| P-F | Translate the explicit P/M/C/T and juncture restrictions into a finite grammar in reading order. Count clean, conflicting and indeterminate texts in the original 2,469-object population; report conflicts by rule and site. | Internal shuffles, 1,999 draws, seed 20261009, preserving sign counts/length. A conservative grammar checks only stated necessary restrictions; ambiguous candidates yield a range. | Report coverage and exceptions beside each rule. A grammar fit without independent boundaries supplies a structural compatibility test. Indeterminate texts cannot be counted as clean. |
| P-L | Use every identifiable proposed reading with complete valued glyphs, fixed Table 18 variants and the same pinned MW headwords. Count attempted readings, eligible occurrences, distinct sequences and exact whole-headword hits. Dictionary-derived roles, mixed/unknown derivations and only non-dictionary-derived roles are reported separately. | Permute value bundles across identified sign roles, keeping sequences, dictionary and variants fixed: exhaustive up to 40,320 assignments; otherwise 1,999 seeded draws (20261009). Exact variants are primary, previous broader normalization secondary. Report add-one Monte Carlo tails, distributions and coverage. | A tail <= .05 describes conditional excess only. Values derived through dictionary contexts make their own training matches circular. Unknown provenance is excluded from the clean non-dictionary subset. A held-out subset requires an explicit source assertion that readings followed a fixed assignment; source order alone is insufficient. Unclear/failed examples count in attempt totals, even when unscorable. No arbitrary substrings, added sounds or semantic fit. |
| P-V | Locate explicit ICIT checks, printed figures and same-object MH/CISI aliases. Count check entries, repeated objects, unresolved joins and reported failures. | Compare object identity across the entire manuscript, and distinguish ICIT-first entry, MH-first alias and iconography remark. | Only explicit post-fix checks qualify as held-out claims. No historical validation rate without a complete attempted denominator and fixed historical values. |

The independent coder packet contains neutral crops and reference class/chart images, instructions and the same candidate-list return schema. It contains neither Bonta's values nor this mapping. The mapping is frozen before packet construction; later corrections require a successor file and amendment. No physical-metrology fit is newly authorized without independently joined mass/quantity observations. The full lexical calculation may require a bounded eligible subset when inscription figures contain unvalued signs or reading boundaries cannot be identified; all exclusions are retained with counts. Caption-source rows keep timestamps; manuscript-source rows acquire verified printed-page locators.
''')
    print('Registered PDF amendment; preserved editorial baseline')

def extract():
    import fitz
    from PIL import Image, ImageDraw
    if OUT.exists() or WORK.exists(): raise SystemExit('Refusing existing PDF outputs')
    OUT.mkdir(); WORK.mkdir()
    expected='12e8e6b1c427dbdc995e64991d5d0a676b8d397956f28379b046a230a5065f14'
    assert sha(PDF)==expected
    doc=fitz.open(PDF)
    old=read(RAW/'papers/page-segments.json')
    pages=[]; occurrences=[]; image_files={}
    normalized=lambda s: re.sub(r'\s+', '', s)
    for index, page in enumerate(doc):
        text=page.get_text()
        (WORK/f'pages/page-{index+1:03d}.txt').parent.mkdir(exist_ok=True)
        (WORK/f'pages/page-{index+1:03d}.txt').write_text(text,encoding='utf-8')
        blocks=page.get_text('dict')['blocks']
        lines=[]
        for block in blocks:
            if block['type']==0:
                for line in block['lines']:
                    lines.append({'bbox':line['bbox'],'text':''.join(s['text'] for s in line['spans'])})
        a,b=normalized(old[index]),normalized(text)
        pages.append({'segment':index,'pdf_page':index+1,'printed_folio':None,
                      'citation_page':index+1,'normalized_exact':a==b,
                      'token_similarity':difflib.SequenceMatcher(None,old[index].split(),text.split(),autojunk=False).ratio(),
                      'retained_chars':len(a),'pdf_chars':len(b)})
        write(WORK/f'pages/page-{index+1:03d}-layout.json',lines)
        for j, info in enumerate(page.get_image_info(xrefs=True)):
            xref=info['xref']
            if xref and xref not in image_files:
                x=doc.extract_image(xref)
                p=WORK/f'embedded/xref-{xref:05d}.{x["ext"]}'
                p.parent.mkdir(exist_ok=True); p.write_bytes(x['image'])
                image_files[xref]=p.relative_to(ROOT).as_posix()
            occurrences.append({'pdf_page':index+1,'image_index':j,'xref':xref,
                                'bbox':list(info['bbox']),'width':info['width'],'height':info['height'],
                                'image_path':image_files.get(xref),'pixel_digest':info['digest'].hex()})
    write(WORK/'image-occurrences.json',occurrences)
    write(OUT/'page-map.json',{'basis':'PDF is unfoliated: inspected pages have no printed page numerals. Citation page is the one-based PDF leaf; retained segment index is zero-based.',
                            'rows':pages,'trailing_segments':len(old)-len(doc)})
    write(OUT/'witness.json',{'status':'Verified computation','pdf_sha256':sha(PDF),'metadata':doc.metadata,'pages':len(doc),
          'normalized_exact_pages':sum(r['normalized_exact'] for r in pages),
          'minimum_token_similarity':min(r['token_similarity'] for r in pages),'embedded_unique_xrefs':len(image_files),
          'image_placements':len(occurrences),'page_text_sha256':sha(RAW/'papers/bonta-2024-partial-decipherment-2nd-ed.page-text.txt'),
          'protocol_sha256':sha(OWN/'PROTOCOL.md'), 'same_edition':'Pending visual and mismatch checks'})
    for number in [18,20,21,44,46,48,53,70,72,74,79,80,81,82,86,96,186,193,213,217]:
        p=WORK/f'renders/page-{number:03d}.png'; p.parent.mkdir(exist_ok=True)
        doc[number-1].get_pixmap(matrix=fitz.Matrix(1.7,1.7)).save(p)
    table=[o for o in occurrences if 79<=o['pdf_page']<=82]
    cards=Image.new('RGB',(1100,((len(table)+5)//6)*150),'white'); draw=ImageDraw.Draw(cards)
    for i,o in enumerate(table):
        if not o['image_path']: continue
        im=Image.open(ROOT/o['image_path']).convert('RGB'); im.thumbnail((150,105))
        x=(i%6)*183;y=(i//6)*150
        cards.paste(im,(x+10,y+30));draw.text((x+5,y+5),f'p{o["pdf_page"]} #{o["image_index"]} x{o["xref"]}',fill='black')
    cards.save(WORK/'table18-contact.png')
    print(json.dumps(read(OUT/'witness.json'),indent=2))

def inline():
    """Repair extractor's missing inline-image witnesses in successor manifest."""
    import fitz
    from PIL import Image, ImageDraw
    doc=fitz.open(PDF); occurrences=read(WORK/'image-occurrences.json')
    for page in doc:
        blocks=[b for b in page.get_text('dict')['blocks'] if b['type']==1]
        for o in [x for x in occurrences if x['pdf_page']==page.number+1 and not x['image_path']]:
            b=min(blocks,key=lambda b:sum(abs(x-y) for x,y in zip(b['bbox'],o['bbox'])))
            p=WORK/f'embedded/inline-p{page.number+1:03d}-{o["image_index"]:03d}.png'
            page.get_pixmap(matrix=fitz.Matrix(4,4),clip=fitz.Rect(o['bbox'])).save(p)
            o['image_path']=p.relative_to(ROOT).as_posix()
            o['extraction']='rendered image placement (inline, xref unavailable)'
    write(WORK/'image-occurrences-v2.json',occurrences)
    table=[o for o in occurrences if 79<=o['pdf_page']<=82]
    cards=Image.new('RGB',(1100,((len(table)+5)//6)*150),'white');draw=ImageDraw.Draw(cards)
    for i,o in enumerate(table):
        im=Image.open(ROOT/o['image_path']).convert('RGB');im.thumbnail((150,105))
        x=(i%6)*183;y=(i//6)*150
        cards.paste(im,(x+10,y+30));draw.text((x+5,y+5),f'p{o["pdf_page"]} #{o["image_index"]} x{o["xref"]}',fill='black')
    cards.save(WORK/'table18-contact-v2.png')
    print(json.dumps(read(OUT/'witness.json'),indent=2))
    print('Inline placements',sum(o['xref']==0 for o in occurrences))

def catalog():
    from PIL import Image, ImageDraw
    occurrences=read(WORK/'image-occurrences-v2.json')
    inventory=read(ROOT/'research/literature/2026-10-08-bonta-sign-inventory/inventory.json')['rows'][:58]
    indexes=[]
    indexes += [(79,[i]) for i in range(7,16)]
    indexes += [(80,x) for x in [[0],[1],[2],[3],[4],[5],[6],[7,8],[9],[10],[11],[12],[13,14],[15],[16],[17]]]
    indexes += [(81,x) for x in [[0],[1],[2],[3],[4],[5],[6],[7,8],[9],[10],[11],[12,13],[14],[15],[16],[17],[18]]]
    indexes += [(82,x) for x in [[0],[1],[2],[3],[4],[5],[6,7],[8],[9],[10,11,12],[13],[14],[15],[16],[17],[18]]]
    assert len(indexes)==58
    catalogue=[]
    for entry,(page,nums) in zip(inventory,indexes):
        for variant,j in enumerate(nums,1):
            o=next(o for o in occurrences if o['pdf_page']==page and o['image_index']==j)
            neutral=f'B{len(catalogue)+1:03d}'
            im=Image.open(ROOT/o['image_path']).convert('RGB')
            crop=WORK/f'sign-crops/{neutral}.png';crop.parent.mkdir(exist_ok=True);im.save(crop)
            row={'sign_id':neutral,'table_entry':entry['entry'],'label':entry['label'],'proposed_variants':entry['readings'],
                 'category':entry['category'],'pdf_page':page,'printed_folio':None,'table':18,'variant':variant,
                 'crop_path':crop.relative_to(ROOT).as_posix(),'visual_description':entry['visual_description'],
                 'pixel_digest':o['pixel_digest'],'bbox':o['bbox'],'xref':o['xref']}
            catalogue.append(row)
    write(WORK/'sign-catalogue.json',catalogue)
    write(OUT/'sign-catalogue-index.json',{'status':'Exploratory','rows':[{k:v for k,v in r.items() if k not in ('proposed_variants','pixel_digest','bbox')} for r in catalogue]})
    # Reference images use the chart's own numbers; no semantic values.
    schema=read(ROOT/'data/normalized/mayig_sign_schema.json')['signs']
    chart=read(ROOT/'experiments/2026-10-08-chart-reference-audit/chart-reference-v2.1.json')['rows']
    bycode={str(r['code']).zfill(3):r for r in chart}
    for start in [1,101,201,301]:
        cards=Image.new('RGB',(1200,17*110),'white');draw=ImageDraw.Draw(cards)
        for n in range(start,min(start+100,398)):
            k=f'P{n:03d}'; v=schema.get(k); i=n-start
            if not v:continue
            options=[bycode.get(s[1:].zfill(3)) for s in v['parpola_graphemes']]
            options=[s for s in options if s]
            x=(i%6)*200;y=(i//6)*110
            draw.text((x+3,y+3),k+' '+','.join(v['wells_graphemes'])[:26],fill='black')
            if options:
                c=options[0]; p=ROOT/f'output/chart_atlas/cells/p{c["pdf_page"]}_c{c["column"]}_r{c["row"]}.png'
                im=Image.open(p).convert('RGB');im.thumbnail((185,80));cards.paste(im,(x+4,y+25))
        cards.save(WORK/f'reference-classes-{start:03d}.png')
    for page in [20,21,44,46,48,53,70,72,74]:
        rows=[o for o in occurrences if o['pdf_page']==page]
        cards=Image.new('RGB',(1100,((len(rows)+5)//6)*145),'white');draw=ImageDraw.Draw(cards)
        for i,o in enumerate(rows):
            im=Image.open(ROOT/o['image_path']).convert('RGB');im.thumbnail((160,100));x=(i%6)*183;y=(i//6)*145
            cards.paste(im,(x+5,y+28));draw.text((x+4,y+4),f'p{page} #{o["image_index"]} {o["pixel_digest"][:6]}',fill='black')
        cards.save(WORK/f'contact-page-{page:03d}.png')
    old=read(RAW/'papers/page-segments.json'); diffs=[]; counts=collections.Counter()
    for i in range(259):
        a=old[i]
        if i==0:a=a.split('---\n',1)[1]
        b=(WORK/f'pages/page-{i+1:03d}.txt').read_text(encoding='utf-8')
        a=re.sub(r'\s+','',a);b=re.sub(r'\s+','',b)
        sm=difflib.SequenceMatcher(None,a,b,autojunk=False)
        ops=[(tag,a[x:y],b[u:v]) for tag,x,y,u,v in sm.get_opcodes() if tag!='equal']
        for op in ops:counts[op]+=1
        diffs.append({'page':i+1,'differences':ops})
    write(WORK/'text-differences.json',diffs)
    w=read(OUT/'witness.json'); w.update({'same_edition':'Same section/table order and content; page-text header/UI excluded. Character differences listed locally for inspection.',
      'difference_types':[{'difference':list(k),'occurrences':v} for k,v in counts.most_common()],
      'table18_labelled_assignments':58,'table18_drawings':len(catalogue),
      'table18_unique_pixel_digests':len(set(r['pixel_digest'] for r in catalogue))})
    write(OUT/'witness-v2.json',w)
    print(json.dumps({'drawings':len(catalogue),'diff_types':w['difference_types'][:25]},ensure_ascii=False))

def mapping():
    from PIL import Image
    rows=read(WORK/'sign-catalogue.json');occ=read(WORK/'image-occurrences-v2.json')
    extras=[(21,[3],'O1', ['P364']),(21,[4],'O1-variant',['P364']),
      (21,[5],'O2',['P075']),(21,[6],'O3',['P366']),
      (21,[12],'F-vertical',['P056']),(21,[17],'F-horizontal',['P058']),
      (21,[16],'F-caret',['P060']),(21,[15],'F-whiskers',['P062']),
      (21,[13,14],'F-comb',[]),(21,[18,19],'F-two-strokes',[]),
      (21,[2],'twelve-strokes',['P142']),
      (20,[55],'juncture-two-short',['P122']),
      (20,[56],'juncture-bent-pair',['P120']),
      (20,[57],'juncture-one-short',['P121'])]
    extra_candidates={}
    for page,js,label,candidates in extras:
        selected=[o for o in occ if o['pdf_page']==page and o['image_index'] in js]
        neutral=f'B{len(rows)+1:03d}'
        imlist=[Image.open(ROOT/o['image_path']).convert('RGB') for o in selected]
        if len(imlist)==1: im=imlist[0]
        else:
            h=max(i.height for i in imlist); scaled=[]
            for i in imlist:
                i=i.resize((round(i.width*h/i.height),h));scaled.append(i)
            im=Image.new('RGB',(sum(i.width for i in scaled)+8,h),'white');x=0
            for i in scaled:im.paste(i,(x,0));x+=i.width+8
        p=WORK/f'sign-crops/{neutral}.png';im.save(p)
        rows.append({'sign_id':neutral,'label':label,'table_entry':None,'category':'field figure',
                     'pdf_page':page,'table':None,'crop_path':p.relative_to(ROOT).as_posix(),
                     'pixel_digests':[o['pixel_digest'] for o in selected],'proposed_variants':None,
                     'basis':'Explicit membership in the field/juncture inventories on pages 20–21'})
        extra_candidates[neutral]=candidates
    write(WORK/'sign-catalogue-v2.json',rows)
    schema=read(ROOT/'data/normalized/mayig_sign_schema.json')['signs']
    chart=read(ROOT/'experiments/2026-10-08-chart-reference-audit/chart-reference-v2.1.json')['rows']
    # Visual decisions made before seeing any new corpus or lexical endpoint.
    byentry={1:['P280'],2:['P290'],3:['P159','P176'],4:['P082'],5:['P276'],6:['P316'],
      7:['P255'],8:['P092'],9:['P289'],10:['P369'],11:['P349'],12:['P145'],13:['P188'],
      14:[],15:['P144'],16:[],17:['P085','P086'],18:['P182'],19:['P035'],20:['P270'],
      21:['P114'],22:['P091'],23:['P205'],24:['P076'],25:['P256'],26:['P009','P013'],
      27:['P095'],28:['P204'],29:['P050'],30:['P227'],31:['P310'],32:['P268'],
      33:['P221','P235'],34:['P265'],35:['P342'],36:['P147'],37:['P352'],38:['P048'],
      39:['P360'],40:['P303'],41:['P366'],42:['P165'],43:['P305'],44:['P160'],45:[],
      46:['P378'],47:['P385'],48:[],49:[],50:['P324'],51:['P217'],52:['P325','P326','P327'],
      53:['P382'],54:['P384'],55:['P074'],56:['P258'],57:['P304'],58:['P223']}
    medium={3,4,13,17,21,22,24,26,33,37,38,55,57,58}
    result=[]
    for r in rows:
        e=r['table_entry']; candidates=byentry.get(e,extra_candidates.get(r['sign_id'],[])).copy()
        if e==17:candidates=['P085'] if r['variant']==1 else ['P086']
        if e==33:candidates=['P221'] if r['variant']==1 else ['P235']
        if e==52:candidates=[{1:'P325',2:'P326',3:'P327'}[r['variant']]]
        wells=sorted({s[1:].zfill(3) for c in candidates for s in schema[c]['wells_graphemes']})
        codes={s[1:].zfill(3) for c in candidates for s in schema[c]['parpola_graphemes']}
        cells=[{'cell_id':f'p{c["pdf_page"]}_c{c["column"]}_r{c["row"]}',
                'code':str(c['code']).zfill(3),'class':c['rank'],'numeric_confidence':c['numeric_confidence']}
               for c in chart if str(c['code']).zfill(3) in codes]
        conf='unmapped' if not candidates else ('medium' if e in medium or r['sign_id'] in ['B067','B069'] else 'high')
        basis='Drawing compared with Mayig description and the Helsinki images for its listed Parpola candidates; direct Mayig Wells list retained.'
        if not candidates:basis='No sufficiently distinguishing reference class identified; retain as unresolved.'
        if r['sign_id']=='B069':basis+=' Lower internal stroke reaches the oval boundary; Mayig P366 also includes B045 with a shorter central stroke, so this corpus class cannot separate the author\'s included/excluded forms.'
        sequences=[]
        if r['sign_id'] in ['B074','B075']:
            sequences=[['P050','P092' if r['sign_id']=='B074' else 'P145']]
            conf='medium';basis='Two separately drawn components treated by the author as one F-field unit; no single reference class forced.'
        result.append({'sign_id':r['sign_id'],'mayig_candidates':candidates,'wells_candidates':wells,
              'helsinki_candidates':cells,'component_sequence_candidates':sequences,'confidence':conf,'basis':basis})
    p=OUT/'mapping-v1-frozen.json'
    if p.exists():raise SystemExit('Mapping already frozen')
    write(p,{'status':'Exploratory','coder':'Package Q first visual coder','rows':result,
              'source_catalogue_sha256':sha(WORK/'sign-catalogue-v2.json'),
              'reference_sha256':sha(ROOT/'experiments/2026-10-08-chart-reference-audit/chart-reference-v2.1.json'),
              'scope':'65 Table 18 drawings and 14 field/juncture drawings or compounds; corpus and lexical outputs not consulted.'})
    write(OUT/'mapping-freeze.json',{'sha256':sha(p),'file':p.relative_to(ROOT).as_posix(),
        'created_utc':__import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(),
        'rows':len(result),'singleton_mayig':sum(len(r['mayig_candidates'])==1 for r in result),
        'ambiguous_mayig':sum(len(r['mayig_candidates'])>1 for r in result),
        'unmapped_mayig':sum(not r['mayig_candidates'] for r in result),
        'compound_component_mappings':sum(bool(r['component_sequence_candidates']) for r in result),
        'wells_covered':sum(bool(r['wells_candidates']) for r in result),
        'helsinki_covered':sum(bool(r['helsinki_candidates']) for r in result)})
    print(json.dumps(read(OUT/'mapping-freeze.json'),indent=2))

def packet():
    freeze=read(OUT/'mapping-freeze.json'); assert sha(OUT/'mapping-v1-frozen.json')==freeze['sha256']
    target=RAW/'second-coder-v1'
    if target.exists():raise SystemExit('Packet exists')
    target.mkdir();(target/'signs').mkdir();(target/'references').mkdir()
    catalogue=read(WORK/'sign-catalogue-v2.json')
    for r in catalogue:shutil.copyfile(ROOT/r['crop_path'],target/f'signs/{r["sign_id"]}.png')
    for p in (ROOT/'output/chart_atlas/cells').glob('*.png'):
        folder=target/'references/chart-cells';folder.mkdir(exist_ok=True);shutil.copyfile(p,folder/p.name)
    shutil.copyfile(ROOT/'experiments/2026-10-08-chart-reference-audit/chart-reference-v2.1.json',target/'references/chart-reference-v2.1.json')
    schema=read(ROOT/'data/normalized/mayig_sign_schema.json')['signs']
    # Reference descriptions and codes only; no author values or first-coder answers.
    write(target/'references/mayig-classes.json',{'source':'Mayig MIT; Michael Carlson 2024; pinned ad2f1e218a34b8c33c57de0d6cb8d99272765bbb',
        'signs':{k:{field:v[field] for field in ('id','description','parpola_graphemes','wells_graphemes')} for k,v in schema.items()}})
    for p in WORK.glob('reference-classes-*.png'):shutil.copyfile(p,target/'references'/p.name)
    template={'status':'Exploratory','coder':'','rows':[{'sign_id':r['sign_id'],'mayig_candidates':[],
      'wells_candidates':[],'helsinki_candidates':[],'component_sequence_candidates':[],'confidence':'unmapped','basis':''} for r in catalogue]}
    write(target/'return-template.json',template)
    (target/'INSTRUCTIONS.md').write_text('''# Independent visual coding

Map the 79 neutral sign drawings in `signs/` to the supplied Mayig reference classes and Helsinki chart cells. Inspect shape and orientation. Do not infer a mapping from a proposed sound, meaning, dictionary match or corpus result. Neither the first mapping nor proposed values is supplied. Work independently and record uncertainty.

Use `return-template.json`. Keep every ID, including unresolved ones. Candidate lists can contain more than one class. `helsinki_candidates` entries use `cell_id`, three-digit `code`, `class` and the chart's `numeric_confidence`. Copy direct Wells candidates for your selected Mayig classes, rather than merging connected classes. For a drawing made from separate components, fill `component_sequence_candidates` with lists of Mayig IDs in visual left-to-right order; distinguish that order from inscription reading direction. Use high, medium, low or unmapped confidence and a short visual basis. Mark mirrored forms and uncertain internal strokes explicitly. Do not force a one-to-one assignment.

The 687 chart-cell images include adjacent printed details; the central cell drawing and its code/class are indexed by `chart-reference-v2.1.json`. Mayig classes list direct Parpola and Wells candidates. The four class sheets reuse these chart cells, not an independent Mayig glyph font. Chart numbers themselves remain Exploratory annotations pending expert review. Reference attribution: Koskenniemi and Parpola (1979), *Corpus of Texts in the Indus Script*, CC BY 4.0; Michael Carlson's Mayig corpus, MIT, 2024. Source sign crops are third-party manuscript material and remain local-only.
''',encoding='utf-8')
    files=[{'path':p.relative_to(target).as_posix(),'sha256':sha(p)} for p in sorted(target.rglob('*')) if p.is_file()]
    write(target/'packet-manifest.json',{'files':files,'sign_crops':len(catalogue),'reference_cells':687,
                                      'contains_first_mapping':False,'contains_author_values':False})
    write(OUT/'second-coder-packet.json',{'path':target.relative_to(ROOT).as_posix(),'sign_crops':len(catalogue),
          'reference_chart_cells':687,'mapping_frozen_sha256':freeze['sha256'],
          'packet_manifest_sha256':sha(target/'packet-manifest.json'),'status':'Awaiting second coding'})
    print('Prepared neutral packet',len(catalogue))

if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('stage', choices=['register','extract','inline','catalog','mapping','packet'])
    args=parser.parse_args()
    if args.stage=='register': register()
    if args.stage=='extract': extract()
    if args.stage=='inline': inline()
    if args.stage=='catalog': catalog()
    if args.stage=='mapping': mapping()
    if args.stage=='packet': packet()
