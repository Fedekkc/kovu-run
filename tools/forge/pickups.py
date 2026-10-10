"""Things Kovu grabs: the spinning biscuit, the power-up icons and the shop badges."""

from __future__ import annotations

import math

from game.palette import Tone
from tools.forge.canvas import Canvas

BISCUIT_W = 13
BISCUIT_H = 8
BISCUIT_FRAMES = 6
ICON_W = 12
ICON_H = 15
ROCKET_FRAMES = 4
PULSE_FRAMES = 2
BADGE = 12

_FLAMES = (3, 4, 2, 4)


def biscuit(frame: int) -> Canvas:
    """Half a turn is enough: the bone looks the same from both faces."""
    c = Canvas(BISCUIT_W, BISCUIT_H)
    turn = abs(math.cos(math.pi * frame / BISCUIT_FRAMES))
    cx = BISCUIT_W / 2
    cy = BISCUIT_H / 2
    half = max(0.6, 4.2 * turn)
    knob = max(0.7, 1.6 * turn)
    for side in (-1, 1):
        for row in (-1, 1):
            c.ellipse(cx + side * half, cy + row * 1.3, knob, 1.5, Tone.TAN_LIGHT)
    c.rect(int(cx - half), int(cy) - 1, max(1, int(round(half * 2))), 2, Tone.TAN_LIGHT)
    c.hline(int(cx - half), int(cx + half) - 1, int(cy) + 1, Tone.TAN)
    if turn > 0.4:
        c.hline(int(cx - half) + 1, int(cx), int(cy) - 1, Tone.TAN_SHINE)
        c.dot(cx - 1, cy, Tone.TAN_DARK)
        c.dot(cx + 1, cy, Tone.TAN_DARK)
    c.outline(Tone.INK)
    if frame == 0:
        c.dot(BISCUIT_W - 2, 1, Tone.CREAM)
    return c


def rocket(frame: int) -> Canvas:
    c = Canvas(ICON_W, ICON_H)
    _glow_plate(c, Tone.CORAL)
    x = ICON_W // 2
    for side in (-1, 1):
        c.poly(((x + side * 2, 7), (x + side * 5, 10), (x + side * 5, 12), (x + side * 2, 10)), Tone.GERANIUM)
    c.shaded(x - 0.5, 6.5, 2.6, 5.0, Tone.CREAM, Tone.STONE, Tone.CREAM)
    c.poly(((x - 3, 3), (x - 0.5, -0.5), (x + 2, 3)), Tone.GERANIUM)
    c.rect(x - 1, 5, 2, 2, Tone.BLUE_LIGHT)
    c.dot(x - 1, 5, Tone.CREAM)
    c.outline(Tone.INK)
    length = _FLAMES[frame % len(_FLAMES)]
    for step in range(length):
        c.hline(x - 2 + step // 2, x + 1 - step // 2, 12 + step, Tone.SUN if step < 2 else Tone.CORAL)
    return c


def spring(frame: int) -> Canvas:
    c = Canvas(ICON_W, ICON_H)
    _glow_plate(c, Tone.NEON_PINK)
    squash = frame % PULSE_FRAMES
    top = 5 + squash * 2
    c.rect(1, ICON_H - 2, ICON_W - 2, 2, Tone.STONE_DARK)
    coils = 3
    span = (ICON_H - 2 - top - 2) / coils
    for index in range(coils):
        y0 = top + 2 + index * span
        c.line(2, y0, ICON_W - 3, y0 + span / 2, Tone.SUN)
        c.line(ICON_W - 3, y0 + span / 2, 2, y0 + span, Tone.TAN_DARK)
    c.rect(1, top, ICON_W - 2, 2, Tone.GERANIUM)
    c.hline(1, ICON_W - 3, top, Tone.GERANIUM_LIGHT)
    if not squash:
        c.poly(((3, 3), (ICON_W / 2, 0), (ICON_W - 3, 3)), Tone.CREAM)
    c.outline(Tone.INK)
    return c


def chevrons(frame: int) -> Canvas:
    c = Canvas(ICON_W, ICON_H)
    _glow_plate(c, Tone.NEON_CYAN)
    rise = frame % PULSE_FRAMES
    for index, base in enumerate((Tone.NEON_CYAN, Tone.BLUE_LIGHT)):
        y = 3 + index * 6 - rise
        _chevron(c, ICON_W // 2, y, base)
    c.outline(Tone.INK)
    return c


def _glow_plate(c: Canvas, glow: Tone) -> None:
    """Solid colored disc under the icon so each power keeps its hue when tiny."""
    c.ellipse(ICON_W / 2, ICON_H / 2 + 0.5, 5.2, 6.4, glow)
    c.ellipse(ICON_W / 2, ICON_H / 2, 3.4, 4.2, Tone.CREAM)


def jump_badge() -> Canvas:
    c = Canvas(BADGE, BADGE)
    x = BADGE // 2
    c.poly(((1, 6), (x, 0), (BADGE - 1, 6)), Tone.SUN)
    c.rect(x - 2, 6, 4, 5, Tone.SUN)
    c.vline(x - 2, 6, 10, Tone.CREAM)
    c.outline(Tone.INK)
    return c


def agility_badge() -> Canvas:
    c = Canvas(BADGE, BADGE)
    c.poly(((7, 0), (2, 7), (6, 7), (4, 12), (10, 4), (6, 4)), Tone.SUN)
    c.dot(6, 2, Tone.CREAM)
    c.outline(Tone.INK)
    return c


def slide_badge() -> Canvas:
    c = Canvas(BADGE, BADGE)
    for y in (2, 5):
        c.hline(0, 4, y, Tone.BLUE_LIGHT)
    _chevron(c, 7, 4, Tone.NEON_CYAN, down=True)
    c.rect(1, 9, 10, 2, Tone.CREAM)
    c.outline(Tone.INK)
    return c


def _chevron(c: Canvas, x: int, y: int, base: Tone, down: bool = False) -> None:
    for step in range(4):
        row = y + (3 - step if down else step)
        c.hline(x - 1 - step, x - step, row, base)
        c.hline(x + step - 1, x + step, row, base)
