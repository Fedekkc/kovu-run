"""Sunset sky and two layers of barrio rooftops for the horizon."""

from __future__ import annotations

from game.palette import Tone
from tools.forge.canvas import Canvas

SKY_W = 320
SKY_H = 62
FAR_W = 352
FAR_H = 46
NEAR_W = 384
NEAR_H = 32
BLINK_FRAMES = 2

_SKY_STOPS = (Tone.SKY_TOP, Tone.SKY_HIGH, Tone.SKY_MID, Tone.SKY_LOW, Tone.SKY_GLOW, Tone.PEACH)
_STARS = (
    (12, 3), (41, 9), (63, 2), (88, 6), (117, 11), (139, 4), (171, 8), (196, 2),
    (222, 10), (248, 5), (271, 12), (299, 3), (25, 15), (104, 16), (186, 14), (309, 15),
    (54, 12), (232, 16), (152, 13), (281, 7),
)
_BRIGHT = ((63, 2), (196, 2), (117, 11), (299, 3))
_CLOUDS = (
    (14, 27, 58), (84, 31, 40), (196, 25, 72), (262, 33, 46), (36, 40, 34), (230, 42, 52), (120, 21, 30),
)
_NIGHT_STOPS = (Tone.INK, Tone.SKY_TOP, Tone.SKY_TOP, Tone.SKY_HIGH, Tone.PLUM, Tone.MAUVE)
_NIGHT_STARS = (
    (7, 20), (33, 24), (71, 18), (95, 27), (128, 22), (163, 19), (209, 23), (240, 28),
    (262, 21), (290, 25), (315, 22), (147, 29), (80, 33), (184, 31), (20, 30), (300, 33),
)
_NIGHT_BRIGHT = ((33, 24), (163, 19), (262, 21))
_MOON = (254, 13, 6)
_NIGHT_CLOUDS = ((30, 38, 46), (180, 34, 60), (110, 44, 28), (268, 42, 40))
_SUN_X = 160
_SUN_Y = 60
_SUN_R = 17
_SUN_CUTS = (50, 54, 57, 59, 61)

_FAR_TOWERS = (
    (4, 14, 30), (20, 10, 38), (32, 16, 26), (52, 12, 42), (66, 18, 31), (88, 10, 36),
    (100, 14, 24), (118, 12, 33), (134, 8, 27), (210, 12, 29), (224, 16, 40), (242, 10, 34),
    (254, 18, 28), (274, 12, 44), (288, 16, 30), (306, 10, 37), (318, 14, 26), (334, 14, 33),
)
_DOME = (148, 20)
_MAST = (278, 44)

_NEAR_HOUSES = (
    (0, 22, 16), (22, 18, 20), (40, 26, 14), (66, 20, 22), (86, 24, 17), (110, 18, 19),
    (128, 22, 15), (150, 18, 21), (216, 20, 18), (236, 24, 15), (260, 18, 21), (278, 26, 16),
    (304, 20, 20), (324, 22, 14), (346, 18, 19), (364, 20, 16),
)
_TANKS = ((8, 16), (72, 22), (118, 19), (244, 15), (312, 20), (370, 16))
_ANTENNAS = ((30, 20), (96, 17), (160, 21), (226, 18), (290, 16), (354, 19))
_POLES = (46, 140, 250, 336)
_SIGNS = ((88, Tone.NEON_PINK, Tone.ROSE), (262, Tone.NEON_CYAN, Tone.BLUE_DARK))


def sky() -> Canvas:
    c = Canvas(SKY_W, SKY_H)
    c.gradient(0, SKY_H, _SKY_STOPS)
    for x, y in _STARS:
        c.dot(x, y, Tone.CREAM)
    for x, y in _BRIGHT:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            c.dot(x + dx, y + dy, Tone.SUN)
    for x, y, length in _CLOUDS:
        _streak(c, x, y, length)
    _sun(c)
    return c


def night_sky() -> Canvas:
    c = Canvas(SKY_W, SKY_H)
    c.gradient(0, SKY_H, _NIGHT_STOPS)
    for x, y in _STARS + _NIGHT_STARS:
        c.dot(x, y, Tone.CREAM)
    for x, y in _BRIGHT + _NIGHT_BRIGHT:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            c.dot(x + dx, y + dy, Tone.WINDOW_DIM)
    mx, my, r = _MOON
    c.ellipse(mx, my, r, r, Tone.CREAM)
    c.ellipse(mx + 3, my - 2, r - 1, r - 1, Tone.SKY_TOP)
    c.dot(mx - 4, my + 2, Tone.WINDOW_DIM)
    for x, y, length in _NIGHT_CLOUDS:
        c.hline(x, x + length, y, Tone.PLUM)
        c.hline(x + 3, x + length - 4, y + 1, Tone.VIOLET)
    return c


