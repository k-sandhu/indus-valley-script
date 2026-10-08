"""Check the review amendments and preservation without rerunning inference."""
import argparse
import json
from pathlib import Path
import apply_v3_review as a


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    out = args.out.resolve()
    if out.exists() or not out.is_relative_to(a.HERE):
        raise ValueError('Use a new output file in the owned directory')
    pins = a.read(a.DEFAULT / 'preservation-check.json')['hashes']
    checks = {'all_protected_hashes_unchanged': all(a.sha(a.HERE/p) == h for p,h in pins.items())}
    before = {p:a.sha(a.HERE/p) for p in a.DOCS}
    import write_v3_endpoint_docs
    write_v3_endpoint_docs.main()
    checks['documentation_regeneration_identical'] = before == {p:a.sha(a.HERE/p) for p in a.DOCS}
    for name in ['README.md', 'REPORT.md']:
        s = (a.HERE/name).read_text(encoding='utf-8')
        checks[name+'_reference_provenance'] = all(x in s for x in ['no human check', 'field-block cue', 'Claude Sonnet 5.5'])
        checks[name+'_sensitivities'] = all(x in s for x in ['64/80', '65/80', '71.3\u201388.3%'])
        checks[name+'_window_correction'] = 'seven shifted' not in s and 'windows 3\u20136' in s
        checks[name+'_adjacent_table_rows'] = '|\n\n|' not in s
    s = (a.HERE/'sources.json').read_text(encoding='utf-8')
    checks['source_encoding_clean'] = all(x not in s for x in ['\u00e2\u20ac\u201c', '\u00e2\u0080\u0093', '\ufffd'])
    checks['opening_superseded'] = 'Superseded preparation status' in (a.HERE/'RETROSPECTIVE.md').read_text(encoding='utf-8')
    result = dict(status='Verified computation' if all(checks.values()) else 'Failed', checks=checks,
                  passed=sum(checks.values()), total=len(checks), protected_file_count=len(pins), source_en_dashes=s.count('\u2013'))
    a.dump(out, result)
    print(json.dumps({k:result[k] for k in ['status', 'passed', 'total', 'protected_file_count']}))
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == '__main__':
    main()
