#!/usr/bin/env bash
# Manual launcher for Codex run c-statistics of the head-direction corpora package. No scheduling or automation.
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/../../../.." && pwd)"
RUN="$ROOT/experiments/2026-10-21-head-direction-corpora/codex/c-statistics"
LOG="$ROOT/data/raw/2026-10-21-head-direction-corpora/codex-c"
mkdir -p "$LOG"
echo "start $(date -u +%FT%TZ) gpt-6.1-sol xhigh" >> "$LOG/launches.txt"
cd "$ROOT"
codex exec -m gpt-6.1-sol -c model_reasoning_effort=xhigh    -s workspace-write -C "$ROOT" -o "$LOG/final.md" - < "$RUN/CODEX-PROMPT.md" > "$LOG/codex.log" 2>&1
STATUS=$?
echo "end $(date -u +%FT%TZ) exit=$STATUS" >> "$LOG/launches.txt"
exit $STATUS
