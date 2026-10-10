"""Bus de volumen. Hoy no hay samples; deja el mixer listo para cuando existan."""

from __future__ import annotations

import pygame

from game.options import VOLUME_MAX


class Audio:
    def __init__(self) -> None:
        self._ready = False
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            self._ready = pygame.mixer.get_init() is not None
        except pygame.error:
            self._ready = False
        self._volume = VOLUME_MAX

    @property
    def ready(self) -> bool:
        return self._ready

    def set_volume(self, steps: int) -> None:
        level = max(0, min(VOLUME_MAX, steps))
        self._volume = level
        if not self._ready:
            return
        pygame.mixer.music.set_volume(level / VOLUME_MAX)
