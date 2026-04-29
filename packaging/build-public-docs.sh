#!/bin/bash
set -euo pipefail

VERSION="${1:-}"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ -z "$VERSION" ]]; then
  if [[ -f "$ROOT_DIR/PUBLIC_VERSION" ]]; then
    VERSION="$(tr -d '[:space:]' < "$ROOT_DIR/PUBLIC_VERSION")"
  else
    VERSION="1.0.0"
  fi
fi

SRC_DIR="$ROOT_DIR/public-docs"
DIST_DIR="$ROOT_DIR/dist"
DOCS_NAME="pcbm-v${VERSION}-docs"
DOCS_DIR="$DIST_DIR/$DOCS_NAME"
ZIP_PATH="$DIST_DIR/${DOCS_NAME}.zip"

if [[ ! -d "$SRC_DIR" ]]; then
  echo "Error: public-docs directory not found: $SRC_DIR" >&2
  exit 1
fi

rm -rf "$DOCS_DIR" "$ZIP_PATH"
mkdir -p "$DOCS_DIR"

rsync -a \
  --exclude='.DS_Store' \
  --exclude='._*' \
  --exclude='__MACOSX' \
  --exclude='.gitkeep' \
  "$SRC_DIR/" "$DOCS_DIR/"

find "$DOCS_DIR" -name '.DS_Store' -delete
find "$DOCS_DIR" -name '._*' -delete
find "$DOCS_DIR" -name '.gitkeep' -delete

(
  cd "$DIST_DIR"
  zip -qr "${DOCS_NAME}.zip" "$DOCS_NAME"
)

echo "Built: $ZIP_PATH"
