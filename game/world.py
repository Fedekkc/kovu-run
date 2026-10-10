"""Simulación del recorrido: mueve obstáculos y galletas hacia z=0."""

from __future__ import annotations

import random
from typing import Protocol

from game.events import Event, Feed, Kind
from game.factory import TrackFactory
from game.hitbox import (
    PLAYER_HALF_LANE,
    PLAYER_HALF_Z,
    PLAYER_Z,
    WAGON_HALF_Z,
    Box,
    obstacle_box,
    on_deck,
    overlaps_swept,
    pickup_box,
)
from game.items import Biscuit, Bonus, Obstacle
from game.settings import (
    ACCEL_PER_METER,
    BASE_SPEED,
    BISCUIT,
    BISCUIT_POINTS,
    DESPAWN_Z,
    DOUBLE_JUMP,
    FULL,
    HIGH,
    LOW,
    MAX_SPEED,
    ROCKET,
    SPAWN_Z,
    SUPER_JUMP,
    WAGON,
)

LANES = (0, 1, 2)
START_CURSOR = 36.0
MIN_GAP = 12.0
BASE_GAP = 22.0
GAP_SHRINK_PER_METER = 0.004
LINE_COUNT = 4
LINE_STEP = 3.2
LINE_SPAN = 10.0
JUMP_COUNT = 3
JUMP_STEP = 3.0
JUMP_SPAN = 6.0
WEIGHT_SINGLE = 4
WEIGHT_PAIR = 3
WEIGHT_LINE = 2
WEIGHT_JUMP = 2
WEIGHT_WAGON = 2
WEIGHT_BONUS = 2
BONUS_KINDS = (ROCKET, SUPER_JUMP, DOUBLE_JUMP)
FULL_SHARE_START = 0.16
FULL_SHARE_END = 0.30
FULL_RAMP_METERS = 5000.0
WAGON_CARS = 4
WAGON_STEP = WAGON_HALF_Z * 2.0
WAGON_SPAN = WAGON_CARS * WAGON_STEP + 4.0
WAGON_BISCUITS = 6
WAGON_BISCUIT_STEP = WAGON_STEP * 0.7


class _Player(Protocol):
    speed_scale: float
    pickup_span: float
    spawn_luck: int

    def hitbox(self) -> Box: ...

    def grant(self, kind: str) -> None: ...


