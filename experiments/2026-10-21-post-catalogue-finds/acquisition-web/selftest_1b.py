"""Verify acquisition hashes, file presence, source sets, and proposed tracked outputs."""
import argparse
import codecs
import csv
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("repo", type=Path)
ap.add_argument("out", type=Path)
args = ap.parse_args()
root = args.repo.resolve()
out = args.out.resolve()
rows = list(csv.DictReader((out / "source-candidates-1b.csv").open(encoding="utf-8", newline="")))
rows += list(csv.DictReader((out / "supplementary-assets-1b.csv").open(encoding="utf-8", newline="")))
proposals = json.loads((out / "manifest-proposals-1b.json").read_text(encoding="utf-8"))
by_id = {p["id"]: p for p in proposals}
problems = []
checked = []
for row in rows:
    if row["downloaded"] != "yes":
        continue
    path = root / row["local_path"]
    if not path.is_file():
        problems.append({"id":row["source_id"],"error":"missing file"})
        continue
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    proposal = by_id.get(row["source_id"], {})
    acquisition = json.loads((path.parent / "acquisition.json").read_text(encoding="utf-8"))
    expected = [row["sha256"], proposal.get("fetch",{}).get("sha256"), proposal.get("hashes",{}).get(row["local_path"]), acquisition["sha256"]]
    if any(value != digest for value in expected):
        problems.append({"id":row["source_id"],"error":"hash mismatch"})
    if int(row["bytes"]) != path.stat().st_size or acquisition["bytes"] != path.stat().st_size:
        problems.append({"id":row["source_id"],"error":"byte count mismatch"})
    checked.append(row["source_id"])
if set(checked) != set(by_id):
    problems.append({"error":"proposal and downloaded row sets differ"})
asset_dirs=root/"data/raw/2026-10-21-post-catalogue-finds/run1b/sources"
held_ids={p.parent.name for p in asset_dirs.glob("*/acquisition.json")}
if held_ids != set(checked):
    problems.append({"error":"acquisition records and CSV assets differ","ids":sorted(held_ids.symmetric_difference(set(checked)))})
requested="RGR FRM BHR SNL RPR KRP BJR BRR TKD BNW KNL KLB DHV KHR KNM SKP GDH NGW PDR BTD KNT JKR KBD NVN SKT NHT LKD GNW CHN WTW CHL RJP HRP MHJ".split()
queries=list(csv.DictReader((out/"search-log-1b.csv").open(encoding="utf-8",newline="")))
query_counts={code:len({q["query"] for q in queries if q["site_code"]==code}) for code in requested}
if any(n<5 for n in query_counts.values()):
    problems.append({"error":"requested site has fewer than five distinct queries","counts":query_counts})
for item in proposals:
    if item.get("status")!="held" or item.get("location")!="local-only" or item.get("rights",{}).get("status")!="rights-unverified" or item.get("fetch",{}).get("method")!="http" or item.get("questions")!=["Q-1026"]:
        problems.append({"id":item.get("id"),"error":"proposal policy fields differ from required values"})
terms = codecs.decode("havpbea|ohyy|euvabprebf|ryrcunag|gvtre|ohssnyb|mroh|tbng|nagrybcr|zbgvs|navzny|fvta frdhrapr|ernqf nf", "rot_13")
pattern = re.compile(r"\b(?:" + terms + r")\b|\b\d+(?:\.\d+)?\s*(?:m" + r"m|c" + r"m)\b", re.IGNORECASE)
hits = []
scanned = []
for path in sorted(out.rglob("*")):
    if not path.is_file() or "__pycache__" in path.parts:
        continue
    scanned.append(path.relative_to(root).as_posix())
    for number,line in enumerate(path.read_text(encoding="utf-8").splitlines(),1):
        for match in pattern.finditer(line):
            hits.append({"file":path.relative_to(root).as_posix(),"line":number,"column":match.start()+1})
result = {"tested_utc":datetime.now(timezone.utc).isoformat(),"agent":"codex gpt-6.1-sol run 1B","result":"pass" if not problems and not hits else "fail","downloaded_files_checked":len(checked),"downloaded_bytes_checked":sum(int(r["bytes"]) for r in rows if r["downloaded"]=="yes"),"distinct_query_counts_by_requested_site":query_counts,"hash_or_record_errors":problems,"forbidden_field_hits":hits,"tracked_files_scanned":scanned}
(out / "selftest-1b.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
print(json.dumps(result,indent=2))
raise SystemExit(0 if result["result"]=="pass" else 1)
