"""Reviewer scan: long string values and long CSV cells in tracked census files.

Reports, per file and key name, how many string values exceed a length threshold, so a human can
judge which are the package's own prose and which could be copied third-party text. It prints
lengths and key names only, never the text itself.
"""
import csv, json, subprocess, sys, collections
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
THRESH = int(sys.argv[1]) if len(sys.argv) > 1 else 300
tracked = subprocess.run(['git', 'ls-files', 'experiments/2026-10-06-evidence-census', 'experiments/2026-10-06-research-program'],
                         cwd=ROOT, capture_output=True, text=True, check=True).stdout.splitlines()
report = collections.defaultdict(lambda: collections.Counter())
maxlen = collections.defaultdict(int)


def walk(node, key, bucket, path):
    if isinstance(node, str):
        if len(node) > THRESH:
            report[bucket][key] += 1
            maxlen[(bucket, key)] = max(maxlen[(bucket, key)], len(node))
    elif isinstance(node, list):
        for x in node:
            walk(x, key, bucket, path)
    elif isinstance(node, dict):
        for k, v in node.items():
            walk(v, k, bucket, path)


for rel in tracked:
    p = ROOT / rel
    if rel.endswith('.json') and p.exists():
        try:
            walk(json.loads(p.read_text(encoding='utf-8-sig')), '<root>', rel, rel)
        except Exception as e:
            print('PARSE-FAIL', rel, e)
    elif rel.endswith('.csv') and p.exists():
        with p.open(encoding='utf-8-sig', newline='') as f:
            for row in csv.DictReader(f):
                for k, v in row.items():
                    if v and len(v) > THRESH:
                        report[rel][k] += 1
                        maxlen[(rel, k)] = max(maxlen[(rel, k)], len(v))
for rel in sorted(report):
    if '/synthesis/' in rel and any(x in rel for x in ('main-2026', 'replay-2026', 'development-2026', 'annotation-replay')):
        continue
    for k, n in sorted(report[rel].items(), key=lambda kv: -maxlen[(rel, kv[0])]):
        print(f'{n:5d} values > {THRESH} chars, max {maxlen[(rel, k)]:6d}  key={k!r:40.40}  {rel.replace("experiments/2026-10-06-evidence-census/", "")}')
