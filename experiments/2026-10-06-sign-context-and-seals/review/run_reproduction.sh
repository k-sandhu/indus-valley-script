#!/usr/bin/env bash
# Reviewer reproduction of the D2 README commands. Run from the repository root.
# Every output goes to experiments/2026-10-06-sign-context-and-seals/review/ (aggregates)
# or data/raw/2026-10-06-sign-context-and-seals/review/ (local-only arrays and logs).
set -u
export PYTHONDONTWRITEBYTECODE=1
RAWREV="$(pwd)/data/raw/2026-10-06-sign-context-and-seals/review"
export TMP="$RAWREV/tmp" TEMP="$RAWREV/tmp" MPLCONFIGDIR="$RAWREV/tmp"
PKG=experiments/2026-10-06-sign-context-and-seals
LOG="$RAWREV/reproduction.log"
step() { echo "=== $(date -u +%FT%TZ) :: $*" | tee -a "$LOG"; }
step "analyze.py (primary run)"
python $PKG/analyze.py --run review/rerun-primary 2>&1 | tee -a "$LOG"
step "verify.py"
python $PKG/verify.py --replicate review/rerun-primary --output review/reviewer-checks-2026-10-07-01.json 2>&1 | tee -a "$LOG"
step "sensitivity.py"
python $PKG/sensitivity.py --run review/rerun-exploratory 2>&1 | tee -a "$LOG"
step "supplement.py"
python $PKG/supplement.py --run review/rerun-supplement 2>&1 | tee -a "$LOG"
step "finish_checks.py"
python $PKG/finish_checks.py --exploratory review/rerun-exploratory --supplement review/rerun-supplement --output review/reviewer-final-checks-2026-10-07-01.json 2>&1 | tee -a "$LOG"
step "lecture_followup.py"
python $PKG/lecture_followup.py --run review/rerun-postlaunch 2>&1 | tee -a "$LOG"
step "verify_followup.py"
python $PKG/verify_followup.py --replicate review/rerun-postlaunch --output review/reviewer-post-launch-checks-2026-10-07.json 2>&1 | tee -a "$LOG"
step "done"
