"""Review audit coordinates and identity fields only."""
import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from audit import BASE,OUT,csvrows,families,save,safe
mode=sys.argv[2]
if mode=='locators':
    fam=families();obj={r['row_id']:r for r in csvrows(BASE/'objects.csv')}
    data=json.loads((OUT/'locator-check.json').read_text(encoding='utf-8'))
    for r in data['failures']:
        if 'family' in r:
            print(r['row_id'],'row site',obj[r['row_id']]['site'],'family sites',[x['site'] for x in fam[r['family']]],'family',r['family'])
    for r in json.loads((OUT/'coordinator-join-check.json').read_text(encoding='utf-8'))['would_not_reach']:
        if r['match_basis']=='context' and r['decision']!='matched':print('CONTEXT candidate rejected',r['row_id'],r['reasons'])
elif mode=='content':
    data=json.loads((OUT/'content-check.json').read_text(encoding='utf-8'))
    print('TRACKED',data['tracked_files_scanned'],'WORKING',data['working_files_scanned'])
    for r in data['hits']:print(r['file'],r['line'],r['category'])
elif mode=='inputs':
    for fname in ['extraction/D/seal-table-D.json','extraction/D/catalogue-metadata-D.json','acquisition-web/candidate-publication-locators-1b.json']:
        data=json.loads((BASE/fname).read_text(encoding='utf-8-sig'));print(fname,type(data).__name__)
        if isinstance(data,list) and data:print('keys',list(data[0]))
        elif isinstance(data,dict):print('keys',list(data))
        if 'candidate-publication' in fname:
            for r in data[:5]:
                v=r.get('site_candidate_pages')
                print('CANDIDATE SHAPE',r.get('source_id'),type(v).__name__,list(v)[:8] if isinstance(v,dict) else v[:2] if isinstance(v,list) else None)
elif mode=='identifiers':
    fam=families();obj={r['row_id']:r for r in csvrows(BASE/'objects.csv')}
    data=json.loads((OUT/'locator-check.json').read_text(encoding='utf-8'))
    for x in data['failures']:
        r=obj[x['row_id']]
        print(r['row_id'],{k:safe(r[k]) for k in ['registration','other_numbers','local_family_ids','match_note']})
elif mode=='status':
    for name in ['coordinator-join-check.json','dholavira-grid-check.json','content-check.json']:
        p=OUT/name;d=json.loads(p.read_text(encoding='utf-8'));print(name,p.stat().st_size)
        if 'would_not_reach' in d:
            for r in d['would_not_reach']:print(r['row_id'],r['match_basis'],r['reasons'])
elif mode=='revision':
    from audit import inputpath
    rs=csvrows(inputpath('join-decisions.csv'));print('headers',list(rs[0]))
    for r in rs[:8]:print({k:v for k,v in r.items() if k=='row_id' or any(x in k for x in ['local_match','match_basis','final_','review_','verification_'])})
    print('object headers',list(csvrows(inputpath('objects.csv'))[0]))
    for r in csvrows(inputpath('objects.csv')):
        if r['row_id'] in ('PCF-DHV-005','PCF-DSL-002','PCF-HUL-001','PCF-SKT-002','PCF-KNM-001'):
            print(r['row_id'],{k:safe(r[k]) for k in ['other_numbers','local_match','local_family_ids','match_basis','match_note']})
    d=json.loads((OUT/'count-check.json').read_text(encoding='utf-8'))['decision_application_differences']
    from collections import Counter
    print('decision difference fields',Counter(x['field'] for x in d))
    print('first differences',d[:5])
