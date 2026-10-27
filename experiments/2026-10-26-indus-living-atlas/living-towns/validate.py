"""Check reference integrity and chronological coding; not archaeological proof."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

HERE = Path(__file__).resolve().parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="validation-v1.json")
    args = parser.parse_args()
    out = HERE / args.out
    if out.exists():
        raise SystemExit(f"Refusing existing result: {out}")
    towns = json.loads((HERE / "towns.json").read_text(encoding="utf-8"))
    source_data = json.loads((HERE / "sources.json").read_text(encoding="utf-8"))
    sources = source_data["sources"]
    records = towns["records"]
    checks = []

    def check(name, condition, details=None):
        checks.append(dict(name=name, passed=bool(condition), details=details))

    check("schema version", towns["schema_version"] == "1.0")
    check("protocol planned candidate coverage", 16 <= len(records) <= 20)
    check("unique town IDs", len({t["id"] for t in records}) == len(records))
    check("unique source IDs", len({s["id"] for s in sources}) == len(sources))
    check("five country coverage", {t["country"] for t in records} == {"India", "Pakistan", "Nepal", "Sri Lanka", "Bangladesh"})
    check("two explicit abandoned contrasts", sum(t["category"] == "abandoned-indus-contrast" for t in records) == 2)
    byid = {s["id"]: s for s in sources}
    allowed_status = {"documented-sequence-with-hiatus", "long-sequence-continuity-unproven", "continuity-asserted-not-demonstrated",
                      "nearby-modern-settlement", "later-origin-no-indus-overlap", "archaeological-or-sacred-place-not-town-continuity",
                      "abandoned-ancient-city", "unresolved"}
    required = {"id", "name", "country", "lat", "lon", "coordinate_precision", "earliest_evidence_bce", "indus_overlap",
                "continuity_status", "spatial_relation", "summary", "source_ids", "gaps", "modern_civic_identity", "evidence_place",
                "urban_foundation", "known_hiatuses", "indus_to_present_demonstrated", "earlier_regional_evidence", "occupation_spans"}
    for t in records:
        tid = t["id"]
        check(f"{tid}: required fields", required <= t.keys())
        check(f"{tid}: approximate South Asia coordinate", all(math.isfinite(t[x]) for x in ("lat", "lon")) and 5 <= t["lat"] <= 37 and 60 <= t["lon"] <= 93)
        check(f"{tid}: explicit coarse precision", t["coordinate_precision"]["meters"] >= 2000 and bool(t["coordinate_precision"]["basis"]))
        check(f"{tid}: known continuity class", t["continuity_status"] in allowed_status)
        check(f"{tid}: source links resolve", bool(t["source_ids"]) and all(x in byid for x in t["source_ids"]))
        check(f"{tid}: explicit spatial and temporal gaps", bool(t["spatial_relation"]) and bool(t["gaps"]) and bool(t["known_hiatuses"]))
        d = t["earliest_evidence_bce"]
        a, b = d["earliest"], d["latest"]
        check(f"{tid}: date interval", (a is None and b is None) or (isinstance(a, int) and isinstance(b, int) and a >= b >= 1))
        check(f"{tid}: date basis", all(bool(d.get(x)) for x in ("date_label", "basis", "kind")))
        check(f"{tid}: no unsupported Indus-to-present certification", t["indus_to_present_demonstrated"] is False)
        for s in t["occupation_spans"]:
            check(f"{tid}: valid occupation span", isinstance(s["start_bce"], int) and isinstance(s["end_bce"], int) and s["start_bce"] >= s["end_bce"] > 0 and bool(s["scope"]))
        for label, bounds in [("mature_2600_1900", (2600, 1900)), ("late_1900_1300", (1900, 1300))]:
            state = t["indus_overlap"][label]
            check(f"{tid}: {label} enum", state in {"yes", "no", "uncertain"})
            overlap = any(s["start_bce"] >= bounds[1] and s["end_bce"] <= bounds[0] for s in t["occupation_spans"])
            if state == "yes":
                check(f"{tid}: {label} positive supported by local span", overlap)
            if state == "no":
                check(f"{tid}: {label} no contradicting local span", not overlap)
        for r in t["earlier_regional_evidence"]:
            check(f"{tid}: regional source links resolve", bool(r["source_ids"]) and all(x in byid for x in r["source_ids"]))
            check(f"{tid}: regional spatial relation explicit", bool(r["relationship"]))
    for s in sources:
        sid = s["id"]
        check(f"{sid}: bibliography fields", all(s.get(x) for x in ("title", "authors", "url", "accessed", "locator", "access_depth", "kind", "rights")))
        check(f"{sid}: date or explicit unknown", s["year"] is None or 1800 <= s["year"] <= 2026)
        check(f"{sid}: stable public URL", urlparse(s["url"]).scheme == "https" and "token=" not in s["url"].lower() and "signature=" not in s["url"].lower())
        check(f"{sid}: explicit rights", s["rights"]["status"] in {"rights-unverified", "explicit-license", "mixed-assets"} and bool(s["rights"]["notice"]))
    acquired = []
    for manifest in ("acquisition-v1.json", "acquisition-v2.json"):
        p = HERE / manifest
        check(f"{manifest}: exists", p.is_file())
        if not p.is_file():
            continue
        for r in json.loads(p.read_text(encoding="utf-8"))["records"]:
            check(f'{manifest}/{r["source_id"]}: source exists', r["source_id"] in byid)
            if r["status"] == "retrieved":
                f = Path(r["physical_path"])
                check(f'{manifest}/{f.name}: physical file hash', f.is_file() and f.stat().st_size == r["bytes"] and digest(f) == r["sha256"])
                check(f'{manifest}/{f.name}: D local-only path', f.as_posix().lower().startswith("d:/projects/indus_valley_script/data/raw/2026-10-26-indus-living-atlas/living-towns/") and r["handling"] == "local-only")
                acquired.append(r)
    # Explicit high-risk joins must retain their distinctions, independent of row counts.
    lookup = {t["id"]: t for t in records}
    check("Harappa modern overlap retained", "overlaps" in lookup["LT-04"]["spatial_relation"])
    check("Rupnagar's hiatus retained", any("1400–1000" in x for x in lookup["LT-11"]["known_hiatuses"]))
    check("Patna's sampled-area hiatus retained", any("600–1600" in x for x in lookup["LT-08"]["known_hiatuses"]))
    check("Srinagar not dated from Burzahom", lookup["LT-10"]["earliest_evidence_bce"]["earliest"] is None and len(lookup["LT-10"]["earlier_regional_evidence"]) > 0)
    check("Lumbini temple not dated from nearby village", lookup["LT-13"]["earliest_evidence_bce"]["earliest"] == 600 and bool(lookup["LT-13"]["earlier_regional_evidence"]))
    check("Rajgir uncalibrated result not a calendar date", lookup["LT-09"]["earliest_evidence_bce"]["earliest"] is None)
    check("all source IDs used", set(byid) == {sid for t in records for sid in t["source_ids"]})
    inspection = json.loads((HERE / "witness-inspection-v2.json").read_text(encoding="utf-8"))
    check("primary page fragments pass corrected locators", all(c["fragments_present"] for c in inspection["checks"]))
    check("failed first locator check preserved", not all(c["fragments_present"] for c in json.loads((HERE / "witness-inspection-v1.json").read_text(encoding="utf-8"))["checks"]))
    files = ["PROTOCOL.md", "towns.json", "sources.json", "towns.schema.json", "TABLE.md", "REPORT.md", "DATA-UPDATE.md", "RETROSPECTIVE.md", "build_register.py", "validate.py", "acquisition-v1.json", "acquisition-v2.json", "witness-inspection-v1.json", "witness-inspection-v2.json"]
    for name in files:
        check(f"package file: {name}", (HERE / name).is_file())
    result = dict(schema_version="1.0", task="living-town-register-validation", created_at=datetime.now(timezone.utc).isoformat(),
                  scientific_status="source-review; internal checks do not authenticate continuous settlement",
                  passed=all(c["passed"] for c in checks), checks_passed=sum(c["passed"] for c in checks), checks_total=len(checks),
                  summary=dict(records=len(records), living_candidates=sum(t["category"] == "living-town-candidate" for t in records),
                               sources=len(sources), local_witnesses=len(acquired),
                               continuity_classes=dict(Counter(t["continuity_status"] for t in records)),
                               demonstrated_indus_to_present=sum(t["indus_to_present_demonstrated"] for t in records)),
                  inputs={name: digest(HERE / name) for name in files if (HERE / name).is_file()}, checks=checks)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: result[k] for k in ("passed", "checks_passed", "checks_total", "summary")}))
    for c in checks:
        if not c["passed"]:
            print("FAIL:", c["name"])
    raise SystemExit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
