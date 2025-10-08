#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR" || { echo "❌ Error: Could not navigate to project directory ($ROOT_DIR). Please check permissions."; exit 1; }

info() { echo "[INFO] $*" ; }
err()  { echo "[ERROR] $*" 1>&2 ; exit 1 ; }

need_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    err "$1 is not installed. Please install $1 and try again."
  fi
}

need_cmd npm

MOVE_MAP=(
  "airdrop_perps.py|airdrop/perps"
  "lighter_perp.py|airdrop/perps"
  "extended_perp.py|airdrop/perps"
)

for entry in "${MOVE_MAP[@]}"; do
  fname="${entry%%|*}"
  dest_rel="${entry##*|}"
  src_path="$ROOT_DIR/$fname"
  dest_dir="$ROOT_DIR/scripts/modules/premium/$dest_rel"
  if [ -f "$src_path" ]; then
    mkdir -p "$dest_dir"
    mv -f "$src_path" "$dest_dir/"
    info "Moved $fname -> scripts/modules/premium/$dest_rel/"
  fi
done

info "Launching application..."
if ! npm start; then
  err "Failed to start the application. Please check the project setup or contact support."
fi
