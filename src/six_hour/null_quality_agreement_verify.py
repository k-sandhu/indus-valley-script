"""Independent generation, integer tails and hypergeometric score audit."""
from collections import Counter, defaultdict
from fractions import Fraction as F
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys
import time

import numpy as np

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "knowledge").is_dir())
PARENT = ROOT / "experiments/2026-10-02-six-hour/null-calibration"
QUALITY = PARENT / "shared-quality"
FOLDER = QUALITY / "agreement-diagnostic"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def generator(seed):
    rng = np.random.default_rng(seed)
    probabilities = np.array([.20, .16, .14, .12, .11, .10, .09, .08])
    rows, truth = [], []
    for obj in range(20):
        site, within = divmod(obj, 10)
        label = "low_error" if within < 5 else "high_error"
        rate = .025 if within < 5 else .60
        latent = [int(rng.choice(8, p=np.roll(probabilities, site + 2 * slot))) for slot in range(3)]
        faces = []
        for face in range(2):
            values, changes = [], []
            for x in latent:
                change = bool(rng.random() < rate)
                y = int(rng.choice([a for a in range(8) if a != x])) if change else x
                values.append(f"{y + 1:03d}")
                changes.append(change)
            rows.append({"record_id": f"record_{2 * obj + face:03d}", "seq": tuple(values), "artifact": f"artifact_{obj:03d}",
                         "artifact_aliases": [f"artifact_{obj:03d}"], "site": f"site_{site}", "object_type": "SEAL:S",
                         "quality": label, "stratum": (f"site_{site}", "SEAL:S")})
            faces.append({"face": face, "replacement_indicators": changes})
        truth.append({"artifact": f"artifact_{obj:03d}", "quality": label, "latent_seq": [f"{x + 1:03d}" for x in latent], "faces": faces})
    return rows, {"seed": seed, "latent_objects": 20, "rates": {"low_error": .025, "high_error": .6}, "truth": truth}


def oracle_score(rows, oracle):
    total = 0
    for a, b in oracle.pairs(rows):
        left, right = rows[a]["seq"], rows[b]["seq"]
        total += int(left[0] == right[0] and left[1] == right[1])
        total += int(left[1] == right[1] and left[2] == right[2])
    return total


def choose(n, a):
    return math.comb(n, a) if 0 <= a <= n else 0


def cell_distribution(n, counts):
    a, b, c = counts
    left = {x: choose(b, x) * choose(n - b, a - x) for x in range(b + 1)}
    right = {y: choose(b, y) * choose(n - b, c - y) for y in range(b + 1)}
    distribution = Counter()
    for x, wx in left.items():
        for y, wy in right.items():
            if wx and wy:
                distribution[x + y] += choose(n, b) * wx * wy
    assert sum(distribution.values()) == choose(n, a) * choose(n, b) * choose(n, c)
    return distribution


def conditional(rows, quality, oracle):
    cells = defaultdict(list)
    for pair in oracle.pairs(rows):
        row = rows[pair[0]]
        cells[(3, tuple(row["stratum"]), row["quality"] if quality else "")].append(pair)
    distribution, records, mean = Counter({0: 1}), [], F(0)
    for profile, pairs in sorted(cells.items()):
        n = len(pairs)
        counts = tuple(sum(rows[a]["seq"][slot] == rows[b]["seq"][slot] for a, b in pairs) for slot in range(3))
        records.append({"profile": profile, "objects": n, "agreement_counts": counts})
        cell = cell_distribution(n, counts)
        updated = Counter()
        for s, weight in distribution.items():
            for t, count in cell.items():
                updated[s + t] += weight * count
        distribution = updated
        mean += F(counts[0] * counts[1] + counts[1] * counts[2], n)
    total = sum(distribution.values())
    assert F(sum(s * count for s, count in distribution.items()), total) == mean
    observed = oracle_score(rows, oracle)
    tail = F(sum(count for s, count in distribution.items() if s >= observed), total)
    return records, mean, tail, total


def norm(value):
    return json.loads(json.dumps(value))


