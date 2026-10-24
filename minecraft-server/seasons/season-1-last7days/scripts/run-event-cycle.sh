#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

# 開催日が未設定なら何も実行しない
if [[ ! -f config/event.conf ]]; then
  echo "ERROR: Event configuration is missing."
  exit 1
fi

START_DATE=$(sed -n \
  's/^EVENT_START_DATE=//p' config/event.conf | tail -n 1)

if [[ -z "$START_DATE" ]]; then
  echo "Event is not activated. No changes made."
  exit 0
fi

echo "=== Event Scheduler ==="
./scripts/event-scheduler.sh run

echo "=== Event Recovery ==="
python3 scripts/recover-event.py run

echo "Event cycle completed."
