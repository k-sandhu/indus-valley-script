"""Verify the atlas against its pinned inputs and rendered assets."""
from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import json
import math
from pathlib import Path
import xml.etree.ElementTree as ET

from PIL import Image

HERE = Path(__file__).resolve().parent
BASE = HERE.parents[1]
ROOT = BASE.parents[1]


def read(path):
    return json.loads(path.read_text(encoding="utf8"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", default="run-v7")
    args = parser.parse_args()
    manifest_path = HERE / f"manifest-{args.run}.json"
    atlas = read(manifest_path)
    checks = []

    def check(label, passed, detail=None):
        checks.append({"check": label, "passed": bool(passed), "detail": detail})

    check("validated scientific register", read(BASE / "run-v3/validation.json")["status"] == "pass")
    check("23 distinct figures", atlas["figure_count"] == 23 and len({r["id"] for r in atlas["figures"]}) == 23)
    check("preserved input endpoint", atlas["data_endpoint"] == "run-v3")
    check("no new measurements or confirmation access", atlas["new_archaeological_measurements"] == 0 and not atlas["confirmation_access"])
    check("no copied source imagery", atlas["third_party_images_reproduced"] == 0)
    check("build code hash", sha(HERE / "build_atlas.py") == atlas["code_sha256"])
    for row in atlas["input_manifest"]:
        p = Path(row["path"])
        check("input " + p.name, p.exists() and p.stat().st_size == row["bytes"] and sha(p) == row["sha256"], str(p))

    observations = {r["id"]: r for r in read(BASE / "run-v3/observations.json")}
    source_index = {r["source_id"]: r for r in read(BASE / "run-v3/sources.json")}
    towns = {r["town"]: r for r in read(BASE / "run-v3/towns.json")}
    figures = {r["figure"]: r for r in atlas["figures"]}
    asset_count = 0
    for number, figure in figures.items():
        check(f"figure {number} source relations", bool(figure["sources"]) and all(oid in observations for oid in figure["observation_ids"]))
        for oid in figure["observation_ids"]:
            observation = observations[oid]
            matches = [s for s in figure["sources"] if s["source_id"] == observation["source_id"]]
            check(f"figure {number} locator {oid}", any(observation["locator"] in s.get("locators", []) for s in matches))
        for source in figure["sources"]:
            canonical = source_index.get(source["source_id"])
            if canonical:
                check(f"figure {number} exact source metadata {source['source_id']}", all(source.get(k) == canonical.get(k) for k in ["title", "url", "sha256"]))
            check(f"figure {number} source locator {source['source_id']}", bool(source.get("locator") or source.get("locators")))
        check(f"figure {number} PNG and SVG", {a["format"] for a in figure["assets"]} == {"png", "svg"})
        for asset in figure["assets"]:
            asset_count += 1
            p = Path(asset["physical_path"])
            check(f"figure {number} {asset['format']} local D path", p.resolve().is_relative_to(Path("D:/projects/indus_valley_script")))
            check(f"figure {number} {asset['format']} hash", p.exists() and sha(p) == asset["sha256"] and p.stat().st_size == asset["bytes"])
            if asset["format"] == "png":
                with Image.open(p) as im:
                    check(f"figure {number} publication PNG", im.size == (3420, 2160) and all(abs(v - 300) < .01 for v in im.info.get("dpi", [])) and len(im.info.get("dpi", [])) == 2)
            else:
                tree = ET.parse(p)
                check(f"figure {number} SVG parses", tree.getroot().tag.endswith("svg"))
        check(f"figure {number} outside text", not next(r["outside_canvas_text"] for r in atlas["text_bounds"] if r["figure"] == number))
    check("46 figure exports", asset_count == 46)

    for town, point in figures[1]["data_values"].items():
        original = towns[town]["axis_horizon_register"]
        check("inherited coordinate " + town, all(point[k] == original[k] for k in point))
        check("inherited coordinate hash " + town, sha(ROOT / point["source_path"]) == point["source_sha256"])
    domain = figures[2]["data_values"]
    display_names = {"location_setting":"Setting", "occupation_chronology":"Chronology", "settlement_extent":"Extent", "excavation_coverage":"Excavation", "layout_and_access":"Layout / access", "building_inventory":"Buildings", "construction_materials":"Materials", "water_and_sanitation":"Water / drainage", "incremental_alteration":"Local change", "replanning_and_retention":"Replanning", "documentary_context":"Documents", "quantities_and_scope":"Count denominator", "phase_information":"Phase joins"}
    check("domain labels follow named keys", domain["domain_display_labels"] == [display_names[d] for d in domain["domains"]])
    check("domain index exact cells", domain["matrix"] == [[domain["codes"][towns[t]["domains"][d]["status"]] for d in domain["domains"]] for t in domain["towns"]])
    counts = collections.Counter(v for row in domain["matrix"] for v in row)
    check("156 domain cells, status counts 98/40/18", counts == {0: 98, 1: 40, 2: 18})
    expected = {t: dict(collections.Counter(r["module"] for r in observations.values() if t in r.get("towns", [r["town"]]))) for t in domain["towns"]}
    check("town assertion counts", figures[3]["data_values"] == expected)
    check("287 unique assertions and core links", len(observations) == 287 and sum(sum(x.values()) for x in expected.values()) == 287)
    durations = {r["observation_id"]: r for r in read(BASE / "run-v3/duration-spans.json")}
    check("Dholavira source bounds", figures[6]["data_values"]["bounds"] == [[observations[oid]["phase"], durations[oid]["start_bce"], durations[oid]["end_bce"]] for oid in figures[6]["observation_ids"]])
    check("continuous occupation not assumed", not figures[6]["data_values"]["continuity_assumed"])
    with (BASE / "modules/western/mohenjo-daro-residential-series.csv").open(encoding="utf8", newline="") as handle:
        residences = list(csv.DictReader(handle))
    check("five original residence rows", figures[10]["data_values"] == residences and len(residences) == 5)
    context = read(BASE / "modules/inscriptions/context-table-summary.json")
    check("Dholavira raw stage labels", figures[12]["data_values"]["all_raw_labels"] == context["stage_raw_counts"])
    check("Dholavira raw inscription flags", figures[13]["data_values"]["raw_flags"] == context["inscription_raw_counts"])
    check("225-row denominators", sum(x[1] for x in figures[12]["data_values"]["five_groups"]) == sum(x[1] for x in figures[13]["data_values"]["groups"]) == context["rows"] == 225)
    check("detailed context hash", sha(Path(context["detailed_physical_path"])) == context["detailed_sha256"])
    prior = {r["id"]: r for r in read(BASE / "modules/inscriptions/prior-results.json")["results"]}
    expected_clump = prior["PR-04"]["values"]["/manufacture_group_by_association"]
    check("22-tablet source matrix", figures[14]["data_values"]["matrix"] == [[r[k] for k in ["clump", "nearby", "scattered"]] for r in expected_clump])
    check("Lothal populations unreconciled", not figures[15]["data_values"]["inventories_reconciled"])
    for card in figures[17]["data_values"]["cards"]:
        p = prior[card[-1]]
        check("frozen prior " + p["id"], sha(ROOT / p["exact_output"]) == p["sha256"] and not p["fresh_confirmation_here"])
    synthetic = read(BASE / "synthetic-v1/results.json")
    check("synthetic power original rows", figures[19]["data_values"] == synthetic["power"])
    for r in figures[18]["data_values"]:
        check("synthetic Q4 " + str(r["offset_degrees"]), abs(r["global_q4"] - abs(math.cos(math.radians(2 * r["offset_degrees"])))) < 1e-12 and all(abs(v-1) < 1e-12 for v in r["local_q4"]))
    for r in figures[19]["data_values"]:
        n, k, p = r["independent_non_tied_pairs"], r["critical_positive_pairs"], r["true_positive_pair_probability"]
        exact = sum(math.comb(n, j) * p**j * (1-p)**(n-j) for j in range(k, n+1))
        check("exact binomial power " + str((n,p)), abs(exact-r["power"]) < 1e-12)
    ratios = read(BASE / "shape-comparison-v1/results.json")
    check("six original dimension-pair rows", figures[23]["data_values"] == ratios["rows"] and ratios["passed"] and ratios["source_measurements_new"] == 0)
    check("ratio uncertainty retained", all(r["ratio_uncertainty"] is None and r["missing_uncertainty_reason"] for r in figures[23]["data_values"]))

    result = {"status":"pass" if all(c["passed"] for c in checks) else "fail", "checks":checks, "checks_count":len(checks), "failed":[c for c in checks if not c["passed"]], "manifest_path":str(manifest_path), "manifest_sha256":sha(manifest_path), "output_root":atlas["output_root"], "scope":"Input consistency, derivation checks and asset integrity; archaeological source interpretation receives manual review."}
    (HERE / f"validation-{args.run}.json").write_text(json.dumps(result, ensure_ascii=False, indent=2)+"\n", encoding="utf8")
    print(json.dumps({k:result[k] for k in ["status","checks_count","failed"]}, ensure_ascii=False))
    raise SystemExit(0 if result["status"] == "pass" else 1)


if __name__ == "__main__":
    main()
