"""Reviewer runner for the D1 package.

Runs the package's own scripts unchanged (they are imported from the package
directory) while redirecting only their aggregate output directory from the
package directory to review/rerun/. Record-level details go to the package's
local raw directory under fresh reviewer-* names, as the package scripts do.

The package scripts hard-code their output location as <package directory>/<run name>.
This runner points `analyze.OWN` (and the copies of it bound by the other scripts) at
review/rerun/ and copies the byte-identical protocol and code files that the scripts hash
into that directory before the first run.

Usage (from the repository root):
  python -B experiments/2026-10-06-chronology-region/review/run_review_step.py STEP [script args...]
STEP is one of: analyze, verify, supplement, verify_supplement, post_launch, verify_post_launch
Commands used for the review (run in this order):
  analyze --run reviewer-main-v1
  verify --run reviewer-main-v1 --output reviewer-verification-v1.json
  supplement --main reviewer-main-v1 --run reviewer-exploratory-v1
  verify_supplement --main reviewer-main-v1 --supplement reviewer-exploratory-v1 --output reviewer-supplement-verification-v1.json
  post_launch --run reviewer-post-launch-v1
  verify_post_launch --run reviewer-post-launch-v1 --output reviewer-post-launch-verification-v1.json --coverage reviewer-post-launch-coverage-v1
"""
import os, sys, time, shutil
from pathlib import Path

sys.dont_write_bytecode = True
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
PKG = Path(__file__).resolve().parents[1]
REV = PKG / 'review' / 'rerun'
sys.path.insert(0, str(PKG))

# byte-identical copies that the package scripts hash or read from their own directory
REV.mkdir(parents=True, exist_ok=True)
for name in ['PROTOCOL.md', 'PRECOMPUTATION_CLARIFICATION.md', 'analyze.py', 'post_launch.py', 'supplement.py',
             'POST-LAUNCH-PROTOCOL-2026-10-07.md', 'AMENDMENT-2026-10-07.md']:
    if not (REV / name).exists(): shutil.copyfile(PKG / name, REV / name)
if not (REV / 'post-launch-document-baseline-2026-10-07-v1').exists():
    shutil.copytree(PKG / 'post-launch-document-baseline-2026-10-07-v1', REV / 'post-launch-document-baseline-2026-10-07-v1')

step, rest = sys.argv[1], sys.argv[2:]
sys.argv = [step + '.py'] + rest

import analyze as base            # package module, unmodified
base.OWN = REV                    # aggregates land in review/rerun/<run>

t0 = time.time()
if step == 'analyze':
    base.main()
elif step == 'verify':
    import verify as m
    m.OWN = REV
    m.main()
elif step == 'supplement':
    import supplement as m        # binds OWN from analyze (already patched)
    assert m.OWN == REV
    m.main()
elif step == 'verify_supplement':
    import verify_supplement as m
    m.OWN = REV
    m.main()
elif step == 'post_launch':
    import post_launch as m
    assert m.OWN == REV
    m.main()
elif step == 'verify_post_launch':
    import post_launch            # imported by the verifier itself, must see the patched OWN
    import verify_post_launch as m
    m.main()
else:
    raise SystemExit('unknown step ' + step)
print('STEP', step, 'finished in %.1f s' % (time.time() - t0), flush=True)
