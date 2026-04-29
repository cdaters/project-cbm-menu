#!/bin/bash
set -euo pipefail

VERSION="${1:-6.5}"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIST_DIR="$ROOT_DIR/dist"
STAGE_DIR="$DIST_DIR/Project-CBM-v${VERSION}-Bundle"
ZIP_PATH="$DIST_DIR/Project-CBM-v${VERSION}-Bundle.zip"

rm -rf "$STAGE_DIR" "$ZIP_PATH"
mkdir -p "$STAGE_DIR" "$DIST_DIR"

cp "$ROOT_DIR/LICENSE" "$STAGE_DIR/"
cp "$ROOT_DIR/README.md" "$STAGE_DIR/README-FIRST.txt"
cp "$ROOT_DIR/CHANGELOG.md" "$STAGE_DIR/REVISION-NOTES.txt"
cp "$ROOT_DIR/docs/Project CBM v${VERSION} Build Notes and Documentation.md" "$STAGE_DIR/" 2>/dev/null ||   cp "$ROOT_DIR/docs/Project CBM v6.5 Build Notes and Documentation.md" "$STAGE_DIR/"
cp "$ROOT_DIR/docs/AUDIT-NOTES.md" "$STAGE_DIR/"

rsync -a --delete   --exclude='.DS_Store' --exclude='._*' --exclude='__MACOSX'   "$ROOT_DIR/scripts/" "$STAGE_DIR/scripts/"
rsync -a --delete   --exclude='.DS_Store' --exclude='._*' --exclude='__MACOSX'   "$ROOT_DIR/configs/" "$STAGE_DIR/configs/"

if [[ -d "$ROOT_DIR/covers" ]]; then
  rsync -a --delete     --exclude='.DS_Store' --exclude='._*' --exclude='__MACOSX'     "$ROOT_DIR/covers/" "$STAGE_DIR/covers/"
fi

find "$STAGE_DIR/scripts" -type f -exec chmod 755 {} \;
find "$STAGE_DIR/configs" -type f -exec chmod 644 {} \;
chmod 755 "$STAGE_DIR/configs/99-pcbm" 2>/dev/null || true

(
  cd "$DIST_DIR"
  zip -qr "$(basename "$ZIP_PATH")" "$(basename "$STAGE_DIR")"
)

printf 'Built: %s
' "$ZIP_PATH"
