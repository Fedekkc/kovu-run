"""Simulación del recorrido: mueve obstáculos y galletas hacia z=0."""

from __future__ import annotations

import random
from collections import deque
from typing import Protocol

from game.cycle import mood_at
from game.events import Event, Feed, Kind
from game.factory import TrackFactory
from game.hitbox import (
    PLAYER_HALF_LANE,
    PLAYER_HALF_Z,
    PLAYER_Z,
    WAGON_HALF_Z,
    WAGON_PX,
    Box,
    obstacle_box,
    on_deck,
    overlaps_swept,
    pickup_box,
    px_to_units,
)
from game.items import Biscuit, Bonus, Obstacle
from game.settings import (
    ACCEL_PER_METER,
    BASE_SPEED,
    BISCUIT,
    BISCUIT_POINTS,
    COMBO_WINDOW,
    COMBO_X2_AT,
    COMBO_X3_AT,
    DESPAWN_Z,
    DOUBLE_JUMP,
    FULL,
    HIGH,
    LATE_ACCEL_PER_METER,
    LATE_SPEED_FROM,
    LOW,
    MAX_SPEED,
    MODE_LAVA,
    MODE_NORMAL,
    ROCKET,
    SPAWN_Z,
    SUPER_JUMP,
    WAGON,
    combo_mult_for,
    heat_at,
)
from game.story import CHASE_BOOST_TIME, STORM_PRESS_TIME

LANES = (0, 1, 2)
START_CURSOR = 36.0
MIN_GAP = 10.0
BASE_GAP = 24.0
GAP_SHRINK_PER_METER = 0.0032
LAVA_GAP_BASE = 10.5
LAVA_GAP_MIN = 7.5
LAVA_GAP_SHRINK = 0.0015
LINE_COUNT = 4
LINE_STEP = 3.2
LINE_SPAN = 10.0
JUMP_COUNT = 3
JUMP_STEP = 3.0
JUMP_SPAN = 6.0
BURST_STEP = 2.4
BURST_SPAN = 4.8
WEIGHT_SINGLE = 5
WEIGHT_PAIR = 3
WEIGHT_TRIPLE = 1
WEIGHT_GATE = 1
WEIGHT_LINE = 2
WEIGHT_JUMP = 2
WEIGHT_WAGON = 2
WEIGHT_BONUS = 1
WEIGHT_BURST = 1
BONUS_KINDS = (ROCKET, SUPER_JUMP, DOUBLE_JUMP)
FULL_SHARE_START = 0.14
FULL_SHARE_END = 0.38
FULL_RAMP_METERS = 7000.0
PRESSURE_METERS = 5500.0
WAGON_CARS = 4
WAGON_EXPRESS_CARS = 6
WAGON_STEP = WAGON_HALF_Z * 2.0
WAGON_SPAN = WAGON_CARS * WAGON_STEP + 4.0
# Una galleta por vagón, centrada en el techo (no un chorro a lo largo del tren).
WAGON_DECK = px_to_units(WAGON_PX)
LAVA_FLOOR = 0.08


