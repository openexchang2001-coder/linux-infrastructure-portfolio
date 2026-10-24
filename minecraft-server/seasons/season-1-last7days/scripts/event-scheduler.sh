#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

MODE="${1:-preview}"

if [[ "$MODE" == "preview" ]]; then
  TODAY="${2:-2026-11-03}"
  TIME="${3:-20:55}"
  START_DATE="${4:-2026-11-01}"
elif [[ "$MODE" == "run" ]]; then
  START_DATE=$(sed -n 's/^EVENT_START_DATE=//p' config/event.conf | tail -n 1)
  if [[ -z "$START_DATE" ]]; then
    echo "Event is not activated."
    exit 0
  fi
  TODAY=$(TZ=Asia/Tokyo date +%F)
  TIME=$(TZ=Asia/Tokyo date +%H:%M)
else
  echo "Usage: $0 preview [date time start-date] | run"
  exit 1
fi

# 日付を検証し、開催何日目かを計算
START=$(TZ=Asia/Tokyo date -d "$START_DATE 00:00:00" +%s)
CURRENT=$(TZ=Asia/Tokyo date -d "$TODAY 00:00:00" +%s)
DAY=$(( (CURRENT - START) / 86400 + 1 ))

STAGE=""
ACTION=""

if (( DAY >= 3 && DAY <= 6 )); then
  STAGE="$DAY"
  case "$TIME" in
    20:55) ACTION="warn" ;;
    21:00) ACTION="apply" ;;
  esac
elif (( DAY == 7 )); then
  case "$TIME" in
    20:55) STAGE="7a"; ACTION="warn" ;;
    21:00) STAGE="7a"; ACTION="apply" ;;
    21:20) STAGE="7b"; ACTION="warn" ;;
    21:25) STAGE="7b"; ACTION="apply" ;;
    21:45) STAGE="7c"; ACTION="warn" ;;
    21:50) STAGE="7c"; ACTION="apply" ;;
  esac
fi

if [[ -z "$ACTION" ]]; then
  echo "DAY $DAY $TIME: No scheduled event."
  exit 0
fi

case "$STAGE" in
  3) TARGET=1600 ;;
  4) TARGET=1200 ;;
  5) TARGET=800 ;;
  6) TARGET=400 ;;
  7a) TARGET=250 ;;
  7b) TARGET=100 ;;
  7c) TARGET=30 ;;
esac

echo "DAY $DAY | $TIME | $ACTION | border=$TARGET"

if [[ "$MODE" == "preview" ]]; then
  if [[ "$STAGE" == "7a" && "$ACTION" == "apply" ]]; then
    echo "Additional action: Enable PvP"
  fi
  echo "PREVIEW ONLY: No server changes."
  exit 0
fi

# 二重実行を防止
mkdir -p logs
exec 9>logs/.event-scheduler.lock
flock -n 9 || exit 0

MARKER="logs/.event-${TODAY}-${TIME}-${ACTION}-${STAGE}.done"

if [[ -f "$MARKER" ]]; then
  echo "Already executed."
  exit 0
fi

if [[ "$ACTION" == "warn" ]]; then
  docker compose exec -T mc rcon-cli \
    "say [LAST 7 DAYS] WARNING: Border shrinks to $TARGET blocks in 5 minutes!"
else
  # DAY 7の最終決戦開始時にPvPを解禁
  if [[ "$STAGE" == "7a" ]]; then
    if [[ ! -x "./scripts/pvp-final.sh" ]]; then
      echo "ERROR: PvP controller is missing."
      exit 1
    fi
    ./scripts/pvp-final.sh apply on
  fi

  ./scripts/worldborder-stage.sh "$STAGE" apply
fi

touch "$MARKER"
echo "Event executed successfully."
