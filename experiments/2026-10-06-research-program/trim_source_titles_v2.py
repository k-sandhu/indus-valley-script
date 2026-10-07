"""Second pass: remove copied search-result prose from census source titles.

The census review (experiments/2026-10-06-evidence-census/synthesis/review/
residual-snippet-title-judgement.json) identified 32 further source records whose
title field holds search-result prose, and noted that the first pass kept 120
characters of each trimmed title. This pass replaces every title judged to be
prose, in both review lists, with a neutral label and keeps the current and
earlier text in a local-only file. Legitimate long titles are left alone.
Run from the repository root:

    python experiments/2026-10-06-research-program/trim_source_titles_v2.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CENSUS = ROOT / "experiments/2026-10-06-evidence-census"
FIRST = CENSUS / "synthesis/source-title-review.json"
RESIDUAL = CENSUS / "synthesis/review/residual-snippet-title-judgement.json"
LOCAL = ROOT / "data/raw/2026-10-06-research-program/trimmed-source-titles-v2.json"
LABEL = "Search-result text removed by the coordinator on 2026-10-07; see the record URL and its local witness"


def targets():
    wanted = {}
    first = json.loads(FIRST.read_text(encoding="utf-8"))
    for record in first["records"]:
        if record["classification"] == "prose_or_search_snippet_payload":
            wanted.setdefault(record["file"], set()).add(record["record_id"])
    residual = json.loads(RESIDUAL.read_text(encoding="utf-8"))
    for key, ids in residual["search_result_prose_titles"].items():
        if key.startswith("sites-deep/a-pakistan-afghanistan"):
            files = ["sites-deep/a-pakistan-afghanistan/sources.json",
                     "sites-deep/a-pakistan-afghanistan/revision-west-upper-sources.json"]
        else:
            files = [key]
        for name in files:
            wanted.setdefault(f"experiments/2026-10-06-evidence-census/{name}", set()).update(ids)
    return wanted


def walk(node, ids, hits):
    if isinstance(node, dict):
        rid = node.get("id") or node.get("record_id") or node.get("source_id")
        if rid in ids and isinstance(node.get("title"), str):
            hits.append((rid, node))
        for value in node.values():
            walk(value, ids, hits)
    elif isinstance(node, list):
        for value in node:
            walk(value, ids, hits)


def main():
    moved = []
    for rel, ids in sorted(targets().items()):
        path = ROOT / rel
        raw = path.read_bytes()
        newline = "\r\n" if b"\r\n" in raw else "\n"
        data = json.loads(raw.decode("utf-8-sig"))
        hits = []
        walk(data, ids, hits)
        for rid, node in hits:
            if node["title"] == LABEL:
                continue
            moved.append({"file": rel, "record_id": rid, "replaced_title": node["title"]})
            node["title"] = LABEL
        text = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
        path.write_bytes(text.replace("\n", newline).encode("utf-8"))
    LOCAL.parent.mkdir(parents=True, exist_ok=True)
    previous = json.loads(LOCAL.read_text(encoding="utf-8"))["records"] if LOCAL.exists() else []
    LOCAL.write_text(json.dumps({"records": previous + moved}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"replaced {len(moved)} title fields; earlier text kept in {LOCAL.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
