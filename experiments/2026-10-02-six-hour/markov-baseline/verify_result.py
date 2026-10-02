"""Read-only independent count-formula audit of the saved Markov predictions."""
from collections import Counter, defaultdict
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
from methods.conditional_structure import UNKNOWN, group_records, load_records, make_folds


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    folder = Path(__file__).parent / "main"
    result = json.loads((folder / "results.json").read_text(encoding="utf-8"))
    assert result["source_sha256"] == sha(folder / "code_snapshot.py")
    assert result["helper_sha256"] == sha(folder / "conditional_structure_snapshot.py")
    assert result["protocol_sha256"] == sha(folder.parent / "PROTOCOL.md")
    spec = importlib.util.spec_from_file_location("markov_snapshot", folder / "code_snapshot.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    rows, _ = load_records(ROOT / "data/normalized/lipi_clean_rtl_singleline.jsonl", min_length=3, unique=True)
    groups = group_records(rows)
    assignments, loads = make_folds(rows, groups, 5, result["parameters"]["seed"])
    scored = module.read_jsonl(folder / "markov_slot_audit.jsonl")
    by_key = {(score["record_id"], score["slot"]): score for score in scored}
    assert len(by_key) == len(scored) == 8009
    maximum_mass_error = 0.0
    maximum_loss_error = 0.0
    checks = 0
    for fold in range(5):
        train = [row for i, row in enumerate(rows) if assignments[i] != fold]
        test = [row for i, row in enumerate(rows) if assignments[i] == fold]
        train_aliases = {alias for row in train for alias in row["artifact_aliases"]}
        test_aliases = {alias for row in test for alias in row["artifact_aliases"]}
        assert not train_aliases.intersection(test_aliases)
        assert not {row["seq"] for row in train}.intersection({row["seq"] for row in test})
        signs = sorted({sign for row in train for sign in row["seq"]}) + [UNKNOWN]
        counts = Counter(sign for row in train for sign in row["seq"])
        starts = Counter(row["seq"][0] for row in train)
        pairs = Counter()
        for row in train:
            sequence = row["seq"]
            pairs.update(zip(sequence[:-1], sequence[1:]))
            pairs[(sequence[-1], "END")] += 1
        outgoing = Counter()
        for (left, right), count in pairs.items():
            outgoing[left] += count
        glyph_total = sum(counts.values()) + 0.5 * len(signs)
        destination_total = glyph_total + len(train) + 0.5
        q = {sign: (counts[sign] + 0.5) / destination_total for sign in signs}
        q["END"] = (len(train) + 0.5) / destination_total
        alpha = result["folds"][fold]["chosen_alpha"]

        def transition(left, right):
            return (pairs[(left, right)] + alpha * q[right]) / (outgoing[left] + alpha)

        for row in test:
            for slot, actual in enumerate(row["seq"]):
                successor = row["seq"][slot + 1] if slot + 1 < len(row["seq"]) else "END"
                if successor != "END" and successor not in q:
                    successor = UNKNOWN
                previous = row["seq"][slot - 1] if slot else None
                if previous is not None and previous not in q:
                    previous = UNKNOWN
                weights = []
                for candidate in signs:
                    initial_or_previous = transition(previous, candidate) if previous is not None else (starts[candidate] + alpha * (counts[candidate] + 0.5) / glyph_total) / (len(train) + alpha)
                    weights.append(initial_or_previous * transition(candidate, successor))
                probabilities = np.asarray(weights) / sum(weights)
                rank = np.argsort(-probabilities, kind="stable")
                saved = by_key[(row["record_id"], slot)]
                assert [item["code"] for item in saved["suggestions"]] == [signs[index] for index in rank[:10]]
                for item, index in zip(saved["suggestions"], rank[:10]):
                    maximum_mass_error = max(maximum_mass_error, abs(item["model_mass"] - probabilities[index]))
                actual_index = signs.index(actual if actual in q else UNKNOWN)
                maximum_loss_error = max(maximum_loss_error, abs(saved["bucket_loss_bits"] + math.log2(probabilities[actual_index])))
                assert saved["top1"] == (signs[rank[0]] == actual)
                assert saved["top5"] == (actual in [signs[index] for index in rank[:5]])
                assert saved["top10"] == (actual in [signs[index] for index in rank[:10]])
                assert saved["known_in_training"] == (actual in signs)
                if not saved["known_in_training"]:
                    assert not saved["top1"] and not saved["top5"] and not saved["top10"]
                checks += 1
    assert maximum_mass_error < 1e-12 and maximum_loss_error < 1e-10
    summary = module.summarize(scored)
    assert summary == result["models"]["Markov"]
    for name, comparison in result["paired"].items():
        if name == "Markov_minus_PM":
            first, second = result["models"]["PM"], summary
        else:
            first, second = summary, result["models"]["PMB"]
        for metric in ["top1", "top5", "top10"]:
            assert abs(comparison["metrics"][metric + "_slot"]["difference"] - (second[metric] - first[metric])) < 1e-12
        assert abs(comparison["metrics"]["top1_type"]["difference"] - (second["macro_type"]["top1"] - first["macro_type"]["top1"])) < 1e-12
    report = {"passed": True, "queries_checked": checks,
              "maximum_top10_mass_error": maximum_mass_error, "maximum_bucket_loss_error": maximum_loss_error,
              "checks": ["saved_code_helper_protocol_hashes", "all_fold_alias_and_text_exclusions", "all_top10_rankings_from_independent_counts", "all_target_losses_from_independent_counts", "all_exact_accuracy_flags", "OOV_exact_failure_rule", "all_summary_fields", "paired_point_estimates"],
              "audit_source_sha256": sha(__file__)}
    path = Path(__file__).parent / "verification.json"
    if path.exists():
        raise FileExistsError("Preserve the existing verification record before repeating the audit")
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
