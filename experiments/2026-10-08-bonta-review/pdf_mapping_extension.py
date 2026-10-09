"""Freeze additional caption-associated drawings, then supplement neutral packet."""
from pathlib import Path
import collections, json, shutil, sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from pdf_followup import ROOT, RAW, OUT, WORK, read, write, sha

def main():
    if (OUT/'mapping-v2-frozen.json').exists():raise SystemExit('Successor mapping exists')
    first=read(OUT/'mapping-v1-frozen.json');votes=read(WORK/'lexical-selection.json')['caption_variant_votes']
    unknown={r['sign_id']:r for r in read(WORK/'unassigned-image-catalogue.json')}
    classmap={'U180':['P050'],'U044':['P076'],'U012':['P144'],'U136':['P123'],
       'U109':['P270','P264'],'U011':['P270'],'U072':['P270'],'U190':['P271'],
       'U192':['P385'],'U068':['P385'],'U066':['P144'],'U036':['P091'],
       'U149':['P221'],'U177':['P304'],'U075':['P326'],'U069':['P316'],'U137':['P061']}
    schema=read(ROOT/'data/normalized/mayig_sign_schema.json')['signs']
    chart=read(ROOT/'experiments/2026-10-08-chart-reference-audit/chart-reference-v2.1.json')['rows']
    additional=[];local=[]
    for sid in sorted(votes):
        c=classmap[sid];codes={g[1:].zfill(3) for k in c for g in schema[k]['parpola_graphemes']}
        cells=[{'cell_id':f'p{x["pdf_page"]}_c{x["column"]}_r{x["row"]}','code':str(x['code']).zfill(3),
                'class':x['rank'],'numeric_confidence':x['numeric_confidence']} for x in chart if str(x['code']).zfill(3) in codes]
        basis='Additional drawing compared visually with Table 18 family and Mayig/Helsinki reference; direct candidate list retained.'
        if sid=='U149':basis='Triangle form matches the kara class; captions on pages 159 and 170 say sava. Source value association is inconsistent; excluded from lexical scoring.'
        if sid=='U136':basis='Short triple strokes; author queries possible miscopying of full-height tra on pages 72 and 96. Preserve the distinction from B039.'
        additional.append({'sign_id':sid,'mayig_candidates':c,'wells_candidates':sorted({g[1:].zfill(3) for k in c for g in schema[k]['wells_graphemes']}),
              'helsinki_candidates':cells,'component_sequence_candidates':[],'confidence':'medium' if sid in ['U044','U109','U036','U149','U177'] else 'high','basis':basis})
        o=unknown[sid]['first_occurrence']; roles=sorted({v['role'] for v in votes[sid]})
        local.append({'sign_id':sid,'source_pages':sorted({v['page'] for v in votes[sid]}),'caption_proposed_role_candidates':roles,
                     'source_value_consistent_with_visual_Table18_family':sid!='U149',
                     'crop_path':o['image_path'],'pixel_digest':o['pixel_digest'],'witness_occurrences':votes[sid]})
    write(WORK/'additional-valued-catalogue.json',local)
    mapping=first|{'rows':first['rows']+additional,'scope':'First 79 targets plus 17 additional caption-associated drawings; one source value inconsistency retained.'}
    write(OUT/'mapping-v2-frozen.json',mapping)
    freeze={'status':'Exploratory','sha256':sha(OUT/'mapping-v2-frozen.json'),
        'created_utc':__import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(),
        'rows':len(mapping['rows']),'singleton_mayig':sum(len(r['mayig_candidates'])==1 for r in mapping['rows']),
        'ambiguous_mayig':sum(len(r['mayig_candidates'])>1 for r in mapping['rows']),
        'unmapped_mayig':sum(not r['mayig_candidates'] for r in mapping['rows']),
        'wells_covered':sum(bool(r['wells_candidates']) for r in mapping['rows']),
        'helsinki_covered':sum(bool(r['helsinki_candidates']) for r in mapping['rows']),
        'compound_component_mappings':2,'Table18_drawings_mapped':sum(bool(r['mayig_candidates']) for r in first['rows'][:65]),
        'Table18_drawings':65,'original_mapping_sha256':sha(OUT/'mapping-v1-frozen.json')}
    write(OUT/'mapping-freeze-v2.json',freeze)
    # Freeze above before any second-coder packet addition.
    target=RAW/'second-coder-v1'; supplement=target/'additional-forms-v2';supplement.mkdir()
    for r in local:shutil.copyfile(ROOT/r['crop_path'],supplement/f'{r["sign_id"]}.png')
    blank=read(target/'return-template.json')
    blank['rows'] += [{**r,'mayig_candidates':[],'wells_candidates':[],'helsinki_candidates':[],
                        'component_sequence_candidates':[],'confidence':'unmapped','basis':''} for r in additional]
    write(target/'return-template-v2.json',blank)
    (target/'ADDITIONAL-FORMS.md').write_text('''# Additional forms

The 17 neutral drawings in `additional-forms-v2/` extend the initial 79 targets. Use `return-template-v2.json` for all 96. The original instructions and reference images apply. These additions include different renderings and internal-stroke variants; do not assume they are new archaeological signs. No proposed values or first-coder answers are supplied. The original 79-target template and manifest remain preserved.
''',encoding='utf-8')
    files=[{'path':p.relative_to(target).as_posix(),'sha256':sha(p)} for p in sorted(target.rglob('*')) if p.is_file() and p.name!='packet-manifest-v2.json']
    write(target/'packet-manifest-v2.json',{'files':files,'targets':96,'original_crops':79,'additional_crops':17,
              'contains_first_mapping':False,'contains_author_values':False})
    write(OUT/'second-coder-packet-v2.json',{'status':'Awaiting second coding','path':target.relative_to(ROOT).as_posix(),
           'targets':96,'sign_crops':79,'additional_crops':17,'reference_cells':687,
           'mapping_frozen_sha256':freeze['sha256'],'packet_manifest_sha256':sha(target/'packet-manifest-v2.json')})
    print(json.dumps(freeze,indent=2))

if __name__=='__main__':main()
