"""Append one Check 1 reading to check1-readings.jsonl with a UTC time stamp.

Usage: python record_check1.py '<json object>'
"""
import datetime
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
rec = json.loads(sys.argv[1])
rec["utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
with open(HERE / "check1-readings.jsonl", "a", encoding="utf-8") as fh:
    fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
print("recorded", rec["object"])
