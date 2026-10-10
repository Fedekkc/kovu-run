"""Caption e ícono de la ventana."""

from __future__ import annotations

import pygame

from game.paths import asset
from game.settings import TITLE

ICON_SIZE = 64
SIDE_FRAME_W = 66


def decorate() -> None:
    pygame.display.set_caption(TITLE)
    icon = _load_icon()
    if icon is not None:
        pygame.display.set_icon(icon)


def _load_icon() -> pygame.Surface | None:
    path = asset("kovu_side.png")
    if not path.is_file():
        return None
    try:
        sheet = pygame.image.load(str(path))
        if pygame.display.get_surface() is not None:
            sheet = sheet.convert_alpha()
    except pygame.error:
        return None
    frame = sheet.subsurface((0, 0, min(SIDE_FRAME_W, sheet.get_width()), sheet.get_height())).copy()
    return pygame.transform.smoothscale(frame, (ICON_SIZE, ICON_SIZE))
