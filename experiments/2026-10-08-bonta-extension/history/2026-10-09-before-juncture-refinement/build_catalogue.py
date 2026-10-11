"""Build a reviewable, full-inventory semantic hypothesis catalogue."""
from pathlib import Path
from collections import Counter
import argparse, csv, html, json, shutil
from analyze import ROOT, HERE, RAW, write, load, slp, iast, normalize, sha
from semantic_hypotheses import class_hypothesis, modifiers, INHERITED
from unmapped_hypotheses import ROWS as VISUAL
from new_anchors import ANCHORS

SOURCES=[
 {'id':'Bonta2024-ed2','title':'A Partial Decipherment of the Indus Valley Script: Proposed Phonetic and Logographic Values for Selected Indus Signs and Readings of Indus Texts (2nd ed.)',
  'author':'Steven C. Bonta','year':2024,'url':'https://www.academia.edu/120435855/A_Partial_Decipherment_of_the_Indus_Valley_Script_Proposed_Phonetic_and_Logographic_Values_for_Selected_Indus_Signs_and_Readings_of_Indus_Texts_2nd_ed_',
  'local_path':'data/raw/2026-10-08-bonta-review/papers/A_Partial_Decipherment_of_the_Indus_Vall.pdf','pages_used':[79,80,81,82,83,252,253,254,255,256],
  'use':'Table 18 values, glyph witnesses, mixed sound/logogram structure and concluding advice on remaining signs and ligatures.', 'rights':'rights-unverified; local-only'},
 {'id':'Bonta-lecture07','title':'Bonta lecture 7','url':'https://www.youtube.com/watch?v=WYu1lqwQ5B0',
  'use':'Previously reviewed anchor and dictionary-intersection procedure; no new viewing claimed in this pass.'},
 {'id':'MW1899-Cologne','title':'Monier-Williams Sanskrit-English Dictionary (1899), Cologne digitization',
  'url':'https://www.sanskrit-lexicon.uni-koeln.de/scans/MWScan/2020/web/webtc2/index.php',
  'repository':'https://github.com/sanskrit-lexicon/csl-orig','commit':'55e8addbd96e8d9001b8789026b026763f4049c1',
  'local_path':'data/raw/2026-10-08-bonta-review/acquisition-2026-10-08-v1/mw.txt',
  'use':'Exact headwords, homonyms, definition subentries and full/normalized string searches. Each comparison has entry IDs and print-page columns.',
  'chronology':'Vedic and later attestations coexist. Attestation verifies a Sanskrit comparison, not an Indus-period word.'},
 {'id':'MW-web-bhara','title':'Monier-Williams Sanskrit-English Dictionary, University of Hyderabad interface, bh section',
  'url':'https://sanskrit.uohyd.ac.in/SKT/MW/185.html','use':'Internet check of burden/load vocabulary; local Cologne records distinguish bhara, bhāra and bhārika.'},
 {'id':'MW-web-yava','title':'Monier-Williams page 847 scan',
  'url':'https://www.sanskrit-lexicon.uni-koeln.de/scans/MWScan/MWScanpdf/mw0847-yamalacchada.pdf',
  'use':'Search results expose barley compounds; PDF screenshot timed out, so the actual definition check uses the local dictionary entries.'},
 {'id':'Rao2018','title':'The Indus Script and Economics. A Role for Indus Seals and Tablets in Rationing and Administration of Labor',
  'author':'Rajesh P. N. Rao','year':2018,'url':'https://arxiv.org/abs/1812.00049',
  'use':'A prior proposal connects miniature tablets and porter/labour rationing. It informs the labour scenario and is not independent verification of a reading.'},
 {'id':'HARP-sealing','title':'Seal impression','author':'Harappa Archaeological Research Project',
  'url':'https://www.harappa.com/slide/seal-impression',
  'use':'Primary public photograph and description of an Early Harappan sealing with ladder motifs and a probable bundle-sealing use. No object concordance or new inscription imported.'},
 {'id':'HARP-food','title':'What kinds of things did the Indus people eat?',
  'url':'https://www.harappa.com/answers/what-kinds-things-did-indus-people-eat',
  'use':'Archaeologists’ account of crops and animal resources informs commodity alternatives; it gives no sign-to-word anchor.'},
 {'id':'Kenoyer2004-textiles','title':'Ancient Textiles of the Indus Valley Region','author':'Jonathan Mark Kenoyer','year':2004,
  'url':'https://www.harappa.com/sites/default/files/pdf/Kenoyer2004%20IndusTextilesfinal.pdf',
  'use':'Author paper describes fabric impressions, fibers and production tools; supports considering textile goods, with no claimed correspondence to W825.'},
 {'id':'Dholavira-water','title':'Dholavira and Its Mysterious Sign Board',
  'url':'https://www.harappa.com/blog/dholavira-and-its-mysterious-sign-board',
  'use':'Public report of excavator Bisht’s reservoir and drainage observations motivates a water-related alternative. This pass read the web account, not the complete excavation report.'},
 {'id':'Lipi','title':'Lipi corpus and catalogue drawing font','url':'https://github.com/yajnadevam/lipi',
  'commit':'fc8813a52e183d19c441631dc26c33a4dccbea39',
  'use':'Observed signs, object families and U+E000+decimal-code drawings. Upstream proposed decipherments, xlits and translation outputs are excluded.',
  'rights':'rights-unverified; raw sequences, font and rendered drawings local-only'},
 {'id':'Mayig','title':'Indus Valley Script Corpus','author':'Michael Carlson','year':2024,
  'url':'https://github.com/mayig/indus-valley-script-corpus','commit':'ad2f1e218a34b8c33c57de0d6cb8d99272765bbb',
  'use':'Direct many-to-many graphic classes and descriptions. No transitive equivalence is inferred.','rights':'MIT for covered source; raw corpus local-only'},
 {'id':'Helsinki1979','title':'A Concordance to the Texts in the Indus Script','authors':['Kimmo Koskenniemi','Asko Parpola'],'year':1979,
  'local_path':'output/chart_atlas/index.html','use':'Existing chart cells supply an alternative representative class drawing.',
  'rights':'CC BY 4.0 source with existing atlas attribution; source ambiguity remains.'}
]

