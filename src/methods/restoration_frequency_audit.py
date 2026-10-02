"""Descriptive held-out accuracy by glyph frequency; no tuning or root edits."""
from collections import Counter, defaultdict
import json
from pathlib import Path

import numpy as np

from conditional_structure import digest


directory = Path("results/restoration")
base = [json.loads(line) for line in (directory / "baseline_slot_audit.jsonl").read_text(encoding="utf-8").splitlines()]
local = [json.loads(line) for line in (directory / "local_slot_audit.jsonl").read_text(encoding="utf-8").splitlines()]
counts = Counter(s["actual"] for s in local)
per_type = defaultdict(lambda: [0, 0, 0])
strata = defaultdict(list)
for a, b in zip(base, local):
    assert (a["record_id"], a["slot"]) == (b["record_id"], b["slot"])
    n = counts[b["actual"]]
    label = "1" if n == 1 else "2-4" if n <= 4 else "5-19" if n <= 19 else "20+"
    strata[label].append((a, b))
    values = per_type[b["actual"]]
    values[0] += a["top1"]
    values[1] += b["top1"]
    values[2] += 1
result = {
    "scope": "Exploratory descriptive frequency audit of already-held-out predictions; frequency strata use the complete benchmark labels and do not tune any model.",
    "source_sha256": digest(__file__),
    "benchmark_sha256": digest(directory / "benchmark.json"),
    "glyph_types": len(per_type),
    "macro_type_top1_baseline": float(np.mean([a / n for a, b, n in per_type.values()])),
    "macro_type_top1_local": float(np.mean([b / n for a, b, n in per_type.values()])),
    "frequency_strata": {label: {
        "slots": len(pairs), "types": len({b["actual"] for a, b in pairs}),
        "baseline_top1": float(np.mean([a["top1"] for a, b in pairs])),
        "local_top1": float(np.mean([b["top1"] for a, b in pairs])),
        "unknown_in_training_rate": float(np.mean([not b["known_in_training"] for a, b in pairs])),
    } for label, pairs in sorted(strata.items())},
    "interpretation": "Common glyphs dominate token accuracy. Unseen fine codes remain failures; this is graphic prediction, not a semantic dictionary or recovered language.",
}
output = Path("research/methods/restoration_frequency_audit.json")
output.write_text(json.dumps(result, indent=2), encoding="utf-8")
print(json.dumps(result, indent=2))
