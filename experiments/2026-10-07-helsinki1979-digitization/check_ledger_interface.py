"""Exercise Package L's pure importer on 60 staged rows, without writing there."""
import argparse
import hashlib
import importlib.util
import itertools
import json
import sys
from collections import Counter
from importlib.metadata import version
from pathlib import Path

sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
LEDGER_PACKAGE=ROOT/'experiments/2026-10-07-object-ledger'


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--rows',type=Path,default=HERE/'integration/2026-10-07-v1/ledger-import.jsonl')
    ap.add_argument('--ledger',type=Path,default=LEDGER_PACKAGE/'run-2026-10-07-v2/ledger-public.json')
    ap.add_argument('--out',type=Path,default=HERE/'integration/l-interface-check-v1.json');args=ap.parse_args()
    out=args.out.resolve()
    if not out.is_relative_to(HERE) or out.exists():raise ValueError('Audit output must be new and owned')
    with args.rows.open(encoding='utf-8') as stream:rows=[json.loads(line) for line in itertools.islice(stream,60)]
    assert len(rows)==60
    ledger=json.loads(args.ledger.read_text(encoding='utf-8'))
    sys.path.insert(0,str(LEDGER_PACKAGE))
    source=LEDGER_PACKAGE/'import_helsinki1979.py'
    spec=importlib.util.spec_from_file_location('package_l_importer_read_only',source)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    accepted,quarantined=module.import_rows(rows,[],ledger)
    reasons=Counter(reason for row in quarantined for reason in row['reasons'])
    checks=dict(sixty_rows_checked=len(rows)==60,none_accepted_without_crosswalk=len(accepted)==0,
                all_quarantined=len(quarantined)==60,
                interface_fields_present='missing digitization interface field' not in reasons,
                rights_passed='missing exact CC BY license, attribution, source or transformation record' not in reasons,
                segments_distinct=len({r['segment_id'] for r in rows})==60)
    result=dict(status='Verified computation' if all(checks.values()) else 'Failed',checks=checks,
                accepted=len(accepted),quarantined=len(quarantined),reasons=dict(reasons),
                sample_rule='first60 staged source occurrences; interface exercise, not accuracy sample',
                importer_sha256=sha(source),ledger_sha256=sha(args.ledger),staged_payload_sha256=sha(args.rows),
                interface_dependencies={name:version(name) for name in ('jsonschema','attrs','jsonschema-specifications','referencing','rpds-py')},
                code_sha256=sha(__file__),external_writes=False)
    out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))
    if not all(checks.values()):raise SystemExit(1)


if __name__=='__main__':main()
