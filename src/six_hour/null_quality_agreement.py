"""Post-outcome integer diagnostic for quality shared across paired observations."""
from collections import Counter, defaultdict
from fractions import Fraction as F
import hashlib
import importlib.util
import itertools
import json
import math
from pathlib import Path
import shutil
import sys
import time

import numpy as np

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "knowledge").is_dir())
PARENT = ROOT / "experiments/2026-10-02-six-hour/null-calibration"
QUALITY = PARENT / "shared-quality"
FOLDER = QUALITY / "agreement-diagnostic"
SOURCE = QUALITY / "main/code_snapshot.py"
SOURCE_HASH = "1e86c0905b483fd7cf534cff73044fa131403ecf7c31ca1e16b3f9a21eef6e69"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def source():
    assert sha(SOURCE) == SOURCE_HASH
    spec = importlib.util.spec_from_file_location("agreement_quality_snapshot", SOURCE)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def score(rows):
    pairs = defaultdict(list)
    for row in rows:
        pairs[row["artifact"]].append(row["seq"])
    total = 0
    for sequences in pairs.values():
        assert len(sequences) == 2
        a = [int(x == y) for x, y in zip(*sequences)]
        total += a[0] * a[1] + a[1] * a[2]
    assert 0 <= total <= 40
    return total


def dp(n):
    states = {(0, 0, 0, 0): 1}
    for _ in range(n):
        new = defaultdict(int)
        for (a, b, c, s), count in states.items():
            for x, y, z in itertools.product(range(2), repeat=3):
                new[(a + x, b + y, c + z, s + x * y + y * z)] += count
        states = new
    result = defaultdict(Counter)
    for (a, b, c, s), count in states.items():
        result[(a, b, c)][s] += count
    assert len(result) == (n + 1)**3
    for counts, distribution in result.items():
        total = math.prod(math.comb(n, a) for a in counts)
        assert sum(distribution.values()) == total
        assert F(sum(s * count for s, count in distribution.items()), total) == F(counts[0] * counts[1] + counts[1] * counts[2], n)
    assert sum(sum(d.values()) for d in result.values()) == 8**n
    return dict(result)


def cells(rows, quality, module):
    result = []
    for profile, pairs in sorted(module.vector_cells(rows, quality).items()):
        counts = tuple(sum(rows[a]["seq"][slot] == rows[b]["seq"][slot] for a, b in pairs) for slot in range(3))
        result.append({"profile": profile, "objects": len(pairs), "agreement_counts": counts})
    return result


def conditional(rows, quality, module, table):
    distribution = Counter({0: 1})
    records = cells(rows, quality, module)
    mean = F(0)
    for record in records:
        n, counts = record["objects"], record["agreement_counts"]
        mean += F(counts[0] * counts[1] + counts[1] * counts[2], n)
        cell = table[n][counts]
        updated = defaultdict(int)
        for left, a in distribution.items():
            for right, b in cell.items():
                updated[left + right] += a * b
        distribution = Counter(updated)
    total = sum(distribution.values())
    assert F(sum(s * count for s, count in distribution.items()), total) == mean
    observed = score(rows)
    tail = F(sum(count for s, count in distribution.items() if s >= observed), total)
    return {"cells": records, "conditional_mean": str(mean), "conditional_mean_float": float(mean),
            "exact_tail": str(tail), "exact_tail_float": float(tail), "conditional_table_count": total}


