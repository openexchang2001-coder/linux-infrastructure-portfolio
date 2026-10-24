#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

CONF="config/scoreboard.conf"

if [[ ! -f "$CONF" ]]; then
  echo "ERROR: Scoreboard config missing."
  exit 1
fi

SEASON=$(sed -n \
  's/^SCOREBOARD_SEASON=//p' "$CONF" | tail -n 1)

if [[ ! "$SEASON" =~ ^[A-Za-z0-9_-]+$ ]]; then
  echo "ERROR: Invalid season ID."
  exit 1
fi

mkdir -p logs

# 同時実行防止
exec 9>logs/.scoreboard.lock
flock -n 9 || exit 0

echo "Refreshing scoreboard: $SEASON"

python3 scripts/display-survivors.py \
  --season "$SEASON" --apply

echo "Scoreboard refresh completed."
