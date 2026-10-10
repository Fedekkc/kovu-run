"""Cajas de choque en el mismo espacio que el dibujo.

La altura está en 'unidades de salto': 1 es el salto normal del perro.
En pantalla, esa unidad mide PX_PER_UNIT píxeles a la profundidad de Kovu,
y se achica con la perspectiva igual que los sprites.
"""

from __future__ import annotations

from dataclasses import dataclass

from game.settings import (
    FULL,
    HIGH,
    LANE_SPREAD,
    LOW,
    NEAR,
    PLAYER_DRAW_Z,
    WAGON,
)

PX_PER_UNIT = 170.0
PLAYER_SCALE = NEAR / (PLAYER_DRAW_Z + NEAR)

KOVU_W_PX = 80.0
KOVU_H_PX = 176.0
KOVU_SLIDE_PX = 52.0

PLAYER_BODY = KOVU_H_PX / PX_PER_UNIT
PLAYER_SLIDE = KOVU_SLIDE_PX / PX_PER_UNIT
PLAYER_HALF_LANE = KOVU_W_PX / 2.0 / (LANE_SPREAD * PLAYER_SCALE)
PLAYER_HALF_Z = 0.62
PLAYER_Z = PLAYER_DRAW_Z - 0.3
ROCKET_FLOOR = 1.25

LOW_PX = 70.0
HIGH_PX = 160.0
HIGH_GAP_PX = 96.0
FULL_PX = 130.0
HEDGE_W = 96.0
HYDRANT_W = 52.0
BANNER_HALF_LANE = 0.36
BIN_W = 76.0
CRATE_W = 100.0
OBSTACLE_HALF_Z = 0.36
WAGON_PX = 168.0
WAGON_W = 340.0
WAGON_HALF_Z = 4.2
WAGON_LAND = 0.14

PICKUP_HALF_LANE = 0.14
PICKUP_HALF_Z = 0.42
PICKUP_TOP = 1.15


@dataclass(frozen=True)
class Box:
    lane: float
    half_lane: float
    z: float
    half_z: float
    bottom: float
    top: float


def px_to_units(px: float) -> float:
    return px * PLAYER_SCALE / PX_PER_UNIT


def units_to_px(units: float, scale: float) -> float:
    if PLAYER_SCALE <= 0.0:
        return 0.0
    return units * PX_PER_UNIT * scale / PLAYER_SCALE


def variant_bit(lane: float, z: float, distance: float) -> int:
    mark = int(lane) + int(round(z + distance))
    return abs(mark) & 1


def overlaps(a: Box, b: Box) -> bool:
    if abs(a.lane - b.lane) >= a.half_lane + b.half_lane:
        return False
    if abs(a.z - b.z) >= a.half_z + b.half_z:
        return False
    return a.bottom < b.top and b.bottom < a.top


def overlaps_swept(body: Box, item: Box, previous_z: float) -> bool:
    travel = abs(item.z - previous_z)
    swept = Box(
        item.lane,
        item.half_lane,
        (item.z + previous_z) * 0.5,
        item.half_z + travel * 0.5,
        item.bottom,
        item.top,
    )
    return overlaps(body, swept)


def player_hitbox(player: object) -> Box:
    height = float(getattr(player, "height"))
    sliding = bool(getattr(player, "sliding"))
    rocket = float(getattr(player, "rocket_time"))
    floor = float(getattr(player, "floor", 0.0))
    if rocket > 0.0:
        feet = max(height, ROCKET_FLOOR)
        top = feet + PLAYER_BODY
    elif sliding:
        feet = floor
        top = floor + PLAYER_SLIDE
    else:
        feet = height
        top = height + PLAYER_BODY
    return Box(
        float(getattr(player, "lane_pos")),
        PLAYER_HALF_LANE,
        PLAYER_Z,
        PLAYER_HALF_Z,
        feet,
        top,
    )


def obstacle_box(kind: str, lane: float, z: float, distance: float) -> Box:
    bit = variant_bit(lane, z, distance)
    half_z = OBSTACLE_HALF_Z
    if kind == LOW:
        width = HYDRANT_W if bit else HEDGE_W
        bottom = 0.0
        top = px_to_units(LOW_PX)
        half_lane = width * 0.5 / LANE_SPREAD
    elif kind == HIGH:
        bottom = px_to_units(HIGH_GAP_PX)
        top = px_to_units(HIGH_PX)
        half_lane = BANNER_HALF_LANE
    elif kind == FULL:
        width = CRATE_W if bit else BIN_W
        bottom = 0.0
        top = px_to_units(FULL_PX)
        half_lane = width * 0.5 / LANE_SPREAD
    elif kind == WAGON:
        bottom = 0.0
        top = px_to_units(WAGON_PX)
        half_lane = WAGON_W * 0.5 / LANE_SPREAD
        half_z = WAGON_HALF_Z
    else:
        bottom = 0.0
        top = px_to_units(FULL_PX)
        half_lane = BIN_W * 0.5 / LANE_SPREAD
    return Box(float(lane), half_lane, float(z), half_z, bottom, top)


def on_deck(body: Box, deck: Box) -> bool:
    """Pies sobre el techo del vagón (no embistiendo el frente)."""
    if abs(body.lane - deck.lane) >= body.half_lane + deck.half_lane:
        return False
    if abs(body.z - deck.z) >= body.half_z + deck.half_z:
        return False
    return body.bottom >= deck.top - WAGON_LAND


def pickup_box(lane: float, z: float, span: float = 1.0) -> Box:
    scale = max(1.0, span)
    return Box(
        float(lane),
        PICKUP_HALF_LANE * scale,
        float(z),
        PICKUP_HALF_Z * scale,
        0.0,
        PICKUP_TOP,
    )
