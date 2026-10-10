"""Renders every UI screen over the demo with sample data, to review the arcade look.

    py tools/screens.py out-folder
"""

from __future__ import annotations

import os
import random
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pygame

from game.accounts import Account
from game.dao import RankingEntry
from game.demo import Autopilot
from game.render import Renderer
from game.session import Session
from game.settings import HEIGHT, ROCKET, WIDTH
from game.ui import draw_accounts, draw_game_over, draw_hud, draw_menu, draw_naming, draw_upgrades
from game.upgrades import lines_for

WARMUP = 9.0
STEP = 1.0 / 60.0
SAMPLE_TIME = 2.1
NAMES = ("FEDE", "KOVU", "LOLA", "TOTO", "MILO", "NINA", "PIPA")
LEVELS = {"rocket": 2, "super": 5, "double": 1, "jump": 3}


def main(folder: Path) -> None:
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    session = Session(Autopilot(), random.Random(4))
    elapsed = 0.0
    while elapsed < WARMUP:
        session.step(STEP)
        elapsed += STEP
    renderer = Renderer(screen)
    renderer.show_hitboxes = False
    entries = [RankingEntry(name, 3200 - index * 410, 40 - index * 4, "") for index, name in enumerate(NAMES)]
    accounts = [Account(name, 120 - index * 15, {}) for index, name in enumerate(NAMES[:4])]
    folder.mkdir(parents=True, exist_ok=True)

    def shot(name: str) -> None:
        pygame.image.save(screen, str(folder / f"ui_{name}.png"))

    def backdrop() -> None:
        renderer.draw(session.world, session.player, elapsed, session.effects)

    backdrop()
    draw_menu(screen, entries, SAMPLE_TIME, "FEDE", 87)
    shot("menu")
    backdrop()
    draw_accounts(screen, accounts, accounts[0], 1)
    shot("accounts")
    backdrop()
    draw_naming(screen, "KOV", "", SAMPLE_TIME)
    shot("naming")
    backdrop()
    draw_upgrades(screen, lines_for(LEVELS), 87, "FEDE", 1, "No alcanzan las galletas.")
    shot("upgrades")
    session.player.grant(ROCKET)
    session.step(0.6)
    backdrop()
    draw_hud(screen, 1874, 3200, 23, session.player.power_label, session.player.charge)
    shot("hud")
    backdrop()
    draw_hud(screen, 1874, 3200, 23)
    draw_game_over(screen, 1874, 3200, 3, 23, SAMPLE_TIME)
    shot("over")


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("screens"))
