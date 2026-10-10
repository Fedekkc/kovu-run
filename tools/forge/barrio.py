"""The blocks along both sidewalks: casas chorizo, the corner shop, a PH and the street lamp."""

from __future__ import annotations

from dataclasses import dataclass

from game.palette import Tone
from tools.forge.canvas import Canvas

FACADE_W = 60
FACADE_H = 64
LAMP_W = 11
LAMP_H = 54
LAMP_HEAD = 7

_CORNICE = 9
_GROUND = FACADE_H - 3


@dataclass(frozen=True)
class Wall:
    base: Tone
    dark: Tone
    light: Tone
    shutter: Tone


PEACH_WALL = Wall(Tone.PEACH, Tone.CORAL, Tone.CREAM, Tone.LEAF)
BLUE_WALL = Wall(Tone.BLUE_LIGHT, Tone.BLUE, Tone.CREAM, Tone.BLUE_DARK)
ROSE_WALL = Wall(Tone.ROSE, Tone.MAUVE, Tone.PEACH, Tone.PLUM)
BRICK_WALL = Wall(Tone.BRICK, Tone.BRICK_DARK, Tone.BRICK_LIGHT, Tone.TRUNK)

_WEAR = ((5, 40), (12, 52), (50, 18), (55, 44), (21, 15), (38, 57), (44, 30), (7, 20), (30, 50))


def house(wall: Wall) -> Canvas:
    """A casa chorizo: tall door with transom, two French windows, parapet balusters."""
    c = Canvas(FACADE_W, FACADE_H)
    _shell(c, wall)
    _door(c, 6, 24, 11)
    _window(c, 23, 22, lit=True, wall=wall)
    _window(c, 41, 22, lit=False, wall=wall)
    for x in (23, 41):
        _railing(c, x - 1, 49, 13)
    _pot(c, 25, 47)
    _tag(c, 44, 55, Tone.NEON_PINK)
    c.rect(19, 30, 2, 2, Tone.CREAM)
    c.outline(Tone.INK)
    return c


