"""Preserve bounded source extracts and acquisition metadata; bulk witnesses stay local."""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

import fitz
import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
RAW = ROOT / "data/raw/2026-10-11-two-approaches/literature"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    plans = json.loads((OUT / "source-plan.json").read_text(encoding="utf-8"))
    log = []
    for plan in plans:
        source_id = plan["id"]
        if plan.get("existing_witness"):
            witness = ROOT / plan["existing_witness"]
            if not witness.exists():
                log.append({"id": source_id, "error": "Existing witness absent", "path": plan["existing_witness"]})
                continue
            record = {"id": source_id, "operation": "reuse-existing-witness", "witness_path": plan["existing_witness"], "parent_sha256": digest(witness), "parent_bytes": witness.stat().st_size}
        else:
            witness = RAW / (source_id.lower() + plan.get("suffix", ".html"))
            if not witness.exists():
                try:
                    response = requests.get(plan["url"], timeout=45, headers={"User-Agent": "IndusResearchSourceReview/1.0"})
                    response.raise_for_status()
                    witness.write_bytes(response.content)
                    record = {"id": source_id, "operation": "download", "url": plan["url"], "resolved_url": response.url, "http_status": response.status_code, "retrieved_utc": datetime.now(timezone.utc).isoformat(), "content_type": response.headers.get("Content-Type")}
                except Exception as exc:
                    log.append({"id": source_id, "operation": "download-failed", "url": plan["url"], "error": str(exc), "retrieved_utc": datetime.now(timezone.utc).isoformat()})
                    continue
            else:
                record = {"id": source_id, "operation": "reuse-this-run-download", "url": plan["url"]}
            record.update({"witness_path": witness.relative_to(ROOT).as_posix(), "parent_sha256": digest(witness), "parent_bytes": witness.stat().st_size})
        pages = plan.get("pdf_pages", [])
        if witness.suffix.lower() == ".pdf":
            doc = fitz.open(witness)
            record["parent_page_count"] = len(doc)
            if not pages:
                pages = list(range(1, min(len(doc), 5) + 1))
            extract = [{"pdf_page": number, "text": doc[number - 1].get_text()} for number in pages]
            record["transformation"] = "PyMuPDF selected-page text extraction; no OCR or transcription correction"
            doc.close()
        elif witness.suffix.lower() in {".html", ".htm"}:
            soup = BeautifulSoup(witness.read_bytes(), "html.parser")
            for element in soup(["script", "style", "nav", "footer"]):
                element.decompose()
            extract = [{"text": soup.get_text("\n", strip=True)}]
            record["transformation"] = "BeautifulSoup text extraction; scripts and styles removed; no page script executed"
        else:
            extract = [{"text": witness.read_text(encoding="utf-8", errors="replace")}]
            record["transformation"] = "Existing text witness copied into local extract record"
        extract_path = RAW / (source_id.lower() + ".extract.json")
        dump(extract_path, extract)
        record.update({"extract_path": extract_path.relative_to(ROOT).as_posix(), "extract_sha256": digest(extract_path), "extract_bytes": extract_path.stat().st_size, "rights_status": plan.get("rights_status", "rights-unverified"), "disposition": "local-only source payload; own summaries and source pointers may be tracked"})
        log.append(record)
    dump(RAW / "acquisition-log.json", log)
    print(json.dumps({"source_records": len(log), "successful": sum("error" not in item for item in log), "bytes_of_new_raw": sum(p.stat().st_size for p in RAW.iterdir() if p.is_file())}))


if __name__ == "__main__":
    main()
