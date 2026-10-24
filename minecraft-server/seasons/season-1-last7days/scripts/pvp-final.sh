#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

MODE="${1:-preview}"
STATE="${2:-on}"

case "$STATE" in
  on) VALUE=true ;;
  off) VALUE=false ;;
  *)
    echo "ERROR: Use on or off"
    exit 1
    ;;
esac

case "$MODE" in
  preview|apply) ;;
  *)
    echo "ERROR: Use preview or apply"
    exit 1
    ;;
esac

echo "LAST 7 DAYS - PvP Controller"
echo "Mode: $MODE"
echo "PvP enabled: $VALUE"

DIMS=(overworld the_nether the_end)

for DIM in "${DIMS[@]}"; do
  CMD="execute in minecraft:$DIM run gamerule minecraft:pvp $VALUE"
  echo "Command: $CMD"

  if [[ "$MODE" == "apply" ]]; then
    docker compose exec -T mc rcon-cli "$CMD"

    RESULT=$(docker compose exec -T mc rcon-cli \
      "execute in minecraft:$DIM run gamerule minecraft:pvp")

    echo "$RESULT"

    if [[ "$RESULT" != *"set to $VALUE"* ]]; then
      echo "ERROR: PvP verification failed for $DIM"
      exit 1
    fi
  fi
done

if [[ "$MODE" == "preview" ]]; then
  echo "PREVIEW ONLY: No server changes."
else
  echo "$(date -Is) PvP=$VALUE" >> logs/pvp-events.log
  echo "PvP setting applied successfully."
fi
