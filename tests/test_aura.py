"""Cada poder lleva su color: coral, rosa o cian."""

from __future__ import annotations

import os
import unittest
from types import SimpleNamespace

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from game.fx import POWER_GLOW
from game.palette import Tone
from game.render import Renderer, _armed_power
from game.settings import DOUBLE_JUMP, HEIGHT, ROCKET, SUPER_JUMP, WIDTH
from game.world import World


class AuraTest(unittest.TestCase):
    def test_power_colors(self) -> None:
        self.assertEqual(POWER_GLOW[ROCKET], Tone.CORAL)
        self.assertEqual(POWER_GLOW[SUPER_JUMP], Tone.NEON_PINK)
        self.assertEqual(POWER_GLOW[DOUBLE_JUMP], Tone.NEON_CYAN)

    def test_armed_power_priority(self) -> None:
        base = dict(
            rocket_time=0.0,
            powered=False,
            super_armed=False,
            extra_jumps=0,
            flipping=False,
        )
        self.assertIsNone(_armed_power(SimpleNamespace(**base)))
        self.assertEqual(_armed_power(SimpleNamespace(**{**base, "rocket_time": 1.0})), ROCKET)
        self.assertEqual(_armed_power(SimpleNamespace(**{**base, "super_armed": True})), SUPER_JUMP)
        self.assertEqual(_armed_power(SimpleNamespace(**{**base, "powered": True})), SUPER_JUMP)
        self.assertEqual(_armed_power(SimpleNamespace(**{**base, "extra_jumps": 1})), DOUBLE_JUMP)
        self.assertEqual(_armed_power(SimpleNamespace(**{**base, "flipping": True})), DOUBLE_JUMP)
        self.assertEqual(
            _armed_power(SimpleNamespace(**{**base, "rocket_time": 1.0, "super_armed": True})),
            ROCKET,
        )

    def test_bonus_aura_draws(self) -> None:
        pygame.init()
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        world = World()
        world.obstacles.clear()
        world.biscuits.clear()
        world.bonuses.clear()
        from game.items import Bonus

        world.bonuses.append(Bonus(lane=1, z=18.0, kind=ROCKET))
        world.bonuses.append(Bonus(lane=0, z=22.0, kind=SUPER_JUMP))
        world.bonuses.append(Bonus(lane=2, z=26.0, kind=DOUBLE_JUMP))
        renderer = Renderer(screen)
        renderer.show_hitboxes = False
        from game.player import Player

        renderer.draw(world, Player(), 1.2)
        self.assertEqual(screen.get_size(), (WIDTH, HEIGHT))


if __name__ == "__main__":
    unittest.main()
