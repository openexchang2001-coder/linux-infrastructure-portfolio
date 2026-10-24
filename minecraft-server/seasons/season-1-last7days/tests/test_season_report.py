import json
import shutil
import subprocess
import sys
import tempfile
import unittest
import uuid
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / "scripts" / "season-report.py"
SEASON = "sim-30"

class SeasonReportTests(unittest.TestCase):
    def setUp(self):
        workspace = tempfile.TemporaryDirectory(prefix="last7days-sim-")
        self.addCleanup(workspace.cleanup)
        self.root = Path(workspace.name)

        script_dir = self.root / "scripts"
        script_dir.mkdir()
        shutil.copy2(SOURCE, script_dir / "season-report.py")

        self.roster_path = (
            self.root / "logs" / "rosters" / f"{SEASON}.json"
        )
        self.roster_path.parent.mkdir(parents=True)

        self.deaths_path = (
            self.root / "mc-data" / "plugins" /
            "Last7DaysRecorder" / f"deaths-{SEASON}.jsonl"
        )
        self.deaths_path.parent.mkdir(parents=True)

        self.players = [
            {
                "name": f"TestPlayer{i:02d}",
                "uuid": str(uuid.uuid5(
                    uuid.NAMESPACE_DNS, f"last7days-test-{i}"
                ))
            }
            for i in range(1, 31)
        ]

        self.roster_path.write_text(
            json.dumps({
                "season": SEASON,
                "registered": 30,
                "players": self.players
            }),
            encoding="utf-8"
        )

    def run_case(self, death_count, duplicate=False):
        records = [
            {
                "season": SEASON,
                "uuid": p["uuid"],
                "player": p["name"],
                "cause": "TEST"
            }
            for p in self.players[:death_count]
        ]

        if duplicate and records:
            records.append(records[0])

        self.deaths_path.write_text(
            "".join(json.dumps(r) + "\n" for r in records),
            encoding="utf-8"
        )

        completed = subprocess.run(
            [
                sys.executable,
                str(self.root / "scripts" / "season-report.py"),
                "--season", SEASON
            ],
            capture_output=True,
            text=True,
            check=True
        )

        report_path = (
            self.root / "logs" / f"season-report-{SEASON}.json"
        )

        self.assertTrue(report_path.exists(), completed.stdout)

        return json.loads(
            report_path.read_text(encoding="utf-8")
        )

    def test_all_alive(self):
        result = self.run_case(0)
        self.assertEqual(
            (
                result["registered"],
                result["alive"],
                result["eliminated"],
                result["winner_candidate"]
            ),
            (30, 30, 0, None)
        )

    def test_one_survivor(self):
        result = self.run_case(29)
        self.assertEqual(
            (
                result["registered"],
                result["alive"],
                result["eliminated"],
                result["winner_candidate"]
            ),
            (30, 1, 29, "TestPlayer30")
        )

    def test_none_alive(self):
        result = self.run_case(30)
        self.assertEqual(
            (
                result["alive"],
                result["eliminated"],
                result["winner_candidate"]
            ),
            (0, 30, None)
        )

    def test_duplicate_death_does_not_double_count(self):
        result = self.run_case(29, duplicate=True)
        self.assertEqual(
            (
                result["alive"],
                result["eliminated"],
                result["winner_candidate"]
            ),
            (1, 29, "TestPlayer30")
        )

if __name__ == "__main__":
    unittest.main()
