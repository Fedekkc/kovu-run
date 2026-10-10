"""Nombre de una cuenta: letras, entre 3 y 10."""

from __future__ import annotations

import pygame

from game.accounts import NAME_MAX, NAME_MIN


class NameBuffer:
    MIN = NAME_MIN
    MAX = NAME_MAX

    def __init__(self) -> None:
        self.text = ""

    def reset(self) -> None:
        self.text = ""

    def handle_key(self, key: int) -> bool:
        """Devuelve True cuando el nombre ya se puede crear."""
        if key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            return len(self.text) >= self.MIN
        if key == pygame.K_BACKSPACE:
            self.text = self.text[:-1]
            return False
        if pygame.K_a <= key <= pygame.K_z and len(self.text) < self.MAX:
            self.text += chr(key).upper()
        return False