class _Player(Protocol):
    speed_scale: float
    pickup_span: float
    spawn_luck: int
    height: float
    floor: float
    jumping: bool
    rocket_time: float

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
    biscuit_points: int
    combo: int
    combo_max: int
    combo_mult: int
    speed: float
    game_over: bool
    catch_timer: float
    cursor: float
    chase_boost: float
    mode: str
    mutator: str

    def __init__(self, rng: random.Random | None = None) -> None:
        self.rng = random.Random() if rng is None else rng
        self.factory = TrackFactory()
        self.mode = MODE_NORMAL
        self.mutator = ""
        self._queue: deque[str] = deque()
        self._storm_press = 0.0
        self._combo_timer = 0.0
        self._biscuit_scale = 1
        self.reset()

    def configure(self, mode: str = MODE_NORMAL, seed: int | None = None) -> None:
        if seed is not None:
            self.rng.seed(seed)
        self.mode = mode if mode in (MODE_NORMAL, MODE_LAVA) else MODE_NORMAL
        self.mutator = self.mode
        self._biscuit_scale = 1

    @property
    def lava(self) -> bool:
        return self.mode == MODE_LAVA

    def reset(self) -> None:
        self.feed = Feed()
        self.obstacles = []
        self.biscuits = []
        self.bonuses = []
        self.distance = 0.0
        self.biscuits_taken = 0
        self.biscuit_points = 0
        self.combo = 0
        self.combo_max = 0
        self.combo_mult = 1
        self.combo_mult_max = 1
        self.speed = BASE_SPEED
        self.game_over = False
        self.catch_timer = 0.0
        self.cursor = START_CURSOR
        self.chase_boost = 0.0
        self._queue.clear()
        self._storm_press = 0.0
        self._combo_timer = 0.0
        if self.lava:
            self._seed_lava_start()
        else:
            self._fill()

    def queue_pattern(self, name: str) -> None:
        self._queue.append(name)

    def apply_setpiece(self, name: str) -> None:
        if name == "chase":
            self.chase_boost = CHASE_BOOST_TIME
            return
        if name == "wagon":
            self.queue_pattern("wagon_express")
            return
        if name == "storm" and not self.lava:
            self._storm_press = STORM_PRESS_TIME

    def update(self, dt: float, player: _Player) -> None:
        if self.game_over:
            self.catch_timer += dt
            return

        if self.chase_boost > 0.0:
            self.chase_boost = max(0.0, self.chase_boost - dt)
        if self._storm_press > 0.0:
            self._storm_press = max(0.0, self._storm_press - dt)
        if self.combo > 0:
            self._combo_timer -= dt
            if self._combo_timer <= 0.0:
                self.combo = 0
                self.combo_mult = 1

        self.speed = self._speed_at(self.distance)
        dz = self.speed * player.speed_scale * dt
        self.distance += dz
        self._advance(dz)
        self._drop()
        self._fill(player)
        self._collect(player, dz)
        self._collide(player, dz)

    def _speed_at(self, distance: float) -> float:
        pace = BASE_SPEED + ACCEL_PER_METER * distance
        if distance > LATE_SPEED_FROM:
            pace += LATE_ACCEL_PER_METER * (distance - LATE_SPEED_FROM)
        return min(MAX_SPEED, pace)

    @property
    def heat(self) -> float:
        return heat_at(self.distance)

    @property
    def pressure(self) -> float:
        """0→1: cuánto aprieta el spawner late-game."""
        return min(1.0, max(0.0, self.distance / PRESSURE_METERS))

    @property
    def display_score(self) -> int:
        return int(self.distance * self.heat) + self.biscuit_points

    @property
    def combo_next(self) -> int:
        """Galletas para el próximo multiplicador (0 si ya está al tope)."""
        if self.combo_mult >= 3:
            return 0
        if self.combo_mult >= 2:
            return COMBO_X3_AT
        return COMBO_X2_AT

    @property
    def chase_pressure(self) -> float:
        if self.chase_boost <= 0.0:
            return 0.0
        return min(1.0, self.chase_boost / CHASE_BOOST_TIME)

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

    def _mood(self):
        return mood_at(self.distance)

    def _gap(self) -> float:
        if self.lava:
            return max(LAVA_GAP_MIN, LAVA_GAP_BASE - self.distance * LAVA_GAP_SHRINK)
        mood = self._mood()
        shrink = GAP_SHRINK_PER_METER
        floor = MIN_GAP
        if mood.rain > 0.5 or self._storm_press > 0.0:
            shrink *= 1.25
            floor = max(9.5, MIN_GAP - 1.5)
        gap = max(floor, BASE_GAP - self.distance * shrink)
        if mood.rain > 0.5 or self._storm_press > 0.0:
            gap *= 0.88
        return gap

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

    def _seed_lava_start(self) -> None:
        """Tren inicial bajo Kovu para no caer a la lava al arrancar."""
        lane = 1
        cars = 5
        z0 = 0.5
        for car in range(cars):
            self._put(WAGON, lane, z0 + car * WAGON_STEP)
            self._biscuit(lane, z0 + car * WAGON_STEP, WAGON_DECK)
        self.cursor = z0 + cars * WAGON_STEP + self._gap()
        self._fill()

    def _place(self, z: float, player: _Player | None) -> float:
        if self._queue:
            return self._run_pattern(self._queue.popleft(), z)
        if self.lava:
            express = self.rng.random() < min(0.45, 0.22 + 0.2 * self.pressure)
            return self._wagon(z, express=express)
        luck = 0 if player is None else max(0, min(4, player.spawn_luck))
        mood = self._mood()
        night = mood.night
        storm = 1.0 if (mood.rain > 0.5 or self._storm_press > 0.0) else 0.0
        press = self.pressure
        weights = [
            max(1, WEIGHT_SINGLE - int(3 * press)),
            WEIGHT_PAIR + int(2 * storm) + int(2 * press),
            WEIGHT_TRIPLE + int(2 * storm) + int(night > 0.6) + int(3 * press),
            WEIGHT_GATE + int(night > 0.5) + int(2 * press),
            WEIGHT_LINE + luck,
            WEIGHT_JUMP + luck,
            WEIGHT_WAGON + luck + int(press > 0.55),
            WEIGHT_BONUS,
            WEIGHT_BURST,
        ]
        place = self.rng.choices(
            (
                self._single,
                self._pair,
                self._triple,
                self._gate,
                self._line,
                self._jump,
                self._wagon,
                self._bonus,
                self._burst,
            ),
            weights=weights,
            k=1,
        )[0]
        return place(z)

    def _run_pattern(self, name: str, z: float) -> float:
        if name == "wagon" or name == "wagon_express":
            return self._wagon(z, express=name == "wagon_express")
        if self.lava:
            return self._wagon(z)
        if name == "triple":
            return self._triple(z)
        if name == "gate":
            return self._gate(z)
        if name == "burst":
            return self._burst(z)
        if name == "bonus":
            return self._bonus(z)
        return self._single(z)

    def _single(self, z: float) -> float:
        self._put(self._kind(), self._lane(), z)
        return 0.0

    def _pair(self, z: float) -> float:
        for lane in self.rng.sample(LANES, 2):
            self._put(self._kind(), lane, z)
        return 0.0

    def _triple(self, z: float) -> float:
        lanes = list(LANES)
        self.rng.shuffle(lanes)
        kinds = [self._kind() for _ in range(3)]
        if all(kind == FULL for kind in kinds):
            kinds[self.rng.randrange(3)] = self.rng.choice((LOW, HIGH))
        for lane, kind in zip(lanes, kinds):
            self._put(kind, lane, z)
        return 0.0

    def _gate(self, z: float) -> float:
        left, right = self.rng.sample(LANES, 2)
        self._put(LOW, left, z)
        self._put(HIGH, right, z)
        return 0.0

    def _line(self, z: float) -> float:
        lane = self._lane()
        for step in range(LINE_COUNT):
            self._biscuit(lane, z + step * LINE_STEP)
        return LINE_SPAN

    def _jump(self, z: float) -> float:
        lane = self._lane()
        self._put(LOW, lane, z)
        for step in range(JUMP_COUNT):
            self._biscuit(lane, z + step * JUMP_STEP)
        return JUMP_SPAN

    def _wagon(self, z: float, express: bool = False) -> float:
        lane = self._lane()
        cars = WAGON_EXPRESS_CARS if express else WAGON_CARS
        if self.lava:
            cars = self.rng.randint(3, 6 if express else 5)
        span = cars * WAGON_STEP + 4.0
        for car in range(cars):
            car_z = z + car * WAGON_STEP
            self._put(WAGON, lane, car_z)
            self._biscuit(lane, car_z, WAGON_DECK)
        return span

    def _bonus(self, z: float) -> float:
        self._put(self.rng.choice(BONUS_KINDS), self._lane(), z)
        return 0.0

    def _burst(self, z: float) -> float:
        lane = self._lane()
        self._put(self.rng.choice(BONUS_KINDS), lane, z)
        other = self.rng.choice([item for item in LANES if item != lane] or list(LANES))
        self._put(self.rng.choice(BONUS_KINDS), other, z + BURST_STEP)
        self._biscuit(lane, z + BURST_STEP * 0.5)
        return BURST_SPAN

    def _biscuit(self, lane: int, z: float, height: float = 0.0) -> None:
        item = self.factory.create(BISCUIT, lane, z)
        if isinstance(item, Biscuit):
            item.height = height
            self.biscuits.append(item)

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
        mood = self._mood()
        if mood.night > 0.5:
            full = min(0.44, full + 0.05 * mood.night)
        if mood.rain > 0.5 or self._storm_press > 0.0:
            full = min(0.48, full + 0.07)
        side = (1.0 - full) / 2.0
        return self.rng.choices((LOW, HIGH, FULL), weights=(side, side, full), k=1)[0]

    def _collect(self, player: _Player, dz: float) -> None:
        body = player.hitbox()
        for biscuit in self.biscuits:
            if biscuit.taken:
                continue
            box = pickup_box(biscuit.lane, biscuit.z, player.pickup_span, biscuit.height)
            if overlaps_swept(body, box, biscuit.z + dz):
                biscuit.taken = True
                self.biscuits_taken += 1
                self.combo += 1
                self.combo_max = max(self.combo_max, self.combo)
                self.combo_mult = combo_mult_for(self.combo)
                self.combo_mult_max = max(self.combo_mult_max, self.combo_mult)
                points = BISCUIT_POINTS * self.combo_mult * self._biscuit_scale
                self.biscuit_points += points
                self._combo_timer = COMBO_WINDOW
                self.feed.emit(Event(Kind.BISCUIT, biscuit.lane, biscuit.z, str(points)))
        if self.lava:
            return
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
            self._crash(obstacle.lane, obstacle.z)
            return

    def _lava_floor(self, player: _Player) -> None:
        if not self.lava:
            return
        if player.jumping or player.rocket_time > 0.0:
            return
        if player.height > LAVA_FLOOR or player.floor > LAVA_FLOOR:
            return
        self._crash(player.hitbox().lane, PLAYER_Z)

    def _crash(self, lane: float, z: float) -> None:
        self.game_over = True
        self.catch_timer = 0.0
        self.combo = 0
        self.combo_mult = 1
        self.feed.emit(Event(Kind.CRASH, lane, z))
