"""Recompute combined museum-number coverage after the dated museum corrections.

Reuse the verifier's independent normalization and number-token rules. Read the
current museum table and local CISI 2 final rows, without importing package join
or scoring code. The original combined-coverage.json remains untouched.
"""
import csv
import hashlib
import json
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

from check_counts import base_key, museum_numbers, usable, ws

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
LOCAL = ROOT / "data/raw/2026-10-13-data-round-1-verification"
INPUTS = {
    "lipi": ROOT / "data/normalized/lipi_observed_faces.jsonl",
    "website": ROOT / "data/normalized/indus_website_observed.jsonl",
    "census": ROOT / "data/raw/2026-10-06-evidence-census/synthesis/main-2026-10-07-v6/confirmed-object-joins.json",
    "museum": ROOT / "experiments/2026-10-13-museum-open-access/joins/join-table.csv",
    "cisi2_final": ROOT / "data/raw/2026-10-13-cisi2-basic-data-pilot/final.jsonl",
}


def main():
    payloads = {key: path.read_bytes() for key, path in INPUTS.items()}
    hashes = {key: hashlib.sha256(value).hexdigest() for key, value in payloads.items()}
    families, base_to_families = defaultdict(list), defaultdict(set)
    for line in payloads["lipi"].decode("utf-8").splitlines():
        face = json.loads(line)
        family = face["object_family_id"]
        families[family].append(face)
        key = base_key(ws(face["metadata"].get("cisi")))
        if key:
            base_to_families[key].add(family)
    website = [json.loads(line) for line in payloads["website"].decode("utf-8").splitlines() if line.strip()]
    website_keys = {ws(r.get("source_cisi")) for r in website if usable("MUSEUM", (r.get("metadata") or {}).get("MUSEUM"))}
    web_set = {family for family, faces in families.items() if any(ws(f["metadata"].get("cisi")) in website_keys for f in faces)}
    census_set = {r["family"] for r in json.loads(payloads["census"])}
    joins = list(csv.DictReader(payloads["museum"].decode("utf-8").splitlines()))
    museum_set = {r["family"] for r in joins if r["cls"] in {"exact", "confirmed"} and usable("accession", r["accession"])}
    pilot = {}
    status = Counter()
    for line in payloads["cisi2_final"].decode("utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        matches = base_to_families.get(row["cisi"], set())
        if not matches:
            status["no-lipi-family"] += 1
        elif len(matches) != 1 or len({base_key(ws(f["metadata"].get("cisi"))) for f in families[next(iter(matches))]}) != 1:
            status["ambiguous"] += 1
        else:
            family = next(iter(matches))
            assert family not in pilot
            pilot[family] = row
            status["one-family"] += 1
    pilot_all = {family for family, row in pilot.items() if museum_numbers(row["col4_museum"])}
    pilot_cell = {family for family in pilot_all if "[" not in pilot[family]["col4_museum"]}
    pilot_number = {family for family in pilot_all if any("[" not in token for token in museum_numbers(pilot[family]["col4_museum"]))}
    sets = {"older_website": web_set, "october_6_census": census_set, "museum_package": museum_set,
            "cisi2_including_brackets": pilot_all, "cisi2_without_brackets_in_cell": pilot_cell,
            "cisi2_any_definite_number": pilot_number}
    baseline = web_set | census_set
    stages = {"website_and_census": baseline, "museum_package_after": baseline | museum_set,
              "combined_including_brackets": baseline | museum_set | pilot_all,
              "combined_without_brackets_in_cell": baseline | museum_set | pilot_cell,
              "combined_any_definite_number": baseline | museum_set | pilot_number,
              "museum_first_over_common_baseline": museum_set - baseline,
              "museum_first_after_cisi2": museum_set - baseline - pilot_all,
              "cisi2_first_after_museum": pilot_all - baseline - museum_set,
              "first_number_from_both_packages": (museum_set & pilot_all) - baseline}
    assert len(families) == 4695
    assert all(value <= families.keys() for value in sets.values())
    for key, path in INPUTS.items():
        if hashlib.sha256(path.read_bytes()).hexdigest() != hashes[key]:
            raise RuntimeError(f"Input changed during read: {key}")
    result = {"date": "2026-10-13", "objects": len(families),
              "rules": {"combined_including_brackets": "At least one number-shaped token, including uncertain readings.",
                        "combined_without_brackets_in_cell": "At least one museum number and no bracket anywhere in its cell.",
                        "combined_any_definite_number": "At least one unbracketed number token, even if another token in the cell is bracketed."},
              "inputs": {key: {"path": path.relative_to(ROOT).as_posix(), "sha256": hashes[key]} for key, path in INPUTS.items()},
              "cisi2_join_dispositions": dict(status),
              "source_sets": {key: {"count": len(value), "families": sorted(value, key=int)} for key, value in sets.items()},
              "pairwise_overlaps": {f"{a} & {b}": {"count": len(sets[a] & sets[b])} for a, b in combinations(sets, 2)},
              "stages": {key: {"count": len(value), "percent": round(100 * len(value) / len(families), 2),
                               "families": sorted(value, key=int)} for key, value in stages.items()}}
    (OUT / "combined-coverage-post-fix.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    with (LOCAL / "combined-museum-coverage-post-fix.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["family"] + list(sets) + list(stages))
        writer.writeheader()
        for family in sorted(families, key=int):
            writer.writerow({"family": family, **{key: int(family in value) for key, value in (sets | stages).items()}})
    print(json.dumps({key: {"count": len(value), "percent": round(100 * len(value) / len(families), 2)} for key, value in stages.items()}, indent=2))


if __name__ == "__main__":
    main()
