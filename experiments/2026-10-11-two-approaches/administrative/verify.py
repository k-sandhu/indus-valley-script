"""Independent linear-algebra audit of every saved administrative allocation.

This verifier does not import the analysis implementation. Its cross-face counts
use sparse incidence multiplication, rather than broadcast sign-pair coding.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from itertools import combinations
import hashlib
import json
from pathlib import Path
import re
import time

import numpy as np
from scipy.sparse import csr_matrix

OWN = Path(__file__).resolve().parent
ROOT = OWN.parents[2]
RAW = ROOT / "data/raw/2026-10-11-two-approaches/administrative"


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def audit_allocations(run, name, role_control, checks):
    started = time.perf_counter()
    witness = load(RAW / run / f"{name}-witness.json")
    endpoint = load(OWN / run / f"{name}.json")
    if endpoint["status"] != "complete":
        checks.append({"name": f"{run}/{name}/completion", "passed": False,
                       "detail": "No complete allocation endpoint to verify"})
        return {"name": name, "status": "unfinished"}
    arrays = np.load(RAW / run / f"{name}-references.npz")
    pilots, tails = arrays["pilot"], arrays["allocations"]
    allocations = np.concatenate([pilots, tails])
    original = np.array(witness["original_assignment"], int)
    modules = witness["modules"]
    ranges = witness["ranges"]
    objects = witness["objects"]
    signs = witness["signs"]
    S = len(signs)
    lookup = {s: i for i, s in enumerate(signs)}
    rr, cc = [], []
    for m, seq in enumerate(modules):
        for s in set(seq):
            if s in lookup:
                rr.append(m)
                cc.append(lookup[s])
    incidence = csr_matrix((np.ones(len(rr), dtype=np.int32), (rr, cc)),
                           shape=(len(modules), S), dtype=np.int32)
    paira, pairb = [], []
    for face_slots in ranges:
        for a, b in combinations(face_slots, 2):
            paira.append(a)
            pairb.append(b)
    paira, pairb = np.array(paira, int), np.array(pairb, int)

    def independent_counts(allocation):
        mat = (incidence[allocation[paira]].T @ incidence[allocation[pairb]]).toarray()
        symmetric = mat + mat.T
        symmetric[np.diag_indices(S)] //= 2
        return np.triu(symmetric).ravel()

    observed = independent_counts(original)
    checks.append({"name": f"{run}/{name}/observed_counts",
                   "passed": bool(np.array_equal(observed, arrays["observed"]))})
    marg = Counter(s for m in original for s in set(modules[m]))
    independent_signs = sorted(s for s, n in marg.items() if n >= 5)
    candidates = np.array([i * S + j for i in range(S) for j in range(i, S)], int)
    checks.append({"name": f"{run}/{name}/invariant_candidate_set",
                   "passed": independent_signs == signs and bool(np.array_equal(candidates, arrays["candidates"]))})
    cells = defaultdict(list)
    for i, o in enumerate(objects):
        key = (o["site"], o["type"], len(o["sequences"]), tuple(sorted(map(len, o["sequences"]))))
        cells[key].append(i)
    collision_vec = np.zeros(len(allocations), dtype=np.int64)
    original_collision = 0
    all_margins, all_unique = True, True
    role_margins = True
    B = len(modules) + 1
    for cellkey, oi in cells.items():
        buckets = defaultdict(list)
        for i in oi:
            for slot in ranges[i]:
                seq = modules[original[slot]]
                bucket = (len(seq), "700" in seq) if role_control else (len(seq),)
                buckets[bucket].append(slot)
        for slots in buckets.values():
            expected = np.sort(original[slots])
            all_margins &= bool(np.all(np.sort(allocations[:, slots], axis=1) == expected))
        if role_control:
            roles = np.array(["700" in seq for seq in modules])
            role_margins &= bool(np.all(roles[allocations] == roles[original]))
        slots = np.array([ranges[i] for i in oi], int)
        sigs = np.sort(allocations[:, slots], axis=2)
        k = sigs.shape[2]
        weights = np.array([B ** j for j in range(k - 1, -1, -1)], np.int64)
        encoded = np.sort(sigs @ weights, axis=1)
        if len(oi) > 1:
            all_unique &= bool(np.all(encoded[:, 1:] != encoded[:, :-1]))
        # Run labels turn sorted equal signatures into per-trial multiplicities.
        runlabels = np.column_stack([np.zeros(len(allocations), int),
                                    np.cumsum(encoded[:, 1:] != encoded[:, :-1], axis=1)])
        labels = (runlabels + np.arange(len(allocations))[:, None] * len(oi)).ravel()
        lengths = np.bincount(labels, minlength=len(allocations) * len(oi)).reshape(len(allocations), len(oi))
        collision_vec += (lengths * (lengths - 1) // 2).sum(axis=1)
        origsigs = Counter(tuple(sorted(original[ranges[i]])) for i in oi)
        original_collision += sum(n * (n - 1) // 2 for n in origsigs.values())
    checks.append({"name": f"{run}/{name}/every_allocation_module_margin", "passed": all_margins,
                   "allocations": len(allocations)})
    if role_control:
        checks.append({"name": f"{run}/{name}/every_allocation_slot_role", "passed": role_margins})
    if name.endswith("prototypes"):
        checks.append({"name": f"{run}/{name}/every_allocation_prototype_uniqueness", "passed": all_unique})
    mean = sum((independent_counts(a).astype(float) for a in pilots), np.zeros(S * S)) / len(pilots)
    checks.append({"name": f"{run}/{name}/every_pilot_reference_mean",
                   "passed": bool(np.allclose(mean, arrays["means"], atol=1e-12, rtol=0))})
    denom = np.sqrt(mean + 1)
    obs_scores = (observed - mean) / denom
    observed_enrichment = float(obs_scores[candidates].max()) if len(candidates) else 0.0
    observed_depletion = float((-obs_scores)[candidates].max()) if len(candidates) else 0.0
    rebuilt = np.zeros_like(arrays["stats"])
    for i, a in enumerate(tails):
        z = (independent_counts(a) - mean) / denom
        rebuilt[i] = [collision_vec[len(pilots) + i],
                      z[candidates].max() if len(candidates) else 0,
                      (-z)[candidates].max() if len(candidates) else 0]
    checks.append({"name": f"{run}/{name}/every_tail_maximum_and_collision",
                   "passed": bool(np.allclose(rebuilt, arrays["stats"], atol=1e-12, rtol=0)),
                   "tail_allocations": len(tails)})
    checks.append({"name": f"{run}/{name}/observed_collision",
                   "passed": original_collision == endpoint["observed_bundle_collisions"]})
    observations = {"bundle_collision": (original_collision, 0),
                    "maximum_enrichment": (observed_enrichment, 1),
                    "maximum_depletion": (observed_depletion, 2)}
    for tname, test in endpoint["tests"].items():
        observed_value, column = observations[tname]
        exceed = int(np.count_nonzero(rebuilt[:, column] >= observed_value - 1e-12))
        p = (exceed + 1) / (len(tails) + 1)
        checks.append({"name": f"{run}/{name}/{tname}/tail_arithmetic",
                       "passed": abs(test["observed"] - observed_value) < 1e-12 and exceed == test["reference_exceedances"] and abs(p - test["p"]) < 1e-15})
    return {"name": name, "pilot_allocations": len(pilots), "tail_allocations": len(tails),
            "cross_face_counts_reconstructed": len(allocations) + 1,
            "runtime_seconds": time.perf_counter() - started}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", default="verification.json")
    args = ap.parse_args()
    output = OWN / args.output
    if output.exists() or Path(args.output).name != args.output:
        raise ValueError("Choose a fresh verification filename")
    checks, populations = [], []
    summary = load(OWN / "run-v1/input-summary.json")
    input_path = ROOT / summary["input_path"]
    rows = [json.loads(l) for l in input_path.read_text(encoding="utf-8").splitlines()]
    families = defaultdict(list)
    bases = defaultdict(set)
    for r in rows:
        families[r["object_family_id"]].append(r)
        match = re.fullmatch(r"([A-Za-z][A-Za-z0-9]*-\d+)[A-Za-z]?", r["source_cisi"].strip())
        if match:
            bases[match[1]].add(r["object_family_id"])
    checks += [{"name": "input_sha256", "passed": digest(input_path) == summary["input_sha256"]},
               {"name": "full_identity_accounting", "passed": len(rows) == summary["rows"] and len(families) == summary["full_physical_components"] and all(len(v) == 1 for v in bases.values())},
               {"name": "frozen_code_snapshot", "passed": digest(OWN / "run-v1/code_snapshot.py") == summary["code_sha256"]},
               {"name": "frozen_protocol_snapshot", "passed": digest(OWN / "run-v1/protocol_snapshot.md") == summary["protocol_sha256"]}]
    for mode in ["rtl", "mirror"]:
        nobj, nface, compatible = 0, 0, 0
        for rs in families.values():
            if len(rs) < 2 or len({r["site"] for r in rs}) > 1 or len({r["object_type"] for r in rs}) > 1:
                continue
            def eligible(r):
                if mode == "rtl":
                    return r["clean_rtl_singleline"]
                return r["complete_observed"] and not r["has_unknown_sign"] and not r["has_blank_space"] and r["single_line"] and bool(r["signs_reading_rtl"])
            if all(eligible(r) for r in rs):
                nobj += 1
                nface += len(rs)
                compatible += all(str(r["metadata"]["sides"]) == str(len(rs)) for r in rs)
        pop = summary["populations"][mode]
        checks.append({"name": f"{mode}/input_eligibility_reconstruction", "passed": nobj == pop["objects"] and nface == pop["faces"] and compatible == pop["declared_side_count_compatible_objects"]})
    for run in ["run-v1", "role-control-v1"]:
        family_tests = []
        for name in ["rtl-all", "rtl-prototypes", "mirror-all", "mirror-prototypes"]:
            populations.append(audit_allocations(run, name, run == "role-control-v1", checks))
            endpoint = load(OWN / run / f"{name}.json")
            family_tests.extend(endpoint.get("tests", {}).values())
        order = sorted(range(len(family_tests)), key=lambda i: family_tests[i]["p"])
        previous, correct = 0.0, True
        for rank, i in enumerate(order):
            previous = max(previous, min(1, family_tests[i]["p"] * (len(order) - rank)))
            correct &= abs(previous - family_tests[i]["p_holm_all_completed_tests"]) < 1e-15
        checks.append({"name": f"{run}/holm_family", "passed": correct and len(order) == 10})
    synthetic = load(OWN / "run-v1/identifiability.json")
    vecs = list(synthetic["likelihood_vectors"].values())
    checks.append({"name": "synthetic_exact_role_equivalence",
                   "passed": all(v == vecs[0] for v in vecs) and abs(sum(vecs[0]) - 1) < 1e-12 and all(v == 0 for v in synthetic["pairwise_total_variation"].values()) and synthetic["equal_prior_optimal_accuracy_without_anchor"] == 0.25})
    result = {"status": "Verified computation" if all(c["passed"] for c in checks) else "verification-failed",
              "method": "Independent sparse sign-incidence multiplication; all saved pilot and tail allocations, exact module/role margins, prototype uniqueness and source accounting checked.",
              "checks": checks, "passed": sum(c["passed"] for c in checks),
              "failed": sum(not c["passed"] for c in checks), "populations": populations,
              "verification_code_sha256": digest(__file__)}
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: result[k] for k in ["status", "passed", "failed"]}), flush=True)


if __name__ == "__main__":
    main()
