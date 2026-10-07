#!/bin/bash
cd /c/Users/sandh/OneDrive/Projects/indus_valley_script
PKG=experiments/2026-10-07-helsinki1979-digitization
PY="C:/Users/sandh/.venvs/indus-ml/Scripts/python.exe"
LOG=$PKG/review/reviewer-check/logs
echo "start evaluate $(date -Iseconds)" > $LOG/repro-times.txt
$PY $PKG/evaluate.py --out $PKG/review/reviewer-check/evaluation-recompute > $LOG/evaluate-stdout.txt 2> $LOG/evaluate-stderr.txt
echo "evaluate exit $? $(date -Iseconds)" >> $LOG/repro-times.txt
echo "start rerun_frozen_sample $(date -Iseconds)" >> $LOG/repro-times.txt
$PY $PKG/rerun_frozen_sample.py --predictions-out data/raw/2026-10-07-helsinki1979-digitization/reviewer-sample-v3.json --audit-out $PKG/review/reviewer-check/sample-rerun-reviewer.json > $LOG/rerun-stdout.txt 2> $LOG/rerun-stderr.txt
echo "rerun exit $? $(date -Iseconds)" >> $LOG/repro-times.txt
echo "start verify $(date -Iseconds)" >> $LOG/repro-times.txt
$PY $PKG/verify.py --out $PKG/review/reviewer-check/verify-reviewer.json > $LOG/verify-stdout.txt 2> $LOG/verify-stderr.txt
echo "verify exit $? $(date -Iseconds)" >> $LOG/repro-times.txt
