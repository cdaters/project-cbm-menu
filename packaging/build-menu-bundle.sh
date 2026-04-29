#!/bin/bash
set -euo pipefail

VERSION="${1:-}"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ -z "$VERSION" ]]; then
  if [[ -f "$ROOT_DIR/VERSION" ]]; then
    VERSION="$(tr -d '[:space:]' < "$ROOT_DIR/VERSION")"
  else
    VERSION="1.0.0"
  fi
fi

DIST_DIR="$ROOT_DIR/dist"
BUNDLE_NAME="Project-CBM-v${VERSION}-Bundle"
BUNDLE_DIR="$DIST_DIR/$BUNDLE_NAME"
ZIP_PATH="$DIST_DIR/${BUNDLE_NAME}.zip"

BUILD_NOTES_NEW="$ROOT_DIR/docs/Project CBM Menu v${VERSION} Build Notes and Documentation.md"
BUILD_NOTES_LEGACY="$ROOT_DIR/docs/Project CBM v6.5 Build Notes and Documentation.md"

rm -rf "$BUNDLE_DIR" "$ZIP_PATH"
mkdir -p "$BUNDLE_DIR"
mkdir -p "$BUNDLE_DIR/scripts" "$BUNDLE_DIR/configs" "$BUNDLE_DIR/covers" "$BUNDLE_DIR/docs" "$BUNDLE_DIR/packaging"

copy_if_exists() {
  local src="$1"
  local dest="$2"

  if [[ -e "$src" ]]; then
    cp -R "$src" "$dest"
  fi
}

copy_if_exists "$ROOT_DIR/README.md" "$BUNDLE_DIR/"
copy_if_exists "$ROOT_DIR/LICENSE" "$BUNDLE_DIR/"
copy_if_exists "$ROOT_DIR/CHANGELOG.md" "$BUNDLE_DIR/"
copy_if_exists "$ROOT_DIR/ROADMAP.md" "$BUNDLE_DIR/"
copy_if_exists "$ROOT_DIR/VERSION" "$BUNDLE_DIR/"
copy_if_exists "$ROOT_DIR/Makefile" "$BUNDLE_DIR/"

copy_if_exists "$ROOT_DIR/scripts/." "$BUNDLE_DIR/scripts/"
copy_if_exists "$ROOT_DIR/configs/." "$BUNDLE_DIR/configs/"
copy_if_exists "$ROOT_DIR/covers/." "$BUNDLE_DIR/covers/"
copy_if_exists "$ROOT_DIR/docs/." "$BUNDLE_DIR/docs/"
copy_if_exists "$ROOT_DIR/packaging/install-menu-bundle.sh" "$BUNDLE_DIR/packaging/"

if [[ -f "$BUILD_NOTES_NEW" ]]; then
  cp "$BUILD_NOTES_NEW" "$BUNDLE_DIR/Project CBM Menu v${VERSION} Build Notes and Documentation.md"
elif [[ -f "$BUILD_NOTES_LEGACY" ]]; then
  cp "$BUILD_NOTES_LEGACY" "$BUNDLE_DIR/Project CBM v6.5 Build Notes and Documentation.md"
else
  echo "Warning: no build notes document found for version $VERSION" >&2
fi

find "$BUNDLE_DIR" -name ".DS_Store" -delete
find "$BUNDLE_DIR" -name "._*" -delete
find "$BUNDLE_DIR" -name ".gitkeep" -delete

chmod +x "$BUNDLE_DIR"/scripts/pcbm-* 2>/dev/null || true
chmod +x "$BUNDLE_DIR/scripts/pcbm-dialog-lib.sh" 2>/dev/null || true
chmod +x "$BUNDLE_DIR/packaging/install-menu-bundle.sh" 2>/dev/null || true

(
  cd "$DIST_DIR"
  zip -qr "${BUNDLE_NAME}.zip" "$BUNDLE_NAME"
)

echo "Built: $ZIP_PATH"