# These refinements were selected after inspecting the expanded search output.
# They use context and shape together; none is a recovered pronunciation.
REFINEMENTS={
 '233':{'meaning':'heavy/large asset denomination or load class','words':['ati','māna','bhāra'],
        'rationale':'Under N01 = bhāra, W233–W151 permits atibhāra, “excessive burden”. The fish’s internal bar also distinguishes a grade. The working meaning is a larger/heavier class; the sound ati remains optional.',
        'headword':'atiBAra','entry_ids':['2710','2710.1'],'anchor':'N01','residual':'ati'},
 '231':{'meaning':'provisioned or collected asset unit','words':['sambhāra','māna'],
        'rationale':'Under N01 = bhāra, W231–W151 permits sambhāra, collection/provisions. This suggests an organized supply lot alongside the standard-weight interpretation.',
        'headword':'samBAra','entry_ids':['237019','237020'],'anchor':'N01','residual':'sam'},
 '204':{'meaning':'shared processed produce or share-bearing commodity/name element','words':['sabhāga','śasya','vastra'],
        'rationale':'Under N12 = bhāga, W204–W540 permits sabhāga, having a share. The paired leaves support a joined/processed-product candidate. Sa is an optional compound modifier.',
        'headword':'saBAga','entry_ids':['232878'],'anchor':'N12','residual':'sa'}
}

FAMILY_ANCHORS=[(1,6,['N01']),(22,42,['N08','N09','N10']),
 (66,74,['N11']),(75,84,['N06']),(91,102,['N02','N07','N09']),
 (103,113,['N14']),(190,192,['N03']),(219,239,['N12']),
 (240,258,['N13']),(259,275,['N04']),(285,309,['N05','N16']),
 (355,376,['N04','N06']),(377,384,['N15']),(385,396,['N08'])]

def attestations(words, entries):
    return {w:[{'entry_id':e['entry_id'],'page_column':e['page_column']} for e in entries.get(slp(w),[])] for w in words}

