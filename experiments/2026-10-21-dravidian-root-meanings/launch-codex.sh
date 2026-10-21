#!/usr/bin/env bash
# Manual launcher for run 1 of the Dravidian root-meanings study by Codex CLI. No scheduling or automation.
# The run needs the network (figshare, Zenodo, DSAL), so web search and sandbox network access are enabled.
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
PKG="$ROOT/experiments/2026-10-21-dravidian-root-meanings"
LOG="$ROOT/data/raw/2026-10-21-dravidian-root-meanings/codex-logs/run1"
mkdir -p "$LOG"
echo "start $(date -u +%FT%TZ) gpt-6.1-sol xhigh run1" >> "$LOG/launches.txt"
cd "$ROOT"
codex exec -m gpt-6.1-sol -c model_reasoning_effort=xhigh -c 'web_search="live"' \
  -s workspace-write -c sandbox_workspace_write.network_access=true \
  -C "$ROOT" -o "$LOG/final.md" - < "$PKG/CODEX-PROMPT.md" > "$LOG/codex.log" 2>&1
STATUS=$?
echo "end $(date -u +%FT%TZ) exit=$STATUS" >> "$LOG/launches.txt"
exit $STATUS
