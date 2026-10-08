"""Validate one returned JSON against packet identity and source conventions."""
import argparse
from pathlib import Path
import workflow as W


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--packet', type=Path, required=True)
    p.add_argument('--return-file', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    args = p.parse_args()
    packet = W.check_packet(args.packet)
    data = None
    try:
        data = W.read(args.return_file)
        errors = W.validate_return(data, packet, W.code_universe())
    except (KeyError, TypeError, ValueError, AttributeError) as error:
        errors = [f'Malformed JSON/return: {error}']
    W.write(args.out, dict(status='Verified computation' if not errors else 'Failed', valid=not errors,
                           evidence_status=data.get('evidence_status') if isinstance(data, dict) else None,
                           errors=errors, packet_sha256=packet['packet_sha256'], return_sha256=W.sha(args.return_file),
                           script_sha256=W.sha(__file__)))
    print('Valid returned reading' if not errors else '\n'.join(errors))
    raise SystemExit(0 if not errors else 1)
