"""The abuela on Kovu's tail, seen from behind like the camera sees her.

She reads by the silver bun, mauve cardigan, floral skirt and the glasses
arms peeking past her ears — still sprinting after the greyhound.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from game.palette import Tone
from tools.forge.canvas import Canvas

WIDTH = 26
HEIGHT = 34
CENTER = 13
RUN_FRAMES = 6
GRAB_FRAMES = 4

_CARDIGAN = (Tone.MAUVE, Tone.PLUM, Tone.ROSE)
_SKIRT = (Tone.VIOLET, Tone.PLUM_DARK, Tone.MAUVE)
_SILVER = (Tone.CREAM, Tone.CURB, Tone.CURB_DARK)
_KICK = 0.3


@dataclass(frozen=True)
class Stride:
    bob: int
    legs: float
    arms: float
    bun: float


def run_strides() -> list[Stride]:
    strides: list[Stride] = []
    for index in range(RUN_FRAMES):
        phase = math.tau * index / RUN_FRAMES
        swing = math.sin(phase)
        strides.append(Stride(bob=-1 if abs(swing) > 0.5 else 0, legs=swing, arms=-swing, bun=-swing * 1.2))
    return strides


def running(stride: Stride) -> Canvas:
    c = Canvas(WIDTH, HEIGHT)
    b = stride.bob
    for side in (-1, 1):
        if stride.arms * side > 0.0:
            _arm(c, side, stride.arms * side, b)
    _legs(c, side_legs=(stride.legs, -stride.legs))
    _skirt(c, b)
    _torso(c, b)
    for side in (-1, 1):
        if stride.arms * side <= 0.0:
            _arm(c, side, stride.arms * side, b)
    _head(c, b)
    _bun(c, b, stride.bun)
    c.outline(Tone.INK)
    return c


def grabbing(frame: int) -> Canvas:
    """Lunging at Kovu: both arms go up and out, the bun jostles."""
    c = Canvas(WIDTH, HEIGHT)
    t = frame / max(1, GRAB_FRAMES - 1)
    b = 1
    _legs(c, side_legs=(1.0, -0.2))
    _skirt(c, b)
    _torso(c, b)
    for side in (-1, 1):
        hand_x = CENTER + side * (8.0 + 3.0 * t)
        hand_y = 17.0 - 11.0 * t
        c.line(CENTER + side * 5, 20 + b, hand_x, hand_y, Tone.MAUVE, 2)
        c.rect(int(hand_x) - 1, int(hand_y) - 2, 2, 2, Tone.SKIN)
        c.dot(hand_x + side, hand_y - 2, Tone.SKIN_DARK)
    _head(c, b)
    _bun(c, b, 0.8 + t * 1.5)
    c.outline(Tone.INK)
    return c


def _legs(c: Canvas, side_legs: tuple[float, float]) -> None:
    planted = [(side, value) for side, value in zip((-1, 1), side_legs) if value <= _KICK]
    kicked = [(side, value) for side, value in zip((-1, 1), side_legs) if value > _KICK]
    for side, _value in planted:
        x = CENTER + side * 3
        c.line(x, 28, x + side * 0.5, 32, Tone.STONE, 2)
        c.dot(x - side, 29, Tone.STONE_LIGHT)
        c.hline(x - 1, x + 1, 33, Tone.STONE_DARK)
        c.dot(x + side, 33, Tone.INK)
    for side, value in kicked:
        x = CENTER + side * 3
        c.line(x, 28, x + side, 31, Tone.STONE, 2)
        sole_y = int(round(31 - value * 2))
        c.rect(x - 1 + side, sole_y, 3, 2, Tone.STONE_DARK)
        c.hline(x - 1 + side, x + 1 + side, sole_y + 1, Tone.INK)


def _skirt(c: Canvas, b: int) -> None:
    c.shaded(CENTER, 27.0 + b, 7.2, 3.8, *_SKIRT)
    for dx, dy in ((-3, 0), (2, 1), (-1, 1), (4, 0)):
        c.dot(CENTER + dx, 27 + b + dy, Tone.ROSE)
    c.hline(CENTER - 5, CENTER + 5, 29 + b, Tone.PLUM_DARK)


def _torso(c: Canvas, b: int) -> None:
    c.shaded(CENTER, 22.5 + b, 6.4, 4.6, *_CARDIGAN)
    c.hline(CENTER - 4, CENTER + 4, 25 + b, Tone.PLUM)
    c.dot(CENTER - 2, 22 + b, Tone.CREAM)
    c.dot(CENTER + 1, 23 + b, Tone.CREAM)
    c.shaded(CENTER, 18.8 + b, 4.6, 2.2, Tone.ROSE, Tone.MAUVE, Tone.CORAL)
    c.rect(CENTER - 1, 16 + b, 2, 1, Tone.SKIN)


def _arm(c: Canvas, side: int, swing: float, b: int) -> None:
    """swing > 0 sends the hand forward (up and behind her), < 0 back toward us."""
    shoulder_x = CENTER + side * 5
    if swing > 0.0:
        hand_x = CENTER + side * 7.0
        hand_y = 22.0 - swing * 2.0 + b
    else:
        hand_x = CENTER + side * (8.0 - swing)
        hand_y = 26.0 - swing * 1.5 + b
    c.line(shoulder_x, 20 + b, hand_x, hand_y, Tone.MAUVE, 2)
    c.dot(shoulder_x + side, 21 + b, Tone.PLUM)
    c.rect(int(round(hand_x)) - 1 + (side > 0), int(round(hand_y)), 2, 2, Tone.SKIN)


def _head(c: Canvas, b: int) -> None:
    for side in (-1, 1):
        c.rect(CENTER + side * 7 - (side < 0), 12 + b, 1, 2, Tone.SKIN)
        c.hline(CENTER + side * 6, CENTER + side * 8, 13 + b, Tone.STONE_DARK)
    c.shaded(CENTER, 12.5 + b, 6.4, 6.0, *_SILVER, Tone.CREAM)
    c.vline(CENTER, 8 + b, 17 + b, Tone.CURB_DARK)
    c.dot(CENTER - 3, 15 + b, Tone.CURB)
    c.dot(CENTER + 3, 16 + b, Tone.CURB)
    c.hline(CENTER - 4, CENTER + 4, 14 + b, Tone.CREAM)


def _bun(c: Canvas, b: int, sway: float) -> None:
    root_y = 7 + b
    cx = CENTER + int(round(sway * 0.35))
    c.shaded(cx, root_y - 0.5, 3.6, 3.2, Tone.CREAM, Tone.CURB, Tone.CURB_DARK)
    c.dot(cx - 1, root_y - 2, Tone.CREAM)
    c.dot(cx + 1, root_y - 1, Tone.CURB)
    c.hline(cx - 1, cx + 1, root_y + 1, Tone.ROSE)
    c.dot(cx, root_y + 1, Tone.SUN)
