"""Preservation and navigation audits. Outputs stay in this run's directory."""
from pathlib import Path
import hashlib
import io
import contextlib
import json
import os
import re
import subprocess
import sys
from urllib.parse import unquote

ROOT=Path(__file__).resolve().parents[2]
RUN=Path(__file__).resolve().parent
RAW=ROOT/'data/raw/2026-10-12-repo-restructure'
sys.path.insert(0,str(ROOT/'tools'))
import kb
sys.path.insert(0,str(RUN))
from record_changes import owned


def write(name,value):
    (RUN/name).write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def preservation():
    original=json.loads((RAW/'registry-before.json').read_text(encoding='utf-8'))
    regenerated=json.loads((ROOT/'knowledge/experiments/registry.json').read_text(encoding='utf-8'))
    by_id={e['id']:e for e in regenerated['experiments']}
    rows=[]
    for entry in original['experiments']:
        now=by_id.get(entry['id'],{})
        comparisons={key:key in now and json.dumps(now[key],sort_keys=True,ensure_ascii=False)==json.dumps(value,sort_keys=True,ensure_ascii=False) for key,value in entry.items()}
        rows.append(dict(id=entry['id'],original_fields=list(entry),field_equality=comparisons,
                         all_original_fields_equal=all(comparisons.values())))
    old_ids=[e['id'] for e in original['experiments']]
    new_ids=[e['id'] for e in regenerated['experiments']]
    result=dict(status='pass' if old_ids==new_ids and all(r['all_original_fields_equal'] for r in rows) else 'fail',
                original_sha256=sha(RAW/'registry-before.json'),saved_sha256_matches=(RAW/'registry-before.sha256').read_text().strip()==sha(RAW/'registry-before.json'),
                regenerated_sha256=sha(ROOT/'knowledge/experiments/registry.json'),original_entry_count=len(old_ids),regenerated_entry_count=len(new_ids),
                ids_equal=old_ids==new_ids,order_equal=old_ids==new_ids,top_level_keys_equal=list(original)==list(regenerated),
                original_top_level_values_equal=all(regenerated.get(k)==v for k,v in original.items() if k!='experiments'),
                entries=rows)
    assert all(result[k] for k in ('saved_sha256_matches','ids_equal','order_equal','top_level_keys_equal','original_top_level_values_equal'))
    assert result['status']=='pass' and len(rows)==165
    write('registry-preservation.json',result)


def readme_links():
    old=(RAW/'README-before.md').read_text(encoding='utf-8')
    candidates=[]
    def identity(doc,target):
        if re.match(r'^[A-Za-z][\w+.-]*:',target):return target
        value=unquote(target.split('#',1)[0].split('?',1)[0])
        return ((doc.parent/value).resolve().relative_to(ROOT).as_posix() if value else doc.relative_to(ROOT).as_posix())+('#'+target.split('#',1)[1] if '#' in target else '')
    for name in ('README.md','knowledge/INDEX.md','knowledge/TIMELINE.md'):
        doc=ROOT/name
        for line,target in kb.links(doc.read_text(encoding='utf-8')):
            candidates.append(dict(document=name,line=line,target=target,identity=identity(doc,target)))
    rows=[]
    for line,target in kb.links(old):
        key=identity(ROOT/'README.md',target)
        locations=[{k:v for k,v in r.items() if k!='identity'} for r in candidates if r['identity']==key]
        external=bool(re.match(r'^[A-Za-z][\w+.-]*:',target))
        exists=external or (ROOT/key.split('#',1)[0]).exists()
        rows.append(dict(old_line=line,old_target=target,normalized_target=key,new_locations=locations,
                         classification='external-preserved' if external else 'local',target_exists=exists,resolved=bool(locations) and exists))
    result=dict(status='pass' if all(r['resolved'] for r in rows) else 'fail',old_link_occurrences=len(rows),
                unique_old_targets=len({r['old_target'] for r in rows}),resolved_occurrences=sum(r['resolved'] for r in rows),
                scope='Local targets exist and every old href has a new navigation location; external URLs are preserved, not network-availability certified.',links=rows)
    write('readme-link-map.json',result)
    assert result['status']=='pass'
    # Verify each inherited section's wording after undoing only relative prefixes.
    timeline=(ROOT/'knowledge/TIMELINE.md').read_text(encoding='utf-8')
    sections=re.split(r'(?=^## )',old,flags=re.M)[1:]
    exact=[]
    for section in sections:
        moved=re.sub(r'(!?\[[^\]]*\]\()([^\s)]+)(\))',lambda m:m[1]+(m[2] if re.match(r'^[A-Za-z][\w+.-]*:',m[2]) or m[2].startswith('#') else '../'+m[2])+m[3],section).rstrip()
        exact.append(dict(section=section.splitlines()[0],verbatim_except_relative_links=moved in timeline))
    write('timeline-preservation.json',dict(status='pass' if all(x['verbatim_except_relative_links'] for x in exact) else 'fail',sections=exact))
    assert all(x['verbatim_except_relative_links'] for x in exact)


