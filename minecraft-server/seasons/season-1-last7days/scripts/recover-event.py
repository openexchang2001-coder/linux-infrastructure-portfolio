#!/usr/bin/env python3
import sys
import re
import json
import fcntl
import subprocess
from pathlib import Path
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
JST = ZoneInfo("Asia/Tokyo")

# 開催日、時刻、境界サイズ
EVENTS = [
    (3, "21:00", 1600),
    (4, "21:00", 1200),
    (5, "21:00", 800),
    (6, "21:00", 400),
    (7, "21:00", 250),
    (7, "21:25", 100),
    (7, "21:50", 30),
]

def rcon(command):
    result = subprocess.run(
        ["docker", "compose", "exec", "-T",
         "mc", "rcon-cli", command],
        cwd=ROOT, text=True,
        capture_output=True, check=True
    )
    return result.stdout.strip()

def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "preview"

    if mode == "preview":
        if len(sys.argv) != 4:
            sys.exit(
                "Usage: recover-event.py preview "
                "YYYY-MM-DDTHH:MM YYYY-MM-DD"
            )
        now = datetime.fromisoformat(sys.argv[2]).replace(tzinfo=JST)
        start = date.fromisoformat(sys.argv[3])

    elif mode == "run":
        now = datetime.now(JST)
        conf = ROOT / "config/event.conf"
        values = [
            line.split("=", 1)[1].strip()
            for line in conf.read_text().splitlines()
            if line.startswith("EVENT_START_DATE=")
        ]
        if not values or not values[-1]:
            print("Event not activated. No changes.")
            return
        start = date.fromisoformat(values[-1])

    else:
        sys.exit("ERROR: Use preview or run")

    day = (now.date() - start).days + 1
    end = datetime.combine(
        start + timedelta(days=6),
        time(22, 0), tzinfo=JST
    )

    print(f"Mode: {mode}")
    print(f"Current: {now.isoformat()}")
    print(f"Event DAY: {day}")

    if day < 1 or now >= end:
        print("Outside event period. No action.")
        return

    # 最も新しい、完了予定時刻を過ぎた縮小を探す
    latest = None

    for event_day, clock, size in EVENTS:
        event_date = start + timedelta(days=event_day - 1)
        event_time = datetime.combine(
            event_date,
            time.fromisoformat(clock),
            tzinfo=JST
        )
        # 通常の5分間の縮小が完了するまで待つ
        if now >= event_time + timedelta(minutes=5):
            latest = (event_day, clock, size)

    if latest is None:
        print("No overdue border stage.")
        return

    event_day, clock, target = latest

    print(f"Latest stage: DAY {event_day} {clock}")
    print(f"Expected border: {target}")
    print(f"Expected PvP: {'true' if event_day == 7 else 'false'}")

    if mode == "preview":
        print("PREVIEW ONLY: No server changes.")
        return

    # 同時実行を防ぐ
    logdir = ROOT / "logs"
    logdir.mkdir(exist_ok=True)

    with open(logdir / ".event-scheduler.lock", "a+") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)

        output = rcon(
            "execute in minecraft:overworld run worldborder get"
        )

        match = re.search(
            r"currently\s+([\d,.]+)\s+block", output
        )
        if not match:
            raise RuntimeError(
                "Cannot read world border: " + output
            )

        current = float(match.group(1).replace(",", ""))
        print(f"Actual border: {current}")

        if current > target:
            print("Recovering missed border stage...")
            print(rcon(
                f"execute in minecraft:overworld "
                f"run worldborder set {target}"
            ))

            verify = rcon(
                "execute in minecraft:overworld run worldborder get"
            )
            verified = re.search(
                r"currently\s+([\d,.]+)\s+block", verify
            )
            if not verified or float(
                verified.group(1).replace(",", "")
            ) > target:
                raise RuntimeError("Border verification failed")

        else:
            print("Border already at or below target.")

        # 最終日のPvP状態を復旧
        if event_day == 7:
            subprocess.run(
                ["bash", "scripts/pvp-final.sh", "apply", "on"],
                cwd=ROOT, check=True
            )

        record = {
            "time": now.isoformat(),
            "event_day": event_day,
            "stage_time": clock,
            "target_border": target,
            "previous_border": current,
            "status": "verified"
        }

        with open(logdir / "event-recovery.jsonl", "a") as f:
            f.write(json.dumps(record) + "\n")

        print("Recovery verification completed.")

if __name__ == "__main__":
    main()
