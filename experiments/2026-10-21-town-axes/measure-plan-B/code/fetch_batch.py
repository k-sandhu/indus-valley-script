"""Download several URLs sequentially with fetch.py's logging. Usage: fetch_batch.py LISTFILE
LISTFILE lines: URL<TAB>FILENAME"""
import subprocess, sys, os
here = os.path.dirname(os.path.abspath(__file__))
for line in open(sys.argv[1], encoding="utf-8"):
    line = line.strip()
    if not line or line.startswith("#"):
        continue
    url, fn = line.split("\t")
    if os.path.exists(os.path.join("data/raw/2026-10-21-town-axes/plan-B/downloads", fn)):
        print("skip", fn); continue
    subprocess.run([sys.executable, os.path.join(here, "fetch.py"), url, fn])