def run():
    output = FOLDER / "verification.json"
    if output.exists():
        raise FileExistsError("Refusing an existing agreement diagnostic audit")
    folder = FOLDER / "main"
    state = json.loads((folder / "results.json").read_text())
    assert state["status"] == "complete" and state["datasets"] == 1000 and state["draws"] == 99
    assert sha(folder / "code_snapshot.py") == state["source_sha256"] and sha(FOLDER / "PROTOCOL.md") == state["protocol_sha256"]
    assert sha(folder / "binary_dp.json") == state["binary_dp_sha256"]
    module = load(folder / "code_snapshot.py", "agreement_snapshot")
    quality_module = module.source()
    old = quality_module.methods()[1]
    oracle_path = QUALITY / "audit-sources/null_quality_verify.py"
    assert sha(oracle_path) == "3d92080378f4bb095f0be095f7100547442a31256fc1e3bb3a1e2a2b500a07ca"
    oracle = load(oracle_path, "agreement_vector_oracle")
    dp = json.loads((folder / "binary_dp.json").read_text())
    checked_cells = 0
    for n, cases in dp.items():
        assert len(cases) == (int(n) + 1)**3
        for case in cases:
            exact = cell_distribution(int(n), tuple(case["agreement_counts"]))
            assert {str(s): count for s, count in exact.items()} == case["score_counts"]
            checked_cells += 1
    assert checked_cells == 1547
    summaries, exact_summaries, indicators, exact_indicators, seeds = [], [], [], [], set()
    values, means, margin_changes = [], defaultdict(list), Counter()
    started, references = time.monotonic(), 0
    for index in range(1000):
        trial = json.loads((folder / f"dataset_{index:04d}.json").read_text())
        assert trial["complete"] and trial["trial_index"] == index
        rows, generation = generator(80261002 + 1009 * index)
        assert norm(rows) == trial["rows"] and generation == trial["generation"]
        observed = oracle_score(rows, oracle)
        assert observed == trial["observed_score"] == module.score(rows)
        values.append(observed)
        flags, exact_flags = [], []
        for name in ["broad_vectors", "quality_vectors"]:
            record = trial["references"][name]
            base = (160000000000 if name == "broad_vectors" else 180000000000) + index * 1000000
            assert record["accepted_seeds"] == list(range(base, base + 99)) and record["seed_base"] == base
            assert not seeds.intersection(record["accepted_seeds"])
            seeds.update(record["accepted_seeds"])
            score_values, changes = [], 0
            for draw in range(99):
                proposed = oracle.oracle_shuffle(rows, base + draw, name == "quality_vectors")
                assert oracle.scalar_counts(proposed) == oracle.scalar_counts(rows)
                assert oracle.joint_counts(proposed, False) == oracle.joint_counts(rows, False)
                assert all(all(before[key] == after[key] for key in before if key != "seq") for before, after in zip(rows, proposed))
                changed = oracle.joint_counts(proposed, True) != oracle.joint_counts(rows, True)
                if name == "quality_vectors":
                    assert not changed
                changes += changed
                score_values.append(oracle_score(proposed, oracle))
                references += 1
            assert score_values == record["null_scores"] and record["quality_margin_changes"] == changes
            margin_changes[name] += changes
            gte = sum(s >= observed for s in score_values)
            assert gte == record["exceedances"] and record["p_value"] == (1 + gte) / 100
            cells, mean, tail, total = conditional(rows, name == "quality_vectors", oracle)
            assert norm(cells) == record["cells"] and str(mean) == record["conditional_mean"]
            assert str(tail) == record["exact_tail"] and float(tail) == record["exact_tail_float"] and total == record["conditional_table_count"]
            means[name].append(float(mean))
            flags.append([int(record["p_value"] <= alpha) for alpha in [.01, .05, .1]])
            exact_flags.append([int(tail <= F(str(alpha))) for alpha in [.01, .05, .1]])
        indicators.append(flags)
        exact_indicators.append(exact_flags)
        summaries.append({"family": trial["family"], "references": {name: {"p_value": r["p_value"]} for name, r in trial["references"].items()}})
        exact_summaries.append({"family": trial["family"], "references": {name: {"p_value": r["exact_tail_float"]} for name, r in trial["references"].items()}})
        if (index + 1) % 100 == 0:
            print(json.dumps({"stage": "agreement_audit", "done": index + 1, "elapsed_seconds": time.monotonic() - started}), flush=True)
    assert old.aggregate(summaries) == state["aggregate"] and old.aggregate(exact_summaries) == state["exact_aggregate"]
    assert references == 198000 and len(seeds) == 198000 and float(np.mean(values)) == state["observed_score_mean"]
    assert {name: float(np.mean(data)) for name, data in means.items()} == state["conditional_mean_average"]
    result = {"status": "pass", "simulation": True, "datasets_independently_generated": 1000, "reference_tables_replayed": references,
              "integer_scores_checked": references + 1000, "hypergeometric_cell_distributions_checked": checked_cells,
              "exact_population_tails_checked": 2000, "distinct_reference_seeds": len(seeds), "quality_margin_changes": dict(margin_changes),
              "paired_rejection": {}, "bootstrap_seed": 2026100211, "bootstrap_replicates": 20000,
              "input_results_sha256": sha(folder / "results.json"), "audit_source_sha256": sha(__file__)}
    for mode, flags in [("monte_carlo", np.asarray(indicators)), ("exact", np.asarray(exact_indicators))]:
        difference = flags[:, 0] - flags[:, 1]
        rng = np.random.default_rng(2026100211)
        boot = np.concatenate([difference[rng.integers(1000, size=(1000, 1000))].mean(axis=1) for _ in range(20)])
        ci = np.quantile(boot, [.025, .975], axis=0)
        result["paired_rejection"][mode] = {}
        for j, alpha in enumerate([.01, .05, .1]):
            broad, quality = flags[:, 0, j], flags[:, 1, j]
            result["paired_rejection"][mode][str(alpha)] = {"both": int(np.sum((broad == 1) & (quality == 1))),
                                                          "broad_only": int(np.sum((broad == 1) & (quality == 0))),
                                                          "quality_only": int(np.sum((broad == 0) & (quality == 1))),
                                                          "neither": int(np.sum((broad == 0) & (quality == 0))),
                                                          "broad_minus_quality_rate": float(difference[:, j].mean()), "paired_95_interval": ci[:, j].tolist()}
    result["elapsed_seconds"] = time.monotonic() - started
    result["checks"] = ["source_hashes", "independent_fresh_generation", "integer_statistic", "every_vector_reference_and_margin",
                        "all_inclusive_MC_tails", "all_hypergeometric_DP_correspondence", "all_exact_tails_and_means", "aggregates", "paired_bootstrap"]
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    run()
