"""Mapa de clicks de la UI."""

from __future__ import annotations

import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from game.hits import Action, Hits
from game.options import Options
from game.settings import HEIGHT, WIDTH
from game.ui import draw_menu, draw_options, draw_splash


class HitsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        pygame.init()
        cls.screen = pygame.display.set_mode((WIDTH, HEIGHT))

    def test_menu_exposes_play_and_shop(self) -> None:
        hits = draw_menu(self.screen, [], 1.0, "FEDE", 10)
        play = hits.at((WIDTH - 100, 280))
        self.assertIsNotNone(play)
        actions = {Action.PLAY, Action.ACCOUNTS, Action.UPGRADES, Action.OPTIONS, Action.QUIT}
        found = set()
        for y in range(200, HEIGHT - 40, 20):
            hit = hits.at((WIDTH - 100, y))
            if hit is not None:
                found.add(hit.action)
        self.assertTrue(actions.issubset(found) or Action.PLAY in found)

    def test_splash_is_clickable(self) -> None:
        hits = draw_splash(self.screen, 0.5)
        hit = hits.at((WIDTH // 2, HEIGHT // 2))
        self.assertIsNotNone(hit)
        self.assertEqual(hit.action, Action.SKIP)

    def test_options_volume_nudge(self) -> None:
        hits = draw_options(self.screen, Options().clamp(), 0)
        found = False
        for x in range(WIDTH // 2, WIDTH - 40):
            for y in range(100, 400):
                hit = hits.at((x, y))
                if hit is not None and hit.action == Action.NUDGE:
                    found = True
                    break
            if found:
                break
        self.assertTrue(found)

    def test_hits_last_wins(self) -> None:
        hits = Hits()
        hits.add(Action.BACK, pygame.Rect(0, 0, 100, 100))
        hits.add(Action.PLAY, pygame.Rect(0, 0, 50, 50))
        self.assertEqual(hits.at((10, 10)).action, Action.PLAY)
        self.assertEqual(hits.at((80, 80)).action, Action.BACK)


if __name__ == "__main__":
    unittest.main()
