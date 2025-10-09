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

ZIP_FILE="compiled-modules-${OS}-latest-python3.10.zip"

if [ -f "$ROOT_DIR/$ZIP_FILE" ]; then
  TEMP_DIR="$(mktemp -d)"
  info "Found $ZIP_FILE, processing..."

  mv "$ROOT_DIR/$ZIP_FILE" "$TEMP_DIR/" || { rm -rf "$TEMP_DIR"; err "Failed to move $ZIP_FILE to temp directory"; }

  info "Extracting $ZIP_FILE..."
  unzip -q "$TEMP_DIR/$ZIP_FILE" -d "$TEMP_DIR" || { rm -rf "$TEMP_DIR"; err "Failed to extract $ZIP_FILE"; }

  info "Moving files to their destinations..."
  find "$TEMP_DIR" -type f | while read -r file; do
    if [ "$(basename "$file")" = "$ZIP_FILE" ]; then
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
  info "Finished processing $ZIP_FILE"
fi

info "Launching application..."
if ! npm start; then
  err "Failed to start the application. Please check the project setup or contact support."
fi
