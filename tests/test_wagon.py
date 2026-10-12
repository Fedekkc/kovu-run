"""Vagones trepables: techo seguro, frente letal."""

from __future__ import annotations

import unittest

from game.hitbox import PLAYER_Z, obstacle_box, on_deck, overlaps, player_hitbox
from game.items import Obstacle
from game.player import Player
from game.settings import FULL, PLAYER_DRAW_Z, WAGON
from game.world import World


class WagonTest(unittest.TestCase):
    def test_deck_is_safe_and_front_is_not(self) -> None:
        player = Player()
        wagon = obstacle_box(WAGON, 1, PLAYER_DRAW_Z, 0.0)
        self.assertTrue(overlaps(player.hitbox(), wagon))
        self.assertFalse(on_deck(player.hitbox(), wagon))
        player.height = wagon.top
        player.floor = wagon.top
        self.assertTrue(on_deck(player.hitbox(), wagon))
        # Pies al ras del techo: no penetran el sólido, pero el deck los sostiene.
        self.assertFalse(overlaps(player.hitbox(), wagon))

    def test_support_and_settle_keep_kovu_on_the_roof(self) -> None:
        world = World()
        world.obstacles.clear()
        world.biscuits.clear()
        world.bonuses.clear()
        world.obstacles.append(Obstacle(1, PLAYER_Z, WAGON))
        top = world.support_at(1.0)
        self.assertGreater(top, 0.55)
        player = Player()
        player.update(0.0, top)
        self.assertAlmostEqual(player.height, top)
        self.assertAlmostEqual(player.floor, top)
        body = player_hitbox(player)
        box = obstacle_box(WAGON, 1, PLAYER_Z, 0.0)
        self.assertTrue(on_deck(body, box))

    def test_world_does_not_crash_when_running_on_deck(self) -> None:
        world = World()
        world.obstacles.clear()
        world.biscuits.clear()
        world.bonuses.clear()
        world.obstacles.append(Obstacle(1, PLAYER_Z, WAGON))
        top = world.support_at(1.0)
        player = Player()
        player.height = top
        player.floor = top

        class Rider:
            speed_scale = 1.0
            pickup_span = 1.0
            spawn_luck = 0

            def hitbox(self):
                return player.hitbox()

            def grant(self, kind: str) -> None:
                return None

        world.update(1.0 / 60.0, Rider())
        self.assertFalse(world.game_over)

    def test_landing_on_wagon_during_jump(self) -> None:
        player = Player()
        wagon = obstacle_box(WAGON, 1, PLAYER_DRAW_Z, 0.0)
        player._begin_jump()
        for _ in range(40):
            player.update(1.0 / 60.0, wagon.top)
            if not player.jumping:
                break
        self.assertFalse(player.jumping)
        self.assertAlmostEqual(player.height, wagon.top, places=2)

    def test_wagon_is_climbable(self) -> None:
        self.assertTrue(Obstacle(1, 10.0, WAGON).climbable)
        self.assertFalse(Obstacle(1, 10.0, FULL).climbable)

    def test_one_biscuit_per_wagon_car(self) -> None:
        world = World()
        world.obstacles.clear()
        world.biscuits.clear()
        world.bonuses.clear()
        world.cursor = 0.0
        world._wagon(10.0)
        wagons = [item for item in world.obstacles if item.kind == WAGON]
        self.assertEqual(len(world.biscuits), len(wagons))
        for biscuit, wagon in zip(world.biscuits, wagons):
            self.assertAlmostEqual(biscuit.z, wagon.z)
            self.assertGreater(biscuit.height, 0.5)


if __name__ == "__main__":
    unittest.main()
