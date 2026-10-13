"""Independent scalar/count audit of the two post-outcome backoff mixtures.

Reads local-only probabilities; writes only aggregate comparisons. No author
code is imported. Positional probabilities are rebuilt from training counts.
"""
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path
import random

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PACKAGE = HERE.parent / "grammar"
RAW = ROOT / "data/raw/2026-10-11-two-approaches/grammar"
WEIGHTS = (0, .05, .1, .2, .3, .5, .75, 1.)
UNKNOWN = "__UNKNOWN__"


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def lines(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def hash_file(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def mixed(a, b, w):
    return [math.log2((1-w) * 2**x + w * 2**y) for x, y in zip(a, b)]


def grouped_folds(rows, seed):
    members = defaultdict(list)
    for i, row in enumerate(rows):
        members[row["group"]].append(i)
    group_order = list(members)
    random.Random(seed).shuffle(group_order)
    group_order.sort(key=lambda g: -sum(len(rows[i]["seq"]) for i in members[g]))
    assignment, load = {}, [0, 0, 0]
    for group in group_order:
        fold = min(range(3), key=lambda f: (load[f], f))
        for i in members[group]:
            assignment[i] = fold
            load[fold] += len(rows[i]["seq"])
    return assignment


def position_model(rows, alpha):
    known = {s for row in rows for s in row["seq"]}
    counts = Counter(s for row in rows for s in row["seq"])
    total = sum(counts.values()) + .5 * (len(known) + 1)
    prior = {s: (counts[s] + .5) / total for s in known | {UNKNOWN}}
    cells = defaultdict(Counter)
    for row in rows:
        for j, sign in enumerate(row["seq"]):
            cells[(len(row["seq"]), j)][sign] += 1
    def score(seq):
        result = []
        for j, sign in enumerate(seq):
            mapped = sign if sign in known else UNKNOWN
            cell = cells[(len(seq), j)]
            probability = (cell[mapped] + alpha * prior[mapped]) / (sum(cell.values()) + alpha)
            result.append(math.log2(probability))
        return result
    return score


def main():
    primary = read(PACKAGE / "run-v1/results.json")
    class_result = read(PACKAGE / "run-v2-mixture/results.json")
    matched_result = read(PACKAGE / "run-v3-matched-mixtures/results.json")
    rows = lines(RAW / "run-v1/fold-assignment.jsonl")
    checks, fold_results = [], []
    def check(name, passed, **details):
        checks.append({"check": name, "pass": bool(passed), **details})
    check("v2 input hash equals frozen v1", class_result["census"]["raw_input_sha256"] == primary["manifest"]["input_sha256"])
    check("v2 preserves v1 result hash", class_result["primary_results_sha256"] == hash_file(PACKAGE / "run-v1/results.json"))
    check("v3 preserves v1 and v2 result hashes", matched_result["primary_result_sha256"] == hash_file(PACKAGE / "run-v1/results.json") and matched_result["preserved_class_mixture_result_sha256"] == hash_file(PACKAGE / "run-v2-mixture/results.json"))
    all_scores = Counter()
    oov_scores = Counter()
    known_scores = Counter()
    tokens, texts, oov = 0, 0, 0
    seen_ids = set()
    max_outer_error = 0.
    for fold in range(5):
        training = [row for row in rows if row["fold"] != fold]
        test_rows = [row for row in rows if row["fold"] == fold]
        inner = grouped_folds(training, primary["manifest"]["seed"] + fold)
        expected = {(row["record_id"], inner[i]): row for i, row in enumerate(training)}
        selected = read(PACKAGE / f"run-v1/fold-{fold}-selection.json")
        saved_inner = lines(RAW / f"run-v2-mixture/fold-{fold}-inner-predictions.jsonl")
        keys = [(row["record_id"], row["inner"]) for row in saved_inner]
        check("v2 inner targets are precisely original outer-training validation rows", len(keys) == len(set(keys)) == len(expected) and set(keys) == set(expected), fold=fold)
        local_scores = {"class": Counter(), "position": Counter()}
        positional_total = 0.
        for subfold in range(3):
            fit = [row for i, row in enumerate(training) if inner[i] != subfold]
            validation_groups = {row["group"] for i, row in enumerate(training) if inner[i] == subfold}
            check("mixture inner physical/text components are disjoint", not (validation_groups & {row["group"] for row in fit}), fold=fold, inner=subfold)
            position_score = position_model(fit, selected["selected"]["POSITION"])
            for row in saved_inner:
                if row["inner"] != subfold:
                    continue
                original = expected[(row["record_id"], subfold)]
                assert row["group"] == original["group"]
                first, second = row["MARKOV_log2"], row["GRAMMAR_log2"]
                pos = position_score(original["seq"])
                assert len(first) == len(second) == len(pos) == len(original["seq"])
                positional_total += sum(pos)
                for w in WEIGHTS:
                    local_scores["class"][w] += sum(mixed(first, second, w))
                    local_scores["position"][w] += sum(mixed(first, pos, w))
        class_fold = class_result["folds"][fold]
        matched_fold = matched_result["folds"][fold]
        chosen = {name: max(WEIGHTS, key=lambda w: local_scores[name][w]) for name in local_scores}
        n_validation = selected["validation_tokens"]
        expected_position_total = -selected["inner_cross_entropy_bits"]["POSITION"][str(selected["selected"]["POSITION"])] * n_validation
        check("independent training-count position score equals v1 validation score", abs(positional_total - expected_position_total) < 1e-7, fold=fold, error_bits=abs(positional_total - expected_position_total))
        for family, saved in (("class", class_fold["inner_cross_entropy_bits"]), ("position", matched_fold["position_inner_cross_entropy_bits"])):
            max_error = max(abs(-local_scores[family][w] / n_validation - saved[str(w)]) for w in WEIGHTS)
            check("independent full weight grid reproduces inner losses", max_error < 1e-10, fold=fold, family=family, maximum_error_bits_per_token=max_error)
        check("both weights maximize training-only inner likelihood", chosen["class"] == class_fold["selected_grammar_weight"] == matched_fold["class_grammar_weight"] and chosen["position"] == matched_fold["position_weight"], fold=fold, chosen=chosen)
        primary_predictions = lines(RAW / f"run-v1/fold-{fold}-predictions.jsonl")
        class_predictions = lines(RAW / f"run-v2-mixture/fold-{fold}-predictions.jsonl")
        check("outer witnesses cover precisely held-out row identities", len(primary_predictions) == len(class_predictions) == len(test_rows) and {row["record_id"] for row in primary_predictions} == {row["record_id"] for row in test_rows}, fold=fold)
        local_sum = Counter()
        fold_tokens = 0
        for original, saved in zip(primary_predictions, class_predictions):
            assert original["record_id"] == saved["record_id"]
            assert original["record_id"] not in seen_ids
            seen_ids.add(original["record_id"])
            scores = original["log2_probabilities"]
            class_mix = mixed(scores["MARKOV"], scores["GRAMMAR"], chosen["class"])
            position_mix = mixed(scores["MARKOV"], scores["POSITION"], chosen["position"])
            max_outer_error = max(max_outer_error, max(abs(a-b) for a, b in zip(class_mix, saved["log2_probabilities"]["GRAMMAR"])))
            combined = {"MARKOV": scores["MARKOV"], "CLASS_MIXTURE": class_mix, "POSITION_MIXTURE": position_mix}
            length = len(original["sequence"])
            fold_tokens += length
            tokens += length
            texts += 1
            for name, values in combined.items():
                local_sum[name] += sum(values)
                all_scores[name] += sum(values)
                for value, known in zip(values, original["in_training_alphabet"]):
                    (known_scores if known else oov_scores)[name] += value
            oov += sum(not known for known in original["in_training_alphabet"])
        increment = (local_sum["CLASS_MIXTURE"] - local_sum["POSITION_MIXTURE"]) / fold_tokens
        check("independent outer fold class increment reproduces v3", abs(increment - matched_fold["class_minus_position_mixture_bits_per_token"]) < 1e-10, fold=fold, increment_bits_per_token=increment)
        fold_results.append({"fold": fold, "weights": chosen, "tokens": fold_tokens,
                             "class_minus_position_mixture_bits_per_token": increment})
    check("v2 outer convex mixtures match each frozen target probability", max_outer_error < 1e-12, maximum_error_bits=max_outer_error)
    cross_entropy = {name: -value / tokens for name, value in all_scores.items()}
    expected_entropies = {"MARKOV": matched_result["class_mixture_vs_markov"]["cross_entropy_bits_per_token"]["MARKOV"],
                          "CLASS_MIXTURE": matched_result["class_mixture_vs_markov"]["cross_entropy_bits_per_token"]["GRAMMAR"],
                          "POSITION_MIXTURE": matched_result["position_mixture_vs_markov"]["cross_entropy_bits_per_token"]["GRAMMAR"]}
    check("independent all-token aggregate scores match v3", max(abs(cross_entropy[k] - expected_entropies[k]) for k in cross_entropy) < 1e-10, cross_entropy_bits_per_token=cross_entropy)
    check("same 1596 texts and 8009 target events scored", texts == 1596 and tokens == 8009 and oov == 257, texts=texts, tokens=tokens, OOV_events=oov)
    # A normalized model on {known,UNKNOWN} is not a distribution on an unlimited
    # number of distinguishable unseen symbols if UNKNOWN mass is copied to each.
    mapped_probability = {"known": .8, "UNKNOWN": .2}
    expanded_sum = mapped_probability["known"] + 2 * mapped_probability["UNKNOWN"]
    check("OOV witness requires mapped-event probability semantics", abs(sum(mapped_probability.values()) - 1) < 1e-12 and expanded_sum > 1, hypothetical_two_distinct_OOV_mass_sum=expanded_sum)
    scope = {"observational_law": "entire prefix-generated sequence after fit-specific OOV collapse, conditional on observed length",
             "outer_model_search_status": "post-outcome; numerical weight selection uses outer training only, but the mixture family and matched comparison were motivated by exposed v1/v2 outcomes",
             "conditional_intervals": "component bootstrap conditions on fitted predictors and chosen folds; it does not include family-search or training-estimation uncertainty",
             "target_free_weight_selection": "one constant weight per fold selected with inner pooled likelihood; no per-target gate or target-defined stratum chooses it"}
    result = {"status": "independent count/scalar audit", "checks": checks,
              "passed": sum(row["pass"] for row in checks), "failed": sum(not row["pass"] for row in checks),
              "folds": fold_results, "scope": scope,
              "known_target_class_minus_position_increment": (known_scores["CLASS_MIXTURE"]-known_scores["POSITION_MIXTURE"]) / (tokens-oov),
              "OOV_target_class_minus_position_increment": (oov_scores["CLASS_MIXTURE"]-oov_scores["POSITION_MIXTURE"]) / oov,
              "class_minus_position_increment_bits_per_token": (all_scores["CLASS_MIXTURE"]-all_scores["POSITION_MIXTURE"]) / tokens,
              "inputs_sha256": {str(p.relative_to(ROOT)): hash_file(p) for p in (PACKAGE / "run-v1/results.json", PACKAGE / "run-v2-mixture/results.json", PACKAGE / "run-v3-matched-mixtures/results.json")}}
    output = HERE / "mixture-checks-v1.json"
    if output.exists():
        raise FileExistsError("Preserve completed reviewer output; choose a new version in the checker before rerunning")
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": result["passed"], "failed": result["failed"], "cross_entropy": cross_entropy,
                      "class_increment": result["class_minus_position_increment_bits_per_token"],
                      "known_target_increment": result["known_target_class_minus_position_increment"],
                      "OOV_increment": result["OOV_target_class_minus_position_increment"]}))


if __name__ == "__main__":
    main()
