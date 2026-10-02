"""Acquire repository-listed primary excavation reports for context audit."""
import json
from concurrent.futures import ThreadPoolExecutor
from fetch_sources import ROOT, retrieve

SOURCES = [
    ("mackay_1943_chandaro", "1943", "primary excavation report; repository scan identity pending", "https://ia802909.us.archive.org/21/items/in.ernet.dli.2015.105167/2015.105167.Chanhu-Daro-Excavations-1935-36.pdf"),
    ("marshall_1931_govscan_14985", "1931", "primary excavation report volume1; government scan identity pending", "https://ignca.gov.in/Asi_data/14985.pdf"),
]

if __name__ == "__main__":
    with ThreadPoolExecutor(max_workers=2) as pool:
        records = list(pool.map(retrieve, SOURCES))
    path = ROOT / "source_retrieval_log.json"
    previous = json.loads(path.read_text(encoding="utf-8"))
    path.write_text(json.dumps(previous + records, indent=2), encoding="utf-8")
    for row in records:
        print(json.dumps(row, indent=2))
