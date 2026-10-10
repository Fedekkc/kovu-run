"""Piezas que aparecen en la ruta."""

from __future__ import annotations

from dataclasses import dataclass

from game.settings import BISCUIT, FULL, HIGH, LOW


@dataclass
class Obstacle:
    lane: int
    z: float
    kind: str

    @property
    def lethal(self) -> bool:
        return self.kind in (LOW, HIGH, FULL)


@dataclass
class Biscuit:
    lane: int
    z: float
    taken: bool = False
    kind: str = BISCUIT


@dataclass
class Bonus:
    lane: int
    z: float
    kind: str
    taken: bool = False
