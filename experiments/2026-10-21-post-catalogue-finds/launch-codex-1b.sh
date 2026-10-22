#!/usr/bin/env bash
# Manual launcher for Codex run 1B of the post-catalogue finds package. No scheduling or automation.
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
PKG="$ROOT/experiments/2026-10-21-post-catalogue-finds"
LOG="$ROOT/data/raw/2026-10-21-post-catalogue-finds/codex/run1b"
mkdir -p "$LOG"
echo "start $(date -u +%FT%TZ) gpt-6.1-sol xhigh run1b" >> "$LOG/launches.txt"
cd "$ROOT"
codex exec -m gpt-6.1-sol -c model_reasoning_effort=xhigh -c sandbox_workspace_write.network_access=true -c 'web_search="live"'   -s workspace-write -C "$ROOT" -o "$LOG/final.md" - < "$PKG/CODEX-PROMPT-1B.md" > "$LOG/codex.log" 2>&1
STATUS=$?
echo "end $(date -u +%FT%TZ) exit=$STATUS" >> "$LOG/launches.txt"
exit $STATUS
