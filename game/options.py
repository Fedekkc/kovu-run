"""Preferencias locales: volumen, pantalla, hitboxes, telemetría."""

from __future__ import annotations

import json
from dataclasses import dataclass, replace
from pathlib import Path

from game.paths import data_dir

VOLUME_MAX = 10
VOLUME_DEFAULT = 7
LANG_ES = "es"

COPY_LANG_ES = "Español"


@dataclass(frozen=True)
class Options:
    volume: int = VOLUME_DEFAULT
    fullscreen: bool = True
    show_hitboxes: bool = False
    telemetry: bool = False
    language: str = LANG_ES

    def clamp(self) -> Options:
        volume = max(0, min(VOLUME_MAX, int(self.volume)))
        language = LANG_ES if self.language == LANG_ES else LANG_ES
        return Options(volume, bool(self.fullscreen), bool(self.show_hitboxes), bool(self.telemetry), language)


def default_options_path() -> Path:
    return data_dir() / "options.json"


class OptionsStore:
    def __init__(self, path: Path | None = None) -> None:
        self._path = path if path is not None else default_options_path()
        self.value = self.load()

    def load(self) -> Options:
        if not self._path.exists():
            return Options().clamp()
        try:
            raw = json.loads(self._path.read_text(encoding="utf-8"))
        except (OSError, ValueError, TypeError):
            return Options().clamp()
        if not isinstance(raw, dict):
            return Options().clamp()
        volume = raw.get("volume", VOLUME_DEFAULT)
        if type(volume) is not int:
            volume = VOLUME_DEFAULT
        language = raw.get("language", LANG_ES)
        if not isinstance(language, str):
            language = LANG_ES
        return Options(
            volume,
            bool(raw.get("fullscreen", True)),
            bool(raw.get("show_hitboxes", False)),
            bool(raw.get("telemetry", False)),
            language,
        ).clamp()

    def save(self) -> None:
        self.value = self.value.clamp()
        self._path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "volume": self.value.volume,
            "fullscreen": self.value.fullscreen,
            "show_hitboxes": self.value.show_hitboxes,
            "telemetry": self.value.telemetry,
            "language": self.value.language,
        }
        temporary = self._path.with_suffix(".json.tmp")
        temporary.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        temporary.replace(self._path)

    def _set(self, **changes: object) -> None:
        self.value = replace(self.value, **changes).clamp()
        self.save()

    def set_volume(self, volume: int) -> None:
        self._set(volume=volume)

    def toggle_fullscreen(self) -> None:
        self._set(fullscreen=not self.value.fullscreen)

    def toggle_hitboxes(self) -> None:
        self._set(show_hitboxes=not self.value.show_hitboxes)

    def toggle_telemetry(self) -> None:
        self._set(telemetry=not self.value.telemetry)
