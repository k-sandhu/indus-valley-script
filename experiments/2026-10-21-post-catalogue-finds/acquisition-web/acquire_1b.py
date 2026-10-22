"""Acquire open documents without executing downloaded content. Run with python -I."""
import argparse
import hashlib
import json
import subprocess
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path


def acquire(root, spec):
    dest = root.resolve() / "sources" / spec["source_id"]
    if not dest.resolve().is_relative_to(root.resolve()):
        raise ValueError("Source directory is outside this run")
    if dest.exists() and [p.name for p in dest.iterdir()] == ["failure.json"]:
        failed = root.resolve() / "failed-attempts" / spec["source_id"]
        if not failed.resolve().is_relative_to(root.resolve()):
            raise ValueError("Failure directory is outside this run")
        failed.parent.mkdir(parents=True, exist_ok=True)
        dest.rename(failed)
    dest.mkdir(parents=True, exist_ok=False)
    url = spec["url"]
    req = urllib.request.Request(url, headers={"User-Agent": "IndusResearchBibliography/1.0", "Accept": "application/pdf,text/html,text/plain,application/json"})
    try:
        with urllib.request.urlopen(req, timeout=90) as response:
            ctype = response.headers.get("Content-Type", "").split(";")[0].lower()
            final_url = response.url
            data = response.read()
        is_pdf = data.startswith(b"%PDF-")
        allowed = is_pdf or ctype in {"text/html", "application/xhtml+xml", "text/plain", "application/json"}
        if not allowed:
            raise ValueError("Response format is outside the allowed document formats")
        if spec.get("format") == "pdf" and not is_pdf:
            raise ValueError("Expected a PDF; response was not a PDF")
        ext = ".pdf" if is_pdf else ".json" if ctype == "application/json" else ".txt" if ctype == "text/plain" else ".html"
        filename = spec.get("filename", spec["source_id"] + ext)
        if Path(filename).name != filename:
            raise ValueError("Filename must be a basename")
        path = dest / filename
        path.write_bytes(data)
        pages = None
        if is_pdf:
            proc = subprocess.run(["pdfinfo", str(path)], capture_output=True, text=True, timeout=45)
            for line in proc.stdout.splitlines():
                if line.startswith("Pages:"):
                    pages = int(line.split(":", 1)[1].strip())
        record = dict(spec)
        record.update({"final_url": final_url, "retrieved_utc": datetime.now(timezone.utc).isoformat(), "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(), "content_type": ctype, "page_count": pages, "filename": filename, "local_path": path.as_posix(), "rights_status": "rights-unverified", "transformations": []})
        if spec.get("archive_md5"):
            record["archive_md5_matches"] = hashlib.md5(data).hexdigest() == spec["archive_md5"]
        if spec.get("archive_sha1"):
            record["archive_sha1_matches"] = hashlib.sha1(data).hexdigest() == spec["archive_sha1"]
        (dest / "acquisition.json").write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({k: record[k] for k in ("source_id", "bytes", "sha256", "page_count", "content_type")}))
    except Exception as exc:
        failure = {"source_id": spec["source_id"], "url": url, "retrieved_utc": datetime.now(timezone.utc).isoformat(), "error_type": type(exc).__name__, "outcome": str(exc)}
        (dest / "failure.json").write_text(json.dumps(failure, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(failure))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("root", type=Path)
    ap.add_argument("spec", type=Path)
    args = ap.parse_args()
    specs = json.loads(args.spec.read_text(encoding="utf-8"))
    if isinstance(specs, dict):
        specs = [specs]
    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(lambda spec: acquire(args.root, spec), specs))
