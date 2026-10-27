"""Record a fresh, hash-checked local delivery without changing research endpoints."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess

PACKAGE = Path(__file__).resolve().parents[1]
ROOT = PACKAGE.parents[1]
RAW = Path("D:/projects/indus_valley_script/data/raw/2026-10-26-indus-living-atlas/qa")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    output = (PACKAGE / args.out).resolve()
    if not output.is_relative_to(PACKAGE) or output.exists():
        raise ValueError("Choose a new owned delivery record.")
    records = []
    excluded = []
    for path in sorted(PACKAGE.rglob("*")):
        if not path.is_file():
            continue
        if "__pycache__" in path.parts:
            excluded.append(path.relative_to(ROOT).as_posix())
            continue
        records.append({"path":path.relative_to(ROOT).as_posix(),"bytes":path.stat().st_size,"sha256":sha(path)})
    attempts = [ROOT / "knowledge/registry/attempts" / name for name in ["INDUS-LIVING-ATLAS-2026-10-26.json","INDUS-CITY-3D-2026-10-26.json","INDUS-MARKER-CONTINUITY-2026-10-26.json","SOUTH-ASIA-LIVING-TOWNS-2026-10-26.json"]]
    for path in attempts:
        records.append({"path":path.relative_to(ROOT).as_posix(),"bytes":path.stat().st_size,"sha256":sha(path)})
    raw = [{"logical_path":"data/raw/2026-10-26-indus-living-atlas/qa/"+p.name,"physical_path":p.as_posix(),"bytes":p.stat().st_size,"sha256":sha(p),"handling":"local-only"} for p in sorted(RAW.iterdir()) if p.is_file()]
    # Verify current selected data and reader against their frozen outputs.
    assert (PACKAGE / "mapping/current-data.js").read_bytes() == (PACKAGE / "mapping/run-v2/atlas-data.js").read_bytes()
    reader = json.loads((PACKAGE / "reader/run-v2/manifest.json").read_text(encoding="utf-8"))
    assert sha(PACKAGE / "research.html") == reader["output"]["sha256"]
    for record in reader["inputs"]:
        assert sha(ROOT / record["path"]) == record["sha256"]
    town = PACKAGE / "living-towns/towns.json"
    assert sha(town) == "f6a8d5075b58090245cc2c2bb696bc01700e9d778b586b30a89441762ae08b48"
    assert sha(PACKAGE / "living-towns/sources.json") == "9b333d2d04442571764419b4befbe0b9db2f9f9da46a77f5d40f894f13200711"
    exported = json.loads((RAW / "filtered-places-v1.geojson").read_text(encoding="utf-8"))
    assert len(exported["features"]) == 100
    assert sum(f["properties"]["layer"] == "town" for f in exported["features"]) == 16
    assert len(exported["metadata"]["unlocated"]) == 1
    selected_checks = ["qa/map-verification-v2.json","qa/browser-verification-v1.json","qa/modern-basemap-v1.json","reconstruction/verification-v5.json","reconstruction/browser-verification-v5.json","continuity/verification-v2.json","living-towns/validation-v4.json"]
    for relative in selected_checks:
        record = json.loads((PACKAGE / relative).read_text(encoding="utf-8-sig"))
        if "passed" in record:
            assert record["passed"] is True, relative
        else:
            assert record.get("summary",{}).get("failed") == 0, relative
    result = {"schema_version":"1.0","created_utc":datetime.now(timezone.utc).isoformat(),"status":"verified-local-delivery","scope":"Own atlas files, source registers, selected software and source checks and local QA artifacts; no independent archaeological review.","selected_map":"mapping/run-v2","selected_models":"reconstruction/run-v5","selected_reader":"reader/run-v2","files":records,"excluded_runtime_cache":excluded,"local_qa_artifacts":raw,"assertions":["Current map payload equals frozen map run-v2","Readable page and its report inputs match reader run-v2","Final town data and source hashes match contributor handoff","Filtered GeoJSON export contains 100 point features, including 16 modern candidates, and one unlocated match","All seven selected package and software verification records pass"],"git_status_command":"git status --short -- experiments/2026-10-26-indus-living-atlas knowledge/registry/attempts/INDUS-LIVING-ATLAS-2026-10-26.json knowledge/registry/attempts/INDUS-CITY-3D-2026-10-26.json knowledge/registry/attempts/INDUS-MARKER-CONTINUITY-2026-10-26.json knowledge/registry/attempts/SOUTH-ASIA-LIVING-TOWNS-2026-10-26.json"}
    output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"status":result["status"],"files":len(records),"local_qa_artifacts":len(raw),"bytes":sum(r["bytes"] for r in records),"assertions":len(result["assertions"])}))


if __name__ == "__main__":
    main()
