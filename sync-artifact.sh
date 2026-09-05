#!/usr/bin/env bash
# The repo is the source of truth. This validates it, then copies it one-way to
# the path the Artifact is published from. Never copy back the other way: doing
# so once silently reverted a fix that had already passed validation.
set -euo pipefail
DEST="${1:-/tmp/claude-0/-home-user-ClaudeBinance/03fd2b85-d3cd-57ae-ac50-d8ddcb51334c/scratchpad/allocation.html}"
cd "$(dirname "$0")"
python3 validate.py
cp allocation.html "$DEST"
echo "synced -> $DEST"
cmp -s allocation.html "$DEST" && echo "verified identical"