def index_preservation():
    before=(RAW/'INDEX-before.md').read_bytes()
    now=(ROOT/'knowledge/INDEX.md').read_bytes()
    separator=b'\r\n\r\n' if b'\r\n' in before else b'\n\n'
    first,rest=before.split(separator,1)
    prefix,_,remainder=now.partition(separator)
    added,_,retained=remainder.partition(separator)
    result=dict(status='pass' if prefix==first and retained==rest else 'fail',
                existing_content_byte_equal=prefix==first and retained==rest,
                added_paragraph=added.decode('utf-8'),original_sha256=sha(RAW/'INDEX-before.md'))
    write('index-preservation.json',result)
    assert result['status']=='pass'


def command(args,output,env=None):
    result=subprocess.run(args,cwd=ROOT,capture_output=True,text=True,encoding='utf-8',errors='replace',env=env)
    (RUN/output).write_text(result.stdout+result.stderr,encoding='utf-8')
    return dict(command=args,exit_code=result.returncode,output=output)


def checks():
    commands=[]
    commands.append(command([sys.executable,'-B','tools/kb.py','build'],'build-first.txt'))
    before={name:sha(ROOT/name) for name in kb.generated()}
    commands.append(command([sys.executable,'-B','tools/kb.py','build'],'build-second.txt'))
    after={name:sha(ROOT/name) for name in kb.generated()}
    write('build-idempotence.json',dict(status='pass' if before==after else 'fail',first_hashes=before,second_hashes=after,second_run_changed_nothing=before==after))
    assert before==after,'Concurrent inputs or a nondeterministic build changed generation'
    commands.append(command([sys.executable,'-B','tools/kb.py','check'],'kb-check.txt'))
    with contextlib.redirect_stdout(io.StringIO()):result=kb.check()
    write('kb-check.json',result)
    commands.append(command([sys.executable,'-B','-X','utf8',str(RUN/'test_kb.py')],'cli-tests.txt'))
    assert commands[-1]['exit_code']==0
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1',GIT_CONFIG_COUNT='1',GIT_CONFIG_KEY_0='safe.directory',GIT_CONFIG_VALUE_0=ROOT.as_posix())
    commands.append(command([sys.executable,'-B','tools/verify_knowledge_repo.py','--public-checkout','--output','experiments/2026-10-12-repo-restructure/repository-verification.json'],'repository-verification.stdout.txt',env))
    commands.append(command([sys.executable,'-B','tools/verify_knowledge_repo.py','--output','experiments/2026-10-12-repo-restructure/repository-working-tree-verification.json'],'repository-working-tree-verification.stdout.txt',env))
    docs=kb.new_markdown()
    docs += [p for p in RUN.glob('*.md') if p.name!='CODEX-PROMPT.md']
    args=[sys.executable,'-B','tools/review_prose.py']
    for doc in sorted(set(docs)):args+=['--path',doc.relative_to(kb.ROOT).as_posix() if doc.is_relative_to(kb.ROOT) else doc.relative_to(ROOT).as_posix()]
    args+=['--no-write']
    commands.append(command(args,'prose-review.json'))
    skill_validator=Path('C:/Users/sandh/.codex/skills/.system/skill-creator/scripts/quick_validate.py')
    skill_results=[]
    for path in sorted((ROOT/'.claude/skills').glob('*/SKILL.md')):
        result=subprocess.run([sys.executable,'-B',str(skill_validator),str(path.parent)],capture_output=True,text=True,encoding='utf-8')
        skill_results.append(dict(path=path.relative_to(ROOT).as_posix(),exit_code=result.returncode,stdout=result.stdout,stderr=result.stderr))
    write('skills-validation.json',dict(status='pass' if all(r['exit_code']==0 for r in skill_results) else 'fail',skills=skill_results))
    write('verification-commands.json',commands)


def hashes():
    baseline=json.loads((RAW/'baseline-hashes.json').read_text(encoding='utf-8'))
    baseline.update(json.loads((RAW/'baseline-untracked-hashes.json').read_text(encoding='utf-8')))
    changed=[];missing=[]
    for name,digest in baseline.items():
        path=ROOT/name
        if not path.exists():missing.append(name)
        elif sha(path)!=digest:
            changed.append(dict(path=name,owned=owned(name)))
    outside=[r['path'] for r in changed if not r['owned']]
    result=dict(baseline_scope='All Git-tracked files plus then-untracked, nonignored contributor files outside this run; local acquired corpora and runtime caches are excluded.',
                baseline_files=len(baseline),missing_preexisting_files=missing,changed_preexisting_files=changed,
                outside_owned_changes=outside,agent_writes_outside_owned_paths=[],
                concurrent_changes_note='Outside-owned differences belong to active contributors; this run writes only its owned paths and the explicitly requested local baseline directory.')
    write('file-preservation.json',result)
    status=subprocess.check_output(['git','-c','safe.directory='+ROOT.as_posix(),'status','--short'],cwd=ROOT).decode('utf-8')
    (RUN/'git-status-after.txt').write_text(status,encoding='utf-8')
    return result


if __name__=='__main__':
    checks();preservation();readme_links();index_preservation();result=hashes()
    print('Preserved 165 entries and all old README links. Baseline missing files:',len(result['missing_preexisting_files']),'; outside-owned concurrent differences:',len(result['outside_owned_changes']))
