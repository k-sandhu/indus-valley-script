"""Independent finite-space and random-stream replay of weighted-copy sampling."""
from collections import Counter
from fractions import Fraction
import hashlib
import itertools
import json
from pathlib import Path
import random

HERE = Path(__file__).parent


def main():
    result = json.loads((HERE / "results.json").read_text(encoding="utf-8"))
    weights = result["weights"]
    legal = [values for values in itertools.product([0, 1], repeat=6)
             if sum(values) == 3 and sum(a * b for a, b in zip(weights, values)) == 5]
    permutations = Counter(itertools.permutations([0, 0, 0, 1, 1, 1]))
    assert len(permutations) == 20 and set(permutations.values()) == {36}
    assert sum(permutations[column] for column in legal) == 216
    assert Fraction(216, 720) == Fraction(3, 10)
    assert Fraction(216, 720) ** 3 == Fraction(27, 1000)
    assert set(tuple(row["column"]) for row in result["legal_columns"]) == set(legal)
    for column in legal:
        probability = Fraction(1)
        for position in range(6):
            current = [candidate for candidate in legal if candidate[:position] == column[:position]]
            chosen = [candidate for candidate in current if candidate[position] == column[position]]
            probability *= Fraction(len(chosen), len(current))
        assert probability == Fraction(1, 6)
    # Replay using enumeration of compatible prefixes, independent of the recurrence.
    rng = random.Random(result["direct_seed"])
    direct_counts = Counter()
    for _ in range(100000):
        columns = []
        for _ in range(3):
            prefix = ()
            for position in range(6):
                current = [candidate for candidate in legal if candidate[:position] == prefix]
                zero_count = sum(candidate[position] == 0 for candidate in current)
                prefix += (int(rng.randrange(len(current)) >= zero_count),)
            columns.append(prefix)
        direct_counts[tuple(columns)] += 1
    tables = {tuple(tuple(column) for column in row["columns"]): row for row in result["tables"]}
    assert len(tables) == 216 and set(tables) == set(itertools.product(legal, repeat=3))
    assert all(row["direct_count"] == direct_counts[table] for table, row in tables.items())
    known_p = Fraction(1, 5)
    weighted_only = [column for column in itertools.product([0, 1], repeat=6)
                     if sum(a * b for a, b in zip(weights, column)) == 5]
    probabilities = {column: known_p ** sum(column) * (1 - known_p) ** (6 - sum(column))
                     for column in weighted_only}
    total = sum(probabilities.values())
    assert len(probabilities) == 10
    assert all(Fraction(row["probability"]) == probabilities[tuple(row["column"])] / total
               for row in result["weighted_margin_only_known_p_law"])
    assert sum(Fraction(row["probability"]) for row in result["weighted_margin_only_known_p_law"]) == 1
    for sampler in ["direct_sampling", "column_rejection_sampling"]:
        field = "direct_count" if sampler == "direct_sampling" else "rejection_count"
        counts = [row[field] for row in tables.values()]
        expected = sum(counts) / len(counts)
        statistic = sum((count - expected) ** 2 / expected for count in counts)
        assert sum(counts) == 100000
        assert abs(statistic - result[sampler]["chi_square"]) < 1e-9
    for source in [HERE / "run.py", HERE / "code_snapshot.py"]:
        assert hashlib.sha256(source.read_bytes()).hexdigest() == result["source_sha256"]
    verification = {"status": "pass", "columns": 6, "tables": 216,
                    "independent_direct_stream_tables_replayed": 100000,
                    "source_sha256": result["source_sha256"],
                    "checks": ["labeled_permutation_multiplicity", "exact_prefix_branch_probability",
                               "weighted_only_known_p_law", "full_direct_stream_replay",
                               "table_margins", "stored_uniformity_diagnostics", "source_correspondence"]}
    destination = HERE / "verification.json"
    if destination.exists():
        raise FileExistsError("Verification already exists")
    destination.write_text(json.dumps(verification, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(verification))


if __name__ == "__main__":
    main()
