#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR" || { echo "[ERROR]  Could not navigate to project directory ($ROOT_DIR). Please check permissions."; exit 1; }

info() { echo "[INFO] $*" ; }
err()  {
  echo "[ERROR] $*" 1>&2;
  echo ""
  read -n 1 -s -r -p "Press any key to exit..."
  echo
  exit 1
}

need_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    err "$1 is not installed. Please install $1 and try again."
  fi
}

need_cmd npm
need_cmd unzip

case "$(uname -s)" in
  Darwin*)
    OS="macos"
    ;;
  MINGW*|MSYS*|CYGWIN*)
    OS="windows"
    ;;
  Linux*)
    OS="linux"
    ;;
  *)
    err "Unsupported operating system: $(uname -s)"
    ;;
esac

ZIP_PATTERN="premium-modules-${OS}-*-python3.10*.zip"

for ZIP_FILE in "$ROOT_DIR"/$ZIP_PATTERN; do
  if [ -f "$ZIP_FILE" ]; then
    ZIP_BASENAME=$(basename "$ZIP_FILE")
    TEMP_DIR="$(mktemp -d)"
    info "Found $ZIP_BASENAME, processing..."

    mv "$ZIP_FILE" "$TEMP_DIR/" || { rm -rf "$TEMP_DIR"; err "Failed to move $ZIP_BASENAME to temp directory"; }

    info "Extracting $ZIP_BASENAME..."
    unzip -q "$TEMP_DIR/$ZIP_BASENAME" -d "$TEMP_DIR" || { rm -rf "$TEMP_DIR"; err "Failed to extract $ZIP_BASENAME"; }

    info "Moving files to their destinations..."
    find "$TEMP_DIR" -type f | while read -r file; do
      if [ "$(basename "$file")" = "$ZIP_BASENAME" ]; then
        continue
      fi

      rel_path="${file#$TEMP_DIR/}"
      if [ -n "$rel_path" ] && [ "$rel_path" != "$file" ]; then
        dest_dir="$ROOT_DIR/scripts/modules/premium/$(dirname "$rel_path")"
        mkdir -p "$dest_dir"
        mv -f "$file" "$dest_dir/"
        info "Moved $rel_path -> scripts/modules/premium/$rel_path"
      fi
    done

    rm -rf "$TEMP_DIR"
    info "Finished processing $ZIP_BASENAME"
  fi
done

info "Launching application..."
if ! npm start; then
  err "Failed to start the application. Please check the project setup or contact support."
fi
