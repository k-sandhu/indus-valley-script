"""Preserve the two earlier meaning inventories without editing either one."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import shutil

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
LOCAL = ROOT / 'data/raw/2026-10-12-semantic-sign-comparison'

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main():
    target = LOCAL / 'inputs-v1'
    target.mkdir(parents=True, exist_ok=False)
    names = {
        'run-v6-assigned-meanings.json': 'experiments/2026-10-11-bonta-adversarial/run-v6/catalogue-data.json',
        'oct12-visual-families.json': 'experiments/2026-10-12-anchor-expansion/visual/families.json',
        'oct12-family-sense-links.json': 'experiments/2026-10-12-anchor-expansion/anchors/family-links-v2.json',
    }
    rows = []
    for name, origin in names.items():
        src = ROOT / origin
        dst = target / name
        shutil.copyfile(src, dst)
        rows.append({'source': origin, 'snapshot': dst.relative_to(ROOT).as_posix(),
                     'bytes': dst.stat().st_size, 'sha256': sha(dst)})
    protocol = PACKAGE / 'PROTOCOL.md'
    manifest = {'frozen_utc': datetime.now(timezone.utc).isoformat(),
                'protocol_sha256': sha(protocol), 'inputs': rows,
                'handling': 'Earlier source-derived payloads remain local; own inventory summaries may be tracked.'}
    (PACKAGE / 'starting-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'frozen_inputs': len(rows), 'manifest': 'starting-manifest.json'}))

if __name__ == '__main__':
    main()
