"""Pruebas del ranking local, sin ventana."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from game.accounts import LocalAccountDAO
from game.dao import LocalArcadeDAO, RankingEntry


class RankingTest(unittest.TestCase):
    def setUp(self) -> None:
        self._dir = tempfile.TemporaryDirectory()
        root = Path(self._dir.name)
        self.path = root / "ranking.json"
        self.accounts = LocalAccountDAO(root / "accounts.json")
        self.dao = LocalArcadeDAO(self.path, limit=3, accounts=self.accounts)

    def tearDown(self) -> None:
        self._dir.cleanup()

    def _register(self, *names: str) -> None:
        for name in names:
            self.accounts.create(name)

    def test_empty_board_accepts_a_positive_score(self) -> None:
        self.assertEqual(self.dao.best(), 0)
        self.assertFalse(self.dao.qualifies(0))
        self.assertTrue(self.dao.qualifies(10))
        self.assertEqual(self.dao.top(), [])

    def test_insert_keeps_only_registered_accounts(self) -> None:
        self._register("KOVU", "LUNA")
        self.assertEqual(self.dao.insert("kovu", 100, 4), 1)
        self.assertEqual(self.dao.insert("luna", 250, 2), 1)
        self.assertEqual(self.dao.insert("nadie", 999, 0), 0)
        self.assertEqual(self.dao.insert("ab", 999, 0), 0)
        rows = self.dao.top()
        self.assertEqual([row.name for row in rows], ["LUNA", "KOVU"])
        self.assertEqual(rows[0].score, 250)
        self.assertEqual(rows[0].biscuits, 2)

    def test_equal_score_keeps_the_earlier_run_ahead(self) -> None:
        self._register("AAA", "BBB")
        self.dao.insert("AAA", 80, 0)
        self.dao.insert("BBB", 80, 0)
        rows = self.dao.top()
        self.assertEqual([row.name for row in rows], ["AAA", "BBB"])

    def test_the_same_account_keeps_a_single_better_score(self) -> None:
        self._register("KOVU")
        self.assertEqual(self.dao.insert("KOVU", 100, 1), 1)
        self.assertEqual(self.dao.insert("KOVU", 40, 3), 0)
        self.assertEqual(len(self.dao.top()), 1)
        self.assertEqual(self.dao.top()[0].score, 100)
        self.assertEqual(self.dao.insert("KOVU", 180, 2), 1)
        rows = self.dao.top()
        self.assertEqual([row.name for row in rows], ["KOVU"])
        self.assertEqual(rows[0].score, 180)
        self.assertEqual(rows[0].biscuits, 2)

    def test_full_board_rejects_a_score_that_does_not_beat_the_last(self) -> None:
        self._register("AAA", "BBB", "CCC", "ZZZ", "NEW")
        self.dao.insert("AAA", 300, 0)
        self.dao.insert("BBB", 200, 0)
        self.dao.insert("CCC", 100, 0)

        self.assertFalse(self.dao.qualifies(100))
        self.assertEqual(self.dao.insert("ZZZ", 100, 0), 0)
        self.assertEqual([row.name for row in self.dao.top()], ["AAA", "BBB", "CCC"])

        self.assertEqual(self.dao.insert("NEW", 150, 1), 3)
        self.assertEqual([row.name for row in self.dao.top()], ["AAA", "BBB", "NEW"])

    def test_corrupt_file_is_treated_as_empty(self) -> None:
        self._register("KOVU")
        self.path.write_text("{no es json", encoding="utf-8")
        self.assertEqual(self.dao.top(), [])
        self.assertEqual(self.dao.insert("KOVU", 40, 1), 1)
        saved = json.loads(self.path.read_text(encoding="utf-8"))
        self.assertEqual(saved["cabinet"], "KOVU-LOCAL")
        self.assertEqual(saved["entries"][0]["name"], "KOVU")

    def test_skips_broken_rows_and_unregistered_names(self) -> None:
        self._register("KOVA")
        payload = {
            "cabinet": "KOVU-LOCAL",
            "entries": [
                {"initials": "kova!", "score": 50, "biscuits": 1, "played_at": "2026-10-06T00:00:00+00:00"},
                {"name": "ZZZ", "score": 80, "biscuits": 0, "played_at": "2026-10-06T00:00:00+00:00"},
                {"initials": "BAD", "score": "50", "played_at": "2026-10-06T00:00:00+00:00"},
                "nope",
            ],
        }
        self.path.write_text(json.dumps(payload), encoding="utf-8")
        rows = self.dao.top()
        self.assertEqual(rows, [RankingEntry("KOVA", 50, 1, "2026-10-06T00:00:00+00:00")])


if __name__ == "__main__":
    unittest.main()
