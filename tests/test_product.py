"""Opciones, telemetría, crash log y pantallas de producto."""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from game.crashlog import write_crash
from game.options import Options, OptionsStore, VOLUME_MAX
from game.settings import HEIGHT, WIDTH
from game.telemetry import Telemetry
from game.ui import draw_credits, draw_options, draw_splash


class OptionsTest(unittest.TestCase):
    def setUp(self) -> None:
        self._dir = tempfile.TemporaryDirectory()
        self.path = Path(self._dir.name) / "options.json"
        self.store = OptionsStore(self.path)

    def tearDown(self) -> None:
        self._dir.cleanup()

    def test_defaults_hide_hitboxes(self) -> None:
        self.assertFalse(self.store.value.show_hitboxes)
        self.assertFalse(self.store.value.telemetry)
        self.assertEqual(self.store.value.volume, 7)

    def test_volume_and_toggles_persist(self) -> None:
        self.store.set_volume(100)
        self.assertEqual(self.store.value.volume, VOLUME_MAX)
        self.store.toggle_hitboxes()
        self.store.toggle_telemetry()
        again = OptionsStore(self.path)
        self.assertEqual(again.value.volume, VOLUME_MAX)
        self.assertTrue(again.value.show_hitboxes)
        self.assertTrue(again.value.telemetry)

    def test_corrupt_options_fall_back(self) -> None:
        self.path.write_text("{roto", encoding="utf-8")
        store = OptionsStore(self.path)
        self.assertEqual(store.value, Options().clamp())


class TelemetryTest(unittest.TestCase):
    def setUp(self) -> None:
        self._dir = tempfile.TemporaryDirectory()
        self.stats = Telemetry(Path(self._dir.name) / "stats.json")

    def tearDown(self) -> None:
        self._dir.cleanup()

    def test_disabled_writes_nothing(self) -> None:
        self.stats.record(100, enabled=False)
        self.assertEqual(self.stats.today().runs, 0)

    def test_average_for_the_day(self) -> None:
        self.stats.record(100, enabled=True)
        self.stats.record(50, enabled=True)
        day = self.stats.today()
        self.assertEqual(day.runs, 2)
        self.assertEqual(day.average, 75)


class CrashLogTest(unittest.TestCase):
    def test_writes_traceback(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "crash.log"
            try:
                raise RuntimeError("boom")
            except RuntimeError as error:
                write_crash(error, path)
            text = path.read_text(encoding="utf-8")
            self.assertIn("RuntimeError", text)
            self.assertIn("boom", text)


class ProductUiTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        pygame.init()
        cls.screen = pygame.display.set_mode((WIDTH, HEIGHT))

    def test_splash_options_credits_draw(self) -> None:
        draw_splash(self.screen, 1.0)
        draw_options(self.screen, Options().clamp(), 0)
        draw_credits(self.screen)
        self.assertEqual(self.screen.get_size(), (WIDTH, HEIGHT))


if __name__ == "__main__":
    unittest.main()