def inherited_reading(rs):
    labels=list(dict.fromkeys(r['label'] for r in rs))
    meanings=[INHERITED[x][0] for x in labels if x in INHERITED]
    roles=[INHERITED[x][1] for x in labels if x in INHERITED]
    sounds=list(dict.fromkeys(iast(v) for r in rs for v in r['slp1']))
    return {'meaning':' / '.join(meanings) if meanings else 'sound component in a personal name or title: '+', '.join(sounds),
       'sanskrit_comparisons':sounds,'role':roles[0] if roles else 'sound',
       'alternatives':['a different sound/name component','an administrative or commodity label'],
       'shape_rationale':'Bonta’s Table 18 proposal imported through the preserved first-coder graphic crosswalk.'}

def chart_paths(code, classes, schema, chart):
    result=[]
    for p in classes:
        for v in schema[p]['parpola_graphemes']:
            n=int(v[1:])
            for r in chart.get(n,[]):
                path=f"output/chart_atlas/cells/p{r['pdf_page']}_c{r['column']}_r{r['row']}.png"
                if (ROOT/path).is_file():
                    result.append({'path':path,'graphic_class':p,'parpola_candidate':v,'confidence':r['numeric_confidence']})
    return result[:4]

def lexical_info(code, base, pref, alt, counts):
    p=pref.get(code,{}); a=alt.get(code,{})
    common=[]; by={r['normalized_slot']:r for r in a.get('top',[])}
    for r in p.get('top',[]):
        s=by.get(r['normalized_slot'])
        if s and min(r['exact_context_count'],s['exact_context_count'])>=2:
            common.append({'slot_iast':r['slot_iast'],'preferred_exact_contexts':r['exact_context_count'],
                'alternative_exact_contexts':s['exact_context_count'],
                'preferred_support_fraction':r['support_fraction'],
                'alternative_support_fraction':s['support_fraction']})
    return {'baseline_patterns':base.get(code,{}).get('pattern_count',0),
            'preferred_patterns':p.get('pattern_count',0),'alternative_patterns':a.get('pattern_count',0),
            'new_anchor_windows':counts.get(code,0),'preferred_candidate_classes':p.get('candidate_classes',0),
            'preferred_full_intersection_classes':p.get('full_intersection_classes',0),
            'alternative_full_intersection_classes':a.get('full_intersection_classes',0),
            'preferred_top':p.get('top',[])[:3],'alternative_top':a.get('top',[])[:3],
            'repeated_exact_candidates_in_both_scenarios':common,
            'interpretation':'Dictionary residuals are optional compound/name hypotheses. Their rank is not a probability or a semantic assignment.'}

def choose_priority(d, h, basis):
    n=d['complete_unique_frame_tokens']
    if n<3:return 'C'
    if n>=10 and h['role'] in {'quantity','grammar','labour','title','institution','operation'}:
        return 'A' if basis!='inherited Bonta proposal' else 'B'
    return 'B'

