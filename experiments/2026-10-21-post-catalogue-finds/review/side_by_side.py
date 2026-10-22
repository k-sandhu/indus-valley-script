"""Print merged rows and local families for one site, identity and context fields only.

Usage: python -I side_by_side.py <repo root> <site label in the local corpus> <site code>
The local corpus is read for identity fields only; sign, motif and size fields are not loaded.
"""
import csv, json, pathlib, sys
sys.stdout.reconfigure(encoding="utf-8")
root = pathlib.Path(sys.argv[1]); label = sys.argv[2]; code = sys.argv[3]
keep = ["excavation-idno", "area-section", "block-house", "room-grid", "depth", "period", "phase", "time", "material", "type"]
fams = {}
with open(root / "data/normalized/lipi_observed_faces.jsonl", encoding="utf-8") as fh:
    for line in fh:
        d = json.loads(line)
        if d["site"] != label:
            continue
        m = d["metadata"]
        fams.setdefault(d["object_family_id"], {"cisi": d["source_cisi"], **{k: m.get(k) for k in keep}})
rows = [r for r in csv.DictReader(open(root / "experiments/2026-10-21-post-catalogue-finds/matching/objects-merged.csv", encoding="utf-8")) if r["site_code"] == code]
for r in rows:
    print(r["row_id"], "|", r["season"][:16], "|", r["registration"], "|", r["other_numbers"][:30], "|", r["findspot"][:40], "|", r["depth_or_layer"][:30], "|", r["period_or_phase"][:12], "|", r["object_type"], r["material"][:12], "|", r["inscription_status"], "|", r["local_match"], r["local_family_ids"], r["match_basis"])
    print("     evidence:", r["match_evidence"][:300])
print("--- local families", len(fams))
for k, v in sorted(fams.items(), key=lambda x: int(x[0])):
    print(k, v)
