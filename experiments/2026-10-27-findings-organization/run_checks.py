"""Run the required read-only checks and save their exact outputs locally."""
import json
from pathlib import Path
import re
import subprocess
import sys
sys.dont_write_bytecode = True

PACKAGE=Path(__file__).resolve().parent
ROOT=PACKAGE.parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import kb

def run(args):
    return subprocess.run([sys.executable,'-B','-X','utf8',*args],cwd=ROOT,capture_output=True,text=True,encoding='utf-8')

def paths():
    names=['knowledge/findings/README.md','knowledge/INDEX.md','knowledge/TIMELINE.md',
           'knowledge/WORKING-MODEL.md','knowledge/retrospectives/README.md',
           'knowledge/registry/attempts/FINDINGS-ORGANIZATION-2026-10-27.json']
    names+=json.loads((PACKAGE/'new-cards.json').read_text(encoding='utf-8'))
    names+=[p.relative_to(ROOT).as_posix() for p in (ROOT/'knowledge/findings').glob('F-003[6-8]*.md')]
    names+=[p.relative_to(ROOT).as_posix() for p in PACKAGE.rglob('*') if p.is_file()
            and p.name not in ['PROMPT.md','launch.sh','codex-log.txt'] and '__pycache__' not in p.parts]
    names += ['experiments/2026-10-27-findings-organization/'+n for n in
              ['changed-paths.json','kb-check.txt','prose-review.txt','prose-dispositions.json','checks-summary.json','evidence-tracking.json']]
    result=sorted(set(names))
    (PACKAGE/'changed-paths.json').write_text(json.dumps({'paths':result},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return result

changed=paths()
markdown=[p for p in changed if p.endswith('.md')]
result=run(['tools/review_prose.py',*[value for path in markdown for value in ['--path',path]],'--no-write'])
(PACKAGE/'prose-review.txt').write_text(result.stdout+result.stderr,encoding='utf-8')
prose=json.loads(result.stdout)
dispositions=[]
for flag in prose['flags']:
    path=flag['file'];line=flag['text'];reason=None
    if path.startswith('knowledge/findings/F-'):
        if line.startswith(('evidence:','registry_ids:')):reason='Machine-readable repository paths or IDs; values are preserved exactly.'
        elif int(Path(path).name[2:6])<=38:reason='Existing card wording or evidence label; body edits are outside the assigned scope.'
        elif line.startswith('- [experiments/'):reason='Exact evidence-path link label; the accompanying JSON Pointer or report section defines the location.'
    if path in ['knowledge/INDEX.md','knowledge/TIMELINE.md','knowledge/retrospectives/README.md','knowledge/WORKING-MODEL.md']:
        base=PACKAGE/'baseline'/path.removeprefix('knowledge/')
        if base.exists() and line in base.read_text(encoding='utf-8-sig'):reason='Preserved historical narrative, source name or technical label.'
    dispositions.append({**flag,'disposition':'retained' if reason else 'edit-required','reason':reason})
(PACKAGE/'prose-dispositions.json').write_text(json.dumps({'flags':dispositions},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

outputs={}
for script,name in [('check_links.py','link-check'),('check_guide.py','guide-check'),('check_preservation.py','preservation-check')]:
    r=run(['experiments/2026-10-27-findings-organization/'+script]);outputs[name]=json.loads((PACKAGE/(name+'.json')).read_text(encoding='utf-8'))
    print(name+': '+outputs[name]['status'])

evidence=[]
for path in json.loads((PACKAGE/'new-cards.json').read_text(encoding='utf-8')):
    fields,_=kb.frontmatter((ROOT/path).read_text(encoding='utf-8-sig'))
    for pointer in fields['evidence']:
        file=pointer.split('#')[0]
        r=subprocess.run(['git','-c','safe.directory='+ROOT.as_posix(),'ls-files','--error-unmatch','--',file],cwd=ROOT,capture_output=True)
        evidence.append({'card':fields['id'],'evidence':pointer,'tracked':r.returncode==0})
(PACKAGE/'evidence-tracking.json').write_text(json.dumps({'status':'pass' if all(r['tracked'] for r in evidence) else 'fail','references':evidence},indent=2)+'\n',encoding='utf-8')

r=run(['tools/kb.py','check']);(PACKAGE/'kb-check.txt').write_text(r.stdout+r.stderr,encoding='utf-8')
summary={'knowledge_check':{'status':'pass' if r.returncode==0 else 'fail','summary':r.stdout.strip().splitlines()[-1]},
         'prose_review':{'status':'pass' if not any(d['disposition']=='edit-required' for d in dispositions) else 'fail','files_scanned':prose['files_scanned'],'flags':len(dispositions),'retained_source_or_path_flags':sum(d['disposition']=='retained' for d in dispositions),'new_prose_flags':sum(d['disposition']=='edit-required' for d in dispositions)},
         'links':{k:v for k,v in outputs['link-check'].items() if k!='files'},
         'guide':outputs['guide-check'],
         'preservation':{k:v for k,v in outputs['preservation-check'].items() if k!='cards'},
         'tracked_new_card_evidence':all(x['tracked'] for x in evidence),
         'changed_paths':len(changed)}
summary['status']='pass' if (r.returncode==0 and summary['prose_review']['status']=='pass' and all(x['status']=='pass' for x in outputs.values()) and summary['tracked_new_card_evidence']) else 'fail'
(PACKAGE/'checks-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False,indent=2))
sys.exit(summary['status']!='pass')
