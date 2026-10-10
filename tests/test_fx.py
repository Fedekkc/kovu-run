"""Partículas, hit-stop y textos flotantes."""

from __future__ import annotations

import os
import unittest
from types import SimpleNamespace

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from game.events import Event, Feed, Kind
from game.fx import STALL_TIME, Effects
from game.player import Player
from game.settings import BISCUIT_POINTS, ROCKET

FRAME = 1.0 / 60.0


class EffectsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        pygame.init()

    def test_biscuit_spawns_sparks_and_floater(self) -> None:
        effects = Effects(1)
        world = SimpleNamespace(feed=Feed(), speed=40.0)
        player = Player()
        world.feed.emit(Event(Kind.BISCUIT, 1.0, 10.0))

        effects.update(FRAME, world, player)

        self.assertGreater(len(effects.particles), 0)
        self.assertEqual(len(effects.floaters), 1)
        self.assertIn(str(BISCUIT_POINTS), effects.floaters[0].text)

    def test_crash_stalls_then_recovers(self) -> None:
        effects = Effects(1)
        world = SimpleNamespace(feed=Feed(), speed=40.0)
        player = Player()
        world.feed.emit(Event(Kind.CRASH, 1.0, 10.0))
        effects.update(FRAME, world, player)

        self.assertEqual(effects.stall(FRAME), 0.0)
        self.assertGreater(effects.flash, 0.0)

        elapsed = 0.0
        while elapsed < STALL_TIME + FRAME:
            effects.stall(FRAME)
            elapsed += FRAME
        self.assertEqual(effects.stall(FRAME), FRAME)

    def test_particles_expire(self) -> None:
        effects = Effects(1)
        world = SimpleNamespace(feed=Feed(), speed=40.0)
        player = Player()
        world.feed.emit(Event(Kind.BONUS, 1.0, 10.0, ROCKET))
        effects.update(FRAME, world, player)
        self.assertGreater(len(effects.particles), 0)

        for _ in range(120):
            effects.update(0.05, world, player)
        self.assertEqual(effects.particles, [])
        self.assertEqual(effects.floaters, [])


if __name__ == "__main__":
    unittest.main()
