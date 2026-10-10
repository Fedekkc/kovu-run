"""Lo que pasó en el último paso, para quien quiera reaccionar (efectos, sonido)."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class Kind(StrEnum):
    BISCUIT = "biscuit"
    BONUS = "bonus"
    CRASH = "crash"
    JUMP = "jump"
    LAND = "land"
    SLIDE = "slide"


@dataclass(frozen=True)
class Event:
    kind: Kind
    lane: float
    z: float
    tag: str = ""


class Feed:
    """Collects events until someone drains them."""

    def __init__(self) -> None:
        self._events: list[Event] = []

    def emit(self, event: Event) -> None:
        self._events.append(event)

    def drain(self) -> list[Event]:
        out = self._events
        self._events = []
        return out
