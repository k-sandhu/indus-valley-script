"""Independent allocation-law audit, retaining only aggregate reviewer output.

No author code is imported. Every saved pilot/tail allocation is checked for
its declared margins and prototype uniqueness. Direct exposure/collision
recounts use a fixed sample of allocations; the coordinator separately
recomputes complete reference statistics.
"""
from collections import Counter, defaultdict
import hashlib
from itertools import combinations
import json
import math
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PACKAGE = HERE.parent / "administrative"
RAW = ROOT / "data/raw/2026-10-11-two-approaches/administrative"


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def freeze(value):
    return tuple(freeze(x) for x in value) if isinstance(value, list) else value


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def exposures(assignment, witness):
    signs = witness["signs"]
    index = {s: i for i, s in enumerate(signs)}
    count = np.zeros(len(signs)**2, dtype=int)
    for slots in witness["ranges"]:
        for left_slot, right_slot in combinations(slots, 2):
            left = set(witness["modules"][int(assignment[left_slot])])
            right = set(witness["modules"][int(assignment[right_slot])])
            for a in left & set(signs):
                for b in right & set(signs):
                    i, j = sorted((index[a], index[b]))
                    count[i * len(signs) + j] += 1
    return count


def collisions(assignment, witness):
    bins = Counter((freeze(obj["cell"]), tuple(sorted(int(assignment[x]) for x in slots)))
                   for obj, slots in zip(witness["objects"], witness["ranges"]))
    return sum(n * (n - 1) // 2 for n in bins.values())


def main():
    checks, populations = [], []
    def check(name, passed, **details):
        checks.append({"check": name, "pass": bool(passed), **details})
    for endpoint, role in (("run-v1", False), ("role-control-v1", True)):
        summary = read(PACKAGE / endpoint / "summary.json")
        expected_tests = []
        for name in ("rtl-all", "rtl-prototypes", "mirror-all", "mirror-prototypes"):
            witness = read(RAW / endpoint / f"{name}-witness.json")
            result = read(PACKAGE / endpoint / f"{name}.json")
            saved = np.load(RAW / endpoint / f"{name}-references.npz")
            original = np.asarray(witness["original_assignment"], int)
            objects, modules = witness["objects"], witness["modules"]
            ranges = witness["ranges"]
            cells, buckets = defaultdict(list), defaultdict(list)
            for i, obj in enumerate(objects):
                cell = freeze(obj["cell"])
                cells[cell].append(i)
                for slot in ranges[i]:
                    module = modules[int(original[slot])]
                    bucket = (cell, len(module), "700" in module) if role else (cell, len(module))
                    buckets[bucket].append(slot)
            faces = sum(len(ix) for ix in ranges)
            check("object cell includes exactly its stored face count and length profile", all(int(obj["cell"][2]) == len(ix) and tuple(obj["cell"][3]) == tuple(sorted(len(modules[int(original[k])]) for k in ix)) for obj, ix in zip(objects, ranges)), endpoint=endpoint, population=name)
            margin_ok, unique_ok, role_ok = True, True, True
            for draw_kind in ("pilot", "allocations"):
                matrix = saved[draw_kind]
                assert matrix.shape[1] == len(original)
                for ix in buckets.values():
                    margin_ok &= bool(np.all(np.sort(matrix[:, ix], axis=1) == np.sort(original[ix])))
                if "prototypes" in name:
                    base = len(modules) + 1
                    for object_indices in cells.values():
                        signatures = []
                        for i in object_indices:
                            ordered = np.sort(matrix[:, ranges[i]], axis=1).astype(np.int64)
                            signatures.append(sum(ordered[:, j] * base**j for j in range(ordered.shape[1])))
                        if len(signatures) > 1:
                            arranged = np.sort(np.stack(signatures, axis=1), axis=1)
                            unique_ok &= bool(np.all(np.diff(arranged, axis=1) != 0))
                if role:
                    is_w700 = np.array(["700" in s for s in modules])
                    role_ok &= bool(np.all(is_w700[matrix] == is_w700[original]))
            check("every saved pilot and tail allocation preserves every declared module bag", margin_ok, endpoint=endpoint, population=name, pilot_draws=len(saved["pilot"]), tail_draws=len(saved["allocations"]))
            if "prototypes" in name:
                check("every saved prototype allocation has unique bundles within each cell", unique_ok, endpoint=endpoint, population=name)
            if role:
                check("every saved role-control allocation preserves W700 presence in each slot", role_ok, endpoint=endpoint, population=name)
            marginals = Counter(s for mid in original for s in set(modules[int(mid)]))
            eligible = sorted(s for s, n in marginals.items() if n >= 5)
            check("candidate eligibility uses invariant full face marginals", eligible == witness["signs"], endpoint=endpoint, population=name, eligible_signs=len(eligible))
            candidates = np.array([i * len(eligible) + j for i in range(len(eligible)) for j in range(i, len(eligible))])
            check("search includes every eligible unordered pair including diagonals", np.array_equal(candidates, saved["candidates"]), endpoint=endpoint, population=name, candidate_count=len(candidates))
            observed = exposures(original, witness)
            check("direct set-product cross-face exposure census reproduces observed vector", np.array_equal(observed, saved["observed"]), endpoint=endpoint, population=name)
            collision_observed = collisions(original, witness)
            check("direct observed bundle collision count reproduces endpoint", collision_observed == result["observed_bundle_collisions"], endpoint=endpoint, population=name, collisions=collision_observed)
            direct_max_error = 0.
            sample_indices = sorted(set((0, 1, 2, 10, 100, len(saved["allocations"])//2, len(saved["allocations"])-1)))
            means = saved["means"]
            denominator = np.sqrt(means + 1)
            for i in sample_indices:
                allocation = saved["allocations"][i]
                counted = exposures(allocation, witness)
                scores = (counted - means) / denominator
                direct = [collisions(allocation, witness), float(scores[candidates].max()), float((-scores[candidates]).max())]
                direct_max_error = max(direct_max_error, float(np.max(np.abs(np.asarray(direct) - saved["stats"][i]))))
            check("independent sampled tail counts reproduce collision and full-search maxima", direct_max_error < 1e-12, endpoint=endpoint, population=name, sampled_tail_indices=sample_indices, maximum_error=direct_max_error)
            observed_stats = {"bundle_collision": collision_observed,
                              "maximum_enrichment": float(((observed - means) / denominator)[candidates].max()),
                              "maximum_depletion": float(((means - observed) / denominator)[candidates].max())}
            columns = {"bundle_collision": 0, "maximum_enrichment": 1, "maximum_depletion": 2}
            for test, reported in result["tests"].items():
                exceed = int(np.count_nonzero(saved["stats"][:, columns[test]] >= observed_stats[test] - 1e-12))
                p = (exceed + 1) / (len(saved["stats"]) + 1)
                check("tail denominator and full-search statistic reproduce reported p", exceed == reported["reference_exceedances"] and abs(p - reported["p"]) < 1e-12 and abs(observed_stats[test] - reported["observed"]) < 1e-12, endpoint=endpoint, population=name, test=test, p=p)
                expected_tests.append((test, reported))
            both = sum("034" in module and "700" in module for module in (modules[int(mid)] for mid in original))
            role_histogram = Counter(sum("700" in modules[int(original[k])] for k in ix) for ix in ranges)
            shape_034_without700 = sum("034" in module and "700" not in module for module in (modules[int(mid)] for mid in original))
            pair_index = witness["signs"].index("034") * len(eligible) + witness["signs"].index("700")
            populations.append({"endpoint": endpoint, "population": name, "objects": len(objects), "faces": faces,
                                "W700_bearing_faces_per_object": dict(sorted(role_histogram.items())),
                                "W034_and_W700_same_face": both, "W034_faces_without_W700": shape_034_without700,
                                "W034_W700_cross_face_exposures": int(observed[pair_index]),
                                "W034_W700_reference_expected_exposures": float(means[pair_index]),
                                "all_tail_margins_verified": margin_ok,
                                "all_tail_prototype_uniqueness_verified": unique_ok if "prototypes" in name else None})
        previous = 0.
        for rank, (_, reported) in enumerate(sorted(expected_tests, key=lambda pair: pair[1]["p"])):
            previous = max(previous, min(1., (len(expected_tests) - rank) * reported["p"]))
            check("independent Holm family reproduces adjustment", abs(previous - reported["p_holm_all_completed_tests"]) < 1e-12 and reported["holm_family_size"] == len(expected_tests) == summary["completed_tests"] == 10, endpoint=endpoint)
    result = {"status": "independent declared-law audit", "checks": checks,
              "passed": sum(row["pass"] for row in checks), "failed": sum(not row["pass"] for row in checks),
              "populations": populations,
              "scope": "Every saved allocation checked for all declared margins/role conditions/prototype uniqueness. Direct reference exposure recounts are a fixed sample; full tails are recounted from saved statistic arrays. This verifies the stated conditional laws, not historical manufacture or the induced original-population deduplication law.",
              "input_summaries_sha256": {str(p.relative_to(ROOT)): sha(p) for p in (PACKAGE / "run-v1/summary.json", PACKAGE / "role-control-v1/summary.json")}}
    output = HERE / "allocation-checks-v1.json"
    if output.exists():
        raise FileExistsError("Preserve completed reviewer output; choose a new version before rerunning")
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": result["passed"], "failed": result["failed"], "populations": populations}))


if __name__ == "__main__":
    main()
