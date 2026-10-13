"""Save source witnesses locally without redistributing acquired content."""
from __future__ import annotations
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / "data/raw/2026-10-11-early-indian-continuity/coordinator/sources-v1"
SOURCES = [
    ("JB2014-INTRO-1", "jb2014-intro-1.pdf", "https://vedisk.sites.ku.dk/files/2021/09/Jamison-Brereton-s.-2-15.pdf"),
    ("JB2014-INTRO-2", "jb2014-intro-2.pdf", "https://vedisk.sites.ku.dk/files/2021/09/13-22-Stephanie_W_Jamison_Joel_P_Brereton_The.pdf"),
    ("SB11-GRETIL", "sb11-gretil.html", "https://gretil.sub.uni-goettingen.de/gretil/1_sanskr/1_veda/2_bra/satapath/sb_11_u.htm"),
    ("SB11-EGGELING", "sb11-eggeling.html", "https://www.sacred-texts.com/hin/sbr/sbe44/sbe44025.htm"),
    ("RV1095-UNIVERSITY", "rv1095-university.html", "https://vedisk.sites.ku.dk/rv-10-95-1-pururavas-og-urvasi/"),
]

def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    out = RAW / "acquisition.json"
    if out.exists():
        raise SystemExit("Acquisition endpoint exists; use a fresh directory for another acquisition.")
    records = []
    for sid, name, url in SOURCES:
        record = {"id": sid, "url": url, "acquired_utc": datetime.now(timezone.utc).isoformat(),
                  "distribution": "local-only; bibliography and own paraphrases may be tracked"}
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "ResearchWitness/1.0"})
            with urllib.request.urlopen(req, timeout=40) as response:
                payload = response.read()
                record.update(status=response.status, final_url=response.url,
                              content_type=response.headers.get("Content-Type"))
            path = RAW / name
            path.write_bytes(payload)
            record.update(path=path.relative_to(ROOT).as_posix(), bytes=len(payload),
                          sha256=hashlib.sha256(payload).hexdigest(),
                          signature="pdf" if payload.startswith(b"%PDF") else "other")
        except Exception as error:
            record["error"] = f"{type(error).__name__}: {error}"
        records.append(record)
    out.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"sources": len(records), "saved": sum("path" in r for r in records),
                      "errors": [r["id"] for r in records if "error" in r]}))

if __name__ == "__main__":
    main()
