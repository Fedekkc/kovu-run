"""Fuente pixel y pantallas arcade: todo el copy tiene glifo y se dibuja."""

from __future__ import annotations

import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from game import fx, ui
from game.accounts import (
    COPY_MISSING,
    COPY_NAME_SHORT,
    COPY_NAME_TAKEN,
    Account,
)
from game.dao import RankingEntry
from game.pixelfont import default_font
from game.render import Renderer
from game.session import Session
from game.options import Options
from game.settings import HEIGHT, TITLE, WIDTH
from game.ui import (
    draw_accounts,
    draw_game_over,
    draw_hud,
    draw_menu,
    draw_naming,
    draw_options,
    draw_splash,
    draw_upgrades,
)
from game.upgrades import (
    COPY_BROKE,
    COPY_MAXED,
    COPY_MISSING as COPY_UPGRADE_MISSING,
    POWER_LABEL,
    lines_for,
)


def _copy_texts(module: object) -> list[str]:
    texts: list[str] = []
    for name, value in vars(module).items():
        if not name.startswith("COPY_"):
            continue
        if isinstance(value, dict):
            texts.extend(str(item) for item in value.values())
        else:
            texts.append(str(value))
    return texts


class PixelFontTest(unittest.TestCase):
    def test_covers_every_copy_string(self) -> None:
        font = default_font()
        samples = [
            TITLE,
            COPY_NAME_SHORT,
            COPY_NAME_TAKEN,
            COPY_MISSING,
            COPY_BROKE,
            COPY_MAXED,
            COPY_UPGRADE_MISSING,
            *POWER_LABEL.values(),
            *_copy_texts(ui),
            *_copy_texts(fx),
            ui.COPY_VOLUME_BAR.format(filled="===", empty="---", level=3),
            ui.COPY_STATS_TODAY.format(runs=2, average=40),
        ]
        for line in lines_for({"rocket": 2, "super": 5}):
            samples.append(line.name)
            samples.append(line.effect)
        for text in samples:
            filled = text.format(
                points=25,
                count=3,
                cost=16,
                best=100,
                rank=2,
                place=1,
                filled="===",
                empty="---",
                level=3,
                runs=2,
                average=40,
                mult=2,
                names="Barrio",
                have=3,
                need=8,
                heat="1.5",
            )
            self.assertTrue(font.covers(filled), filled)


class UiDrawTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        pygame.init()
        cls.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        cls.session = Session()
        cls.renderer = Renderer(cls.screen)
        cls.renderer.show_hitboxes = False

    def _backdrop(self) -> None:
        self.renderer.draw(self.session.world, self.session.player, 1.0, self.session.effects)

    def test_menu_hud_and_over_draw(self) -> None:
        entries = [RankingEntry("FEDE", 1000, 10, "")]
        accounts = [Account("FEDE", 40, {})]
        self._backdrop()
        self.assertIsNotNone(draw_menu(self.screen, entries, 1.5, "FEDE", 40))
        draw_hud(self.screen, 120, 1000, 4, "Cohete", 0.6)
        self.assertIsNotNone(draw_game_over(self.screen, 120, 1000, 1, 4, 1.0))
        self.assertIsNotNone(draw_accounts(self.screen, accounts, accounts[0], 0))
        self.assertIsNotNone(draw_naming(self.screen, "KOV", "", 1.0))
        self.assertIsNotNone(draw_upgrades(self.screen, lines_for({}), 40, "FEDE", 0, ""))
        self.assertIsNotNone(draw_splash(self.screen, 0.5))
        self.assertIsNotNone(draw_options(self.screen, Options().clamp(), 1))
        self.assertEqual(self.screen.get_size(), (WIDTH, HEIGHT))


if __name__ == "__main__":
    unittest.main()
