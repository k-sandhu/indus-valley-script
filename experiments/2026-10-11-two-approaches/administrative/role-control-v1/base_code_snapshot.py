"""Whole-face allocation tests and finite administrative-role equivalences.

Run manually from the repository root. Complete source-derived records and
reference allocations are written only to local RAW. No semantic values enter
the empirical statistics. See PROTOCOL.md for the frozen reference law.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
from itertools import combinations, product
import hashlib
import json
import math
from pathlib import Path
import re
import time

import numpy as np

OWN = Path(__file__).resolve().parent
ROOT = OWN.parents[2]
RAW = ROOT / "data/raw/2026-10-11-two-approaches/administrative"
INPUT = ROOT / "data/normalized/lipi_observed_faces.jsonl"
TALL = {"032": 2, "033": 3, "034": 4}
COHORT = {f"H-{i}" for i in range(2218, 2240)}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, value):
    Path(path).write_text(json.dumps(value, indent=2, ensure_ascii=False,
                                    allow_nan=False) + "\n", encoding="utf-8")


class UF:
    def __init__(self, n):
        self.p = list(range(n))

    def find(self, a):
        while self.p[a] != a:
            self.p[a] = self.p[self.p[a]]
            a = self.p[a]
        return a

    def union(self, a, b):
        a, b = self.find(a), self.find(b)
        if a != b:
            self.p[max(a, b)] = min(a, b)


def cisi_base(raw):
    m = re.fullmatch(r"([A-Za-z][A-Za-z0-9]*-\d+)[A-Za-z]?", raw.strip())
    return m[1] if m else None


def physical_groups(rows):
    uf, seen, unresolved = UF(len(rows)), {}, []
    for i, r in enumerate(rows):
        keys = [("family", str(r["object_family_id"]))]
        base = cisi_base(r.get("source_cisi", ""))
        if base:
            keys.append(("cisi", base))
        elif r.get("source_cisi", "").strip() not in {"", "-", "--"}:
            unresolved.append({"record_id": r["record_id"],
                               "reference": r["source_cisi"]})
        for key in keys:
            if key in seen:
                uf.union(i, seen[key])
            else:
                seen[key] = i
    groups = defaultdict(list)
    for i, r in enumerate(rows):
        groups[uf.find(i)].append(r)
    return list(groups.values()), unresolved


def broad_clean(r):
    return bool(r["complete_observed"] and not r["has_unknown_sign"]
                and not r["has_blank_space"] and r["single_line"]
                and r["signs_reading_rtl"])


def canonical(seq, mirror):
    seq = tuple(seq)
    return min(seq, seq[::-1]) if mirror else seq


def family_sort(key):
    return (int(key) if str(key).isdigit() else math.inf, str(key))


def prepare(groups, mode):
    selected, audit, exclusions = [], [], Counter()
    predicate = (lambda r: r["clean_rtl_singleline"]) if mode == "rtl" else broad_clean
    for rs in groups:
        families = sorted({r["object_family_id"] for r in rs}, key=family_sort)
        sites = {r["site"] for r in rs}
        types = {r["object_type"] for r in rs}
        ok = [bool(predicate(r)) for r in rs]
        reason = None
        if len(rs) < 2:
            reason = "one_recorded_face"
        elif len(sites) != 1 or len(types) != 1:
            reason = "conflicting_site_or_type"
        elif len({r["record_id"] for r in rs}) != len(rs):
            reason = "repeated_record_identifier"
        elif not all(ok):
            reason = "one_or_more_ineligible_recorded_faces"
        audit.append({"families": families, "record_ids": [r["record_id"] for r in rs],
                      "site": sorted(sites), "type": sorted(types),
                      "eligible_faces": sum(ok), "recorded_faces": len(rs),
                      "exclusion": reason})
        if reason:
            exclusions[reason] += 1
            continue
        faces = sorted([(canonical(r["signs_reading_rtl"], mode == "mirror"), r)
                        for r in rs], key=lambda sr: (len(sr[0]), sr[0], sr[1]["record_id"]))
        lengths = tuple(sorted(len(s) for s, _ in faces))
        selected.append({"key": families[0], "families": families,
                         "bases": sorted({cisi_base(r.get("source_cisi", ""))
                                          for r in rs if cisi_base(r.get("source_cisi", ""))}),
                         "site": next(iter(sites)), "type": next(iter(types)),
                         "sequences": [s for s, _ in faces],
                         "records": [r["record_id"] for _, r in faces],
                         "directions": [r["direction"] for _, r in faces],
                         "declared_sides": [r.get("metadata", {}).get("sides", "") for _, r in faces],
                         "cell": (next(iter(sites)), next(iter(types)), len(rs), lengths)})
    selected.sort(key=lambda o: family_sort(o["key"]))
    summary = {"mode": mode, "objects": len(selected),
               "faces": sum(len(o["sequences"]) for o in selected),
               "exclusions": dict(exclusions),
               "multi_objects_with_some_eligible_face": sum(a["recorded_faces"] >= 2 and a["eligible_faces"] > 0 for a in audit),
               "multi_objects_with_partly_eligible_faces": sum(0 < a["eligible_faces"] < a["recorded_faces"] for a in audit if a["recorded_faces"] >= 2),
               "selected_face_counts": dict(Counter(len(o["sequences"]) for o in selected)),
               "selected_directions": dict(Counter(d for o in selected for d in o["directions"])),
               "declared_side_count_compatible_objects": sum(all(str(v) == str(len(o["sequences"])) for v in o["declared_sides"]) for o in selected),
               "declared_side_count_conflicting_objects": sum(not all(str(v) == str(len(o["sequences"])) for v in o["declared_sides"]) for o in selected),
               "declared_sides_selected_face_values": dict(Counter(str(v) for o in selected for v in o["declared_sides"])),
               "site_type_objects": [{"site": k[0], "type": k[1], "objects": n}
                                     for k, n in sorted(Counter((o["site"], o["type"]) for o in selected).items())]}
    return selected, summary, audit


def bundle(o):
    return tuple(sorted(o["sequences"]))


def prototypes(objects):
    representatives, mult = {}, Counter()
    for o in objects:
        key = (o["cell"], bundle(o))
        mult[key] += 1
        representatives.setdefault(key, o)
    out = list(representatives.values())
    out.sort(key=lambda o: family_sort(o["key"]))
    return out, {"matched_prototypes": len(out),
                 "distinct_global_bundles": len({bundle(o) for o in objects}),
                 "copy_excess": len(objects) - len(out),
                 "matched_bundle_multiplicity_histogram": dict(Counter(mult.values())),
                 "largest_matched_bundle_multiplicity": max(mult.values(), default=0),
                 "physical_objects": len(objects)}


def graph_summary(objects):
    uf, seen = UF(len(objects)), {}
    for i, o in enumerate(objects):
        for s in o["sequences"]:
            if s in seen:
                uf.union(i, seen[s])
            else:
                seen[s] = i
    sizes = Counter(uf.find(i) for i in range(len(objects)))
    vals = sorted(sizes.values(), reverse=True)
    return {"objects": len(objects), "components": len(vals),
            "largest_component_objects": max(vals, default=0),
            "largest_component_share": max(vals, default=0) / len(objects) if objects else None,
            "component_size_histogram": dict(Counter(vals)),
            "at_least_five_components": len(vals) >= 5,
            "caveat": "Groups connect through every exact face, including repeated short modules. Component counts describe holdout feasibility, not independent manufacture."}


class Population:
    def __init__(self, objects, unique):
        self.objects, self.unique = objects, unique
        seqs = sorted({s for o in objects for s in o["sequences"]})
        self.seqs = seqs
        ids = {s: i for i, s in enumerate(seqs)}
        assign, ranges, bycell = [], [], defaultdict(list)
        paira, pairb = [], []
        for i, o in enumerate(objects):
            start = len(assign)
            assign.extend(ids[s] for s in o["sequences"])
            ix = tuple(range(start, len(assign)))
            ranges.append(ix)
            bycell[o["cell"]].append(i)
            for a, b in combinations(ix, 2):
                paira.append(a)
                pairb.append(b)
        self.assignment = np.array(assign, dtype=np.int32)
        self.ranges = ranges
        self.paira, self.pairb = np.array(paira, int), np.array(pairb, int)
        cells = []
        for key, oi in sorted(bycell.items()):
            bylen = defaultdict(list)
            for i in oi:
                for slot in ranges[i]:
                    bylen[len(seqs[self.assignment[slot]])].append(slot)
            cells.append({"key": key, "objects": oi,
                          "buckets": [np.array(v, int) for _, v in sorted(bylen.items())]})
        self.cells = cells
        marg = Counter(s for mid in assign for s in set(seqs[mid]))
        self.signs = sorted(s for s, n in marg.items() if n >= 5)
        signids = {s: i for i, s in enumerate(self.signs)}
        self.S = len(self.signs)
        self.candidates = np.array([i * self.S + j for i in range(self.S) for j in range(i, self.S)], int)
        lists = [sorted(signids[s] for s in set(seq) if s in signids) for seq in seqs]
        self.width = max(map(len, lists), default=0)
        pad = np.full((len(lists), self.width), -1, dtype=np.int32)
        for i, signs in enumerate(lists):
            pad[i, :len(signs)] = signs
        self.pad = pad
        self.proposals, self.rejections = 0, 0

    def sample(self, rng, cap):
        out = self.assignment.copy()
        for cell in self.cells:
            if len(cell["objects"]) < 2:
                continue
            while True:
                self.proposals += 1
                if self.proposals > cap:
                    raise RuntimeError("Frozen prototype-allocation proposal cap reached")
                for ix in cell["buckets"]:
                    out[ix] = rng.permutation(self.assignment[ix])
                if not self.unique:
                    break
                sigs = [tuple(sorted(out[list(self.ranges[i])])) for i in cell["objects"]]
                if len(sigs) == len(set(sigs)):
                    break
                self.rejections += 1
        return out

    def counts(self, allocation):
        if self.S == 0 or len(self.paira) == 0 or self.width == 0:
            return np.zeros(self.S * self.S, dtype=np.int32)
        a = self.pad[allocation[self.paira]]
        b = self.pad[allocation[self.pairb]]
        aa, bb = a[:, :, None], b[:, None, :]
        mask = (aa >= 0) & (bb >= 0)
        codes = np.minimum(aa, bb) * self.S + np.maximum(aa, bb)
        return np.bincount(codes[mask], minlength=self.S * self.S).astype(np.int32)

    def collisions(self, allocation):
        cs = Counter((o["cell"], tuple(sorted(allocation[list(ix)])))
                     for o, ix in zip(self.objects, self.ranges))
        return sum(n * (n - 1) // 2 for n in cs.values())

    def summary(self):
        return {"objects": len(self.objects), "faces": len(self.assignment),
                "face_pairs": len(self.paira), "distinct_modules": len(self.seqs),
                "allocation_cells": len(self.cells),
                "exchangeable_objects": sum(len(c["objects"]) for c in self.cells if len(c["objects"]) >= 2),
                "static_objects": sum(len(c["objects"]) for c in self.cells if len(c["objects"]) < 2),
                "eligible_sign_labels": self.S, "searched_unordered_sign_pairs": len(self.candidates),
                "minimum_sign_face_presence": 5,
                "copied_bundle_selection": self.unique}


def tail(observed, refs):
    refs = np.asarray(refs, float)
    exceed = int(np.count_nonzero(refs >= observed - 1e-12))
    p = (exceed + 1) / (len(refs) + 1)
    return {"observed": float(observed), "reference_exceedances": exceed,
            "tail_references": len(refs), "p": p,
            "monte_carlo_se_approx": math.sqrt(p * (1 - p) / (len(refs) + 1)),
            "reference_mean": float(refs.mean()),
            "reference_95_interval": np.quantile(refs, [0.025, 0.975]).tolist()}


def reference(pop, name, out, raw, pilot, tails, seed, cap):
    started = time.perf_counter()
    result = {"name": name, "population": pop.summary(), "pilot_references": pilot,
              "seed_pilot": seed, "seed_tail": seed + 1, "proposal_cap": cap,
              "prototype_constraint": "no duplicate bundle within an allocation cell" if pop.unique else None}
    obs = pop.counts(pop.assignment)
    observed_collision = pop.collisions(pop.assignment)
    try:
        rng = np.random.default_rng(seed)
        pilots = []
        mean = np.zeros(len(obs), float)
        for i in range(pilot):
            alloc = pop.sample(rng, cap)
            pilots.append(alloc)
            mean += pop.counts(alloc)
        mean /= pilot
        denom = np.sqrt(mean + 1)
        def scores(counts):
            if not len(pop.candidates):
                return 0.0, 0.0
            z = (counts - mean) / denom
            return float(z[pop.candidates].max()), float((-z)[pop.candidates].max())
        obsenrich, obsdeplete = scores(obs)
        rng = np.random.default_rng(seed + 1)
        allocations, stats = [], []
        for i in range(tails):
            alloc = pop.sample(rng, cap)
            allocations.append(alloc)
            a, b = scores(pop.counts(alloc))
            stats.append((pop.collisions(alloc), a, b))
        stats = np.array(stats, float)
        def pair_details(sign):
            z = sign * (obs - mean) / denom
            ranked = sorted(pop.candidates, key=lambda ix: (-z[ix], ix))[:10]
            return [{"sign_pair": [pop.signs[ix // pop.S], pop.signs[ix % pop.S]],
                     "cross_face_exposures": int(obs[ix]),
                     "reference_expected_exposures": float(mean[ix]),
                     "exposure_excess": float(obs[ix] - mean[ix]),
                     "score": float(z[ix])} for ix in ranked]
        result["status"] = "complete"
        result["tests"] = {}
        if not pop.unique:
            result["tests"]["bundle_collision"] = tail(observed_collision, stats[:, 0])
        result["tests"]["maximum_enrichment"] = tail(obsenrich, stats[:, 1])
        result["tests"]["maximum_depletion"] = tail(obsdeplete, stats[:, 2])
        result["largest_enrichment_pairs"] = pair_details(1)
        result["largest_depletion_pairs"] = pair_details(-1)
        result["observed_bundle_collisions"] = int(observed_collision)
        np.savez_compressed(raw / f"{name}-references.npz", pilot=np.stack(pilots),
                            allocations=np.stack(allocations), means=mean, observed=obs,
                            stats=stats, candidates=pop.candidates)
    except RuntimeError as exc:
        result["status"] = "unfinished-proposal-cap"
        result["reason"] = str(exc)
        result["tests"] = {}
    result["proposals"] = pop.proposals
    result["rejections"] = pop.rejections
    result["proposal_acceptance"] = ((pop.proposals - pop.rejections) / pop.proposals) if pop.proposals else 1
    result["runtime_seconds"] = time.perf_counter() - started
    write(raw / f"{name}-witness.json", {"objects": pop.objects, "modules": pop.seqs,
                                        "signs": pop.signs, "ranges": pop.ranges,
                                        "original_assignment": pop.assignment.tolist()})
    write(out / f"{name}.json", result)
    print(name, result["status"], "objects", len(pop.objects), "proposals", pop.proposals,
          "rejections", pop.rejections, "seconds", round(result["runtime_seconds"], 2), flush=True)
    return result


def frame_audit(objects):
    anchors = defaultdict(list)
    tall = defaultdict(list)
    for o in objects:
        if len(o["sequences"]) != 2:
            continue
        a, b = o["sequences"]
        for x, y in sorted(set([(a, b), (b, a)])):
            anchors[(o["site"], o["type"], x)].append((o["key"], y))
            if len(y) == 2 and "700" in y:
                s = y[0] if y[1] == "700" else y[1]
                if s in TALL:
                    tall[(o["site"], o["type"], x)].append((o["key"], TALL[s]))
    anchorclasses = []
    for (site, typ, seq), obs in anchors.items():
        ys = Counter(y for _, y in obs)
        one_sub = sum(len(a) == len(b) and sum(x != y for x, y in zip(a, b)) == 1
                      for a, b in combinations(ys, 2))
        anchorclasses.append({"site": site, "type": typ,
                              "anchor_sha256": hashlib.sha256("-".join(seq).encode()).hexdigest(),
                              "anchor_length": len(seq), "objects": len({k for k, _ in obs}),
                              "companion_module_classes": len(ys),
                              "one_code_substitution_class_pairs": one_sub,
                              "companion_multiplicity_histogram": dict(Counter(ys.values()))})
    tallclasses = [{"site": k[0], "type": k[1], "anchor_length": len(k[2]),
                   "anchor_sha256": hashlib.sha256("-".join(k[2]).encode()).hexdigest(),
                   "objects": len({x[0] for x in obs}), "tall_stroke_counts": dict(Counter(x[1] for x in obs)),
                   "distinct_tall_stroke_counts": len({x[1] for x in obs})}
                  for k, obs in tall.items()]
    return {"two_face_objects": sum(len(o["sequences"]) == 2 for o in objects),
            "exact_anchor_classes": len(anchorclasses),
            "anchor_classes_with_at_least_three_objects": sum(a["objects"] >= 3 for a in anchorclasses),
            "anchor_classes_with_multiple_companions": sum(a["companion_module_classes"] > 1 for a in anchorclasses),
            "supported_variable_anchors": sorted([a for a in anchorclasses if a["objects"] >= 3 and a["companion_module_classes"] > 1], key=lambda a: (-a["objects"], a["anchor_sha256"])),
            "tall700_objects": len({x[0] for obs in tall.values() for x in obs}),
            "tall700_anchor_classes": len(tallclasses),
            "tall700_variable_anchor_classes": sum(a["distinct_tall_stroke_counts"] > 1 for a in tallclasses),
            "tall700_count_distribution": dict(Counter(v for obs in tall.values() for _, v in obs)),
            "tall700_variable_anchors": sorted([a for a in tallclasses if a["distinct_tall_stroke_counts"] > 1], key=lambda a: (-a["objects"], a["anchor_sha256"])),
            "scope": "Descriptive enumeration of every exact two-face anchor. Graphic count labels identify tall strokes only; no goods or fee unit is assigned."}


def identifiability():
    # These symbols are invented strings and have no Indus sign assignments.
    role_labels = {
        "bearer-standing-entitlement": ["bearer class", "service entitlement", "entitlement tier"],
        "issuer-licensed-service": ["issuing authority", "licensed service", "licence grade"],
        "commodity-grade": ["producer or controlled class", "commodity class", "quality or quantity grade"],
        "canonical-transaction-receipt": ["transferring office", "canonical packet", "completed transfer tier"],
    }
    distribution = []
    for issuer, service, grade in product(range(2), range(3), range(2)):
        p = [0.6, 0.4][issuer] * [0.5, 0.3, 0.2][service] * ([0.75, 0.25] if service == 0 else [0.3, 0.7])[grade]
        visible = (f"A{issuer}", f"B{service}", f"C{service}{grade}")
        distribution.append({"invented_visible_bundle": visible, "probability": p})
    likelihoods = {role: [r["probability"] for r in distribution] for role in role_labels}
    # A deliberately sharper mechanism pair: physical carriers are reused in one
    # model and destroyed at first use in the other. The measured observation is
    # individual-carrier survival through an independently documented second use.
    intervention = {
        "mechanisms": ["standing reusable credential", "single-use consumed receipt"],
        "prior": [0.5, 0.5],
        "new_observation": "same registered carrier independently documented in a second use",
        "positive_probabilities_assumed": [0.9, 0.1],
        "positive_posterior": [0.9, 0.1],
        "negative_posterior": [0.1, 0.9],
        "optimal_single_observation_accuracy": 0.9,
        "status": "Synthetic mechanism-specific example. A receipt model permitting reuse overlaps the credential model and would not be separated by this observation.",
    }
    return {"status": "Synthetic exact equivalence certificate",
            "visible_states": len(distribution), "probability_sum": sum(r["probability"] for r in distribution),
            "role_interpretations": role_labels, "finite_distribution": distribution,
            "likelihood_vectors": likelihoods,
            "pairwise_total_variation": {f"{a} | {b}": 0.5 * sum(abs(x - y) for x, y in zip(likelihoods[a], likelihoods[b])) for a, b in combinations(role_labels, 2)},
            "equal_prior_optimal_accuracy_without_anchor": 1 / len(role_labels),
            "mutual_information_bits_role_visible_bundle": 0.0,
            "mechanism_specific_acquisition_counterexample": intervention,
            "implication": "A field interpretation is a latent relabelling unless it restricts an additional observable. More face drawings sampled from the same distribution preserve the equivalence."}


def holm(results):
    tests = [(r, name, value) for r in results for name, value in r.get("tests", {}).items()]
    order = sorted(range(len(tests)), key=lambda i: tests[i][2]["p"])
    previous = 0.0
    for rank, i in enumerate(order):
        previous = max(previous, min(1.0, (len(tests) - rank) * tests[i][2]["p"]))
        tests[i][2]["p_holm_all_completed_tests"] = previous
        tests[i][2]["holm_family_size"] = len(tests)
    return len(tests)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default="run-v1")
    ap.add_argument("--pilot", type=int, default=1999)
    ap.add_argument("--references", type=int, default=9999)
    ap.add_argument("--cap", type=int, default=1000000)
    ap.add_argument("--seed", type=int, default=2026101117)
    args = ap.parse_args()
    out, raw = OWN / args.out, RAW / args.out
    if out.exists() or raw.exists() or Path(args.out).name != args.out:
        raise ValueError("Choose a fresh single-directory output name; frozen endpoints are never overwritten")
    out.mkdir(parents=True, exist_ok=False)
    raw.mkdir(parents=True, exist_ok=False)
    rows = [json.loads(l) for l in INPUT.read_text(encoding="utf-8").splitlines()]
    groups, unresolved = physical_groups(rows)
    base_summary = {"input_path": INPUT.relative_to(ROOT).as_posix(), "input_sha256": sha(INPUT),
                    "code_sha256": sha(__file__), "protocol_sha256": sha(OWN / "PROTOCOL.md"),
                    "created_utc": datetime.now(timezone.utc).isoformat(), "rows": len(rows),
                    "numeric_families": len({r["object_family_id"] for r in rows}),
                    "full_physical_components": len(groups),
                    "multi_record_components_before_filters": sum(len(rs) >= 2 for rs in groups),
                    "source_faces_per_component_histogram": dict(Counter(len(rs) for rs in groups)),
                    "clean_rtl_rows": sum(r["clean_rtl_singleline"] for r in rows),
                    "unresolved_nonblank_reference_rows": len(unresolved),
                    "local_raw_path": raw.relative_to(ROOT).as_posix(), "populations": {}}
    write(raw / "identity-witness.json", {"unresolved": unresolved,
                                          "physical_families": [[r["record_id"] for r in rs] for rs in groups]})
    results, frames = [], {}
    for j, mode in enumerate(["rtl", "mirror"]):
        objects, summary, audit = prepare(groups, mode)
        proto, copy = prototypes(objects)
        summary["copied_bundle_audit"] = copy
        summary["all_object_face_sharing"] = graph_summary(objects)
        summary["prototype_face_sharing"] = graph_summary(proto)
        base_summary["populations"][mode] = summary
        write(raw / f"{mode}-eligibility.json", audit)
        frames[mode] = {"all_objects": frame_audit(objects), "prototypes": frame_audit(proto),
                        "without_H2218_H2239": frame_audit([o for o in objects if not (set(o["bases"]) & COHORT)]),
                        "declared_side_count_compatible": frame_audit([o for o in objects if all(str(v) == str(len(o["sequences"])) for v in o["declared_sides"])])}
        for k, (label, obs, unique) in enumerate([("all", objects, False), ("prototypes", proto, True)]):
            pop = Population(obs, unique)
            results.append(reference(pop, f"{mode}-{label}", out, raw, args.pilot,
                                     args.references, args.seed + 100 * j + 10 * k, args.cap))
    ntests = holm(results)
    for r in results:
        write(out / f"{r['name']}.json", r)
    write(out / "input-summary.json", base_summary)
    write(out / "frame-audit.json", frames)
    write(out / "identifiability.json", identifiability())
    write(out / "summary.json", {"status": "Frozen evaluation", "completed_tests": ntests,
                                  "expected_tests": 10,
                                  "results": [{"name": r["name"], "status": r["status"], "tests": r.get("tests", {})} for r in results],
                                  "local_only_reference_witnesses": raw.relative_to(ROOT).as_posix(),
                                  "seed": args.seed, "pilot": args.pilot, "references": args.references})
    (out / "code_snapshot.py").write_bytes(Path(__file__).read_bytes())
    (out / "protocol_snapshot.md").write_bytes((OWN / "PROTOCOL.md").read_bytes())


if __name__ == "__main__":
    main()
