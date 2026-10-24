#!/usr/bin/env python3

import argparse
import json
import re
import uuid
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent.parent

parser = argparse.ArgumentParser()
parser.add_argument("--season", required=True)
args = parser.parse_args()

season = args.season

if not re.fullmatch(r"[A-Za-z0-9_-]+", season):
    raise SystemExit("ERROR: Invalid season ID")

roster_path = ROOT / "logs/rosters" / f"{season}.json"

deaths_path = (
    ROOT / "mc-data/plugins/Last7DaysRecorder"
    / f"deaths-{season}.jsonl"
)

if not roster_path.exists():
    raise SystemExit("ERROR: Frozen roster not found")

with roster_path.open(encoding="utf-8") as f:
    roster = json.load(f)

if roster.get("season") != season:
    raise SystemExit("ERROR: Season mismatch")

players = {}

for player in roster["players"]:
    player_uuid = str(uuid.UUID(player["uuid"]))

    if player_uuid in players:
        raise SystemExit("ERROR: Duplicate roster UUID")

    players[player_uuid] = player["name"]

deaths = {}

if deaths_path.exists():
    with deaths_path.open(encoding="utf-8") as f:
        for line_number, line in enumerate(f, 1):

            if not line.strip():
                continue

            try:
                record = json.loads(line)

                if record.get("season") != season:
                    continue

                player_uuid = str(uuid.UUID(record["uuid"]))

            except (ValueError, KeyError, TypeError) as e:
                raise SystemExit(
                    f"ERROR: Invalid death record "
                    f"at line {line_number}: {e}"
                )

            if player_uuid in players:
                deaths.setdefault(player_uuid, record)

alive = []
eliminated = []

for player_uuid, name in players.items():
    if player_uuid in deaths:
        eliminated.append(name)
    else:
        alive.append(name)

report = {
    "season": season,
    "generated_utc": datetime.now(
        timezone.utc
    ).isoformat(),
    "registered": len(players),
    "alive": len(alive),
    "eliminated": len(eliminated),
    "alive_players": sorted(alive),
    "eliminated_players": sorted(eliminated),
    "winner_candidate": (
        alive[0] if len(alive) == 1 else None
    )
}

output = ROOT / "logs" / f"season-report-{season}.json"

output.parent.mkdir(exist_ok=True)

output.write_text(
    json.dumps(report, indent=2, ensure_ascii=False),
    encoding="utf-8"
)

print("=== LAST 7 DAYS SEASON REPORT ===")
print("Season:", season)
print("Registered:", report["registered"])
print("Alive:", report["alive"])
print("Eliminated:", report["eliminated"])
print("Winner candidate:", report["winner_candidate"])
print("Report saved:", output)
