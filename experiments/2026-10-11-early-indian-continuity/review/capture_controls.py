"""Acquire the exact root control loci for a separate reviewer inspection."""
import json
from capture_sources import OUT, capture

PLAN = [
    ("rv1095-teaching", "https://vedisk.sites.ku.dk/rv-10-95-1-pururavas-og-urvasi/"),
    ("sb11-gretil", "https://gretil.sub.uni-goettingen.de/gretil/1_sanskr/1_veda/2_bra/satapath/sb_11_u.htm"),
    ("sb11-eggeling", "https://www.sacred-texts.com/hin/sbr/sbe44/sbe44025.htm"),
    ("bm-asoka", "https://www.britishmuseum.org/collection/object/A_1880-21"),
]

if __name__ == "__main__":
    out = OUT / "capture-v4.json"
    if out.exists():
        raise FileExistsError(out)
    records = []
    for item in PLAN:
        try:
            records.append(capture(item))
        except Exception as e:
            records.append({"source_id": item[0], "url": item[1], "error": str(e)})
    out.write_text(json.dumps({"sources": records}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps([{k: r.get(k) for k in ("source_id", "bytes", "error")} for r in records]))
