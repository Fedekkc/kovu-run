"""2.5D pygame view of the park road, Kovu, and the abuela chasing him."""

from __future__ import annotations

import math
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from functools import partial
from typing import Protocol

import pygame

from game.hitbox import (
    PX_PER_UNIT,
    HIGH_GAP_PX,
    HIGH_PX,
    FULL_PX,
    LOW_PX,
    WAGON_HALF_Z,
    WAGON_PX,
    WAGON_W,
    obstacle_box,
    overlaps,
    pickup_box,
    player_hitbox,
    units_to_px,
    variant_bit,
)
from game.settings import (
    BISCUIT,
    DESPAWN_Z,
    DOUBLE_JUMP,
    FULL,
    GROUND_Y,
    HEIGHT,
    HIGH,
    HORIZON_Y,
    LANE_SPREAD,
    LOW,
    WAGON,
    NEAR,
    ART_PIXEL,
    PIXEL,
    ROCKET,
    SUPER_JUMP,
    PLAYER_DRAW_Z,
    WIDTH,
)
from game.cycle import Mood, mood_at
from game.fx import POWER_GLOW
from game.projection import JUMP_LIFT, KOVU_SIZE, MIN_Z, project
from game.palette import Tone, tone
from game.sprites import (
    FACADE_BLUE,
    FACADE_PEACH,
    FACADE_PH,
    FACADE_SHOP,
    LAMP,
    SKY,
    SKY_NIGHT,
    SKYLINE_FAR,
    SKYLINE_NEAR,
    BANNER,
    BIN,
    CRATE,
    WAGON as WAGON_SLOT,
    GIRL_GRAB,
    GIRL_RUN,
    HEDGE,
    HYDRANT,
    KOVU_JUMP,
    KOVU_FLIP,
    KOVU_ROCKET,
    KOVU_SUPER,
    KOVU_RUN,
    KOVU_SLIDE,
    SHRUB,
    TREE,
    SpriteBook,
    blit_feet,
    default_book,
)

_MIN_Z = MIN_Z
_FAR_DRAW_Z = 140.0
_OUTLINE = 2

_SKY_TOP = (92, 176, 245)
_SKY_HORIZON = (255, 206, 150)
_SUN_GLOW = (255, 186, 96, 55)
_SUN_CORE = (255, 214, 120)
_SUN_HOT = (255, 244, 214)
_CLOUD = (255, 250, 246)
_CLOUD_SOFT = (255, 236, 214)
_COAT = (214, 164, 96)
_COAT_FAR = (176, 126, 64)
_COAT_SHINE = (228, 186, 124)
_SADDLE = (148, 96, 48)
_BELLY = (245, 228, 204)
_SNOUT = (224, 176, 112)
_INNER_EAR = (204, 150, 118)
_NOSE = (54, 36, 30)
_PAW = (128, 82, 48)
_COLLAR = (64, 140, 210)
_TAG = (236, 206, 120)
_EYE = (48, 32, 26)
_HIGHLIGHT = (255, 248, 236)

_LEAF = (64, 142, 62)
_LEAF_DARK = (40, 108, 48)
_LEAF_LIGHT = (108, 176, 78)
_TRUNK = (118, 78, 44)
_HYDRANT = (204, 42, 40)
_HYDRANT_DARK = (156, 28, 30)
_CAP = (214, 218, 220)
_BOLT = (72, 76, 80)
_WOOD = (150, 98, 52)
_CORAL = (224, 96, 88)
_TEAL = (36, 148, 146)
_BIN = (32, 140, 138)
_BIN_DARK = (20, 102, 104)
_LID = (18, 118, 116)
_CRATE = (176, 132, 74)
_CRATE_DARK = (132, 92, 48)

_BISCUIT = (232, 176, 74)
_BISCUIT_LIGHT = (248, 214, 150)
_BISCUIT_HOLE = (156, 104, 36)

_SKIN = (236, 190, 158)
_HAIR = (236, 228, 214)
_HAIR_DARK = (168, 152, 142)
_HAIR_LIGHT = (255, 248, 236)
_CARDIGAN = (138, 74, 120)
_CARDIGAN_DARK = (92, 48, 96)
_CARDIGAN_LIGHT = (200, 96, 122)
_SKIRT = (92, 50, 104)
_SHOE = (62, 52, 80)
_SOLE = (30, 26, 40)
_BROW = (120, 96, 88)
_IRIS = (78, 48, 32)
_MOUTH = (168, 84, 78)
_SCARF = (232, 132, 102)
_GLASS = (46, 40, 64)
_BUTTON = (255, 245, 220)

_SHADOW = (16, 24, 14, 72)

_ROAD_LEFT = -0.55
_ROAD_RIGHT = 2.55
_VERGE_LEFT = -1.08
_VERGE_RIGHT = 3.08
_SEP_LEFT = 0.5
_SEP_RIGHT = 1.5
_OUTER_LEFT = -7.0
_OUTER_RIGHT = 9.0
_CURB_W = 0.09
_COBBLE_PERIOD = 0.85
_TILE_PERIOD = 1.4
_CURB_PERIOD = 1.7
_STRIPE_NEAR = 0.15
_STRIPE_FAR = 130.0
_FAR_SHIFT = 6 * ART_PIXEL
_NEAR_SHIFT = 12 * ART_PIXEL
_HAZE_ALPHA = 54
_DASH_PERIOD = 4.2
_DASH_LENGTH = 1.85
_DASH_HALF = 0.02
_TREE_SPAN = 22.0
_SHRUB_SPAN = 15.0
_TREE_LANES = (-1.72, 3.72)
_SHRUB_LANES = (-1.18, 3.18)
_TREE = 0
_SHRUB = 1
_FACADE = 2
_LAMP = 3
_FACADE_SPAN = 4.5
_FACADE_LANES = (-2.35, 4.35)
_LAMP_SPAN = 18.0
_LAMP_LANES = (-1.45, 3.45)
_PROP_SLOTS = {_TREE: TREE, _SHRUB: SHRUB, _LAMP: LAMP}
_FACADES = (FACADE_PEACH, FACADE_BLUE, FACADE_SHOP, FACADE_PH)
_HASH_SPOT = 73856093
_HASH_LANE = 19349663
_FACADE_FALLBACK = (240.0, 256.0)
_LAMP_HEAD_AT = 0.87
_LAMP_FALLBACK_H = 200.0
_NIGHT_TINT = (124, 128, 204)
_STORM_TINT = (78, 88, 150)
_WHITE = (255, 255, 255)
_HALO_R = 92.0
_HALO_SIZE = 64
_HALO_GLOW = (255, 190, 104)
_POOL_SQUASH = 0.3
_RAIN_DROPS = 150
_RAIN_FALL = 1100.0
_RAIN_SLANT = 0.28
_RAIN_LEN = 22.0
_FLASH_EVERY = 9.0
_FLASH_TIME = 0.12
_FLASH_FROM = 0.9
_FLASH = (110, 110, 130)
_HAZE_NIGHT = 0.8
_FLASH_PEAK = 170
_AURA_RATE = 7.0
_AURA_PICKUP = 30.0
_AURA_BODY = 54.0
_AURA_RING = 0.58
_AURA_SOFT = 96
_AURA_MIN_PICKUP = 14
_AURA_MIN_BODY = 24
_AURA_PASSES = 1
_AS_HEDGE = 0
_AS_HYDRANT = 1
_BIN_KIND = 0
_CRATE_KIND = 1

_KOVU_SIZE = KOVU_SIZE
_JUMP_LIFT = JUMP_LIFT
_SLIDE_SQUASH = 0.55
_SLIDE_STRETCH = 1.42
_DEPTH = 0.36
_SHEAR = 0.05
_STRETCH_REACH = 0.85
_GAIT = 13.0
_LOW_H = LOW_PX
_HIGH_H = HIGH_PX
_HIGH_GAP = HIGH_GAP_PX
_FULL_H = FULL_PX
_WAGON_H = WAGON_PX
_WAGON_ROOF = (176, 180, 186)
_WAGON_ROOF_FAR = (142, 146, 154)
_WAGON_SIDE = (92, 96, 108)
_WAGON_FACE = (224, 176, 72)
_WAGON_FACE_DARK = (176, 128, 48)
_WAGON_WINDOW = (42, 78, 128)
_WAGON_GLASS = (120, 190, 220)
_WAGON_LIGHT = (255, 148, 48)
_WAGON_BUMPER = (54, 58, 68)
_WAGON_SEAM = (110, 114, 122)
_BISCUIT_W = 36.0
_COVER_AT = 0.45
_REACH_AT = 0.9
_GIRL_HEAD_Y = 640.0
_GIRL_FEET = 84.0
_GRAB_FROM = 0.4
_SPIN_SPREAD = 0.05
_SUN_X = 188
_SUN_Y = HORIZON_Y - 20


class _ObstacleView(Protocol):
    lane: float
    z: float
    kind: str


class _BiscuitView(Protocol):
    lane: float
    z: float
    taken: bool
    height: float


class _BonusView(Protocol):
    lane: float
    z: float
    kind: str
    taken: bool


class _WorldView(Protocol):
    obstacles: Sequence[_ObstacleView]
    biscuits: Sequence[_BiscuitView]
    bonuses: Sequence[_BonusView]
    game_over: bool
    catch_timer: float
    speed: float
    distance: float
    chase_pressure: float
    mutator: str


class _PlayerView(Protocol):
    lane_pos: float
    height: float
    jumping: bool
    sliding: bool
    run_time: float
    rocket_time: float
    powered: bool
    super_armed: bool
    extra_jumps: int
    flipping: bool
    flip_time: float
    air_phase: float
    slide_phase: float