def make_report(out, rows, summary, examples, sources):
    q=summary
    anchors=load(str((out/'new-anchors.json').relative_to(ROOT)))
    text=f'''# Exploratory extension of Bonta’s sign proposals

This run assigns a preferred working interpretation to all {q['catalogue_codes']} Wells codes in the available inventory. {q['new_assignment_codes']} entries are new project assignments; {q['inherited_codes']} retain Bonta’s mapped proposals. The new assignments include semantic labels, occupational and institutional readings, quantities and grammatical functions. They are conditional hypotheses in a mixed sound/logogram and administrative model, with Sanskrit used as a comparison vocabulary. No entry has an authenticated sound or meaning.

The [searchable visual catalogue](catalogue.html), [complete table](candidates.csv) and [structured catalogue](candidates.json) give each code’s preferred meaning, alternatives, dictionary entry IDs, graphic basis, corpus counts and lexical-search outcomes. The catalogue displays locally rendered drawings and, where available, a Helsinki reference-class image. Those are catalogue drawings, not new artifact photographs. Full inscription contexts and the Lipi drawing witnesses remain under the local-only `data/raw/2026-10-08-bonta-extension/` directory.

## New anchors and how they extend the map

The sixteen new comparisons cover seventeen previously unseeded codes. Bhāra and gaṇa are particularly useful working anchors because their proposed roles can be compared with many recurring contexts. The barley, water, wheel and hall comparisons have much smaller inscription samples. Dictionary attestations establish that the proposed Sanskrit vocabulary exists; archaeological reports help choose useful economic alternatives. Neither source supplies an excavated sign-to-word equivalence.

| Anchor | Wells code(s) | Preferred working meaning | Sanskrit comparison | Complete-sequence occurrences |
|---|---|---|---|---:|
'''
    by={r['code']:r for r in rows}
    for a in anchors:
        n=sum(by[w]['observations']['complete_unique_frame_tokens'] for w in a['codes'])
        text+=f"| {a['id']} | {', '.join('W'+w for w in a['codes'])} | {a['meaning']} | {', '.join(a['sanskrit_comparisons'])} | {n} |\n"
    text+='''
New anchors guide related forms as well as dictionary windows. The porter comparison extends to framed, paired and vessel-headed load carriers. The cultivator comparison extends to human/tool compounds. The field/store comparison extends to bounded and divided rectangles, while the cloth comparison supplies an alternative for cross-hatched panels and leaves. These connections are recorded per sign, including the competing possibility that a modification changes sound or graphic form rather than meaning.

Three interpretations were refined after the expanded dictionary search. W233 becomes a heavy/large asset class under the *ati-bhāra* comparison; W231 becomes a provisioned/collected asset unit under *sam-bhāra*; W204 becomes a shared processed product or share-bearing name element under *sa-bhāga*. These are deliberate post-outcome hypotheses. The dictionary gives several rival completions, and no common residual covers every searched context for these signs.

## Observations and procedure

The full inventory contains 712 non-editorial codes observed on 5,680 faces, plus one additional direct crosswalk code. The clean single-line right-to-left frame has 2,930 faces and 1,859 distinct complete sequences. Context counts use those distinct sequences; whole-corpus counts retain face observations. Object-family support is preserved separately. Signs 000 and 999, used for damage and spacing, are excluded from semantic coverage.

The first pass imports the second edition’s Table 18 through the preserved graphic crosswalk and searches two- and three-sign windows with one unknown slot. It uses 194,059 alphabetic Monier-Williams headwords. Exact matching and a separate tolerant matching layer collapse specified vowel-length, stop and sibilant distinctions. Windows are assumed candidate words; they are not independently identified word boundaries. Exact contexts receive an additional half-point in the ranking, and candidates must contain a vowel and occupy at most six letters. These search choices favour short and common residuals, which remain visible as alternatives.

The October 9 amendment adds full Sanskrit comparison stems in two scenarios: the preferred new anchors and their stated alternatives. Earlier files remain unchanged. Visual reasoning used four sheets of direct graphic classes and five further sheets covering the 215 codes without a direct class mapping. For every code, the map combines that drawing comparison with its position and neighbours. No additional VLM API batch, trained semantic model or calibrated posterior was run.

Priority A marks a recurring code whose proposed role fits its visible form and placement. B marks a plausible but weaker combined case. C marks a rare or predominantly pictorial assignment. These priorities compare hypotheses within the chosen model. They are not percentages of historical correctness. Inherited Bonta proposals remain marked as inherited, with the original values visible.

## Computed outcomes

'''
    text+=f"The preferred-anchor search considered {q['search']['scenarios']['preferred']['searched_unknown_codes']} unknown codes. New-anchor windows involved 111 codes in 256 distinct combinations. The alternative-anchor scenario searched the same combinations. There were {q['search']['scenarios']['preferred']['nonempty_full_intersections']} nonempty full intersections in the preferred scenario and {q['search']['scenarios']['alternative']['nonempty_full_intersections']} in the alternative scenario; many intersections have only one context or several competing completions. The output records their denominators and candidate counts.\n\n"
    text+=f"The catalogue contains {q['priority_counts'].get('A',0)} A, {q['priority_counts'].get('B',0)} B and {q['priority_counts'].get('C',0)} C assignments. {q['codes_with_new_anchor_connections']} entries have an explicit connection to a new anchor. All 713 codes have a local font drawing witness; 215 also have a separately authored interpretation from the additional drawing inspection.\n\n"
    text+='''## Worked account interpretations

The examples below show how the working map turns short observed strings into tentative account structures. The exact record, object-family IDs, sequence and slot locations are kept in `worked-examples.json` under the local-only run directory. Reading order follows the clean RTL frame. Proposed syllables are retained where a name remains unresolved; logographic labels are glossed in English. Each account explanation is an authored scenario, and several shown structures contain unresolved name components or grammatical relations.

'''
    for e in examples:
        text+=f"- **{e['label']}** ({e['record_id']}, {e['source_cisi']}): {e['description']}\n"
    text+='''
## Further resolution

The next useful comparisons are whether the staff-holder and divided-store signs substitute in the same positions, whether leaf/fish grades track numerical quantities, and whether paired carriers systematically accompany larger allocations. Longer strings, securely registered new photographs and artifact-use traces could separate goods, occupation and personal-name readings. The current catalogue keeps those alternatives accessible without waiting for such material.

## Sources

'''
    for s in sources:
        url=s.get('url') or '../../../'+s['local_path']
        text+=f"- [{s['title']}]({url}). {s['use']}\n"
    text+='''
## Reproduction and preservation

`analyze.py` produces a new first-pass directory, `extend_search.py` produces a new anchor-scenario directory, and `build_catalogue.py` adds the authored map and review files to that directory. `render_glyphs.py` renders locally retained source drawings. Each creation refuses an existing main run or final catalogue. Source hashes and the selected code versions are recorded. Exact search witnesses, dictionary excerpts and annotated full sequences remain local. The repository contains our code, hypotheses, aggregates, source pointers and the HTML viewer; it does not bundle the unresolved-rights corpus or font drawings.
'''
    (out/'REPORT.md').write_text(text,encoding='utf-8')

