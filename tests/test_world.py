"""Pruebas de la simulación del recorrido, sin ventana."""

from __future__ import annotations

import random
import unittest

from game.hitbox import Box
from game.settings import BISCUIT_POINTS, FULL, HIGH, LOW, PLAYER_DRAW_Z, SPAWN_Z
from game.world import Biscuit, World

FRAME = 1.0 / 60.0
REACTION_Z = 28.0


class FakePlayer:
    def __init__(self, lane: int, clear: bool) -> None:
        self.collision_lane = lane
        self.clear = clear
        self.speed_scale = 1.0
        self.pickup_span = 1.0
        self.spawn_luck = 0
        self.granted: list[str] = []

    def hitbox(self) -> Box:
        if self.clear:
            return Box(20.0, 0.1, PLAYER_DRAW_Z, 0.2, 0.0, 0.2)
        return Box(float(self.collision_lane), 0.5, PLAYER_DRAW_Z, 0.55, 0.0, 3.0)

    def grant(self, kind: str) -> None:
        self.granted.append(kind)


def _snapshot(world: World) -> tuple[object, ...]:
    obstacles = [(item.lane, item.z, item.kind) for item in world.obstacles]
    biscuits = [(item.lane, item.z, item.taken) for item in world.biscuits]
    return obstacles, biscuits, world.distance, world.cursor, world.speed


class WorldTest(unittest.TestCase):
    def test_reset_leaves_room_to_react(self) -> None:
        world = World(random.Random(1))

        self.assertGreaterEqual(len(world.obstacles), 1)
        self.assertGreaterEqual(world.cursor, SPAWN_Z)
        for obstacle in world.obstacles:
            self.assertGreaterEqual(obstacle.z, REACTION_Z)
            self.assertIn(obstacle.lane, (0, 1, 2))
            self.assertIn(obstacle.kind, (LOW, HIGH, FULL))

    def test_crash_freezes_the_world(self) -> None:
        world = World(random.Random(1))
        nearest = min(world.obstacles, key=lambda item: item.z)
        player = FakePlayer(nearest.lane, clear=False)
        crashed = False

        for _ in range(20 * 60):
            world.update(FRAME, player)
            if not world.game_over:
                continue
            self.assertEqual(world.catch_timer, 0.0)
            frozen = _snapshot(world)
            world.update(FRAME, player)
            self.assertGreater(world.catch_timer, 0.0)
            self.assertEqual(_snapshot(world), frozen)
            crashed = True
            break

        self.assertTrue(crashed)

    def test_clearing_survives_eight_seconds(self) -> None:
        world = World(random.Random(1))
        player = FakePlayer(0, clear=True)

        for _ in range(8 * 60):
            world.update(FRAME, player)

        self.assertFalse(world.game_over)
        self.assertGreater(world.distance, 0.0)

    def test_pickup_in_window(self) -> None:
        world = World(random.Random(1))
        world.obstacles.clear()
        world.biscuits.clear()
        world.cursor = SPAWN_Z + 50
        world.biscuits.append(Biscuit(lane=1, z=PLAYER_DRAW_Z))

        world.update(FRAME, FakePlayer(1, clear=False))

        self.assertEqual(world.biscuits_taken, 1)
        self.assertEqual(len(world.biscuits), 1)
        self.assertTrue(world.biscuits[0].taken)
        self.assertFalse(world.game_over)

    def test_display_score(self) -> None:
        world = World(random.Random(1))
        self.assertEqual(BISCUIT_POINTS, 25)
        self.assertEqual(world.display_score, 0)

        world.distance = 10.9
        world.biscuits_taken = 4
        expected = int(world.distance) + world.biscuits_taken * 25
        self.assertEqual(world.display_score, expected)


if __name__ == "__main__":
    unittest.main()
