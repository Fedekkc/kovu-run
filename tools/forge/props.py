"""Street pieces: the brick planter you jump, sidewalk trees and potted shrubs."""

from __future__ import annotations

import math

from game.hitbox import BANNER_HALF_LANE, BIN_W as BIN_PX, CRATE_W as CRATE_PX, FULL_PX, HIGH_GAP_PX, HIGH_PX, HYDRANT_W as HYDRANT_PX, LOW_PX
from game.palette import Tone
from game.settings import ART_PIXEL, LANE_SPREAD
from tools.forge.canvas import Canvas

PLANTER_W = 24
PLANTER_H = 18
TREE_W = 34
TREE_H = 60
SHRUB_W = 20
SHRUB_H = 18
HYDRANT_W = round(HYDRANT_PX / ART_PIXEL)
HYDRANT_H = round(LOW_PX / ART_PIXEL)
LINE_W = round(BANNER_HALF_LANE * 2.0 * LANE_SPREAD / ART_PIXEL)
LINE_H = round(HIGH_PX / ART_PIXEL)
LINE_GAP = round(HIGH_GAP_PX / ART_PIXEL)
BIN_W = round(BIN_PX / ART_PIXEL)
BIN_H = round(FULL_PX / ART_PIXEL)
CRATE_W = round(CRATE_PX / ART_PIXEL)
CRATE_H = round(FULL_PX / ART_PIXEL)
LINE_FRAMES = 2

_SHIRT = "shirt"
_PANTS = "pants"
_SOCK = "sock"
_TOWEL = "towel"
_LAUNDRY = (
    (5, 9, _SHIRT, Tone.BLUE_LIGHT, Tone.BLUE),
    (18, 3, _SOCK, Tone.CREAM, Tone.GERANIUM),
    (25, 9, _PANTS, Tone.BLUE_DARK, Tone.PLUM),
    (38, 8, _TOWEL, Tone.NEON_PINK, Tone.ROSE),
    (50, 3, _SOCK, Tone.SUN, Tone.CORAL),
    (57, 8, _SHIRT, Tone.GERANIUM, Tone.BRICK),
)

_GERANIUMS = ((4, 3), (11, 2), (17, 3), (8, 6), (14, 5), (19, 6))
_BARK_SPOTS = ((15, 36), (16, 40), (14, 44), (17, 47), (15, 51), (16, 33), (14, 49))


def planter() -> Canvas:
    c = Canvas(PLANTER_W, PLANTER_H)
    for cx, cy, rx, ry in ((5.5, 5.5, 4.4, 3.8), (12.0, 4.6, 4.8, 3.8), (18.2, 5.6, 4.3, 3.6)):
        c.shaded(cx, cy, rx, ry, Tone.LEAF, Tone.LEAF_DARK, Tone.LEAF_LIGHT)
    for gx, gy in _GERANIUMS:
        c.rect(gx, gy, 2, 2, Tone.GERANIUM)
        c.dot(gx, gy, Tone.GERANIUM_LIGHT)
    c.hline(2, 21, 8, Tone.SOIL)
    c.hline(1, 22, 9, Tone.CURB)
    c.hline(16, 22, 9, Tone.CURB_DARK)
    _bricks(c, 1, 22, 10, 16)
    c.outline(Tone.INK)
    return c


def tree() -> Canvas:
    c = Canvas(TREE_W, TREE_H)
    c.rect(11, 55, 12, 3, Tone.SOIL)
    c.hline(10, 23, 58, Tone.CURB_DARK)
    c.line(16, 34, 9, 25, Tone.TRUNK, 2)
    c.line(18, 33, 25, 23, Tone.TRUNK, 2)
    c.rect(14, 30, 5, 26, Tone.BARK_LIGHT)
    c.vline(18, 30, 55, Tone.BARK_DARK)
    for px, py in _BARK_SPOTS:
        c.rect(px, py, 2, 2, Tone.TRUNK)
    for cx, cy, rx, ry in ((9.0, 21.0, 7.2, 6.0), (25.0, 20.0, 7.2, 6.4), (17.0, 15.0, 13.0, 11.0), (17.0, 8.5, 9.0, 7.0)):
        c.shaded(cx, cy, rx, ry, Tone.LEAF, Tone.LEAF_DARK, Tone.LEAF_LIGHT)
    for px, py in ((7, 4), (9, 3), (6, 6), (4, 12), (3, 15), (12, 2)):
        c.dot(px + 2, py + 1, Tone.PEACH)
    for px, py in ((10, 12), (22, 10), (16, 18), (26, 17), (8, 18), (19, 6)):
        c.dot(px, py, Tone.LEAF_DARK)
    c.outline(Tone.INK)
    return c


