"""Bakes every forged sprite into assets/ and points the catalog at it.

    py -m tools.forge [contact-sheet.png]
"""

from __future__ import annotations

import json
import os
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from game.settings import ART_PIXEL, BISCUIT, DOUBLE_JUMP, ROCKET, SUPER_JUMP
from game.sprites import (
    AGILITY_ICON,
    BANNER,
    BIN,
    CRATE,
    FACADE_BLUE,
    FACADE_PEACH,
    FACADE_PH,
    FACADE_SHOP,
    FILTER_NEAREST,
    GIRL_GRAB,
    GIRL_RUN,
    HEDGE,
    HYDRANT,
    JUMP_ICON,
    KOVU_FLIP,
    KOVU_JUMP,
    KOVU_ROCKET,
    KOVU_RUN,
    KOVU_SLIDE,
    KOVU_SUPER,
    LAMP,
    MENU_KOVU,
    SHRUB,
    SKY,
    SKY_NIGHT,
    SKYLINE_FAR,
    SKYLINE_NEAR,
    SLIDE_ICON,
    TREE,
    default_catalog_path,
)
from game.pixelfont import default_font_path
from tools.forge import barrio, font, girl, kovu, kovu_side, pickups, props, scenery
from tools.forge.canvas import Canvas, strip

RUN_FPS = 14.0
BLINK_FPS = 1.5
FLAME_FPS = 16.0
SPARK_FPS = 12.0
FLIP_FPS = 12.0
GIRL_FPS = 10.0
GALLOP_FPS = 12.0
WIND_FPS = 2.5
SPIN_FPS = 10.0
PULSE_FPS = 4.0
BISCUIT_LIFT = 3
ICON_LIFT = 2
SHEET_ZOOM = 4
SHEET_GAP = 6
SHEET_MAX_W = 80
SHEET_BACK = (34, 26, 44)


@dataclass(frozen=True)
class Bake:
    id: str
    file: str
    frames: Sequence[Canvas]
    fps: float
    lift: int = 0
    loop: bool = True


def bakes() -> list[Bake]:
    return [
        Bake(KOVU_RUN, "kovu_run.png", [kovu.standing(pose) for pose in kovu.run_poses()], RUN_FPS),
        Bake(KOVU_JUMP, "kovu_jump.png", [kovu.standing(kovu.jump_pose())], 0.0),
        Bake(KOVU_SLIDE, "kovu_slide.png", [kovu.sliding()], 0.0),
        Bake(
            KOVU_ROCKET,
            "kovu_rocket.png",
            [kovu.rocket(frame) for frame in range(kovu.ROCKET_FRAMES)],
            FLAME_FPS,
            lift=-kovu.ROCKET_TAIL,
        ),
        Bake(
            KOVU_SUPER,
            "kovu_super.png",
            [kovu.super_jump(frame) for frame in range(kovu.SUPER_FRAMES)],
            SPARK_FPS,
            lift=-kovu.SUPER_TAIL,
        ),
        Bake(KOVU_FLIP, "kovu_flip.png", kovu.flip(), FLIP_FPS, loop=False),
        Bake(
            MENU_KOVU,
            "kovu_side.png",
            [kovu_side.galloping(frame) for frame in range(kovu_side.FRAMES)],
            GALLOP_FPS,
        ),
        Bake(GIRL_RUN, "girl_run.png", [girl.running(stride) for stride in girl.run_strides()], GIRL_FPS),
        Bake(
            GIRL_GRAB,
            "girl_grab.png",
            [girl.grabbing(frame) for frame in range(girl.GRAB_FRAMES)],
            float(girl.GRAB_FRAMES),
            loop=False,
        ),
        Bake(HEDGE, "planter.png", [props.planter()], 0.0),
        Bake(HYDRANT, "hydrant.png", [props.hydrant()], 0.0),
        Bake(
            BANNER,
            "clothesline.png",
            [props.clothesline(frame) for frame in range(props.LINE_FRAMES)],
            WIND_FPS,
        ),
        Bake(BIN, "container.png", [props.container()], 0.0),
        Bake(CRATE, "crates.png", [props.crates()], 0.0),
        Bake(
            BISCUIT,
            "biscuit.png",
            [pickups.biscuit(frame) for frame in range(pickups.BISCUIT_FRAMES)],
            SPIN_FPS,
            lift=BISCUIT_LIFT,
        ),
        Bake(
            ROCKET,
            "rocket.png",
            [pickups.rocket(frame) for frame in range(pickups.ROCKET_FRAMES)],
            FLAME_FPS,
            lift=ICON_LIFT,
        ),
        Bake(
            SUPER_JUMP,
            "spring.png",
            [pickups.spring(frame) for frame in range(pickups.PULSE_FRAMES)],
            PULSE_FPS,
            lift=ICON_LIFT,
        ),
        Bake(
            DOUBLE_JUMP,
            "chevrons.png",
            [pickups.chevrons(frame) for frame in range(pickups.PULSE_FRAMES)],
            PULSE_FPS,
            lift=ICON_LIFT,
        ),
        Bake(JUMP_ICON, "badge_jump.png", [pickups.jump_badge()], 0.0),
        Bake(AGILITY_ICON, "badge_agility.png", [pickups.agility_badge()], 0.0),
        Bake(SLIDE_ICON, "badge_slide.png", [pickups.slide_badge()], 0.0),
        Bake(TREE, "tree.png", [props.tree()], 0.0),
        Bake(SHRUB, "shrub.png", [props.shrub()], 0.0),
        Bake(FACADE_PEACH, "facade_peach.png", [barrio.house(barrio.PEACH_WALL)], 0.0),
        Bake(FACADE_BLUE, "facade_blue.png", [barrio.house(barrio.BLUE_WALL)], 0.0),
        Bake(FACADE_SHOP, "facade_shop.png", [barrio.shop()], 0.0),
        Bake(FACADE_PH, "facade_ph.png", [barrio.ph(barrio.ROSE_WALL)], 0.0),
        Bake(LAMP, "lamp.png", [barrio.lamp()], 0.0),
        Bake(SKY, "sky.png", [scenery.sky()], 0.0),
        Bake(SKY_NIGHT, "sky_night.png", [scenery.night_sky()], 0.0),
        Bake(
            SKYLINE_FAR,
            "skyline_far.png",
            [scenery.skyline_far(frame) for frame in range(scenery.BLINK_FRAMES)],
            BLINK_FPS,
        ),
        Bake(
            SKYLINE_NEAR,
            "skyline_near.png",
            [scenery.skyline_near(frame) for frame in range(scenery.BLINK_FRAMES)],
            BLINK_FPS,
        ),
    ]


