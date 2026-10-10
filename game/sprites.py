"""PNGs hechos a mano. El archivo vive en el catálogo, no en el dibujo."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import pygame

from game.settings import BISCUIT, DOUBLE_JUMP, ROCKET, SUPER_JUMP

KOVU_RUN = "kovu_run"
KOVU_JUMP = "kovu_jump"
KOVU_SLIDE = "kovu_slide"
KOVU_ROCKET = "kovu_rocket"
KOVU_SUPER = "kovu_super"
KOVU_FLIP = "kovu_flip"
GIRL_RUN = "girl_run"
GIRL_GRAB = "girl_grab"
MENU_KOVU = "menu_kovu"
HEDGE = "hedge"
HYDRANT = "hydrant"
BANNER = "banner"
BIN = "bin"
CRATE = "crate"
TREE = "tree"
SHRUB = "shrub"
JUMP_ICON = "jump"
AGILITY_ICON = "agility"
SLIDE_ICON = "slide"
FACADE_PEACH = "facade_peach"
FACADE_BLUE = "facade_blue"
FACADE_SHOP = "facade_shop"
FACADE_PH = "facade_ph"
LAMP = "lamp"
SKY = "sky"
SKY_NIGHT = "sky_night"
SKYLINE_FAR = "skyline_far"
SKYLINE_NEAR = "skyline_near"

FILTER_NEAREST = "nearest"
FILTER_SMOOTH = "smooth"
# Below this many screen px per art px, nearest drops whole rows: average instead.
SHARP_FROM = 2.5

SLOTS: tuple[str, ...] = (
    KOVU_RUN,
    KOVU_JUMP,
    KOVU_SLIDE,
    KOVU_ROCKET,
    KOVU_SUPER,
    KOVU_FLIP,
    GIRL_RUN,
    GIRL_GRAB,
    MENU_KOVU,
    HEDGE,
    HYDRANT,
    BANNER,
    BIN,
    CRATE,
    TREE,
    SHRUB,
    BISCUIT,
    ROCKET,
    SUPER_JUMP,
    DOUBLE_JUMP,
    JUMP_ICON,
    AGILITY_ICON,
    SLIDE_ICON,
    FACADE_PEACH,
    FACADE_BLUE,
    FACADE_SHOP,
    FACADE_PH,
    LAMP,
    SKY,
    SKY_NIGHT,
    SKYLINE_FAR,
    SKYLINE_NEAR,
)

@dataclass(frozen=True)
class Stamp:
    image: pygame.Surface
    lift: float
    scale: float
    smooth: bool = True


@dataclass(frozen=True)
class _Spec:
    id: str
    file: str | None
    frames: int
    fps: float
    lift: float
    scale: float
    loop: bool = True


def default_catalog_path() -> Path:
    from game.paths import ASSETS

    return ASSETS / "sprites.json"


def blit_feet(
    screen: pygame.Surface,
    image: pygame.Surface,
    x: float,
    y: float,
    scale: float,
    smooth: bool = True,
) -> None:
    """El centro inferior del cuadro cae en (x, y)."""
    draw = scale if scale > 0.0 else 1.0
    width = max(1, int(round(image.get_width() * draw)))
    height = max(1, int(round(image.get_height() * draw)))
    sized = image
    if width != image.get_width() or height != image.get_height():
        tiny = draw < SHARP_FROM
        resize = pygame.transform.smoothscale if smooth or tiny else pygame.transform.scale
        sized = resize(image, (width, height))
    screen.blit(sized, (int(round(x - width / 2)), int(round(y - height))))


class SpriteBook:
    """Lee el catálogo una vez. Un archivo ausente no reemplaza el dibujo."""

    def __init__(self, path: Path | None = None) -> None:
        catalog = path if path is not None else default_catalog_path()
        self._root = catalog.parent
        self._specs, self.smooth = _read(catalog)
        self._frames: dict[str, tuple[pygame.Surface, ...] | None] = {}

    def stamp(self, slot: str, time: float) -> Stamp | None:
        spec = self._specs.get(slot)
        if spec is None or spec.file is None:
            return None
        frames = self._load(spec)
        if not frames:
            return None
        index = 0
        if spec.frames > 1 and spec.fps > 0.0:
            tick = max(0, int(time * spec.fps))
            index = tick % len(frames) if spec.loop else min(len(frames) - 1, tick)
        return Stamp(frames[index], spec.lift, spec.scale, self.smooth)

    def _load(self, spec: _Spec) -> tuple[pygame.Surface, ...] | None:
        if spec.id in self._frames:
            return self._frames[spec.id]
        loaded = self._slice(spec)
        self._frames[spec.id] = loaded
        return loaded

    def _slice(self, spec: _Spec) -> tuple[pygame.Surface, ...] | None:
        if spec.file is None:
            return None
        path = self._root / spec.file
        if not path.is_file():
            return None
        try:
            image = pygame.image.load(path)
            if pygame.display.get_surface() is not None:
                image = image.convert_alpha()
        except pygame.error:
            return None
        frame_w = image.get_width() // spec.frames
        if frame_w < 1:
            return None
        height = image.get_height()
        return tuple(
            image.subsurface((index * frame_w, 0, frame_w, height)).copy()
            for index in range(spec.frames)
        )


_book: SpriteBook | None = None


def default_book() -> SpriteBook:
    global _book
    if _book is None:
        _book = SpriteBook()
    return _book


def _read(path: Path) -> tuple[dict[str, _Spec], bool]:
    if not path.is_file():
        return {}, True
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError):
        return {}, True
    if not isinstance(raw, dict):
        return {}, True
    smooth = raw.get("filter", FILTER_SMOOTH) != FILTER_NEAREST
    rows = raw.get("sprites")
    if not isinstance(rows, list):
        return {}, smooth
    specs: dict[str, _Spec] = {}
    for item in rows:
        spec = _parse(item)
        if spec is None or spec.id in specs:
            continue
        specs[spec.id] = spec
    return specs, smooth


def _parse(raw: object) -> _Spec | None:
    if not isinstance(raw, dict):
        return None
    slot = raw.get("id")
    if not isinstance(slot, str) or slot == "":
        return None
    file = raw.get("file")
    if file is not None and not isinstance(file, str):
        return None
    if file == "":
        file = None
    frames = raw.get("frames", 1)
    if type(frames) is not int or frames < 1:
        frames = 1
    fps = raw.get("fps", 8)
    if type(fps) is not int and type(fps) is not float:
        fps = 8.0
    lift = raw.get("lift", 0)
    if type(lift) is not int and type(lift) is not float:
        lift = 0.0
    scale = raw.get("scale", 1)
    if type(scale) is not int and type(scale) is not float or scale <= 0:
        scale = 1.0
    loop = raw.get("loop", True)
    if type(loop) is not bool:
        loop = True
    return _Spec(slot, file, frames, float(fps), float(lift), float(scale), loop)
