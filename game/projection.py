"""Del carril y la profundidad a la pantalla."""

from __future__ import annotations

from game.hitbox import PX_PER_UNIT
from game.settings import GROUND_Y, HORIZON_Y, LANE_SPREAD, NEAR, PLAYER_DRAW_Z, WIDTH

MIN_Z = 0.15
KOVU_SIZE = 1.28
JUMP_LIFT = PX_PER_UNIT


def project(lane: float, z: float) -> tuple[float, float, float]:
    """Return screen x, ground y, and scale.
    scale is about 1 at z=PLAYER_DRAW_Z and shrinks toward the horizon.
    """
    depth = z if z > MIN_Z else MIN_Z
    scale = NEAR / (depth + NEAR)
    x = WIDTH / 2 + (lane - 1) * LANE_SPREAD * scale
    y = HORIZON_Y + (GROUND_Y - HORIZON_Y) * scale
    return x, y, scale


def kovu_feet(lane_pos: float, height: float) -> tuple[float, float, float]:
    """Where Kovu's paws are on screen and the size he is drawn at."""
    x, ground_y, scale = project(lane_pos, PLAYER_DRAW_Z)
    return x, ground_y - height * JUMP_LIFT, scale * KOVU_SIZE
