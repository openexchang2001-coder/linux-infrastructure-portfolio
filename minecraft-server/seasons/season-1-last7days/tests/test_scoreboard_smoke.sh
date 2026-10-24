#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

SEASON="scoreboard-smoke"
CONF="config/scoreboard.conf"
ROSTER="logs/rosters/${SEASON}.json"
DEATHS="mc-data/plugins/Last7DaysRecorder/deaths-${SEASON}.jsonl"

BACKUP=$(mktemp)
cp -p "$CONF" "$BACKUP"

cleanup() {
  echo "=== Restoring original scoreboard ==="
  cp -p "$BACKUP" "$CONF"
  rm -f "$BACKUP" "$ROSTER" "$DEATHS"

  ./scripts/refresh-scoreboard.sh || true
  sudo systemctl start last7days-scoreboard.timer || true
}

trap cleanup EXIT

# テスト中のタイマーとの競合を防止
sudo systemctl stop last7days-scoreboard.timer

# 仮想参加者2人を作成
python3 - <<'PY'
import json
import uuid
from pathlib import Path

season = "scoreboard-smoke"
players = []

for n in range(1, 3):
    players.append({
        "uuid": str(uuid.uuid5(
            uuid.NAMESPACE_DNS,
            f"last7days-scoreboard-smoke-{n}"
        )),
        "name": f"DemoPlayer{n}"
    })

path = Path(f"logs/rosters/{season}.json")
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text(json.dumps({
    "season": season,
    "registered": 2,
    "players": players
}), encoding="utf-8")

death_path = Path(
    "mc-data/plugins/Last7DaysRecorder/"
    f"deaths-{season}.jsonl"
)
death_path.write_text("", encoding="utf-8")
PY

printf 'SCOREBOARD_SEASON=%s\n' "$SEASON" > "$CONF"

echo "=== TEST 1: All players alive ==="
sudo systemctl start last7days-scoreboard.service

docker compose exec -T mc rcon-cli \
  "scoreboard players get Alive l7d_demo"

# 1人分の仮想死亡履歴を追加
python3 - <<'PY'
import json
from pathlib import Path

season = "scoreboard-smoke"
roster = json.loads(
    Path(f"logs/rosters/{season}.json").read_text()
)

player = roster["players"][0]

record = {
    "season": season,
    "uuid": player["uuid"],
    "player": player["name"],
    "cause": "TEST"
}

path = Path(
    "mc-data/plugins/Last7DaysRecorder/"
    f"deaths-{season}.jsonl"
)

with path.open("a", encoding="utf-8") as f:
    f.write(json.dumps(record) + "\n")
PY

echo "=== TEST 2: One player eliminated ==="
sudo systemctl start last7days-scoreboard.service

docker compose exec -T mc rcon-cli \
  "scoreboard players get Alive l7d_demo"

echo "=== Test completed ==="
