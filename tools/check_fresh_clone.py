"""Check lossless packaging and repeat the rank audit in a clean Git checkout."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def run(clone, args):
    return subprocess.run(args, cwd=clone, text=True, encoding='utf-8', capture_output=True, check=True).stdout.strip()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--clone', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    clone, output = Path(args.clone).resolve(), Path(args.output).resolve()
    if output.exists():
        raise RuntimeError('Use a fresh output directory.')
    initial_status = run(clone, ['git', 'status', '--porcelain'])
    if initial_status:
        raise RuntimeError('The clone must start with a clean working tree.')
    excluded = clone/'experiments/2026-10-02-six-hour/latent-forms/main-v1/results.json'
    if excluded.exists():
        raise RuntimeError('This check requires a clone without the excluded original result.')
    output.mkdir(parents=True)
    package = json.loads(run(clone, [sys.executable, '-X', 'utf8', 'src/six_hour/latent_forms_package.py', 'verify']))
    original = clone/'src/six_hour/latent_generator_identification_verify.py'
    source = original.read_text(encoding='utf-8')
    old = "output = BASE/'review-v2'"
    new = "output = ROOT/'tmp/fresh-identification-review-20261002'"
    if source.count(old) != 1:
        raise RuntimeError('Inspect the audit source before changing its output path.')
    copied = clone/'tmp/fresh-identification-review-20261002.py'
    if copied.exists() or (clone/'tmp/fresh-identification-review-20261002').exists():
        raise RuntimeError('Use another clean clone; preserve the previous audit copy and output.')
    copied.parent.mkdir(exist_ok=True)
    copied.write_text(source.replace(old, new), encoding='utf-8')
    audit = json.loads(run(clone, [sys.executable, '-X', 'utf8', str(copied)]))
    (output/'executed-audit-copy.py').write_bytes(copied.read_bytes())
    record = dict(completed_utc=datetime.now(timezone.utc).isoformat(), clone=str(clone),
                  clone_commit=run(clone, ['git', 'rev-parse', 'HEAD']), initial_working_tree_clean=True,
                  excluded_original_absent=True, package=package, rank_audit=audit,
                  original_audit_sha256=sha(original), executed_audit_sha256=sha(copied),
                  only_audit_change=dict(before=old, after=new), helper_sha256=sha(Path(__file__)),
                  final_working_tree_clean=not bool(run(clone, ['git', 'status', '--porcelain'])))
    (output/'results.json').write_text(json.dumps(record, indent=2)+'\n', encoding='utf-8')
    (output/'helper_snapshot.py').write_bytes(Path(__file__).read_bytes())
    print(json.dumps(record, indent=2))

if __name__ == '__main__':
    main()
