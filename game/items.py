"""Piezas que aparecen en la ruta."""

from __future__ import annotations

from dataclasses import dataclass

from game.settings import BISCUIT, FULL, HIGH, LOW, WAGON


@dataclass
class Obstacle:
    lane: int
    z: float
    kind: str

    @property
    def lethal(self) -> bool:
        return self.kind in (LOW, HIGH, FULL, WAGON)

    @property
    def climbable(self) -> bool:
        return self.kind == WAGON


@dataclass
class Biscuit:
    lane: int
    z: float
    taken: bool = False
    kind: str = BISCUIT
    height: float = 0.0


@dataclass
class Bonus:
    lane: int
    z: float
    kind: str
    taken: bool = False
