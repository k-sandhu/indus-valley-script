"""Exact integer-score tail laws for independently generated copied strings."""
from collections import Counter
from fractions import Fraction
import hashlib
import itertools
import json
import math
from pathlib import Path
import shutil

HERE = Path(__file__).parent


def statistic(columns):
    return sum(left == center for left, center in zip(columns[0], columns[1])) + sum(center == right for center, right in zip(columns[1], columns[2]))


def margins_space(n):
    return [tuple(int(row in ones) for row in range(n)) for ones in itertools.combinations(range(n), n // 2)]


def counted_record_distribution(n):
    arrangements = [math.comb(n // 2, swaps) ** 2 for swaps in range(n // 2 + 1)]
    assert sum(arrangements) == math.comb(n, n // 2)
    counts = Counter()
    for left, left_count in enumerate(arrangements):
        for right, right_count in enumerate(arrangements):
            counts[2 * n - 2 * (left + right)] += left_count * right_count
    assert sum(counts.values()) == math.comb(n, n // 2) ** 2
    return counts


def tail(counts, observed):
    return Fraction(sum(count for score, count in counts.items() if score >= observed), sum(counts.values()))


def main():
    destination = HERE / "results.json"
    if destination.exists():
        raise FileExistsError("Frozen copy-tail endpoint already exists")
    columns = margins_space(4)
    tables = list(itertools.product(columns, repeat=3))
    latent_counts = Counter(statistic(table) for table in tables)
    assert len(tables) == sum(latent_counts.values()) == 216
    results = []
    for copies in range(1, 6):
        n = 4 * copies
        record_counts = counted_record_distribution(n)
        matched_counts = Counter({score * copies: count for score, count in latent_counts.items()})
        if copies <= 2:
            ordinary_columns = margins_space(n)
            enumerated = Counter(statistic(table) for table in itertools.product(ordinary_columns, repeat=3))
            assert all(enumerated[score] == count * len(ordinary_columns) for score, count in record_counts.items())
            assert set(enumerated) == set(record_counts)
        references = {}
        for name, counts in [("record_columns", record_counts), ("block_columns", matched_counts)]:
            tails = {score: tail(counts, score) for score in matched_counts}
            rejection = {}
            for threshold in [Fraction(1, 100), Fraction(1, 20), Fraction(1, 10)]:
                rejected = sum(count for score, count in matched_counts.items() if tails[score] <= threshold)
                rejection[str(float(threshold))] = {"rejected_latent_tables": rejected, "total_latent_tables": 216,
                                                   "probability_exact": str(Fraction(rejected, 216)), "probability": rejected / 216}
            references[name] = {"tails_at_observed_scores": {str(score): str(value) for score, value in sorted(tails.items())},
                                "rejection": rejection}
        results.append({"copies": copies, "records": n, "latent_distribution": dict(sorted(matched_counts.items())),
                        "record_distribution_for_fixed_middle_column": dict(sorted(record_counts.items())),
                        "record_table_count": math.comb(n, n // 2) ** 3,
                        "references": references})
    source = Path(__file__)
    shutil.copyfile(source, HERE / "code_snapshot.py")
    output = {"source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(), "latent_tables": 216,
              "latent_integer_distribution": dict(sorted(latent_counts.items())), "copies": results,
              "checks": ["latent_space_enumeration", "neighbor_arrangement_count", "integer_convolution",
                         "ordinary_space_enumeration_copies_1_and_2", "exact_fraction_tails", "exact_rejection_counts"]}
    destination.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"checks": output["checks"], "rejection_rates": [{"copies": entry["copies"],
          **{name: {alpha: rate["probability"] for alpha, rate in reference["rejection"].items()}
             for name, reference in entry["references"].items()}} for entry in results]}))


if __name__ == "__main__":
    main()
