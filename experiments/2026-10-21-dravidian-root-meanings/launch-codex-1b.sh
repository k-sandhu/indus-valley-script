#!/usr/bin/env bash
# Manual launcher for the run 1b follow-up (parser repair), resuming the run 1 Codex session.
# No scheduling or automation. No network is needed: every page is already on disk with a logged hash.
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
PKG="$ROOT/experiments/2026-10-21-dravidian-root-meanings"
LOG="$ROOT/data/raw/2026-10-21-dravidian-root-meanings/codex-logs/run1b"
SESSION="01a15c7e-9f5a-7bc0-b789-23a5f3b77e54"
mkdir -p "$LOG"
echo "start $(date -u +%FT%TZ) gpt-6.1-sol xhigh run1b resume $SESSION" >> "$LOG/launches.txt"
cd "$ROOT"
codex exec resume "$SESSION" -m gpt-6.1-sol -c model_reasoning_effort=xhigh \
  -c 'sandbox_mode="workspace-write"' \
  -o "$LOG/final.md" - < "$PKG/CODEX-PROMPT-1B.md" > "$LOG/codex.log" 2>&1
STATUS=$?
echo "end $(date -u +%FT%TZ) exit=$STATUS" >> "$LOG/launches.txt"
exit $STATUS
