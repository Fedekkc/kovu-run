"""Kovu in profile for the menu: a greyhound's rotary gallop in six frames.

Deep chest, tucked waist, long legs and a low streaming tail; the far legs
lag one frame behind the near ones and sit in shadow.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from game.palette import Tone
from tools.forge.canvas import Canvas

WIDTH = 66
HEIGHT = 42
FRAMES = 6

_COAT = (Tone.TAN, Tone.TAN_DARK, Tone.TAN_LIGHT)
_SHOULDER = (42.0, 24.0)
_HIP = (17.0, 20.0)
_FRONT = (8.0, 10.0)
_HIND = (9.0, 12.0)


@dataclass(frozen=True)
class Stride:
    front: tuple[float, float]
    hind: tuple[float, float]
    bob: int
    arch: int
    tail: float


STRIDES = (
    Stride(front=(55.0, 80.0), hind=(-60.0, -80.0), bob=-2, arch=0, tail=-2.0),
    Stride(front=(20.0, 5.0), hind=(-40.0, -95.0), bob=-1, arch=0, tail=-1.0),
    Stride(front=(-15.0, -25.0), hind=(5.0, -40.0), bob=0, arch=1, tail=0.0),
    Stride(front=(-45.0, -100.0), hind=(45.0, 15.0), bob=0, arch=2, tail=1.0),
    Stride(front=(-10.0, -60.0), hind=(25.0, 0.0), bob=0, arch=1, tail=0.0),
    Stride(front=(30.0, 35.0), hind=(-25.0, -30.0), bob=-1, arch=0, tail=-1.0),
)


def galloping(frame: int) -> Canvas:
    c = Canvas(WIDTH, HEIGHT)
    near = STRIDES[frame % FRAMES]
    far = STRIDES[(frame - 1) % FRAMES]
    b = near.bob
    _leg(c, _SHOULDER, b, _FRONT, far.front, Tone.TAN_DARK, 2)
    _leg(c, _HIP, b, _HIND, far.hind, Tone.TAN_DARK, 3)
    _tail(c, b, near.tail)
    _torso(c, b, near.arch)
    c.line(45, 15 + b, 51, 8 + b, Tone.TAN, 5)
    c.line(44, 13 + b, 50, 6 + b, Tone.TAN_LIGHT, 1)
    _leg(c, _HIP, b, _HIND, near.hind, Tone.TAN, 3)
    c.shaded(15.5, 19.0 + b, 4.6, 4.8, *_COAT)
    _leg(c, _SHOULDER, b, _FRONT, near.front, Tone.TAN, 2)
    c.shaded(43.0, 19.0 + b, 4.0, 4.6, *_COAT, Tone.TAN_SHINE)
    _head(c, b)
    c.line(47, 10 + b, 49, 14 + b, Tone.BLUE, 2)
    c.dot(47, 11 + b, Tone.BLUE_LIGHT)
    c.dot(49, 15 + b, Tone.SUN)
    c.outline(Tone.INK)
    return c


def _torso(c: Canvas, b: int, arch: int) -> None:
    """One silhouette from rump to chest, lit along the back and shaded under the belly."""
    a = float(arch)
    outline = (
        (9.0, 15.0), (14.0, 11.5), (22.0, 12.5 - a), (32.0, 12.0 - a * 0.5), (38.0, 11.0),
        (44.0, 12.0), (48.0, 14.0), (50.0, 18.0), (49.0, 23.0), (46.0, 26.5), (40.0, 27.0),
        (34.0, 24.0), (28.0, 21.0 - a), (22.0, 21.0 - a), (18.0, 23.0), (13.0, 24.0), (9.0, 20.0),
    )
    c.poly([(x, y + b) for x, y in outline], Tone.TAN)
    for x in range(c.width):
        column = [y for y in range(c.height) if c.is_tone(x, y, Tone.TAN)]
        if not column:
            continue
        c.dot(x, column[0], Tone.TAN_LIGHT)
        c.dot(x, column[-1], Tone.TAN_DARK)
        if len(column) > 6:
            c.dot(x, column[-2], Tone.TAN_DARK)


def _leg(
    c: Canvas,
    root: tuple[float, float],
    b: int,
    lengths: tuple[float, float],
    angles: tuple[float, float],
    shade: Tone,
    thick: int,
) -> None:
    hx, hy = root[0], root[1] + b
    upper, lower = (math.radians(angle) for angle in angles)
    knee = (hx + math.sin(upper) * lengths[0], hy + math.cos(upper) * lengths[0])
    paw = (knee[0] + math.sin(lower) * lengths[1], knee[1] + math.cos(lower) * lengths[1])
    c.line(hx, hy, knee[0], knee[1], shade, thick)
    c.line(knee[0], knee[1], paw[0], paw[1], shade, 2)
    c.rect(int(round(paw[0])) - 1, int(round(paw[1])) - 1, 3, 2, Tone.CREAM)


def _head(c: Canvas, b: int) -> None:
    c.shaded(54.0, 7.0 + b, 4.8, 3.8, *_COAT, Tone.TAN_SHINE)
    c.poly(((55, 4.5 + b), (64, 8 + b), (63.5, 10.5 + b), (55, 11 + b)), Tone.TAN)
    c.hline(57, 62, 7 + b, Tone.TAN_LIGHT)
    c.hline(56, 61, 10 + b, Tone.TAN_DARK)
    c.dot(64, 8 + b, Tone.INK)
    c.dot(63, 8 + b, Tone.INK)
    c.dot(55, 6 + b, Tone.INK)
    c.poly(((49.5, 4 + b), (52.5, 2.5 + b), (53.5, 5 + b), (50, 6.5 + b)), Tone.TAN_DARK)


def _tail(c: Canvas, b: int, sway: float) -> None:
    points = ((10.0, 15.0), (5.0, 18.0 + sway), (2.5, 24.0 + sway), (4.0, 29.0 + sway), (6.5, 30.0 + sway))
    for start, end in zip(points, points[1:]):
        c.line(start[0], start[1] + b, end[0], end[1] + b, Tone.TAN_DARK)
    tip = points[-1]
    c.dot(tip[0], tip[1] + b, Tone.CREAM)
