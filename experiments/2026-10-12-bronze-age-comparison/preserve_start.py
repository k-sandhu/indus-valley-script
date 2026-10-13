"""Preserve the current navigation and named research inputs without changing them."""
from pathlib import Path
import hashlib
import json
import subprocess
from datetime import datetime, timezone

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
LOCAL = ROOT / 'data/raw/2026-10-12-bronze-age-comparison/baseline-v1'
LOCAL.mkdir(parents=True, exist_ok=False)
paths = ['README.md', 'knowledge/INDEX.md', 'knowledge/experiments/registry.json',
         'knowledge/retrospectives/README.md', '.gitignore',
         'knowledge/editorial/WRITING.md', 'knowledge/provenance/REDISTRIBUTION.md',
         'data/normalized/lipi_observed_faces.jsonl',
         'experiments/2026-10-11-two-approaches/grammar/grammar.py',
         'experiments/2026-10-11-two-approaches/grammar/run-v3-matched-mixtures/results.json',
         'experiments/2026-10-11-two-approaches/administrative/role-control-v1/summary.json']
records = []
for name in paths:
    payload = (ROOT / name).read_bytes()
    if name in paths[:5]:
        saved = LOCAL / name
        saved.parent.mkdir(parents=True, exist_ok=True)
        saved.write_bytes(payload)
    records.append({'path': name, 'bytes': len(payload), 'sha256': hashlib.sha256(payload).hexdigest()})
result = {'created_utc': datetime.now(timezone.utc).isoformat(), 'files': records,
          'git_status': subprocess.run(['git', 'status', '--short'], cwd=ROOT, capture_output=True, text=True, check=True).stdout,
          'scope': 'Named starting bytes; navigation copies are local. No exhaustive whole-workspace preservation claim.'}
(PACKAGE / 'baseline-v1.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'preserved_files': len(records), 'local_navigation_copies': 5}))
