"""Audit reference seed reuse and linked-trial copy rejection differences."""
from collections import defaultdict
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent


def main():
    destination = HERE / "paired_seed_audit.json"
    if destination.exists():
        raise FileExistsError("Frozen paired seed audit already exists")
    state = json.loads((HERE / "main/results.json").read_text(encoding="utf-8"))
    assert state["status"] == "complete" and state["datasets_per_family"] == 1000
    seed_uses = defaultdict(list)
    trials = []
    for index in range(1000):
        trial = json.loads((HERE / f"main/physical_copies/dataset_{index:04d}.json").read_text(encoding="utf-8"))
        assert trial["complete"] and trial["trial_index"] == index
        trials.append(trial)
        for reference, result in trial["references"].items():
            assert len(result["accepted_seeds"]) == len(set(result["accepted_seeds"])) == 99
            for seed in result["accepted_seeds"]:
                seed_uses[seed].append((index, reference))
    reused = {seed: uses for seed, uses in seed_uses.items() if len(uses) > 1}
    assert len(reused) == 49500 and all(len(uses) == 2 for uses in reused.values())
    links = defaultdict(int)
    for uses in reused.values():
        uses = sorted(uses)
        assert uses[0][1] == "block_columns" and uses[1][1] == "record_columns"
        assert uses[1][0] - uses[0][0] == 500
        links[(uses[0][0], uses[1][0])] += 1
    assert len(links) == 500 and set(links.values()) == {99}
    thresholds = [.01, .05, .10]
    record = np.array([[trial["references"]["record_columns"]["p_value"] <= alpha for alpha in thresholds] for trial in trials], dtype=int)
    block = np.array([[trial["references"]["block_columns"]["p_value"] <= alpha for alpha in thresholds] for trial in trials], dtype=int)
    differences = record - block
    clusters = np.array([(differences[left] + differences[right]) / 2 for left, right in sorted(links)])
    assert clusters.shape == (500, 3)
    assert np.array_equal(clusters.mean(axis=0), differences.mean(axis=0))
    rng = np.random.default_rng(2026100203)
    means = []
    for _ in range(20):
        indices = rng.integers(500, size=(1000, 500))
        means.append(clusters[indices].mean(axis=1))
    interval = np.quantile(np.concatenate(means), [.025, .975], axis=0)
    paired = {}
    for i, alpha in enumerate(thresholds):
        paired[str(alpha)] = {"both_reject": int(np.sum((record[:, i] == 1) & (block[:, i] == 1))),
                              "record_only": int(np.sum((record[:, i] == 1) & (block[:, i] == 0))),
                              "block_only": int(np.sum((record[:, i] == 0) & (block[:, i] == 1))),
                              "neither_reject": int(np.sum((record[:, i] == 0) & (block[:, i] == 0))),
                              "record_minus_block_rate": float(differences[:, i].mean()),
                              "cluster_bootstrap_95_interval": interval[:, i].tolist()}
    result = {"status": "pass", "physical_copy_trials": 1000, "reference_draws": 198000,
              "distinct_reference_seeds": len(seed_uses), "reused_reference_seeds": len(reused),
              "linked_trial_pairs": [{"trials": pair, "shared_seeds": count} for pair, count in sorted(links.items())],
              "paired_rejection": paired, "bootstrap_seed": 2026100203, "bootstrap_replicates": 20000,
              "checks": ["actual_accepted_seed_overlap", "within_reference_seed_uniqueness",
                         "linked_cluster_mean_correspondence", "paired_rejection_counts"]}
    destination.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key != "linked_trial_pairs"}))


if __name__ == "__main__":
    main()
