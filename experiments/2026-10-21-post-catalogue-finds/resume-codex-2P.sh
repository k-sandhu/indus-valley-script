#!/usr/bin/env bash
# Manual resume of Codex run 2P (session 01a15cc1-066b-7fe1-af8f-a5b060de7c75) after the disk-space stop of 21 October 2026. No scheduling or automation.
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
PKG="$ROOT/experiments/2026-10-21-post-catalogue-finds"
LOG="$ROOT/data/raw/2026-10-21-post-catalogue-finds/codex/run2P"
echo "resume $(date -u +%FT%TZ) session 01a15cc1-066b-7fe1-af8f-a5b060de7c75" >> "$LOG/launches.txt"
cd "$ROOT"
codex exec resume -m gpt-6.1-sol -c model_reasoning_effort=xhigh -c 'sandbox_mode="workspace-write"' -o "$LOG/final.md" 01a15cc1-066b-7fe1-af8f-a5b060de7c75 - < "$PKG/RESUME-2.md" >> "$LOG/codex.log" 2>&1
STATUS=$?
echo "end $(date -u +%FT%TZ) exit=$STATUS (resumed)" >> "$LOG/launches.txt"
exit $STATUS
