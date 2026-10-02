"""Generate meaningful nonphonetic route codes with explicit graph semantics.

Each Q sign denotes an arbitrary office entity, not its spoken name. A sequence
records a route through a legal workflow graph. Node transitions encode allowed
direct handoffs. The control is not proposed as an Indus historical explanation.
"""
import json
from pathlib import Path
import random

seed = 20261001
rng = random.Random(seed)
records = []
for i in range(3000):
    route = [rng.randrange(20)]
    for j in range(5):
        route.append((route[-1] + rng.choice([1, 7])) % 20)
    records.append({
        "record_id": f"workflow{i:04d}",
        "object_family_id": str(i),
        "signs_reading_rtl": [f"Q{node:02d}" for node in route],
        "length": len(route), "site": "districtA" if i % 2 else "districtB",
        "object_type": "dispatch_card", "complete_observed": True,
        "single_line": True, "direction": "synthetic_reading_order",
        "semantics": {"workflow_route_node_ids": route, "meaning": "an ordered path of direct handoffs through an office graph", "contains_phonetic_encoding": False},
    })
out = Path("research/methods/controls")
out.mkdir(parents=True, exist_ok=True)
(out / "workflow_codes.jsonl").write_text("\n".join(json.dumps(row) for row in records), encoding="utf-8")
(out / "workflow_definition.json").write_text(json.dumps({
    "seed": seed, "records": len(records), "nodes": 20, "route_length": 6,
    "transition_rule": "from node n, choose (n+1)mod20 or(n+7)mod20 with equal probability",
    "sign_semantics": "Qxx directly identifies office entity xx; no phonetic or word value",
    "sequence_semantics": "ordered administrative handoff route, not a transcription of an utterance",
    "purpose": "constructive non-specificity control only; not a claim about actual Indus administration",
}, indent=2), encoding="utf-8")
print("Wrote", len(records), "nonphonetic workflow route records")
