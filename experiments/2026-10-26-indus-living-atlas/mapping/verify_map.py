"""Check source preservation, geographic scope and offline atlas packaging."""

import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[3]
PACKAGE = Path(__file__).resolve().parents[1]


class References(HTMLParser):
    def __init__(self):
        super().__init__()
        self.references = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        for field in ("href", "src"):
            if field in values:
                self.references.append((tag, field, values[field]))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    out = (PACKAGE / args.out).resolve()
    if not out.is_relative_to(PACKAGE) or out.exists():
        raise ValueError("Choose a new owned verification output.")
    run = PACKAGE / args.run
    data = json.loads((run / "atlas-data.json").read_text(encoding="utf-8"))
    manifest = json.loads((run / "manifest.json").read_text(encoding="utf-8"))
    original = json.loads((ROOT / "experiments/2026-10-08-site-map-and-overview/data/map-data.json").read_text(encoding="utf-8"))
    checks = []

    def check(name, passed, detail=None):
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    check("All 115 inherited place entities preserved", len(data["sites"]) == 115 and {r["id"] for r in data["sites"]} == {r["id"] for r in original["sites"]})
    check("Exactly three inherited locations remain unplotted", {r["id"] for r in data["sites"] if r.get("lat") is None or r.get("lon") is None} == {"wattoowala", "luristan", "dilmun"})
    check("Only two declared coordinate overlays applied", {r["id"] for r in data["coordinate_changes"]} == {"surkotada", "farmana"})
    old = {r["id"]:r for r in original["sites"]}
    for row in data["sites"]:
        check(f"Original phases preserved: {row['id']}", row["phases"] == old[row["id"]].get("phases", []))
        check(f"Original locator preserved: {row['id']}", row["original_coordinate"]["lat"] == old[row["id"]].get("lat") and row["original_coordinate"]["lon"] == old[row["id"]].get("lon"))
        check(f"Source scope explicit: {row['id']}", "Inherited" in row["evidence_status"] and "quantified" in row["coordinate_precision"])
        if row.get("lat") is not None:
            check(f"Coordinate within geographic range: {row['id']}", -90 <= row["lat"] <= 90 and -180 <= row["lon"] <= 180)
        for p in row.get("phases", []):
            if isinstance(p.get("start_bce"), (int,float)) and isinstance(p.get("end_bce"), (int,float)):
                check(f"Chronology interval ordered: {row['id']} / {p.get('label')}", p["start_bce"] >= p["end_bce"])
    check("Town review includes 18 cases and 16 candidates", len(data["towns"]) == 18 and data["summary"]["living_towns"] == 16)
    check("No town promoted to demonstrated Indus-to-present continuity", not any(r.get("indus_to_present_demonstrated") for r in data["towns"]))
    check("Abandoned comparisons distinct from candidates", sum(r["category"] == "abandoned-indus-contrast" for r in data["towns"]) == 2)
    check("Actual modern river context includes the Indus and Ganges", {"Indus", "Ganges"}.issubset({r["properties"]["name"] for r in data["rivers"]["features"]}))
    for record in manifest["inputs"]:
        path = Path(record["path"])
        if not path.is_absolute():
            path = ROOT / path
        check(f"Input hash: {record['path']}", path.exists() and hashlib.sha256(path.read_bytes()).hexdigest() == record["sha256"])
    for record in manifest["outputs"]:
        path = PACKAGE / record["path"]
        check(f"Output hash: {record['path']}", path.exists() and hashlib.sha256(path.read_bytes()).hexdigest() == record["sha256"])
    current = PACKAGE / "mapping/current-data.js"
    check("Current viewer uses this exact data endpoint", current.read_bytes() == (run / "atlas-data.js").read_bytes())
    for source_set in (data["sources"], data["town_sources"]):
        check("Source identifiers unique within register", len({r["id"] for r in source_set}) == len(source_set))
    for name in ["index.html", "research.html"]:
        path = PACKAGE / name
        check(f"Viewer exists: {name}", path.exists())
        if not path.exists():
            continue
        parser_html = References()
        parser_html.feed(path.read_text(encoding="utf-8"))
        for tag, field, ref in parser_html.references:
            parts = urlsplit(ref)
            if parts.scheme or parts.netloc or not parts.path:
                if field == "src":
                    check(f"No external default resource: {name}/{ref}", not parts.scheme and not parts.netloc)
                continue
            target = (path.parent / unquote(parts.path)).resolve()
            check(f"Local reference: {name}/{ref}", target.exists())
    check("Leaflet full licence retained", "BSD 2-Clause License" in (PACKAGE / "mapping/vendor/leaflet/LICENSE").read_text(encoding="utf-8"))
    check("Map source provides accessible result buttons", 'class="place ' in (PACKAGE / "mapping/atlas.js").read_text(encoding="utf-8"))
    check("No semantic-scoring claim", data["scientific_confirmation"] is False)
    summary = {"passed": all(r["passed"] for r in checks), "checks": len(checks), "failures": sum(not r["passed"] for r in checks), "run": args.run, "scope": "Source preservation, hashes and local packaging; browser interaction is checked separately.", "results": checks}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({k:summary[k] for k in ["passed","checks","failures","run"]}))
    raise SystemExit(0 if summary["passed"] else 1)


if __name__ == "__main__":
    main()
