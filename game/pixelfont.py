"""La fuente arcade: glifos 5x7 en assets/pixelfont.json, siempre en mayúsculas."""

from __future__ import annotations

import json
from pathlib import Path

import pygame

from game.palette import Rgb

UNKNOWN = "?"
GAP = 1


class PixelFontError(Exception):
    """Falta el archivo de la fuente o está roto."""


def default_font_path() -> Path:
    from game.paths import ASSETS

    return ASSETS / "pixelfont.json"


class PixelFont:
    def __init__(self, path: Path | None = None) -> None:
        source = path if path is not None else default_font_path()
        self.height, self._rows = _read(source)
        self._masks: dict[str, pygame.Surface] = {}
        self._cache: dict[tuple[str, Rgb, int, Rgb | None], pygame.Surface] = {}

    def covers(self, text: str) -> bool:
        return all(char in self._rows for char in text.upper())

    def size(self, text: str, scale: int) -> tuple[int, int]:
        return self._width(text.upper()) * scale, self.height * scale

    def render(self, text: str, color: Rgb, scale: int, shadow: Rgb | None = None) -> pygame.Surface:
        key = (text, color, scale, shadow)
        cached = self._cache.get(key)
        if cached is not None:
            return cached
        upper = text.upper()
        ink = self._ink(upper, color, scale)
        if shadow is None:
            image = ink
        else:
            image = pygame.Surface((ink.get_width() + scale, ink.get_height() + scale), pygame.SRCALPHA)
            image.blit(self._ink(upper, shadow, scale), (scale, scale))
            image.blit(ink, (0, 0))
        self._cache[key] = image
        return image

    def mask(self, text: str, scale: int) -> pygame.Surface:
        """White glyphs on clear, for callers that paint their own gradient."""
        return self._ink(text.upper(), (255, 255, 255), scale)

    def _ink(self, upper: str, color: Rgb, scale: int) -> pygame.Surface:
        width = max(1, self._width(upper))
        line = pygame.Surface((width, self.height), pygame.SRCALPHA)
        x = 0
        for char in upper:
            glyph = self._mask(char)
            line.blit(glyph, (x, 0))
            x += glyph.get_width() + GAP
        line.fill((*color, 255), special_flags=pygame.BLEND_RGBA_MULT)
        return pygame.transform.scale(line, (width * scale, self.height * scale))

    def _width(self, upper: str) -> int:
        if not upper:
            return 0
        return sum(self._mask(char).get_width() for char in upper) + GAP * (len(upper) - 1)

    def _mask(self, char: str) -> pygame.Surface:
        known = char if char in self._rows else UNKNOWN
        cached = self._masks.get(known)
        if cached is not None:
            return cached
        rows = self._rows[known]
        glyph = pygame.Surface((len(rows[0]), self.height), pygame.SRCALPHA)
        for y, row in enumerate(rows):
            for x, cell in enumerate(row):
                if cell:
                    glyph.set_at((x, y), (255, 255, 255, 255))
        self._masks[known] = glyph
        return glyph


def _read(path: Path) -> tuple[int, dict[str, tuple[tuple[bool, ...], ...]]]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        raise PixelFontError(f"No se pudo leer la fuente: {path}") from error
    if not isinstance(raw, dict):
        raise PixelFontError("La fuente no es un objeto.")
    height = raw.get("height")
    ink = raw.get("ink")
    table = raw.get("glyphs")
    if type(height) is not int or height < 1 or not isinstance(ink, str) or not isinstance(table, dict):
        raise PixelFontError("La fuente no tiene alto, tinta o glifos.")
    rows: dict[str, tuple[tuple[bool, ...], ...]] = {}
    for char, lines in table.items():
        if not isinstance(lines, list) or len(lines) != height:
            raise PixelFontError(f"Glifo roto: {char}")
        cells = tuple(tuple(cell == ink for cell in line) for line in lines if isinstance(line, str))
        if len(cells) != height or len({len(line) for line in cells}) != 1 or not cells[0]:
            raise PixelFontError(f"Glifo roto: {char}")
        rows[char] = cells
    if UNKNOWN not in rows:
        raise PixelFontError("La fuente necesita el glifo '?'.")
    return height, rows


_font: PixelFont | None = None


def default_font() -> PixelFont:
    global _font
    if _font is None:
        _font = PixelFont()
    return _font