def skyline_far(frame: int) -> Canvas:
    c = Canvas(FAR_W, FAR_H)
    base = FAR_H - 1
    for x, w, h in _FAR_TOWERS:
        c.rect(x, base - h, w, h + 1, Tone.VIOLET)
        c.vline(x, base - h, base, Tone.MAUVE)
        c.hline(x, x + w - 1, base - h, Tone.MAUVE)
        for wy in range(base - h + 3, base - 1, 4):
            for wx in range(x + 2, x + w - 2, 3):
                if (wx * 7 + wy * 3) % 5 == 0:
                    c.dot(wx, wy, Tone.WINDOW_DIM)
    dome_x, dome_h = _DOME
    c.rect(dome_x - 5, base - dome_h + 6, 11, dome_h - 5, Tone.VIOLET)
    c.ellipse(dome_x + 0.5, base - dome_h + 6, 6.0, 5.0, Tone.VIOLET)
    c.vline(dome_x, base - dome_h - 3, base - dome_h, Tone.MAUVE)
    c.hline(dome_x - 1, dome_x + 1, base - dome_h - 2, Tone.MAUVE)
    mast_x, mast_h = _MAST
    c.vline(mast_x, base - mast_h - 8, base - mast_h, Tone.MAUVE)
    blink = Tone.NEON_PINK if frame == 0 else Tone.PLUM
    c.dot(mast_x, base - mast_h - 9, blink)
    return c


def skyline_near(frame: int) -> Canvas:
    c = Canvas(NEAR_W, NEAR_H)
    base = NEAR_H - 1
    for x, w, h in _NEAR_HOUSES:
        top = base - h
        c.rect(x, top, w, h + 1, Tone.PLUM_DARK)
        c.hline(x, x + w - 1, top, Tone.PLUM)
        c.dot(x, top - 1, Tone.PLUM)
        c.dot(x + w - 1, top - 1, Tone.PLUM)
        for wx in range(x + 3, x + w - 3, 5):
            lit = (wx * 5 + h) % 3 != 0
            c.rect(wx, top + 4, 2, 3, Tone.WINDOW if lit else Tone.PLUM)
            if h > 17:
                c.rect(wx, top + 10, 2, 3, Tone.WINDOW_DIM if lit else Tone.PLUM)
    for x, y in _TANKS:
        _tank(c, x, base - y)
    for x, y in _ANTENNAS:
        _antenna(c, x, base - y)
    for x, glow, dim in _SIGNS:
        light = glow if frame == 0 else dim
        c.rect(x, base - 12, 12, 1, light)
        c.rect(x, base - 7, 12, 1, light)
        c.vline(x, base - 12, base - 7, light)
        c.vline(x + 11, base - 12, base - 7, light)
        c.hline(x + 3, x + 8, base - 10, light)
    for left, right in zip(_POLES, _POLES[1:]):
        _cable(c, left, right, base - 22)
    for x in _POLES:
        c.vline(x, base - 24, base, Tone.INK)
    return c


def _streak(c: Canvas, x: int, y: int, length: int) -> None:
    c.hline(x + 3, x + length - 3, y - 1, Tone.MAUVE)
    c.hline(x, x + length, y, Tone.ROSE)
    c.hline(x + 2, x + length - 2, y + 1, Tone.CORAL)
    c.hline(x + 6, x + length - 8, y + 2, Tone.PEACH)


def _sun(c: Canvas) -> None:
    for y in range(_SUN_Y - _SUN_R, SKY_H):
        if y in _SUN_CUTS:
            continue
        half = (_SUN_R * _SUN_R - (y - _SUN_Y) ** 2) ** 0.5 if abs(y - _SUN_Y) <= _SUN_R else 0.0
        if half <= 0.0:
            continue
        name = Tone.CREAM if y < _SUN_Y - 11 else Tone.SUN if y < _SUN_Y - 4 else Tone.PEACH
        c.hline(int(_SUN_X - half), int(_SUN_X + half), y, name)


def _tank(c: Canvas, x: int, y: int) -> None:
    c.vline(x + 1, y + 4, y + 7, Tone.INK)
    c.vline(x + 5, y + 4, y + 7, Tone.INK)
    c.rect(x, y, 7, 4, Tone.PLUM_DARK)
    c.hline(x, x + 6, y, Tone.PLUM)
    c.dot(x + 1, y + 1, Tone.VIOLET)


def _antenna(c: Canvas, x: int, y: int) -> None:
    c.vline(x, y, y + 6, Tone.INK)
    c.hline(x - 3, x + 3, y + 1, Tone.INK)
    c.hline(x - 2, x + 2, y + 3, Tone.INK)


def _cable(c: Canvas, left: int, right: int, y: int) -> None:
    span = right - left
    for step in range(span + 1):
        t = step / span
        sag = 4.0 * t * (1.0 - t) * 4.0
        c.dot(left + step, y + sag, Tone.INK)
