"""Summarize ordered compound components from a frozen public concordance."""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).parent
RAW = ROOT / "data/raw/2026-10-02-connections-and-priority/south-india"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", required=True)
    args = parser.parse_args()
    out = HERE / args.run
    out.mkdir(exist_ok=False)
    client = (RAW / "tngraffiti-index.js").read_text(encoding="utf-8")
    match = re.search(r"va=JSON\.parse\('(\[.*?\])'\)", client)
    if match is None:
        raise ValueError("Public string-preserving client map not found")
    mapping = json.loads(match[1])
    crosswalk = defaultdict(set)
    for row in mapping:
        crosswalk[row["rsign"]].add(row["dsign"])
    concordance = json.loads((RAW / "concordance-sign39.json").read_text(encoding="utf-8"))
    groups = defaultdict(list)
    for row in concordance["unique_response"]:
        if row["type"] == "Composite":
            groups[row["sn"]].append(row)
    plain = {"39"} | {f"39.{i}" for i in range(1, 16)}
    accepted, unresolved = [], []
    for key, records in sorted(groups.items()):
        seqs = {tuple(r[k] for k in sorted(r, key=lambda x: int(x[1:]) if re.fullmatch(r"s\d+", x) else -1)
                      if re.fullmatch(r"s\d+", k)) for r in records}
        ns = {r["occurrence_count"] for r in records}
        if len(seqs) != 1 or len(ns) != 1:
            unresolved.append({"key": key, "reason": "inconsistent components or frequency"})
            continue
        seq = next(iter(seqs))
        if any(len(crosswalk[c]) != 1 for c in seq):
            unresolved.append({"key": key, "reason": "unmapped or ambiguous component"})
            continue
        codes = [next(iter(crosswalk[c])) for c in seq]
        mask = [code in plain for code in codes]
        if not any(mask):
            continue
        blocks = sum(v and (i == 0 or not mask[i-1]) for i, v in enumerate(mask))
        accepted.append({"key": key, "component_count": len(codes),
                         "stroke_components": sum(mask), "stroke_blocks": blocks,
                         "other_components": len(codes)-sum(mask),
                         "left_endpoint_stroke": mask[0], "right_endpoint_stroke": mask[-1],
                         "reported_occurrences": next(iter(ns)),
                         "simple_pair": blocks == 1 and len(codes)-sum(mask) == 1})
    result = {
        "inputs": {name: hashlib.sha256((RAW / name).read_bytes()).hexdigest()
                   for name in ["tngraffiti-index.js", "concordance-sign39.json"]},
        "response_rows": len(concordance["unique_response"]),
        "response_reported_unique_count": concordance["unique_count"],
        "compound_keys": len(groups), "unresolved": unresolved,
        "resolved_compounds_with_plain_strokes": len(accepted),
        "reported_occurrences_of_resolved_compounds": sum(r["reported_occurrences"] for r in accepted),
        "component_length_form_counts": dict(sorted(Counter(r["component_count"] for r in accepted).items())),
        "stroke_block_form_counts": dict(sorted(Counter(r["stroke_blocks"] for r in accepted).items())),
        "simple_pair_forms": sum(r["simple_pair"] for r in accepted),
        "simple_pair_reported_occurrences": sum(r["reported_occurrences"] for r in accepted if r["simple_pair"]),
        "split_stroke_block_forms": sum(r["stroke_blocks"] > 1 for r in accepted),
        "forms_with_several_other_components": sum(r["other_components"] > 1 for r in accepted),
        "own_form_properties": accepted,
        "scope": "Authors' normalized compound components; illustrative selection by stroke-family query",
    }
    (out / "results.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    (out / "code_snapshot.py").write_bytes(Path(__file__).read_bytes())
    print(json.dumps({k: v for k, v in result.items() if k not in ["own_form_properties", "inputs", "unresolved"]}))
    print("unresolved", len(unresolved))


if __name__ == "__main__":
    main()
