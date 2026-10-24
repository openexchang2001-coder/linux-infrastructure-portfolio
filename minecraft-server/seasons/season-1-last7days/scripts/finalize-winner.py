#!/usr/bin/env python3

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
JST = ZoneInfo("Asia/Tokyo")

parser = argparse.ArgumentParser()
parser.add_argument("--season", required=True)
parser.add_argument("--start-date", required=True)
parser.add_argument("--as-of")
parser.add_argument("--confirm", metavar="PLAYER_NAME")
args = parser.parse_args()

if not re.fullmatch(r"[A-Za-z0-9_-]+", args.season):
    parser.error("Invalid season ID")

if args.confirm and args.as_of:
    parser.error(
        "Simulated time cannot be used to finalize results"
    )

start = date.fromisoformat(args.start_date)
now = datetime.now(JST)

if args.as_of:
    now = datetime.fromisoformat(args.as_of)
    if now.tzinfo is None:
        parser.error("--as-of requires a timezone offset")
    now = now.astimezone(JST)

event_end = datetime.combine(
    start + timedelta(days=6),
    time(22, 0),
    tzinfo=JST
)

roster_path = (
    ROOT / "logs/rosters" / f"{args.season}.json"
)
deaths_path = (
    ROOT / "mc-data/plugins/Last7DaysRecorder"
    / f"deaths-{args.season}.jsonl"
)

if not roster_path.exists():
    sys.exit("ERROR: Frozen roster is missing")

# 最新の死亡履歴から集計
subprocess.run(
    [
        sys.executable,
        str(ROOT / "scripts/season-report.py"),
        "--season", args.season
    ],
    check=True,
    stdout=subprocess.DEVNULL
)

report_path = (
    ROOT / "logs" / f"season-report-{args.season}.json"
)

report = json.loads(
    report_path.read_text(encoding="utf-8")
)
roster = json.loads(
    roster_path.read_text(encoding="utf-8")
)

registered = report["registered"]
alive = report["alive"]
candidate = report["winner_candidate"]

if registered < 2:
    status = "NO_CONTEST"
elif now < event_end:
    status = "IN_PROGRESS"
elif alive == 0:
    status = "NO_SURVIVOR"
elif alive > 1:
    status = "UNDECIDED"
else:
    status = "WINNER_READY"

print("=== LAST 7 DAYS FINAL RESULT ===")
print("Season:", args.season)
print("Registered:", registered)
print("Alive:", alive)
print("Status:", status)
print("Winner candidate:", candidate)
print("Event end:", event_end.isoformat())

if not args.confirm:
    print("PREVIEW ONLY: No winner record written.")
    sys.exit(0)

if status != "WINNER_READY":
    sys.exit("ERROR: Winner cannot be finalized")

if candidate != args.confirm:
    sys.exit("ERROR: Confirmed player does not match")

winner = next(
    (
        p for p in roster["players"]
        if p["name"] == candidate
    ),
    None
)

if winner is None:
    sys.exit("ERROR: Winner not found in roster")

def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

if not deaths_path.exists():
    sys.exit("ERROR: Death records are missing")

result = {
    "season": args.season,
    "status": "FINALIZED",
    "winner": winner,
    "registered": registered,
    "eliminated": report["eliminated"],
    "finalized_at_utc": datetime.now(
        timezone.utc
    ).isoformat(),
    "roster_sha256": sha256(roster_path),
    "deaths_sha256": sha256(deaths_path)
}

output = (
    ROOT / "logs/results"
    / f"{args.season}-winner.json"
)

output.parent.mkdir(parents=True, exist_ok=True)

# 既存の確定結果は上書きしない
try:
    with output.open("x", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
except FileExistsError:
    sys.exit("ERROR: Result already finalized")

print("Winner finalized:", candidate)
print("Saved:", output)
