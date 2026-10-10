"""El catálogo de PNGs no dibuja nada si el archivo no está."""

from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from game.hitbox import (
    BANNER_HALF_LANE,
    BIN_W,
    CRATE_W,
    FULL_PX,
    HEDGE_W,
    HIGH_GAP_PX,
    HIGH_PX,
    HYDRANT_W,
    KOVU_H_PX,
    KOVU_SLIDE_PX,
    KOVU_W_PX,
    LOW_PX,
)
from game.player import Player
from game.render import Renderer, _kovu_slot, project
from game.settings import ART_PIXEL, DOUBLE_JUMP, HEIGHT, LANE_SPREAD, LOW, ROCKET, SUPER_JUMP, WIDTH
from game.sprites import (
    BANNER,
    BIN,
    CRATE,
    HEDGE,
    HYDRANT,
    KOVU_FLIP,
    KOVU_JUMP,
    KOVU_ROCKET,
    KOVU_RUN,
    KOVU_SLIDE,
    KOVU_SUPER,
    SLOTS,
    SpriteBook,
    default_book,
    default_catalog_path,
)


class SpriteCatalogTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        pygame.init()
        pygame.display.set_mode((32, 32))

    def test_shipped_catalog_lists_every_slot_and_its_files_exist(self) -> None:
        catalog = default_catalog_path()
        raw = json.loads(catalog.read_text(encoding="utf-8"))
        ids = [row["id"] for row in raw["sprites"]]
        self.assertEqual(sorted(ids), sorted(SLOTS))
        book = default_book()
        for row in raw["sprites"]:
            if row["file"] is None:
                self.assertIsNone(book.stamp(row["id"], 0.0))
                continue
            self.assertTrue((catalog.parent / row["file"]).is_file(), row["file"])
            self.assertIsNotNone(book.stamp(row["id"], 0.0), row["id"])

    def test_shipped_art_matches_its_hitbox(self) -> None:
        book = default_book()
        checks = (
            (KOVU_RUN, KOVU_W_PX, KOVU_H_PX),
            (KOVU_SLIDE, None, KOVU_SLIDE_PX),
            (HEDGE, HEDGE_W, LOW_PX),
            (HYDRANT, HYDRANT_W, LOW_PX),
            (BANNER, BANNER_HALF_LANE * 2.0 * LANE_SPREAD, HIGH_PX),
            (BIN, BIN_W, FULL_PX),
            (CRATE, CRATE_W, FULL_PX),
        )
        for slot, width, height in checks:
            stamp = book.stamp(slot, 0.0)
            if stamp is None:
                continue
            bounds = stamp.image.get_bounding_rect(min_alpha=1)
            if width is not None:
                self.assertLessEqual(abs(bounds.width * stamp.scale - width), ART_PIXEL * 1.5, slot)
            self.assertLessEqual(abs(bounds.height * stamp.scale - height), ART_PIXEL * 1.5, slot)
            self.assertEqual(bounds.bottom, stamp.image.get_height(), slot)

    def test_clothes_leave_the_slide_gap(self) -> None:
        stamp = default_book().stamp(BANNER, 0.0)
        if stamp is None:
            self.skipTest("sin tendedero en el catálogo")
        image = stamp.image
        posts = 4
        lowest = max(
            y
            for x in range(posts, image.get_width() - posts)
            for y in range(image.get_height())
            if image.get_at((x, y))[3] > 0
        )
        gap = (image.get_height() - lowest - 1) * stamp.scale
        self.assertLessEqual(abs(gap - HIGH_GAP_PX), ART_PIXEL * 1.5)

    def test_kovu_sprite_follows_his_state(self) -> None:
        player = Player()
        self.assertEqual(_kovu_slot(player)[0], KOVU_RUN)
        jump = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_UP)
        player.grant(SUPER_JUMP)
        player.handle_event(jump)
        player.update(0.1)
        self.assertEqual(_kovu_slot(player)[0], KOVU_SUPER)
        player.reset()
        player.grant(DOUBLE_JUMP)
        player.handle_event(jump)
        player.update(0.2)
        self.assertEqual(_kovu_slot(player)[0], KOVU_JUMP)
        player.handle_event(jump)
        player.update(0.05)
        slot, clock = _kovu_slot(player)
        self.assertEqual(slot, KOVU_FLIP)
        self.assertAlmostEqual(clock, 0.05)
        player.grant(ROCKET)
        player.update(0.0)
        self.assertEqual(_kovu_slot(player)[0], KOVU_ROCKET)

    def test_one_shot_strip_holds_its_last_frame(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            image = pygame.Surface((30, 10), pygame.SRCALPHA)
            image.fill((10, 20, 30, 255), (0, 0, 10, 10))
            image.fill((200, 10, 10, 255), (20, 0, 10, 10))
            pygame.image.save(image, root / "flip.png")
            catalog = root / "sprites.json"
            row = {"id": KOVU_FLIP, "file": "flip.png", "frames": 3, "fps": 10, "loop": False}
            catalog.write_text(json.dumps({"sprites": [row]}), encoding="utf-8")
            book = SpriteBook(catalog)
            late = book.stamp(KOVU_FLIP, 5.0)
            assert late is not None
            self.assertEqual(late.image.get_at((0, 0))[:3], (200, 10, 10))

    def test_missing_file_and_corrupt_catalog_draw_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            catalog = root / "sprites.json"
            catalog.write_text(
                json.dumps({"sprites": [{"id": "kovu_run", "file": "no-esta.png"}]}),
                encoding="utf-8",
            )
            book = SpriteBook(catalog)
            self.assertIsNone(book.stamp("kovu_run", 0.0))
            catalog.write_text("{no", encoding="utf-8")
            self.assertIsNone(SpriteBook(catalog).stamp("kovu_run", 0.0))

    def test_strip_uses_the_frame_for_the_clock(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            image = pygame.Surface((60, 20), pygame.SRCALPHA)
            image.fill((10, 20, 30, 255), (0, 0, 20, 20))
            image.fill((200, 10, 10, 255), (40, 0, 20, 20))
            pygame.image.save(image, root / "kovu.png")
            catalog = root / "sprites.json"
            catalog.write_text(
                json.dumps(
                    {
                        "sprites": [
                            {
                                "id": "kovu_run",
                                "file": "kovu.png",
                                "frames": 3,
                                "fps": 8,
                                "lift": 12,
                                "scale": 1.5,
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            book = SpriteBook(catalog)
            first = book.stamp("kovu_run", 0.0)
            later = book.stamp("kovu_run", 0.3)
            assert first is not None and later is not None
            self.assertEqual(first.image.get_at((0, 0))[:3], (10, 20, 30))
            self.assertEqual(later.image.get_at((0, 0))[:3], (200, 10, 10))
            self.assertEqual(first.lift, 12.0)
            self.assertEqual(first.scale, 1.5)
            self.assertEqual(first.image.get_size(), (20, 20))

    def test_a_catalog_png_replaces_the_procedural_obstacle(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            image = pygame.Surface((40, 40), pygame.SRCALPHA)
            image.fill((255, 0, 180, 255))
            pygame.image.save(image, root / "hedge.png")
            catalog = root / "sprites.json"
            catalog.write_text(
                json.dumps({"sprites": [{"id": HEDGE, "file": "hedge.png"}]}),
                encoding="utf-8",
            )
            screen = pygame.Surface((WIDTH, HEIGHT))
            screen.fill((0, 0, 0))
            renderer = Renderer(screen, SpriteBook(catalog))

            class Piece:
                lane = 1.0
                z = 3.0
                kind = LOW

            renderer._draw_obstacle(Piece(), 0.0, 0.0, ())
            x, y, _scale = project(1.0, 3.0)
            color = screen.get_at((int(x), int(y) - 12))
            self.assertGreater(color[0], 240)
            self.assertLess(color[1], 20)
            self.assertGreater(color[2], 160)


if __name__ == "__main__":
    unittest.main()
