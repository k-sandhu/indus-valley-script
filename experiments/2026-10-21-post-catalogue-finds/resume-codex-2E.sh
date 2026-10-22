#!/usr/bin/env bash
# Manual resume of Codex run 2E (session 01a15d22-5627-7932-a6bb-46e9a279ee35) after the model-capacity stop of 21 October 2026. No scheduling or automation.
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
PKG="$ROOT/experiments/2026-10-21-post-catalogue-finds"
LOG="$ROOT/data/raw/2026-10-21-post-catalogue-finds/codex/run2E"
echo "resume $(date -u +%FT%TZ) session 01a15d22-5627-7932-a6bb-46e9a279ee35" >> "$LOG/launches.txt"
cd "$ROOT"
codex exec resume -m gpt-6.1-sol -c model_reasoning_effort=xhigh -c 'sandbox_mode="workspace-write"' -o "$LOG/final.md" 01a15d22-5627-7932-a6bb-46e9a279ee35 - < "$PKG/RESUME-CAPACITY.md" >> "$LOG/codex.log" 2>&1
STATUS=$?
echo "end $(date -u +%FT%TZ) exit=$STATUS (resumed)" >> "$LOG/launches.txt"
exit $STATUS
