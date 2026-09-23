#!/usr/bin/env bash
# The repo is the source of truth. This validates it, then copies it one-way to
# the path the Artifact is published from. Never copy back the other way: doing
# so once silently reverted a fix that had already passed validation.
#
#   ./sync-artifact.sh <publish-path>        or   ARTIFACT_DEST=<path> ./sync-artifact.sh
#
# The target used to default to one session's scratch directory, which does not
# exist in any other session; it is now passed in.
set -euo pipefail
DEST="${1:-${ARTIFACT_DEST:-}}"
if [ -z "$DEST" ]; then
  echo "usage: $0 <publish-path>   (or set ARTIFACT_DEST)" >&2
  exit 2
fi
cd "$(dirname "$0")"
python3 validate.py
cp allocation.html "$DEST"
echo "synced -> $DEST"
cmp -s allocation.html "$DEST" && echo "verified identical"
