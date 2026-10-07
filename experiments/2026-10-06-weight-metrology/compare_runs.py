"""Compare preserved numerical endpoints and local predictions byte for byte."""
import argparse
import json
from pathlib import Path
from parse_catalogue import ROOT, RUN, RAW, sha, write_json

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--actual',default='experiments/2026-10-06-weight-metrology/runs/2026-10-07-reproduction')
    ap.add_argument('--actual-raw',default='data/raw/2026-10-06-weight-metrology/reproduction')
    ap.add_argument('--output',default='experiments/2026-10-06-weight-metrology/reproduction.json')
    args=ap.parse_args(); actual=ROOT/args.actual; actualraw=ROOT/args.actual_raw; output=ROOT/args.output
    if output.exists(): raise FileExistsError(output)
    expected=RUN/'runs/2026-10-06-main'; expectedraw=RAW/'main'
    e=json.loads((expected/'manifest.json').read_text()); a=json.loads((actual/'manifest.json').read_text())
    for key in ['source_rows_sha256','analysis_sha256','protocol_sha256','models','bootstrap_iterations','mc_simulations']:
        assert e[key]==a[key],key
    ec=json.loads((expected/'completion.json').read_text()); ac=json.loads((actual/'completion.json').read_text())
    assert all(sha(actual/name)==digest for name,digest in ac['output_hashes'].items())
    names=[name for name in ec['output_hashes'] if name!='manifest.json']
    for name in names:
        assert sha(expected/name)==sha(actual/name),name
    raw_names=[p.relative_to(expectedraw).as_posix() for p in expectedraw.rglob('*') if p.is_file()]
    for name in raw_names:
        assert sha(expectedraw/name)==sha(actualraw/name),name
    write_json(output,{'status':'Verified computation','same_inputs_protocol_code':True,
        'numerical_files_byte_identical':names,'local_derivatives_byte_identical_n':len(raw_names),
        'actual_endpoint':args.actual,'actual_raw_endpoint':args.actual_raw,
        'reproduction_elapsed_seconds':ac['elapsed_seconds'],
        'limits':'Same-code reproduction, distinct from independent algorithm or page review.',
        'comparison_code_sha256':sha(Path(__file__))})
    print(output.read_text())

if __name__=='__main__': main()
