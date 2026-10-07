"""Read-only check of Package L's revised occurrence/suffix contract."""
import argparse
from collections import Counter
import importlib.util
import json
from pathlib import Path
import re
import sys
sys.dont_write_bytecode=True
import jsonschema

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
LEDGER=ROOT/'experiments/2026-10-07-object-ledger'


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,default=HERE/'follow-up/2026-10-07/ledger-interface-v2.json');args=ap.parse_args()
    out=args.out.resolve()
    if not out.is_relative_to(HERE) or out.exists():raise ValueError('Choose a new owned output')
    sys.path.insert(0,str(LEDGER))
    source=LEDGER/'import_helsinki1979_v2.py';spec=importlib.util.spec_from_file_location('ledger_occurrence_contract',source)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    schema=module.interface_schema()
    validator=jsonschema.Draft202012Validator({'$ref':'#/$defs/digitized_row','$defs':schema['$defs']})
    regular=[];suffix=[]
    with (HERE/'integration/2026-10-07-v1/ledger-import.jsonl').open(encoding='utf-8') as stream:
        for line in stream:
            row=json.loads(line)
            if row['text_number'] is not None and len(regular)<60:regular.append(row)
            if re.fullmatch(r'\d+[A-Za-z]+',row['text_number'] or '') and len(suffix)<3:suffix.append(row)
            if len(regular)==60 and len(suffix)==3:break
    rows=regular+suffix
    rows=list({r['segment_id']:r for r in rows}.values())
    errors={r['segment_id']:[e.message for e in validator.iter_errors(r)] for r in rows}
    ledger=json.loads((LEDGER/'run-2026-10-07-v4/ledger-public.json').read_text(encoding='utf-8'))
    accepted,quarantine=module.import_rows(rows,[],ledger)
    reasons=Counter(reason for r in quarantine for reason in r['reasons'])
    import hashlib
    digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    checks=dict(schema_passes=not any(errors.values()),suffixes_exercised=len(suffix)==3,
                distinct_occurrence_segments=len({r['segment_id'] for r in rows})==len(rows),
                none_imported_without_concordance=len(accepted)==0,all_quarantined=len(quarantine)==len(rows))
    result=dict(status='Verified computation' if all(checks.values()) else 'Failed',checks=checks,
        real_provisional_rows=len(rows),suffix_examples=[r['text_number'] for r in suffix],
        suffix_note='Recognized provisional strings, not visually authenticated numbers',
        accepted=len(accepted),quarantined=len(quarantine),reasons=dict(reasons),errors=errors,
        importer_sha256=digest(source),ledger_sha256=digest(LEDGER/'run-2026-10-07-v4/ledger-public.json'),
        available_contract='HELSINKI-INTERFACE.md and AMENDMENT-2026-10-07-review-response.md',
        requested_IMPORT_INTERFACE_present=(LEDGER/'IMPORT_INTERFACE.md').exists(),external_writes=False)
    out.write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))
    if not all(checks.values()):raise SystemExit(1)


if __name__=='__main__':main()
