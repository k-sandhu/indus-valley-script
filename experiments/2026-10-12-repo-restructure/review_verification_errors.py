"""Separate index availability and inherited link errors from owned-layer defects."""
from collections import Counter
from pathlib import Path
import json
import re
import subprocess
import sys
from urllib.parse import unquote
ROOT=Path(__file__).resolve().parents[2]
RUN=Path(__file__).resolve().parent
sys.path.insert(0,str(RUN))
from record_changes import owned


def main():
    raw=ROOT/'data/raw/2026-10-12-repo-restructure'
    baseline=json.loads((raw/'baseline-hashes.json').read_text(encoding='utf-8'))
    baseline.update(json.loads((raw/'baseline-untracked-hashes.json').read_text(encoding='utf-8')))
    selected=set(subprocess.check_output(['git','-c','safe.directory='+ROOT.as_posix(),'ls-files','-z']).decode('utf-8').split('\0'))
    reports={}
    for name in ('repository-verification.json','repository-working-tree-verification.json','repository-working-tree-final.json'):
        report=json.loads((RUN/name).read_text(encoding='utf-8'))
        contexts={r['snapshot']:r['source_context'] for r in report['document_snapshot_link_contexts']+report['frozen_protocol_link_contexts']}
        rows=[]
        for error in report['errors']:
            referring=None;target=None
            m=re.match(r'^Broken link: (.*?) -> (.*)$',error)
            if m:
                referring,destination=m.groups()
                base=ROOT/contexts[referring] if referring in contexts else (ROOT/referring).parent
                path=(base/unquote(destination.split('#',1)[0].strip('<>'))).resolve()
                try:target=path.relative_to(ROOT).as_posix()
                except ValueError:target=str(path)
            else:
                m=re.match(r'^Missing evidence for (.*?): (.*)$',error)
                if m:referring,target=m.groups()
                else:
                    m=re.match(r'^Missing required file: (.*)$',error)
                    if m:target=m[1]
            exists=(ROOT/target).exists() if target else None
            is_selected=target in selected or any(p.startswith(target.rstrip('/')+'/') for p in selected) if target else None
            if error=="Forbidden distributed paths: ['data/MANIFEST.json']":
                category='authorized-manifest-rejected-by-legacy-verifier'
            elif exists and not is_selected and owned(target):
                category='new-layer-file-not-staged'
            elif exists and not is_selected and target in baseline:
                category='preexisting-untracked-or-local-target'
            elif exists and not is_selected:
                category='concurrent-or-local-target-not-staged'
            elif exists:
                category='inspect-context-or-index-availability'
            elif target and not owned(target):
                category='missing-target-outside-owned-paths'
            elif target:
                category='owned-missing-target'
            else:
                category='other-verifier-rule'
            rows.append(dict(error=error,referring=referring,target=target,working_tree_exists=exists,index_selected=is_selected,
                             referring_owned=owned(referring) if referring and '/' in referring else None,category=category))
        reports[name]=dict(errors=len(rows),categories=dict(sorted(Counter(r['category'] for r in rows).items())),rows=rows)
    result=dict(reports=reports,target_state='Target existence is rechecked against the current working tree after data completion.',ownership_review='No target in this run’s owned layer is missing. Shared data and earlier study paths remain for their owners/coordinator to resolve.',
                legacy_manifest_rule='verify_knowledge_repo.py forbids data paths other than data/README.md; the separately authorized data/MANIFEST.json needs a maintainer-reviewed exception outside this phase’s owned tools.')
    (RUN/'verification-error-review.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    for name,report in reports.items():print(name,report['categories'])
    assert not any(r['category']=='owned-missing-target' for report in reports.values() for r in report['rows'])


if __name__=='__main__':main()
