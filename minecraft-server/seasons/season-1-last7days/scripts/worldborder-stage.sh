#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

STAGE="${1:-}"
MODE="${2:-preview}"

case "$STAGE" in
  1|2) SIZE=2000 ;;
  3) SIZE=1600 ;;
  4) SIZE=1200 ;;
  5) SIZE=800 ;;
  6) SIZE=400 ;;
  7a) SIZE=250 ;;
  7b) SIZE=100 ;;
  7c) SIZE=30 ;;
  *)
    echo "ERROR: Invalid stage"
    echo "Usage: $0 1|2|3|4|5|6|7a|7b|7c [preview|apply]"
    exit 1
    ;;
esac

if [[ "$MODE" != "preview" && "$MODE" != "apply" ]]; then
  echo "ERROR: Use preview or apply"
  exit 1
fi

CMD="execute in minecraft:overworld run worldborder set $SIZE"

if [[ "$STAGE" != "1" && "$STAGE" != "2" ]]; then
  CMD="$CMD 300s"
fi

echo "Stage: $STAGE"
echo "Target border: $SIZE blocks"
echo "Mode: $MODE"
echo "Command: $CMD"

if [[ "$MODE" == "preview" ]]; then
  echo "Preview only. No changes made."
  exit 0
fi

docker compose exec -T mc rcon-cli \
  "say [LAST 7 DAYS] World border event starting!"

docker compose exec -T mc rcon-cli "$CMD"

mkdir -p logs

echo "$(date -Is) STAGE=$STAGE TARGET=$SIZE" \
  >> logs/worldborder-events.log

echo "Border command sent."