def main():
    p=argparse.ArgumentParser();p.add_argument('--run',default='run-2026-10-09-v2')
    p.add_argument('--search-run',help='Reuse a preserved lexical endpoint in a new catalogue directory.')
    args=p.parse_args()
    out=HERE/args.run; raw=RAW/args.run
    if args.search_run:
        source=HERE/args.search_run
        out.mkdir(parents=True,exist_ok=False); raw.mkdir(parents=True,exist_ok=False)
        for name in ['new-anchors.json','input-manifest.json','preferred-lexical-summary.json',
                     'alternative-lexical-summary.json','preferred-new-anchor-context-counts.json',
                     'alternative-new-anchor-context-counts.json','search-summary.json']:
            shutil.copyfile(source/name,out/name)
        write(out/'projection-manifest.json',{'status':'Exploratory catalogue projection',
           'preserved_search_run':args.search_run,'search_rerun':False,
           'revision':'Select illustrative account examples by the named anchor relationship. The final drawing review corrects descriptions and associated senses for W383, W951 and W953; earlier catalogue projections are preserved.',
           'source_files':{name:sha(source/name) for name in ['new-anchors.json','preferred-lexical-summary.json','alternative-lexical-summary.json']}})
    if (out/'candidates.json').exists():raise FileExistsError('Preserve final catalogue; choose a new run.')
    ds=load('experiments/2026-10-08-bonta-extension/run-2026-10-08-v1/dossiers.json')
    base=load('experiments/2026-10-08-bonta-extension/run-2026-10-08-v1/lexical-summary.json')
    inherited=load('experiments/2026-10-08-bonta-extension/run-2026-10-08-v1/inherited-seeds.json')['by_wells']
    pref=load(str((out/'preferred-lexical-summary.json').relative_to(ROOT)))
    alt=load(str((out/'alternative-lexical-summary.json').relative_to(ROOT)))
    cnt=load(str((out/'preferred-new-anchor-context-counts.json').relative_to(ROOT)))
    entries=load('data/raw/2026-10-08-bonta-extension/run-2026-10-08-v1/dictionary-index.json')
    glyphs={r['code']:r for r in load('data/raw/2026-10-08-bonta-extension/source-2026-10-09/glyph-witness-index.json')['rows']}
    schema=load('data/normalized/mayig_sign_schema.json')['signs']
    chart={}
    for r in load('experiments/2026-10-08-chart-reference-audit/chart-reference-v2.1.json')['rows']:
        chart.setdefault(r['code'],[]).append(r)
    new={w:a for a in ANCHORS for w in a['codes']}
    missing={d['code'] for d in ds['rows'] if not d['mayig_candidates']}-set(VISUAL)
    assert not missing, missing
    rows=[]
    for d in ds['rows']:
        code=d['code']; ps=d['mayig_candidates']; anchor_ids=[]
        if code in inherited:
            h=inherited_reading(inherited[code]);basis='inherited Bonta proposal'
        elif code in new:
            a=new[code];h={**a,'alternatives':['an occupational or personal-name component','a commodity/measure or institution alternative: '+a['alternative_probe']]}
            basis='new Sanskrit anchor';anchor_ids=[a['id']]
        elif ps:
            hs=[class_hypothesis(p) for p in ps];assert all(hs),(code,ps)
            h=hs[0];basis='direct graphic class and observed context'
            for p in ps:
                n=int(p[1:])
                for lo,hi,ids in FAMILY_ANCHORS:
                    if lo<=n<=hi:anchor_ids.extend(ids)
            if len(hs)>1:
                h={**h,'alternatives':list(dict.fromkeys(h['alternatives']+[v['meaning'] for v in hs[1:]]))}
        else:
            h=VISUAL[code];basis='new inspection of unmapped catalogue drawing';anchor_ids=h['new_anchor_connections']
        words=list(h['sanskrit_comparisons']); meaning=h['meaning']
        refinement=REFINEMENTS.get(code)
        if refinement and code not in inherited:
            meaning=refinement['meaning'];words=refinement['words'];basis+='; post-outcome lexical refinement'
            anchor_ids=list(anchor_ids)+[refinement['anchor']]
        at=attestations(words,entries)
        mods=modifiers(' '.join(d['shape_descriptions']))
        row={'code':code,'sign_id':'W'+code,'preferred_meaning':meaning,'sanskrit_comparisons':words,
          'role':h['role'],'priority':choose_priority(d,h,basis),'basis':basis,
          'inherited':code in inherited,'new_anchor_id':new[code]['id'] if code in new else None,
          'new_anchor_connections':sorted(set(anchor_ids)),
          'alternatives':h['alternatives'],'shape_rationale':h['shape_rationale'],
          'modifier_hypotheses':mods,'lexical_refinement':refinement,
          'dictionary_attestations':at,'graphic_classes':ps,
          'graphic_class_descriptions':d['shape_descriptions'],
          'font_drawing':glyphs[code],'reference_class_drawings':chart_paths(code,ps,schema,chart),
          'inherited_proposals':inherited.get(code,[]),
          'observations':{k:v for k,v in d.items() if k not in {'code','mayig_candidates','shape_descriptions'}},
          'lexical_search':lexical_info(code,base,pref,alt,cnt),
          'context_witness_pointer':f"data/raw/2026-10-08-bonta-extension/run-2026-10-08-v1/observation-witnesses.json#/{code}",
          'visual_review_correction':code in {'383','951','953'}}
        # Preserve source phonetic variants; dictionary non-attestation is allowed for a syllable.
        if code not in inherited:assert all(at.values()), (code,at)
        rows.append(row)
    search=load(str((out/'search-summary.json').relative_to(ROOT)))
    summary={'status':'Exploratory semantic hypothesis catalogue','catalogue_codes':len(rows),
      'observed_codes':ds['counts']['observed_codes'],'inherited_codes':sum(r['inherited'] for r in rows),
      'new_assignment_codes':sum(not r['inherited'] for r in rows),
      'new_anchor_families':len(ANCHORS),'new_anchor_codes':len(new),'post_outcome_refinements':len(REFINEMENTS),
      'priority_counts':dict(Counter(r['priority'] for r in rows)),
      'role_counts':dict(Counter(r['role'] for r in rows)),
      'new_role_counts':dict(Counter(r['role'] for r in rows if not r['inherited'])),
      'codes_with_new_anchor_connections':sum(bool(r['new_anchor_connections']) for r in rows),
      'inspected_additional_drawing_codes':len(VISUAL),'local_font_drawing_codes':sum(r['font_drawing']['drawing_present'] for r in rows),
      'codes_with_reference_class_drawing':sum(bool(r['reference_class_drawings']) for r in rows),
      'codes_with_new_anchor_lexical_windows':len(cnt),'search':search,
      'source_observation_counts':ds['counts'],
      'publication':'local workspace/private knowledge record; no external publication',
      'code_hashes':{x:sha(HERE/x) for x in ['build_catalogue.py','semantic_hypotheses.py','unmapped_hypotheses.py','new_anchors.py']}}
    write(out/'candidates.json',{'summary':summary,'rows':rows})
    write(out/'construction-summary.json',summary)
    sources=[]
    for s in SOURCES:
        r={**s,'accessed_or_reused':'2026-10-09'}
        if s.get('local_path') and (ROOT/s['local_path']).is_file():r['sha256']=sha(ROOT/s['local_path'])
        sources.append(r)
    write(out/'sources.json',sources)
    with (out/'candidates.csv').open('w',encoding='utf-8-sig',newline='') as f:
        fields=['sign_id','preferred_meaning','sanskrit_comparisons','role','priority','basis','inherited','new_anchor_connections','alternatives','whole_corpus_tokens','complete_unique_frame_tokens','new_anchor_windows']
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader()
        for r in rows:
            x={k:r[k] for k in fields if k in r}
            for k in ['sanskrit_comparisons','alternatives','new_anchor_connections']:x[k]='; '.join(x[k])
            x.update({k:r['observations'][k] for k in ['whole_corpus_tokens','complete_unique_frame_tokens']})
            x['new_anchor_windows']=r['lexical_search']['new_anchor_windows'];writer.writerow(x)
    contexts=load('data/raw/2026-10-08-bonta-extension/run-2026-10-08-v1/observation-witnesses.json')
    by={r['code']:r for r in rows};worked=[]
    for code,label,description in [
      ('151','Transport obligation','A carried-load or porter category follows an accounted party or asset category. The recurring final placement makes this a useful transport-service scenario.'),
      ('400','Closing account category','The comb-like total/category can follow the jar. A working structure is a named party’s batch or assessment, with the comb supplying the account class.'),
      ('130','Agricultural worker','The person/tool sign supplies a cultivator or agricultural obligation within a name/title or goods account.'),
      ('825','Textile allotment','The cross-hatched leaf is read as a cloth lot; a nearby count specifies the allocation. A registered estate/weight class remains an alternative.'),
      ('233','Heavy load class','The fish grade before the porter/load sign is interpreted as a larger load class. The Sanskrit atibhāra comparison supplies an optional semantic connection.'),
      ('204','Share-bearing product','The paired-leaf sign near the opposed-triangle share anchor supplies a shared product or share-bearing name element, under the sabhāga comparison.')]:
        candidates=contexts.get(code,[])
        if not candidates:continue
        target={'151':'740','400':'740','233':'151','204':'540','825':'002'}.get(code)
        e=min(candidates,key=lambda x:(0 if target and target in x['sequence'] else 1,len(x['sequence']),x['record_id']))
        gloss=[{'code':s,'meaning':by[s]['preferred_meaning'] if s in by else 'editorial marker',
                'inherited':by[s]['inherited'] if s in by else False} for s in e['sequence']]
        worked.append({**e,'label':label,'description':description,'working_glosses':gloss,
                       'status':'constructed account interpretation; source sequence retained locally'})
    write(raw/'worked-examples.json',worked)
    make_report(out,rows,summary,worked,sources)
    template=(HERE/'catalogue-template.html').read_text(encoding='utf-8')
    payload=json.dumps({'summary':summary,'rows':rows},ensure_ascii=False).replace('</','<\\/')
    (out/'catalogue.html').write_text(template.replace('__CATALOGUE_DATA__',payload),encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False,indent=2),flush=True)

if __name__=='__main__':main()
