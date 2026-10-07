"""Preserve a before-work integrity ledger and adapt the prior acquisition code."""
import hashlib
import json
from pathlib import Path

AMEND=Path(__file__).resolve().parent
OWN=AMEND.parent
ROOT=OWN.parents[1]
manifest=json.loads((OWN/'file-manifest-final.json').read_text(encoding='utf-8'))
for item in manifest['files']:
    assert hashlib.sha256((ROOT/item['path']).read_bytes()).hexdigest()==item['sha256'],item['path']
paths=[ROOT/item['path'] for item in manifest['files']]+[OWN/'file-manifest-final.json']
ledger={'status':'Verified computation','baseline_manifest_records':len(manifest['files']),
        'baseline_records_match':True,
        'baseline_files':[{'path':path.relative_to(ROOT).as_posix(),
                          'sha256':hashlib.sha256(path.read_bytes()).hexdigest()} for path in paths]}
destination=AMEND/'baseline-integrity.json'
if destination.exists(): raise FileExistsError(destination)
destination.write_text(json.dumps(ledger,indent=2)+'\n',encoding='utf-8')
code=(OWN/'acquire_sources.py').read_text(encoding='utf-8').replace('parents[2]','parents[3]')
code=code.replace("ROOT / 'data/raw/2026-10-06-backward-chronology'",
                  "ROOT / 'data/raw/2026-10-06-backward-chronology/amendment-2026-10-07-frenez'")
(AMEND/'acquire_sources.py').write_text(code,encoding='utf-8')
print(json.dumps({'baseline_files_verified':len(paths),'acquisition_script':str(AMEND/'acquire_sources.py')}))
