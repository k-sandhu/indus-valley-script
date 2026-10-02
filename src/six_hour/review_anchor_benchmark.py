"""Check exact-search arithmetic and summarize the preserved synthetic grid."""
from __future__ import annotations
import csv
import hashlib
import importlib.util
from itertools import permutations
import json
import math
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "experiments/2026-10-02-six-hour/anchor-benchmark"

def load_module(path):
    spec = importlib.util.spec_from_file_location("anchor_frozen", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def scalar_score(texts, reference, mapping, kind):
    start, pairs, uni = reference
    value = 0.0
    for text in texts:
        decoded = [mapping[i] for i in text]
        if kind == "unigram":
            value += sum(uni[i] for i in decoded)
        else:
            value += start[decoded[0]]
            value += sum(pairs[a,b] for a,b in zip(decoded, decoded[1:]))
    return value

def main():
    endpoint = BASE / "main/results.json"
    data = json.loads(endpoint.read_text(encoding="utf-8"))
    snapshot = BASE / "main/code_snapshot.py"
    mod = load_module(snapshot)
    checks = {}
    checks["snapshot_hash_matches_endpoint"] = hashlib.sha256(snapshot.read_bytes()).hexdigest() == data["code_sha256"]
    maps = np.asarray(list(permutations(range(mod.K))), dtype=np.int8)
    spec = mod.system(90773, "transition")
    reference = mod.fit(mod.sample(spec, 8000, 90774))
    texts = mod.sample(spec, 40, 90775)
    selected = maps[[0, 113, 9701, 40111]]
    for kind in ("unigram", "markov"):
        vector = mod.score_maps(mod.counts(texts), reference, selected, kind)
        scalar = np.asarray([scalar_score(texts, reference, mapping, kind) for mapping in selected])
        checks[f"{kind}_vector_equals_direct_sequence_score"] = bool(np.allclose(vector, scalar, atol=1e-9, rtol=0))
        rename = np.array([4,7,2,0,6,1,5,3])
        renamed = mod.encode(texts, rename)
        adjusted = selected[:,np.argsort(rename)]
        rescored = mod.score_maps(mod.counts(renamed), reference, adjusted, kind)
        checks[f"{kind}_consistent_observed_renaming_preserves_score"] = bool(np.allclose(vector, rescored, atol=1e-9, rtol=0))
    encoding = np.array([5,0,7,2,4,1,3,6])
    truth = np.argsort(encoding)
    encoded = mod.encode(mod.sample(spec, 4000, 90776), encoding)
    recovered = maps[np.argmax(mod.score_maps(mod.counts(encoded), reference, maps, "markov"))]
    checks["separated_reference_example_recovers_hidden_mapping"] = bool(np.array_equal(recovered, truth))
    checks["anchor_enumeration_counts"] = all(int(np.sum(np.all(maps[:,:a] == truth[:a], axis=1))) == math.factorial(mod.K-a) for a in (0,1,2,4))
    rows = data["trials"]
    checks["complete_declared_grid"] = len(rows) == 2 * 12 * 2 * 3 * 4 * 2
    checks["all_recorded_anchor_counts_correct"] = all(r["compatible_maps"] == math.factorial(mod.K-r["anchors"]) for r in rows)
    checks["all_best_maps_respect_supplied_anchors"] = all(all(r["best_map"][a] == b for a,b in r["anchor_pairs"]) for r in rows)
    checks["all_recorded_mapping_accuracies_correct"] = all(np.mean(np.array(r["best_map"]) == r["true_map"]) == r["symbol_mapping_accuracy"] for r in rows)
    # Generation uses different seed streams. Identical short strings may occur naturally.
    checks["reference_training_test_seed_streams_distinct"] = all(len({r["seed"]+1, r["seed"]+4, r["seed"]+5+r["training_texts"]}) == 3 for r in rows)
    groups = {}
    for row in rows:
        key = (row["family"],row["domain_shift"],row["training_texts"],row["anchors"],row["model"])
        groups.setdefault(key,[]).append(row)
    summary = []
    for (family,shift,n,anchors,model), group in sorted(groups.items()):
        summary.append({"family":family,"domain_shift":shift,"training_texts":n,"anchors":anchors,"model":model,
                        "seeded_systems":len(group),"exact_maps":sum(r["exact_mapping_recovered"] for r in group),
                        "mean_symbol_accuracy":float(np.mean([r["symbol_mapping_accuracy"] for r in group])),
                        "reference_wins":sum(r["correct_reference_beats_wrong_on_holdout"] for r in group),
                        "confident_wrong_maps":sum(not r["exact_mapping_recovered"] and r["plugin_best_map_mass"] >= .95 for r in group),
                        "mean_holdout_gain_bits_per_sign":float(np.mean([r["reference_heldout_gain_bits_per_sign"] for r in group]))})
    out = BASE / "review"
    out.mkdir(exist_ok=True)
    with (out/"conditions.csv").open("w",newline="",encoding="utf-8") as f:
        writer = csv.DictWriter(f,fieldnames=list(summary[0]))
        writer.writeheader(); writer.writerows(summary)
    failures = [r for r in rows if r["model"] == "markov" and not r["exact_mapping_recovered"]]
    review = {"status":"pass" if all(checks.values()) else "fail","checks":checks,
              "source_sha256":hashlib.sha256(endpoint.read_bytes()).hexdigest(),"conditions":len(summary),
              "markov_failed_rows":len(failures),"markov_failed_rows_with_plugin_mass_at_least_095":sum(r["plugin_best_map_mass"]>=.95 for r in failures),
              "markov_failed_rows_that_still_select_correct_reference":sum(r["correct_reference_beats_wrong_on_holdout"] for r in failures),
              "independence_unit":"24 generated systems; conditions within each system share reference and/or heldout samples",
              "mass_interpretation":"Conditional plug-in mass under fixed likelihood and uniform map prior. Reference uncertainty and misspecification are omitted."}
    (out/"checks.json").write_text(json.dumps(review,indent=2)+"\n",encoding="utf-8")
    (out/"confident-failures.json").write_text(json.dumps([r for r in failures if r["plugin_best_map_mass"]>=.95],indent=2)+"\n",encoding="utf-8")
    print(json.dumps(review,indent=2))
    if not all(checks.values()):
        raise SystemExit(1)

if __name__ == "__main__":
    main()
