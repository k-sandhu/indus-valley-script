"""Export all observational source identifiers for one exploratory pair audit."""
import json
from pathlib import Path

from conditional_structure import frames, load_records, pair_frames


rows, _ = load_records("data/normalized/lipi_clean_rtl_singleline.jsonl")
frame_map = frames(rows)
pair = ("176", "904")
contexts = pair_frames(frame_map)[pair]
result = {"pair": pair, "purpose": "Physical plate/source audit of three frame correspondences; no semantic claim", "contexts": []}
for key in contexts:
    entry = {"length": key[0], "slot_zero_based_reading": key[1], "frame_reading_rtl": key[2], "variants": {}}
    for sign in pair:
        entry["variants"][sign] = [{"record_id": r.get("record_id"), "artifact": r["artifact"], "CISI": r.get("source_cisi"), "site": r.get("site"), "type": r.get("object_type"), "metadata": r.get("metadata"), "sequence_reading_rtl": r["seq"]} for r in frame_map[key][sign]]
    result["contexts"].append(entry)
target = Path("research/methods/candidate_176_904_plate_audit.json")
target.write_text(json.dumps(result, indent=2), encoding="utf-8")
print(json.dumps({"output": str(target), "identifiers": [{"frame": e["frame_reading_rtl"], "records": {s: [{"id": r["record_id"], "CISI": r["CISI"]} for r in records] for s, records in e["variants"].items()}} for e in result["contexts"]]}))
