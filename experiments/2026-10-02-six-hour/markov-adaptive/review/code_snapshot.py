"""Flat-count full-likelihood verification of adaptive Markov restoration."""
from fractions import Fraction as F
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import time

import numpy as np

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "knowledge").is_dir())
FOLDER = ROOT / "experiments/2026-10-02-six-hour/markov-adaptive"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def run():
    output = FOLDER / "review"
    if output.exists():
        raise FileExistsError("Refusing an existing adaptive review")
    output.mkdir()
    shutil.copyfile(__file__, output / "code_snapshot.py")
    started = time.monotonic()
    try:
        state = json.loads((FOLDER / "main/results.json").read_text())
        assert state["status"] == "complete"
        assert sha(FOLDER / "main/code_snapshot.py") == state["source_sha256"]
        assert sha(FOLDER / "PROTOCOL.md") == state["protocol_sha256"]
        main = load(FOLDER / "main/code_snapshot.py", "adaptive_frozen_main")
        base = main.BASE
        direct_module = load(FOLDER / "sources/direct_review.py", "adaptive_flat_count_review")
        assert sha(FOLDER / "sources/direct_review.py") == state["source_hashes"]["direct_review.py"]

        class Direct(direct_module.Direct):
            def __init__(self, rows, alpha, kappa):
                super().__init__(rows, alpha)
                self.kappa = kappa

            def factor(self, a, b, target):
                a, b, target = np.broadcast_arrays(a, b, target)
                prior = np.empty(a.shape)
                beginning = b == self.begin
                if np.any(beginning):
                    prior[beginning] = np.r_[self.first, 0.][target[beginning]]
                if np.any(~beginning):
                    prior[~beginning] = self.trans[b[~beginning], target[~beginning]]
                if self.kappa is None:
                    return prior
                count = np.array([self.triples[int(x), int(y), int(z)] for x, y, z in zip(a.flat, b.flat, target.flat)]).reshape(a.shape)
                n = np.array([self.contexts[int(x), int(y)] for x, y in zip(a.flat, b.flat)]).reshape(a.shape)
                effective = self.alpha + self.kappa + np.divide(self.alpha * self.kappa, n, out=np.zeros(a.shape), where=n > 0)
                values = (count + effective * prior) / (n + effective)
                return np.where(n > 0, values, prior)

            def exact_factor(self, a, b, target):
                if b == self.begin:
                    prior = F(0) if target == self.n else (self.starts[target] + 20 * F(2 * self.uni[target] + 1, 2 * self.tokens + self.n)) / (self.record_count + 20)
                else:
                    destination = F(2 * (self.record_count if target == self.n else self.uni[target]) + 1,
                                    2 * self.tokens + self.n + 2 * self.record_count + 1)
                    prior = (self.edges[b, target] + 20 * destination) / (self.uni[b] + 20)
                n = self.contexts[a, b]
                if self.kappa is None or n == 0:
                    return prior
                q2 = (self.triples[a, b, target] + self.alpha * prior) / (n + self.alpha)
                mixture = F(n, n + self.kappa) * q2 + F(self.kappa, n + self.kappa) * prior
                effective = self.alpha + self.kappa + F(self.alpha * self.kappa, n)
                assert mixture == (self.triples[a, b, target] + effective * prior) / (n + effective)
                return mixture

            def local(self, row, slot):
                if self.kappa is not None:
                    return self.distribution(row, slot)
                values = [self.index.get(x, self.index[base.UNKNOWN]) for x in row["seq"]]
                mass = self.first.copy() if slot == 0 else self.trans[values[slot - 1], :self.n].copy()
                following = values[slot + 1] if slot + 1 < len(values) else self.n
                mass *= self.trans[:, following]
                return mass / mass.sum()

        rows, _ = base.load_records(ROOT / "data/normalized/lipi_clean_rtl_singleline.jsonl", min_length=3, unique=True)
        groups = base.group_records(rows)
        assignment, loads = base.make_folds(rows, groups, 5, 20261006)
        lookup = {rows[i]["record_id"]: g for g, indices in enumerate(groups) for i in indices}
        saved = base.read_jsonl(FOLDER / "main/adaptive_slot_audit.jsonl")
        queries = {(row["record_id"], row["slot"]): row for row in saved}
        assert len(saved) == len(queries) == 8009 and len(rows) == 1596 and len(groups) == 1526
        assert loads == state["correspondence"]["fold_token_loads"]
        max_mass = max_loss = max_complete = max_equivalence = 0.0
        witnesses, checked, contexts_checked, coefficient_checks = [], 0, 0, 0
        for fold_record in state["folds"]:
            fold = fold_record["fold"]
            train = [row for i, row in enumerate(rows) if assignment[i] != fold]
            test = [row for i, row in enumerate(rows) if assignment[i] == fold]
            assert not {r["record_id"] for r in train}.intersection(r["record_id"] for r in test)
            inner_groups = base.group_records(train)
            inner_assignment, inner_loads = base.make_folds(train, inner_groups, 3, 20261006 + fold)
            assert inner_loads == fold_record["inner"]["fold_token_loads"]
            candidates = fold_record["inner"]["candidates"]
            chosen = min(main.PARAMS, key=lambda pair: (candidates[main.label(pair)]["bucket_loss_bits"],
                            -float("inf") if pair[1] is None else -pair[1], -float("inf") if pair[0] is None else -pair[0]))
            assert chosen == (fold_record["chosen_alpha"], fold_record["chosen_kappa"])
            for part in range(3):
                count = fold_record["inner"]["split_sizes"][part]
                assert count["test_strings"] == sum(inner_assignment[i] == part for i in range(len(train)))
                assert count["test_slots"] == sum(len(r["seq"]) for i, r in enumerate(train) if inner_assignment[i] == part)
            model = Direct(train, *chosen)
            probe = main.Restorer(train, 20, 100)
            proof_model = Direct(train, 20, 100)
            assert dict(probe.history_counts) == dict(proof_model.contexts)
            for a, b in probe.history_counts:
                expected = proof_model.factor(np.full(proof_model.n + 1, a), np.full(proof_model.n + 1, b), np.arange(proof_model.n + 1))
                max_equivalence = max(max_equivalence, float(np.max(np.abs(expected - probe.probability(a, b)))))
                contexts_checked += 1
            for n in set(proof_model.contexts.values()):
                for alpha, kappa in main.PARAMS[:-1]:
                    effective = alpha + kappa + F(alpha * kappa, n)
                    assert F(n, n + effective) == F(n*n, (n + alpha) * (n + kappa))
                    coefficient_checks += 1
            for row in test:
                for slot, actual in enumerate(row["seq"]):
                    old = queries[row["record_id"], slot]
                    p = model.local(row, slot)
                    full = model.distribution(row, slot)
                    max_complete = max(max_complete, float(np.max(np.abs(full - p))))
                    ranking = np.argsort(-p, kind="stable")
                    predicted = [model.signs[i] for i in ranking]
                    for rank in range(10):
                        reported = old["suggestions"][rank]["code"]
                        if reported != predicted[rank]:
                            first = model.exact_likelihood(row, slot, reported)
                            second = model.exact_likelihood(row, slot, predicted[rank])
                            assert first == second
                            witnesses.append({"record_id": row["record_id"], "slot": slot, "rank": rank,
                                              "reported_code": reported, "independent_code": predicted[rank], "equal_exact_likelihood": str(first)})
                        max_mass = max(max_mass, abs(old["suggestions"][rank]["model_mass"] - float(p[model.index[reported]])))
                    assert old["top1"] == (predicted[0] == actual)
                    assert old["top5"] == (actual in predicted[:5]) and old["top10"] == (actual in predicted[:10])
                    assert old["actual"] == actual and old["fold"] == fold and old["group"] == lookup[row["record_id"]]
                    assert old["length"] == len(row["seq"]) and old["known_in_training"] == (actual in model.index)
                    actual_index = model.index.get(actual, model.index[base.UNKNOWN])
                    max_loss = max(max_loss, abs(-np.log2(p[actual_index]) - old["bucket_loss_bits"]))
                    hidden = dict(row, seq=list(row["seq"]))
                    hidden["seq"][slot] = "HIDDEN_REPLACEMENT"
                    assert np.array_equal(p, model.local(hidden, slot))
                    checked += 1
            print(json.dumps({"stage": "adaptive_review", "fold": fold, "queries": checked, "elapsed_seconds": time.monotonic() - started}), flush=True)
        assert checked == 8009 and max_mass < 1e-12 and max_loss < 1e-10 and max_complete < 1e-12 and max_equivalence < 1e-12
        assert base.summarize(saved) == state["models"]["adaptive"]
        comparators = {"M1": ROOT / "experiments/2026-10-02-six-hour/markov-baseline/main/markov_slot_audit.jsonl",
                       "M2_top1_selected": ROOT / "experiments/2026-10-02-six-hour/markov-order2/main/markov2_slot_audit.jsonl",
                       "PMB": ROOT / "results/restoration/local_slot_audit.jsonl"}
        for name, path in comparators.items():
            comparator = base.read_jsonl(path)
            assert base.summarize(comparator) == state["models"][name]
            assert base.paired(comparator, saved, 10000, seed=23102) == state["paired"][name]
        result = {"status": "pass", "queries_independently_reconstructed": checked, "strings": len(rows), "components": len(groups),
                  "flat_history_contexts_checked": contexts_checked, "rational_effective_strength_coefficients_checked": coefficient_checks,
                  "max_candidate_mass_error": max_mass, "max_loss_error_bits": float(max_loss), "max_full_chain_conditional_error": max_complete,
                  "max_effective_strength_factor_error": max_equivalence, "exact_rational_tie_witnesses": len(witnesses),
                  "input_results_sha256": sha(FOLDER / "main/results.json"), "audit_source_sha256": sha(__file__),
                  "elapsed_seconds": time.monotonic() - started,
                  "checks": ["all_query_group_fold_identity", "inner_allocations_and_selected_criterion", "independent_flat_counts",
                             "effective_strength_equivalence", "all_conditional_factors_and_complete_record_likelihoods", "all_exact_topk_outcomes",
                             "all_target_losses_and_candidate_masses", "hidden_target_invariance", "aggregates_and_paired_component_intervals"]}
        (output / "verification.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        (output / "tie_slot_audit.jsonl").write_text("\n".join(json.dumps(row) for row in witnesses) + "\n", encoding="utf-8")
        print(json.dumps(result, indent=2))
    except Exception as error:
        (output / "failure.json").write_text(json.dumps({"exception": type(error).__name__, "message": str(error)}, indent=2) + "\n", encoding="utf-8")
        raise


if __name__ == "__main__":
    run()
