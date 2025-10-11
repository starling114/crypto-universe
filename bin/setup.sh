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

if [ -f "myenv/bin/python" ]; then
  VENV_PYTHON="myenv/bin/python"
else
  err "Failed to find Python executable in virtual environment. Please check your Python installation."
fi

info "Upgrading pip in the virtual environment..."
if ! "$VENV_PYTHON" -m pip install --upgrade pip --no-cache-dir; then
  err "Failed to upgrade pip. Please check your Python installation."
fi

info "Installing Python dependencies..."
if ! "$VENV_PYTHON" -m pip install -r requirements.txt; then
  err "Failed to install Python dependencies. Please check requirements.txt or your internet connection."
fi

info "Creating Applications shortcut for start.sh..."
DESTINATION_DIR="/Applications"
SHORTCUT_NAME="CU"
START_SH="$TARGET_DIR/bin/start.sh"
ICON_PATH="$TARGET_DIR/frontend/public/logo.icns"
APP_DIR="$DESTINATION_DIR/$SHORTCUT_NAME.app"
CONTENTS_DIR="$APP_DIR/Contents"
EXEC_DIR="$CONTENTS_DIR/MacOS"
PLIST_FILE="$CONTENTS_DIR/Info.plist"

need_cmd bash
need_cmd osascript

if [ -d "$APP_DIR" ]; then
    rm -rf "$APP_DIR" || warn "Failed to delete existing shortcut: $APP_DIR"
fi

mkdir -p "$EXEC_DIR" || err "Failed to create directory $EXEC_DIR"

cat > "$EXEC_DIR/$SHORTCUT_NAME" << EOF
#!/bin/bash
osascript -e "tell application \\"Terminal\\" to do script \\"bash '$START_SH'\\"" -e 'tell application "Terminal" to activate'
EOF

chmod +x "$EXEC_DIR/$SHORTCUT_NAME" || err "Failed to make $EXEC_DIR/$SHORTCUT_NAME executable"

cat > "$PLIST_FILE" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>$SHORTCUT_NAME</string>
    <key>CFBundleIdentifier</key>
    <string>com.example.$SHORTCUT_NAME</string>
    <key>CFBundleName</key>
    <string>$SHORTCUT_NAME</string>
    <key>CFBundleIconFile</key>
    <string>AppIcon</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
</dict>
</plist>
EOF

mkdir -p "$CONTENTS_DIR/Resources"
cp "$ICON_PATH" "$CONTENTS_DIR/Resources/AppIcon.icns" || warn "Failed to copy icon to $CONTENTS_DIR/Resources/AppIcon.icns"

info "Created Applcations shortcut for start.sh: $APP_DIR"

cd "$TARGET_DIR" || err "Could not return to project directory."

info "Setup complete!"
