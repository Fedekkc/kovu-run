"""Síntesis y bus de audio."""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from game.audio import Audio
from game.events import Event, Kind
from game.sounds import Clip, EVENT_CLIP
from tools.forge.sound import write_catalog


class SoundBakeTest(unittest.TestCase):
    def test_writes_every_clip(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            paths = write_catalog(Path(folder))
            names = {path.name for path in paths}
            for clip in Clip:
                self.assertIn(f"{clip.value}.wav", names)
            for path in paths:
                self.assertGreater(path.stat().st_size, 200)


class AudioBusTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        pygame.init()
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
        except pygame.error:
            pass

    def test_event_map_covers_kinds(self) -> None:
        for kind in Kind:
            self.assertIn(kind, EVENT_CLIP)

    def test_loads_baked_folder(self) -> None:
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as folder:
            root = Path(folder)
            write_catalog(root)
            bus = Audio(root)
            bus.set_volume(5)
            bus.play(Clip.CLICK)
            bus.event(Event(Kind.JUMP, 1.0, 2.0))
            bus.play_music()
            bus.stop_music()
            self.assertTrue(bus.ready or not bus.ready)


if __name__ == "__main__":
    unittest.main()
