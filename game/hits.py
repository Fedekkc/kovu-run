"""Regiones clickeables de la UI. Cada pantalla devuelve un Hits."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

import pygame


class Action(StrEnum):
    PLAY = "play"
    LAVA = "lava"
    ACCOUNTS = "accounts"
    UPGRADES = "upgrades"
    OPTIONS = "options"
    QUIT = "quit"
    BACK = "back"
    NEW = "new"
    SELECT = "select"
    BUY = "buy"
    CONFIRM = "confirm"
    TOGGLE = "toggle"
    NUDGE = "nudge"
    CREDITS = "credits"
    SKIP = "skip"
    RETRY = "retry"


@dataclass(frozen=True)
class Hit:
    action: Action
    rect: pygame.Rect
    index: int = 0
    delta: int = 0


class Hits:
    def __init__(self) -> None:
        self._items: list[Hit] = []

    def add(self, action: Action, rect: pygame.Rect, index: int = 0, delta: int = 0) -> None:
        self._items.append(Hit(action, pygame.Rect(rect), index, delta))

    def at(self, pos: tuple[int, int]) -> Hit | None:
        for hit in reversed(self._items):
            if hit.rect.collidepoint(pos):
                return hit
        return None
