"""Independent finite formulas for the hypothetical external-anchor example."""
import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent


def entropy(ps):
    return -sum(p * math.log2(p) for p in ps if p)


def main(out_name):
    source = HERE.parent / "anchors-v1/results.json"
    saved = json.loads(source.read_text(encoding="utf-8"))
    checks = []
    def add(name, passed, **details):
        checks.append({"check": name, "pass": bool(passed), **details})
    for row in saved["rows"]:
        error = row["assumed_symmetric_error"]
        channel = 1 - entropy([error, 1-error])
        add("balanced binary partition information formula", abs(row["one_validated_partition"]["expected_information_bits"]-channel) < 1e-12, error=error)
        add("distinct independent partition information formula", abs(row["two_distinct_independent_partitions"]["expected_information_bits"]-2*channel) < 1e-12, error=error)
        expected = 0.
        for a, b in itertools.product([0, 1], repeat=2):
            mass = [.5*((1-error) if bit == a else error)*((1-error) if bit == b else error) for bit in [0, 1]]
            probability = sum(mass)
            if probability:
                expected += probability * entropy([p/probability for p in mass])
        add("independent repeated-partition entropy formula", abs(row["two_independent_witnesses_for_same_partition"]["expected_remaining_entropy_bits"]-(1+expected)) < 1e-12, error=error)
        add("shared copies supply no additional information", row["two_copies_of_one_witness"] == row["one_validated_partition"], error=error)
        naive = error**2 / (error**2+(1-error)**2)
        add("copied-witness nominal and actual error separated", abs(row["copy_treated_as_independent_nominal_wrong_bit_probability"]-naive) < 1e-12 and row["actual_wrong_bit_probability_after_a_copied_answer"] == error, error=error)
    add("anchor code hash matches current source", saved["code_sha256"] == hashlib.sha256((HERE.parent / "contextual_anchors.py").read_bytes()).hexdigest())
    result = {"status": "independent exact formula audit of synthetic anchors", "checks": checks,
              "passed": sum(row["pass"] for row in checks), "failed": sum(not row["pass"] for row in checks),
              "scope": "The source partitions and error model are assumed. This verifies the mathematical calculation and contains zero archaeological observations.",
              "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest()}
    output = HERE / out_name
    if output.exists():
        raise FileExistsError("Preserve the earlier review endpoint and choose a fresh --out file")
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": result["passed"], "failed": result["failed"]}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="anchor-checks-recheck.json")
    main(parser.parse_args().out)
