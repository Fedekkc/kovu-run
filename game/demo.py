"""El modo demo: un piloto automático que corre detrás de los menús."""

from __future__ import annotations

import pygame

from game.hitbox import PLAYER_Z
from game.player import Player
from game.session import Session
from game.settings import FULL, HIGH, LOW, WAGON
from game.world import LANES, World

JUMP_LEAD = 0.2
SLIDE_LEAD = 0.12
DODGE_LEAD = 0.45
JUMP_PAD = 0.6
SLIDE_PAD = 0.8
DODGE_PAD = 2.0
CLEAR = 1000.0
RESTART_AFTER = 1.6

_JUMP = pygame.K_UP
_SLIDE = pygame.K_DOWN
_LEFT = pygame.K_LEFT
_RIGHT = pygame.K_RIGHT


class Autopilot:
    """Reads the road ahead like a player would and presses the same keys."""

    def steer(self, world: World, player: Player) -> None:
        if player.rocket_time > 0.0 or player.jumping or player.sliding:
            return
        pace = world.speed * player.speed_scale
        ahead = self._ahead(world, player.lane)
        if ahead is None:
            return
        kind, gap = ahead
        if kind == FULL and gap <= pace * DODGE_LEAD + DODGE_PAD:
            self._dodge(world, player)
        elif kind in (LOW, WAGON) and player.floor <= 0.0 and gap <= pace * JUMP_LEAD + JUMP_PAD:
            self._press(player, _JUMP)
        elif kind == HIGH and gap <= pace * SLIDE_LEAD + SLIDE_PAD:
            self._press(player, _SLIDE)

    def _ahead(self, world: World, lane: int) -> tuple[str, float] | None:
        nearest: tuple[str, float] | None = None
        for obstacle in world.obstacles:
            gap = obstacle.z - PLAYER_Z
            if obstacle.lane != lane or gap < 0.0:
                continue
            if nearest is None or gap < nearest[1]:
                nearest = (obstacle.kind, gap)
        return nearest

    def _dodge(self, world: World, player: Player) -> None:
        def room(lane: int) -> float:
            ahead = self._ahead(world, lane)
            return CLEAR if ahead is None else ahead[1]

        best = max((lane for lane in LANES if abs(lane - player.lane) == 1), key=room)
        self._press(player, _LEFT if best < player.lane else _RIGHT)

    def _press(self, player: Player, key: int) -> None:
        player.handle_event(pygame.event.Event(pygame.KEYDOWN, key=key))


class Demo:
    """The attract loop: a session on autopilot that restarts after every catch."""

    def __init__(self) -> None:
        self.session = Session(Autopilot())

    def update(self, dt: float) -> None:
        world = self.session.world
        if world.game_over and world.catch_timer > RESTART_AFTER:
            self.session.reset()
        self.session.step(dt)
