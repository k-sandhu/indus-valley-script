"""Independent row-state dynamic count of every saved ordinary reference law."""
from collections import Counter
from fractions import Fraction
import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).parent


def row_state_count(n):
    states = {(0, 0, 0): 1}
    for middle in [0] * (n // 2) + [1] * (n // 2):
        changed = Counter()
        for (left_ones, right_ones, score), count in states.items():
            for left, right in itertools.product([0, 1], repeat=2):
                next_left, next_right = left_ones + left, right_ones + right
                if next_left <= n // 2 and next_right <= n // 2:
                    changed[(next_left, next_right, score + (left == middle) + (right == middle))] += count
        states = changed
    return {score: count for (left, right, score), count in states.items() if left == right == n // 2}


def main():
    result = json.loads((HERE / "results.json").read_text(encoding="utf-8"))
    for source in [HERE / "run.py", HERE / "code_snapshot.py"]:
        assert hashlib.sha256(source.read_bytes()).hexdigest() == result["source_sha256"]
    latent = Counter({int(score): count for score, count in result["latent_integer_distribution"].items()})
    assert latent == Counter({0: 6, 2: 48, 4: 108, 6: 48, 8: 6})
    for entry in result["copies"]:
        record = row_state_count(entry["records"])
        assert record == {int(score): count for score, count in entry["record_distribution_for_fixed_middle_column"].items()}
        observed = {score * entry["copies"]: count for score, count in latent.items()}
        for name, reference in entry["references"].items():
            counts = record if name == "record_columns" else observed
            for score, value in reference["tails_at_observed_scores"].items():
                exact = Fraction(sum(count for candidate, count in counts.items() if candidate >= int(score)), sum(counts.values()))
                assert exact == Fraction(value)
            for threshold, endpoint in reference["rejection"].items():
                rejected = sum(count for score, count in observed.items()
                               if Fraction(reference["tails_at_observed_scores"][str(score)]) <= Fraction(threshold))
                assert rejected == endpoint["rejected_latent_tables"]
                assert Fraction(rejected, 216) == Fraction(endpoint["probability_exact"])
    verification = {"status": "pass", "copies_checked": 5, "reference_tails_checked": 50,
                    "rejection_endpoints_checked": 30,
                    "source_sha256": result["source_sha256"],
                    "checks": ["independent_row_state_counts", "exact_rational_tails", "rejection_counts", "source_correspondence"]}
    destination = HERE / "verification.json"
    if destination.exists():
        raise FileExistsError("Frozen verification already exists")
    destination.write_text(json.dumps(verification, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(verification))


if __name__ == "__main__":
    main()
