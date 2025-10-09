#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR" || {
  echo "[ERROR]  Could not navigate to project directory ($ROOT_DIR). Please check permissions."
  exit 1
}


info() { echo "[INFO] $*"; }
warn() { echo "[WARN] $*"; }
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

IS_WINDOWS=false
if [[ "${OS:-}" == "Windows_NT" ]] || command -v powershell.exe >/dev/null 2>&1; then
  IS_WINDOWS=true
fi

if "$IS_WINDOWS"; then
  info "Detected Windows environment."
  need_cmd powershell.exe

  info "Running updater..."
  powershell.exe -NoProfile -ExecutionPolicy Bypass -Command \
    "iwr -UseBasicParsing https://raw.githubusercontent.com/starling114/crypto-universe/refs/heads/main/bin/setup_windows.ps1 | iex" \
    || err "Update failed."
else
  info "Detected Linux/macOS environment."
  need_cmd curl
  need_cmd bash

  info "Running updater..."
  curl -fsSL https://raw.githubusercontent.com/starling114/crypto-universe/refs/heads/main/bin/setup.sh | bash \
    || err "Update failed."
fi

info "Update complete!"
echo ""
read -n 1 -s -r -p "Press any key to exit..."
echo
