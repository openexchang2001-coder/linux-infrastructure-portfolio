import importlib.util
import unittest
from pathlib import Path

path = (
    Path(__file__).resolve().parents[1]
    / "scripts/winner-status.py"
)

spec = importlib.util.spec_from_file_location(
    "winner_status", path
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class WinnerStatusTests(unittest.TestCase):

    def test_before_event_end(self):
        self.assertEqual(
            module.judge(30, 1, False),
            "IN_PROGRESS"
        )

    def test_one_survivor_after_end(self):
        self.assertEqual(
            module.judge(30, 1, True),
            "WINNER_READY"
        )

    def test_no_survivors(self):
        self.assertEqual(
            module.judge(30, 0, True),
            "NO_SURVIVOR"
        )

    def test_multiple_survivors(self):
        self.assertEqual(
            module.judge(30, 3, True),
            "UNDECIDED"
        )

    def test_insufficient_players(self):
        self.assertEqual(
            module.judge(1, 0, True),
            "NO_CONTEST"
        )


if __name__ == "__main__":
    unittest.main()
