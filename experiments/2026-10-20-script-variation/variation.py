"""Source-qualified graphic variation; raw source-derived outputs stay local."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import csv
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import platform
import re
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from bench import shots

HERE = Path(__file__).resolve().parent
LOCAL = ROOT / "data/raw/2026-10-20-script-variation"
SEED = "2026-10-20-script-variation"
INPUTS = {
    "faces": ROOT / "data/normalized/lipi_observed_faces.jsonl",
    "crosswalk": ROOT / "data/normalized/mayig_wells_class_crosswalk.json",
    "cisi1": ROOT / "data/raw/2026-10-13-cisi-basic-data-full/assembled/cisi1-basic-data.jsonl",
    "cisi2": ROOT / "data/raw/2026-10-13-cisi-basic-data-full/assembled/cisi2-basic-data.jsonl",
    "cisi_flags": ROOT / "experiments/2026-10-13-cisi-basic-data-full/object-flags.csv",
    "excavation_join": ROOT / "experiments/2026-10-13-mackay-marshall-tables/run-2026-10-13/join-table.csv",
    "inventory_code": ROOT / "experiments/2026-10-12-data-inventory/coverage.py",
}
spec = importlib.util.spec_from_file_location("script_variation_inventory", INPUTS["inventory_code"])
INV = importlib.util.module_from_spec(spec)
spec.loader.exec_module(INV)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def rows(path):
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]


def dump(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, allow_nan=False)
        f.write("\n")


def jsonl(path, records):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, allow_nan=False) + "\n")


def provenance():
    paths = dict(INPUTS, scoring_code=Path(__file__), protocol=HERE / "PROTOCOL.md", predictions=HERE / "PREDICTIONS.json")
    return {
        "inputs_and_code": {k: {"path": str(p.relative_to(ROOT)).replace("\\", "/"), "sha256": sha(p)} for k, p in paths.items()},
        "python": sys.version,
        "numpy": np.__version__,
        "platform": platform.platform(),
        "utc": datetime.now(timezone.utc).isoformat(),
        "authors": [{"agent": "OpenAI Codex /root/script_variation", "model": "GPT-6 family; exact identifier unavailable to agent", "harness": "Codex desktop multi-agent, functions, PowerShell, Python"}],
    }


def norm(field, value):
    return INV.norm(value) if INV.usable(field, value) else "<MISSING>"


def source_layer():
    """Build qualified source links without inventing a physical-identity edge."""
    outdir = HERE / "source-v1"
    localdir = LOCAL / "source-v1"
    outdir.mkdir(exist_ok=False)
    localdir.mkdir(parents=True, exist_ok=False)
    with INPUTS["cisi_flags"].open(encoding="utf-8") as f:
        flags = list(csv.DictReader(f))
    by_cisi = {(r["cisi"], r["volume"]): r for r in flags}
    by_family = defaultdict(lambda: {"cisi_sources": [], "excavation_sources": [], "accession_keys": [], "qualified_cisi": False})
    collision_keys = defaultdict(set)
    failed = Counter()
    for source in ("cisi1", "cisi2"):
        for row in rows(INPUTS[source]):
            flag = by_cisi.get((row["cisi"], row["volume"]))
            if not flag or flag["join"] != "one-family" or not flag["lipi_family"]:
                failed["no_one_family_join"] += 1
                continue
            fam = str(flag["lipi_family"])
            entry = by_family[fam]
            uncertainty = set(row.get("uncertain_columns", []))
            entry["cisi_sources"].append({
                "cisi": row["cisi"], "volume": row["volume"],
                "printed_page": row["printed_page"], "pdf_page": row["pdf_page"],
                "block": row.get("block"), "uncertain_columns": sorted(uncertainty),
                "excavation_usable": bool(row.get("parsed", {}).get("excavation_usable")),
            })
            if flag.get("supplies_unbracketed_excavation") == "1" and "col1" not in uncertainty and "col3_excavation" not in uncertainty:
                entry["qualified_cisi"] = True
            if "col4_museum" in uncertainty:
                continue
            for group in row.get("parsed", {}).get("museum_holdings", []):
                for holding in group:
                    number = holding.get("number")
                    code = holding.get("code")
                    if (not code or not number or holding.get("former") or holding.get("query_mark") or holding.get("unknown_code")
                            or not re.fullmatch(r"[A-Za-z0-9 ./_-]+", number)):
                        continue
                    key = code.upper() + ":" + re.sub(r"\s+", "", number).upper()
                    entry["accession_keys"].append(key)
                    collision_keys[key].add(fam)
    with INPUTS["excavation_join"].open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            by_family[row["lipi_family_id"]]["excavation_sources"].append({
                k: row[k] for k in ("source", "source_row_id", "catalogue_no", "printed_page", "disposition", "basis")
            })
    collisions = {k: sorted(v) for k, v in collision_keys.items() if len(v) > 1}
    collision_families = set(f for v in collisions.values() for f in v)
    for fam, r in by_family.items():
        r["family"] = fam
        r["volumes"] = sorted({x["volume"] for x in r["cisi_sources"]})
        r["accession_keys"] = sorted(set(r["accession_keys"]))
        r["accession_collision"] = fam in collision_families
    jsonl(localdir / "objects.jsonl", [by_family[k] for k in sorted(by_family)])
    dump(localdir / "accession-collisions.json", collisions)
    all_faces = rows(INPUTS["faces"])
    families = {r["object_family_id"] for r in all_faces}
    counts = {
        "all_objects": len(families),
        "objects_with_source_layer": len(by_family),
        "objects_with_cisi_table_locator": sum(bool(r["cisi_sources"]) for r in by_family.values()),
        "objects_with_unbracketed_excavation_source": sum(r["qualified_cisi"] for r in by_family.values()),
        "objects_with_excavation_table_locator": sum(bool(r["excavation_sources"]) for r in by_family.values()),
        "objects_with_unambiguous_accession_key": sum(bool(r["accession_keys"]) for r in by_family.values()),
        "candidate_accession_collision_keys": len(collisions),
        "candidate_accession_collision_families": len(collision_families),
        "by_catalogue_volume_set": dict(Counter("+".join(r["volumes"]) or "not-held" for r in by_family.values())),
        "unjoined_cisi_rows": dict(failed),
        "new_external_sources": 0,
        "new_observed_physical_objects": 0,
        "added_fields": ["cisi_table_locator", "catalogue_volume_set", "excavation_table_locator", "unbracketed_excavation_source", "accession_collision_candidate"],
        "prior_values_preserved": True,
        "local_objects_sha256": sha(localdir / "objects.jsonl"),
        "local_collisions_sha256": sha(localdir / "accession-collisions.json"),
    }
    dump(outdir / "coverage.json", dict(counts, provenance=provenance()))
    print(json.dumps(counts, indent=2))


def mapping():
    raw = json.loads(INPUTS["crosswalk"].read_text(encoding="utf-8"))["by_wells_id"]
    codeclass = {k: v[0] for k, v in raw.items() if len(v) == 1}
    familycodes = defaultdict(list)
    for code, cl in codeclass.items():
        if int(code) >= 200:
            familycodes[cl].append(code)
    return codeclass, {k: sorted(v) for k, v in familycodes.items() if len(v) > 1}


def observations(rawrows, unit="component"):
    codeclass, familycodes = mapping()
    src = {r["family"]: r for r in rows(LOCAL / "source-v1/objects.jsonl")}
    candidates = defaultdict(list)
    elig = Counter()
    for row in rawrows:
        if not row.get("clean_rtl_singleline") or len(row["signs_reading_rtl"]) < 3:
            continue
        seq = row["signs_reading_rtl"]
        m = row.get("metadata", {})
        s = src.get(row["object_family_id"], {})
        classtext = [codeclass.get(c, "W" + c) for c in seq]
        for i, code in enumerate(seq):
            cl = codeclass.get(code)
            if code not in familycodes.get(cl, []):
                continue
            elig["target_events"] += 1
            event = {
                "code": code, "class": cl, "candidate_codes": familycodes[cl],
                "site": norm("site", row.get("site")),
                "carrier": norm("type", row.get("object_type")),
                "material": norm("material", m.get("material")),
                "motif": norm("symbol", row.get("symbol")),
                "preservation": norm("preservation", m.get("preservation")),
                "volume": "+".join(s.get("volumes", [])) or "not-held",
                "qualified": s.get("qualified_cisi", False),
                "accession_collision": s.get("accession_collision", False),
                "excavation_source": "+".join(sorted({z["source"] for z in s.get("excavation_sources", [])})) or "not-held",
                "component": row["component"], "family": row["object_family_id"],
                "record": row["record_id"], "position": i, "length": len(seq),
                "previous": classtext[i - 1] if i else "<START>",
                "next": classtext[i + 1] if i + 1 < len(seq) else "<END>",
                "fine_frame": seq[:i] + [cl] + seq[i + 1:],
                "graphic_frame": classtext,
                "rank": digest([SEED, row["component"], row["record_id"], i]),
            }
            candidates[row[unit if unit == "component" else "object_family_id"]].append(event)
    result = [min(events, key=lambda x: x["rank"]) for events in candidates.values()]
    elig["selected_units"] = len(result)
    return result, dict(elig)


def metakey(r, usevolume=True):
    return tuple(r[k] for k in ("class", "carrier", "material", "motif", "preservation")) + ((r["volume"],) if usevolume else ())


def contextkey(r, usevolume=True):
    return metakey(r, usevolume) + tuple(r[k] for k in ("length", "position", "previous", "next"))


class VariantModel:
    def __init__(self, train, usevolume=True):
        self.usevolume = usevolume
        self.prior = defaultdict(Counter)
        self.meta, self.context = defaultdict(Counter), defaultdict(Counter)
        self.siteprior, self.sitemeta, self.sitecontext = defaultdict(Counter), defaultdict(Counter), defaultdict(Counter)
        self.volumeprior, self.volumemeta, self.volumecontext = defaultdict(Counter), defaultdict(Counter), defaultdict(Counter)
        self.candidates = {}
        for r in train:
            code, cl = r["code"], r["class"]
            self.candidates[cl] = r["candidate_codes"]
            self.prior[cl][code] += 1
            mk, ck = metakey(r, usevolume), contextkey(r, usevolume)
            self.meta[mk][code] += 1
            self.context[ck][code] += 1
            self.siteprior[(cl, r["site"])][code] += 1
            self.sitemeta[(mk, r["site"])][code] += 1
            self.sitecontext[(ck, r["site"])][code] += 1
            self.volumeprior[(cl, r["site"], r["volume"])][code] += 1
            self.volumemeta[(mk, r["site"], r["volume"])][code] += 1
            self.volumecontext[(ck, r["site"], r["volume"])][code] += 1

    @staticmethod
    def shrink(c, code, prior):
        return (c.get(code, 0) + 20 * prior) / (sum(c.values()) + 20)

    def probability(self, r, regional=False, source=False):
        code, cl = r["code"], r["class"]
        c = self.prior[cl]
        p = (c.get(code, 0) + 1) / (sum(c.values()) + len(self.candidates[cl]))
        mk, ck = metakey(r, self.usevolume), contextkey(r, self.usevolume)
        if regional or source:
            p = self.shrink(self.siteprior[(cl, r["site"])], code, p)
            p = self.shrink(self.sitemeta[(mk, r["site"])], code, p)
            p = self.shrink(self.sitecontext[(ck, r["site"])], code, p)
        else:
            p = self.shrink(self.meta[mk], code, p)
            p = self.shrink(self.context[ck], code, p)
        if source:
            p = self.shrink(self.volumeprior[(cl, r["site"], r["volume"])], code, p)
            p = self.shrink(self.volumemeta[(mk, r["site"], r["volume"])], code, p)
            p = self.shrink(self.volumecontext[(ck, r["site"], r["volume"])], code, p)
        return p


def eligible_classes(train):
    ct = defaultdict(Counter)
    for r in train:
        ct[r["class"]][r["code"]] += 1
    return {cl for cl, codes in ct.items() if sum(v >= 3 for v in codes.values()) >= 2}


def bootstrap(values, components, draws=4999, seed=2671020):
    if not values:
        return None
    grouped = defaultdict(list)
    for value, component in zip(values, components):
        grouped[component].append(value)
    sums = np.array([sum(v) for v in grouped.values()])
    ns = np.array([len(v) for v in grouped.values()])
    rng = np.random.default_rng(seed)
    samples = []
    for _ in range(draws):
        idx = rng.integers(len(sums), size=len(sums))
        samples.append(float(sum(sums[idx]) / sum(ns[idx])))
    return [float(x) for x in np.quantile(samples, [0.025, 0.975])]


def compare(train, test, usevolume=True, source=False, draws=4999):
    eligible = eligible_classes(train)
    test = [r for r in test if r["class"] in eligible]
    train = [r for r in train if r["class"] in eligible]
    model = VariantModel(train, usevolume)
    details = []
    for r in test:
        pb = model.probability(r, regional=source)
        pa = model.probability(r, regional=True, source=source)
        details.append(dict(r, p_baseline=pb, p_added=pa, gain=math.log2(pa / pb)))
    values = [r["gain"] for r in details]
    gain = float(np.mean(values)) if values else None
    interval = bootstrap(values, [r["component"] for r in details], draws=draws)
    sites = Counter(r["site"] for r in details)
    family_removals = {}
    for cl in sorted({r["class"] for r in details}):
        reduced = [r["gain"] for r in details if r["class"] != cl]
        family_removals[cl] = float(np.mean(reduced)) if reduced else None
    support = len(details) >= 100 and sum(n >= 15 for n in sites.values()) >= 3
    positive_removals = bool(family_removals) and all(v is not None and v > 0 for v in family_removals.values())
    outcome = {
        "discovery_observations": len(train), "confirmation_observations": len(test),
        "eligible_classes": len(eligible), "scored_classes": len({r["class"] for r in test}),
        "site_counts": dict(sites), "mean_gain_bits": gain, "component_bootstrap_95_interval": interval,
        "mean_baseline_log2_probability": float(np.mean([math.log2(r["p_baseline"]) for r in details])) if details else None,
        "mean_added_log2_probability": float(np.mean([math.log2(r["p_added"]) for r in details])) if details else None,
        "support_threshold_met": support, "leave_one_class_out_gain_bits": family_removals,
        "all_leave_one_class_out_positive": positive_removals,
        "passes_primary_rule": bool(support and gain >= 0.03 and interval[0] > 0 and positive_removals) if gain is not None else False,
    }
    return outcome, details


def lr_stat(events, site_labels=None):
    if not events:
        return 0.0
    cells, codes, sites = Counter(), Counter(), Counter()
    for i, r in enumerate(events):
        site = site_labels[i] if site_labels is not None else r["site"]
        code = r["code"]
        cells[(site, code)] += 1
        codes[code] += 1
        sites[site] += 1
    n = len(events)
    return 2 * sum(count * math.log(count * n / (sites[site] * codes[code])) for (site, code), count in cells.items())


def frame_test(test, graphic=False, permutations=4999):
    buckets = defaultdict(list)
    for r in test:
        frame = r["graphic_frame"] if graphic else r["fine_frame"]
        key = tuple(frame) + (r["position"], r["carrier"], r["motif"], r["preservation"], r["volume"])
        buckets[key].append(r)
    cells = [v for v in buckets.values() if len({r["site"] for r in v}) > 1 and len({r["code"] for r in v}) > 1]
    observed_cells = [lr_stat(v) for v in cells]
    observed = sum(observed_cells)
    rng = np.random.default_rng(2671021 + graphic)
    null = []
    for _ in range(permutations):
        null.append(sum(lr_stat(v, rng.permutation([r["site"] for r in v])) for v in cells))
    p = (1 + sum(v >= observed - 1e-12 for v in null)) / (1 + permutations)
    support = sum(len(v) for v in cells) >= 30 and len(cells) >= 5
    influence = max(observed_cells) / observed if observed else None
    return {
        "frame": "graphic_classes" if graphic else "fine_codes_outside_target",
        "matching_cells": len(buckets), "informative_cells": len(cells),
        "informative_components": sum(len(v) for v in cells), "likelihood_ratio": observed,
        "permutations": permutations, "null_mean": float(np.mean(null)),
        "p": p, "largest_cell_statistic_share": influence,
        "support_threshold_met": support,
        "passes_rule": bool(support and p <= 0.05 and influence is not None and influence <= 0.5),
    }, cells


def simulation():
    out = HERE / "synthetic-v1"
    out.mkdir(exist_ok=False)
    rng = np.random.default_rng(2671019)
    result = {}
    for scenario in ("null", "local_spelling", "context_confounding"):
        records = []
        for i in range(2400):
            site = "A" if rng.random() < 0.5 else "B"
            motif = ("Bull" if rng.random() < (0.95 if site == "A" else 0.05) else "Unicorn") if scenario == "context_confounding" else "Unicorn"
            p = 0.5
            if scenario == "local_spelling":
                p = 0.85 if site == "A" else 0.15
            if scenario == "context_confounding":
                p = 0.9 if motif == "Bull" else 0.1
            code = "390" if rng.random() < p else "405"
            records.append({"class": "P086", "code": code, "candidate_codes": ["390", "405"], "site": site,
                            "carrier": "SEAL:S", "material": "Steatite", "motif": motif, "preservation": "complete",
                            "volume": "fixture", "length": 4, "position": 1, "previous": "P01", "next": "P02",
                            "component": f"generated-{i}", "family": f"generated-{i}"})
        outcome, details = compare(records[:1200], records[1200:], draws=4999)
        result[scenario] = outcome
    result["observational_equivalence"] = {
        "same_input_scenarios": ["one language with local spelling", "two languages with common written categories"],
        "observable_input_identical": True,
        "historical_mechanism_identified": False,
        "explanation": "Both historical accounts can assign the same city-conditioned probabilities to every observed sign. Renaming their hidden cause changes no scorer input or outcome.",
    }
    dump(out / "controls.json", {"schema_version": "1.0", "synthetic": True, "result": result, "provenance": provenance()})
    print(json.dumps({k: v.get("mean_gain_bits") for k, v in result.items() if "mean_gain_bits" in v}, indent=2))


def discover():
    rr, event = shots.load_half(HERE / "round.json", "discovery", "variant-choice", HERE / "spent-private.json", allow_spent=True)
    obs, eligibility = observations(rr)
    object_obs, object_eligibility = observations(rr, unit="object_family_id")
    localdir = LOCAL / "discovery-v1"
    localdir.mkdir(parents=True, exist_ok=False)
    jsonl(localdir / "component-observations.jsonl", obs)
    jsonl(localdir / "object-observations.jsonl", object_obs)
    summary = {"eligibility": eligibility, "object_eligibility": object_eligibility,
               "candidate_class_count": len({r["class"] for r in obs}), "eligible_class_count": len(eligible_classes(obs)),
               "site_counts": dict(Counter(r["site"] for r in obs)), "access_event": event,
               "component_observations_sha256": sha(localdir / "component-observations.jsonl"),
               "object_observations_sha256": sha(localdir / "object-observations.jsonl"), "provenance": provenance()}
    dump(HERE / "discovery-v1.json", summary)
    print(json.dumps({k: v for k, v in summary.items() if k not in ("provenance", "access_event")}, indent=2))


def confirm():
    outdir = HERE / "run-v1"
    localdir = LOCAL / "run-v1"
    outdir.mkdir(exist_ok=False)
    localdir.mkdir(parents=True, exist_ok=False)
    rr, event = shots.load_half(HERE / "round.json", "confirmation", "variant-choice", HERE / "spent-private.json", allow_spent=True)
    test, eligibility = observations(rr)
    object_test, object_eligibility = observations(rr, unit="object_family_id")
    train = rows(LOCAL / "discovery-v1/component-observations.jsonl")
    object_train = rows(LOCAL / "discovery-v1/object-observations.jsonl")
    summary, details = compare(train, test)
    jsonl(localdir / "primary-details.jsonl", details)
    variants = {"primary": summary}
    variants["without_catalogue_volume"], _ = compare(train, test, usevolume=False)
    variants["source_block_after_site"], _ = compare(train, test, usevolume=False, source=True)
    predicates = {
        "seals_only": lambda r: r["carrier"].startswith("SEAL"),
        "qualified_cisi": lambda r: r["qualified"],
        "excluding_accession_collisions": lambda r: not r["accession_collision"],
        "mohenjo_daro": lambda r: r["site"] == "Mohenjo-daro",
        "excluding_mohenjo_daro": lambda r: r["site"] != "Mohenjo-daro",
        "cisi1_only": lambda r: r["volume"] == "cisi1",
        "cisi2_only": lambda r: r["volume"] == "cisi2",
    }
    for name, predicate in predicates.items():
        variants[name], _ = compare([r for r in train if predicate(r)], [r for r in test if predicate(r)])
    variants["one_per_physical_object"], _ = compare(object_train, object_test)
    frames = {}
    for name, graphic in (("fine", False), ("graphic", True)):
        frames[name], cells = frame_test(test, graphic)
        dump(localdir / f"{name}-frame-cells.json", cells)
    jsonl(localdir / "component-observations.jsonl", test)
    jsonl(localdir / "object-observations.jsonl", object_test)
    source_support = {}
    for key in ("site", "class", "volume", "carrier", "material", "motif", "preservation", "excavation_source"):
        source_support[key] = dict(Counter(str(r[key]) for r in test))
    summary = {"schema_version": "1.0", "synthetic": False, "status_class": "exploratory",
               "fresh_population": False, "eligibility": eligibility, "object_eligibility": object_eligibility,
               "variant_prediction": variants, "exact_frames": frames, "coverage_of_selected_targets": source_support,
               "access_event": event, "provenance": provenance(),
               "local_output_hashes": {p.name: sha(p) for p in localdir.iterdir()}}
    dump(outdir / "summary.json", summary)
    print(json.dumps({"primary": variants["primary"], "exact_frames": frames}, indent=2))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("action", choices=["source", "synthetic", "discovery", "confirmation"])
    args = ap.parse_args()
    {"source": source_layer, "synthetic": simulation, "discovery": discover, "confirmation": confirm}[args.action]()
