"""Factory method de las piezas de la ruta.

Cada creador implementa `create`. `TrackFactory` elige el creador y llama a
`spawn`, que es el único lugar por el que nace un objeto.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from game.items import Biscuit, Bonus, Obstacle
from game.settings import (
    BISCUIT,
    DOUBLE_JUMP,
    FULL,
    HIGH,
    LOW,
    ROCKET,
    SUPER_JUMP,
    WAGON,
)

TrackItem = Obstacle | Biscuit | Bonus


class ItemCreator(ABC):
    def spawn(self, lane: int, z: float) -> TrackItem:
        return self.create(lane, z)

    @abstractmethod
    def create(self, lane: int, z: float) -> TrackItem:
        """Construye la pieza concreta de este creador."""


class ObstacleCreator(ItemCreator):
    def __init__(self, kind: str) -> None:
        self._kind = kind

    def create(self, lane: int, z: float) -> Obstacle:
        return Obstacle(lane, z, self._kind)


class BiscuitCreator(ItemCreator):
    def create(self, lane: int, z: float) -> Biscuit:
        return Biscuit(lane, z)


class BonusCreator(ItemCreator):
    def __init__(self, kind: str) -> None:
        self._kind = kind

    def create(self, lane: int, z: float) -> Bonus:
        return Bonus(lane, z, self._kind)


class TrackFactory:
    def __init__(self) -> None:
        self._creators: dict[str, ItemCreator] = {
            LOW: ObstacleCreator(LOW),
            HIGH: ObstacleCreator(HIGH),
            FULL: ObstacleCreator(FULL),
            WAGON: ObstacleCreator(WAGON),
            BISCUIT: BiscuitCreator(),
            ROCKET: BonusCreator(ROCKET),
            SUPER_JUMP: BonusCreator(SUPER_JUMP),
            DOUBLE_JUMP: BonusCreator(DOUBLE_JUMP),
        }

    def create(self, kind: str, lane: int, z: float) -> TrackItem:
        try:
            creator = self._creators[kind]
        except KeyError:
            raise ValueError(f"No hay piezas de tipo {kind}") from None
        return creator.spawn(lane, z)
