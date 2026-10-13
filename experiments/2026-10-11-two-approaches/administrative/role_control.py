"""Post-outcome W700-bearing-face allocation control; see dated amendment."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path

import numpy as np

OWN = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("administrative_frozen", OWN / "analyze.py")
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)


class RolePopulation(base.Population):
    def __init__(self, objects, unique):
        super().__init__(objects, unique)
        for cell in self.cells:
            byrole = defaultdict(list)
            for i in cell["objects"]:
                for slot in self.ranges[i]:
                    seq = self.seqs[self.assignment[slot]]
                    byrole[(len(seq), "700" in seq)].append(slot)
            cell["buckets"] = [np.array(v, int) for _, v in sorted(byrole.items())]

    def summary(self):
        out = super().summary()
        out["allocation_role"] = "whole-module W700 presence within each exact length bucket"
        out["w700_bearing_faces_per_object_histogram"] = dict(Counter(sum("700" in seq for seq in o["sequences"]) for o in self.objects))
        out["objects_with_any_w700_bearing_face"] = sum(any("700" in seq for seq in o["sequences"]) for o in self.objects)
        out["declared_side_count_compatible_objects"] = sum(all(str(v) == str(len(o["sequences"])) for v in o["declared_sides"]) for o in self.objects)
        return out


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default="role-control-v1")
    ap.add_argument("--pilot", type=int, default=1999)
    ap.add_argument("--references", type=int, default=4999)
    ap.add_argument("--seed", type=int, default=2026102117)
    ap.add_argument("--cap", type=int, default=1000000)
    args = ap.parse_args()
    out, raw = OWN / args.out, base.RAW / args.out
    if out.exists() or raw.exists() or Path(args.out).name != args.out:
        raise ValueError("Choose a fresh output directory")
    out.mkdir(parents=True, exist_ok=False)
    raw.mkdir(parents=True, exist_ok=False)
    rows = [json.loads(l) for l in base.INPUT.read_text(encoding="utf-8").splitlines()]
    groups, _ = base.physical_groups(rows)
    results = []
    for j, mode in enumerate(["rtl", "mirror"]):
        objects, _, _ = base.prepare(groups, mode)
        proto, _ = base.prototypes(objects)
        for k, (label, obs, unique) in enumerate([("all", objects, False), ("prototypes", proto, True)]):
            pop = RolePopulation(obs, unique)
            result = base.reference(pop, f"{mode}-{label}", out, raw, args.pilot,
                                    args.references, args.seed + 100 * j + 10 * k, args.cap)
            result["status_scope"] = "Exploratory post-outcome face-role control"
            results.append(result)
    ntests = base.holm(results)
    for r in results:
        base.write(out / f"{r['name']}.json", r)
    base.write(out / "summary.json", {"status": "Exploratory post-outcome W700-role control",
                                      "created_utc": datetime.now(timezone.utc).isoformat(),
                                      "input_sha256": base.sha(base.INPUT),
                                      "base_code_sha256": base.sha(OWN / "analyze.py"),
                                      "control_code_sha256": base.sha(__file__),
                                      "amendment_sha256": base.sha(OWN / "AMENDMENT-2026-10-11-role-control.md"),
                                      "completed_tests": ntests, "expected_tests": 10,
                                      "seed": args.seed, "pilot": args.pilot, "references": args.references,
                                      "results": [{"name": r["name"], "status": r["status"], "tests": r.get("tests", {})} for r in results],
                                      "local_raw_path": raw.relative_to(base.ROOT).as_posix()})
    (out / "code_snapshot.py").write_bytes(Path(__file__).read_bytes())
    (out / "base_code_snapshot.py").write_bytes((OWN / "analyze.py").read_bytes())
    (out / "protocol_snapshot.md").write_bytes((OWN / "AMENDMENT-2026-10-11-role-control.md").read_bytes())


if __name__ == "__main__":
    main()
