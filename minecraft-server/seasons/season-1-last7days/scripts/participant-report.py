#!/usr/bin/env python3
import json
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "mc-data"

def load_json(filename):
    path = DATA / filename
    if not path.exists():
        raise FileNotFoundError(path)

    with path.open(encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError(f"Invalid data: {filename}")

    return data

whitelist = load_json("whitelist.json")
banned = load_json("banned-players.json")

ban_by_uuid = {
    str(b.get("uuid", "")).lower(): b
    for b in banned if b.get("uuid")
}

ban_by_name = {
    str(b.get("name", "")).lower(): b
    for b in banned if b.get("name")
}

stats = {
    "registered": 0,
    "not_banned": 0,
    "death_banned": 0,
    "other_banned": 0,
}

for player in whitelist:
    stats["registered"] += 1

    ban = ban_by_uuid.get(
        str(player.get("uuid", "")).lower()
    )

    if not ban:
        ban = ban_by_name.get(
            str(player.get("name", "")).lower()
        )

    if not ban:
        stats["not_banned"] += 1
        continue

    reason = str(ban.get("reason", "")).upper()
    source = str(ban.get("source", "")).lower()

    if (
        "LAST 7 DAYS" in reason
        and "GAME OVER" in reason
    ) or source == "deathban":
        stats["death_banned"] += 1
    else:
        stats["other_banned"] += 1

report = {
    "timestamp_utc": datetime.now(
        timezone.utc
    ).isoformat(),
    **stats
}

output = ROOT / "logs/participant-status.json"
output.parent.mkdir(exist_ok=True)
output.write_text(
    json.dumps(report, indent=2),
    encoding="utf-8"
)

print("=== LAST 7 DAYS Participant Report ===")
print("Registered:", stats["registered"])
print("Not banned:", stats["not_banned"])
print("Death banned:", stats["death_banned"])
print("Other banned:", stats["other_banned"])
print("Report saved:", output)
