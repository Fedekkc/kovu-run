"""Una carrera: mundo, Kovu y efectos avanzando juntos. La usa la partida y el demo."""

from __future__ import annotations

import random
from typing import Protocol

from game.fx import Effects
from game.player import Player
from game.world import World


class Pilot(Protocol):
    def steer(self, world: World, player: Player) -> None: ...


class Session:
    def __init__(self, pilot: Pilot | None = None, rng: random.Random | None = None) -> None:
        self.world = World(rng)
        self.player = Player()
        self.effects = Effects()
        self._pilot = pilot

    def reset(self) -> None:
        self.player.reset()
        self.world.reset()
        self.effects.reset()

    def step(self, dt: float) -> None:
        if not self.world.game_over:
            if self._pilot is not None:
                self._pilot.steer(self.world, self.player)
            self.player.update(dt)
        self.world.update(self.effects.stall(dt), self.player)
        self.effects.update(dt, self.world, self.player)