class _EffectsView(Protocol):
    flash: float
    offset: tuple[int, int]

    def draw(self, screen: pygame.Surface, time: float) -> None: ...


@dataclass(frozen=True)
class _Pose:
    x: float
    y: float
    g: float
    ease: float
    stride: float


def _mix(start: tuple[int, int, int], end: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    return (
        int(start[0] + (end[0] - start[0]) * t),
        int(start[1] + (end[1] - start[1]) * t),
        int(start[2] + (end[2] - start[2]) * t),
    )


def _dark(color: tuple[int, int, int], amount: int = 68) -> tuple[int, int, int]:
    return (
        max(0, color[0] - amount),
        max(0, color[1] - amount),
        max(0, color[2] - amount),
    )


def _ints(points: Sequence[tuple[float, float]]) -> list[tuple[int, int]]:
    return [(int(point[0]), int(point[1])) for point in points]


def _in_view(z: float) -> bool:
    return z >= DESPAWN_Z and z <= _FAR_DRAW_Z


def _variant(lane: float, z: float, distance: float) -> int:
    return variant_bit(lane, z, distance)


def _kovu_slot(player: _PlayerView) -> tuple[str, float]:
    if player.rocket_time > 0.0:
        return KOVU_ROCKET, player.run_time
    if player.sliding and not player.jumping:
        return KOVU_SLIDE, player.slide_phase
    if player.flipping:
        return KOVU_FLIP, player.flip_time
    if player.powered:
        return KOVU_SUPER, player.run_time
    if player.jumping:
        return KOVU_JUMP, player.air_phase
    return KOVU_RUN, player.run_time


def _obstacle_slot(kind: str, variant: int) -> str:
    if kind == LOW:
        return HYDRANT if variant == _AS_HYDRANT else HEDGE
    if kind == HIGH:
        return BANNER
    if kind == WAGON:
        return WAGON_SLOT
    if variant == _CRATE_KIND:
        return CRATE
    return BIN


def _bonus_slot(kind: str) -> str:
    if kind == ROCKET:
        return ROCKET
    if kind == SUPER_JUMP:
        return SUPER_JUMP
    return DOUBLE_JUMP


def _armed_power(player: _PlayerView) -> str | None:
    """Which power glow Kovu should wear right now, if any."""
    if player.rocket_time > 0.0:
        return ROCKET
    if player.powered or player.super_armed:
        return SUPER_JUMP
    if player.flipping or player.extra_jumps > 0:
        return DOUBLE_JUMP
    return None


class Renderer:
    def __init__(self, screen: pygame.Surface, sprites: SpriteBook | None = None) -> None:
        self._screen = screen
        self._sprites = default_book() if sprites is None else sprites
        self._sky = self._make_sky()
        self._haze = self._make_haze()
        self._small = pygame.Surface((WIDTH // PIXEL, HEIGHT // PIXEL))
        self._halo = self._make_halo()
        self._soft = self._make_soft()
        self._scaled: dict[str, pygame.Surface] = {}
        self._lamps: list[tuple[float, float, float]] = []
        self.show_hitboxes = False
        self.pixelate = True

    def attach(self, screen: pygame.Surface) -> None:
        self._screen = screen

    def _blit_slot(
        self,
        slot: str,
        x: float,
        y: float,
        scale: float,
        time: float,
        shadow: bool = True,
    ) -> bool:
        stamp = self._sprites.stamp(slot, time)
        if stamp is None:
            return False
        draw = scale * stamp.scale
        if shadow:
            width = stamp.image.get_width() * draw
            self._shadow(x, y, width * 0.28, max(3.0, 7.0 * scale))
        blit_feet(self._screen, stamp.image, x, y - stamp.lift * draw, draw, stamp.smooth)
        return True

    def draw(
        self,
        world: _WorldView,
        player: _PlayerView,
        time: float,
        effects: _EffectsView | None = None,
    ) -> None:
        mood = mood_at(world.distance)
        self._lamps.clear()
        self._draw_sky(time, mood.night)
        self._draw_skyline(player.lane_pos, time)
        self._draw_grass(world.distance)
        self._draw_road(world.distance)
        self._haze.set_alpha(int(255 * (1.0 - mood.night * _HAZE_NIGHT)))
        self._screen.blit(self._haze, (0, HORIZON_Y - 12))
        self._draw_actors(world, time)
        self._draw_chase(world, player, time)
        if effects is not None:
            effects.draw(self._screen, time)
        if self.pixelate:
            pygame.transform.scale(self._screen, self._small.get_size(), self._small)
            self._grade(self._small, mood, time)
            pygame.transform.scale(self._small, (WIDTH, HEIGHT), self._screen)
        else:
            self._grade(self._screen, mood, time)
        if effects is not None:
            self._jolt(effects)
        if self.show_hitboxes:
            self._draw_hitboxes(world, player)

    def _jolt(self, effects: _EffectsView) -> None:
        if effects.flash > 0.0:
            level = int(_FLASH_PEAK * effects.flash)
            self._screen.fill((level, level, level), special_flags=pygame.BLEND_ADD)
        dx, dy = effects.offset
        if dx or dy:
            self._screen.scroll(dx, dy)

    def _grade(self, target: pygame.Surface, mood: Mood, time: float) -> None:
        """Night and storm are a tint over the finished frame plus the lights that beat it."""
        if mood.night <= 0.0 and mood.rain <= 0.0:
            return
        k = target.get_width() / WIDTH
        tint = _mix(_mix(_WHITE, _NIGHT_TINT, mood.night), _STORM_TINT, mood.rain)
        target.fill(tint, special_flags=pygame.BLEND_MULT)
        self._glow(target, k, mood)
        self._rain(target, k, mood.rain, time)

    def _glow(self, target: pygame.Surface, k: float, mood: Mood) -> None:
        if mood.night <= 0.0:
            return
        level = int(255 * mood.night)
        for x, head_y, foot_y, scale in self._lamp_spots():
            size = max(2, int(_HALO_R * 2.0 * scale * k))
            halo = pygame.transform.scale(self._halo, (size, size))
            pool_h = max(1, int(size * _POOL_SQUASH * (1.0 + 2.0 * mood.rain)))
            pool = pygame.transform.scale(self._halo, (int(size * 1.4), pool_h))
            for light in (halo, pool):
                light.fill((level, level, level), special_flags=pygame.BLEND_MULT)
            target.blit(halo, (int(x * k - size / 2), int(head_y * k - size / 2)), special_flags=pygame.BLEND_ADD)
            target.blit(
                pool,
                (int(x * k - pool.get_width() / 2), int(foot_y * k - pool_h / 2)),
                special_flags=pygame.BLEND_ADD,
            )

    def _lamp_spots(self) -> list[tuple[float, float, float, float]]:
        return [(x, foot - self._lamp_height(scale), foot, scale) for x, foot, scale in self._lamps]

    def _lamp_height(self, scale: float) -> float:
        stamp = self._sprites.stamp(LAMP, 0.0)
        if stamp is None:
            return _LAMP_FALLBACK_H * scale
        return stamp.image.get_height() * stamp.scale * scale * _LAMP_HEAD_AT

    def _rain(self, target: pygame.Surface, k: float, amount: float, time: float) -> None:
        if amount <= 0.0:
            return
        color = tone(Tone.BLUE_LIGHT)
        for index in range(int(_RAIN_DROPS * amount)):
            pace = _RAIN_FALL * (0.8 + (index % 5) * 0.1)
            fall = time * pace
            x = (index * 137.0 - fall * _RAIN_SLANT) % WIDTH
            y = (index * 271.0 + fall) % HEIGHT
            tail = (x - _RAIN_LEN * _RAIN_SLANT, y - _RAIN_LEN)
            pygame.draw.line(target, color, (int(x * k), int(y * k)), (int(tail[0] * k), int(tail[1] * k)))
        if amount >= _FLASH_FROM and time % _FLASH_EVERY < _FLASH_TIME:
            target.fill(_FLASH, special_flags=pygame.BLEND_ADD)

    def _make_halo(self) -> pygame.Surface:
        halo = pygame.Surface((_HALO_SIZE, _HALO_SIZE))
        halo.fill((0, 0, 0))
        center = _HALO_SIZE / 2
        for radius in range(_HALO_SIZE // 2, 0, -1):
            heat = (1.0 - radius / center) ** 1.6
            color = (int(_HALO_GLOW[0] * heat), int(_HALO_GLOW[1] * heat), int(_HALO_GLOW[2] * heat))
            pygame.draw.circle(halo, color, (int(center), int(center)), radius)
        return halo

    def _make_soft(self) -> pygame.Surface:
        """White radial blob; tinted per power and blitted with ADD."""
        soft = pygame.Surface((_AURA_SOFT, _AURA_SOFT))
        soft.fill((0, 0, 0))
        center = _AURA_SOFT / 2
        for radius in range(_AURA_SOFT // 2, 0, -1):
            heat = (1.0 - radius / center) ** 1.35
            level = int(255 * heat)
            pygame.draw.circle(soft, (level, level, level), (int(center), int(center)), radius)
        return soft

    def _aura(
        self,
        x: float,
        y: float,
        scale: float,
        kind: str,
        time: float,
        size: float,
        soft: bool = True,
        ring: bool = True,
    ) -> None:
        """Soft ADD glow and/or a crisp ring so each power keeps its color at any distance."""
        glow = POWER_GLOW.get(kind)
        if glow is None or scale <= 0.0:
            return
        rgb = tone(glow)
        cream = tone(Tone.CREAM)
        pulse = 0.82 + 0.18 * math.sin(time * _AURA_RATE)
        floor = _AURA_MIN_PICKUP if size <= _AURA_PICKUP else _AURA_MIN_BODY
        if soft:
            diam = max(floor, int(size * 2.0 * scale * pulse))
            blob = pygame.transform.scale(self._soft, (diam, diam))
            blob.fill(rgb, special_flags=pygame.BLEND_MULT)
            corner = (int(x - diam / 2), int(y - diam / 2))
            for _ in range(_AURA_PASSES):
                self._screen.blit(blob, corner, special_flags=pygame.BLEND_ADD)
        if not ring:
            return
        rx = max(floor * 0.38, size * _AURA_RING * scale * pulse)
        ry = rx * 0.78
        width = max(1, int(round(1.6 * max(scale, 0.4))))
        box = (int(x - rx), int(y - ry), max(2, int(rx * 2)), max(2, int(ry * 2)))
        pygame.draw.ellipse(self._screen, cream, box, width + 1)
        pygame.draw.ellipse(self._screen, rgb, box, width)

    def _draw_skyline(self, lane_pos: float, time: float) -> None:
        offset = lane_pos - 1.0
        self._blit_slot(SKYLINE_FAR, WIDTH / 2 - offset * _FAR_SHIFT, HORIZON_Y, 1.0, time, shadow=False)
        self._blit_slot(SKYLINE_NEAR, WIDTH / 2 - offset * _NEAR_SHIFT, HORIZON_Y, 1.0, time, shadow=False)

    def _draw_hitboxes(self, world: _WorldView, player: _PlayerView) -> None:
        layer = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        body = player_hitbox(player)
        horizon = 36.0
        for obstacle in world.obstacles:
            if obstacle.z > horizon:
                continue
            box = obstacle_box(obstacle.kind, obstacle.lane, obstacle.z, world.distance)
            color = (255, 96, 84, 220) if overlaps(body, box) else (255, 236, 220, 150)
            self._draw_prism(layer, box, color)
        for biscuit in world.biscuits:
            if biscuit.taken or biscuit.z > horizon:
                continue
            box = pickup_box(biscuit.lane, biscuit.z, height=biscuit.height)
            color = (255, 196, 64, 220) if overlaps(body, box) else (255, 196, 64, 110)
            self._draw_prism(layer, box, color)
        for bonus in world.bonuses:
            if bonus.taken or bonus.z > horizon:
                continue
            box = pickup_box(bonus.lane, bonus.z)
            color = (90, 210, 255, 220) if overlaps(body, box) else (90, 210, 255, 120)
            self._draw_prism(layer, box, color)
        self._draw_prism(layer, body, (255, 186, 48, 235))
        self._screen.blit(layer, (0, 0))

    def _draw_prism(self, layer: pygame.Surface, box: object, color: tuple[int, int, int, int]) -> None:
        def point(lane: float, z: float, height: float) -> tuple[float, float]:
            x, y, scale = project(lane, z)
            return x, y - units_to_px(height, scale)

        lanes = (box.lane - box.half_lane, box.lane + box.half_lane)
        depths = (box.z - box.half_z, box.z + box.half_z)
        ground = [
            point(lanes[0], depths[0], box.bottom),
            point(lanes[1], depths[0], box.bottom),
            point(lanes[1], depths[1], box.bottom),
            point(lanes[0], depths[1], box.bottom),
        ]
        roof = [
            point(lanes[0], depths[0], box.top),
            point(lanes[1], depths[0], box.top),
            point(lanes[1], depths[1], box.top),
            point(lanes[0], depths[1], box.top),
        ]
        fill = (color[0], color[1], color[2], min(64, color[3]))
        pygame.draw.polygon(layer, fill, [(int(p[0]), int(p[1])) for p in ground])
        loop = ground[1:] + ground[:1]
        roof_loop = roof[1:] + roof[:1]
        for start, end in zip(ground, loop):
            pygame.draw.line(layer, color, (int(start[0]), int(start[1])), (int(end[0]), int(end[1])), 2)
        for start, end in zip(roof, roof_loop):
            pygame.draw.line(layer, color, (int(start[0]), int(start[1])), (int(end[0]), int(end[1])), 2)
        for start, end in zip(ground, roof):
            pygame.draw.line(layer, color, (int(start[0]), int(start[1])), (int(end[0]), int(end[1])), 2)

    def _make_sky(self) -> pygame.Surface:
        sky = pygame.Surface((WIDTH, max(1, HORIZON_Y)))
        span = HORIZON_Y if HORIZON_Y else 1
        for y in range(HORIZON_Y):
            color = _mix(_SKY_TOP, _SKY_HORIZON, y / span)
            pygame.draw.line(sky, color, (0, y), (WIDTH, y))
        return sky

    def _make_haze(self) -> pygame.Surface:
        haze = pygame.Surface((WIDTH, 56), pygame.SRCALPHA)
        for row in range(56):
            alpha = int(_HAZE_ALPHA * (1.0 - row / 56.0))
            pygame.draw.line(haze, (*tone(Tone.PEACH), alpha), (0, row), (WIDTH, row))
        return haze

    def _draw_sky(self, time: float, night: float) -> None:
        if not self._blit_slot(SKY, WIDTH / 2, HORIZON_Y, 1.0, time, shadow=False):
            self._screen.blit(self._sky, (0, 0))
            self._draw_sun()
            self._draw_clouds(time)
        if night > 0.0:
            self._fade_slot(SKY_NIGHT, WIDTH / 2, HORIZON_Y, night)

    def _fade_slot(self, slot: str, x: float, y: float, amount: float) -> None:
        stamp = self._sprites.stamp(slot, 0.0)
        if stamp is None:
            return
        image = self._scaled.get(slot)
        if image is None:
            size = (int(stamp.image.get_width() * stamp.scale), int(stamp.image.get_height() * stamp.scale))
            image = pygame.transform.scale(stamp.image, size)
            self._scaled[slot] = image
        image.set_alpha(int(255 * min(1.0, amount)))
        self._screen.blit(image, (int(x - image.get_width() / 2), int(y - image.get_height())))

    def _draw_sun(self) -> None:
        glow = pygame.Surface((170, 170), pygame.SRCALPHA)
        pygame.draw.circle(glow, _SUN_GLOW, (85, 85), 74)
        pygame.draw.circle(glow, (255, 206, 130, 80), (85, 85), 46)
        self._screen.blit(glow, (_SUN_X - 85, _SUN_Y - 85))
        self._fill_disc(_SUN_X, _SUN_Y, 28, _SUN_CORE)
        self._fill_disc(_SUN_X - 7, _SUN_Y - 6, 12, _SUN_HOT)

    def _draw_clouds(self, time: float) -> None:
        clouds = (
            (90.0, 52.0, 86.0, 26.0, 7.0),
            (460.0, 96.0, 110.0, 30.0, 11.0),
            (820.0, 44.0, 74.0, 22.0, 8.0),
            (1080.0, 118.0, 64.0, 18.0, 14.0),
            (260.0, 150.0, 52.0, 16.0, 9.0),
        )
        span = WIDTH + 280
        for index, (base_x, y, rx, ry, speed) in enumerate(clouds):
            drift = (base_x + time * speed) % span - 120.0
            self._cloud(drift, y, rx, ry, index)

    def _cloud(self, x: float, y: float, rx: float, ry: float, index: int) -> None:
        soft = _CLOUD_SOFT if index % 2 else _CLOUD
        self._fill_oval(x, y, rx * 2.0, ry * 2.0, _CLOUD)
        self._fill_oval(x - rx * 0.42, y + ry * 0.2, rx * 1.15, ry * 1.45, soft)
        self._fill_oval(x + rx * 0.48, y + ry * 0.12, rx * 0.95, ry * 1.3, _CLOUD)

    def _draw_grass(self, distance: float) -> None:
        self._paint(
            [(0, HORIZON_Y), (WIDTH, HORIZON_Y), (WIDTH, HEIGHT), (0, HEIGHT)],
            tone(Tone.PLUM_DARK),
        )
        self._stripes(_OUTER_LEFT, _VERGE_LEFT, distance, _TILE_PERIOD, tone(Tone.PLUM))
        self._stripes(_VERGE_RIGHT, _OUTER_RIGHT, distance, _TILE_PERIOD, tone(Tone.PLUM))
        for lane_a, lane_b in ((_VERGE_LEFT, _ROAD_LEFT), (_ROAD_RIGHT, _VERGE_RIGHT)):
            self._wedge(lane_a, lane_b, tone(Tone.WALK))
            self._stripes(lane_a, lane_b, distance, _TILE_PERIOD, tone(Tone.WALK_LIGHT))

    def _draw_road(self, distance: float) -> None:
        self._wedge(_ROAD_LEFT, _ROAD_RIGHT, tone(Tone.STONE))
        self._stripes(_ROAD_LEFT, _ROAD_RIGHT, distance, _COBBLE_PERIOD, tone(Tone.STONE_DARK))
        for lane_a, lane_b in ((_ROAD_LEFT - _CURB_W, _ROAD_LEFT), (_ROAD_RIGHT, _ROAD_RIGHT + _CURB_W)):
            self._wedge(lane_a, lane_b, tone(Tone.CURB))
            self._stripes(lane_a, lane_b, distance, _CURB_PERIOD, tone(Tone.BRICK))
        self._draw_dashes(distance)

    def _stripes(
        self,
        lane_a: float,
        lane_b: float,
        distance: float,
        period: float,
        color: tuple[int, int, int],
    ) -> None:
        center = (lane_a + lane_b) / 2.0
        half = (lane_b - lane_a) / 2.0
        z = -(distance % (period * 2.0))
        while z < _STRIPE_FAR:
            near = max(z, _STRIPE_NEAR)
            far = min(z + period, _STRIPE_FAR)
            if far > near:
                self._band(center, near, far, half, color)
            z += period * 2.0

    def _draw_dashes(self, distance: float) -> None:
        phase = distance % _DASH_PERIOD
        z = -phase
        while z < _FAR_DRAW_Z:
            far = z + _DASH_LENGTH
            near = z if z > 0.4 else 0.4
            if far > near:
                limit = far if far < _FAR_DRAW_Z else _FAR_DRAW_Z
                if limit > near:
                    self._band(_SEP_LEFT, near, limit, _DASH_HALF, tone(Tone.PAINT))
                    self._band(_SEP_RIGHT, near, limit, _DASH_HALF, tone(Tone.PAINT))
            z += _DASH_PERIOD

    def _draw_actors(self, world: _WorldView, time: float) -> None:
        paints: list[tuple[float, Callable[[], None]]] = []
        for obstacle in world.obstacles:
            if _in_view(obstacle.z):
                paints.append(
                    (
                        obstacle.z,
                        partial(
                            self._draw_obstacle,
                            obstacle,
                            time,
                            world.distance,
                            world.obstacles,
                        ),
                    )
                )
        for biscuit in world.biscuits:
            if not biscuit.taken and _in_view(biscuit.z):
                paints.append((biscuit.z, partial(self._draw_biscuit, biscuit, time)))
        for bonus in world.bonuses:
            if not bonus.taken and _in_view(bonus.z):
                paints.append((bonus.z, partial(self._draw_bonus, bonus, time)))
        for spot in self._scenery(world.distance):
            paints.append((spot[0], partial(self._draw_prop, spot[1], spot[0], spot[2], spot[3])))
        paints.sort(key=lambda item: item[0], reverse=True)
        for _, paint in paints:
            paint()

    def _scenery(self, distance: float) -> list[tuple[float, float, int, int]]:
        spots: list[tuple[float, float, int, int]] = []
        self._fill_row(spots, distance, _TREE_SPAN, _TREE_LANES, _TREE)
        self._fill_row(spots, distance, _SHRUB_SPAN, _SHRUB_LANES, _SHRUB)
        self._fill_row(spots, distance, _FACADE_SPAN, _FACADE_LANES, _FACADE)
        self._fill_row(spots, distance, _LAMP_SPAN, _LAMP_LANES, _LAMP)
        return spots

    def _fill_row(
        self,
        spots: list[tuple[float, float, int, int]],
        distance: float,
        span: float,
        lanes: tuple[float, float],
        kind: int,
    ) -> None:
        phase = distance % span
        z = span - phase
        while z < _FAR_DRAW_Z:
            if z > 1.1:
                spot = int(round((z + distance) / span))
                for lane in lanes:
                    mark = (spot * _HASH_SPOT) ^ (int(lane * 8.0) * _HASH_LANE)
                    spots.append((z, lane, kind, (mark >> 4) & 3))
            z += span

    def _draw_chase(self, world: _WorldView, player: _PlayerView, time: float) -> None:
        girl_covers = world.game_over and world.catch_timer > _COVER_AT
        if girl_covers:
            self._draw_kovu(player)
            self._draw_girl(world, player, time)
            return
        self._draw_girl(world, player, time)
        self._draw_kovu(player)

    def _draw_kovu(self, player: _PlayerView) -> None:
        ground_x, ground_y, scale = project(player.lane_pos, PLAYER_DRAW_Z)
        scale *= _KOVU_SIZE
        sliding = player.sliding and not player.jumping
        squat = _SLIDE_SQUASH if sliding else 1.0
        stretch = _SLIDE_STRETCH if sliding else 1.0
        phase = player.run_time * _GAIT
        drive = math.sin(phase)
        ay = ground_y - player.height * _JUMP_LIFT
        if sliding:
            ay += 22.0 * scale
        elif not player.jumping:
            ay -= math.sin(phase * 2.0) * 4.0 * scale
        shadow_rx = (48.0 if sliding else 34.0) * scale * (1.0 - 0.4 * player.height)
        shadow_ry = 11.0 * scale * (1.0 - 0.35 * player.height)
        self._shadow(ground_x, ground_y, shadow_rx, shadow_ry)
        feet_y = ground_y - player.height * _JUMP_LIFT
        armed = _armed_power(player)
        body_y = feet_y - 58.0 * scale
        if armed is not None:
            self._aura(ground_x, body_y, scale, armed, player.run_time, _AURA_BODY, ring=False)
        slot, clock = _kovu_slot(player)
        drawn = self._blit_slot(slot, ground_x, feet_y, scale, clock, shadow=False)
        if armed is not None:
            self._aura(ground_x, body_y, scale, armed, player.run_time, _AURA_BODY, soft=False)
        if drawn:
            return
        if player.rocket_time > 0.0:
            flicker = 0.75 + 0.25 * math.sin(player.run_time * 30.0)
            self._fill_oval(ground_x, ay + 18.0 * scale, 16.0 * scale, 28.0 * scale * flicker, (255, 150, 40))
            self._fill_oval(ground_x, ay + 8.0 * scale, 8.0 * scale, 14.0 * scale, (255, 230, 150))

        def place(lateral: float, forward: float, lift: float) -> tuple[float, float]:
            vertical = (lift + forward * _DEPTH) * squat
            extra = forward * (stretch - 1.0) * _STRETCH_REACH
            x = ground_x + (lateral + forward * _SHEAR * stretch) * scale
            y = ay - (vertical + extra) * scale
            return x, y

        def paw(forward: float, lateral: float, wave: float) -> tuple[float, float, float]:
            if player.jumping:
                return lateral * 0.65, forward - 14.0, 30.0
            if sliding:
                return lateral * 1.25, forward - 48.0, 0.0
            return lateral + wave * 2.0, forward + wave * 17.0, max(0.0, wave) * 16.0

        def knee(
            hip: tuple[float, float, float], foot: tuple[float, float, float]
        ) -> tuple[float, float, float]:
            bend = 8.0 if hip[0] >= 0.0 else -8.0
            lift = hip[2] * 0.4 + foot[2] * 0.28
            fwd = hip[1] * 0.55 + foot[1] * 0.45 - 5.0
            if player.jumping:
                lift = hip[2] * 0.72
                fwd = hip[1] - 4.0
            return (hip[0] + foot[0]) * 0.5 + bend, fwd, lift

        def leg(
            hip: tuple[float, float, float],
            foot: tuple[float, float, float],
            radius: float,
            color: tuple[int, int, int],
        ) -> None:
            joint = knee(hip, foot)
            points = (place(*hip), place(*joint), place(*foot))
            self._limb(points, (radius, radius * 0.72), color)
            self._oval(points[2][0], points[2][1], radius * 2.5, radius * 1.25, _PAW)

        hind_l = (-12.0, 6.0, 50.0)
        hind_r = (11.0, 10.0, 48.0)
        front_l = (-8.0, 54.0, 44.0)
        front_r = (10.0, 60.0, 42.0)
        flap = math.sin(phase * 2.0) * (3.0 if player.jumping or sliding else 7.0)
        perk = 8.0 if player.jumping else 0.0
        wag = math.sin(phase * 2.0 + 0.5) * (4.0 if player.jumping or sliding else 12.0)
        trail = -18.0 if sliding else 0.0

        tail = (
            place(-6.0, 4.0 + trail, 58.0),
            place(-26.0, -4.0 + trail, 78.0 + wag * 0.35),
            place(-34.0, 10.0 + trail * 0.3, 102.0 + wag),
            place(-18.0, 24.0, 118.0 + wag * 0.4),
        )
        self._limb(tail, (4.6 * scale, 3.2 * scale, 2.0 * scale), _SADDLE)

        leg(hind_l, paw(2.0, -11.0, -drive), 4.0 * scale, _COAT_FAR)
        leg(front_l, paw(50.0, -7.0, drive), 3.2 * scale, _COAT_FAR)

        rump = place(0.0, 12.0, 40.0)
        back = place(1.0, 40.0, 56.0)
        chest = place(2.0, 66.0, 50.0)
        self._oval(rump[0], rump[1], 42.0 * scale, 34.0 * scale * squat, _COAT)
        self._oval(back[0], back[1], 28.0 * scale, 62.0 * scale * squat, _COAT)
        self._oval(chest[0], chest[1], 26.0 * scale, 30.0 * scale * squat, _COAT)
        saddle = place(0.0, 38.0, 66.0)
        self._oval(saddle[0], saddle[1], 14.0 * scale, 40.0 * scale * squat, _SADDLE)
        belly = place(9.0, 34.0, 38.0)
        self._fill_oval(belly[0], belly[1], 12.0 * scale, 16.0 * scale * squat, _BELLY)
        shine = place(-2.0, 18.0, 52.0)
        self._fill_oval(shine[0], shine[1], 12.0 * scale, 8.0 * scale * squat, _COAT_SHINE)

        leg(hind_r, paw(8.0, 10.0, drive), 4.2 * scale, _COAT)
        leg(front_r, paw(58.0, 11.0, -drive), 3.4 * scale, _COAT)

        self._limb(
            (place(1.0, 64.0, 58.0), place(2.0, 82.0, 86.0)),
            (5.2 * scale,),
            _COAT,
        )
        self._ear(place, -1.0, flap + perk, scale, squat)
        self._ear(place, 1.0, flap * 0.75 + perk, scale, squat)
        skull = place(1.0, 86.0, 100.0)
        self._oval(skull[0], skull[1], 26.0 * scale, 24.0 * scale * squat, _COAT)
        snout = place(14.0, 96.0, 90.0)
        self._oval(snout[0], snout[1], 16.0 * scale, 9.0 * scale * squat, _SNOUT)
        nose = place(20.0, 100.0, 88.0)
        self._disc(nose[0], nose[1], 3.6 * scale, _NOSE)
        eye = place(10.0, 90.0, 102.0)
        self._fill_disc(eye[0], eye[1], 2.4 * scale, _EYE)
        self._fill_disc(eye[0] - 0.7 * scale, eye[1] - 0.7 * scale, 0.9 * scale, _HIGHLIGHT)
        collar = place(1.0, 76.0, 68.0)
        self._oval(collar[0], collar[1], 20.0 * scale, 9.0 * scale * max(squat, 0.7), _COLLAR)
        tag = place(8.0, 76.0, 58.0)
        self._disc(tag[0], tag[1], 3.4 * scale, _TAG)

    def _ear(
        self,
        place: Callable[[float, float, float], tuple[float, float]],
        side: float,
        flap: float,
        scale: float,
        squat: float,
    ) -> None:
        outer = (
            place(side * 5.0, 80.0, 104.0),
            place(side * 13.0, 74.0, 124.0 + flap),
            place(side * 18.0, 70.0, 112.0 + flap * 0.3),
            place(side * 7.0, 78.0, 96.0),
        )
        inner = (
            place(side * 7.0, 78.0, 104.0),
            place(side * 12.0, 74.0, 116.0 + flap * 0.6),
            place(side * 10.0, 76.0, 100.0),
        )
        self._poly(outer, _SADDLE)
        if squat > 0.7:
            self._poly(inner, _INNER_EAR)

    def _draw_girl(self, world: _WorldView, player: _PlayerView, time: float) -> None:
        pose = self._girl_pose(world, player, time)
        grabbing = pose.ease > _GRAB_FROM
        slot = GIRL_GRAB if grabbing else GIRL_RUN
        clock = (pose.ease - _GRAB_FROM) / (1.0 - _GRAB_FROM) if grabbing else time
        if self._blit_slot(slot, pose.x, pose.y + _GIRL_FEET * pose.g, pose.g, clock):
            return
        swing = pose.stride * (1.0 - pose.ease)
        left = self._girl_hand(pose, -1.0, swing)
        right = self._girl_hand(pose, 1.0, -swing)
        self._girl_back(pose)
        if not grabbing:
            self._girl_arm_of(pose, left, right, rear=True)
        self._girl_torso(pose)
        self._girl_legs(pose)
        self._girl_head(pose)
        if grabbing:
            self._girl_arm(pose, -1.0, left, 14.0)
            self._girl_arm(pose, 1.0, right, -14.0)
            return
        self._girl_arm_of(pose, left, right, rear=False)

    def _girl_pose(self, world: _WorldView, player: _PlayerView, time: float) -> _Pose:
        raw = 0.0
        if world.game_over:
            raw = world.catch_timer / _REACH_AT
            if raw > 1.0:
                raw = 1.0
        pressure = 0.0 if world.game_over else min(1.0, max(0.0, world.chase_pressure))
        dog_x, dog_y, dog_scale = project(player.lane_pos, PLAYER_DRAW_Z)
        dog_y -= player.height * _JUMP_LIFT
        rest_z = 1.35 - 0.55 * pressure
        rest_x, _, _ = project(player.lane_pos, rest_z)
        aim_x = dog_x
        aim_y = dog_y - 48.0 * dog_scale
        ease = max(raw, pressure * 0.35)
        sway = math.sin(time * 2.0) * 14.0 * (1.0 - ease)
        bob = math.sin(time * 20.0) * 4.5 * (1.0 - ease)
        return _Pose(
            x=rest_x + sway + (aim_x - rest_x) * raw,
            y=_GIRL_HEAD_Y + bob + (aim_y - _GIRL_HEAD_Y) * raw - 18.0 * pressure,
            g=1.0 + raw * 0.5 + pressure * 0.12,
            ease=ease,
            stride=math.sin(time * (10.0 + 6.0 * pressure)),
        )

    def _girl_back(self, pose: _Pose) -> None:
        sway = pose.stride * 6.0 * (1.0 - pose.ease)
        bun = self._at(pose, sway, -34.0)
        self._oval(bun[0], bun[1], 28.0 * pose.g, 24.0 * pose.g, _HAIR)
        self._fill_oval(bun[0] - 4.0 * pose.g, bun[1] - 4.0 * pose.g, 12.0 * pose.g, 8.0 * pose.g, _HAIR_LIGHT)
        pin = self._at(pose, sway, -28.0)
        self._fill_disc(pin[0], pin[1], 3.2 * pose.g, _CARDIGAN_LIGHT)
        cape = self._at(pose, 0.0, 22.0)
        self._oval(cape[0], cape[1], 58.0 * pose.g, 30.0 * pose.g, _CARDIGAN_DARK)

    def _girl_legs(self, pose: _Pose) -> None:
        lift_l = max(0.0, pose.stride) * 24.0 * (1.0 - pose.ease * 0.85)
        lift_r = max(0.0, -pose.stride) * 24.0 * (1.0 - pose.ease * 0.85)
        self._girl_leg(pose, -1.0, lift_l)
        self._girl_leg(pose, 1.0, lift_r)

    def _girl_leg(self, pose: _Pose, side: float, lift: float) -> None:
        hip = self._at(pose, side * 12.0, 58.0)
        knee = self._at(pose, side * 15.0, 74.0 - lift * 0.35)
        shoe = self._at(pose, side * 10.0, 84.0 - lift * 0.55)
        self._limb((hip, knee, shoe), (7.2 * pose.g, 5.8 * pose.g), _HAIR_DARK)
        self._oval(shoe[0], shoe[1], 24.0 * pose.g, 14.0 * pose.g, _SHOE)
        self._fill_oval(shoe[0], shoe[1] + 4.0 * pose.g, 24.0 * pose.g, 7.0 * pose.g, _SOLE)

    def _girl_torso(self, pose: _Pose) -> None:
        shoulder_y = 32.0 - pose.ease * 8.0
        hip_y = 58.0 + pose.ease * 18.0
        hem_y = 70.0 + pose.ease * 20.0
        torso = (
            self._at(pose, -24.0, shoulder_y),
            self._at(pose, 24.0, shoulder_y),
            self._at(pose, 18.0, hip_y),
            self._at(pose, -18.0, hip_y),
        )
        self._poly(torso, _CARDIGAN)
        skirt = (
            self._at(pose, -22.0, hip_y - 4.0),
            self._at(pose, 22.0, hip_y - 4.0),
            self._at(pose, 28.0, hem_y),
            self._at(pose, -28.0, hem_y),
        )
        self._poly(skirt, _SKIRT)
        for dx, dy in ((-10.0, 8.0), (6.0, 12.0), (-2.0, 16.0), (14.0, 6.0)):
            bloom = self._at(pose, dx, hip_y + dy)
            self._fill_disc(bloom[0], bloom[1], 2.4 * pose.g, _CARDIGAN_LIGHT)
        chest = self._at(pose, -4.0, 46.0)
        self._fill_oval(chest[0], chest[1], 16.0 * pose.g, 14.0 * pose.g, _CARDIGAN_LIGHT)
        neck = self._at(pose, 0.0, 24.0)
        self._limb((self._at(pose, 0.0, 16.0), neck), (7.0 * pose.g,), _SKIN)
        scarf = self._at(pose, 0.0, 28.0)
        self._oval(scarf[0], scarf[1], 34.0 * pose.g, 12.0 * pose.g, _SCARF)
        for dx, dy in ((-6.0, 42.0), (4.0, 50.0)):
            button = self._at(pose, dx, dy)
            self._fill_disc(button[0], button[1], 2.6 * pose.g, _BUTTON)

    def _girl_head(self, pose: _Pose) -> None:
        center = self._at(pose, 0.0, 0.0)
        radius = 30.0 * pose.g
        self._disc(center[0], center[1], radius, _SKIN)
        ear_l = self._at(pose, -24.0, 4.0)
        ear_r = self._at(pose, 24.0, 4.0)
        self._fill_oval(ear_l[0], ear_l[1], 10.0 * pose.g, 14.0 * pose.g, _SKIN)
        self._fill_oval(ear_r[0], ear_r[1], 10.0 * pose.g, 14.0 * pose.g, _SKIN)
        self._line(self._at(pose, -28.0, 2.0), self._at(pose, -34.0, 6.0), _GLASS, _OUTLINE)
        self._line(self._at(pose, 28.0, 2.0), self._at(pose, 34.0, 6.0), _GLASS, _OUTLINE)
        crown = self._at(pose, 0.0, -12.0)
        self._oval(crown[0], crown[1], 62.0 * pose.g, 40.0 * pose.g, _HAIR)
        side_l = self._at(pose, -24.0, 2.0)
        side_r = self._at(pose, 24.0, 2.0)
        self._oval(side_l[0], side_l[1], 18.0 * pose.g, 36.0 * pose.g, _HAIR)
        self._oval(side_r[0], side_r[1], 18.0 * pose.g, 36.0 * pose.g, _HAIR)
        shine = self._at(pose, -8.0, -20.0)
        self._fill_oval(shine[0], shine[1], 16.0 * pose.g, 10.0 * pose.g, _HAIR_LIGHT)
        bun = self._at(pose, 0.0, -30.0)
        self._oval(bun[0], bun[1], 26.0 * pose.g, 22.0 * pose.g, _HAIR)
        self._fill_disc(bun[0], bun[1] + 4.0 * pose.g, 3.0 * pose.g, _CARDIGAN_LIGHT)
        self._girl_face(pose)

    def _girl_face(self, pose: _Pose) -> None:
        glance = -3.0 * pose.ease
        self._eye(pose, -11.0, 6.0 + glance, glance)
        self._eye(pose, 11.0, 6.0 + glance, glance)
        rim = max(1, int(2.4 * pose.g))
        for dx in (-11.0, 11.0):
            center = self._at(pose, dx, 6.0 + glance)
            rect = pygame.Rect(
                int(center[0] - 7.0 * pose.g),
                int(center[1] - 6.0 * pose.g),
                max(2, int(14.0 * pose.g)),
                max(2, int(12.0 * pose.g)),
            )
            pygame.draw.ellipse(self._screen, _GLASS, rect, rim)
        self._line(self._at(pose, -4.0, 6.0 + glance), self._at(pose, 4.0, 6.0 + glance), _GLASS, rim)
        brow_w = max(_OUTLINE, int(2.5 * pose.g))
        self._line(self._at(pose, -18.0, 0.0), self._at(pose, -4.0, 2.0), _BROW, brow_w)
        self._line(self._at(pose, 4.0, 2.0), self._at(pose, 18.0, 0.0), _BROW, brow_w)
        nose = self._at(pose, 0.0, 12.0)
        self._line(nose, (nose[0], nose[1] + 5.0 * pose.g), _dark(_SKIN, 40), _OUTLINE)
        mouth = self._at(pose, 0.0, 18.0)
        if pose.ease > 0.55:
            self._fill_oval(mouth[0], mouth[1], 12.0 * pose.g, 8.0 * pose.g, _MOUTH)
        else:
            self._line(
                (mouth[0] - 7.0 * pose.g, mouth[1]),
                (mouth[0] + 7.0 * pose.g, mouth[1]),
                _dark(_SKIN, 50),
                _OUTLINE,
            )

    def _eye(self, pose: _Pose, dx: float, dy: float, glance: float) -> None:
        center = self._at(pose, dx, dy)
        self._fill_disc(center[0], center[1], 5.0 * pose.g, _HIGHLIGHT)
        pupil = self._at(pose, dx, dy + 0.8 + glance * 0.15)
        self._fill_disc(pupil[0], pupil[1], 2.8 * pose.g, _IRIS)
        self._fill_disc(pupil[0], pupil[1] + 0.4 * pose.g, 1.4 * pose.g, _EYE)
        catch = self._at(pose, dx - 1.6, dy - 1.5)
        self._fill_disc(catch[0], catch[1], max(1.0, 1.3 * pose.g), _HIGHLIGHT)

    def _girl_arm_of(
        self,
        pose: _Pose,
        left: tuple[float, float],
        right: tuple[float, float],
        rear: bool,
    ) -> None:
        left_is_rear = left[1] >= right[1]
        if rear == left_is_rear:
            self._girl_arm(pose, -1.0, left, -8.0)
            return
        self._girl_arm(pose, 1.0, right, 8.0)

    def _girl_hand(self, pose: _Pose, side: float, swing: float) -> tuple[float, float]:
        reach = pose.ease
        run = self._at(pose, side * (34.0 + swing * 4.0), 72.0 - swing * 12.0)
        grab = self._at(pose, side * 72.0, 6.0 - reach * 8.0)
        return (
            run[0] + (grab[0] - run[0]) * reach,
            run[1] + (grab[1] - run[1]) * reach,
        )

    def _girl_arm(
        self,
        pose: _Pose,
        side: float,
        hand: tuple[float, float],
        bend: float,
    ) -> None:
        shoulder = self._at(pose, side * 22.0, 38.0 - pose.ease * 8.0)
        elbow = (
            (shoulder[0] + hand[0]) * 0.5 + bend * pose.g,
            (shoulder[1] + hand[1]) * 0.5 + 6.0 * pose.g * (1.0 - pose.ease),
        )
        self._limb((shoulder, elbow, hand), (7.2 * pose.g, 6.0 * pose.g), _CARDIGAN)
        self._disc(hand[0], hand[1], 7.0 * pose.g, _SKIN)

    def _draw_prop(self, lane: float, z: float, kind: int, variant: int) -> None:
        x, y, scale = project(lane, z)
        if kind == _LAMP:
            self._lamps.append((x, y, scale))
        slot = _FACADES[variant % len(_FACADES)] if kind == _FACADE else _PROP_SLOTS[kind]
        if self._blit_slot(slot, x, y, scale, 0.0, shadow=kind != _FACADE):
            return
        if kind == _TREE:
            self._draw_tree(lane, z, variant)
            return
        if kind == _FACADE:
            self._draw_facade(x, y, scale)
            return
        if kind == _LAMP:
            self._draw_lamp(x, y, scale)
            return
        self._draw_shrub(lane, z, variant)

    def _draw_facade(self, x: float, y: float, scale: float) -> None:
        w = _FACADE_FALLBACK[0] * scale
        h = _FACADE_FALLBACK[1] * scale
        self._paint([(x - w / 2, y - h), (x + w / 2, y - h), (x + w / 2, y), (x - w / 2, y)], tone(Tone.PEACH))
        for side in (-1.0, 1.0):
            cx = x + side * w * 0.22
            top = y - h * 0.7
            self._paint(
                [(cx - w * 0.08, top), (cx + w * 0.08, top), (cx + w * 0.08, top + h * 0.35), (cx - w * 0.08, top + h * 0.35)],
                tone(Tone.WINDOW),
            )

    def _draw_lamp(self, x: float, y: float, scale: float) -> None:
        head = y - _LAMP_FALLBACK_H * scale
        pygame.draw.line(self._screen, tone(Tone.INK), (int(x), int(y)), (int(x), int(head)), max(1, int(6 * scale)))
        self._fill_disc(x, head, 10.0 * scale, tone(Tone.SUN))

    def _draw_tree(self, lane: float, z: float, variant: int) -> None:
        x, y, scale = project(lane, z)
        tall = 1.22 if variant & 2 else 1.0
        trunk_h = 86.0 * scale * tall
        canopy = 36.0 * scale * tall
        self._shadow(x, y, canopy * 0.85, 8.0 * scale)
        top = y - trunk_h
        self._poly(
            (
                (x - 6.0 * scale, y),
                (x + 6.0 * scale, y),
                (x + 4.0 * scale, top),
                (x - 4.0 * scale, top),
            ),
            _TRUNK,
        )
        leaf = _LEAF_DARK if variant & 1 else _LEAF
        self._oval(x, top - canopy * 0.15, canopy * 2.0, canopy * 1.7, leaf)
        self._oval(x - canopy * 0.42, top + canopy * 0.1, canopy * 1.25, canopy * 1.15, _LEAF_LIGHT)
        self._oval(x + canopy * 0.38, top - canopy * 0.35, canopy * 1.15, canopy * 1.05, _LEAF)

    def _draw_shrub(self, lane: float, z: float, variant: int) -> None:
        x, y, scale = project(lane, z)
        w = (78.0 if variant & 1 else 62.0) * scale
        h = 48.0 * scale
        self._shadow(x, y, w * 0.45, 7.0 * scale)
        self._oval(x - w * 0.22, y - h * 0.34, w * 0.55, h * 0.7, _LEAF_DARK)
        self._oval(x + w * 0.2, y - h * 0.3, w * 0.5, h * 0.62, _LEAF)
        self._oval(x, y - h * 0.55, w * 0.48, h * 0.58, _LEAF_LIGHT)

    def _draw_obstacle(
        self,
        obstacle: _ObstacleView,
        time: float,
        distance: float,
        obstacles: Sequence[_ObstacleView],
    ) -> None:
        if obstacle.kind == WAGON:
            self._draw_wagon(obstacle.lane, obstacle.z, obstacles)
            return
        variant = _variant(obstacle.lane, obstacle.z, distance)
        x, y, scale = project(obstacle.lane, obstacle.z)
        if self._blit_slot(_obstacle_slot(obstacle.kind, variant), x, y, scale, time):
            return
        if obstacle.kind == LOW:
            self._draw_low(obstacle.lane, obstacle.z, variant)
            return
        if obstacle.kind == HIGH:
            self._draw_high(obstacle.lane, obstacle.z, time, variant)
            return
        if obstacle.kind == FULL:
            self._draw_full(obstacle.lane, obstacle.z, variant)

    def _draw_wagon(self, lane: float, z: float, obstacles: Sequence[_ObstacleView]) -> None:
        """Caja 2.5D de frente: techo hacia el horizonte y trompa hacia la cámara."""
        near_z = max(_MIN_Z, z - WAGON_HALF_Z)
        far_z = z + WAGON_HALF_Z
        xn, yn, sn = project(lane, near_z)
        xf, yf, sf = project(lane, far_z)
        half_n = WAGON_W * 0.48 * sn
        half_f = WAGON_W * 0.48 * sf
        hn = _WAGON_H * sn
        hf = _WAGON_H * sf
        rail = 10.0 * sn
        self._shadow(xn, yn, half_n * 1.05, max(4.0, 9.0 * sn))
        left = (
            (xn - half_n, yn - rail),
            (xn - half_n, yn - hn),
            (xf - half_f, yf - hf),
            (xf - half_f, yf - rail * sf / max(sn, 0.01)),
        )
        right = (
            (xn + half_n, yn - rail),
            (xn + half_n, yn - hn),
            (xf + half_f, yf - hf),
            (xf + half_f, yf - rail * sf / max(sn, 0.01)),
        )
        self._poly(left, _WAGON_SIDE)
        self._poly(right, _WAGON_SIDE)
        roof = (
            (xn - half_n, yn - hn),
            (xn + half_n, yn - hn),
            (xf + half_f, yf - hf),
            (xf - half_f, yf - hf),
        )
        self._poly(roof, _WAGON_ROOF)
        self._paint(
            (
                (xn - half_n * 0.72, yn - hn),
                (xn + half_n * 0.72, yn - hn),
                (xf + half_f * 0.72, yf - hf),
                (xf - half_f * 0.72, yf - hf),
            ),
            _WAGON_ROOF_FAR,
        )
        seam_y = yf - hf
        self._line((xf - half_f, seam_y), (xf + half_f, seam_y), _WAGON_SEAM, max(1, int(2 * sf)))
        if self._wagon_nose(lane, z, obstacles):
            self._wagon_face(xn, yn, sn, half_n, hn, rail)

    def _wagon_nose(self, lane: float, z: float, obstacles: Sequence[_ObstacleView]) -> bool:
        """Solo la trompa del vagón más cercano del convoy mira a la cámara."""
        nose = z - WAGON_HALF_Z
        for other in obstacles:
            if other.kind != WAGON or int(other.lane) != int(lane):
                continue
            if other.z >= z - 0.01:
                continue
            if other.z + WAGON_HALF_Z >= nose - 0.2:
                return False
        return True

    def _wagon_face(
        self,
        x: float,
        y: float,
        scale: float,
        half: float,
        height: float,
        rail: float,
    ) -> None:
        top = y - height
        skirt = y - rail
        self._poly(
            (
                (x - half, skirt),
                (x + half, skirt),
                (x + half, top),
                (x - half, top),
            ),
            _WAGON_FACE,
        )
        self._paint(
            (
                (x - half, top),
                (x + half, top),
                (x + half * 0.92, top + height * 0.12),
                (x - half * 0.92, top + height * 0.12),
            ),
            _WAGON_FACE_DARK,
        )
        pane_w = half * 0.28
        pane_h = height * 0.28
        pane_y = top + height * 0.28
        for side in (-1.0, 1.0):
            cx = x + side * half * 0.42
            self._paint(
                (
                    (cx - pane_w, pane_y),
                    (cx + pane_w, pane_y),
                    (cx + pane_w, pane_y + pane_h),
                    (cx - pane_w, pane_y + pane_h),
                ),
                _WAGON_WINDOW,
            )
            self._paint(
                (
                    (cx - pane_w * 0.7, pane_y + 2.0 * scale),
                    (cx + pane_w * 0.2, pane_y + 2.0 * scale),
                    (cx + pane_w * 0.2, pane_y + pane_h * 0.45),
                    (cx - pane_w * 0.7, pane_y + pane_h * 0.45),
                ),
                _WAGON_GLASS,
            )
        for side in (-1.0, 1.0):
            lx = x + side * half * 0.72
            ly = skirt - height * 0.18
            self._fill_disc(lx, ly, max(2.0, 4.5 * scale), _WAGON_LIGHT)
            self._fill_disc(lx, ly, max(1.0, 2.0 * scale), (255, 220, 140))
        bump = skirt - height * 0.08
        self._paint(
            (
                (x - half * 0.9, bump),
                (x + half * 0.9, bump),
                (x + half * 0.85, skirt),
                (x - half * 0.85, skirt),
            ),
            _WAGON_BUMPER,
        )

    def _draw_low(self, lane: float, z: float, variant: int) -> None:
        if variant == _AS_HYDRANT:
            self._draw_hydrant(lane, z)
            return
        self._draw_hedge(lane, z)

    def _draw_hedge(self, lane: float, z: float) -> None:
        x, y, scale = project(lane, z)
        w = 96.0 * scale
        h = _LOW_H * scale
        self._shadow(x, y, w * 0.42, 8.0 * scale)
        self._oval(x - w * 0.26, y - h * 0.36, w * 0.52, h * 0.62, _LEAF_DARK)
        self._oval(x + w * 0.24, y - h * 0.32, w * 0.48, h * 0.58, _LEAF)
        self._oval(x, y - h * 0.58, w * 0.58, h * 0.7, _LEAF)
        self._fill_oval(x - w * 0.04, y - h * 0.78, w * 0.28, h * 0.32, _LEAF_LIGHT)

    def _draw_hydrant(self, lane: float, z: float) -> None:
        x, y, scale = project(lane, z)
        h = _LOW_H * scale
        w = 24.0 * scale
        top = y - h
        self._shadow(x, y, w * 1.3, 7.0 * scale)
        self._oval(x, y - 5.0 * scale, w * 1.9, 14.0 * scale, _HYDRANT_DARK)
        self._poly(
            (
                (x - w * 0.58, y - 8.0 * scale),
                (x + w * 0.58, y - 8.0 * scale),
                (x + w * 0.42, top + 16.0 * scale),
                (x - w * 0.42, top + 16.0 * scale),
            ),
            _HYDRANT,
        )
        self._oval(x, top + 16.0 * scale, w * 1.15, 22.0 * scale, _HYDRANT)
        self._oval(x, top + 6.0 * scale, w * 0.62, 12.0 * scale, _CAP)
        self._fill_disc(x, top + 2.0 * scale, 3.4 * scale, _BOLT)
        self._oval(x - w * 0.95, y - h * 0.46, 16.0 * scale, 12.0 * scale, _HYDRANT)
        self._oval(x + w * 0.95, y - h * 0.46, 16.0 * scale, 12.0 * scale, _HYDRANT_DARK)
        self._fill_disc(x - w * 0.95, y - h * 0.46, 3.2 * scale, _BOLT)
        self._fill_disc(x + w * 0.95, y - h * 0.46, 3.2 * scale, _BOLT)

    def _draw_high(self, lane: float, z: float, time: float, variant: int) -> None:
        x, y, scale = project(lane, z)
        half = LANE_SPREAD * scale * 0.36
        height = _HIGH_H * scale
        gap = _HIGH_GAP * scale
        top = y - height
        hem = y - gap
        wave = math.sin(time * 3.4 + z) * 6.0 * scale
        left = x - half
        right = x + half
        post = max(4.0, 7.0 * scale)
        cloth = _CORAL if variant == _AS_HEDGE else _TEAL
        band = _TEAL if variant == _AS_HEDGE else _CORAL
        self._shadow(x, y, half * 0.85, 8.0 * scale)
        self._poly(
            (
                (left + post, top + 12.0 * scale),
                (right - post, top + 10.0 * scale),
                (right - post, hem),
                (x, hem + 7.0 * scale + wave * 0.45),
                (left + post, hem + wave * 0.2),
            ),
            cloth,
        )
        stripe = top + (hem - top) * 0.46
        self._paint(
            (
                (left + post * 1.4, stripe),
                (right - post * 1.4, stripe - 2.0 * scale),
                (right - post * 1.4, stripe + 12.0 * scale),
                (left + post * 1.4, stripe + 14.0 * scale),
            ),
            band,
        )
        for post_x in (left, right):
            self._poly(
                (
                    (post_x - post * 0.5, y),
                    (post_x + post * 0.5, y),
                    (post_x + post * 0.35, top),
                    (post_x - post * 0.35, top),
                ),
                _WOOD,
            )
        pygame.draw.line(
            self._screen,
            _dark(_WOOD, 30),
            (int(left), int(top)),
            (int(right), int(top + 8.0 * scale)),
            _OUTLINE,
        )

    def _draw_full(self, lane: float, z: float, variant: int) -> None:
        if variant == _CRATE_KIND:
            self._draw_crate(lane, z)
            return
        self._draw_bin(lane, z)

    def _draw_bin(self, lane: float, z: float) -> None:
        x, y, scale = project(lane, z)
        w = 76.0 * scale
        h = _FULL_H * scale
        top = y - h
        self._shadow(x, y, w * 0.55, 9.0 * scale)
        self._poly(
            (
                (x - w * 0.38, y - 4.0 * scale),
                (x + w * 0.38, y - 4.0 * scale),
                (x + w * 0.48, top + 16.0 * scale),
                (x - w * 0.48, top + 16.0 * scale),
            ),
            _BIN,
        )
        self._paint(
            (
                (x - w * 0.1, y - 10.0 * scale),
                (x - w * 0.02, y - 10.0 * scale),
                (x - w * 0.06, top + 22.0 * scale),
                (x - w * 0.16, top + 22.0 * scale),
            ),
            _BIN_DARK,
        )
        self._oval(x, top + 14.0 * scale, w * 1.12, 20.0 * scale, _LID)
        self._oval(x, top + 8.0 * scale, w * 0.72, 12.0 * scale, _BIN_DARK)
        self._fill_oval(x, top + 6.0 * scale, w * 0.28, 6.0 * scale, _CAP)

    def _draw_crate(self, lane: float, z: float) -> None:
        x, y, scale = project(lane, z)
        w = 100.0 * scale
        h = _FULL_H * scale
        top = y - h
        self._shadow(x, y, w * 0.48, 9.0 * scale)
        self._poly(
            (
                (x - w * 0.46, y),
                (x + w * 0.46, y),
                (x + w * 0.4, top),
                (x - w * 0.4, top),
            ),
            _CRATE,
        )
        for step in (1, 2, 3):
            line_y = top + h * step / 4.0
            inset = w * (0.4 + 0.06 * step / 4.0)
            pygame.draw.line(
                self._screen,
                _CRATE_DARK,
                (int(x - inset), int(line_y)),
                (int(x + inset), int(line_y)),
                _OUTLINE,
            )
        pygame.draw.line(
            self._screen,
            _CRATE_DARK,
            (int(x - w * 0.42), int(y - 4.0 * scale)),
            (int(x + w * 0.36), int(top + 6.0 * scale)),
            _OUTLINE,
        )

    def _draw_biscuit(self, biscuit: _BiscuitView, time: float) -> None:
        x, ground_y, scale = project(biscuit.lane, biscuit.z)
        # El lift tiene que escalar con la perspectiva; si no, lejos quedan en el cielo
        # y al acercarse parecen caer al vagón.
        on_deck = biscuit.height > 0.05
        y = ground_y - units_to_px(biscuit.height, scale) if on_deck else ground_y
        bob = 0.0 if on_deck else math.sin(time * 6.0 + biscuit.z) * 6.0 * scale
        feet = y - bob
        if self._blit_slot(BISCUIT, x, feet, scale, time + biscuit.z * _SPIN_SPREAD):
            return
        cy = feet - 20.0 * scale
        length = _BISCUIT_W * 0.5 * scale
        knob = 7.2 * scale
        self._shadow(x, ground_y, 14.0 * scale, 4.5 * scale)
        for side_x in (-1.0, 1.0):
            for side_y in (-1.0, 1.0):
                self._disc(
                    x + side_x * length * 0.62,
                    cy + side_y * knob * 0.55,
                    knob * 0.72,
                    _BISCUIT,
                )
        self._oval(x, cy, length * 1.45, knob * 1.15, _BISCUIT)
        self._fill_oval(x, cy - knob * 0.2, length * 0.7, knob * 0.4, _BISCUIT_LIGHT)
        hole = max(1.0, 2.1 * scale)
        self._fill_disc(x - length * 0.18, cy, hole, _BISCUIT_HOLE)
        self._fill_disc(x + length * 0.18, cy, hole, _BISCUIT_HOLE)

    def _draw_bonus(self, bonus: _BonusView, time: float) -> None:
        x, y, scale = project(bonus.lane, bonus.z)
        bob = math.sin(time * 6.0 + bonus.z) * 8.0 * scale
        feet = y - bob
        body = feet - 28.0 * scale
        clock = time + bonus.z * 0.1
        self._aura(x, body, scale, bonus.kind, clock, _AURA_PICKUP, ring=False)
        if not self._blit_slot(_bonus_slot(bonus.kind), x, feet, scale, time):
            cy = y - 34.0 * scale - bob
            self._shadow(x, y, 16.0 * scale, 5.0 * scale)
            if bonus.kind == ROCKET:
                self._draw_rocket(x, cy, scale, time)
            elif bonus.kind == SUPER_JUMP:
                self._draw_spring(x, cy, scale)
            else:
                self._draw_double_jump(x, cy, scale)
        self._aura(x, body, scale, bonus.kind, clock, _AURA_PICKUP, soft=False)

    def _draw_rocket(self, x: float, cy: float, scale: float, time: float) -> None:
        flame = 10.0 + 6.0 * math.sin(time * 18.0)
        self._fill_oval(x, cy + 16.0 * scale, 12.0 * scale, flame * scale, (255, 170, 40))
        self._fill_oval(x, cy + 12.0 * scale, 6.0 * scale, 8.0 * scale, (255, 236, 170))
        self._poly(
            (
                (x, cy - 26.0 * scale),
                (x + 13.0 * scale, cy + 10.0 * scale),
                (x + 6.0 * scale, cy + 8.0 * scale),
                (x - 6.0 * scale, cy + 8.0 * scale),
                (x - 13.0 * scale, cy + 10.0 * scale),
            ),
            (196, 54, 42),
        )
        self._fill_oval(x, cy - 2.0 * scale, 8.0 * scale, 10.0 * scale, (236, 214, 150))

    def _draw_spring(self, x: float, cy: float, scale: float) -> None:
        for step in range(4):
            self._oval(
                x,
                cy + (step - 1.5) * 8.0 * scale,
                24.0 * scale,
                9.0 * scale,
                (232, 176, 48),
            )
        self._poly(
            (
                (x - 8.0 * scale, cy - 22.0 * scale),
                (x, cy - 34.0 * scale),
                (x + 8.0 * scale, cy - 22.0 * scale),
            ),
            (232, 86, 48),
        )

    def _draw_double_jump(self, x: float, cy: float, scale: float) -> None:
        for lift in (0.0, 16.0):
            self._poly(
                (
                    (x - 14.0 * scale, cy + lift * scale),
                    (x, cy - 12.0 * scale + lift * scale),
                    (x + 14.0 * scale, cy + lift * scale),
                    (x, cy - 4.0 * scale + lift * scale),
                ),
                (64, 176, 210),
            )

    def _at(self, pose: _Pose, dx: float, dy: float) -> tuple[float, float]:
        return pose.x + dx * pose.g, pose.y + dy * pose.g

    def _bottom(self, lane: float) -> tuple[float, float]:
        near_x, near_y, _ = project(lane, _MIN_Z)
        rise = near_y - HORIZON_Y
        if rise <= 1.0:
            return near_x, float(HEIGHT)
        span = (float(HEIGHT) - HORIZON_Y) / rise
        return WIDTH / 2.0 + (near_x - WIDTH / 2.0) * span, float(HEIGHT)

    def _wedge(self, lane_a: float, lane_b: float, color: tuple[int, int, int]) -> None:
        self._paint(
            ((WIDTH / 2.0, float(HORIZON_Y)), self._bottom(lane_a), self._bottom(lane_b)),
            color,
        )

    def _band(
        self,
        lane: float,
        z0: float,
        z1: float,
        half: float,
        color: tuple[int, int, int],
    ) -> None:
        corners = (
            project(lane - half, z0),
            project(lane + half, z0),
            project(lane + half, z1),
            project(lane - half, z1),
        )
        self._paint(tuple((corner[0], corner[1]) for corner in corners), color)

    def _line(
        self,
        start: tuple[float, float],
        end: tuple[float, float],
        color: tuple[int, int, int],
        width: int,
    ) -> None:
        pygame.draw.line(
            self._screen,
            color,
            (int(start[0]), int(start[1])),
            (int(end[0]), int(end[1])),
            width,
        )

    def _paint(self, points: Sequence[tuple[float, float]], color: tuple[int, int, int]) -> None:
        if len(points) < 3:
            return
        pygame.draw.polygon(self._screen, color, _ints(points))

    def _poly(self, points: Sequence[tuple[float, float]], color: tuple[int, int, int]) -> None:
        if len(points) < 3:
            return
        drawn = _ints(points)
        pygame.draw.polygon(self._screen, color, drawn)
        pygame.draw.polygon(self._screen, _dark(color), drawn, _OUTLINE)

    def _fill_disc(self, x: float, y: float, radius: float, color: tuple[int, int, int]) -> None:
        if radius < 0.5:
            return
        pygame.draw.circle(self._screen, color, (int(x), int(y)), max(1, int(radius)))

    def _disc(self, x: float, y: float, radius: float, color: tuple[int, int, int]) -> None:
        if radius < 0.5:
            return
        center = (int(x), int(y))
        r = max(1, int(radius))
        pygame.draw.circle(self._screen, color, center, r)
        if r > 2:
            pygame.draw.circle(self._screen, _dark(color), center, r, _OUTLINE)

    def _fill_oval(
        self,
        x: float,
        y: float,
        w: float,
        h: float,
        color: tuple[int, int, int],
    ) -> None:
        rect = pygame.Rect(int(x - w / 2.0), int(y - h / 2.0), max(1, int(w)), max(1, int(h)))
        pygame.draw.ellipse(self._screen, color, rect)

    def _oval(
        self,
        x: float,
        y: float,
        w: float,
        h: float,
        color: tuple[int, int, int],
        edge: bool = True,
    ) -> None:
        rect = pygame.Rect(int(x - w / 2.0), int(y - h / 2.0), max(1, int(w)), max(1, int(h)))
        pygame.draw.ellipse(self._screen, color, rect)
        if edge and rect.w > 4 and rect.h > 4:
            pygame.draw.ellipse(self._screen, _dark(color), rect, _OUTLINE)

    def _shadow(self, x: float, y: float, rx: float, ry: float) -> None:
        w = max(2, int(rx * 2.0))
        h = max(2, int(ry * 2.0))
        blob = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.ellipse(blob, _SHADOW, blob.get_rect())
        self._screen.blit(blob, (int(x - w / 2.0), int(y - h / 2.0)))

    def _limb(
        self,
        points: Sequence[tuple[float, float]],
        radii: Sequence[float],
        color: tuple[int, int, int],
    ) -> None:
        outline = _dark(color)
        spans = list(zip(points, points[1:], radii))
        for start, end, radius in spans:
            self._capsule(start, end, radius + _OUTLINE, outline)
        for start, end, radius in spans:
            self._capsule(start, end, radius, color)

    def _capsule(
        self,
        start: tuple[float, float],
        end: tuple[float, float],
        radius: float,
        color: tuple[int, int, int],
    ) -> None:
        if radius < 0.6:
            return
        x0, y0 = start
        x1, y1 = end
        dx = x1 - x0
        dy = y1 - y0
        length = math.hypot(dx, dy)
        if length < 0.01:
            self._fill_disc(x0, y0, radius, color)
            return
        px = -dy / length * radius
        py = dx / length * radius
        self._paint(
            (
                (x0 + px, y0 + py),
                (x0 - px, y0 - py),
                (x1 - px, y1 - py),
                (x1 + px, y1 + py),
            ),
            color,
        )
        self._fill_disc(x0, y0, radius, color)
        self._fill_disc(x1, y1, radius, color)
