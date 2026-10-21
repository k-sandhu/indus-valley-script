"""Audit parsing, rights and files: python -I code/validate_run1.py --help."""
from pathlib import Path
import sys
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
import argparse
import ast
import io
import json
import re
import tokenize
import unicodedata
import hashlib
import subprocess
from common import CODE,RUN,LOCAL,ENTRY,PACKAGE,read,write,sha,code_hashes
from dedr_parse import no_parentheses,normalise

def state_snapshot():
    codings={}
    for path in sorted((LOCAL/'codings').glob('*.json')):
        codings[path.stem]={meaning:dict(entry=item['entry'],tips={tip:v['state'] for tip,v in item['tips'].items()})
                            for meaning,item in read(path).items()}
    pools={}
    for path in sorted((LOCAL/'reference').glob('*.json')):
        pools[path.stem]={hashlib.sha256(head.encode()).hexdigest():
                         {tip:v['state'] for tip,v in item['tips'].items()} for head,item in read(path).items()}
    return dict(codings=codings,pools=pools,pool_sizes=read(RUN/'pool-sizes.json'),
                parse_summary=read(RUN/'parse-summary.json'))

def snapshot():
    path=LOCAL/'run1b/before.json'
    if path.exists(): raise ValueError('Preserve the existing baseline')
    write(path,state_snapshot())
    print('Saved coding states, opaque pool identifiers and parse counts before the repair')

def compare():
    before=read(LOCAL/'run1b/before.json'); after=state_snapshot()
    if before['codings'].keys()!=after['codings'].keys(): raise ValueError('Coding variant set changed')
    changes=[]; reference_changes=[]
    for variant,items in before['codings'].items():
        if items.keys()!=after['codings'][variant].keys(): raise ValueError('Meaning set changed')
        for meaning,item in items.items():
            current=after['codings'][variant][meaning]
            if item['tips'].keys()!=current['tips'].keys(): raise ValueError('Tip set changed')
            for tip,old in item['tips'].items():
                new=current['tips'][tip]
                if old!=new: changes.append(dict(meaning=meaning,variant=variant,tip=tip,old=old,new=new))
    for entry,pool in before['pools'].items():
        current=after['pools'][entry]
        for identifier in sorted(set(pool)|set(current)):
            old=pool.get(identifier); new=current.get(identifier)
            if old is None or new is None:
                reference_changes.append(dict(entry=entry,head_sha256=identifier,membership='added' if old is None else 'removed'))
            else:
                for tip,state in old.items():
                    if state!=new[tip]:
                        reference_changes.append(dict(entry=entry,head_sha256=identifier,tip=tip,old=state,new=new[tip]))
    sizes=[dict(entry=k,old=v,new=after['pool_sizes']['entries'][k])
           for k,v in before['pool_sizes']['entries'].items() if v!=after['pool_sizes']['entries'][k]]
    parsing={k:dict(old=v,new=after['parse_summary']['entries'][k])
             for k,v in before['parse_summary']['entries'].items() if v!=after['parse_summary']['entries'][k]}
    result=dict(coding_state_changes=changes,reference_state_changes=reference_changes,
                pool_size_changes=sizes,parse_count_changes=parsing,
                s4_parse_issues_before=before['parse_summary'].get('s4_parse_issues',{}),
                s4_parse_issues_after=after['parse_summary'].get('s4_parse_issues',{}))
    write(RUN/'run1b-changes.json',result)
    print(json.dumps(result))

def audit():
    issues=[]; summaries={'chosen':{},'S4':{}}; failures=[]
    selected=[('chosen',key,LOCAL/'parsed'/(key+'.json')) for key in sorted(set(ENTRY.values()))]
    selected += [('S4',key,LOCAL/'parsed/s4'/(key+'.json')) for key in read(LOCAL/'s4-entries.json')]
    for scope,key,path in selected:
        entry=read(path)
        invalid=[line['index'] for line in entry['language_lines'] if line.get('parenthesis_depth')!=0]
        if invalid: failures.append(dict(scope=scope,entry=key,line_indices=invalid))
        for f in entry['forms']:
            why=[]
            if f['form'].count('(')!=f['form'].count(')'): why.append('unbalanced_form_parentheses')
            if re.fullmatch(r'[\d\s.()]+',f['gloss']) and key not in {'910','2485','5052'}: why.append('citation_only_gloss')
            if not any(s['normalised'] for s in f['segments']): why.append('empty_gloss')
            if why: issues.append(dict(scope=scope,entry=key,form_index=f['index'],reasons=why,form=f['form'],gloss=f['gloss']))
        summaries[scope][key]=dict(language_lines=len(entry['language_lines']),forms=len(entry['forms']),
                                  issues=len(entry['issues']),language_lines_inside_parentheses=len(invalid),
                                  parenthesis_audit_passed=not invalid)
    write(LOCAL/'parse-audit.json',dict(issues=issues,entries=summaries,parenthesis_failures=failures))
    write(RUN/'parse-audit.json',dict(entries=summaries,parenthesis_failures=failures,passed=not failures,
                                     total_entries=len(selected),total_language_lines=sum(v['language_lines'] for group in summaries.values() for v in group.values())))
    print(json.dumps(dict(chosen_entries=len(summaries['chosen']),s4_entries=len(summaries['S4']),
                          parenthesis_failures=len(failures),other_parse_audit_issues=len(issues))))
    if failures: raise ValueError('A language line begins inside parentheses or lacks opening-depth metadata')

