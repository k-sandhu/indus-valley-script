"""Append navigation over current shared bytes, preserving their exact snapshot."""
import hashlib
import json
import shutil
from datetime import datetime,timezone
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
RAW=ROOT/'data/raw/2026-10-12-transmission-hypothesis/coordinator/navigation-v1'
NAV=['README.md','knowledge/INDEX.md','knowledge/experiments/registry.json','knowledge/retrospectives/README.md']
PREFIX='experiments/2026-10-12-transmission-hypothesis/'


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    out=HERE/'navigation-integration-v1.json'
    if out.exists() or RAW.exists():raise SystemExit('Navigation integration exists; no overwrite.')
    additions=json.loads((HERE/'registry-additions.json').read_text('utf-8'))
    registry=json.loads((ROOT/NAV[2]).read_text('utf-8'))
    old=registry['experiments'];newids={entry['id'] for entry in additions}
    if newids & {entry['id'] for entry in old}:raise SystemExit('Registry IDs already present.')
    for entry in additions:
        for name in entry['evidence']:
            if not (ROOT/name).is_file():raise SystemExit('Missing evidence target: '+name)
    # Build edits before changing shared files.
    texts={name:(ROOT/name).read_text('utf-8') for name in NAV if name!=NAV[2]}
    marker='| Purpose | Read |\n|---|---|'
    if texts[NAV[0]].count(marker)!=1:raise SystemExit('README navigation marker changed.')
    row='| Practical knowledge, inherited institutions and transmission into early literature | [Rival tests]('+PREFIX+'REPORT.md), [manuscript]('+PREFIX+'MANUSCRIPT.md), [adversarial review]('+PREFIX+'review/REVIEW.md) |'
    texts[NAV[0]]=texts[NAV[0]].replace(marker,marker+'\n'+row)
    texts[NAV[1]]+='\n## Transmission hypothesis, October 12\n\nThe [new historical study](../'+PREFIX+'REPORT.md) develops practical survival, recoding and conceptual incorporation through seven source-based component comparisons. Intermediate working-stage objects and crop specimens, three complete Rigvedic hymns and Iranian/Greek/Pali controls face compatible local, inherited, regional, reconstructive and later-organization routes. The sifting/speech analogy directly represents conceptual reuse; a particular Harappan literary ancestry remains untraced.\n\nRead the [manuscript](../'+PREFIX+'MANUSCRIPT.md), [claim map](../'+PREFIX+'CLAIM-EVIDENCE.json), [independent review](../'+PREFIX+'review/REVIEW.md) and [tests](../'+PREFIX+'EMPIRICAL-TESTS.md). The [retrospective](retrospectives/2026-10-12-transmission-hypothesis.md) preserves source and code corrections, local-only witnesses and the distinction between declaration checks and historical support.\n'
    texts[NAV[3]]+='\n## October 12 transmission study\n\n[Transmission after the Indus cities](2026-10-12-transmission-hypothesis.md) records new material/textual comparisons, inherited-role controls, the represented sifting/speech association, missing carrier transitions and the validator\'s semantic boundary. Consult it before repeating the proposed operation or literary-origin tests.\n'
    registry['experiments']=old+additions
    RAW.mkdir(parents=True);records=[]
    for name in NAV:
        snapshot=RAW/name;snapshot.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/name,snapshot)
        records.append({'path':name,'snapshot':snapshot.relative_to(ROOT).as_posix(),'before_sha256':sha(snapshot)})
    for name in NAV:
        if name==NAV[2]:value=json.dumps(registry,ensure_ascii=False,indent=2)+'\n'
        else:value=texts[name]
        (ROOT/name).write_text(value,encoding='utf-8',newline='\n')
    for record in records:record['after_sha256']=sha(ROOT/record['path'])
    with out.open('x',encoding='utf-8') as stream:
        json.dump({'created_utc':datetime.now(timezone.utc).isoformat(),'files':records,
                   'registry_entries_added':len(additions),'prior_registry_objects_retained':len(old)},stream,indent=2);stream.write('\n')
    print(json.dumps({'navigation_files':len(records),'registry_added':len(additions),'registry_total':len(registry['experiments'])}))


if __name__=='__main__':main()
