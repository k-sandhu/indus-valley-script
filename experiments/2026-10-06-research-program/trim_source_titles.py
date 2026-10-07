"""Trim copied snippet text from source-record titles flagged by the census synthesis.

The synthesis package (experiments/2026-10-06-evidence-census/synthesis) flagged
source records whose title field holds copied prose or search-snippet text. This
script moves each flagged title to a local-only file under data/raw and replaces
it with a short label in the tracked file. Run from the repository root:

    python experiments/2026-10-06-research-program/trim_source_titles.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REVIEW = ROOT / "experiments/2026-10-06-evidence-census/synthesis/source-title-review.json"
LOCAL = ROOT / "data/raw/2026-10-06-research-program/trimmed-source-titles.json"
KEEP = 120


def walk(node, record_id, hits):
    if isinstance(node, dict):
        if record_id in (node.get("id"), node.get("record_id"), node.get("source_id")) and isinstance(node.get("title"), str):
            hits.append(node)
        for value in node.values():
            walk(value, record_id, hits)
    elif isinstance(node, list):
        for value in node:
            walk(value, record_id, hits)


def main():
    review = json.loads(REVIEW.read_text(encoding="utf-8"))
    moved = []
    by_file = {}
    for record in review["records"]:
        by_file.setdefault(record["file"], []).append(record)
    for rel, records in by_file.items():
        path = ROOT / rel
        raw_bytes = path.read_bytes()
        newline = "\r\n" if b"\r\n" in raw_bytes else "\n"
        data = json.loads(raw_bytes.decode("utf-8-sig"))
        for record in records:
            hits = []
            walk(data, record["record_id"], hits)
            for node in hits:
                title = node["title"]
                if len(title) <= KEEP + 40 or "[trimmed by coordinator" in title:
                    continue
                moved.append({"file": rel, "record_id": record["record_id"], "classification": record["classification"], "original_title": title})
                node["title"] = title[:KEEP].rstrip() + " [trimmed by coordinator 2026-10-07: copied text removed; original kept locally]"
        text = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
        path.write_bytes(text.replace("\n", newline).encode("utf-8"))
    LOCAL.parent.mkdir(parents=True, exist_ok=True)
    if LOCAL.exists():
        moved = json.loads(LOCAL.read_text(encoding="utf-8"))["records"] + moved
    LOCAL.write_text(json.dumps({"source": str(REVIEW.relative_to(ROOT)), "records": moved}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"trimmed {len(moved)} title fields in {len(by_file)} files; originals in {LOCAL.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
