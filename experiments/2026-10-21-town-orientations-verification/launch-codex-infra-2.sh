#!/usr/bin/env bash
# Manual launcher for the second infra run by Codex CLI. No scheduling or automation.
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
PKG="$ROOT/experiments/2026-10-21-town-orientations-verification"
LOG="$ROOT/data/raw/2026-10-21-town-orientations-verification/codex/infra-2"
mkdir -p "$LOG"
echo "start $(date -u +%FT%TZ) gpt-6.1-sol xhigh prompt_sha256=$(sha256sum "$PKG/CODEX-PROMPT-INFRA-2.md" | cut -d' ' -f1)" >> "$LOG/launches.txt"
cd "$ROOT"
codex exec -m gpt-6.1-sol -c model_reasoning_effort=xhigh   -c sandbox_workspace_write.network_access=true   -s workspace-write -C "$ROOT" -o "$LOG/final.md" - < "$PKG/CODEX-PROMPT-INFRA-2.md" > "$LOG/codex.log" 2>&1
STATUS=$?
echo "end $(date -u +%FT%TZ) exit=$STATUS" >> "$LOG/launches.txt"
exit $STATUS
