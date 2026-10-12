"""Hitos narrativos por distancia."""

from __future__ import annotations

import unittest

from game.story import BEATS, StoryTracker
from game.world import World
import random


class StoryTest(unittest.TestCase):
    def test_fires_beats_when_crossing_meters(self) -> None:
        tracker = StoryTracker()
        first = tracker.update(50.0, 0.016)
        self.assertEqual(first, [])
        fired = tracker.update(100.0, 0.016)
        self.assertEqual(len(fired), 1)
        self.assertEqual(fired[0].id, "start")
        self.assertIsNotNone(tracker.toast)
        again = tracker.update(120.0, 0.016)
        self.assertEqual(again, [])

    def test_setpiece_chase_boosts_world(self) -> None:
        world = World(random.Random(1))
        tracker = StoryTracker()
        tracker.update(400.0, 0.016)
        pieces = tracker.drain_setpieces()
        self.assertTrue(any(beat.setpiece == "chase" for beat in pieces))
        for beat in pieces:
            if beat.setpiece:
                world.apply_setpiece(beat.setpiece)
        self.assertGreater(world.chase_boost, 0.0)
        self.assertGreater(world.chase_pressure, 0.0)

    def test_beats_table_is_ordered(self) -> None:
        distances = [beat.at_m for beat in BEATS]
        self.assertEqual(distances, sorted(distances))


if __name__ == "__main__":
    unittest.main()
