import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

SOURCE = Path(__file__).resolve().parents[1] / "scripts"
JST = ZoneInfo("Asia/Tokyo")
SEASON = "simulation-30"


class WinnerFinalizationTests(unittest.TestCase):

    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="last7days-final-")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)

        scripts = self.root / "scripts"
        scripts.mkdir()

        for filename in ("finalize-winner.py", "season-report.py"):
            shutil.copy2(SOURCE / filename, scripts / filename)

        self.roster_path = (
            self.root / "logs/rosters" / f"{SEASON}.json"
        )
        self.roster_path.parent.mkdir(parents=True)

        self.deaths_path = (
            self.root / "mc-data/plugins/Last7DaysRecorder"
            / f"deaths-{SEASON}.jsonl"
        )
        self.deaths_path.parent.mkdir(parents=True)

        self.result_path = (
            self.root / "logs/results"
            / f"{SEASON}-winner.json"
        )

        self.players = [
            {
                "name": f"TestPlayer{i:02d}",
                "uuid": str(uuid.uuid5(
                    uuid.NAMESPACE_DNS,
                    f"last7days-final-{i}"
                ))
            }
            for i in range(1, 31)
        ]

        self.save_roster(self.players)
        self.save_deaths(29)

        today = datetime.now(JST).date()
        self.past_start = str(today - timedelta(days=8))
        self.future_start = str(today + timedelta(days=1))

    def save_roster(self, players):
        self.roster_path.write_text(
            json.dumps({
                "season": SEASON,
                "registered": len(players),
                "players": players
            }),
            encoding="utf-8"
        )

    def save_deaths(self, count):
        records = [
            {
                "season": SEASON,
                "uuid": p["uuid"],
                "player": p["name"],
                "cause": "TEST"
            }
            for p in self.players[:count]
        ]

        self.deaths_path.write_text(
            "".join(json.dumps(r) + "\n" for r in records),
            encoding="utf-8"
        )

    def execute(self, start=None, confirm=None, as_of=None):
        cmd = [
            sys.executable,
            str(self.root / "scripts/finalize-winner.py"),
            "--season", SEASON,
            "--start-date", start or self.past_start
        ]

        if confirm is not None:
            cmd += ["--confirm", confirm]

        if as_of is not None:
            cmd += ["--as-of", as_of]

        return subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )

    def test_successful_finalization(self):
        result = self.execute(confirm="TestPlayer30")
        self.assertEqual(result.returncode, 0, result.stderr)

        saved = json.loads(self.result_path.read_text())
        self.assertEqual(saved["status"], "FINALIZED")
        self.assertEqual(saved["winner"]["name"], "TestPlayer30")
        self.assertEqual(saved["eliminated"], 29)

        self.assertEqual(
            saved["roster_sha256"],
            hashlib.sha256(self.roster_path.read_bytes()).hexdigest()
        )
        self.assertEqual(
            saved["deaths_sha256"],
            hashlib.sha256(self.deaths_path.read_bytes()).hexdigest()
        )

    def test_duplicate_finalization(self):
        first = self.execute(confirm="TestPlayer30")
        self.assertEqual(first.returncode, 0)

        original = self.result_path.read_bytes()
        second = self.execute(confirm="TestPlayer30")

        self.assertNotEqual(second.returncode, 0)
        self.assertEqual(self.result_path.read_bytes(), original)

    def test_wrong_winner_rejected(self):
        result = self.execute(confirm="TestPlayer01")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.result_path.exists())

    def test_early_finalization_rejected(self):
        result = self.execute(
            start=self.future_start,
            confirm="TestPlayer30"
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.result_path.exists())

    def test_no_survivors(self):
        self.save_deaths(30)
        result = self.execute(confirm="TestPlayer30")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.result_path.exists())

    def test_no_contest(self):
        self.save_roster(self.players[:1])
        result = self.execute(confirm="TestPlayer01")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.result_path.exists())

    def test_simulated_time_cannot_finalize(self):
        result = self.execute(
            confirm="TestPlayer30",
            as_of=datetime.now(JST).isoformat()
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.result_path.exists())

    def test_preview_creates_no_final_result(self):
        result = self.execute(
            as_of=datetime.now(JST).isoformat()
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("PREVIEW ONLY", result.stdout)
        self.assertFalse(self.result_path.exists())


if __name__ == "__main__":
    unittest.main()
