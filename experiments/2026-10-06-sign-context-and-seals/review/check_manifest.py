"""Reviewer: re-hash every file listed in FILE-MANIFEST-RECOVERY-2026-10-07.json and classify the result.
Run from the repository root. Writes review/manifest-recheck.json (paths and counts only)."""
import hashlib, json
from collections import Counter
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
PKG = ROOT / 'experiments/2026-10-06-sign-context-and-seals'
man = json.loads((PKG / 'FILE-MANIFEST-RECOVERY-2026-10-07.json').read_text(encoding='utf-8'))
res = Counter(); problems = []
for item in man['files']:
    p = ROOT / item['path']
    if item['sha256'] is None:
        res['self_entry_no_hash'] += 1; continue
    try:
        h = hashlib.sha256()
        with p.open('rb') as f:
            for chunk in iter(lambda: f.read(1 << 20), b''):
                h.update(chunk)
        if h.hexdigest() == item['sha256'] and p.stat().st_size == item['bytes']:
            res['match'] += 1
        else:
            res['mismatch'] += 1; problems.append({'path': item['path'], 'issue': 'hash or size differs'})
    except FileNotFoundError:
        res['missing'] += 1; problems.append({'path': item['path'], 'issue': 'missing'})
    except PermissionError as e:
        res['unreadable_permission_denied'] += 1; problems.append({'path': item['path'], 'issue': 'permission denied'})
    except OSError as e:
        res['unreadable_other'] += 1; problems.append({'path': item['path'], 'issue': str(e)[:80]})
out = {'manifest_entries': len(man['files']), 'results': dict(res), 'problems_listed': problems[:5],
       'problem_prefix_counts': dict(Counter('/'.join(p['path'].split('/')[:4]) for p in problems))}
(PKG / 'review/manifest-recheck.json').write_text(json.dumps(out, indent=1) + '\n', encoding='utf-8')
print(json.dumps({k: out[k] for k in ('manifest_entries', 'results', 'problem_prefix_counts')}, indent=1))
print(problems[:5])
