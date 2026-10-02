"""Replay exact quality-mixture moments by summing latent sign pairs."""
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "knowledge").is_dir())
FOLDER = ROOT / "experiments/2026-10-02-six-hour/null-calibration/shared-quality/analytic-moments"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run():
    destination = FOLDER / "verification.json"
    if destination.exists():
        raise FileExistsError("Refusing an existing analytic moment audit")
    state = json.loads((FOLDER / "results.json").read_text())
    entries = json.loads((FOLDER / "single_face_entries.json").read_text())
    assert sha(FOLDER / "code_snapshot.py") == state["source_sha256"] and sha(FOLDER / "single_face_entries.json") == state["single_face_entries_sha256"]
    base = [F(x, 100) for x in [20, 16, 14, 12, 11, 10, 9, 8]]
    rates = [F(1, 40), F(3, 5)]
    def p(site, slot):
        return [base[(x - site - 2 * slot) % 8] for x in range(8)]
    def k(y, x, rate):
        return 1 - rate if y == x else rate / 7
    for entry in entries:
        site, slot, a, b = [entry[key] for key in ["site", "left_slot", "left_sign", "right_sign"]]
        left, right = p(site, slot), p(site, slot + 1)
        joint = sum(left[x] * right[y] * k(a, x, rate) * k(b, y, rate) / 2 for rate in rates for x in range(8) for y in range(8))
        ma = sum(left[x] * k(a, x, rate) / 2 for rate in rates for x in range(8))
        mb = sum(right[y] * k(b, y, rate) / 2 for rate in rates for y in range(8))
        assert joint == F(entry["joint_probability"]) and joint - ma * mb == F(entry["covariance"])
    maximum = max(abs(F(entry["covariance"])) for entry in entries)
    assert maximum == F(state["single_face_maximum_absolute_covariance"]) == F(4761, 7840000)
    vector_witnesses = 0
    for case in state["vector_maximum"]:
        left, right = p(case["site"], case["left_slot"]), p(case["site"], case["left_slot"] + 1)
        for witness in case["witnesses"]:
            a, b = witness["left_vector"]
            c, d = witness["right_vector"]
            joint = sum(left[x] * right[y] * k(a, x, rate) * k(b, x, rate) * k(c, y, rate) * k(d, y, rate) / 2
                        for rate in rates for x in range(8) for y in range(8))
            ma = sum(left[x] * k(a, x, rate) * k(b, x, rate) / 2 for rate in rates for x in range(8))
            mb = sum(right[y] * k(c, y, rate) * k(d, y, rate) / 2 for rate in rates for y in range(8))
            assert joint == F(witness["joint_probability"]) and joint - ma * mb == F(witness["covariance"])
            assert abs(joint - ma * mb) == F(case["largest_absolute_covariance"])
            vector_witnesses += 1
    assert state["class_agreement"] == [str(sum(k(y, 0, rate)**2 for y in range(8))) for rate in rates]
    result = {"status": "pass", "single_face_entries_by_latent_pair_sum": len(entries),
              "maximum_vector_witnesses_by_latent_pair_sum": vector_witnesses,
              "input_results_sha256": sha(FOLDER / "results.json"), "audit_source_sha256": sha(__file__),
              "checks": ["saved_entry_correspondence", "independent_latent_pair_sums", "single_face_covariance", "vector_maximum_witnesses", "class_agreement"]}
    destination.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result))


if __name__ == "__main__":
    run()