def write(items: Sequence[Bake], catalog: Path) -> None:
    root = catalog.parent
    for item in items:
        pygame.image.save(strip(item.frames), str(root / item.file))
    raw = json.loads(catalog.read_text(encoding="utf-8"))
    raw["filter"] = FILTER_NEAREST
    rows = raw["sprites"]
    by_id = {row["id"]: row for row in rows}
    for item in items:
        row = by_id.get(item.id)
        if row is None:
            row = {"id": item.id}
            rows.append(row)
        row.update(
            {
                "file": item.file,
                "frames": len(item.frames),
                "fps": item.fps,
                "lift": item.lift,
                "scale": ART_PIXEL,
                "loop": item.loop,
            }
        )
    catalog.write_text(_dump(raw), encoding="utf-8")


def sheet(items: Sequence[Bake], target: Path) -> None:
    small = [entry for entry in items if entry.frames[0].width <= SHEET_MAX_W]
    width = SHEET_GAP + sum(
        (entry.frames[0].width * len(entry.frames) * SHEET_ZOOM) + SHEET_GAP for entry in small
    )
    height = max(entry.frames[0].height for entry in small) * SHEET_ZOOM + SHEET_GAP * 2
    board = pygame.Surface((width, height))
    board.fill(SHEET_BACK)
    x = SHEET_GAP
    for entry in small:
        image = strip(entry.frames)
        big = pygame.transform.scale(image, (image.get_width() * SHEET_ZOOM, image.get_height() * SHEET_ZOOM))
        board.blit(big, (x, height - SHEET_GAP - big.get_height()))
        x += big.get_width() + SHEET_GAP
    target.parent.mkdir(parents=True, exist_ok=True)
    pygame.image.save(board, str(target))


def _dump(raw: dict[str, object]) -> str:
    rows = raw.get("sprites", [])
    head = {key: value for key, value in raw.items() if key != "sprites"}
    lines = ["{"]
    for key, value in head.items():
        lines.append(f"  {json.dumps(key)}: {json.dumps(value)},")
    lines.append('  "sprites": [')
    body = [f"    {json.dumps(row, ensure_ascii=False)}" for row in rows]
    lines.append(",\n".join(body))
    lines.append("  ]")
    lines.append("}")
    return "\n".join(lines) + "\n"


def write_font(target: Path) -> None:
    table = font.catalog()
    glyphs = table.pop("glyphs")
    assert isinstance(glyphs, dict)
    lines = ["{"]
    for key, value in table.items():
        lines.append(f"  {json.dumps(key)}: {json.dumps(value)},")
    lines.append('  "glyphs": {')
    body = [f"    {json.dumps(char, ensure_ascii=False)}: {json.dumps(rows)}" for char, rows in glyphs.items()]
    lines.append(",\n".join(body))
    lines.append("  }")
    lines.append("}")
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: Sequence[str]) -> None:
    pygame.init()
    pygame.display.set_mode((8, 8))
    items = bakes()
    write(items, default_catalog_path())
    write_font(default_font_path())
    if len(argv) > 1:
        sheet(items, Path(argv[1]))


if __name__ == "__main__":
    main(sys.argv)
