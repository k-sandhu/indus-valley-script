#!/usr/bin/env bash
# Launch record: run from Git Bash at the repository root.
set -euo pipefail
ROOT="C:/Users/sandh/OneDrive/Projects/indus_valley_script"
PKG="$ROOT/experiments/2026-10-27-site-organization"
codex exec -m gpt-6.1-sol -c model_reasoning_effort=xhigh -s workspace-write -C "$ROOT"   -o "$PKG/final.md" - < "$PKG/PROMPT.md" > "$PKG/codex-log.txt" 2>&1
