"""Reviewer comparison of a fresh rerun against the package's saved endpoint.

Usage: python compare_outputs.py AUTHOR_DIR REVIEWER_DIR [--ignore key1,key2]
Compares every .json and .csv file present in AUTHOR_DIR with the file of the
same name in REVIEWER_DIR. Floats use a relative tolerance of 1e-9. Keys that
carry timings, hashes of changed locations, run names or file listings are
ignored. Prints one line per file and the first differences.
"""
import sys, json, math, csv
from pathlib import Path

IGNORE = {'elapsed_seconds', 'local_details', 'aggregate_files', 'files', 'generated_utc', 'files_sha256', 'sha256',
          'code_sha256', 'analyzer_sha256', 'amendment_sha256', 'input_sha256', 'protocol_sha256', 'clarification_sha256',
          'reused_group_code_sha256', 'reused_analyzer_sha256', 'coordinator_caption_check_sha256', 'run', 'source_run',
          'verification', 'coverage_directory', 'assay_run', 'immutable_assay_files'}
diffs = []

def close(a, b):
    if a == b: return True
    if isinstance(a, (int, float)) and isinstance(b, (int, float)) and not isinstance(a, bool) and not isinstance(b, bool):
        return math.isclose(a, b, rel_tol=1e-9, abs_tol=1e-12)
    return False

def cmp(a, b, path, ignore):
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b), key=str):
            if k in ignore: continue
            if k not in a: diffs.append((path + '/' + str(k), 'missing in author', None)); continue
            if k not in b: diffs.append((path + '/' + str(k), None, 'missing in reviewer')); continue
            cmp(a[k], b[k], path + '/' + str(k), ignore)
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b): diffs.append((path, 'len %d' % len(a), 'len %d' % len(b))); return
        for i, (x, y) in enumerate(zip(a, b)): cmp(x, y, path + '[%d]' % i, ignore)
    else:
        if not close(a, b): diffs.append((path, a, b))

def read_csv(p):
    with open(p, encoding='utf-8', newline='') as f: return list(csv.reader(f))

def main():
    a_dir, b_dir = Path(sys.argv[1]), Path(sys.argv[2])
    ignore = set(IGNORE)
    if '--ignore' in sys.argv: ignore |= set(sys.argv[sys.argv.index('--ignore') + 1].split(','))
    total_files = 0; same_files = 0; total_leaves = 0
    for p in sorted(a_dir.iterdir()):
        if p.suffix not in ('.json', '.csv'): continue
        q = b_dir / p.name
        total_files += 1
        if not q.exists():
            print('MISSING in reviewer:', p.name); continue
        diffs.clear()
        if p.suffix == '.json':
            cmp(json.loads(p.read_text(encoding='utf-8')), json.loads(q.read_text(encoding='utf-8')), '', ignore)
        else:
            ra, rb = read_csv(p), read_csv(q)
            if len(ra) != len(rb): diffs.append(('rows', len(ra), len(rb)))
            else:
                for i, (x, y) in enumerate(zip(ra, rb)):
                    if x != y:
                        if len(x) != len(y): diffs.append(('row %d' % i, x, y)); continue
                        for j, (u, v) in enumerate(zip(x, y)):
                            if u != v:
                                try:
                                    if not close(float(u), float(v)): diffs.append(('row %d col %s' % (i, ra[0][j]), u, v))
                                except ValueError:
                                    diffs.append(('row %d col %s' % (i, ra[0][j]), u, v))
        if not diffs: same_files += 1
        print(('SAME ' if not diffs else 'DIFF ') + p.name + ('' if not diffs else '  (%d differences)' % len(diffs)))
        for d in diffs[:6]: print('      ', d)
    print('files compared: %d; identical: %d' % (total_files, same_files))

if __name__ == '__main__':
    main()
