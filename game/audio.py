"""Música y SFX. Si falta un sample, el juego sigue en silencio para ese cue."""

from __future__ import annotations

from pathlib import Path

import pygame

from game.events import Event
from game.options import VOLUME_MAX
from game.paths import ASSETS
from game.sounds import EVENT_CLIP, SFX, Clip


def audio_dir() -> Path:
    return ASSETS / "audio"


class Audio:
    def __init__(self, folder: Path | None = None) -> None:
        self._ready = False
        self._volume = VOLUME_MAX
        self._sounds: dict[Clip, pygame.mixer.Sound] = {}
        self._root = folder if folder is not None else audio_dir()
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
            self._ready = pygame.mixer.get_init() is not None
        except pygame.error:
            self._ready = False
        if self._ready:
            self._load()
            self.set_volume(VOLUME_MAX)

    @property
    def ready(self) -> bool:
        return self._ready

    def set_volume(self, steps: int) -> None:
        level = max(0, min(VOLUME_MAX, steps))
        self._volume = level
        if not self._ready:
            return
        gain = level / VOLUME_MAX
        pygame.mixer.music.set_volume(gain * 0.55)
        for sound in self._sounds.values():
            sound.set_volume(gain)

    def play_music(self) -> None:
        if not self._ready or self._volume <= 0:
            return
        path = self._root / f"{Clip.MUSIC.value}.wav"
        if not path.is_file():
            return
        try:
            if not pygame.mixer.music.get_busy():
                pygame.mixer.music.load(str(path))
                pygame.mixer.music.play(-1)
        except pygame.error:
            return

    def stop_music(self) -> None:
        if not self._ready:
            return
        pygame.mixer.music.stop()
        unload = getattr(pygame.mixer.music, "unload", None)
        if unload is not None:
            try:
                unload()
            except pygame.error:
                return

    def play(self, clip: Clip) -> None:
        if not self._ready or self._volume <= 0:
            return
        sound = self._sounds.get(clip)
        if sound is None:
            return
        try:
            sound.play()
        except pygame.error:
            return

    def event(self, event: Event) -> None:
        clip = EVENT_CLIP.get(event.kind)
        if clip is not None:
            self.play(clip)

    def click(self) -> None:
        self.play(Clip.CLICK)

    def start(self) -> None:
        self.play(Clip.START)

    def _load(self) -> None:
        for clip in SFX:
            path = self._root / f"{clip.value}.wav"
            if not path.is_file():
                continue
            try:
                self._sounds[clip] = pygame.mixer.Sound(str(path))
            except pygame.error:
                continue
