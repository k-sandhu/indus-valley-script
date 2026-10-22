"""Assemble the audit report from saved, independently computed results."""
import collections
import hashlib
import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from audit import ROOT,BASE,OUT,csvrows,save,savecsv

def get(name):return json.loads((OUT/name).read_text(encoding='utf-8'))
def pct(x):return 'unavailable' if x is None else f'{100*x:.1f}%'
def ci(v):return pct(v[0])+'–'+pct(v[1])
def short(p):
    s=p.replace('\\','/')
    prefix='experiments/2026-10-21-post-catalogue-finds/'
    return s[len(prefix):] if s.startswith(prefix) else s
def compact(values):
    groups=collections.defaultdict(list)
    for v in sorted(values):
        head,tail=v.rsplit('-',1);groups[head].append(int(tail))
    out=[]
    for head,ns in sorted(groups.items()):
        chunks=[];a=b=ns[0]
        for n in ns[1:]:
            if n==b+1:b=n
            else:chunks.append(f'{a:03}' if a==b else f'{a:03}–{b:03}');a=b=n
        chunks.append(f'{a:03}' if a==b else f'{a:03}–{b:03}')
        out.append(head+' '+', '.join(chunks))
    return '; '.join(out)

def main():
    blind=get('blind-summary.json');om=get('omission-summary.json');counts=get('count-check.json');join=get('coordinator-join-check.json');loc=get('locator-check.json');content=get('content-check.json');unnamed=get('unnamed-summary.json');revision=get('input-revision.json');sampling=get('sampling.json')
    total=counts['recomputed_total'];historical=join['would_not_reach'];current=join['current_would_not_reach']
    raw_search=csvrows(OUT/'unnamed-search.csv')
    read_status={r['family']:any(x['family']==r['family'] and x['source_page_read_by_extraction']=='yes' for x in raw_search) for r in unnamed['results']}
    save('unnamed-read-status.json',{'families':[{'family':r['family'],'registration':r['registration'],'result':r['result'],'occurs_on_page_logged_read_by_extraction':read_status[r['family']] if r['registration'] else None} for r in unnamed['results']],'interpretation':'This is a coordinate cross-check against pages-read logs. A number occurrence on a logged page is not confirmation that the number identifies this object.'})
    lines=[]
    lines.append('We completed the saved verification checks, with unresolved source coverage and join objections. The revised snapshot has 503 rows, including 301 main rows: 11 matched, 271 candidate and 19 absent. Its absent bounds are 45–290. All '+str(counts['cells_checked'])+' site-table cells recompute exactly, including the three added context sensitivity columns. Those give '+str(total['matched_with_context_joins'])+' matched main rows and bounds '+str(total['absent_lower_with_context_joins'])+'–'+str(total['absent_upper_with_context_joins'])+'. The current locator and identifier audit has no failures. The remaining objections are recorded below; the source list was not edited by this run.')
    lines.append('The object list, join decisions and site counts were revised externally during the audit. We preserved the initial results and captured four revised input CSV files in revised-input-2026-10-21/. The initial arithmetic also reproduced exactly, with 77 matched main rows, 205 candidates and bounds of 45–224. No sampled blind field changed between revisions. input-revision.json gives both hashes; the revised object table is SHA256 '+next(r['sha256'] for r in revision['inputs'] if r['input'].endswith('objects.csv'))+'.')
    allocation=', '.join(p+' '+str(sampling['part_allocations'][p]) for p in 'NGDPEF')
    lines.append('The blind sample contains 60 of 503 rows, selected with seed 20261021: '+allocation+'. Part E contains only one row, which was included. The allocation starts with the minimum available per part and fills the largest remaining raw-quota deficit. The source-only observations were frozen before comparison. There are 113 field disagreements, 198 unassessed field slots and 35 inapplicable registration slots. Unassessed fields were retained. When both entries say unknown, agreement records missing evidence; it does not confirm that an illustration or transcription exists.')
    lines.append('Per-field agreement among assessed comparisons is shown below. Intervals are two-sided exact binomial 95% intervals. They are descriptive and unweighted; shared source pages make rows dependent. blind-summary.json also gives conservative rates using every applicable sampled row.')
    table=['| Field | Agreement | Exact 95% interval | Unassessed |','|---|---:|---:|---:|']
    for field,r in blind['fields'].items():table.append('| '+field+' | '+str(r['agreements'])+'/'+str(r['assessed'])+' ('+pct(r['rate'])+') | '+ci(r['exact_binomial_95'])+' | '+str(r['unassessed'])+' |')
    lines.append('\n'.join(table))
    lines.append('The 40 omission pages were drawn with seed 20261022 from unique source-page pairs listed with purpose candidate. We could assess 31 inventories and found no confirmed omitted object. Their conditional omission rate is 0/31, with exact 95% interval '+ci(om['assessed_page_exact_binomial_95'])+'. The full-sample omission rate is unavailable because nine inventories remain unresolved. If all nine were clear, the full-sample interval would be '+ci(om['all_sample_sensitivity']['if_no_unresolved_page_has_an_omission']['exact_binomial_95'])+'; if all nine contained an omission, the rate would be 9/40 with interval '+ci(om['all_sample_sensitivity']['if_every_unresolved_page_has_an_omission']['exact_binomial_95'])+'. There is no confirmed omitted-object description to list. Farmana, PDF page 391, seal, is already represented from PDF page 385; its illustration page is an explicit page-citation gap.')
    lines.append('Unresolved omission pages are '+ '; '.join(r['source_id']+' PDF '+r['pdf_page'] for r in om['page_results'] if r['assessment']=='unresolved')+'. No substitute pages were drawn.')
    lines.append('No count cell differs, and no applied decision differs after using protocol_local_match for the revised register. The 131 literal differences from its historical columns are documented separately: 67 status cells and 64 family-set cells. Historical context identities are preserved in context_join_family.')
    lines.append('We re-derived 121 coordinator decisions in the requested basis classes. We would not reach '+str(len(historical))+' historical decisions: '+str(sum(r['match_basis']=='context' for r in historical))+' context decisions, five catalogue-containment decisions and one plate-citation decision. The historical context matches lack the identifier required by the frozen protocol. The five containment decisions do not establish individual membership from the cited identities, and the plate reference does not identify its publication. The independent basic-data check found all ten cited entries across the six containment decisions; entry presence does not supply the missing identity tie. The revised table demotes 67 historical context matches to candidates. Its current candidate sets still produce '+str(len(current))+' decision objections, principally explicit registration, type, grid, area or trench conflicts. Every family-level reason is retained in coordinator-join-check.json. The independent Dholavira algorithm reproduces all 210 historical decisions with zero differences.')
    lines.append('Historical decisions we would not reach, with every row stated explicitly:')
    histrows=[]
    for r in historical:
        histrows.append({'row_id':r['row_id'],'match_basis':r['match_basis'],'reasons':'; '.join(r['reasons'])})
    savecsv('historical-join-objections.csv',histrows,['row_id','match_basis','reasons'])
    for r in histrows:lines.append(r['row_id']+' ['+r['match_basis']+']: '+r['reasons'])
    lines.append('Current protocol decisions we would not reach:')
    currows=[]
    for r in current:
        currows.append({'row_id':r['row_id'],'match_basis':r['match_basis'],'protocol_status':r['protocol_status'],'conflicting_candidate_families':len(r['candidate_families_with_conflicts']),'reasons':'; '.join(r['reasons'])})
    savecsv('current-join-objections.csv',currows,list(currows[0]))
    for r in currows:lines.append(r['row_id']+' ['+r['match_basis']+', '+r['protocol_status']+']: '+r['reasons']+(' Conflicting candidate families: '+str(r['conflicting_candidate_families'])+'.' if r['conflicting_candidate_families'] else ''))
    lines.append('The revised locator audit checks 506 primary page locators, 21 secondary references, all named family identifiers and sites, the one-family matched rule, duplicate links and baseline CISI identifiers. It reports zero failures and no empty primary page text. The initial missing baseline identifiers are present in the revised cisi_in_baseline column. Declared site aliases are used.')
    categories=collections.Counter(r['category'] for r in content['hits'])
    lines.append('The content audit found no tracked package file at the time of the Git inventory, so it additionally scanned the working package. It scanned '+str(content['files_scanned'])+' files and 200 windows for each of 48 cited sources, 9,600 windows in total. It found '+str(len(content['hits']))+' coordinate-level hits: '+', '.join(k+' '+str(v) for k,v in sorted(categories.items()))+'. R01–R13 follow the ordered vocabulary in check 6 of CODEX-PROMPT-4.md; R14 is the numeric-unit pattern, R15 an excluded populated data field and R16 a sampled 13-word source-window match. No R14 or R15 hit occurred. The raw hit text is withheld. Every coordinate, including overlapping windows, follows and is also in content-hits.csv.')
    ch=[]
    for i,r in enumerate(content['hits'],1):
        ch.append({'hit_id':i,'file':short(r['file']),'line':r['line'],'column':r.get('column',''),'category':r['category'],'source_id':r.get('source_id',''),'pdf_page':r.get('pdf_page',''),'source_word_offset':r.get('source_word_offset','')})
    savecsv('content-hits.csv',ch,['hit_id','file','line','column','category','source_id','pdf_page','source_word_offset'])
    for r in ch:
        detail=('; source '+r['source_id']+' PDF '+str(r['pdf_page'])+' window '+str(r['source_word_offset'])) if r['source_id'] else '; column '+str(r['column'])
        lines.append('Hit '+str(r['hit_id'])+': '+r['file']+':'+str(r['line'])+' ['+r['category']+']'+detail+'.')
    lines.append('The unnamed-family search covered all 39 rows. Twenty supplied a registration: eight produced 69 registration-shaped occurrences and twelve produced none. Nineteen supplied no registration. The immediate-line review did not establish these broad search hits as object identities; short numbers can be pagination or unrelated references. The result for every family follows; every source, page and matching line is in unnamed-search.csv.')
    for r in unnamed['results']:
        lines.append('Family '+r['family']+' ('+r['site']+'): '+(r['registration']+'; ' if r['registration'] else '')+r['result']+(' ('+str(r['occurrences'])+' occurrences)' if r['occurrences'] else '')+('; occurrence on a page logged read by extraction: '+('yes' if read_status[r['family']] else 'no') if r['registration'] else '')+'.')
    lines.append('An initial display filter exposed nonidentity source fragments in tool output. exposure-incidents.json records the affected display set. This run therefore fails the tool-output exposure restriction, although the saved audit records omit those source fragments. No page images were opened. The service interruption left complete saved records; no download, installation, OCR or render was needed. The original frozen observations remain unchanged.')
    outputs=['blind-assignments.csv','blind-observations-frozen.csv','blind-freeze.json','blind-sample.csv','blind-summary.json','omission-assignments.csv','omission-sample.csv','omission-summary.json','count-check.json','coordinator-join-check.json','catalogue-containment-check.json','dholavira-grid-check.json','historical-join-objections.csv','current-join-objections.csv','locator-check.json','content-check.json','content-hits.csv','unnamed-search.csv','unnamed-summary.json','unnamed-read-status.json','unnamed-line-review.csv','input-revision.json','resume-integrity.json','selftest-4.json','exposure-log.csv','exposure-mechanical.csv','exposure-incidents.json','RETROSPECTIVE.md','VERIFICATION.md','final.md']
    lines.append('Outputs are in experiments/2026-10-21-post-catalogue-finds/verification/: '+', '.join(outputs)+'. The initial results are in initial-results-2026-10-21/, the revised inputs in revised-input-2026-10-21/, and the first search endpoint in prior-search-2026-10-21/. Reproduction scripts are in the same verification directory. No list file, frozen protocol or file outside the owned paths was changed by this run.')
    lines.append('The reproducible result is the site arithmetic for the recorded snapshot. Acceptance still requires resolving the source inventories and the listed family conflicts. A further source-only review of those exact pages and candidate sets would decide those points.')
    (OUT/'final.md').write_text('\n\n'.join(lines)+'\n',encoding='utf-8')
    # A shorter connected report retains the same quantitative findings and names
    # all objections and hits through compact coordinate inventories.
    brief=lines[:8]
    brief.append('The historical objections are '+compact([r['row_id'] for r in historical])+'. The current objections are '+compact([r['row_id'] for r in current])+'. Their individual reasons and conflicting family identifiers are in coordinator-join-check.json and the two objection CSV files. These records preserve both the historical and applied decision states.')
    brief.append(lines[next(i for i,v in enumerate(lines) if v.startswith('The revised locator audit'))])
    brief.append(lines[next(i for i,v in enumerate(lines) if v.startswith('The content audit'))].split('Every coordinate')[0]+'All coordinates are retained in content-check.json, content-hits.csv and final.md.')
    grouped=collections.defaultdict(collections.Counter)
    for r in ch:grouped[r['file']][(r['line'],r['category'])]+=1
    brief.append('Content-hit locations: '+'; '.join(file+' '+', '.join(str(line)+' '+cat+(' ×'+str(n) if n>1 else '') for (line,cat),n in sorted(vals.items())) for file,vals in sorted(grouped.items()))+'.')
    byresult=collections.defaultdict(list)
    for r in unnamed['results']:byresult[r['result']].append(r['family']+(' ('+r['registration']+')' if r['registration'] else ''))
    brief.append('For every unnamed family, the registration-search result is: '+'; '.join(key+': '+', '.join(vals) for key,vals in sorted(byresult.items()))+'. The eight positive family searches yielded 69 occurrence coordinates, without establishing object identity. A search occurrence lies on a page logged read by extraction for families '+', '.join(r['family'] for r in unnamed['results'] if read_status[r['family']])+'. No such occurrence was found for the other registered families. unnamed-search.csv lists all sources and pages, and unnamed-line-review.csv records the immediate-line classifications.')
    brief.append(lines[-3]);brief.append(lines[-2]);brief.append(lines[-1])
    (OUT/'VERIFICATION.md').write_text('\n\n'.join(brief)+'\n',encoding='utf-8')
    save('report-summary.json',{'blind_rows':60,'blind_field_disagreements':blind['disagreements'],'blind_unassessed_slots':blind['unassessed_fields'],'omission_sample':40,'omission_assessed':31,'omission_unresolved':9,'confirmed_omitted_objects':0,'count_cells_checked':counts['cells_checked'],'count_differences':len(counts['differences']),'current_total':total,'historical_join_objections':len(historical),'current_join_objections':len(current),'current_objections_compact':compact([r['row_id'] for r in current]),'historical_objections_compact':compact([r['row_id'] for r in historical]),'locator_failures':len(loc['failures']),'content_hits':len(content['hits']),'content_categories':dict(categories),'unnamed_family_results':dict(collections.Counter(r['result'] for r in unnamed['results'])),'overall':'Review remains unresolved; computation reproduces but source coverage, candidate identities and exposure requirements do not all pass.'})
    print('Reports written;',len(historical),'historical and',len(current),'current join objections;',len(ch),'content coordinates.')

if __name__=='__main__':
    try:main()
    except OSError as e:
        try:save('WRITE-FAILURE.json',{'stopped':True,'error_class':type(e).__name__})
        finally:raise SystemExit('Stopped after an input/output error.')
