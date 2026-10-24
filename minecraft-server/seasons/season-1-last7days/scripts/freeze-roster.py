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

source = ROOT / "mc-data/whitelist.json"
destination = ROOT / "logs/rosters" / f"{season}.json"

if not source.exists():
    raise SystemExit("ERROR: whitelist.json not found")

with source.open(encoding="utf-8") as f:
    whitelist = json.load(f)

if not isinstance(whitelist, list) or not whitelist:
    raise SystemExit("ERROR: No registered players")

players = []
seen = set()

for player in whitelist:
    player_uuid = str(uuid.UUID(player["uuid"]))
    name = player["name"]

    if player_uuid in seen:
        raise SystemExit("ERROR: Duplicate UUID")

    seen.add(player_uuid)

    players.append({
        "uuid": player_uuid,
        "name": name
    })

players.sort(key=lambda p: p["name"].lower())

roster = {
    "season": season,
    "frozen_at_utc": datetime.now(
        timezone.utc
    ).isoformat(),
    "registered": len(players),
    "players": players
}

destination.parent.mkdir(
    parents=True,
    exist_ok=True
)

# 既存の名簿は絶対に上書きしない
try:
    with destination.open(
        "x", encoding="utf-8"
    ) as f:
        json.dump(
            roster, f,
            indent=2,
            ensure_ascii=False
        )
except FileExistsError:
    raise SystemExit(
        "ERROR: Roster already frozen. "
        "Existing roster was not changed."
    )

print("=== LAST 7 DAYS ROSTER ===")
print("Season:", season)
print("Registered:", len(players))
print("Roster frozen successfully.")
print("Saved:", destination)
