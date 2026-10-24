#!/usr/bin/env python3

import argparse
import json
import re
import subprocess
import sys
from datetime import date, datetime, time, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
JST = ZoneInfo("Asia/Tokyo")


def judge(registered, alive, ended):
    if registered < 2:
        return "NO_CONTEST"
    if not ended:
        return "IN_PROGRESS"
    if alive == 1:
        return "WINNER_READY"
    if alive == 0:
        return "NO_SURVIVOR"
    return "UNDECIDED"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--season", required=True)
    parser.add_argument("--start-date", required=True)
    parser.add_argument("--as-of")
    args = parser.parse_args()

    if not re.fullmatch(r"[A-Za-z0-9_-]+", args.season):
        parser.error("Invalid season ID")

    start = date.fromisoformat(args.start_date)

    now = (
        datetime.fromisoformat(args.as_of)
        if args.as_of
        else datetime.now(JST)
    )

    if now.tzinfo is None:
        parser.error("--as-of requires a timezone offset")

    now = now.astimezone(JST)

    event_end = datetime.combine(
        start + timedelta(days=6),
        time(22, 0),
        tzinfo=JST
    )

    # 最新の固定名簿・死亡記録から集計を更新
    subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/season-report.py"),
            "--season",
            args.season
        ],
        check=True,
        stdout=subprocess.DEVNULL
    )

    report_path = (
        ROOT / "logs"
        / f"season-report-{args.season}.json"
    )

    with report_path.open(encoding="utf-8") as f:
        report = json.load(f)

    registered = report["registered"]
    alive = report["alive"]

    status = judge(
        registered,
        alive,
        now >= event_end
    )

    print("=== LAST 7 DAYS WINNER STATUS ===")
    print("Season:", args.season)
    print("Registered:", registered)
    print("Alive:", alive)
    print("Event end:", event_end.isoformat())
    print("Checked at:", now.isoformat())
    print("Status:", status)
    print(
        "Winner candidate:",
        report["winner_candidate"]
    )
    print("No official winner record written.")


if __name__ == "__main__":
    main()
