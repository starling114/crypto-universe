#!/usr/bin/env bash
set -euo pipefail

DESKTOP_DIR="$HOME/Desktop"
TARGET_DIR="$DESKTOP_DIR/crypto-universe"

echo "🐳 Preparing Crypto Universe setup..."

mkdir -p "$TARGET_DIR"
cd "$TARGET_DIR"

echo "📁 Using Desktop at: $DESKTOP_DIR"
echo "📂 Working directory: $TARGET_DIR"

if ! command -v curl >/dev/null 2>&1; then
  echo "❌ curl is required but not found. Please install curl and re-run." >&2
  exit 1
fi

SCRIPT_URL="https://raw.githubusercontent.com/starling114/crypto-universe/migration_to_docker/bin/docker_run.sh"

echo "⬇️  Downloading docker_run.sh..."
curl -fsSL -o docker_run.sh "$SCRIPT_URL"
chmod +x docker_run.sh

echo "🚀 Running docker_run.sh..."
./docker_run.sh
