"""Exact covariance available to single-face and ordered-vector observations."""
from fractions import Fraction as F
import hashlib
import itertools
import json
from pathlib import Path
import shutil

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "knowledge").is_dir())
FOLDER = ROOT / "experiments/2026-10-02-six-hour/null-calibration/shared-quality"
OUTPUT = FOLDER / "analytic-moments"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run():
    if OUTPUT.exists():
        raise FileExistsError("Refusing an existing analytic moment endpoint")
    OUTPUT.mkdir()
    shutil.copyfile(__file__, OUTPUT / "code_snapshot.py")
    e = [F(1, 40), F(3, 5)]
    t = [1 - 8 * rate / 7 for rate in e]
    variance = (t[0] - t[1])**2 / 4
    base = [F(v, 100) for v in [20, 16, 14, 12, 11, 10, 9, 8]]
    vectors = list(itertools.product(range(8), repeat=2))
    singles, vector_maximum, vector_checks = [], [], 0
    for site in range(2):
        p, marginal, paired = [], [], []
        for slot in range(3):
            shift = (site + 2 * slot) % 8
            latent = base[-shift:] + base[:-shift] if shift else base[:]
            p.append(latent)
            single, pair = [], []
            for rate in e:
                kernel = [[1 - rate if y == x else rate / 7 for y in range(8)] for x in range(8)]
                single.append([sum(latent[x] * kernel[x][y] for x in range(8)) for y in range(8)])
                pair.append({v: sum(latent[x] * kernel[x][v[0]] * kernel[x][v[1]] for x in range(8)) for v in vectors})
                assert sum(single[-1]) == sum(pair[-1].values()) == 1
                assert all(single[-1][y] == F(1, 8) + (1 - 8 * rate / 7) * (latent[y] - F(1, 8)) for y in range(8))
            marginal.append(single)
            paired.append(pair)
        for slot in range(2):
            for a, b in itertools.product(range(8), repeat=2):
                joint = sum(marginal[slot][q][a] * marginal[slot + 1][q][b] for q in range(2)) / 2
                mean_a = sum(marginal[slot][q][a] for q in range(2)) / 2
                mean_b = sum(marginal[slot + 1][q][b] for q in range(2)) / 2
                covariance = joint - mean_a * mean_b
                closed = variance * (p[slot][a] - F(1, 8)) * (p[slot + 1][b] - F(1, 8))
                assert covariance == closed
                singles.append({"site": site, "left_slot": slot, "left_sign": a, "right_sign": b,
                                "joint_probability": str(joint), "covariance": str(covariance)})
            total, witnesses, largest = F(0), [], F(-1)
            for left, right in itertools.product(vectors, repeat=2):
                joint = sum(paired[slot][q][left] * paired[slot + 1][q][right] for q in range(2)) / 2
                ma = sum(paired[slot][q][left] for q in range(2)) / 2
                mb = sum(paired[slot + 1][q][right] for q in range(2)) / 2
                covariance = joint - ma * mb
                independent = (paired[slot][0][left] - paired[slot][1][left]) * (paired[slot + 1][0][right] - paired[slot + 1][1][right]) / 4
                assert covariance == independent
                total += joint
                vector_checks += 1
                if abs(covariance) > largest:
                    largest, witnesses = abs(covariance), []
                if abs(covariance) == largest:
                    witnesses.append({"left_vector": left, "right_vector": right, "covariance": str(covariance), "joint_probability": str(joint)})
            assert total == 1
            vector_maximum.append({"site": site, "left_slot": slot, "largest_absolute_covariance": str(largest),
                                   "largest_absolute_covariance_float": float(largest), "witnesses": witnesses})
    largest_single = max(abs(F(row["covariance"])) for row in singles)
    result = {"status": "pass", "simulation": True, "source_sha256": sha(__file__),
              "protocol_sha256": sha(FOLDER / "ANALYTIC_PROTOCOL.md"), "single_face_entries_checked": len(singles),
              "vector_event_entries_checked": vector_checks, "attenuation_variance": str(variance),
              "class_agreement": [str((1 - rate)**2 + rate**2 / 7) for rate in e],
              "class_whole_string_agreement": [str(((1 - rate)**2 + rate**2 / 7)**3) for rate in e],
              "single_face_maximum_absolute_covariance": str(largest_single),
              "single_face_maximum_absolute_covariance_float": float(largest_single), "vector_maximum": vector_maximum}
    assert len(singles) == 256 and vector_checks == 16384
    (OUTPUT / "single_face_entries.json").write_text(json.dumps(singles, indent=2) + "\n", encoding="utf-8")
    result["single_face_entries_sha256"] = sha(OUTPUT / "single_face_entries.json")
    (OUTPUT / "results.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result))


if __name__ == "__main__":
    run()
