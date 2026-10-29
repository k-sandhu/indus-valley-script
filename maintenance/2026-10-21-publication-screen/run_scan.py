import importlib.util, json, sys
from pathlib import Path
ROOT = Path('C:/Users/sandh/OneDrive/Projects/indus_valley_script')
SCR = Path(sys.argv[1])
spec = importlib.util.spec_from_file_location('scan', ROOT/'experiments/2026-10-13-publication-screen/scan_sequences.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
m.HERE = SCR
files = [l.strip() for l in (SCR/'commit1-files.txt').read_text(encoding='utf-8').splitlines() if l.strip()]
inv = {'files': [{'path': p, 'bytes': (ROOT/p).stat().st_size} for p in files if (ROOT/p).is_file()]}
m.RAW.mkdir(parents=True, exist_ok=True)
(m.RAW/'inventory-2026-10-21b.json').write_text(json.dumps(inv), encoding='utf-8')
sys.argv = ['scan', 'inventory-2026-10-21b.json', 'sequence-scan-2026-10-21b.json']
m.main()
out = json.loads((SCR/'sequence-scan-2026-10-21b.json').read_text(encoding='utf-8'))
for r in out['files']:
    print(r['path'], '| strict windows', r['strict']['matched_windows'], 'full', r['strict']['distinct_full_texts'], '| stream', r['stream']['matched_windows'], '| short distinct', r['short_complete_texts']['distinct'])
