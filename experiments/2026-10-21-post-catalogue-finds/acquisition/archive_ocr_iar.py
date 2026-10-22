"""Locate archive page OCR for the already assigned IAR volumes."""
import argparse
import concurrent.futures as cf
import importlib.util
import json
import pathlib
import re
import sys

sys.dont_write_bytecode = True


def main():
    ap = argparse.ArgumentParser()
    for name in ("root", "raw", "records"):
        ap.add_argument("--" + name, type=pathlib.Path, required=True)
    args = ap.parse_args()
    root, raw, records = args.root.resolve(), args.raw.resolve(), args.records.resolve()
    spec = importlib.util.spec_from_file_location("acquisition_fetch", records / "fetch_proposed.py")
    fetch = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fetch)
    fetch.initialize(root, raw, records)
    states = [json.loads(p.read_text(encoding="utf-8")) for p in (raw / "processing").glob("iar-*.json")]
    targets = [s for s in states if s.get("needs_ocr")]
    years = sorted({int(s["year_or_volume"][:4]) for s in targets})
    def find(year):
        return year, fetch.search(f'title:("Indian Archaeology") AND title:{year} AND mediatype:texts')
    with cf.ThreadPoolExecutor(max_workers=5) as pool:
        discovered = dict(pool.map(find, years))
    ids = {doc["identifier"] for values in discovered.values() for doc in values}
    with cf.ThreadPoolExecutor(max_workers=5) as pool:
        metadata = dict(zip(sorted(ids), pool.map(fetch.metadata, sorted(ids))))
    proposals = json.loads((records / "manifest-proposals-1a.json").read_text(encoding="utf-8"))
    existing = {e["id"] for e in proposals["sources"]}
    results = []
    for state in targets:
        sid, year = state["source_id"], int(state["year_or_volume"][:4])
        matches = []
        for doc in discovered[year]:
            title = str(doc.get("title", ""))
            compact = re.sub(r'[^a-z0-9]', '', title.lower())
            if str(year) + str(year+1)[2:] not in compact and str(year) + str(year+1) not in compact:
                continue
            meta = metadata.get(doc["identifier"])
            if meta and fetch.choose(meta, "ocr"):
                matches.append(doc["identifier"])
        if matches and sid + "-page-ocr" not in existing:
            identifier = sorted(matches, key=lambda v: (not v.startswith("indianarchaeology"), v))[0]
            entry = fetch.proposal(sid, identifier, metadata[identifier], "ocr", "annual-review")
            entry["selection_note"] = "OCR alternative for the assigned volume; page count must agree before use."
            proposals["sources"].append(entry)
            existing.add(entry["id"])
        results.append(dict(source_id=sid, observed_year=state["year_or_volume"], archive_alternatives=matches))
    fetch.dump(records / "iar-ocr-alternatives-1a.json", results)
    fetch.dump(records / "manifest-proposals-1a.json", proposals)
    print(json.dumps(dict(targets=len(targets), proposals=len(proposals["sources"]), matched=sum(bool(r["archive_alternatives"]) for r in results))))


if __name__ == "__main__":
    main()
