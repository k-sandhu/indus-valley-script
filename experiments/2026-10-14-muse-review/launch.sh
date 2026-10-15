#!/usr/bin/env bash
# Run one Muse Wonder Full review lens, read-only, against the repository.
# Usage, from the repository root in Git Bash:
#   bash experiments/2026-10-14-muse-review/launch.sh a-structure|b-process|c-ambition <out-dir>
# Reports were written outside the repository and copied into reports/ afterwards.
set -u
LENS="$1"
OUT="$2"
HERE="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$HERE/../.." && pwd)"
MUSE="${MUSE:-$LOCALAPPDATA/Programs/muse/muse.cmd}"
mkdir -p "$OUT"
cat "$HERE/prompts/common.md" "$HERE/prompts/lens-$LENS.md" > "$OUT/prompt-$LENS.md"
cd "$REPO" || exit 1
"$MUSE" exec \
  --model muse-wonder-full-1.0 \
  --reasoning-effort xhigh \
  --contributor-mode off \
  --workspace "$REPO" \
  --disable-write \
  --disable-web-tools \
  --approval-mode never \
  --no-foreign-personal-context \
  --prompt-file "$OUT/prompt-$LENS.md" \
  > "$OUT/report-$LENS.md" 2> "$OUT/stderr-$LENS.log"
echo "exit=$?" >> "$OUT/stderr-$LENS.log"
