#!/bin/bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC_DIR="$ROOT_DIR/public-docs"
PUBLIC_REPO="${1:-../project-cbm}"
MODE="${2:---dry-run}"

if [[ ! -d "$SRC_DIR" ]]; then
  echo "Error: public-docs directory not found: $SRC_DIR" >&2
  exit 1
fi

if [[ ! -d "$PUBLIC_REPO/.git" ]]; then
  echo "Error: public repo not found or not a Git repo: $PUBLIC_REPO" >&2
  echo "Usage: ./packaging/sync-public-docs.sh ../project-cbm --dry-run" >&2
  echo "       ./packaging/sync-public-docs.sh ../project-cbm --apply" >&2
  exit 1
fi

case "$MODE" in
  --apply)
    RSYNC_FLAGS="-av"
    CP_FLAGS="-v"
    echo "Applying public docs sync to: $PUBLIC_REPO"
    ;;
  --dry-run|"")
    RSYNC_FLAGS="-avn"
    CP_FLAGS="-vn"
    echo "Dry run only. No files will be changed. Add --apply to copy files."
    ;;
  *)
    echo "Unknown mode: $MODE" >&2
    echo "Use --dry-run or --apply" >&2
    exit 1
    ;;
esac

# Top-level public documentation files. Only copy files that exist in public-docs.
for file in \
  ACKNOWLEDGEMENTS.md \
  CHANGELOG.md \
  CONTRIBUTING.md \
  LICENSE.md \
  README.md \
  README.txt \
  SUPPORT.md \
  "Project CBM End-User Guide.pdf"; do
  if [[ -f "$SRC_DIR/$file" ]]; then
    cp $CP_FLAGS "$SRC_DIR/$file" "$PUBLIC_REPO/$file" || true
  fi
done

mkdir -p "$PUBLIC_REPO/docs" "$PUBLIC_REPO/release-notes"

rsync $RSYNC_FLAGS \
  --delete \
  --exclude='.DS_Store' \
  --exclude='._*' \
  --exclude='__MACOSX' \
  "$SRC_DIR/docs/" "$PUBLIC_REPO/docs/"

rsync $RSYNC_FLAGS \
  --delete \
  --exclude='.DS_Store' \
  --exclude='._*' \
  --exclude='__MACOSX' \
  "$SRC_DIR/release-notes/" "$PUBLIC_REPO/release-notes/"

if [[ "$MODE" != "--apply" ]]; then
  echo
  echo "Dry run complete. To apply:"
  echo "  ./packaging/sync-public-docs.sh $PUBLIC_REPO --apply"
fi