def norm(s): return unicodedata.normalize('NFC',s).casefold()

def scan():
    # Exempt the frozen class vocabulary, recorded separately from dictionary text.
    protocol=(PACKAGE/'PROTOCOL.md').read_text(encoding='utf-8')
    rules=protocol.split('### Sense classes',1)[1].split('### Coding languages',1)[0]
    allowed=set()
    # Exact words and phrases appearing in the class specification are authorised vocabulary.
    # The local match report retains every exemption for review.
    targets={}
    parsed_paths=sorted((LOCAL/'parsed').rglob('*.json'))
    for path in parsed_paths:
        entry=read(path)
        for f in entry['forms']:
            values=[('form',f['form']),('form',no_parentheses(f['form']).strip())]
            values += [('gloss',s['text']) for s in f['segments']]+[('gloss',s['normalised']) for s in f['segments']]
            for kind,value in values:
                value=norm(value.strip(' .;,?'))
                if len(value)<=3: continue
                if re.search(r'(?<!\w)'+re.escape(value)+r'(?!\w)',norm(rules)):
                    allowed.add(value); continue
                targets.setdefault(value,set()).add((entry['entry'],kind))
    matches=[]; lexical=[]
    paths=sorted([p for folder in [CODE,RUN] for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts])
    for path in paths:
        text=path.read_text(encoding='utf-8')
        prose=text
        if path.suffix=='.py':
            parts=[]
            for tok in tokenize.generate_tokens(io.StringIO(text).readline):
                if tok.type==tokenize.COMMENT: parts.append(tok.string)
                elif tok.type==tokenize.STRING:
                    try:
                        value=ast.literal_eval(tok.string)
                        if isinstance(value,str): parts.append(value)
                    except (ValueError,SyntaxError): pass
            prose='\n'.join(parts)
        for value,origins in targets.items():
            rx=r'(?<!\w)'+re.escape(value)+r'(?!\w)'
            if re.search(rx,norm(text)):
                relative=path.relative_to(PACKAGE).as_posix()
                rec=dict(path=relative,value=value,origins=sorted(origins),review_id=hashlib.sha256((relative+'\0'+value).encode()).hexdigest())
                lexical.append(rec)
                if re.search(rx,norm(prose)): matches.append(rec)
    write(LOCAL/'rights-scan-detail.json',dict(prose_or_string_matches=matches,all_literal_matches=lexical,
                                             class_vocabulary_exemptions=sorted(allowed)))
    reviewpath=LOCAL/'rights-scan-review.json'
    reviews=read(reviewpath) if reviewpath.exists() else {}
    remaining=[m for m in matches if m['review_id'] not in reviews]
    # This aggregate contains no matched dictionary material.
    result=dict(files_scanned=len(paths),method='NFC casefold whole-token sequences; strings and comments separately audited',
                form_and_segment_minimum_characters=4,source_entries=len(parsed_paths),
                exempt_class_vocabulary=len(allowed),all_literal_matches=len(lexical),prose_or_string_matches=len(matches),
                reviewed_incidental_matches=len(matches)-len(remaining),unreviewed_matches=len(remaining),
                dictionary_form_matches=sum(any(kind=='form' for _,kind in m['origins']) for m in matches),
                passed=len(remaining)==0,files={p.relative_to(PACKAGE).as_posix():sha(p) for p in paths if p.name!='rights-scan.json'})
    write(RUN/'rights-scan.json',result)
    print(json.dumps({k:v for k,v in result.items() if k!='files'}))

