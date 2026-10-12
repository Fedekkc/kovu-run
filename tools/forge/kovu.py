"""Kovu seen from behind and a little above, the way the chase camera sees him.

A greyhound reads by its pinched waist, long neck, folded rose ears and the
thin tail with an upturned tip, so every pose keeps those four.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from game.palette import Tone
from tools.forge.canvas import Canvas

WIDTH = 30
HEIGHT = 46
SLIDE_HEIGHT = 14
CENTER = 15
RUN_FRAMES = 12
BOB = (0, -1, -2, -1, 0, -1, -2, -1, 0, -1, -2, -1)
JUMP_FRAMES = 6
SLIDE_FRAMES = 4
ROCKET_FRAMES = 4
ROCKET_TAIL = 6
FLAMES = (9, 13, 11, 15)
SUPER_FRAMES = 3
SUPER_TAIL = 8
SPARKS = (
    ((3, 10), (26, 22), (5, 33)),
    ((25, 6), (3, 24), (26, 37)),
    ((4, 4), (27, 14), (3, 40)),
)

_COAT = (Tone.TAN, Tone.TAN_DARK, Tone.TAN_LIGHT)


@dataclass(frozen=True)
class Pose:
    bob: int
    hind_left: float
    hind_right: float
    front: float
    tail: float
    flap: int


def run_poses() -> list[Pose]:
    poses: list[Pose] = []
    for index in range(RUN_FRAMES):
        phase = math.tau * index / RUN_FRAMES
        poses.append(
            Pose(
                bob=BOB[index],
                hind_left=math.sin(phase),
                hind_right=math.sin(phase + 0.7),
                front=-math.sin(phase + 0.35),
                tail=1.8 * math.sin(phase + 1.2),
                flap=1 if math.cos(phase * 2.0) > 0.0 else 0,
            )
        )
    return poses


def jump_pose() -> Pose:
    """Apex pose; also the last frame of the flip strip."""
    return Pose(bob=-1, hind_left=1.25, hind_right=1.15, front=-1.0, tail=0.4, flap=1)


def jump_poses() -> list[Pose]:
    """Crouch → push → apex → fall → tuck → land prep, synced to air_phase."""
    return [
        Pose(bob=1, hind_left=0.35, hind_right=0.25, front=0.45, tail=-0.3, flap=0),
        Pose(bob=-1, hind_left=1.05, hind_right=0.95, front=-0.7, tail=0.15, flap=1),
        jump_pose(),
        Pose(bob=-1, hind_left=0.85, hind_right=0.95, front=-0.45, tail=0.55, flap=1),
        Pose(bob=0, hind_left=-0.15, hind_right=-0.05, front=0.35, tail=0.75, flap=0),
        Pose(bob=1, hind_left=0.45, hind_right=0.55, front=0.2, tail=0.05, flap=0),
    ]


def standing(pose: Pose) -> Canvas:
    c = Canvas(WIDTH, HEIGHT)
    _body(c, pose)
    c.outline(Tone.INK)
    return c


def rocket(frame: int) -> Canvas:
    """Twin side boosters; the flame hangs below the paws, hence the extra rows."""
    c = Canvas(WIDTH, HEIGHT + ROCKET_TAIL)
    swing = 1 if frame % 2 else -1
    for side in (-1, 1):
        _booster(c, CENTER + side * 9)
    _body(c, Pose(bob=0, hind_left=-1.0, hind_right=-0.8, front=-1.0, tail=1.2 * swing, flap=2))
    c.hline(CENTER - 7, CENTER + 7, 22, Tone.BLUE_DARK)
    c.hline(CENTER - 7, CENTER - 2, 21, Tone.BLUE)
    c.outline(Tone.INK)
    for index, side in enumerate((-1, 1)):
        length = FLAMES[(frame + index * 2) % len(FLAMES)]
        _flame(c, CENTER + side * 9, 33, length)
    return c


def super_jump(frame: int) -> Canvas:
    c = Canvas(WIDTH, HEIGHT + SUPER_TAIL)
    _body(c, Pose(bob=0, hind_left=1.4, hind_right=1.4, front=-1.0, tail=0.0, flap=2))
    c.outline(Tone.INK)
    for index, column in enumerate((CENTER - 7, CENTER, CENTER + 7)):
        for y in range(HEIGHT - 1, HEIGHT + SUPER_TAIL):
            lit = (y + frame + index) % 3
            if lit == 0:
                continue
            c.dot(column, y, Tone.SUN if lit == 1 else Tone.PEACH)
    for sx, sy in SPARKS[frame % len(SPARKS)]:
        _spark(c, sx, sy)
    return c


def flip() -> list[Canvas]:
    """A forward somersault seen from behind: back, belly up, head up, then the jump pose."""
    return [_curl(head_up=False), _belly_up(), _curl(head_up=True), standing(jump_pose())]


def _body(c: Canvas, pose: Pose) -> None:
    x = CENTER
    b = pose.bob
    _front_legs(c, x, b, pose.front)
    c.ellipse(x, 4.6 + b, 1.6, 1.7, Tone.TAN_LIGHT)
    c.dot(x, 3 + b, Tone.INK)
    c.shaded(x, 8.4 + b, 3.2, 3.7, *_COAT, Tone.TAN_SHINE)
    c.shaded(x, 13.6 + b, 2.6, 3.2, *_COAT)
    _ears(c, x, b, pose.flap)
    _collar(c, x, 14 + b)
    c.shaded(x, 25.5 + b, 3.9, 3.4, *_COAT)
    c.shaded(x, 20.2 + b, 6.2, 4.4, *_COAT, Tone.TAN_SHINE)
    _hind_legs(c, x, b, pose.hind_left, pose.hind_right)
    c.shaded(x, 31.4 + b, 6.4, 4.6, *_COAT, Tone.TAN_SHINE)
    for side in (-1, 1):
        c.shaded(x + side * 4.4, 34.2 + b, 3.0, 3.9, *_COAT)
    c.vline(x, 32 + b, 37 + b, Tone.TAN_DARK)
    for y in (17, 18, 28, 29):
        c.dot(x - 1, y + b, Tone.TAN_SHINE)
    _tail(c, x, b, pose.tail)


def _curl(head_up: bool) -> Canvas:
    c = Canvas(WIDTH, HEIGHT)
    x = CENTER
    paws_y = 36 if head_up else 20
    for side in (-1, 1):
        _sock(c, x + side * 3, paws_y)
        _sock(c, x + side * 6, paws_y + (1 if head_up else -1))
    c.shaded(x, 28, 8.4, 8.0, *_COAT, Tone.TAN_SHINE)
    if head_up:
        c.shaded(x, 22, 3.2, 3.2, *_COAT, Tone.TAN_SHINE)
        _collar(c, x, 25)
        for side in (-1, 1):
            c.dot(x + side * 3, 21, Tone.TAN_DARK)
            c.dot(x + side * 4, 20, Tone.TAN_DARK)
        c.line(x + 6, 31, x + 3, 35, Tone.TAN_DARK)
        c.dot(x + 2, 35, Tone.CREAM)
    else:
        c.vline(x, 23, 34, Tone.TAN_DARK)
        c.line(x, 22, x + 4, 18, Tone.TAN_DARK)
        c.dot(x + 5, 17, Tone.CREAM)
        c.dot(x + 4, 17, Tone.CREAM)
    for side in (-1, 1):
        c.shaded(x + side * 4.6, 31.0, 3.0, 3.0, *_COAT)
    c.outline(Tone.INK)
    return c


def _belly_up() -> Canvas:
    c = Canvas(WIDTH, HEIGHT)
    x = CENTER
    for side in (-1, 1):
        c.line(x + side * 5, 22, x + side * 7, 13, Tone.TAN, 2)
        _sock(c, x + side * 7, 12.6)
        c.line(x + side * 5, 32, x + side * 9, 26, Tone.TAN_DARK, 2)
        _sock(c, x + side * 9, 25.6)
    c.line(x, 19, x + 2, 13, Tone.TAN_DARK)
    c.dot(x + 2, 12, Tone.CREAM)
    c.shaded(x, 23.0, 6.4, 4.6, *_COAT, Tone.TAN_SHINE)
    for side in (-1, 1):
        c.shaded(x + side * 4.4, 21.0, 3.0, 3.6, *_COAT)
    c.shaded(x, 28.5, 3.9, 3.4, *_COAT)
    c.shaded(x, 33.4, 6.2, 4.4, *_COAT, Tone.TAN_SHINE)
    c.shaded(x, 38.4, 2.6, 3.0, *_COAT)
    _collar(c, x, 36)
    c.shaded(x, 41.2, 3.2, 3.4, *_COAT, Tone.TAN_SHINE)
    c.ellipse(x, 44.0, 1.6, 1.4, Tone.TAN_LIGHT)
    c.dot(x, 45, Tone.INK)
    for side in (-1, 1):
        c.vline(x + side * 4, 40, 43, Tone.TAN_DARK)
    c.outline(Tone.INK)
    return c


def _booster(c: Canvas, x: int) -> None:
    c.rect(x - 1, 18, 3, 13, Tone.GERANIUM)
    c.vline(x - 1, 19, 30, Tone.GERANIUM_LIGHT)
    c.vline(x + 1, 18, 30, Tone.BRICK)
    c.hline(x - 1, x + 1, 17, Tone.CREAM)
    c.dot(x, 16, Tone.CREAM)
    c.hline(x - 1, x + 1, 24, Tone.CREAM)
    c.hline(x - 1, x + 1, 31, Tone.STONE_DARK)
    c.dot(x - 2, 30, Tone.BRICK_DARK)
    c.dot(x + 2, 30, Tone.BRICK_DARK)


def _flame(c: Canvas, x: int, top: int, length: int) -> None:
    for step in range(length):
        y = top + step
        t = step / max(1, length - 1)
        if t < 0.55:
            c.hline(x - 1, x + 1, y, Tone.CORAL)
            c.dot(x, y, Tone.SUN if t < 0.3 else Tone.PEACH)
            continue
        c.dot(x, y, Tone.CORAL if t < 0.85 else Tone.GERANIUM)


def _spark(c: Canvas, x: int, y: int) -> None:
    c.dot(x, y, Tone.CREAM)
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        c.dot(x + dx, y + dy, Tone.SUN)


def sliding(frame: int = 0) -> Canvas:
    """Duck in, stretch, hold, ease out — frame drives paw reach and bob."""
    phase = frame % SLIDE_FRAMES
    stretch = (0.55, 1.0, 1.05, 0.75)[phase]
    bob = (1, 0, 0, 1)[phase]
    ear = (0, 1, 1, 0)[phase]
    c = Canvas(WIDTH, SLIDE_HEIGHT)
    x = CENTER
    front = 7.0 * stretch
    hind = 10.0 + 2.0 * stretch
    for side in (-1, 1):
        c.line(x + side * 3, 4 + bob, x + side * 6, 3 + bob, Tone.TAN_DARK, 2)
        _sock(c, x + side * front, 3 + bob)
    c.shaded(x, 4.4 + bob, 3.0, 2.7, *_COAT, Tone.TAN_SHINE)
    for side in (-1, 1):
        c.dot(x + side * 2, 6 + bob, Tone.TAN_DARK)
        c.dot(x + side * 3, 7 + bob - ear, Tone.TAN_DARK)
    _collar(c, x, 6 + bob)
    for side in (-1, 1):
        c.line(x + side * 7, 10 + bob, x + side * hind, 11 + bob, Tone.TAN, 2)
        _sock(c, x + side * (hind + 1.0), 11.4 + bob)
    c.shaded(x, 8.8 + bob, 6.6, 3.2, *_COAT, Tone.TAN_SHINE)
    for side in (-1, 1):
        c.shaded(x + side * 5.2, 10.0 + bob, 2.8, 2.3, *_COAT)
    c.line(x, 9 + bob, x, 12 + bob, Tone.TAN_DARK)
    c.dot(x, 13 + bob, Tone.CREAM)
    c.outline(Tone.INK)
    return c


def _front_legs(c: Canvas, x: int, b: int, reach: float) -> None:
    for side in (-1, 1):
        paw_y = 20.0 - reach * 6.0 + b
        paw_x = x + side * 5
        c.line(x + side * 4, 21 + b, paw_x, paw_y, Tone.TAN_DARK, 2)
        _sock(c, paw_x, paw_y)


def _ears(c: Canvas, x: int, b: int, flap: int) -> None:
    for side in (-1, 1):
        c.dot(x + side * 2, 10 + b, Tone.TAN_DARK)
        c.dot(x + side * 3, 10 + b, Tone.TAN_DARK)
        c.dot(x + side * 3, 11 + b, Tone.TAN_DARK)
        c.dot(x + side * 4, 11 + b - flap, Tone.TAN_DARK)
        c.dot(x + side * 4, 12 + b - flap, Tone.TAN_DARK)
        c.dot(x + side * 5, 12 + b - flap * 2, Tone.TAN_DARK)


def _collar(c: Canvas, x: int, y: int) -> None:
    c.hline(x - 3, x + 3, y, Tone.BLUE)
    c.hline(x - 3, x + 3, y + 1, Tone.BLUE)
    c.hline(x - 3, x - 1, y, Tone.BLUE_LIGHT)
    c.hline(x + 1, x + 3, y + 1, Tone.BLUE_DARK)


def _hind_legs(c: Canvas, x: int, b: int, left: float, right: float) -> None:
    for side, reach in ((-1, left), (1, right)):
        paw_y = 44.0 - max(0.0, -reach) * 4.0
        paw_x = x + side * (6.2 + reach * 0.9)
        c.line(x + side * 5, 37 + b, paw_x, paw_y - 1.0, Tone.TAN, 2)
        _sock(c, paw_x, paw_y - 0.4)


def _sock(c: Canvas, x: float, y: float) -> None:
    c.ellipse(x, y, 1.6, 1.1, Tone.CREAM)
    c.dot(x + 1, y, Tone.CURB_DARK)


def _tail(c: Canvas, x: int, b: int, sway: float) -> None:
    hook = 1 if sway >= 0 else -1
    points = (
        (x, 30 + b),
        (x + sway * 0.3, 36 + b),
        (x + sway, 41 + b),
        (x + sway + hook * 2, 40 + b),
    )
    for start, end in zip(points, points[1:]):
        c.line(start[0], start[1], end[0], end[1], Tone.TAN_DARK)
    tip = points[-1]
    c.dot(tip[0], tip[1], Tone.CREAM)
    c.dot(tip[0] - hook, tip[1] + 1, Tone.CREAM)