def shop() -> Canvas:
    """The corner almacén: striped awning, a lit window full of jars and a bone-shaped neon."""
    c = Canvas(FACADE_W, FACADE_H)
    _shell(c, BRICK_WALL)
    for y in range(_CORNICE + 2, _GROUND):
        offset = 0 if (y // 3) % 2 == 0 else 3
        if y % 3 == 0:
            c.hline(1, FACADE_W - 2, y, Tone.MORTAR)
            continue
        for x in range(1 + offset, FACADE_W - 1, 6):
            c.dot(x, y, Tone.BRICK_DARK)
    _bone_sign(c, 18, 13)
    c.rect(4, 36, 38, 22, Tone.WINDOW)
    for shelf in (42, 49, 56):
        c.hline(4, 41, shelf, Tone.TRUNK)
        for index, x in enumerate(range(6, 40, 4)):
            jar = (Tone.GERANIUM, Tone.LEAF_LIGHT, Tone.SUN, Tone.BLUE_LIGHT)[(index + shelf) % 4]
            c.rect(x, shelf - 3, 2, 3, jar)
            c.dot(x, shelf - 3, Tone.CREAM)
    c.rect(46, 34, 10, 24, Tone.BARK_DARK)
    c.rect(48, 36, 6, 10, Tone.WINDOW_DIM)
    c.dot(47, 47, Tone.SUN)
    _awning(c, 2, 27, FACADE_W - 4)
    c.outline(Tone.INK)
    return c


def ph(wall: Wall) -> Canvas:
    """A two-storey PH: garage below, a balcony with plants, an AC unit and a cat upstairs."""
    c = Canvas(FACADE_W, FACADE_H)
    _shell(c, wall)
    c.hline(1, FACADE_W - 2, 36, wall.light)
    c.hline(1, FACADE_W - 2, 37, wall.dark)
    c.rect(4, 42, 30, 19, Tone.STONE)
    for y in range(43, 61, 2):
        c.hline(4, 33, y, Tone.STONE_DARK)
    c.hline(4, 33, 42, Tone.CURB)
    _door(c, 41, 40, 10)
    c.rect(10, 15, 18, 15, Tone.WINDOW)
    c.vline(19, 15, 29, Tone.CREAM)
    c.hline(10, 27, 22, Tone.CREAM)
    _cat(c, 22, 29)
    c.rect(36, 16, 18, 13, wall.shutter)
    for y in range(17, 29, 2):
        c.hline(36, 53, y, Tone.INK)
    c.rect(40, 30, 9, 5, Tone.CURB)
    c.hline(40, 48, 34, Tone.CURB_DARK)
    c.dot(44, 32, Tone.STONE_DARK)
    _railing(c, 6, 32, 26)
    _pot(c, 8, 30)
    _pot(c, 25, 30)
    _tag(c, 6, 57, Tone.NEON_CYAN)
    c.outline(Tone.INK)
    return c


def lamp() -> Canvas:
    """A farol porteño: black fluted pole and a four-paned lantern."""
    c = Canvas(LAMP_W, LAMP_H)
    x = LAMP_W // 2
    c.rect(x - 3, LAMP_H - 4, 7, 4, Tone.INK)
    c.hline(x - 2, x + 2, LAMP_H - 4, Tone.STONE_DARK)
    c.rect(x - 1, 12, 2, LAMP_H - 16, Tone.INK)
    c.vline(x - 1, 13, LAMP_H - 6, Tone.STONE_DARK)
    for y in (24, 40):
        c.hline(x - 2, x + 2, y, Tone.INK)
        c.dot(x - 2, y, Tone.STONE_DARK)
    c.hline(x - 3, x + 3, 11, Tone.INK)
    c.poly(((x - 3.5, 11), (x + 4.5, 11), (x + 3, 3), (x - 2, 3)), Tone.SUN)
    c.vline(x, 4, 10, Tone.INK)
    c.hline(x - 3, x + 3, LAMP_HEAD, Tone.CREAM)
    c.dot(x - 1, 5, Tone.CREAM)
    c.poly(((x - 4, 3), (x + 5, 3), (x + 0.5, -1)), Tone.INK)
    c.outline(Tone.INK)
    return c


def _shell(c: Canvas, wall: Wall) -> None:
    c.rect(0, _CORNICE, FACADE_W, _GROUND - _CORNICE, wall.base)
    c.vline(0, _CORNICE, _GROUND, wall.light)
    c.vline(FACADE_W - 1, _CORNICE, _GROUND, wall.dark)
    c.vline(FACADE_W - 2, _CORNICE, _GROUND, wall.dark)
    for px, py in _WEAR:
        c.dot(px, py, wall.dark)
        c.dot(px + 1, py, wall.light)
    c.rect(0, 2, FACADE_W, _CORNICE - 2, wall.base)
    for x in range(3, FACADE_W - 3, 4):
        c.rect(x, 4, 2, 4, wall.dark)
    c.hline(0, FACADE_W - 1, 2, wall.light)
    c.hline(0, FACADE_W - 1, _CORNICE, Tone.CREAM)
    c.hline(0, FACADE_W - 1, _CORNICE + 1, wall.dark)
    for x in (0, FACADE_W - 4):
        c.rect(x, 0, 4, 3, Tone.CREAM)
    c.rect(0, _GROUND, FACADE_W, 3, Tone.CURB)
    c.hline(0, FACADE_W - 1, FACADE_H - 1, Tone.CURB_DARK)


def _door(c: Canvas, x: int, y: int, width: int) -> None:
    c.rect(x - 1, y - 5, width + 2, _GROUND - y + 5, Tone.CREAM)
    c.rect(x, y - 4, width, 3, Tone.WINDOW_DIM)
    c.rect(x, y, width, _GROUND - y, Tone.BARK_LIGHT)
    half = width // 2
    c.vline(x + half, y, _GROUND - 1, Tone.TRUNK)
    for px in (x + 1, x + half + 1):
        c.rect(px, y + 2, half - 2, 8, Tone.TRUNK)
        c.rect(px, y + 13, half - 2, 10, Tone.TRUNK)
    c.dot(x + half - 1, y + 12, Tone.SUN)


def _window(c: Canvas, x: int, y: int, lit: bool, wall: Wall) -> None:
    c.rect(x - 1, y - 1, 13, 27, Tone.CREAM)
    if lit:
        c.rect(x, y, 11, 25, Tone.WINDOW)
        c.vline(x + 5, y, y + 24, Tone.CREAM)
        c.rect(x + 7, y + 12, 3, 6, Tone.WINDOW_DIM)
        c.rect(x + 7, y + 10, 3, 2, Tone.WINDOW_DIM)
        return
    c.rect(x, y, 11, 25, wall.shutter)
    for py in range(y + 1, y + 25, 2):
        c.hline(x, x + 10, py, Tone.INK)
    c.vline(x + 5, y, y + 24, Tone.INK)


def _railing(c: Canvas, x: int, y: int, width: int) -> None:
    c.hline(x, x + width - 1, y - 4, Tone.INK)
    c.hline(x, x + width - 1, y, Tone.INK)
    for px in range(x, x + width, 2):
        c.vline(px, y - 4, y, Tone.INK)


def _pot(c: Canvas, x: int, y: int) -> None:
    c.rect(x, y - 2, 3, 2, Tone.BRICK_LIGHT)
    c.rect(x - 1, y - 5, 5, 3, Tone.LEAF)
    c.dot(x, y - 6, Tone.LEAF_LIGHT)
    c.dot(x + 2, y - 5, Tone.GERANIUM)


def _tag(c: Canvas, x: int, y: int, ink: Tone) -> None:
    for step, dy in enumerate((0, -1, -2, -1, 0, 1, 0, -2)):
        c.dot(x + step, y + dy, ink)


def _awning(c: Canvas, x: int, y: int, width: int) -> None:
    for px in range(x, x + width):
        stripe = Tone.GERANIUM if (px - x) // 4 % 2 == 0 else Tone.CREAM
        c.vline(px, y, y + 5, stripe)
        if (px - x) % 4 in (1, 2):
            c.dot(px, y + 6, stripe)
    c.hline(x, x + width - 1, y, Tone.BRICK_DARK)


def _bone_sign(c: Canvas, x: int, y: int) -> None:
    c.rect(x - 2, y - 3, 28, 13, Tone.PLUM_DARK)
    for side in (0, 21):
        for row in (0, 4):
            c.ellipse(x + side + 2.5, y + row + 1.5, 2.2, 2.0, Tone.NEON_PINK)
    c.rect(x + 3, y + 1, 18, 4, Tone.NEON_PINK)
    c.hline(x + 4, x + 19, y + 2, Tone.CREAM)


def _cat(c: Canvas, x: int, y: int) -> None:
    c.rect(x, y - 3, 4, 3, Tone.INK)
    c.rect(x + 1, y - 6, 3, 3, Tone.INK)
    c.dot(x + 1, y - 7, Tone.INK)
    c.dot(x + 3, y - 7, Tone.INK)
    c.line(x, y - 1, x - 3, y + 1, Tone.INK)
