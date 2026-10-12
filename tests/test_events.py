"""Los eventos que el mundo y Kovu le tiran a los efectos."""

from __future__ import annotations

import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from game.events import Kind
from game.hitbox import Box
from game.items import Biscuit, Obstacle
from game.player import Player
from game.settings import FULL, PLAYER_DRAW_Z
from game.world import World

FRAME = 1.0 / 60.0


class QuietPlayer:
    def __init__(self, lane: int) -> None:
        self.collision_lane = lane
        self.speed_scale = 1.0
        self.pickup_span = 1.0
        self.spawn_luck = 0
        self.granted: list[str] = []

    def hitbox(self) -> Box:
        return Box(float(self.collision_lane), 0.5, PLAYER_DRAW_Z, 0.55, 0.0, 3.0)

    def grant(self, kind: str) -> None:
        self.granted.append(kind)


class EventsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        pygame.init()

    def test_biscuit_emits(self) -> None:
        world = World()
        world.obstacles.clear()
        world.biscuits.clear()
        world.cursor = 80.0
        world.biscuits.append(Biscuit(lane=1, z=PLAYER_DRAW_Z))

        world.update(FRAME, QuietPlayer(1))

        kinds = [event.kind for event in world.feed.drain()]
        self.assertEqual(kinds, [Kind.BISCUIT])

    def test_crash_emits(self) -> None:
        world = World()
        world.obstacles.clear()
        world.biscuits.clear()
        world.cursor = 80.0
        world.obstacles.append(Obstacle(lane=1, z=PLAYER_DRAW_Z, kind=FULL))

        world.update(FRAME, QuietPlayer(1))

        kinds = [event.kind for event in world.feed.drain()]
        self.assertEqual(kinds, [Kind.CRASH])
        self.assertTrue(world.game_over)

    def test_jump_and_land_emit(self) -> None:
        player = Player()
        player.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_UP))
        self.assertEqual([event.kind for event in player.feed.drain()], [Kind.JUMP])

        while player.jumping:
            player.update(FRAME)
        kinds = [event.kind for event in player.feed.drain()]
        self.assertIn(Kind.LAND, kinds)

    def test_crouch_in_air_fast_falls(self) -> None:
        normal = Player()
        normal._begin_jump()
        for _ in range(10):
            normal.update(FRAME)
        height_normal = normal.height

        dive = Player()
        dive._begin_jump()
        for _ in range(5):
            dive.update(FRAME)
        dive.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN))
        self.assertTrue(dive._fast_fall)
        self.assertFalse(dive.sliding)
        for _ in range(5):
            dive.update(FRAME)
        self.assertLess(dive.height, height_normal)


if __name__ == "__main__":
    unittest.main()

