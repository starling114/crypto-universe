#!/usr/bin/env bash
set -euo pipefail

APP_DIR="/app"
DATA_DIR="/data"

mkdir -p "$DATA_DIR"

BACKEND_MODULES=(
  "balances"
  "crypto_universe"
)

SCRIPT_MODULES=(
  "bridge/jumper"
  "bridge/relay"
  "bridge/hyperlane"
  "chore/rabby_import"
  "swap/jumper"
  "swap/pancakeswap"
  "testing/ads_execution"
  "transfer"
  "withdraw/okx"
  "yt_tokens"
)

PREMIUM_SCRIPT_MODULES=(
  "premium/farm/aster:farm_aster.py"
  "premium/farm/lighter:farm_lighter.py"
  "premium/mint/kingdomly:mint_kingdomly.py"
  "premium/mint/magiceden:mint_magiceden.py"
)

link_json() {
  local src="$1"
  local rel="${src#${APP_DIR}/}"
  local dst="${DATA_DIR}/${rel}"
  local dst_dir
  dst_dir="$(dirname "$dst")"

  mkdir -p "$dst_dir"

  if [ ! -e "$dst" ]; then
    if [ -e "$src" ]; then
      cp -a "$src" "$dst" || echo "{}" > "$dst"
    else
      echo "{}" > "$dst"
    fi
  fi

  rm -f "$src"
  ln -s "$dst" "$src"
}

link_json "$APP_DIR/configs.json"
link_json "$APP_DIR/private_configs.json"

if [ -e "$DATA_DIR/.env" ]; then
  rm -f "$APP_DIR/.env"
  ln -s "$DATA_DIR/.env" "$APP_DIR/.env"
fi

for module in "${BACKEND_MODULES[@]}"; do
  for name in instructions.json secrets.json configs.json; do
    link_json "$APP_DIR/backend/modules/$module/$name"
  done
done

for module in "${SCRIPT_MODULES[@]}"; do
  for name in instructions.json secrets.json configs.json; do
    link_json "$APP_DIR/scripts/modules/$module/$name"
  done
done

for mapping in "${PREMIUM_SCRIPT_MODULES[@]}"; do
  IFS=":" read -r mid_path data_name <<< "$mapping"
  src_path="$DATA_DIR/$data_name"
  dst_path="$APP_DIR/scripts/modules/$mid_path/$data_name"

  mkdir -p "$APP_DIR/scripts/modules/$mid_path"

  if [ -e "$src_path" ]; then
    cp -f "$src_path" "$dst_path"
  fi

  for name in instructions.json secrets.json configs.json; do
    link_json "$APP_DIR/scripts/modules/$mid_path/$name"
  done
done

exec npm start