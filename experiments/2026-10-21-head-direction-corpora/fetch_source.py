"""Download one source file into a new empty directory and write its acquisition record.

Usage:
  python -I experiments/2026-10-21-head-direction-corpora/fetch_source.py \
      --url <url> --dest <new empty directory> --name <file name> --record <record.json> \
      --source-id <id> --title "<bibliographic title>" --rights-status <status> --rights-note "<observed notice>" \
      [--expect-sha1 <sha1 from the Internet Archive metadata>] [--expect-bytes <n>] [--note "<free text>"]

The destination directory must not exist or must be empty; the record path must not exist. The record
gives the URL, retrieval time (UTC), byte count, SHA-256, SHA-1, the check against an expected SHA-1 or
size, the PDF page count when the file is a PDF (read with PyMuPDF), and the rights status and notice as
observed. Only the standard library and PyMuPDF are used; nothing in the downloaded file is executed.
"""
import argparse
import datetime
import hashlib
import json
import sys
import urllib.request
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    for a in ("--url", "--dest", "--name", "--record", "--source-id", "--title", "--rights-status", "--rights-note"):
        ap.add_argument(a, required=True)
    ap.add_argument("--expect-sha1")
    ap.add_argument("--expect-bytes", type=int)
    ap.add_argument("--note", default="")
    args = ap.parse_args()
    dest, record = Path(args.dest), Path(args.record)
    if dest.exists() and any(dest.iterdir()):
        sys.exit(f"refusing: {dest} is not empty")
    if record.exists():
        sys.exit(f"refusing: {record} exists")
    dest.mkdir(parents=True, exist_ok=True)
    target = dest / args.name
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    req = urllib.request.Request(args.url, headers={"User-Agent": "indus-research-kb/1.0 (research acquisition)"})
    h256, h1, n = hashlib.sha256(), hashlib.sha1(), 0
    with urllib.request.urlopen(req, timeout=600) as resp, open(target, "wb") as out:
        final_url = resp.geturl()
        status = resp.status
        ctype = resp.headers.get("Content-Type")
        while True:
            chunk = resp.read(1 << 20)
            if not chunk:
                break
            out.write(chunk)
            h256.update(chunk)
            h1.update(chunk)
            n += len(chunk)
    finished = datetime.datetime.now(datetime.timezone.utc).isoformat()
    rec = {"source_id": args.source_id, "title": args.title, "url": args.url, "final_url": final_url,
           "http_status": status, "content_type": ctype, "retrieved_utc_start": started,
           "retrieved_utc_end": finished, "local_path": str(target).replace("\\", "/"), "bytes": n,
           "sha256": h256.hexdigest(), "sha1": h1.hexdigest(),
           "expected_sha1": args.expect_sha1, "sha1_matches_expected": (h1.hexdigest() == args.expect_sha1) if args.expect_sha1 else None,
           "expected_bytes": args.expect_bytes, "bytes_match_expected": (n == args.expect_bytes) if args.expect_bytes else None,
           "rights_status": args.rights_status, "rights_note": args.rights_note, "note": args.note}
    if target.suffix.lower() == ".pdf":
        try:
            import site
            # -I hides the user site, where PyMuPDF is installed; append it after the standard library.
            sys.path.append(site.getusersitepackages())
            import fitz
            with fitz.open(target) as doc:
                rec["pdf_pages"] = doc.page_count
        except Exception as exc:  # recorded, not fatal
            rec["pdf_pages"] = None
            rec["pdf_error"] = repr(exc)
    record.parent.mkdir(parents=True, exist_ok=True)
    record.write_text(json.dumps(rec, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({k: rec[k] for k in ("source_id", "bytes", "sha256", "sha1_matches_expected", "bytes_match_expected")}))


if __name__ == "__main__":
    main()
