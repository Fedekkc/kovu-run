"""Las cajas coinciden con saltar, agacharse y un objeto que cruza en un frame."""

from __future__ import annotations

import unittest

from game.hitbox import (
    obstacle_box,
    overlaps,
    overlaps_swept,
    player_hitbox,
    px_to_units,
    HIGH_GAP_PX,
)
from game.player import Player
from game.settings import FULL, HIGH, LOW, PLAYER_DRAW_Z


class HitboxTest(unittest.TestCase):
    def test_standing_hits_a_hedge_and_a_jump_clears_it(self) -> None:
        player = Player()
        hedge = obstacle_box(LOW, 1, PLAYER_DRAW_Z, 0.0)
        self.assertTrue(overlaps(player.hitbox(), hedge))
        player.height = 0.55
        player.jumping = True
        self.assertFalse(overlaps(player.hitbox(), hedge))

    def test_slide_passes_under_the_banner(self) -> None:
        player = Player()
        banner = obstacle_box(HIGH, 1, PLAYER_DRAW_Z, 0.0)
        self.assertGreater(player.hitbox().top, px_to_units(HIGH_GAP_PX))
        self.assertTrue(overlaps(player.hitbox(), banner))
        player.sliding = True
        self.assertLess(player.hitbox().top, banner.bottom)
        self.assertFalse(overlaps(player.hitbox(), banner))

    def test_a_fast_obstacle_cannot_tunnel(self) -> None:
        player = Player()
        landed_z = PLAYER_DRAW_Z - 4.0
        box = obstacle_box(FULL, 1, landed_z, 0.0)
        self.assertFalse(overlaps(player_hitbox(player), box))
        self.assertTrue(overlaps_swept(player.hitbox(), box, PLAYER_DRAW_Z + 4.0))


if __name__ == "__main__":
    unittest.main()
