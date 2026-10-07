"""Reviewer rerun: recompute every aggregate with the package's compute() and write to review/rerun/.

Writes the five aggregate files inside the review directory and the per-query matches into
data/raw/2026-10-06-resemblance-baseline/review-tmp/ (per-query results stay local, as in the package).
Compares each recomputed JSON with the frozen run-v1 file (parsed equality, and byte equality after the
package's own serialisation) and with run-v1-query-matches.json in the local raw directory.
"""
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PKG = ROOT / 'experiments/2026-10-06-resemblance-baseline'
RAW = ROOT / 'data/raw/2026-10-06-resemblance-baseline'
REVIEW = Path(__file__).resolve().parent
OUT = REVIEW / 'rerun'

spec = importlib.util.spec_from_file_location('pkg_analyze', PKG / 'analyze.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

outputs, queries = mod.compute()
OUT.mkdir(exist_ok=True)
report = {}
for name, value in outputs.items():
    text = json.dumps(value, indent=2, sort_keys=True) + '\n'
    (OUT / name).write_text(text, encoding='utf-8')
    frozen_text = (PKG / 'run-v1' / name).read_text(encoding='utf-8')
    report[name] = {
        'parsed_equal': json.loads(frozen_text) == value,
        'bytes_equal': frozen_text.replace('\r\n', '\n') == text,
    }
qtext = json.dumps(queries, indent=2) + '\n'
(RAW / 'review-tmp' / 'rerun-query-matches.json').write_text(qtext, encoding='utf-8')
frozen_q = (RAW / 'run-v1-query-matches.json').read_text(encoding='utf-8')
report['query-matches.json'] = {
    'parsed_equal': json.loads(frozen_q) == queries,
    'bytes_equal': frozen_q.replace('\r\n', '\n') == qtext,
}
print(json.dumps(report, indent=2))
sys.exit(0 if all(v['parsed_equal'] for v in report.values()) else 1)
