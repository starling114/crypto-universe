#!/usr/bin/env bash

set -euo pipefail

REPO_URL="https://github.com/starling114/crypto-universe.git"
TARGET_DIR="${HOME}/Desktop/crypto-universe"

info() { echo "[INFO] $*" ; }
warn() { echo "[WARN] $*" ; }
err()  { echo "[ERROR] $*" 1>&2 ; exit 1 ; }

need_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    err "$1 is not installed. Please install it and try again."
  fi
}

ensure_node() {
  if ! command -v node >/dev/null 2>&1; then
    err "Node.js is not installed. Please download and install Node.js (LTS version) from https://nodejs.org, then re-run this script."
  fi
  if ! command -v npm >/dev/null 2>&1; then
    err "npm is not installed. Please reinstall Node.js from https://nodejs.org (npm is included) and try again."
  fi
  NODE_VER=$(node -v 2>/dev/null || echo "unknown")
  NPM_VER=$(npm -v 2>/dev/null || echo "unknown")
  info "Node.js ($NODE_VER) and npm ($NPM_VER) are ready."
}

ensure_python() {
  if command -v python3 >/dev/null 2>&1; then
    PY=python3
  elif command -v python >/dev/null 2>&1; then
    PY=python
  else
    err "Python 3 is not installed. Please install Python 3.10 or higher from https://www.python.org/downloads/ and try again."
  fi

  if "$PY" -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)" 2>/dev/null; then
    PY_VER=$("$PY" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')")
    info "Python ($PY_VER) is ready (meets 3.10 or higher requirement)."
  else
    CUR_VER=$("$PY" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')")
    err "Your Python version ($CUR_VER) is too old. Please install Python 3.10 or higher from https://www.python.org/downloads/ and try again."
  fi
}

info "Starting setup for crypto-universe application..."

need_cmd git
ensure_node
ensure_python

if [ -d "$TARGET_DIR/.git" ]; then
  info "Found existing project at $TARGET_DIR. Resetting to main branch..."
  (
    cd "$TARGET_DIR" || err "Could not access $TARGET_DIR"
    
    if ! git fetch --all; then
      err "Failed to fetch from remote. Please check your internet connection."
    fi
    
    if git stash --include-untracked; then
      info 'Stashed local changes before reset.'
    fi
    
    if ! git checkout --force main; then
      err "Failed to checkout main branch."
    fi
    
    if ! git reset --hard origin/main; then
      err "Failed to reset to origin/main. Please check your repository access."
    fi
    
    git clean -fd || warn "Warning: Failed to clean untracked files"
  )
else
  info "Downloading project to $TARGET_DIR..."
  if ! mkdir -p "$(dirname "$TARGET_DIR")" || ! git clone "$REPO_URL" "$TARGET_DIR"; then
    err "Failed to download the project. Please check your internet connection or ensure you have permission to write to $TARGET_DIR."
  fi
fi

cd "$TARGET_DIR" || err "Could not access $TARGET_DIR. Please check permissions."

info "Installing Node.js dependencies..."
if ! npm install; then
  err "Failed to install Node.js dependencies. Please check your internet connection or Node.js installation."
fi

info "Setting up Python environment in scripts/myenv..."
cd scripts || err "Could not access scripts directory. Please ensure the project structure is correct."
if [ ! -d myenv ]; then
  if ! "$PY" -m venv myenv; then
    err "Failed to create Python virtual environment. Please ensure Python 3.10+ is installed correctly."
  fi
fi

PIP_BIN="$(pwd)/myenv/bin/pip"
if [ ! -x "$PIP_BIN" ]; then
  err "pip not found in virtual environment. Please try re-running the script or reinstalling Python."
fi

info "Installing Python dependencies..."
if ! "$PIP_BIN" install --upgrade pip || ! "$PIP_BIN" install -r requirements.txt; then
  err "Failed to install Python dependencies. Please check requirements.txt or your internet connection."
fi

cd "$TARGET_DIR" || err "Could not return to project directory."

info "Setup complete!"
