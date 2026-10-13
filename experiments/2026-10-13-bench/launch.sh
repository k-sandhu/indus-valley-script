#!/usr/bin/env bash
# Manual launcher for the phase-1 restructure by Codex CLI. No scheduling or automation.
set -uo pipefail
ROOT="C:/Users/sandh/OneDrive/Projects/indus_valley_script"
PKG="$ROOT/experiments/2026-10-13-bench"
LOG="$ROOT/data/raw/2026-10-13-bench"
mkdir -p "$LOG"
echo "start $(date -u +%FT%TZ) gpt-6.1-sol xhigh" >> "$LOG/launches.txt"
cd "$ROOT"
codex exec -m gpt-6.1-sol -c model_reasoning_effort=xhigh -c 'web_search="live"' \
  -s workspace-write -C "$ROOT" -o "$LOG/final.md" - < "$PKG/CODEX-PROMPT.md" > "$LOG/codex.log" 2>&1
STATUS=$?
echo "end $(date -u +%FT%TZ) exit=$STATUS" >> "$LOG/launches.txt"
exit $STATUS
