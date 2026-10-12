"""Partículas, textos flotantes, sacudón y congelado: la respuesta visual a los eventos."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Protocol

import pygame

from game.events import Event, Feed, Kind
from game.palette import Tone, tone
from game.pixelfont import default_font
from game.projection import kovu_feet, project
from game.settings import BISCUIT_POINTS, DOUBLE_JUMP, HORIZON_Y, MAX_SPEED, ROCKET, SUPER_JUMP, WIDTH

COPY_POINTS = "+{points}"
COPY_BONUS = {
    ROCKET: "¡Cohete!",
    SUPER_JUMP: "¡Super salto!",
    DOUBLE_JUMP: "¡Doble salto!",
}

SPARK_GOLD = (Tone.CREAM, Tone.SUN, Tone.TAN_SHINE, Tone.TAN)
FLAME = (Tone.CREAM, Tone.SUN, Tone.CORAL, Tone.GERANIUM)
SMOKE = (Tone.CREAM, Tone.WALK_LIGHT, Tone.WALK, Tone.STONE)
DUST = (Tone.WALK_LIGHT, Tone.WALK, Tone.CURB_DARK)
STARS = (Tone.CREAM, Tone.SUN, Tone.SUN, Tone.CORAL)
BONUS_RAMPS = {
    ROCKET: FLAME,
    SUPER_JUMP: (Tone.CREAM, Tone.SUN, Tone.NEON_PINK, Tone.ROSE),
    DOUBLE_JUMP: (Tone.CREAM, Tone.NEON_CYAN, Tone.BLUE_LIGHT, Tone.BLUE),
}
# Coral = cohete, rosa = super salto, cian = doble salto. Lo usan fx y el aura del render.
POWER_GLOW = {ROCKET: Tone.CORAL, SUPER_JUMP: Tone.NEON_PINK, DOUBLE_JUMP: Tone.NEON_CYAN}
BONUS_TONES = POWER_GLOW

STALL_TIME = 0.14
SHAKE_TIME = 0.45
SHAKE_PX = 16.0
FLASH_TIME = 0.18
TEXT_SCALE = 3
TEXT_LIFE = 0.85
TEXT_RISE = 80.0
EXHAUST_EVERY = 0.018
SPEED_FROM = 52.0
SPEED_LINES = 26
LINE_SPAN = 560.0
LINE_START = 380.0
LINE_PACE = 1100.0
GOLDEN = 2.399963
GRID = 2


class _WorldView(Protocol):
    feed: Feed
    speed: float


class _PlayerView(Protocol):
    feed: Feed
    lane_pos: float
    height: float
    rocket_time: float


class _AudioView(Protocol):
    def event(self, event: Event) -> None: ...


@dataclass
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    life: float
    ramp: tuple[Tone, ...]
    size: float
    gravity: float = 0.0
    grow: float = 0.0
    age: float = 0.0


@dataclass
class Floater:
    text: str
    x: float
    y: float
    color: Tone
    age: float = 0.0


class Effects:
    def __init__(self, seed: int | None = None) -> None:
        self._rng = random.Random(seed)
        self.reset()

    def reset(self) -> None:
        self.particles: list[Particle] = []
        self.floaters: list[Floater] = []
        self._shake = 0.0
        self._flash = 0.0
        self._stall = 0.0
        self._exhaust = 0.0
        self._speed = 0.0
        self.offset = (0, 0)

    @property
    def flash(self) -> float:
        return self._flash / FLASH_TIME

    def stall(self, dt: float) -> float:
        """Hit-stop: the world holds still for a beat after a crash."""
        if self._stall <= 0.0:
            return dt
        self._stall = max(0.0, self._stall - dt)
        return 0.0

    def update(
        self,
        dt: float,
        world: _WorldView,
        player: _PlayerView,
        audio: _AudioView | None = None,
    ) -> None:
        for event in world.feed.drain() + player.feed.drain():
            if audio is not None:
                audio.event(event)
            self._react(event, player)
        for particle in self.particles:
            particle.age += dt
            particle.vy += particle.gravity * dt
            particle.x += particle.vx * dt
            particle.y += particle.vy * dt
        self.particles = [particle for particle in self.particles if particle.age < particle.life]
        for floater in self.floaters:
            floater.age += dt
        self.floaters = [floater for floater in self.floaters if floater.age < TEXT_LIFE]
        self._flash = max(0.0, self._flash - dt)
        self._shake = max(0.0, self._shake - dt)
        self.offset = self._jolt()
        rocket = player.rocket_time > 0.0
        if rocket:
            self._trail(dt, player)
        ramp = (world.speed - SPEED_FROM) / (MAX_SPEED - SPEED_FROM)
        self._speed = 1.0 if rocket else min(1.0, max(0.0, ramp))

    def draw(self, screen: pygame.Surface, time: float) -> None:
        self._draw_lines(screen, time)
        for particle in self.particles:
            step = min(len(particle.ramp) - 1, int(particle.age / particle.life * len(particle.ramp)))
            size = max(GRID, int(particle.size + particle.grow * particle.age) // GRID * GRID)
            x = int(particle.x) // GRID * GRID
            y = int(particle.y) // GRID * GRID
            screen.fill(tone(particle.ramp[step]), (x - size // 2, y - size // 2, size, size))
        font = default_font()
        for floater in self.floaters:
            if floater.age > TEXT_LIFE * 0.7 and int(floater.age * 20) % 2:
                continue
            image = font.render(floater.text, tone(floater.color), TEXT_SCALE, tone(Tone.INK))
            rise = TEXT_RISE * floater.age / TEXT_LIFE
            screen.blit(image, (int(floater.x - image.get_width() / 2), int(floater.y - rise)))

    def _react(self, event: Event, player: _PlayerView) -> None:
        if event.kind == Kind.BISCUIT:
            x, y = self._at_body(event, player)
            self._burst(x, y, 10, SPARK_GOLD, (180.0, 320.0), 4.0)
            try:
                points = int(event.tag) if event.tag else BISCUIT_POINTS
            except ValueError:
                points = BISCUIT_POINTS
            self.floaters.append(Floater(COPY_POINTS.format(points=points), x, y - 30.0, Tone.SUN))
            return
        if event.kind == Kind.BONUS:
            x, y = self._at_body(event, player)
            self._burst(x, y, 24, BONUS_RAMPS.get(event.tag, SPARK_GOLD), (220.0, 420.0), 6.0)
            label = COPY_BONUS.get(event.tag)
            if label is not None:
                self.floaters.append(Floater(label, x, y - 40.0, BONUS_TONES.get(event.tag, Tone.SUN)))
            return
        if event.kind == Kind.CRASH:
            x, feet, scale = kovu_feet(player.lane_pos, player.height)
            self._burst(x, feet - 160.0 * scale, 12, STARS, (160.0, 300.0), 6.0, gravity=520.0)
            self._stall = STALL_TIME
            self._shake = SHAKE_TIME
            self._flash = FLASH_TIME
            return
        x, ground, scale = kovu_feet(event.lane, 0.0)
        count = 8 if event.kind == Kind.LAND else 4
        for _ in range(count):
            side = self._rng.choice((-1.0, 1.0))
            self.particles.append(
                Particle(
                    x + side * self._rng.uniform(10.0, 34.0) * scale,
                    ground - self._rng.uniform(0.0, 8.0),
                    side * self._rng.uniform(50.0, 160.0),
                    -self._rng.uniform(20.0, 70.0),
                    self._rng.uniform(0.3, 0.5),
                    DUST,
                    8.0 * scale,
                    gravity=220.0,
                    grow=14.0,
                )
            )

    def _at_body(self, event: Event, player: _PlayerView) -> tuple[float, float]:
        x, _, scale = project(event.lane, event.z)
        _, feet, _ = kovu_feet(player.lane_pos, player.height)
        return x, feet - 80.0 * scale

    def _burst(
        self,
        x: float,
        y: float,
        count: int,
        ramp: tuple[Tone, ...],
        speed: tuple[float, float],
        size: float,
        gravity: float = 640.0,
    ) -> None:
        for index in range(count):
            angle = math.tau * index / count + self._rng.uniform(-0.3, 0.3)
            pace = self._rng.uniform(*speed)
            self.particles.append(
                Particle(
                    x,
                    y,
                    math.cos(angle) * pace,
                    math.sin(angle) * pace - 120.0,
                    self._rng.uniform(0.35, 0.6),
                    ramp,
                    size,
                    gravity=gravity,
                )
            )

    def _trail(self, dt: float, player: _PlayerView) -> None:
        self._exhaust += dt
        x, feet, scale = kovu_feet(player.lane_pos, player.height)
        while self._exhaust >= EXHAUST_EVERY:
            self._exhaust -= EXHAUST_EVERY
            for side in (-1.0, 1.0):
                nozzle_x = x + side * 36.0 * scale + self._rng.uniform(-4.0, 4.0)
                nozzle_y = feet - 40.0 * scale
                self.particles.append(
                    Particle(nozzle_x, nozzle_y, self._rng.uniform(-30.0, 30.0), self._rng.uniform(260.0, 360.0),
                             0.5, SMOKE, 8.0 * scale, gravity=-180.0, grow=34.0)
                )
                self.particles.append(
                    Particle(nozzle_x, nozzle_y, self._rng.uniform(-60.0, 60.0), self._rng.uniform(380.0, 520.0),
                             0.22, FLAME, 4.0)
                )

    def _jolt(self) -> tuple[int, int]:
        if self._shake <= 0.0:
            return (0, 0)
        amp = SHAKE_PX * self._shake / SHAKE_TIME
        dx = int(self._rng.uniform(-amp, amp)) // GRID * GRID
        dy = int(self._rng.uniform(-amp, amp)) // GRID * GRID
        return (dx, dy)

    def _draw_lines(self, screen: pygame.Surface, time: float) -> None:
        count = int(SPEED_LINES * self._speed)
        if count <= 0:
            return
        color = tone(Tone.CREAM)
        cx, cy = WIDTH / 2, float(HORIZON_Y)
        length = 50.0 + 70.0 * self._speed
        for index in range(count):
            angle = index * GOLDEN
            reach = LINE_START + (index * 97.0 + time * LINE_PACE) % LINE_SPAN
            dx, dy = math.cos(angle), math.sin(angle) * 0.6
            start = (cx + dx * reach, cy + dy * reach)
            end = (cx + dx * (reach + length), cy + dy * (reach + length))
            pygame.draw.line(screen, color, start, end, GRID)
