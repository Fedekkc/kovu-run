"""El autopiloto: salta, se agacha y cambia de carril."""

from __future__ import annotations

import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from game.demo import Autopilot
from game.hitbox import PLAYER_Z
from game.items import Obstacle
from game.player import Player
from game.settings import FULL, HIGH, LOW
from game.world import World


class AutopilotTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        pygame.init()

    def _road(self, kind: str, lane: int = 1, gap: float = 2.0) -> tuple[World, Player]:
        world = World()
        world.obstacles.clear()
        world.biscuits.clear()
        world.cursor = 80.0
        world.obstacles.append(Obstacle(lane=lane, z=PLAYER_Z + gap, kind=kind))
        return world, Player()

    def test_jumps_low(self) -> None:
        world, player = self._road(LOW)
        Autopilot().steer(world, player)
        self.assertTrue(player.jumping)

    def test_slides_high(self) -> None:
        world, player = self._road(HIGH)
        Autopilot().steer(world, player)
        self.assertTrue(player.sliding)

    def test_dodges_full(self) -> None:
        world, player = self._road(FULL, lane=1, gap=1.5)
        world.obstacles.append(Obstacle(lane=0, z=PLAYER_Z + 1.0, kind=FULL))
        Autopilot().steer(world, player)
        self.assertEqual(player.lane, 2)


if __name__ == "__main__":
    unittest.main()
