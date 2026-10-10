"""Paleta única del juego. Sprites y calle salen de los mismos colores."""

from __future__ import annotations

import json
from enum import StrEnum
from pathlib import Path

Rgb = tuple[int, int, int]


class PaletteError(Exception):
    """Falta el archivo de paleta o le falta un color."""


class Tone(StrEnum):
    INK = "ink"
    PLUM_DARK = "plum_dark"
    PLUM = "plum"
    VIOLET = "violet"
    MAUVE = "mauve"
    ROSE = "rose"
    CORAL = "coral"
    PEACH = "peach"
    SUN = "sun"
    CREAM = "cream"
    SKY_TOP = "sky_top"
    SKY_HIGH = "sky_high"
    SKY_MID = "sky_mid"
    SKY_LOW = "sky_low"
    SKY_GLOW = "sky_glow"
    TAN_DARK = "tan_dark"
    TAN = "tan"
    TAN_LIGHT = "tan_light"
    TAN_SHINE = "tan_shine"
    BLUE_DARK = "blue_dark"
    BLUE = "blue"
    BLUE_LIGHT = "blue_light"
    BRICK_DARK = "brick_dark"
    BRICK = "brick"
    BRICK_LIGHT = "brick_light"
    MORTAR = "mortar"
    LEAF_DARK = "leaf_dark"
    LEAF = "leaf"
    LEAF_LIGHT = "leaf_light"
    GERANIUM = "geranium"
    GERANIUM_LIGHT = "geranium_light"
    SOIL = "soil"
    STONE_DARK = "stone_dark"
    STONE = "stone"
    STONE_LIGHT = "stone_light"
    WALK_DARK = "walk_dark"
    WALK = "walk"
    WALK_LIGHT = "walk_light"
    CURB = "curb"
    CURB_DARK = "curb_dark"
    PAINT = "paint"
    WINDOW = "window"
    WINDOW_DIM = "window_dim"
    NEON_PINK = "neon_pink"
    NEON_CYAN = "neon_cyan"
    TRUNK = "trunk"
    BARK_LIGHT = "bark_light"
    BARK_DARK = "bark_dark"
    SKIN = "skin"
    SKIN_DARK = "skin_dark"
    HAIR = "hair"
    HAIR_DARK = "hair_dark"
    HAIR_LIGHT = "hair_light"


def default_palette_path() -> Path:
    from game.paths import ASSETS

    return ASSETS / "palette.json"


def load_palette(path: Path | None = None) -> dict[Tone, Rgb]:
    source = path if path is not None else default_palette_path()
    try:
        raw = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        raise PaletteError(f"No se pudo leer la paleta: {source}") from error
    colors = raw.get("colors") if isinstance(raw, dict) else None
    if not isinstance(colors, dict):
        raise PaletteError("La paleta no tiene colores.")
    table: dict[Tone, Rgb] = {}
    for tone in Tone:
        value = colors.get(tone.value)
        if not isinstance(value, str):
            raise PaletteError(f"Falta el color {tone.value}.")
        table[tone] = _hex(value)
    return table


_cache: dict[Tone, Rgb] | None = None


def tone(name: Tone) -> Rgb:
    global _cache
    if _cache is None:
        _cache = load_palette()
    return _cache[name]


def _hex(value: str) -> Rgb:
    digits = value.removeprefix("#")
    if len(digits) != 6:
        raise PaletteError(f"Color inválido: {value}")
    try:
        return (int(digits[0:2], 16), int(digits[2:4], 16), int(digits[4:6], 16))
    except ValueError as error:
        raise PaletteError(f"Color inválido: {value}") from error
