"""Append one Check 2 reading (made on a blind-v3 composite) to check2-readings.jsonl.

Usage: python record_reading.py '<json object>'
The reading is stored with a UTC time stamp. Readings name only the blind label; the key
is joined later by decide.py.
"""
import datetime
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
rec = json.loads(sys.argv[1])
rec["utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
with open(HERE / "check2-readings.jsonl", "a", encoding="utf-8") as fh:
    fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
print("recorded", rec["label"])
