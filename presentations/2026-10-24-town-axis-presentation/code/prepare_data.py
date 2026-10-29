"""Prepare the presentation's aggregate evidence without copying source imagery."""
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
STUDY = ROOT / "experiments/2026-10-24-q1032-town-axis-register"
PACKAGE = Path(__file__).resolve().parents[1]
LOCAL = Path("D:/projects/indus_valley_script/data/raw/2026-10-24-town-axis-presentation")


def read(relative):
    path = ROOT / relative
    payload = path.read_bytes()
    inputs.append({"logical_path": relative, "sha256": hashlib.sha256(payload).hexdigest(), "bytes": len(payload)})
    return json.loads(payload)


inputs = []
prefix = "experiments/2026-10-24-q1032-town-axis-register/"
coverage = read(prefix + "run-v5/coverage.json")
towns = read(prefix + "run-v5/town-axis-table.json")["towns"]
wanzke = read(prefix + "run-v5/published-wanzke.json")
horizons = read(prefix + "horizon-repair-v1/horizons.json")
geodesic = read(prefix + "geodesic-check.json")
storage = read("experiments/2026-10-24-storage-migration/summary.json")
picks = read(prefix + "new-observations.json")
measure_path = ROOT / prefix / "run-v5/measurements.jsonl"
measure_bytes = measure_path.read_bytes()
inputs.append({"logical_path": prefix + "run-v5/measurements.jsonl", "sha256": hashlib.sha256(measure_bytes).hexdigest(), "bytes": len(measure_bytes)})
new_lines = [r for line in measure_bytes.decode("utf-8").splitlines() if (r := json.loads(line))["measurement_id"].startswith("new-surkotada:")]

labels = {
    "mohenjo-daro": "Mohenjo-daro", "chanhu-daro": "Chanhu-daro",
    "rakhigarhi": "Rakhigarhi", "dholavira": "Dholavira", "harappa": "Harappa",
    "kalibangan": "Kalibangan", "lothal": "Lothal", "surkotada": "Surkotada",
    "banawali": "Banawali", "kanmer": "Kanmer", "shikarpur": "Shikarpur",
}
required = [{
    "town": labels[t["town"]], "image_lines": t["imagery_lines"],
    "plan_lines": t["plan_lines"], "horizon": "Present" if t["missing"]["horizon"] is None else "Missing",
    "phase_assertions": len(t["dated_part_assertions"]),
} for t in towns if t["required"]]

gap_names = [
    ("two_independent_imagery_sources", "Validated independent imagery"),
    ("horizon_sigma", "Horizon uncertainty budget"),
    ("layout_boundary", "Dated construction boundary"),
    ("bayesian_start", "Bayesian construction start"),
    ("exact_wall_coordinate", "Surveyed wall coordinate"),
    ("plan_true_north", "Plan tied to true north"),
    ("horizon", "Usable modern horizon"),
    ("coordinates", "Resolved site coordinate"),
]
gaps = [{"field": key, "label": label, "count": sum(t["missing"].get(key) is not None for t in towns)} for key, label in gap_names]
assert sum(g["count"] for g in gaps) == coverage["missing_field_rows"] == 218
assert len(required) == 11

md_parts = ["Moneer N-S 5", "Moneer N-S 6", "HR First Street"]
md = []
for part in md_parts:
    row = next(r for r in wanzke["rows"] if r["town"] == "mohenjo-daro" and r["part"] == part)
    md.append({"part": part, "gon": row["reported_deviation_gon"], "deg": row["reported_deviation_gon"] * .9,
               "printed_page": row["printed_page"], "pdf_page_index": row["pdf_page_index"]})

data = {
    "date": "24 October 2026", "coverage": coverage, "required_towns": required,
    "mohenjo_daro": md, "gaps": gaps, "horizons": horizons["towns"],
    "surkotada_geodesic": geodesic["rows"], "surkotada_picks": picks, "surkotada_lines": new_lines,
    "storage": storage,
    "radiocarbon": [
        {"lab": "TF-1297", "bp": 3635, "sigma": 95, "printed_page": 579},
        {"lab": "TF-1311", "bp": 3625, "sigma": 90, "printed_page": 580},
        {"lab": "TF-1294", "bp": 3620, "sigma": 95, "printed_page": 579},
        {"lab": "TF-1307", "bp": 3510, "sigma": 105, "printed_page": 579},
    ],
    "lothal": [
        {"source": "Esri", "deviation_deg": -1.88, "reported_sigma_deg": .30},
        {"source": "Sentinel-2", "deviation_deg": .19, "reported_sigma_deg": .30},
    ],
    "scope": "Presentation of existing observations. No new scientific test, source acquisition or confirmation population.",
}

# Verify the rounded display values against the earlier comparison and the
# source-linked date assertions. The primary scans remain local-only.
comparison = read("experiments/2026-10-21-town-orientations-verification/comparison-v3/comparison.json")
lothal = next(r for r in comparison["bearings"]["rows"] if r["slug"] == "lothal")
assert round(lothal["theirs"], 2) == data["lothal"][0]["deviation_deg"]
assert round(lothal["ours"], 2) == data["lothal"][1]["deviation_deg"]
rc_relative = prefix + "run-v5/radiocarbon.jsonl"
rc_path = ROOT / rc_relative
rc_bytes = rc_path.read_bytes()
inputs.append({"logical_path": rc_relative, "sha256": hashlib.sha256(rc_bytes).hexdigest(), "bytes": len(rc_bytes)})
rc_rows = [json.loads(line) for line in rc_bytes.decode().splitlines()]
for displayed in data["radiocarbon"]:
    source = next(r["values"] for r in rc_rows if r["town"] == "surkotada" and r["values"].get("lab_code") == displayed["lab"] and r["compilation"] == "verify-dating")
    assert (source["conventional_age_bp"], source["error_bp"]) == (displayed["bp"], displayed["sigma"])
    assert source["phase_label"] == "Period IC"
for relative in [
    prefix + "REPORT.md", "LOCAL_STORAGE.md",
    "research/literature/sources/jansen_urban1987_interim2_govscan_77275.pdf",
    "data/raw/2026-10-21-town-axes/plan-B/downloads/joshi1990_surkotada_masi87.pdf",
    "data/raw/2026-10-21-town-axes/dating/radiocarbon-journal/TF-X.pdf",
]:
    source_path = ROOT / relative
    source_bytes = source_path.read_bytes()
    inputs.append({"logical_path": relative, "sha256": hashlib.sha256(source_bytes).hexdigest(), "bytes": len(source_bytes)})

if not LOCAL.parent.is_dir() or (ROOT / "data/raw").resolve() != Path("D:/projects/indus_valley_script/data/raw").resolve():
    raise RuntimeError("D: storage or the data/raw junction is unavailable")
LOCAL.mkdir(exist_ok=True)
for name in ("build", "output"):
    (LOCAL / name).mkdir(exist_ok=True)
dest = LOCAL / "build/evidence.json"
dest.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
manifest = {
    "inputs": inputs, "prepared_data_sha256": hashlib.sha256(dest.read_bytes()).hexdigest(),
    "prepared_data_logical_path": "data/raw/2026-10-24-town-axis-presentation/build/evidence.json",
    "prepared_data_physical_path": str(dest),
    "raw_images_embedded": False, "new_sources": 0, "coverage_changes": 0,
}
(PACKAGE / "input-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"data": str(dest), "required": len(required), "gaps": gaps, "geodesic_keys": list(geodesic["rows"][0])}))
