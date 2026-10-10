"""Input and motion for the Kovu runner."""

from __future__ import annotations

import math

import pygame

from game.events import Event, Feed, Kind
from game.hitbox import ROCKET_FLOOR, player_hitbox
from game.settings import DOUBLE_JUMP, PLAYER_DRAW_Z, ROCKET, SUPER_JUMP
from game.upgrades import POWER_LABEL, RunMods

_LANE_MIN = 0
_LANE_MAX = 2
_LANE_START = 1


def _smoothstep(t: float) -> float:
    return t * t * (3.0 - 2.0 * t)


def _clamp_lane(lane: int) -> int:
    return min(_LANE_MAX, max(_LANE_MIN, lane))


class Player:
    lane: int
    lane_pos: float
    height: float
    jumping: bool
    sliding: bool
    alive: bool
    run_time: float

    def __init__(self) -> None:
        self.mods = RunMods()
        self._switch_from = float(_LANE_START)
        self._switch_t = 0.0
        self._jump_t = 0.0
        self._slide_t = 0.0
        self._jump_limit = self.mods.jump_time
        self._jump_scale = self.mods.jump_scale
        self.reset()

    def equip(self, mods: RunMods) -> None:
        self.mods = mods

    def reset(self) -> None:
        self.lane = _LANE_START
        self.lane_pos = float(_LANE_START)
        self.height = 0.0
        self.jumping = False
        self.sliding = False
        self.alive = True
        self.run_time = 0.0
        self._switch_from = float(_LANE_START)
        self._switch_t = 0.0
        self._jump_t = 0.0
        self._slide_t = 0.0
        self._jump_limit = self.mods.jump_time
        self._jump_scale = self.mods.jump_scale
        self._powered_jump = False
        self.rocket_time = 0.0
        self.super_time = 0.0
        self.double_time = 0.0
        self.extra_jumps = 0
        self.flipping = False
        self.flip_time = 0.0
        self.feed = Feed()

    @property
    def powered(self) -> bool:
        return self.jumping and self._powered_jump

    @property
    def super_armed(self) -> bool:
        return self.super_time > 0.0

    @property
    def charge(self) -> float:
        """What is left of the active hold window, from 1 to 0."""
        if self.rocket_time > 0.0 and self.mods.rocket_time > 0.0:
            return min(1.0, self.rocket_time / self.mods.rocket_time)
        if self.super_time > 0.0 and self.mods.super_hold > 0.0:
            return min(1.0, self.super_time / self.mods.super_hold)
        if self.double_time > 0.0 and self.mods.double_hold > 0.0:
            return min(1.0, self.double_time / self.mods.double_hold)
        return 0.0

    def _emit(self, kind: Kind) -> None:
        self.feed.emit(Event(kind, self.lane_pos, PLAYER_DRAW_Z))

    def grant(self, kind: str) -> None:
        if kind == ROCKET:
            self.rocket_time = self.mods.rocket_time
            self.jumping = False
            self.sliding = False
            return
        if kind == SUPER_JUMP:
            self.super_time = self.mods.super_hold
            return
        if kind == DOUBLE_JUMP:
            self.extra_jumps = 1
            self.double_time = self.mods.double_hold

    @property
    def speed_scale(self) -> float:
        if self.rocket_time > 0.0:
            return self.mods.rocket_speed
        return 1.0

    @property
    def pickup_span(self) -> float:
        return self.mods.pickup_span

    @property
    def spawn_luck(self) -> int:
        return self.mods.luck_weight

    @property
    def power_label(self) -> str:
        names: list[str] = []
        if self.rocket_time > 0.0:
            names.append(POWER_LABEL[ROCKET])
        if self.super_armed or self._powered_jump:
            names.append(POWER_LABEL[SUPER_JUMP])
        if self.extra_jumps > 0 or self.double_time > 0.0:
            names.append(POWER_LABEL[DOUBLE_JUMP])
        return " · ".join(names)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return
        key = event.key
        if key in (pygame.K_LEFT, pygame.K_a):
            self._set_lane(_clamp_lane(self.lane - 1))
            return
        if key in (pygame.K_RIGHT, pygame.K_d):
            self._set_lane(_clamp_lane(self.lane + 1))
            return
        if key in (pygame.K_UP, pygame.K_w, pygame.K_SPACE):
            self._begin_jump()
            return
        if key in (pygame.K_DOWN, pygame.K_s):
            self._begin_slide()

    def update(self, dt: float) -> None:
        self.run_time += dt
        self._advance_lane(dt)
        self._tick_holds(dt)
        if self.rocket_time > 0.0:
            self.rocket_time = max(0.0, self.rocket_time - dt)
            if self.rocket_time <= 0.0:
                self._emit(Kind.LAND)
            self.jumping = False
            self.sliding = False
            self._jump_t = 0.0
            self._slide_t = 0.0
            self._powered_jump = False
            self.flipping = False
            self.height = ROCKET_FLOOR if self.rocket_time > 0.0 else 0.0
            return
        self._advance_jump(dt)
        self._advance_slide(dt)

    def _tick_holds(self, dt: float) -> None:
        """La ventana corre siempre; al vencerse se pierde el poder, no al usarlo."""
        if self.super_time > 0.0:
            self.super_time = max(0.0, self.super_time - dt)
        if self.double_time > 0.0:
            self.double_time = max(0.0, self.double_time - dt)
            if self.double_time <= 0.0:
                self.extra_jumps = 0

    def hitbox(self):
        return player_hitbox(self)

    @property
    def collision_lane(self) -> int:
        return _clamp_lane(round(self.lane_pos))

    def _set_lane(self, lane: int) -> None:
        if lane == self.lane:
            return
        self._switch_from = self.lane_pos
        self._switch_t = 0.0
        self.lane = lane

    def _advance_lane(self, dt: float) -> None:
        limit = self.mods.lane_switch
        if limit <= 0.0:
            self.lane_pos = float(self.lane)
            return
        self._switch_t = min(self._switch_t + dt, limit)
        blend = _smoothstep(self._switch_t / limit)
        self.lane_pos = self._switch_from + (float(self.lane) - self._switch_from) * blend
        if self._switch_t >= limit:
            self.lane_pos = float(self.lane)

    def _begin_jump(self) -> None:
        if self.rocket_time > 0.0 or self.sliding:
            return
        if self.jumping:
            if self.extra_jumps <= 0:
                return
            self.extra_jumps -= 1
            self._jump_scale = max(self._jump_scale, self.mods.double_jump_scale)
            self._jump_limit = max(self._jump_limit, self.mods.double_jump_time)
            ratio = min(1.0, self.height / max(0.01, self._jump_scale))
            self._jump_t = math.asin(ratio) * self._jump_limit / math.pi
            self.flipping = True
            self.flip_time = 0.0
            self._emit(Kind.JUMP)
            return
        powered = self.super_time > 0.0
        self._powered_jump = powered
        self._jump_limit = self.mods.super_jump_time if powered else self.mods.jump_time
        self._jump_scale = self.mods.super_jump_scale if powered else self.mods.jump_scale
        if self.double_time > 0.0:
            self.extra_jumps = 1
        self.jumping = True
        self._jump_t = 0.0
        self.height = 0.0
        self._emit(Kind.JUMP)

    def _advance_jump(self, dt: float) -> None:
        if not self.jumping:
            return
        self._jump_t += dt
        self.flip_time += dt
        if self._jump_t >= self._jump_limit:
            self.jumping = False
            self.height = 0.0
            self._powered_jump = False
            self.flipping = False
            self._emit(Kind.LAND)
            self._jump_limit = self.mods.jump_time
            self._jump_scale = self.mods.jump_scale
            if self.double_time > 0.0:
                self.extra_jumps = 1
            return
        self.height = math.sin(math.pi * self._jump_t / self._jump_limit) * self._jump_scale

    def _begin_slide(self) -> None:
        if self.rocket_time > 0.0 or self.sliding or self.jumping:
            return
        self.sliding = True
        self._slide_t = 0.0

    def _advance_slide(self, dt: float) -> None:
        if not self.sliding:
            return
        self._slide_t += dt
        if self._slide_t >= self.mods.slide_time:
            self.sliding = False
