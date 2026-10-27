"""Inject an external tile loader into an ignored copy and require checker rejection."""
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
import build_site as site

original = ROOT / '_site/site-preview-final'
probe = ROOT / '_site/site-preview-external-tile-probe'
shutil.copytree(original, probe)
before = site.check(probe)
(probe / 'assets/tile-probe.js').write_bytes(b'L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png");\n')
after = site.check(probe)
result = {'ok': before['ok'] and not after['ok'] and
          'assets/tile-probe.js: script loads an external resource' in after['errors'],
          'clean_copy_passed': before['ok'], 'injected_copy_passed': after['ok'], 'errors': after['errors'],
          'probe': probe.relative_to(ROOT).as_posix()}
(Path(__file__).parent / 'gate-test.json').write_bytes(site.dumps(result).encode())
print(site.dumps(result))
raise SystemExit(0 if result['ok'] else 1)
