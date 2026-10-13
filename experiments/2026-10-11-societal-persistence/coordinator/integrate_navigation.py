"""Append new research navigation over current shared files, preserving their bytes."""
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
PACKAGE=HERE.parent
RAW=ROOT/"data/raw/2026-10-11-societal-persistence/coordinator/navigation-v1"
NAV=("README.md","knowledge/INDEX.md","knowledge/experiments/registry.json","knowledge/retrospectives/README.md")

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    endpoint=HERE/"navigation-integration-v1.json"
    if endpoint.exists() or RAW.exists(): raise SystemExit("Navigation integration exists; do not overwrite.")
    additions=json.loads((HERE/"registry-additions.json").read_text(encoding="utf-8"))
    registry=json.loads((ROOT/NAV[2]).read_text(encoding="utf-8"))
    existing={r["id"] for r in registry["experiments"]}
    if existing & {r["id"] for r in additions}: raise SystemExit("A requested registry ID already exists.")
    for entry in additions:
        for path in entry["evidence"]:
            if not (ROOT/path).is_file(): raise SystemExit("Missing proposed evidence: "+path)
    texts={name:(ROOT/name).read_text(encoding="utf-8") for name in NAV if not name.endswith(".json")}
    marker="|---|---|\n"
    if marker not in texts[NAV[0]]: raise SystemExit("README navigation marker unavailable.")
    texts[NAV[0]]=texts[NAV[0]].replace(marker,marker+"| Minimum capacities for long societal persistence | [Theory and findings](experiments/2026-10-11-societal-persistence/REPORT.md), [manuscript](experiments/2026-10-11-societal-persistence/MANUSCRIPT.md), [survey](experiments/2026-10-11-societal-persistence/literature/SURVEY.md) |\n",1)
    texts[NAV[1]]+="\n## Societal persistence and renewal, October 11\n\nThe [reviewed theory](../experiments/2026-10-11-societal-persistence/REPORT.md) and [manuscript](../experiments/2026-10-11-societal-persistence/MANUSCRIPT.md) develop minimum functional conditions relative to an outcome, boundary and horizon. A 25-work scoped primary survey identifies direct precedents; a separate 14-work Harappan application codes 34 observations of renewal, dependence and changing use.\n\nThe [finite constructions](../experiments/2026-10-11-societal-persistence/MODEL-RESULTS.md) distinguish current service from replacement capacity, shared deadlines and shared inputs. A post-baseline repair/learning variant changes the result under explicit alternative costs. Independent model and source reviews are preserved. The [empirical design](../experiments/2026-10-11-societal-persistence/EMPIRICAL-PROTOCOL.md) requires independently bounded delivery and dated operations before a numerical archaeological minimum can be estimated. [Retrospective](retrospectives/2026-10-11-societal-persistence.md).\n"
    texts[NAV[3]]+="\nThe [societal persistence program](2026-10-11-societal-persistence.md) records direct theoretical predecessors, source-qualified Harappan renewal, conditional output and work-window bounds, shared repair/learning, preserved access failures and independent counterexample and numerical review. Its next tests need measured delivery, renewal windows and participation rather than a generic complexity score.\n"
    RAW.mkdir(parents=True)
    records=[]
    for name in NAV:
        path=ROOT/name; snapshot=RAW/name; snapshot.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(path,snapshot)
        records.append({"path":name,"snapshot":snapshot.relative_to(ROOT).as_posix(),"before_sha256":sha(path)})
    registry["experiments"]+=additions
    for name,value in texts.items(): (ROOT/name).write_text(value,encoding="utf-8")
    (ROOT/NAV[2]).write_text(json.dumps(registry,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    for record in records: record["after_sha256"]=sha(ROOT/record["path"])
    with endpoint.open("x",encoding="utf-8") as stream:
        json.dump({"created_utc":datetime.now(timezone.utc).isoformat(),"files":records,"registry_entries_added":len(additions),
                   "prior_registry_objects_retained":len(registry["experiments"])-len(additions)},stream,indent=2); stream.write("\n")
    print(json.dumps({"files":len(records),"registry_entries":len(registry["experiments"]),"added":len(additions)}))

if __name__=="__main__": main()
