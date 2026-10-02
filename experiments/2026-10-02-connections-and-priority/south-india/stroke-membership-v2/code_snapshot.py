"""Count explicit plain-stroke components without naming other components."""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).parent
RAW = ROOT / "data/raw/2026-10-02-connections-and-priority/south-india"

parser = argparse.ArgumentParser()
parser.add_argument("--run", required=True)
args = parser.parse_args()
dest = HERE / args.run
dest.mkdir(exist_ok=False)
client = (RAW / "tngraffiti-index.js").read_text(encoding="utf-8")
crosswalk = json.loads(re.search(r"va=JSON\.parse\('(\[.*?\])'\)", client)[1])
target = {"39"} | {f"39.{i}" for i in range(1, 16)}
plain_codes = {r["rsign"] for r in crosswalk if r["dsign"] in target}
assert len(plain_codes) == len(target) == 16
assert {r["dsign"] for r in crosswalk if r["rsign"] in plain_codes} == target
source = json.loads((RAW / "concordance-sign39.json").read_text())
groups = defaultdict(list)
for row in source["unique_response"]:
    if row["type"] == "Composite":
        groups[row["sn"]].append(row)
properties, opaque, inconsistent = [], [], []
for key, rows in sorted(groups.items()):
    sequences = {tuple(row[k] for k in sorted(
        [k for k in row if re.fullmatch(r"s\d+", k)], key=lambda k: int(k[1:]))) for row in rows}
    frequencies = {r["occurrence_count"] for r in rows}
    if len(sequences) != 1 or len(frequencies) != 1:
        inconsistent.append(key)
        continue
    seq = next(iter(sequences))
    mask = [code in plain_codes for code in seq]
    n = next(iter(frequencies))
    if not any(mask):
        opaque.append({"form": key, "reported_occurrences": n})
        continue
    blocks = sum(v and (i == 0 or not mask[i-1]) for i, v in enumerate(mask))
    other = len(seq) - sum(mask)
    properties.append({"form": key, "component_count": len(seq),
                       "stroke_components": sum(mask), "stroke_blocks": blocks,
                       "other_components": other, "reported_occurrences": n,
                       "simple_pair": blocks == 1 and other == 1})
result = {
    "inputs": {n: hashlib.sha256((RAW / n).read_bytes()).hexdigest() for n in
               ["tngraffiti-index.js", "concordance-sign39.json"]},
    "compound_keys": len(groups), "inconsistent": inconsistent,
    "resolved_compounds_with_explicit_plain_strokes": len(properties),
    "opaque": opaque,
    "component_length_form_counts": dict(sorted(Counter(r["component_count"] for r in properties).items())),
    "simple_pair_forms": sum(r["simple_pair"] for r in properties),
    "simple_pair_reported_occurrences": sum(r["reported_occurrences"] for r in properties if r["simple_pair"]),
    "resolved_reported_occurrences": sum(r["reported_occurrences"] for r in properties),
    "split_stroke_block_forms": sum(r["stroke_blocks"] > 1 for r in properties),
    "forms_with_several_other_components": sum(r["other_components"] > 1 for r in properties),
    "own_form_properties": properties,
    "printed_source_checks": [
        {"form": "1.6C", "specimen": "KDL-G-0042", "volII_pdf_page": 32,
         "printed_page": 707, "portal_components": 3, "printed_components": 3,
         "portal_stroke_blocks": 2, "printed_stroke_blocks": 2, "agrees": True},
        {"form": "39.13C", "specimen": "KLD-G-1329", "volII_pdf_page": 307,
         "printed_page": 982, "portal_components": 2, "printed_components": 2,
         "portal_stroke_blocks": 1, "printed_stroke_blocks": 1, "agrees": True},
        {"form": "4.19C", "specimen": "SGI(PPT)-G-0137", "volII_pdf_page": 104,
         "printed_page": 779, "portal_components": 5, "printed_components": 6,
         "portal_stroke_blocks": 1, "printed_stroke_blocks": 2, "agrees": False},
    ],
    "status": "Exploratory post-outcome membership refinement with a recorded source disagreement",
    "scope": "Explicit components in the frozen portal's normalized compounds; no assigned meanings or units",
}
(dest / "results.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
(dest / "code_snapshot.py").write_bytes(Path(__file__).read_bytes())
print(json.dumps({k: v for k, v in result.items() if k not in ["inputs", "opaque", "own_form_properties", "printed_source_checks"]}))
print("opaque", len(opaque))