class World:
    """Camino de 3 carriles. El perro lo controla otro módulo."""

    feed: Feed
    obstacles: list[Obstacle]
    biscuits: list[Biscuit]
    bonuses: list[Bonus]
    distance: float
    biscuits_taken: int
    speed: float
    game_over: bool
    catch_timer: float
    cursor: float

    def __init__(self, rng: random.Random | None = None) -> None:
        self.rng = random.Random() if rng is None else rng
        self.factory = TrackFactory()
        self.reset()

    def reset(self) -> None:
        self.feed = Feed()
        self.obstacles = []
        self.biscuits = []
        self.bonuses = []
        self.distance = 0.0
        self.biscuits_taken = 0
        self.speed = BASE_SPEED
        self.game_over = False
        self.catch_timer = 0.0
        self.cursor = START_CURSOR
        self._fill()

    def update(self, dt: float, player: _Player) -> None:
        if self.game_over:
            self.catch_timer += dt
            return

        self.speed = min(MAX_SPEED, BASE_SPEED + ACCEL_PER_METER * self.distance)
        dz = self.speed * player.speed_scale * dt
        self.distance += dz
        self._advance(dz)
        self._drop()
        self._fill(player)
        self._collect(player, dz)
        self._collide(player, dz)

    @property
    def display_score(self) -> int:
        return int(self.distance) + self.biscuits_taken * BISCUIT_POINTS

    def _advance(self, dz: float) -> None:
        self.cursor -= dz
        for obstacle in self.obstacles:
            obstacle.z -= dz
        for biscuit in self.biscuits:
            biscuit.z -= dz
        for bonus in self.bonuses:
            bonus.z -= dz

    def _drop(self) -> None:
        self.obstacles = [item for item in self.obstacles if item.z >= DESPAWN_Z]
        self.biscuits = [
            item for item in self.biscuits if not item.taken and item.z >= DESPAWN_Z
        ]
        self.bonuses = [
            item for item in self.bonuses if not item.taken and item.z >= DESPAWN_Z
        ]

    def _fill(self, player: _Player | None = None) -> None:
        while self.cursor < SPAWN_Z:
            span = self._place(self.cursor, player)
            self.cursor += self._gap() + span

    def _gap(self) -> float:
        return max(MIN_GAP, BASE_GAP - self.distance * GAP_SHRINK_PER_METER)

    def support_at(self, lane: float) -> float:
        """Altura del techo bajo Kovu, o 0 si corre por el piso."""
        top = 0.0
        for obstacle in self.obstacles:
            if obstacle.kind != WAGON:
                continue
            box = obstacle_box(obstacle.kind, obstacle.lane, obstacle.z, self.distance)
            if abs(lane - box.lane) >= PLAYER_HALF_LANE + box.half_lane:
                continue
            if abs(PLAYER_Z - box.z) >= PLAYER_HALF_Z + box.half_z:
                continue
            top = max(top, box.top)
        return top

    def _place(self, z: float, player: _Player | None) -> float:
        luck = 0 if player is None else max(0, player.spawn_luck)
        place = self.rng.choices(
            (self._single, self._pair, self._line, self._jump, self._wagon, self._bonus),
            weights=(
                WEIGHT_SINGLE,
                WEIGHT_PAIR,
                WEIGHT_LINE + luck,
                WEIGHT_JUMP + luck,
                WEIGHT_WAGON + luck,
                WEIGHT_BONUS,
            ),
            k=1,
        )[0]
        return place(z)

    def _single(self, z: float) -> float:
        self._put(self._kind(), self._lane(), z)
        return 0.0

    def _pair(self, z: float) -> float:
        for lane in self.rng.sample(LANES, 2):
            self._put(self._kind(), lane, z)
        return 0.0

    def _line(self, z: float) -> float:
        lane = self._lane()
        for step in range(LINE_COUNT):
            self._put(BISCUIT, lane, z + step * LINE_STEP)
        return LINE_SPAN

    def _jump(self, z: float) -> float:
        lane = self._lane()
        self._put(LOW, lane, z)
        for step in range(JUMP_COUNT):
            self._put(BISCUIT, lane, z + step * JUMP_STEP)
        return JUMP_SPAN

    def _wagon(self, z: float) -> float:
        lane = self._lane()
        for car in range(WAGON_CARS):
            self._put(WAGON, lane, z + car * WAGON_STEP)
        for step in range(WAGON_BISCUITS):
            self._put(BISCUIT, lane, z + 1.2 + step * WAGON_BISCUIT_STEP)
        return WAGON_SPAN

    def _bonus(self, z: float) -> float:
        self._put(self.rng.choice(BONUS_KINDS), self._lane(), z)
        return 0.0

    def _put(self, kind: str, lane: int, z: float) -> None:
        item = self.factory.create(kind, lane, z)
        if isinstance(item, Obstacle):
            self.obstacles.append(item)
            return
        if isinstance(item, Biscuit):
            self.biscuits.append(item)
            return
        self.bonuses.append(item)

    def _lane(self) -> int:
        return self.rng.choice(LANES)

    def _kind(self) -> str:
        ramp = min(1.0, self.distance / FULL_RAMP_METERS)
        full = FULL_SHARE_START + (FULL_SHARE_END - FULL_SHARE_START) * ramp
        side = (1.0 - full) / 2.0
        return self.rng.choices((LOW, HIGH, FULL), weights=(side, side, full), k=1)[0]

    def _collect(self, player: _Player, dz: float) -> None:
        body = player.hitbox()
        for biscuit in self.biscuits:
            if biscuit.taken:
                continue
            box = pickup_box(biscuit.lane, biscuit.z, player.pickup_span)
            if overlaps_swept(body, box, biscuit.z + dz):
                biscuit.taken = True
                self.biscuits_taken += 1
                self.feed.emit(Event(Kind.BISCUIT, biscuit.lane, biscuit.z))
        for bonus in self.bonuses:
            if bonus.taken:
                continue
            box = pickup_box(bonus.lane, bonus.z, player.pickup_span)
            if overlaps_swept(body, box, bonus.z + dz):
                bonus.taken = True
                player.grant(bonus.kind)
                self.feed.emit(Event(Kind.BONUS, bonus.lane, bonus.z, bonus.kind))

    def _collide(self, player: _Player, dz: float) -> None:
        body = player.hitbox()
        for obstacle in self.obstacles:
            box = obstacle_box(obstacle.kind, obstacle.lane, obstacle.z, self.distance)
            if not overlaps_swept(body, box, obstacle.z + dz):
                continue
            if obstacle.kind == WAGON and on_deck(body, box):
                continue
            self.game_over = True
            self.catch_timer = 0.0
            self.feed.emit(Event(Kind.CRASH, obstacle.lane, obstacle.z))
            return
