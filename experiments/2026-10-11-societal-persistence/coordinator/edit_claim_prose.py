"""Space working claim prose before final review; numeric outputs are untouched."""
import copy
import hashlib
import json
from pathlib import Path
import sys
sys.dont_write_bytecode=True
from prepare_claims import readable

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
path=HERE.parent/"CLAIM-EVIDENCE.json"
raw=ROOT/"data/raw/2026-10-11-societal-persistence/coordinator/claim-editorial-v1"
if raw.exists(): raise SystemExit("Claim draft snapshot exists; do not overwrite.")
raw.mkdir(parents=True)
before=path.read_bytes()
(raw/path.name).write_bytes(before)
original=json.loads(before.decode("utf-8"))
current=copy.deepcopy(original)
for claim in current["claims"]: claim["statement"]=readable(claim["statement"])
for old,new in zip(original["claims"],current["claims"]):
    for field in old:
        if field!="statement": assert old[field]==new[field]
after=(json.dumps(current,indent=2)+"\n").encode("utf-8")
path.write_bytes(after)
record={"scope":"Working document prose correction before final review; IDs, pointers, assertions and all numerical values retained",
        "snapshot":(raw/path.name).relative_to(ROOT).as_posix(),"before_sha256":hashlib.sha256(before).hexdigest(),
        "after_sha256":hashlib.sha256(after).hexdigest(),"claims":len(current["claims"])}
with (HERE/"claim-editorial-v1.json").open("x",encoding="utf-8") as stream:
    json.dump(record,stream,indent=2); stream.write("\n")
print(json.dumps({"claims":record["claims"],"numeric_values_changed":False}))
