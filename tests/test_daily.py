"""Medallas y modo el piso es lava."""

from __future__ import annotations

import unittest

from game.medals import award, unlocked_by
from game.session import Session
from game.settings import MODE_LAVA, WAGON
from game.world import WAGON_DECK, World
import random


class LavaModeTest(unittest.TestCase):
    def test_lava_spawns_only_wagons_and_deck_biscuits(self) -> None:
        world = World(random.Random(3))
        world.configure(MODE_LAVA)
        world.reset()
        self.assertTrue(world.lava)
        self.assertEqual(world.bonuses, [])
        for obstacle in world.obstacles:
            self.assertEqual(obstacle.kind, WAGON)
        self.assertGreater(len(world.biscuits), 0)
        for biscuit in world.biscuits:
            self.assertAlmostEqual(biscuit.height, WAGON_DECK)

    def test_lava_kills_on_floor(self) -> None:
        session = Session(rng=random.Random(4))
        session.reset(MODE_LAVA)
        # Asegurar que no hay vagón bajo los pies.
        session.world.obstacles.clear()
        session.player.height = 0.0
        session.player.floor = 0.0
        session.player.jumping = False
        session.world._lava_floor(session.player)
        self.assertTrue(session.world.game_over)

    def test_lava_safe_on_deck(self) -> None:
        session = Session(rng=random.Random(5))
        session.reset(MODE_LAVA)
        floor = session.world.support_at(session.player.lane_pos)
        self.assertGreater(floor, 0.0)
        session.player.height = floor
        session.player.floor = floor
        session.world._lava_floor(session.player)
        self.assertFalse(session.world.game_over)


class MedalTest(unittest.TestCase):
    def test_award_unlocks_once(self) -> None:
        self.assertEqual(unlocked_by(400.0), [])
        self.assertIn("barrio", unlocked_by(500.0))
        medals: list[str] = []
        first = award(medals, 1200.0)
        self.assertEqual(first, ["barrio", "avenida"])
        second = award(medals, 1200.0)
        self.assertEqual(second, [])
        self.assertEqual(medals, ["barrio", "avenida"])


if __name__ == "__main__":
    unittest.main()
