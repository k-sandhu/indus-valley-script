#!/usr/bin/env bash
# Manual follow-up for one finished Codex work package, resuming its session.
# Usage: bash experiments/2026-10-06-research-program/resume.sh <name> <session-id> <followup-file> <owned-dir> <raw-dir> <model> <effort> <log-dir> [extra-writable-dir]
set -uo pipefail
ROOT="C:/Users/sandh/OneDrive/Projects/indus_valley_script"
NAME="$1"; SESSION="$2"; FOLLOWUP="$3"; OWNED="$ROOT/$4"; RAW="$ROOT/$5"; MODEL="$6"; EFFORT="$7"; LOGDIR="$8"; EXTRA="${9:-}"
ROOTS="\"$RAW\""
if [ -n "$EXTRA" ]; then ROOTS="$ROOTS, \"$EXTRA\""; fi
echo "resume-start $(date -u +%FT%TZ) $NAME $SESSION" >> "$LOGDIR/launches.txt"
cd "$OWNED"
codex exec resume "$SESSION" -m "$MODEL" -c "model_reasoning_effort=$EFFORT" -c 'web_search="live"' \
  -c 'sandbox_mode="workspace-write"' -c sandbox_workspace_write.network_access=true \
  -c "sandbox_workspace_write.writable_roots=[$ROOTS]" \
  -o "$LOGDIR/$NAME.resume.final.md" - < "$FOLLOWUP" 2>&1 | gzip -6 > "$LOGDIR/$NAME.resume.log.gz"
STATUS=${PIPESTATUS[0]}
echo "resume-end $(date -u +%FT%TZ) $NAME exit=$STATUS" >> "$LOGDIR/launches.txt"
exit $STATUS
