"""Make readable comparisons and a lossless quantity export from the frozen merge."""
from pathlib import Path
import csv
import hashlib
import json

P=Path(__file__).resolve().parent
R=P/'run-v3'
rows=json.loads((R/'observations.json').read_text(encoding='utf-8'))
towns=json.loads((R/'towns.json').read_text(encoding='utf-8'))
sources=json.loads((R/'sources.json').read_text(encoding='utf-8'))
byid={r['id']:r for r in rows}
labels={'chanhu-daro':'Chanhudaro','mohenjo-daro':'Mohenjo-daro'}
def name(t): return labels.get(t,t.capitalize())

sections=[('Setting and extent',['location_setting','settlement_extent'],3),
          ('Occupation and chronology',['occupation_chronology'],7),
          ('Materials by episode',['construction_materials'],5),
          ('Structures and reported quantities',['building_inventory','quantities_and_scope'],5),
          ('Changes to the urban framework',['incremental_alteration','replanning_and_retention','layout_and_access'],6),
          ('Writing and archaeological context',['documentary_context'],4)]
lines=['# Twelve source-backed town profiles','',
       'This comparison selects assertions from the complete register. Each ID resolves in `run-v3/observations.json` and retains a source and exact locator. The source index records URLs, local files and hashes. Selection favours phase relations and scoped quantities. A missing field is an acquisition or join gap, and no unreported structure becomes a zero. These are selected cases with uneven exposure, not a ranked resemblance score.','']
selection=[]
for town in towns:
    lines+=['## '+name(town['town']),'']
    lines += [f"The register links {town['observation_count']} assertions to this town. Source completeness and contemporaneous building totals are not assessed.",'']
    for label,domains,limit in sections:
        ids=list(dict.fromkeys(i for d in domains for i in town['domains'][d]['observation_ids']))
        # Phase-change assertions take precedence over a long list of dimensions.
        if label=='Changes to the urban framework':
            preferred=[i for i in ids if any(w in byid[i]['feature'] for w in ['replan','encroach','growth','open-space occupation','lane occupation','closure','rebuilding','regularization'])]
            ids=list(dict.fromkeys(preferred+ids))
        chosen=ids[:limit]
        selection.append(dict(town=town['town'],field=label,observation_ids=chosen,all_candidate_ids=ids,selection_limit=limit))
        lines+=['### '+label,'']
        if not chosen:
            lines+=['No directly tagged assertion was recovered for this field in the bounded review. The complete register may contain related context, and the remaining source task stays open.','']
        for oid in chosen:
            row=byid[oid]
            lines.append(f"- **{oid}**. {row['assertion']} Phase: {row['phase']}. Source: {row['source_id']}, {row['locator']}.")
            scope=row.get('denominator') or row.get('count_or_measurement_scope')
            if scope: lines.append('  Scope: '+str(scope)+'.')
            if row.get('missing_reason'): lines.append('  Missing evidence: '+str(row['missing_reason']))
            if row.get('uncertainty'): lines.append('  Uncertainty: '+str(row['uncertainty']))
        if len(ids)>limit: lines+=['',f"The complete register retains {len(ids)-limit} additional tagged assertions for this field."]
        lines+=['']
    lines+=['The remaining comparative prerequisites are a phase-contemporary building census, independently joined construction boundaries, a phase-specific street graph, matched documentary recovery denominators and component-level material provenance. See `run-v3/missing-fields.csv`.','']
(P/'COMPARISON.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
(P/'comparison-selection.json').write_text(json.dumps(selection,indent=2)+'\n',encoding='utf-8')

quantities=[]
for r in rows:
    for key in ['value','quantity','count','brick_dimensions_cm','brick_ratio']:
        if key in r:
            quantities.append(dict(observation_id=r['id'],town=r['town'],towns=';'.join(r['towns']),phase=r['phase'],feature=r['feature'],
                                   numeric_field=key,raw_value_json=json.dumps(r[key],ensure_ascii=False),
                                   unit=r.get('unit',r.get('count_unit','cm' if key=='brick_dimensions_cm' else 'ratio' if key=='brick_ratio' else 'source convention')),
                                   operator=r.get('operator','not explicitly supplied'),
                                   denominator=r.get('denominator',r.get('count_or_measurement_scope','Not uniformly quantified; see source assertion')),
                                   evidence_status=r['evidence_status'],uncertainty=r.get('uncertainty'),measurement_error=r.get('measurement_error'),
                                   source_id=r['source_id'],locator=r['locator']))
fields=list(quantities[0])
with (P/'quantities.csv').open('w',newline='',encoding='utf-8-sig') as f:
    writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(quantities)

bib=['# Source-use bibliography','',
     'The core register has 42 source-use records. Repeated editions, failed acquisition routes and methods references remain separate. Thirty-eight file paths passed hash checks and contain 36 distinct file hashes. This is not a count of publications or independent witnesses. New raw source copies remain on D:.','']
for s in sources:
    title=s.get('title','Untitled source')
    authors=s.get('author',s.get('authors','Source record'))
    if isinstance(authors,list):authors=', '.join(str(v) for v in authors)
    url=s.get('url',s.get('source_url',''))
    linked=f'[{title}]({url})' if url else title
    bib += ['## '+s['source_id'],'',f"{authors}. {s.get('year','year unresolved')}. {linked}.",'']
    locator=s.get('read_locator',s.get('locator',s.get('scope','See assertion-level locators')))
    bib += ['Read scope: '+str(locator)+'.', '']
    if s.get('edition_caution') or s.get('note'):bib+=['Edition or access note: '+str(s.get('edition_caution',s.get('note'))),'']
    if s.get('sha256'):bib+=['SHA-256: `'+s['sha256']+'`.','']
    else:bib+=['Local content hash: unavailable. '+str(s.get('missing_reason',s.get('status','No local source asset in this record')))+'.','']
    bib+=['Rights: '+str(s.get('rights','Unresolved; local-only source handling'))+'.','']
bib += ['## Additional prospective-method references','',
        '[Rajesh P. N. Rao 2018, *The Indus Script and Economics. A Role for Indus Seals and Tablets in Rationing and Administration of Labor*](https://arxiv.org/abs/1812.00049), pp. 518-525. Direct prior proposal for labour and ration tokens; local held-source hash and locators are recorded in the western review.','',
        '[Christopher Bronk Ramsey 2009, *Bayesian analysis of radiocarbon dates*](https://ora.ox.ac.uk/bookmarks/uuid%3Abbcb620d-af5c-479c-97e3-9d0c6bdb6e48), Radiocarbon 51(1), 337-360. Chronological-method precedent; no model is fitted in this study.','',
        '[Historic England, *Radiocarbon Dating and Chronological Modelling: The Bayesian Process*](https://historicengland.org.uk/images-books/publications/radiocarbon-dating-chronological-modelling/the-bayesian-process/), sections 3.1-3.6, inspected 24 October 2026. Sample selection and reporting guidance; no source binary acquired.','']
(P/'SOURCES.md').write_text('\n'.join(bib),encoding='utf-8')
manifest=dict(register='run-v3',register_sha256=hashlib.sha256((R/'observations.json').read_bytes()).hexdigest(),
              comparison_fields=len(selection),selected_assertion_uses=sum(len(r['observation_ids']) for r in selection),
              quantity_rows=len(quantities),sources=len(sources),code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
(P/'tables-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
print(json.dumps(manifest,indent=2))
