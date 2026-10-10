"""The girl on Kovu's tail, seen from behind like the camera sees her.

She reads by the red hoodie with its hood, the high ponytail that swings
against her stride and the white soles flashing on every kick.
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

_HOODIE = (Tone.GERANIUM, Tone.BRICK, Tone.GERANIUM_LIGHT)
_HOOD = (Tone.BRICK, Tone.BRICK_DARK, Tone.GERANIUM)
_HAIR = (Tone.HAIR, Tone.HAIR_DARK, Tone.HAIR_LIGHT)
_KICK = 0.3


@dataclass(frozen=True)
class Stride:
    bob: int
    legs: float
    arms: float
    tail: float


def run_strides() -> list[Stride]:
    strides: list[Stride] = []
    for index in range(RUN_FRAMES):
        phase = math.tau * index / RUN_FRAMES
        swing = math.sin(phase)
        strides.append(Stride(bob=-1 if abs(swing) > 0.5 else 0, legs=swing, arms=-swing, tail=-swing * 3.0))
    return strides


def running(stride: Stride) -> Canvas:
    c = Canvas(WIDTH, HEIGHT)
    b = stride.bob
    for side in (-1, 1):
        if stride.arms * side > 0.0:
            _arm(c, side, stride.arms * side, b)
    _legs(c, side_legs=(stride.legs, -stride.legs))
    _torso(c, b)
    for side in (-1, 1):
        if stride.arms * side <= 0.0:
            _arm(c, side, stride.arms * side, b)
    _head(c, b)
    _ponytail(c, b, stride.tail, lift=0.0)
    c.outline(Tone.INK)
    return c


def grabbing(frame: int) -> Canvas:
    """Lunging at Kovu: both arms go up and out, the ponytail flies."""
    c = Canvas(WIDTH, HEIGHT)
    t = frame / max(1, GRAB_FRAMES - 1)
    b = 1
    _legs(c, side_legs=(1.0, -0.2))
    _torso(c, b)
    for side in (-1, 1):
        hand_x = CENTER + side * (8.0 + 3.0 * t)
        hand_y = 17.0 - 11.0 * t
        c.line(CENTER + side * 5, 20 + b, hand_x, hand_y, Tone.GERANIUM, 2)
        c.rect(int(hand_x) - 1, int(hand_y) - 2, 2, 2, Tone.SKIN)
        c.dot(hand_x + side, hand_y - 2, Tone.SKIN_DARK)
    _head(c, b)
    _ponytail(c, b, 1.5, lift=t)
    c.outline(Tone.INK)
    return c


def _legs(c: Canvas, side_legs: tuple[float, float]) -> None:
    planted = [(side, value) for side, value in zip((-1, 1), side_legs) if value <= _KICK]
    kicked = [(side, value) for side, value in zip((-1, 1), side_legs) if value > _KICK]
    for side, _value in planted:
        x = CENTER + side * 3
        c.line(x, 28, x + side * 0.5, 32, Tone.BLUE_DARK, 2)
        c.dot(x - side, 29, Tone.BLUE)
        c.hline(x - 1, x + 1, 33, Tone.CREAM)
        c.dot(x + side, 33, Tone.CURB_DARK)
    for side, value in kicked:
        x = CENTER + side * 3
        c.line(x, 28, x + side, 31, Tone.BLUE_DARK, 2)
        sole_y = int(round(31 - value * 2))
        c.rect(x - 1 + side, sole_y, 3, 2, Tone.CREAM)
        c.hline(x - 1 + side, x + 1 + side, sole_y + 1, Tone.CURB_DARK)


def _torso(c: Canvas, b: int) -> None:
    c.shaded(CENTER, 24.0 + b, 6.6, 5.0, *_HOODIE)
    c.hline(CENTER - 5, CENTER + 5, 28 + b, Tone.BRICK)
    c.hline(CENTER + 1, CENTER + 4, 29 + b, Tone.BRICK_DARK)
    c.shaded(CENTER, 19.6 + b, 5.0, 2.6, *_HOOD)
    c.dot(CENTER, 21 + b, Tone.BRICK_DARK)
    c.rect(CENTER - 1, 17 + b, 2, 1, Tone.SKIN)


def _arm(c: Canvas, side: int, swing: float, b: int) -> None:
    """swing > 0 sends the hand forward (up and behind her), < 0 back toward us."""
    shoulder_x = CENTER + side * 5
    if swing > 0.0:
        hand_x = CENTER + side * 7.0
        hand_y = 22.0 - swing * 2.0 + b
    else:
        hand_x = CENTER + side * (8.0 - swing)
        hand_y = 26.0 - swing * 1.5 + b
    c.line(shoulder_x, 20 + b, hand_x, hand_y, Tone.GERANIUM, 2)
    c.dot(shoulder_x + side, 21 + b, Tone.BRICK)
    c.rect(int(round(hand_x)) - 1 + (side > 0), int(round(hand_y)), 2, 2, Tone.SKIN)


def _head(c: Canvas, b: int) -> None:
    for side in (-1, 1):
        c.rect(CENTER + side * 7 - (side < 0), 12 + b, 1, 2, Tone.SKIN)
    c.shaded(CENTER, 12.5 + b, 6.6, 6.4, *_HAIR, Tone.HAIR_LIGHT)
    c.vline(CENTER, 7 + b, 18 + b, Tone.HAIR_DARK)
    c.dot(CENTER - 3, 15 + b, Tone.HAIR_DARK)
    c.dot(CENTER + 3, 16 + b, Tone.HAIR_DARK)


def _ponytail(c: Canvas, b: int, sway: float, lift: float) -> None:
    root = (CENTER, 7.0 + b)
    mid = (CENTER + sway * 0.5, 15.0 + b - lift * 10.0)
    tip = (CENTER + sway * 1.2, 23.0 + b - lift * 21.0)
    for dx in (-2, 2):
        c.line(root[0] + dx, root[1] + 1, mid[0] + dx * 0.8, mid[1], Tone.HAIR_DARK)
        c.line(mid[0] + dx * 0.8, mid[1], tip[0] + dx * 0.4, tip[1], Tone.HAIR_DARK)
    c.line(root[0], root[1], mid[0], mid[1], Tone.HAIR, 3)
    c.line(mid[0], mid[1], tip[0], tip[1], Tone.HAIR, 2)
    c.line(mid[0] - 1, mid[1], tip[0] - 1, tip[1] - 1, Tone.HAIR_LIGHT)
    c.dot(tip[0], tip[1] + (1 if lift < 0.5 else -1), Tone.HAIR_DARK)
    c.hline(CENTER - 1, CENTER + 1, int(root[1]), Tone.SUN)
    c.dot(CENTER - 1, int(root[1]) - 1, Tone.SUN)
