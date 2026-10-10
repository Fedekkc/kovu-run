"""Factory method de las piezas y el efecto de cada bonus."""

from __future__ import annotations

import unittest

from game.factory import TrackFactory
from game.hitbox import obstacle_box, overlaps, player_hitbox
from game.items import Biscuit, Bonus, Obstacle
from game.player import Player
from game.settings import (
    BISCUIT,
    DOUBLE_HOLD,
    DOUBLE_JUMP,
    FULL,
    HIGH,
    LOW,
    PLAYER_DRAW_Z,
    ROCKET,
    ROCKET_TIME,
    SUPER_HOLD,
    SUPER_JUMP,
    SUPER_JUMP_TIME,
    WAGON,
)
from game.world import World


class FactoryTest(unittest.TestCase):
    def setUp(self) -> None:
        self.factory = TrackFactory()

    def test_each_kind_uses_its_creator(self) -> None:
        self.assertIsInstance(self.factory.create(LOW, 0, 12), Obstacle)
        self.assertIsInstance(self.factory.create(HIGH, 1, 12), Obstacle)
        self.assertIsInstance(self.factory.create(FULL, 2, 12), Obstacle)
        wagon = self.factory.create(WAGON, 1, 12)
        self.assertIsInstance(wagon, Obstacle)
        self.assertTrue(wagon.climbable)
        self.assertIsInstance(self.factory.create(BISCUIT, 1, 8), Biscuit)
        rocket = self.factory.create(ROCKET, 1, 8)
        spring = self.factory.create(SUPER_JUMP, 0, 8)
        hops = self.factory.create(DOUBLE_JUMP, 2, 8)
        self.assertIsInstance(rocket, Bonus)
        self.assertIsInstance(spring, Bonus)
        self.assertIsInstance(hops, Bonus)
        self.assertEqual(rocket.kind, ROCKET)
        self.assertTrue(self.factory.create(FULL, 1, 4).lethal)

    def test_unknown_kind_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self.factory.create("escudo", 1, 4)


class BonusTest(unittest.TestCase):
    def test_rocket_flies_over_obstacles_and_then_lands(self) -> None:
        player = Player()
        player.grant(ROCKET)
        full = obstacle_box(FULL, player.lane_pos, PLAYER_DRAW_Z, 0.0)
        banner = obstacle_box(HIGH, player.lane_pos, PLAYER_DRAW_Z, 0.0)
        self.assertFalse(overlaps(player.hitbox(), full))
        self.assertFalse(overlaps(player.hitbox(), banner))
        self.assertGreater(player.speed_scale, 1.0)
        self.assertEqual(player.power_label, "Cohete")
        player.update(ROCKET_TIME + 0.05)
        self.assertTrue(overlaps(player.hitbox(), full))
        self.assertEqual(player.height, 0.0)
        self.assertEqual(player.power_label, "")

    def test_super_jump_clears_a_full_obstacle(self) -> None:
        player = Player()
        player.grant(SUPER_JUMP)
        self.assertGreater(player.super_time, 0.0)
        player._begin_jump()
        self.assertGreater(player.super_time, 0.0)
        self.assertGreaterEqual(player._jump_limit, SUPER_JUMP_TIME)
        player.update(0.25)
        full = obstacle_box(FULL, player.lane_pos, PLAYER_DRAW_Z, 0.0)
        low = obstacle_box(LOW, player.lane_pos, PLAYER_DRAW_Z, 0.0)
        banner = obstacle_box(HIGH, player.lane_pos, PLAYER_DRAW_Z, 0.0)
        self.assertFalse(overlaps(player.hitbox(), low))
        self.assertFalse(overlaps(player.hitbox(), full))
        self.assertFalse(overlaps(player.hitbox(), banner))

    def test_super_hold_is_reusable_until_it_expires(self) -> None:
        player = Player()
        player.grant(SUPER_JUMP)
        player._begin_jump()
        self.assertTrue(player.powered)
        while player.jumping:
            player.update(1.0 / 60.0)
        player._begin_jump()
        self.assertTrue(player.powered)
        self.assertGreater(player.super_time, 0.0)
        player.update(SUPER_HOLD + 0.05)
        self.assertFalse(player.super_armed)
        while player.jumping:
            player.update(1.0 / 60.0)
        player._begin_jump()
        self.assertFalse(player.powered)
        self.assertAlmostEqual(player._jump_limit, player.mods.jump_time)

    def test_double_jump_spends_the_extra_hop(self) -> None:
        player = Player()
        player.grant(DOUBLE_JUMP)
        self.assertAlmostEqual(player.double_time, DOUBLE_HOLD)
        player._begin_jump()
        player.update(0.2)
        player._begin_jump()
        self.assertTrue(player.jumping)
        self.assertEqual(player.extra_jumps, 0)
        self.assertGreater(player.double_time, 0.0)
        player._begin_jump()
        self.assertEqual(player.extra_jumps, 0)
        peak = player.height
        for _ in range(90):
            player.update(1.0 / 60.0)
            peak = max(peak, player.height)
        self.assertGreater(peak, 1.7)

    def test_double_hold_rearms_on_the_next_jump(self) -> None:
        player = Player()
        player.grant(DOUBLE_JUMP)
        player._begin_jump()
        player.update(0.15)
        player._begin_jump()
        self.assertEqual(player.extra_jumps, 0)
        while player.jumping:
            player.update(1.0 / 60.0)
        self.assertEqual(player.extra_jumps, 1)
        player._begin_jump()
        player.update(0.15)
        player._begin_jump()
        self.assertTrue(player.flipping)

    def test_double_hold_expires_before_the_second_hop(self) -> None:
        player = Player()
        player.grant(DOUBLE_JUMP)
        player._begin_jump()
        player.update(DOUBLE_HOLD + 0.05)
        self.assertEqual(player.extra_jumps, 0)
        player._begin_jump()
        self.assertFalse(player.flipping)

    def test_world_grants_a_bonus_in_the_lane(self) -> None:
        world = World()
        world.obstacles.clear()
        world.biscuits.clear()
        world.bonuses.clear()
        world.cursor = 400
        world.bonuses.append(world.factory.create(ROCKET, 1, PLAYER_DRAW_Z))
        player = Player()

        world.update(1.0 / 60.0, player)

        self.assertGreater(player.rocket_time, 0.0)
        self.assertTrue(world.bonuses[0].taken)


if __name__ == "__main__":
    unittest.main()
