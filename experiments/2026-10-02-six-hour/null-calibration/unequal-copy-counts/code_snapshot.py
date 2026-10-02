"""Finite weighted-copy conditional spaces and integer continuation sampling."""
from collections import Counter
from fractions import Fraction
from functools import lru_cache
import hashlib
import itertools
import json
from pathlib import Path
import random
import shutil
import time

from scipy.stats import chi2

HERE = Path(__file__).parent
WEIGHTS = (1, 1, 1, 2, 2, 3)
LATENT_ONES = 3
RECORD_ONES = 5
SAMPLES = 100000


@lru_cache(None)
def continuations(index, latent, expanded):
    if latent < 0 or expanded < 0:
        return 0
    if index == len(WEIGHTS):
        return int(latent == 0 and expanded == 0)
    return (continuations(index + 1, latent, expanded)
            + continuations(index + 1, latent - 1, expanded - WEIGHTS[index]))


def draw_column(rng):
    latent, expanded = LATENT_ONES, RECORD_ONES
    assignment = []
    for index, weight in enumerate(WEIGHTS):
        zero = continuations(index + 1, latent, expanded)
        one = continuations(index + 1, latent - 1, expanded - weight)
        assert zero + one > 0
        sign = int(rng.randrange(zero + one) >= zero)
        assignment.append(sign)
        latent -= sign
        expanded -= sign * weight
    assert latent == expanded == 0
    return tuple(assignment)


def path_probability(assignment):
    latent, expanded, probability = LATENT_ONES, RECORD_ONES, Fraction(1)
    for index, (weight, sign) in enumerate(zip(WEIGHTS, assignment)):
        total = continuations(index, latent, expanded)
        next_latent, next_expanded = latent - sign, expanded - sign * weight
        probability *= Fraction(continuations(index + 1, next_latent, next_expanded), total)
        latent, expanded = next_latent, next_expanded
    assert latent == expanded == 0
    return probability


def diagnostic(counts, tables):
    expected = SAMPLES / len(tables)
    statistic = sum((counts[table] - expected) ** 2 / expected for table in tables)
    return {"samples": SAMPLES, "all_tables_observed": all(counts[table] for table in tables),
            "minimum_count": min(counts.values()), "maximum_count": max(counts.values()),
            "chi_square": statistic, "degrees_of_freedom": len(tables) - 1,
            "diagnostic_p": float(chi2.sf(statistic, len(tables) - 1))}


def main():
    destination = HERE / "results.json"
    if destination.exists():
        raise FileExistsError("Frozen weighted-copy endpoint already exists")
    start = time.perf_counter()
    assignments = list(itertools.product((0, 1), repeat=len(WEIGHTS)))
    weighted_only = [column for column in assignments if sum(w * s for w, s in zip(WEIGHTS, column)) == RECORD_ONES]
    legal = [column for column in weighted_only if sum(column) == LATENT_ONES]
    assert len(legal) == continuations(0, LATENT_ONES, RECORD_ONES) == 6
    probabilities = {column: path_probability(column) for column in legal}
    assert set(probabilities.values()) == {Fraction(1, 6)}
    class_counts = Counter(weight for weight, sign in zip(WEIGHTS, legal[0]) if sign)
    class_space = [column for column in legal if Counter(weight for weight, sign in zip(WEIGHTS, column) if sign) == class_counts]
    assert len(class_space) == 3
    p = Fraction(1, 5)
    weights = {column: p ** sum(column) * (1 - p) ** (len(column) - sum(column)) for column in weighted_only}
    normalization = sum(weights.values())
    tables = list(itertools.product(legal, repeat=3))
    assert len(tables) == 216
    direct_rng, rejection_rng = random.Random(2026100201), random.Random(2026100202)
    direct = Counter(tuple(draw_column(direct_rng) for _ in range(3)) for _ in range(SAMPLES))
    rejection, proposals = Counter(), 0
    for _ in range(SAMPLES):
        columns = []
        for _ in range(3):
            while True:
                proposed = [0, 0, 0, 1, 1, 1]
                rejection_rng.shuffle(proposed)
                proposals += 1
                if sum(w * s for w, s in zip(WEIGHTS, proposed)) == RECORD_ONES:
                    columns.append(tuple(proposed))
                    break
        rejection[tuple(columns)] += 1
    assert set(direct) == set(rejection) == set(tables)
    for counts in [direct, rejection]:
        assert sum(counts.values()) == SAMPLES
        for table in counts:
            for column in table:
                assert sum(column) == LATENT_ONES
                assert sum(w * s for w, s in zip(WEIGHTS, column)) == RECORD_ONES
    source = Path(__file__)
    shutil.copyfile(source, HERE / "code_snapshot.py")
    result = {
        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "weights": WEIGHTS, "latent_ones": LATENT_ONES, "record_ones": RECORD_ONES,
        "latent_margin_only_columns": 20, "weighted_margin_only_columns": len(weighted_only),
        "both_margin_columns": len(legal), "both_margin_three_column_tables": len(tables),
        "within_weight_class_columns": len(class_space), "within_weight_class_three_column_tables": len(class_space) ** 3,
        "unrestricted_column_acceptance_exact": .3, "unrestricted_whole_table_acceptance_exact": .027,
        "direct_seed": 2026100201, "rejection_seed": 2026100202,
        "direct_sampling": diagnostic(direct, tables), "column_rejection_sampling": diagnostic(rejection, tables),
        "column_proposals": proposals, "accepted_columns": 3 * SAMPLES,
        "column_acceptance_observed": 3 * SAMPLES / proposals,
        "legal_columns": [{"column": column, "dp_path_probability": str(probabilities[column]),
                           "within_weight_class_space": column in class_space} for column in legal],
        "weighted_margin_only_known_p_law": [{"column": column, "latent_ones": sum(column),
                                             "probability": str(weights[column] / normalization)} for column in weighted_only],
        "tables": [{"columns": table, "direct_count": direct[table], "rejection_count": rejection[table]} for table in tables],
        "elapsed_seconds": time.perf_counter() - start,
        "checks": ["complete_enumeration", "integer_continuation_counts", "exact_path_probabilities",
                   "conditional_known_probability", "latent_margins", "expanded_record_margins", "draw_counts"]}
    destination.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key not in ["tables", "legal_columns", "weighted_margin_only_known_p_law"]}), flush=True)


if __name__ == "__main__":
    main()