def status():
    root=PACKAGE.parent.parent
    output=subprocess.run(['git','-c','safe.directory='+root.as_posix(),'status','--short','--untracked-files=all'],cwd=root,text=True,capture_output=True,check=True).stdout
    ownprefix=PACKAGE.relative_to(root).as_posix()+'/'
    owned=[ownprefix+'code/',ownprefix+'run1/',ownprefix+'PLAN-CODEX.md',ownprefix+'TOOLS.md',ownprefix+'CODEX-NOTES-RUN1.md']
    ours=[]; others=[]
    for line in output.splitlines():
        name=line[3:].replace(chr(92),'/').strip('"')
        (ours if any(name.startswith(prefix) for prefix in owned) else others).append(line)
    write(LOCAL/'git-status.json',dict(owned_changes=ours,other_session_changes=others))
    files={}
    for filename,hashfile in [('PROTOCOL.md','PROTOCOL.sha256'),('ENTRIES.md','ENTRIES.sha256')]:
        expected=re.search(r'\b[0-9a-f]{64}\b',(PACKAGE/hashfile).read_text(encoding='utf-8')).group(0)
        actual=sha(PACKAGE/filename); files[filename]=dict(expected=expected,actual=actual,matches=expected==actual)
    synthetic_runs={p.parent.name:read(p)['code_hashes']==code_hashes() for p in sorted(LOCAL.glob('synthetic*/results.json'))}
    write(RUN/'verification.json',dict(specification_integrity=files,owned_status_paths=len(ours),
          other_session_status_paths=len(others),other_session_status_local='codex-run1/git-status.json',
          freeze_exists=(PACKAGE/'FREEZE.json').exists(),real_results_exist=(PACKAGE/'results-v1').exists(),
          code_hashes=code_hashes(),selftest_code_hashes_match=read(RUN/'selftest.json')['code_hashes']==code_hashes(),
          parenthesis_audit_passed=read(RUN/'parse-audit.json')['passed'],
          synthetic_runs=synthetic_runs,synthetic_code_hashes_match=bool(synthetic_runs) and all(synthetic_runs.values())))
    tracked=[p.relative_to(root).as_posix() for folder in [CODE,RUN] for p in sorted(folder.rglob('*')) if p.is_file()]
    tracked.extend((PACKAGE/n).relative_to(root).as_posix() for n in ['PLAN-CODEX.md','TOOLS.md','CODEX-NOTES-RUN1.md'] if (PACKAGE/n).exists())
    local=[p.relative_to(root).as_posix() for folder in [LOCAL,LOCAL.parent/'downloads'] for p in sorted(folder.rglob('*')) if p.is_file()]
    write(RUN/'created-paths.json',dict(tracked=sorted(set(tracked+[str((RUN/'created-paths.json').relative_to(root)).replace(chr(92),'/')])),local=local))
    print(json.dumps(dict(owned_status_paths=len(ours),other_session_status_paths=len(others),specification_hashes_match=all(v['matches'] for v in files.values()))))

def summary():
    tests=read(RUN/'selftest.json')
    calibration={tree:{mode:dict(correct_calls=values['correct_calls'],bins=[dict(bin=b['bin'],n=b['count'],frequency=b['frequency'],prediction=b['mean_prediction'],interval=b['binomial_95']) for b in values['bins']]) for mode,values in modes.items()} for tree,modes in tests['calibration']['trees'].items()}
    mapping=read(RUN/'language-tip-map.json')
    print(json.dumps(dict(test_count=tests['test_count'],failures=tests['failures'],calibration=calibration,
                          parsing=read(RUN/'parse-summary.json'),uncertain_labels=[r['label'] for r in mapping['labels'] if r['uncertain']],
                          dictionary_requests=read(RUN/'sources-dedr.json')['requests']),ensure_ascii=False,indent=2))

def inspect(entries='3253,4572'):
    from dedr_parse import Page,tokenise
    for key in entries.split(','):
        path=LOCAL/'parsed'/(key+'.json')
        entry=read(path if path.exists() else LOCAL/'parsed/s4'/(key+'.json'))
        print('ENTRY '+key)
        print(json.dumps(entry['source']))
        page=Page(); page.feed(Path(entry['source']['path']).read_text(encoding='utf-8'))
        for block in page.blocks:
            if any(s=='number' and t.strip()==key for s,t in block): print(json.dumps(tokenise(block),ensure_ascii=True))

def review(accept,reason):
    matches=read(LOCAL/'rights-scan-detail.json')['prose_or_string_matches']
    if not accept:
        print(json.dumps([dict(id=m['review_id'],path=m['path'],value=m['value'],form_match=any(kind=='form' for _,kind in m['origins'])) for m in matches],ensure_ascii=True,indent=2))
        return
    path=LOCAL/'rights-scan-review.json'; records=read(path) if path.exists() else {}
    valid={m['review_id'] for m in matches}
    for identifier in accept.split(','):
        if identifier not in valid: raise ValueError('Unknown review identifier')
        records[identifier]=dict(reason=reason)
    write(path,records)

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__); ap.add_argument('command',choices=['audit','scan','status','summary','inspect','review','snapshot','compare'])
    ap.add_argument('--accept',default=''); ap.add_argument('--reason',default='Reviewed independent vocabulary or identifier overlap; no dictionary text reproduced')
    ap.add_argument('--entries',default='3253,4572')
    args=ap.parse_args()
    if args.command=='review': review(args.accept,args.reason)
    elif args.command=='inspect': inspect(args.entries)
    else: globals()[args.command]()
