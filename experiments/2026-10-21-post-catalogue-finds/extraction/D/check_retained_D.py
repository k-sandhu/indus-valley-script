"""Check retained part D files before resuming."""
import argparse
import csv
import json
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path

ap=argparse.ArgumentParser()
ap.add_argument("paths",nargs="+")
args=ap.parse_args()
files=[p for value in args.paths for p in Path(value).rglob("*") if p.is_file()]
bad=[]
empty=[]
for p in files:
    try:
        if p.suffix==".json":
            json.loads(p.read_text(encoding="utf-8-sig"))
        elif p.suffix==".xml":
            ET.fromstring(p.read_bytes())
        elif p.suffix==".csv":
            with p.open(encoding="utf-8-sig",newline="") as stream:
                rows=list(csv.reader(stream))
            assert rows and all(len(r)==len(rows[0]) for r in rows)
        elif p.suffix==".py":
            compile(p.read_text(encoding="utf-8-sig"),str(p),"exec")
        elif p.suffix==".txt" and not p.read_text(encoding="utf-8-sig",errors="replace").strip():
            empty.append(str(p))
    except Exception as error:
        bad.append({"path":str(p),"error":type(error).__name__})
print(json.dumps({"files":len(files),"bytes":sum(p.stat().st_size for p in files),
                  "disk_free_bytes":shutil.disk_usage(Path(args.paths[0]).resolve()).free,
                  "invalid":bad,"empty_text":empty},indent=2))
