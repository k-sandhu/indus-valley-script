#!/usr/bin/env bash
# Manual resume of Codex run 4 (session 01a15d68-e990-7760-9328-a836bc892c46) for the re-check of the revised list of 21 October 2026. No scheduling or automation.
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
PKG="$ROOT/experiments/2026-10-21-post-catalogue-finds"
LOG="$ROOT/data/raw/2026-10-21-post-catalogue-finds/codex/run4"
echo "resume $(date -u +%FT%TZ) session 01a15d68-e990-7760-9328-a836bc892c46" >> "$LOG/launches.txt"
cd "$ROOT"
codex exec resume -m gpt-6.1-sol -c model_reasoning_effort=xhigh -c 'sandbox_mode="workspace-write"' -o "$LOG/final.md" 01a15d68-e990-7760-9328-a836bc892c46 - < "$PKG/RECHECK-4B.md" >> "$LOG/codex.log" 2>&1
STATUS=$?
echo "end $(date -u +%FT%TZ) exit=$STATUS (recheck-b)" >> "$LOG/launches.txt"
exit $STATUS
