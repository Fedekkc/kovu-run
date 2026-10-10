"""Cuentas locales y la tienda de mejoras, sin ventana."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import pygame

from game.accounts import Account, AccountError, LocalAccountDAO, normalize_name
from game.name import NameBuffer
from game.player import Player
from game.settings import LANE_SWITCH, ROCKET, ROCKET_TIME
from game.upgrades import MAX_LEVEL, banked_biscuits, lines_for, purchase, run_mods


class UpgradeTest(unittest.TestCase):
    def test_level_zero_matches_the_base_run(self) -> None:
        mods = run_mods({})
        self.assertEqual(mods.rocket_time, ROCKET_TIME)
        self.assertEqual(mods.jump_scale, 1.0)
        self.assertEqual(mods.lane_switch, LANE_SWITCH)

    def test_rocket_and_agility_move_in_the_expected_direction(self) -> None:
        mods = run_mods({"rocket": 2, "agility": 3, "jump": 2})
        self.assertGreater(mods.rocket_time, ROCKET_TIME)
        self.assertLess(mods.lane_switch, LANE_SWITCH)
        self.assertGreater(mods.jump_scale, 1.0)

    def test_lines_show_the_next_step_until_max(self) -> None:
        rocket = lines_for({})[0]
        self.assertEqual(rocket.id, "rocket")
        self.assertEqual(rocket.cost, 45)
        self.assertIn("→", rocket.effect)
        self.assertEqual(rocket.effect.count("vuelo"), 1)
        maxed = lines_for({"rocket": MAX_LEVEL})[0]
        self.assertIsNone(maxed.cost)
        self.assertNotIn("→", maxed.effect)

    def test_purchase_spends_biscuits_and_stops_at_max(self) -> None:
        account = Account("KOVU", 45, {})
        self.assertEqual(purchase(account, "rocket"), "")
        self.assertEqual(account.biscuits, 0)
        self.assertEqual(account.levels["rocket"], 1)
        self.assertEqual(purchase(account, "rocket"), "No alcanzan las galletas.")
        account.biscuits = 1000
        for _ in range(10):
            purchase(account, "jump")
        self.assertEqual(account.levels["jump"], MAX_LEVEL)
        self.assertEqual(purchase(account, "jump"), "Ya está al máximo.")
        self.assertEqual(purchase(account, "escudo"), "Esa mejora no existe.")

    def test_meta_upgrades_affect_run_and_bank(self) -> None:
        mods = run_mods({"magnet": 3, "lucky": 2, "vault": 4})
        self.assertGreater(mods.pickup_span, 1.0)
        self.assertEqual(mods.luck_weight, 2)
        self.assertGreater(mods.bank_rate, 0.0)
        self.assertEqual(banked_biscuits(10, mods.bank_rate), 13)

    def test_catalog_has_nine_lines(self) -> None:
        self.assertEqual(len(lines_for({})), 9)

    def test_equipped_rocket_lasts_longer(self) -> None:
        player = Player()
        player.equip(run_mods({"rocket": 2}))
        player.grant(ROCKET)
        self.assertGreater(player.rocket_time, ROCKET_TIME)
        player.update(ROCKET_TIME + 0.05)
        self.assertGreater(player.rocket_time, 0.0)
        self.assertGreater(player.height, 0.0)


class AccountDaoTest(unittest.TestCase):
    def setUp(self) -> None:
        self._dir = tempfile.TemporaryDirectory()
        self.path = Path(self._dir.name) / "accounts.json"
        self.dao = LocalAccountDAO(self.path)

    def tearDown(self) -> None:
        self._dir.cleanup()

    def test_create_selects_and_normalizes(self) -> None:
        created = self.dao.create("ko vu!")
        self.assertEqual(created.name, "KOVU")
        self.assertEqual(self.dao.active().name, "KOVU")
        with self.assertRaises(AccountError):
            self.dao.create("ab")
        with self.assertRaises(AccountError):
            self.dao.create("kovu")

    def test_select_and_update_keep_the_other_accounts(self) -> None:
        self.dao.create("KOVU")
        self.dao.create("LUNA")
        self.assertEqual(self.dao.active().name, "LUNA")
        self.dao.select("kovu")
        self.assertEqual(self.dao.active().name, "KOVU")
        account = self.dao.active()
        account.biscuits = 15
        account.levels["rocket"] = 2
        self.dao.update(account)
        rows = self.dao.list()
        self.assertEqual([row.name for row in rows], ["KOVU", "LUNA"])
        self.assertEqual(rows[0].biscuits, 15)
        self.assertEqual(rows[0].levels, {"rocket": 2})
        self.assertEqual(rows[1].biscuits, 0)

    def test_corrupt_file_is_quarantined_and_starts_empty(self) -> None:
        self.path.write_text("{no es json", encoding="utf-8")
        self.assertEqual(self.dao.list(), [])
        self.assertIsNone(self.dao.active())
        backups = list(self.path.parent.glob("accounts.corrupt-*.json"))
        self.assertEqual(len(backups), 1)
        self.dao.create("KOVU")
        saved = json.loads(self.path.read_text(encoding="utf-8"))
        self.assertEqual(saved["active"], "KOVU")
        self.assertEqual(saved["accounts"][0]["name"], "KOVU")

    def test_skips_broken_rows_and_a_missing_active_name(self) -> None:
        payload = {
            "active": "NADIE",
            "accounts": [
                {"name": "kova!", "biscuits": 4, "levels": {"rocket": 1, "bad": "x"}},
                {"name": "no", "biscuits": 1, "levels": {}},
                "basura",
            ],
        }
        self.path.write_text(json.dumps(payload), encoding="utf-8")
        rows = self.dao.list()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].name, "KOVA")
        self.assertEqual(rows[0].biscuits, 4)
        self.assertEqual(rows[0].levels, {"rocket": 1})
        self.assertIsNone(self.dao.active())

    def test_normalize_name(self) -> None:
        self.assertEqual(normalize_name("k1o!vu"), "KOVU")
        self.assertEqual(normalize_name("ABCDEFGHIJKLM"), "ABCDEFGHIJ")


class NameBufferTest(unittest.TestCase):
    def test_letters_build_a_name_and_enter_waits_for_three(self) -> None:
        buffer = NameBuffer()
        self.assertFalse(buffer.handle_key(pygame.K_k))
        self.assertFalse(buffer.handle_key(pygame.K_o))
        self.assertFalse(buffer.handle_key(pygame.K_RETURN))
        self.assertEqual(buffer.text, "KO")
        buffer.handle_key(pygame.K_v)
        self.assertTrue(buffer.handle_key(pygame.K_RETURN))
        self.assertEqual(buffer.text, "KOV")
        buffer.handle_key(pygame.K_BACKSPACE)
        self.assertEqual(buffer.text, "KO")


if __name__ == "__main__":
    unittest.main()
