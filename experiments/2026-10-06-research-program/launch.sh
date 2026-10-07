#!/usr/bin/env bash
# Manual launcher for one Codex work package. No scheduling or automation.
# Usage: bash experiments/2026-10-06-research-program/launch.sh <prompt-name> <owned-dir> <raw-dir> <model> <effort> <log-dir> [extra-writable-dir]
set -euo pipefail
ROOT="C:/Users/sandh/OneDrive/Projects/indus_valley_script"
PROGRAM="$ROOT/experiments/2026-10-06-research-program"
NAME="$1"; OWNED="$ROOT/$2"; RAW="$ROOT/$3"; MODEL="$4"; EFFORT="$5"; LOGDIR="$6"; EXTRA="${7:-}"
mkdir -p "$OWNED" "$RAW" "$LOGDIR"
PROMPT="$LOGDIR/$NAME.prompt.md"
{ cat "$PROGRAM/COMMON.md"; printf '\n\n'; cat "$PROGRAM/prompts/$NAME.md"; } > "$PROMPT"
ARGS=(exec -m "$MODEL" -c "model_reasoning_effort=$EFFORT" -c 'web_search="live"'
      -s workspace-write -c sandbox_workspace_write.network_access=true
      -C "$OWNED" --add-dir "$RAW" -o "$LOGDIR/$NAME.final.md")
if [ -n "$EXTRA" ]; then ARGS+=(--add-dir "$EXTRA"); fi
echo "start $(date -u +%FT%TZ) $NAME $MODEL $EFFORT" >> "$LOGDIR/launches.txt"
cd "$ROOT"
codex "${ARGS[@]}" - < "$PROMPT" > "$LOGDIR/$NAME.log" 2>&1
STATUS=$?
echo "end $(date -u +%FT%TZ) $NAME exit=$STATUS" >> "$LOGDIR/launches.txt"
exit $STATUS
