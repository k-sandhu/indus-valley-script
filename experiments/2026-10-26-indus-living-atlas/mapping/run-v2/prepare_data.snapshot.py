"""Build a new atlas evidence snapshot without altering earlier map endpoints."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PACKAGE = Path(__file__).resolve().parents[1]
OLD = ROOT / "experiments/2026-10-08-site-map-and-overview/data/map-data.json"
REGISTER = ROOT / "experiments/2026-10-24-q1032-town-axis-register/run-v5/town-axis-table.json"
VENDOR = ROOT / "experiments/2026-10-12-satellite-prospection/atlas/vendor"


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path: Path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", required=True, help="New package-relative snapshot directory")
    args = parser.parse_args()
    out = (PACKAGE / args.run).resolve()
    if not out.is_relative_to(PACKAGE) or out.exists():
        raise ValueError("Choose a new snapshot inside the owned package.")
    original = read(OLD)
    register = read(REGISTER)
    by_town = {row["town"]: row for row in register["towns"]}
    overlays = read(PACKAGE / "mapping/overlays.json")
    sources = read(PACKAGE / "mapping/sources.json")
    towns_file = PACKAGE / "living-towns/towns.json"
    living = read(towns_file) if towns_file.exists() else {"records": []}
    living_sources = PACKAGE / "living-towns/sources.json"
    sites = []
    changes = []
    for prior in original["sites"]:
        row = json.loads(json.dumps(prior))
        row["layer"] = "find-site"
        row["coordinate_precision"] = "Not quantified in this map; inspect the cited coordinate source."
        row["evidence_status"] = "Inherited 8 October source register; individual sources were not all reopened."
        row["original_coordinate"] = {"lat": row.get("lat"), "lon": row.get("lon"), "kind": row.get("coord_kind")}
        row["coordinate_assertions"] = []
        if row["id"] in by_town:
            town = by_town[row["id"]]
            row["coordinate_assertions"] = town.get("coordinate_candidates", [])
            row["architectural_register"] = "../2026-10-24-q1032-town-axis-register/REPORT.md"
            row["architectural_coverage"] = {k: town.get(k) for k in ["imagery_lines", "plan_lines", "radiocarbon_assertions"]}
        rule = overlays.get("sites", {}).get(row["id"], {})
        row["warnings"] = rule.get("warnings", [])
        row["model_id"] = rule.get("model_id")
        row["official_source_ids"] = rule.get("source_ids", [])
        if rule.get("use_register_coordinate"):
            current = by_town[row["id"]]["coordinate"]
            old = [row["lat"], row["lon"]]
            row["lat"], row["lon"] = current["lat"], current["lon"]
            row["coordinate_update"] = current
            row["coord_note"] = current["basis"]
            changes.append({"id": row["id"], "before": old, "after": [row["lat"], row["lon"]], "basis": current})
        # Rechecked heritage ranges are additional assertions. Original phasing is retained.
        row["reviewed_ranges"] = rule.get("reviewed_ranges", [])
        sites.append(row)
    countries_file = VENDOR / "natural-earth/ne_110m_admin_0_countries.geojson"
    countries = read(countries_file)
    # Preserve geometry, retain only fields needed for geographic orientation.
    geography = {"type": "FeatureCollection", "features": [{"type": "Feature", "properties": {"name": f["properties"].get("NAME", "")}, "geometry": f["geometry"]} for f in countries["features"]]}
    river_record = PACKAGE / "mapping/river-acquisition-v2.json"
    rivers = {"type": "FeatureCollection", "features": []}
    if river_record.exists():
        river_path = Path(read(river_record)["physical_path"])
        if digest(river_path) != read(river_record)["sha256"]:
            raise ValueError("River source hash differs from the preserved witness.")
        rivers = {"type": "FeatureCollection", "features": [{"type": "Feature", "properties": {"name": f["properties"].get("name", "")}, "geometry": f["geometry"]} for f in read(river_path)["features"]]}
    manifest_paths = [OLD, REGISTER, PACKAGE / "PROTOCOL.md", Path(__file__), PACKAGE / "mapping/overlays.json", PACKAGE / "mapping/sources.json", countries_file]
    if towns_file.exists():
        manifest_paths.append(towns_file)
    if living_sources.exists():
        manifest_paths.append(living_sources)
    if river_record.exists():
        manifest_paths.extend([river_record, river_path])
    data = {"schema_version": "1.0", "created_date": "2026-10-26", "scientific_confirmation": False,
            "summary": {"find_sites": len(sites), "located_find_sites": sum(r.get("lat") is not None and r.get("lon") is not None for r in sites), "living_towns": sum(r.get("category") == "living-town-candidate" for r in living.get("records", [])), "town_review_records": len(living.get("records", [])), "coordinate_overlays": len(changes)},
            "scope": "Regional find-site reference points and present-day town anchors; no surveyed city footprint or continuous-occupation inference.",
            "sites": sites, "towns": living.get("records", []), "sources": sources["sources"],
            "town_sources": read(living_sources).get("sources", []) if living_sources.exists() else [],
            "geography": geography, "rivers": rivers, "coordinate_changes": changes}
    out.mkdir(parents=True)
    (out / "prepare_data.snapshot.py").write_bytes(Path(__file__).read_bytes())
    (out / "overlays.snapshot.json").write_bytes((PACKAGE / "mapping/overlays.json").read_bytes())
    (out / "sources.snapshot.json").write_bytes((PACKAGE / "mapping/sources.json").read_bytes())
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    (out / "atlas-data.json").write_text(payload + "\n", encoding="utf-8")
    (out / "atlas-data.js").write_text("window.INDUS_ATLAS=" + payload.replace("</", "<\\/") + ";\n", encoding="utf-8")
    inputs = [{"path": p.relative_to(ROOT).as_posix() if p.is_relative_to(ROOT) else str(p), "bytes": p.stat().st_size, "sha256": digest(p)} for p in manifest_paths]
    manifest = {"schema_version": "1.0", "inputs": inputs, "outputs": [{"path": p.relative_to(PACKAGE).as_posix(), "bytes": p.stat().st_size, "sha256": digest(p)} for p in sorted(out.iterdir())], "coordinate_changes": changes, "living_towns_included": towns_file.exists(), "new_raw_acquisitions": len(list((PACKAGE / "mapping").glob("river-acquisition*.json")))}
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"run": args.run, **data["summary"], "living_towns_included": towns_file.exists()}))


if __name__ == "__main__":
    main()
