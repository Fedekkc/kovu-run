"""La hora del barrio avanza con los metros y vuelve a empezar."""

from __future__ import annotations

import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from game.cycle import CYCLE_M, NIGHT, STORM, SUNSET, mood_at
from game.player import Player
from game.render import Renderer
from game.settings import HEIGHT, WIDTH
from game.world import World


class CycleTest(unittest.TestCase):
    def test_sunset_night_storm_in_order(self) -> None:
        self.assertEqual(mood_at(0.0), SUNSET)
        self.assertEqual(mood_at(1000.0), NIGHT)
        self.assertEqual(mood_at(1600.0), STORM)

    def test_changes_fade_instead_of_jumping(self) -> None:
        dusk = mood_at(625.0)
        self.assertGreater(dusk.night, 0.0)
        self.assertLess(dusk.night, 1.0)
        self.assertEqual(dusk.rain, 0.0)

    def test_loops_every_cycle(self) -> None:
        self.assertEqual(mood_at(CYCLE_M + 1600.0), mood_at(1600.0))
        self.assertLess(mood_at(CYCLE_M - 1.0).night, 0.01)


class NightFrameTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        pygame.init()
        pygame.display.set_mode((32, 32))

    def _frame(self, distance: float) -> pygame.Surface:
        screen = pygame.Surface((WIDTH, HEIGHT))
        world = World()
        world.distance = distance
        renderer = Renderer(screen)
        renderer.show_hitboxes = False
        renderer.draw(world, Player(), 1.0)
        return screen

    def test_night_darkens_the_frame_but_lamps_still_shine(self) -> None:
        sunset = pygame.transform.average_color(self._frame(100.0))
        night = self._frame(1000.0)
        dark = pygame.transform.average_color(night)
        self.assertLess(sum(dark[:3]), sum(sunset[:3]))
        brightest = max(
            sum(night.get_at((x, y))[:3]) for x in range(0, WIDTH, 4) for y in range(HEIGHT // 3, HEIGHT, 4)
        )
        self.assertGreater(brightest, 500)


if __name__ == "__main__":
    unittest.main()
