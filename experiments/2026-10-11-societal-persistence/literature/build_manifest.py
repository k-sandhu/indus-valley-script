"""Describe owned artifacts and local-only witnesses; retain generated helpers."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
RAW=ROOT/'data/raw/2026-10-11-societal-persistence/literature'


def record(path, category):
    data=path.read_bytes()
    return dict(path=path.relative_to(ROOT).as_posix(),category=category,
                bytes=len(data),sha256=hashlib.sha256(data).hexdigest())


def main():
    target=HERE/'changed-paths.json'
    authored=[]; helpers=[]
    for path in sorted(HERE.rglob('*')):
        if not path.is_file():continue
        if '__pycache__' in path.parts or path.suffix=='.pyc':
            helpers.append(record(path,'ignored local generated helper'))
        elif path!=target:
            authored.append(record(path,'authored research metadata, prose or code'))
    raw=[record(p,'local-only publication, acquisition record or mechanical derivative') for p in sorted(RAW.rglob('*')) if p.is_file()]
    sources=json.loads((HERE/'SOURCES.json').read_text('utf-8'))['sources']
    dependencies={}
    for source in sources:
        for entry in source['witnesses']:
            if entry['reused_collaborator_witness']:
                dependencies[entry['path']]=dict(entry,source_id=source['source_id'])
        for attempt in source['acquisition_attempts']:
            if attempt.get('reused_from_collaborator'):
                relative=attempt['acquisition_manifest']
                dependencies[relative]=dict(record(ROOT/relative,'unmodified collaborator acquisition metadata'),source_id=source['source_id'])
    own_paths=[x['path'] for x in authored]+[target.relative_to(ROOT).as_posix()]
    report=dict(scope='Only this literature branch owned directories; dependencies were read without editing',
        authored_and_review_output_paths=own_paths,
        authored_artifact_count=len(own_paths),
        authored_artifact_hashes=authored,
        self_hash_note='changed-paths.json is included in the artifact count but cannot carry its own nonrecursive hash.',
        local_only_raw_paths=raw,local_only_raw_count=len(raw),
        ignored_local_generated_helpers=helpers,
        helper_note='Compiled bytecode remains on disk and is a local generated helper, not a repository artifact.',
        unmodified_collaborator_dependencies=sorted(dependencies.values(),key=lambda x:x['path']),
        no_global_edits='No edits to root protocol, theory, global navigation, registry, other agent packages or old frozen endpoints.',
        no_publication='No commit, push, visibility change, publication, CI/CD or automation.')
    target.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(authored=report['authored_artifact_count'],raw=report['local_only_raw_count'],helpers=len(helpers),dependencies=len(dependencies))))


if __name__=='__main__':main()