def shrub() -> Canvas:
    c = Canvas(SHRUB_W, SHRUB_H)
    c.shaded(10.0, 5.8, 7.6, 4.8, Tone.LEAF, Tone.LEAF_DARK, Tone.LEAF_LIGHT)
    for gx, gy in ((5, 3), (10, 2), (14, 4), (8, 6)):
        c.rect(gx, gy, 2, 2, Tone.GERANIUM)
        c.dot(gx, gy, Tone.GERANIUM_LIGHT)
    c.hline(3, 16, 10, Tone.BRICK_LIGHT)
    c.poly(((4, 11), (16, 11), (14.5, 17), (5.5, 17)), Tone.BRICK)
    c.vline(6, 11, 16, Tone.BRICK_LIGHT)
    c.vline(14, 11, 16, Tone.BRICK_DARK)
    c.vline(13, 12, 16, Tone.BRICK_DARK)
    c.outline(Tone.INK)
    return c


def hydrant() -> Canvas:
    c = Canvas(HYDRANT_W, HYDRANT_H)
    x = HYDRANT_W // 2
    c.rect(x - 4, 16, 9, 2, Tone.CURB_DARK)
    c.rect(x - 3, 6, 7, 10, Tone.GERANIUM)
    c.vline(x - 3, 6, 15, Tone.GERANIUM_LIGHT)
    c.vline(x + 3, 6, 15, Tone.BRICK)
    c.vline(x + 2, 7, 15, Tone.BRICK)
    for side in (-1, 1):
        c.rect(x + side * 5 - (side < 0), 9, 2, 3, Tone.SUN)
        c.dot(x + side * 6, 10, Tone.TAN_DARK)
    c.hline(x - 4, x + 4, 6, Tone.SUN)
    c.hline(x - 3, x + 3, 13, Tone.SUN)
    c.shaded(x, 4.0, 3.6, 2.6, Tone.SUN, Tone.TAN_DARK, Tone.CREAM)
    c.rect(x, 0, 1, 2, Tone.TAN_DARK)
    c.outline(Tone.INK)
    return c


def clothesline(frame: int) -> Canvas:
    """Only the hanging clothes collide: their lowest row is the slide gap."""
    c = Canvas(LINE_W, LINE_H)
    for x in (1, LINE_W - 3):
        c.rect(x, 1, 2, LINE_H - 1, Tone.TRUNK)
        c.vline(x, 1, LINE_H - 1, Tone.BARK_LIGHT)
    for x in range(2, LINE_W - 2):
        sag = int(round(2.0 * math.sin(math.pi * (x - 2) / (LINE_W - 4))))
        c.dot(x, 2 + sag, Tone.CREAM)
    for left, width, kind, base, dark in _LAUNDRY:
        sway = (frame + left) % 2
        _garment(c, left + sway, width, kind, base, dark)
    c.outline(Tone.INK)
    return c


def container() -> Canvas:
    """A barrio dumpster with a cat peeking from under the lid."""
    c = Canvas(BIN_W, BIN_H)
    c.rect(1, 9, BIN_W - 2, BIN_H - 12, Tone.LEAF)
    c.vline(1, 9, BIN_H - 4, Tone.LEAF_LIGHT)
    c.vline(BIN_W - 2, 9, BIN_H - 4, Tone.LEAF_DARK)
    c.vline(BIN_W - 3, 10, BIN_H - 4, Tone.LEAF_DARK)
    for y in (14, 20, 26):
        c.hline(2, BIN_W - 3, y, Tone.LEAF_DARK)
    c.rect(5, 16, 9, 3, Tone.CREAM)
    c.hline(6, 12, 17, Tone.GERANIUM)
    for x in (3, BIN_W - 5):
        c.rect(x, BIN_H - 3, 2, 3, Tone.STONE_DARK)
    c.poly(((0, 8), (BIN_W, 8), (BIN_W - 2, 1), (2, 1)), Tone.STONE_DARK)
    c.hline(3, BIN_W - 4, 1, Tone.STONE)
    c.hline(2, BIN_W - 3, 2, Tone.STONE)
    c.rect(0, 8, BIN_W, 1, Tone.LEAF_DARK)
    c.outline(Tone.INK)
    cat = BIN_W // 2
    c.rect(cat - 4, 9, 9, 2, Tone.BARK_DARK)
    c.dot(cat - 4, 8, Tone.BARK_DARK)
    c.dot(cat + 4, 8, Tone.BARK_DARK)
    c.dot(cat - 2, 9, Tone.NEON_CYAN)
    c.dot(cat + 2, 9, Tone.NEON_CYAN)
    return c


