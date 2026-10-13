"""Scan the Smithsonian Open Access bulk metadata for Indus objects.

The Open Access API requires an api.data.gov key, so it was not used (two keyless requests
returned HTTP 403 API_KEY_MISSING). The same CC0 metadata is published without a key as
line-delimited JSON in the public bucket s3://smithsonian-open-access (AWS Open Data).
This script streams every file of the units named below, records each file's URL, bytes and
SHA256, and keeps only the lines that match the Indus pattern. Whole files are not cached
because the anthropology unit is 1.15 GB.

Usage (from the repository root):
    python experiments/2026-10-13-museum-open-access/harvest_smithsonian.py [unit ...]
    python experiments/2026-10-13-museum-open-access/harvest_smithsonian.py --summarize
"""
import hashlib
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mo_common import PKG, RAW, UA, fetch, requests, write_json  # noqa: E402

BUCKET = "https://smithsonian-open-access.s3-us-west-2.amazonaws.com/"
UNITS = ["nmaa", "fsg", "nmnhanthro"]
PATTERN = re.compile(r"harapp|mohenjo|moenjo|indus valley|indus civili[sz]ation|indus script|chanhu|lothal|kalibangan|"
                     r"dholavira|\bindus\b", re.I)


def list_keys(unit):
    meta = fetch("smithsonian", f"{BUCKET}?list-type=2&prefix=metadata/edan/{unit}/")
    text = Path(meta["path"]).read_text(encoding="utf-8") if Path(meta["path"]).is_absolute() else \
        (Path(__file__).resolve().parents[2] / meta["path"]).read_text(encoding="utf-8")
    return re.findall(r"<Key>(.*?\.txt)</Key>", text)


def main(units):
    outdir = RAW / "smithsonian"
    outdir.mkdir(parents=True, exist_ok=True)
    log_path = outdir / "bulk-files.jsonl"
    done = set()
    if log_path.exists():
        for line in log_path.read_text(encoding="utf-8").splitlines():
            done.add(json.loads(line)["url"])
    s = requests.Session()
    s.headers["User-Agent"] = UA
    for unit in units:
        keys = list_keys(unit)
        match_path = outdir / f"matches-{unit}.jsonl"
        for key in keys:
            url = BUCKET + key
            if url in done:
                continue
            t0 = datetime.now(timezone.utc).isoformat(timespec="seconds")
            h = hashlib.sha256()
            n = 0
            lines = 0
            matches = []
            buf = b""
            with s.get(url, stream=True, timeout=120) as r:
                status = r.status_code
                for chunk in r.iter_content(1 << 20):
                    h.update(chunk)
                    n += len(chunk)
                    buf += chunk
                    *full, buf = buf.split(b"\n")
                    for ln in full:
                        lines += 1
                        txt = ln.decode("utf-8", errors="replace")
                        if PATTERN.search(txt):
                            matches.append(txt)
                if buf.strip():
                    lines += 1
                    txt = buf.decode("utf-8", errors="replace")
                    if PATTERN.search(txt):
                        matches.append(txt)
            with open(match_path, "a", encoding="utf-8") as fh:
                for m in matches:
                    fh.write(m + "\n")
            with open(log_path, "a", encoding="utf-8") as fh:
                fh.write(json.dumps({"url": url, "retrieved_utc": t0, "status": status, "bytes": n,
                                     "sha256": h.hexdigest(), "lines": lines, "matches": len(matches)}) + "\n")
            time.sleep(1.0)
        print(unit, "done")


def summarize():
    """Write the tracked CC0 extraction of matching records and the scan log summary."""
    import csv
    outdir = RAW / "smithsonian"
    rows = [json.loads(x) for x in (outdir / "bulk-files.jsonl").read_text(encoding="utf-8").splitlines()]
    recs = []
    for unit in UNITS:
        path = outdir / f"matches-{unit}.jsonl"
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            d = json.loads(line)
            c = d.get("content", {})
            ft, ix, dn = c.get("freetext", {}), c.get("indexedStructured", {}), c.get("descriptiveNonRepeating", {})
            notes = " ".join(x.get("content", "") for x in ft.get("notes", []))
            name = " ".join(x.get("content", "") for x in ft.get("objectType", [])) or " ".join(ix.get("object_type", []))
            cast = "cast" in (d.get("title", "") + " " + notes).lower()
            indus = "Indus civilization" in (ix.get("culture") or [])
            recs.append({
                "museum": "Smithsonian (NMNH Anthropology)" if unit == "nmnhanthro" else unit,
                "record_id": d.get("id"),
                "accession": ", ".join(x.get("content", "") for x in ft.get("identifier", []) if x.get("label", "").startswith("Catalog")) or
                             ", ".join(x.get("content", "") for x in ft.get("identifier", [])),
                "url": dn.get("record_link") or dn.get("guid"),
                "title": d.get("title"), "object_name": name, "place": ix.get("place"), "culture": ix.get("culture"),
                "notes": notes[:400], "data_licence": "CC0 (Smithsonian Open Access)",
                "indus_attributed": indus, "originality": "cast-or-replica" if cast else "original",
                "seal_like": "seal" in (d.get("title", "") + name).lower(),
                "in_scope": False,
                "exclusion_reason": "cast or replica" if cast else ("not Indus-attributed" if not indus else ""),
            })
    write_json(PKG / "harvest" / "smithsonian-records.json", recs)
    with open(PKG / "harvest" / "smithsonian-queries.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["route", "files", "http_200", "bytes", "records_scanned", "lines_matching", "pattern"])
        for unit in UNITS:
            ur = [r for r in rows if f"/{unit}/" in r["url"]]
            w.writerow([f"s3://smithsonian-open-access/metadata/edan/{unit}/", len(ur), sum(r["status"] == 200 for r in ur),
                        sum(r["bytes"] for r in ur), sum(r["lines"] for r in ur), sum(r["matches"] for r in ur), PATTERN.pattern])
        w.writerow(["https://api.si.edu/openaccess/api/v1.0/search (no key)", 2, 0, "", "", "",
                    "HTTP 403 API_KEY_MISSING; not used further"])
    print(len(recs), "matching records;", sum(r["seal_like"] and r["indus_attributed"] for r in recs), "Indus seal casts")


if __name__ == "__main__":
    if sys.argv[1:] == ["--summarize"]:
        summarize()
    else:
        main(sys.argv[1:] or UNITS)
