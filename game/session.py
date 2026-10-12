"""Una carrera: mundo, Kovu y efectos avanzando juntos. La usa la partida y el demo."""

from __future__ import annotations

import random
from typing import Protocol

from game.events import Event
from game.fx import Effects
from game.player import Player
from game.settings import MODE_NORMAL
from game.story import StoryTracker
from game.world import World


class Pilot(Protocol):
    def steer(self, world: World, player: Player) -> None: ...


class AudioBus(Protocol):
    def event(self, event: Event) -> None: ...


class Session:
    def __init__(self, pilot: Pilot | None = None, rng: random.Random | None = None) -> None:
        self.world = World(rng)
        self.player = Player()
        self.effects = Effects()
        self.story = StoryTracker()
        self.mode = MODE_NORMAL
        self._pilot = pilot

    def reset(self, mode: str = MODE_NORMAL) -> None:
        self.mode = mode
        self.player.reset()
        self.world.configure(mode)
        self.world.reset()
        self.effects.reset()
        self.story.reset()

    def step(self, dt: float, audio: AudioBus | None = None) -> None:
        if not self.world.game_over:
            if self._pilot is not None:
                self._pilot.steer(self.world, self.player)
            floor = self.world.support_at(self.player.lane_pos)
            self.player.update(dt, floor)
        self.world.update(self.effects.stall(dt), self.player)
        self.player.settle(self.world.support_at(self.player.lane_pos))
        if not self.world.game_over:
            self.story.update(self.world.distance, dt)
            for beat in self.story.drain_setpieces():
                if beat.setpiece:
                    self.world.apply_setpiece(beat.setpiece)
            # Tras aterrizar, el piso lava se revisa de nuevo con el floor actualizado.
            if not self.world.game_over:
                self.world._lava_floor(self.player)
        self.effects.update(dt, self.world, self.player, audio)