def crates() -> Canvas:
    """The greengrocer's stack: three crates of tomatoes, oranges and lettuce."""
    c = Canvas(CRATE_W, CRATE_H)
    _crate(c, 0, CRATE_H - 11, CRATE_W, Tone.GERANIUM, Tone.BRICK)
    _crate(c, 1, CRATE_H - 22, CRATE_W - 2, Tone.CORAL, Tone.SUN)
    _crate(c, 3, CRATE_H - 33, CRATE_W - 7, Tone.LEAF_LIGHT, Tone.LEAF)
    c.outline(Tone.INK)
    return c


def _crate(c: Canvas, x: int, y: int, width: int, fruit: Tone, shade: Tone) -> None:
    for step in range(width // 3):
        fx = x + 1 + step * 3 + (step % 2)
        c.rect(fx, y + 1, 3, 3, fruit)
        c.dot(fx, y + 1, Tone.CREAM)
        c.dot(fx + 2, y + 3, shade)
    c.rect(x, y + 4, width, 7, Tone.BARK_LIGHT)
    c.hline(x, x + width - 1, y + 4, Tone.PEACH)
    c.hline(x, x + width - 1, y + 7, Tone.TRUNK)
    c.hline(x, x + width - 1, y + 10, Tone.TRUNK)
    for px in (x, x + width - 1):
        c.vline(px, y + 4, y + 10, Tone.TRUNK)
    c.rect(x + width // 2 - 2, y + 5, 4, 2, Tone.BARK_DARK)


def _garment(c: Canvas, left: int, width: int, kind: str, base: Tone, dark: Tone) -> None:
    top = 2 + int(round(2.0 * math.sin(math.pi * (left + width / 2 - 2) / (LINE_W - 4))))
    bottom = LINE_H - LINE_GAP - 2
    if kind == _SHIRT:
        c.rect(left - 2, top + 1, width + 4, 3, base)
        c.rect(left, top + 1, width, bottom - top, base)
        c.vline(left + width - 1, top + 2, bottom, dark)
        c.hline(left + 1, left + width - 2, top + 1, Tone.CREAM)
    elif kind == _PANTS:
        c.rect(left, top + 1, width, 4, base)
        c.rect(left, top + 5, width // 2 - 1, bottom - top - 4, base)
        c.rect(left + width // 2 + 1, top + 5, width - width // 2 - 1, bottom - top - 4, base)
        c.vline(left + width - 1, top + 1, bottom, dark)
    elif kind == _SOCK:
        c.rect(left, top + 1, width, bottom - top - 3, base)
        c.rect(left, bottom - 2, width + 2, 3, base)
        c.hline(left, left + width - 1, top + 1, dark)
    else:
        c.rect(left, top + 1, width, bottom - top - 2, base)
        for y in range(top + 2, bottom - 2, 3):
            c.hline(left, left + width - 1, y, dark)
        for x in range(left, left + width, 2):
            c.dot(x, bottom - 1, base)
    c.dot(left + width // 2, top, Tone.CREAM)


def _bricks(c: Canvas, x0: int, x1: int, y0: int, y1: int) -> None:
    for row, y in enumerate(range(y0, y1 + 1)):
        band = row % 3
        if band == 2:
            c.hline(x0, x1, y, Tone.MORTAR if y < y1 - 2 else Tone.CURB_DARK)
            continue
        lit = y == y0
        low = y >= y1 - 1
        tone_name = Tone.BRICK_LIGHT if lit else Tone.BRICK_DARK if low else Tone.BRICK
        c.hline(x0, x1, y, tone_name)
        offset = 0 if (row // 3) % 2 == 0 else 3
        for x in range(x0 + offset, x1 + 1, 6):
            c.dot(x, y, Tone.MORTAR if not low else Tone.CURB_DARK)
        c.dot(x1, y, Tone.BRICK_DARK)
