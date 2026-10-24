#!/usr/bin/env python3

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OBJECTIVE = "l7d_demo"

parser = argparse.ArgumentParser()
parser.add_argument("--season", required=True)
parser.add_argument("--apply", action="store_true")
args = parser.parse_args()

if not re.fullmatch(r"[A-Za-z0-9_-]+", args.season):
    parser.error("Invalid season ID")

# 最新の生存者情報を取得
subprocess.run(
    [
        sys.executable,
        str(ROOT / "scripts/season-report.py"),
        "--season",
        args.season
    ],
    check=True
)

report_path = (
    ROOT / "logs" /
    f"season-report-{args.season}.json"
)

report = json.loads(
    report_path.read_text(encoding="utf-8")
)

print("=== LAST 7 DAYS DISPLAY ===")
print("Registered:", report["registered"])
print("Alive:", report["alive"])
print("Eliminated:", report["eliminated"])

commands = [
    f"scoreboard players set Registered {OBJECTIVE} {report['registered']}",
    f"scoreboard players set Alive {OBJECTIVE} {report['alive']}",
    f"scoreboard players set Eliminated {OBJECTIVE} {report['eliminated']}",
    f"scoreboard objectives setdisplay sidebar {OBJECTIVE}"
]

if not args.apply:
    print("PREVIEW ONLY: No Minecraft changes.")
    for command in commands:
        print(command)
    sys.exit(0)

def rcon(command):
    result = subprocess.run(
        ["docker", "compose", "exec", "-T",
         "mc", "rcon-cli", command],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True
    )
    print(result.stdout.strip())
    return result.stdout

# 既存の目標がなければ新規作成
objectives = rcon("scoreboard objectives list")

if not re.search(r"\bl7d_demo\b", objectives):
    rcon(f"scoreboard objectives add {OBJECTIVE} dummy")

for command in commands:
    rcon(command)

print("Scoreboard commands sent.")