def run():
    module = source()
    old = module.methods()[1]
    completed = json.loads((QUALITY / "verification_main.json").read_text())
    assert completed["status"] == "pass"
    output = FOLDER / "main"
    if output.exists():
        raise FileExistsError("Refusing an existing agreement diagnostic")
    output.mkdir(parents=True)
    shutil.copyfile(__file__, output / "code_snapshot.py")
    table = {n: dp(n) for n in [5, 10]}
    serial = {str(n): [{"agreement_counts": counts, "score_counts": dict(distribution)} for counts, distribution in sorted(by_counts.items())]
              for n, by_counts in table.items()}
    (output / "binary_dp.json").write_text(json.dumps(serial, separators=(",", ":")) + "\n", encoding="utf-8")
    h = [F(1331, 1400), F(37, 175)]
    observed_mean = 20 * sum(x*x for x in h)
    broad_mean = 40 * (sum(h) / 2)**2
    state = {"status": "running", "simulation": True, "post_outcome": True, "datasets": 1000, "draws": 99,
             "source_sha256": sha(__file__), "protocol_sha256": sha(FOLDER / "PROTOCOL.md"), "quality_source_sha256": SOURCE_HASH,
             "prior_nested_results_sha256": sha(QUALITY / "main/results.json"), "prior_nested_audit_sha256": sha(QUALITY / "verification_main.json"),
             "binary_dp_sha256": sha(output / "binary_dp.json"), "generator_expected_score": str(observed_mean),
             "broad_reference_expected_conditional_mean": str(broad_mean), "expected_mean_difference": str(observed_mean - broad_mean)}
    summaries, exact_summaries, score_values, mean_values = [], [], [], defaultdict(list)
    started = time.monotonic()
    prior_seeds = {40261002 + 1009 * i for i in range(1000)} | {60261002 + 1009 * i for i in range(300)}
    generator_seeds = {80261002 + 1009 * i for i in range(1000)}
    assert len(generator_seeds) == 1000 and not prior_seeds.intersection(generator_seeds)
    def save():
        state["completed_datasets"] = len(summaries)
        state["elapsed_seconds"] = time.monotonic() - started
        state["aggregate"] = old.aggregate(summaries) if summaries else {}
        state["exact_aggregate"] = old.aggregate(exact_summaries) if exact_summaries else {}
        (output / "state.json").write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    try:
        for index in range(1000):
            rows, generation = module.population(80261002 + 1009 * index)
            observed = score(rows)
            assert score([dict(row, quality="ignored") for row in rows]) == observed
            trial = {"complete": False, "family": "agreement_diagnostic", "trial_index": index, "rows": rows,
                     "generation": generation, "observed_score": observed, "references": {}}
            target_broad, target_quality = module.margins(rows, False), module.margins(rows, True)
            for ref_index, name in enumerate(["broad_vectors", "quality_vectors"]):
                base = 160000000000 + ref_index * 20000000000 + index * 1000000
                null, changed = [], 0
                for draw in range(99):
                    proposed = module.shuffle(rows, base + draw, name == "quality_vectors")
                    assert module.margins(proposed, False) == target_broad
                    changed += module.margins(proposed, True) != target_quality
                    if name == "quality_vectors":
                        assert module.margins(proposed, True) == target_quality
                    null.append(score(proposed))
                gte = sum(value >= observed for value in null)
                exact = conditional(rows, name == "quality_vectors", module, table)
                trial["references"][name] = {"seed_base": base, "accepted_seeds": list(range(base, base + 99)), "null_scores": null,
                                             "quality_margin_changes": changed, "exceedances": gte, "p_value": (1 + gte) / 100, **exact}
                mean_values[name].append(exact["conditional_mean_float"])
            trial["complete"] = True
            (output / f"dataset_{index:04d}.json").write_text(json.dumps(trial, separators=(",", ":")) + "\n", encoding="utf-8")
            score_values.append(observed)
            summaries.append({"family": trial["family"], "references": {name: {"p_value": r["p_value"]} for name, r in trial["references"].items()}})
            exact_summaries.append({"family": trial["family"], "references": {name: {"p_value": r["exact_tail_float"]} for name, r in trial["references"].items()}})
            if (index + 1) % 50 == 0:
                save()
                print(json.dumps({"stage": "agreement_diagnostic", "done": index + 1, "elapsed_seconds": state["elapsed_seconds"]}), flush=True)
        state["status"] = "complete"
        state["reference_tables"] = 198000
        state["observed_score_mean"] = float(np.mean(score_values))
        state["conditional_mean_average"] = {name: float(np.mean(values)) for name, values in mean_values.items()}
        save()
        (output / "results.json").write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(state), flush=True)
    except Exception as error:
        state["status"] = "failed"
        state["failure"] = {"exception": type(error).__name__, "message": str(error)}
        save()
        raise


if __name__ == "__main__":
    run()
