"""Renders a fixed gameplay scene to a PNG so art changes can be compared.

    py tools/snapshot.py out.png [boxes] [run|rocket|super|flip|caught|night|storm]
"""

from __future__ import annotations

import os
import sys
from collections.abc import Callable
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pygame

from game.player import Player
from game.render import Renderer
from game.settings import BISCUIT, DOUBLE_JUMP, FULL, HEIGHT, HIGH, LOW, ROCKET, SUPER_JUMP, WIDTH
from game.world import World

SCENE_DISTANCE = 412.0
SCENE_TIME = 3.4
RUN_TIME = 0.37
CATCH_TIMER = 0.9
NIGHT_AT = 1000.0
STORM_AT = 1600.0
BOXES = "boxes"
PIECES = (
    (LOW, 0, 8.0),
    (LOW, 2, 16.0),
    (FULL, 2, 23.0),
    (HIGH, 1, 30.0),
    (LOW, 0, 40.0),
    (FULL, 0, 58.0),
    (FULL, 1, 48.0),
    (LOW, 2, 52.0),
)
BISCUITS = ((0, 6.0), (0, 8.5), (0, 11.0), (2, 12.0), (2, 14.5))
BONUSES = ((2, 34.0, SUPER_JUMP), (0, 26.0, ROCKET), (1, 20.0, DOUBLE_JUMP))


def _jump(player: Player) -> None:
    player.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_UP))


def _run(player: Player, world: World) -> None:
    return


def _rocket(player: Player, world: World) -> None:
    player.grant(ROCKET)
    player.update(0.0)


def _super(player: Player, world: World) -> None:
    player.grant(SUPER_JUMP)
    _jump(player)
    player.update(0.3)


def _flip(player: Player, world: World) -> None:
    player.grant(DOUBLE_JUMP)
    _jump(player)
    player.update(0.25)
    _jump(player)
    player.update(0.1)


def _caught(player: Player, world: World) -> None:
    world.game_over = True
    world.catch_timer = CATCH_TIMER


def _night(player: Player, world: World) -> None:
    world.distance = NIGHT_AT


def _storm(player: Player, world: World) -> None:
    world.distance = STORM_AT


POSES: dict[str, Callable[[Player, World], None]] = {
    "run": _run,
    "rocket": _rocket,
    "super": _super,
    "flip": _flip,
    "caught": _caught,
    "night": _night,
    "storm": _storm,
}


def render(target: Path, hitboxes: bool, pose: str) -> None:
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    world = World()
    world.obstacles.clear()
    world.biscuits.clear()
    world.bonuses.clear()
    world.distance = SCENE_DISTANCE
    for kind, lane, z in PIECES:
        world.obstacles.append(world.factory.create(kind, lane, z))
    for lane, z in BISCUITS:
        world.biscuits.append(world.factory.create(BISCUIT, lane, z))
    for lane, z, kind in BONUSES:
        world.bonuses.append(world.factory.create(kind, lane, z))
    player = Player()
    player.run_time = RUN_TIME
    POSES[pose](player, world)
    renderer = Renderer(screen)
    renderer.show_hitboxes = hitboxes
    renderer.draw(world, player, SCENE_TIME)
    target.parent.mkdir(parents=True, exist_ok=True)
    pygame.image.save(screen, str(target))


if __name__ == "__main__":
    args = sys.argv[1:]
    out = Path(args[0]) if args else Path("snapshot.png")
    boxes = BOXES in args
    chosen = next((arg for arg in args[1:] if arg in POSES), "run")
    render(out, boxes, chosen)
