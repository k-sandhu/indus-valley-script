"""Build a new catalogue and a local-only complete-inscription companion.

The public output contains authored hypotheses, aggregates, sense pointers and
bounded examples. The full source-derived strings and font witnesses stay local.
"""
from pathlib import Path
from collections import Counter
import argparse, hashlib, json, shutil

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
RAW = ROOT / 'data/raw/2026-10-12-anchor-expansion'
OLD = ROOT / 'experiments/2026-10-11-bonta-adversarial/run-v6'
ROLE_LABELS = {'closing':'Closing block', 'counted_entity':'Immediately after W001–W005',
 'nonfinal_entity':'Non-final entity', 'internal_connector':'Strictly internal',
 'opening':'Initial slot', 'unconstrained':'No fixed order constraint'}

def read(p): return json.loads(p.read_text(encoding='utf-8'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):
    with p.open('x',encoding='utf-8') as f:
        json.dump(d,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')

def pass_role(seq,i,role):
    if role=='closing': return i==len(seq)-1 or (i==len(seq)-2 and seq[-1] in {'400','740'})
    if role=='counted_entity': return i>0 and seq[i-1] in {'001','002','003','004','005'}
    if role=='nonfinal_entity': return i<len(seq)-1
    if role=='internal_connector': return 0<i<len(seq)-1
    if role=='opening': return i==0
    return None

def normalized_fit(frame,role):
    if role=='unconstrained': return None
    score=frame['role_scores'][role]
    return dict(role=role,label=ROLE_LABELS[role],observed=score['matching_tokens'],
        expected=score['expected_matching_tokens'],tokens=score['tokens'],
        contradictions=score['contradicting_tokens'],distinct_strings=frame['containing_inscriptions'],
        all_occurrences_matching_inscriptions=score['all_occurrences_matching_inscriptions'],
        any_contradiction_inscriptions=score['any_contradiction_inscriptions'],
        supporting_direction=score['supporting_direction'],empty_sample=score['empty_sample'])

def grade(frames,role,has_anchor,has_picture):
    allf=frames['all_texts'];n=allf['containing_inscriptions']
    if not has_anchor or not has_picture:
        return 'role-only','A specific semantic comparison lacks a selected sense or a documented component.'
    if role=='unconstrained':
        return 'visual-lead','The visible component supplies a comparison. No fixed order constraint was declared for this family.'
    if n<5:
        return 'visual-lead',f'Only {n} distinct complete strings support this code or family; its order remains a sparse test.'
    parts=[frames[k]['role_scores'][role] for k in ['discovery','transfer']]
    if any(x['empty_sample'] for x in parts):
        return 'visual-lead','A component split has no target occurrence; transfer direction cannot be assessed.'
    if all(x['supporting_direction'] for x in parts):
        return 'context-supported','The declared role exceeds its conditional shuffle mean in both component splits, with at least five distinct complete strings. This is structural prioritization.'
    return 'mixed-context','The declared role does not exceed its shuffle mean in both component splits. The picture remains a semantic lead, with this role unresolved.'

def load_senses():
    main=read(HERE/'anchors/senses.json')['rows']
    supplement=HERE/'anchors/supplement-v1.json'
    if supplement.exists():
        x=read(supplement);main+=x.get('rows',x.get('senses',[]))
    by={}
    for a in main:
        k=(a['word'],a['entry_id']);assert k not in by,k;by[k]=a
    return list(by.values())

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--run',default='run-v1');args=parser.parse_args()
    out=HERE/args.run
    if out.exists():raise SystemExit('Preserve completed builds; choose another --run')
    source=read(HERE/'visual/families.json');rawfamilies=[dict(f) for f in source['rows']]
    overlay_path=HERE/'visual/integration-supplement-v1.json'
    overlay=read(overlay_path) if overlay_path.exists() else {}
    corrections={r['family_id']:r for r in overlay.get('family_corrections',[])}
    for f in rawfamilies:
        change=corrections.get(f['family_id'],{})
        for key in ['picture_observation','working_meaning','Sanskrit_comparison_words']:
            if key in change:f[key]=change[key]
        f['graphic_rivals']=f['graphic_rivals']+change.get('extra_graphic_rivals',[])
    context=read(HERE/'context/run-v2/summary.json')
    codes={r['code']:r for r in context['code_rows']}
    family_context={r.get('family_id',r.get('id')):r for r in context['family_rows']}
    base=read(OLD/'catalogue-data.json');before={r['code']:r for r in base['rows']}
    senses=load_senses();sense_by_id={a.get('sense_id','MW-'+a['entry_id']):a for a in senses}
    words={}
    for a in senses:words.setdefault(a['word'],[]).append(a)
    linkfile=HERE/'anchors/family-links-v2.json'
    if not linkfile.exists():linkfile=HERE/'anchors/family-links.json'
    links=read(linkfile)['families']
    if isinstance(links,list):links={r['family_id']:r for r in links}
    conflicts={r['code']:r for r in source.get('chart_conflicts',[])}
    crosswalk=HERE/'visual/chart-crosswalk-audit.json'
    for r in overlay.get('glyph_dispositions',[]):
        if r['suppress_public_glyph']:conflicts[r['code']]=r
        else:conflicts.pop(r['code'],None)
    rawrecords=read(RAW/'context/run-v2/complete-records.json')['records']
    records=[]
    for r in rawrecords:
        records.append(dict(record_id=r['record_id'],object_family_id=r['object_family_id'],
            physical_component_id=r['physical_component_id'],component_id=r['component_id'],
            split=r['split'],cisi=r['source_cisi'],site=r['site'],object_type=r['object_type'],
            codes=r['complete_codes_reading_rtl'],complete_text_length=r['length']))
    # The companion's primary view matches the unique-string calculation.
    # Repeated recorded faces remain available as provenance on each keeper.
    all_faces=len(records);groups={}
    for r in records:groups.setdefault(tuple(r['codes']),[]).append(r)
    keepers=[]
    for sequence,members in groups.items():
        members.sort(key=lambda r:(r['cisi'] in {'-','--',''},tuple(int(x) for x in r['record_id'].split('.'))))
        keeper=dict(members[0]);keeper['identical_record_ids']=[r['record_id'] for r in members]
        keeper['recorded_face_copies']=len(members)
        assert len({r['component_id'] for r in members})==1
        assert len({r['split'] for r in members})==1
        keepers.append(keeper)
    records=keepers
    families=[];membership={};unmatched=[]
    for f in rawfamilies:
        fid=f['family_id'];fc=family_context[fid];role=f['role_predictions']
        assert role in ROLE_LABELS,(fid,role)
        a=[];link=links.get(fid,{})
        for sid in link.get('sense_ids',[]):
            if sid in sense_by_id and sense_by_id[sid] not in a:a.append(sense_by_id[sid])
        for word in link.get('words',f['Sanskrit_comparison_words']):
            for entry in words.get(word,[]):
                if entry not in a:a.append(entry)
            if word not in words:unmatched.append(dict(family_id=fid,word=word))
        correction=corrections.get(fid,{})
        extra=correction.get('Sanskrit_comparison_words',[])+correction.get('extra_anchor_words',[])
        for word in extra:
            for entry in words.get(word,[]):
                if entry not in a:a.append(entry)
        frames=fc['frames'];g,why=grade(frames,role,bool(a),bool(f['picture_observation']))
        fit=normalized_fit(frames['all_texts'],role)
        newcodes=[c for c in f['codes'] if before[c]['tier']=='unreviewed']
        representatives=[]
        for c in f.get('representative_codes',[]):
            if c in f['codes'] and c not in representatives:representatives.append(c)
        rep=(f.get('licensed_representative_seen') or {}).get('code')
        if rep and rep not in representatives:representatives.insert(0,rep)
        ordered=sorted(f['codes'],key=lambda c:(-codes[c]['frames']['all_texts']['containing_inscriptions'],c))
        for c in ordered:
            if c not in representatives:representatives.append(c)
        representatives=representatives[:4]
        n=frames['all_texts']['containing_inscriptions'];longn=frames['length_ge3']['containing_inscriptions']
        physical=frames['all_texts'].get('physical_object_support')
        sentence=f'{n} distinct complete strings contain this family; {longn} have at least three slots.'
        if fit:sentence+=f" The declared rule matches {fit['observed']} of {fit['tokens']} target tokens, with {fit['contradictions']} exceptions."
        fam=dict(family_id=fid,codes=f['codes'],new_codes=newcodes,working_meaning=f['working_meaning'],
            short_meaning=f['working_meaning'].split(';')[0].rstrip('.'),picture_observation=f['picture_observation'],
            visual_scope='Exact-code components were inspected in local font witnesses. Public drawings are representative chart classes; conflicting mappings are suppressed.',
            visual_support=f['visual_support'],role=role,anchors=a,grade=g,grade_reason=why,
            representatives=representatives,context_sentence=sentence,fits=[fit] if fit else [],
            split_fits={k:normalized_fit(frames[k],role) for k in ['discovery','transfer']},
            complete_context=dict(distinct_strings=n,longer_strings=longn,physical_object_support=physical,
                closure_components=frames['all_texts'].get('closure_component_support')),
            rivals=f['graphic_rivals']+link.get('rivals',[]),
            contradiction_note='The rule is a directional enrichment test. Nonmatching occurrences are counted as rule exceptions, without treating them as disproved word meanings. Every occurrence remains in the complete-record view.',
            membership_note='The family pools a shared component. Every member has separate counts and its own evidence tier; rare variants do not inherit the pooled result.',
            semantic_twin_note='Replacing a pictured item with an item-themed name or issuer emblem while preserving the same role gives exactly the same role fits.',
            examples=[])
        families.append(fam)
        for c in f['codes']:assert c not in membership,c;membership[c]=fam
    rows=[]
    for old in base['rows']:
        c=old['code'];f=membership.get(c);cr=codes[c];frames=cr['frames'];af=frames['all_texts']
        if f:
            g,why=grade(frames,f['role'],bool(f['anchors']),bool(f['picture_observation']))
            rolefit=normalized_fit(af,f['role'])
        else:g='inherited' if old['tier']=='inherited' else 'unreviewed';why='No new primary visual family was assigned.';rolefit=None
        conflict=conflicts.get(c)
        row=dict(code=c,sign_id='W'+c,family_id=f['family_id'] if f else None,
            short_meaning=f['short_meaning'] if f else old['meaning'],meaning=f['working_meaning'] if f else old['meaning'],
            grade=g,grade_reason=why,newly_reviewed=bool(f and old['tier']=='unreviewed'),
            previous_tier=old['tier'],previous_meaning=old['meaning'],
            picture_observation=f['picture_observation'] if f else old['picture_evidence'],
            argument=old['argument'],anchors=f['anchors'] if f else old['anchors'],
            role=f['role'] if f else 'unconstrained',fits=[rolefit] if rolefit else [],
            drawings=[] if conflict and conflict.get('suppress_public_glyph',True) else old['drawings'],
            conflicting_class=conflict,visual_scope=(str(conflict.get('font_observation',''))+' '+str(conflict.get('mapped_class_observation',''))) if conflict else (f['visual_scope'] if f else old['picture_evidence']),
            context=dict(distinct_strings=af['containing_inscriptions'],longer_strings=frames['length_ge3']['containing_inscriptions'],
                tokens=af['tokens'],physical_objects=af['physical_object_support'],closure_components=af['closure_component_support']),
            context_note='A font drawing is a glyph witness; artifact-level identity and interpretation remain source-dependent.',
            full_context=cr,inherited_proposals=old['inherited_proposals'])
        if c=='169':
            row.update(short_meaning='Paired ovals or paired units',meaning='Paired ovals or paired units; suspended loads remain a rival',
                picture_observation='Two closed ovals are joined horizontally. No pole or suspension cord is visible in this font witness.',
                anchors=[a for a in senses if a['word'] in {'yuga (pair)','dvaya'}],
                context_note='The original pooled carrier family is retained for its frozen context test. This member is described by its paired-oval component; its closing fit does not identify a carrier.')
        rows.append(row)
    by={r['code']:r for r in rows}
    # Source-derived complete strings only enter this ignored local companion.
    for r in records:
        r['role_walk']=[by[c]['role'] if by[c]['family_id'] else 'unresolved' for c in r['codes']]
        r['tests']=[]
        for fid in sorted({by[c]['family_id'] for c in r['codes'] if by[c]['family_id']}):
            f=next(x for x in families if x['family_id']==fid)
            if f['role']=='unconstrained':continue
            slots=[i for i,c in enumerate(r['codes']) if c in f['codes']]
            passed=sum(pass_role(r['codes'],i,f['role']) for i in slots)
            r['tests'].append(dict(family_id=fid,role=ROLE_LABELS[f['role']],tested=len(slots),passed=passed,compatible=passed==len(slots)))
        r['search_text']=' '.join(['W'+c+' '+by[c]['short_meaning']+' '+' '.join(a['word'] for a in by[c]['anchors']) for c in r['codes']])
    # A small attributed selection of complete short strings, plus clipped
    # counterexamples for other families. No exhaustive string list is public.
    selected=[];used_records=set();source_url='https://github.com/yajnadevam/lipi/tree/fc8813a52e183d19c441631dc26c33a4dccbea39'
    order_grade={'context-supported':0,'visual-lead':1,'mixed-context':2,'role-only':3}
    families.sort(key=lambda f:(order_grade.get(f['grade'],4),-len(f['new_codes']),-f['complete_context']['distinct_strings'],f['family_id']))
    for f in families:
        candidates=[r for r in records if any(c in f['codes'] for c in r['codes']) and r['cisi'] not in {'-','--',''}]
        # Selection rule favours intact short records, then deterministic hash.
        candidates.sort(key=lambda r:(len(r['codes'])>3,hashlib.sha256((f['family_id']+'|'+r['record_id']).encode()).hexdigest()))
        for r in candidates:
            if r['record_id'] in used_records:continue
            if len(selected)>=36:break
            seq=r['codes'];i=next(i for i,c in enumerate(seq) if c in f['codes'])
            start=max(0,min(i-1,len(seq)-3)) if len(seq)>3 else 0
            e={k:r[k] for k in ['record_id','object_family_id','cisi','site','object_type','complete_text_length','split']}
            e.update(codes=seq[start:start+3],start_slot_one_based=start+1,excerpt_only=len(seq)>3,
                family_id=f['family_id'],role_walk=r['role_walk'],source_url=source_url,
                purpose='Bounded attributed evidence excerpt for an authored sign-family analysis; full source strings remain local.')
            f['examples'].append(e);selected.append(e);used_records.add(r['record_id']);break
    public_complete=[{k:e[k] for k in ['record_id','object_family_id','cisi','site','object_type','complete_text_length','split','codes','role_walk','source_url']} for e in selected if not e['excerpt_only']]
    glyph_index=read(ROOT/'data/raw/2026-10-08-bonta-extension/source-2026-10-09/glyph-witness-index.json')
    glyphs={r['code']:r['path'] for r in glyph_index['rows'] if r['drawing_present']}
    assert len(rows)==713
    assert len(membership)==source['counts']['assigned_codes']
    assert all(len(e['codes'])<=3 for e in selected)
    summary=dict(codes=len(rows),families=len(families),newly_reviewed_codes=sum(r['newly_reviewed'] for r in rows),
        context_supported_codes=sum(r['newly_reviewed'] and r['grade']=='context-supported' for r in rows),
        tiers=dict(Counter(r['grade'] for r in rows)),new_tiers=dict(Counter(r['grade'] for r in rows if r['newly_reviewed'])),
        unresolved_codes=sum(not r['family_id'] for r in rows),senses=len(senses),public_examples=len(selected),
        complete_short_public_examples=len(public_complete),complete_local_strings=len(records),recorded_complete_faces=all_faces,
        chart_conflicts_suppressed=len(conflicts),unmatched_requested_anchor_words=unmatched)
    data=dict(title='Expanded anchor families and complete inscriptions',date='2026-10-12',run=args.run,
        scope='Visible components and selected Sanskrit senses supply ranked working meanings. A fixed map is tested across complete inscriptions, with contradictions and unresolved slots retained. The component split measures stability on the known corpus.',
        summary=summary,families=families,rows=rows,public_complete_records=public_complete,
        source_scope='Licensed chart classes and bounded excerpts are public; full corpus strings and exact font witnesses remain local.')
    out.mkdir(exist_ok=False)
    write(out/'catalogue-data.json',data);write(out/'sanskrit-senses.json',dict(rows=senses))
    write(out/'example-provenance.json',dict(scope='Selected bounded excerpts only; local companion retains all complete strings.',examples=selected))
    write(out/'coverage.json',summary)
    template=(HERE/'catalogue-template.html').read_text(encoding='utf-8')
    (out/'catalogue.html').write_text(template.replace('__CATALOGUE_DATA__',json.dumps(data,ensure_ascii=False).replace('</',r'<\/')),encoding='utf-8')
    local_out=RAW/args.run;local_out.mkdir(exist_ok=False)
    companion=dict(scope='Local-only source-derived full strings and font pointers; not part of the public package.',run=args.run,
        distinct_complete_strings=len(records),recorded_complete_faces=all_faces,
        input_sha256=sha(ROOT/'data/normalized/lipi_clean_rtl_singleline.jsonl'),glyphs=glyphs,records=records)
    write(local_out/'companion.json',companion)
    # A stable local projection is replaceable; every dated companion is frozen.
    (RAW/'companion.json').write_bytes((local_out/'companion.json').read_bytes())
    inputs=[HERE/'visual/families.json',HERE/'visual/freeze-manifest.json',HERE/'context/run-v2/summary.json',HERE/'anchors/senses.json',linkfile,OLD/'catalogue-data.json',HERE/'catalogue-template.html',Path(__file__)]
    for p in [HERE/'anchors/supplement-v1.json',crosswalk,overlay_path]:
        if p.exists():inputs.append(p)
    for name in ['integrate.py','catalogue-template.html']:(out/name).write_bytes((HERE/name).read_bytes())
    write(out/'build-manifest.json',dict(status='Exploratory complete-inscription extension',
        inputs=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in inputs],
        local_sources=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in [RAW/'context/run-v2/complete-records.json',ROOT/'data/normalized/lipi_clean_rtl_singleline.jsonl',ROOT/'data/lipi/src/assets/fonts/indus-font.woff2']],
        local_companion=dict(path=(local_out/'companion.json').relative_to(ROOT).as_posix(),sha256=sha(local_out/'companion.json')),
        outputs=[dict(path=p.relative_to(out).as_posix(),sha256=sha(p)) for p in out.rglob('*') if p.is_file()]))
    print(json.dumps(summary,ensure_ascii=False))

if __name__=='__main__':main()
