"""Print the current imagery and plan-library entries for one town slug."""
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
base = Path("experiments/2026-10-21-town-orientations-verification/infra-v1")
slug = sys.argv[1]
man = json.loads((base / "imagery-manifest-v1.json").read_text(encoding="utf-8"))
lib = json.loads((base / "plan-library-v1.json").read_text(encoding="utf-8"))
print("manifest created", man["created_utc"], "| library created", lib["created_utc"])
for t in man["towns"]:
    if t["slug"] == slug:
        comp = t.get("composite") or {}
        print("imagery:", t["status"], t.get("missing_reason"), comp.get("path"), "scenes", t.get("composite_scene_ids"))
for t in lib["towns"]:
    if t["slug"] == slug:
        print("plans:", t["plan_count"], t["status"], t.get("missing_reason"))
        for p in t["plans"]:
            print(" ", p["id"], p["local_source_path"], "pdf", p["pdf_page"], "printed", p["printed_page"], p["figure_or_plate"], "|", p["caption_exact"], "|", p["north_class"], p["north_words_exact"], "|", p["north_evidence_location"], "| notes:", p["notes"])
