"""Redirect preserved D1 scripts without editing them.

--output-dir is an aggregate root within the repository, outside the package if
desired. Run names remain single components. Record-level files stay in the
assigned local raw directory. This adapter reuses review/run_review_step.py's
bound-module redirection and stages the original, archived protocol.
"""
from __future__ import annotations
import argparse, importlib, os, shutil, sys
from pathlib import Path

sys.dont_write_bytecode=True
OWN=Path(__file__).resolve().parent
ROOT=OWN.parents[1]
STEPS=['analyze','verify','supplement','verify_supplement','post_launch',
       'check_catalogue_join','acquire_sources','acquire_post_launch_sources']

def main():
    parser=argparse.ArgumentParser(description=__doc__,allow_abbrev=False)
    parser.add_argument('step',choices=STEPS)
    parser.add_argument('--output-dir',required=True)
    args,rest=parser.parse_known_args()
    output=Path(args.output_dir).resolve()
    if output==OWN or not output.is_relative_to(ROOT):
        raise ValueError('Use an output root inside the repository and outside the package root.')
    if args.step.startswith('acquire_') and not output.is_relative_to(ROOT/'data/raw/2026-10-06-chronology-region'):
        raise ValueError('Third-party payloads must use the assigned local raw directory.')
    output.mkdir(parents=True,exist_ok=True)
    files=['PROTOCOL.md','PRECOMPUTATION_CLARIFICATION.md','analyze.py','post_launch.py','supplement.py',
           'POST-LAUNCH-PROTOCOL-2026-10-07.md','AMENDMENT-2026-10-07.md']
    for name in files:
        source=OWN/('review-response-baseline-2026-10-07-v1/PROTOCOL.md' if name=='PROTOCOL.md' else name)
        destination=output/name
        if destination.exists():
            if destination.read_bytes()!=source.read_bytes(): raise ValueError(f'Staged file differs: {destination}')
        else: shutil.copyfile(source,destination)
    # The preserved follow-up reads the saved first-pass aggregate endpoint.
    if args.step in ['post_launch','supplement'] and not (output/'main-2026-10-07-v1').exists():
        shutil.copytree(OWN/'main-2026-10-07-v1',output/'main-2026-10-07-v1')
    import analyze as base
    base.OWN=output
    module=base if args.step=='analyze' else importlib.import_module(args.step)
    if hasattr(module,'OWN'): module.OWN=output
    # Source acquisition has only raw payloads; redirect its output to this root.
    if args.step.startswith('acquire_'): module.RAW=output
    sys.argv=[args.step+'.py',*rest]
    module.main()

if __name__=='__main__': main()
