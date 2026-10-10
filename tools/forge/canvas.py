"""A tiny pixel canvas: every call places whole pixels from the shared palette."""

from __future__ import annotations

from collections.abc import Sequence

import pygame

from game.palette import Rgb, Tone, tone

BAYER = (
    (0, 8, 2, 10),
    (12, 4, 14, 6),
    (3, 11, 1, 9),
    (15, 7, 13, 5),
)
_CLEAR = (0, 0, 0, 0)


class Canvas:
    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.surface = pygame.Surface((width, height), pygame.SRCALPHA)
        self.surface.fill(_CLEAR)

    def rgb(self, name: Tone) -> Rgb:
        return tone(name)

    def inside(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def dot(self, x: float, y: float, name: Tone) -> None:
        px, py = int(round(x)), int(round(y))
        if self.inside(px, py):
            self.surface.set_at((px, py), (*tone(name), 255))

    def clear(self, x: int, y: int) -> None:
        if self.inside(x, y):
            self.surface.set_at((x, y), _CLEAR)

    def filled(self, x: int, y: int) -> bool:
        return self.inside(x, y) and self.surface.get_at((x, y))[3] > 0

    def is_tone(self, x: int, y: int, name: Tone) -> bool:
        return self.filled(x, y) and tuple(self.surface.get_at((x, y))[:3]) == tone(name)

    def rect(self, x: int, y: int, w: int, h: int, name: Tone) -> None:
        for py in range(y, y + h):
            for px in range(x, x + w):
                self.dot(px, py, name)

    def hline(self, x0: int, x1: int, y: int, name: Tone) -> None:
        for px in range(min(x0, x1), max(x0, x1) + 1):
            self.dot(px, y, name)

    def vline(self, x: int, y0: int, y1: int, name: Tone) -> None:
        for py in range(min(y0, y1), max(y0, y1) + 1):
            self.dot(x, py, name)

    def ellipse(self, cx: float, cy: float, rx: float, ry: float, name: Tone) -> None:
        for px, py in _ellipse_pixels(cx, cy, rx, ry):
            self.dot(px, py, name)

    def shaded(
        self,
        cx: float,
        cy: float,
        rx: float,
        ry: float,
        base: Tone,
        dark: Tone,
        light: Tone,
        shine: Tone | None = None,
    ) -> None:
        """Lit from the upper left: dark rim low-right, soft light high-left."""
        body = set(_ellipse_pixels(cx, cy, rx, ry))
        for px, py in body:
            self.dot(px, py, base)
        for px, py in body:
            if (px + 1, py + 1) not in body or (px, py + 1) not in body:
                self.dot(px, py, dark)
        glow = _ellipse_pixels(cx - rx * 0.32, cy - ry * 0.34, rx * 0.5, ry * 0.42)
        for px, py in glow:
            if (px, py) in body:
                self.dot(px, py, light)
        if shine is not None:
            self.dot(cx - rx * 0.42, cy - ry * 0.48, shine)

    def line(self, x0: float, y0: float, x1: float, y1: float, name: Tone, width: int = 1) -> None:
        steps = int(max(abs(x1 - x0), abs(y1 - y0))) + 1
        for step in range(steps + 1):
            t = step / steps if steps else 0.0
            x = x0 + (x1 - x0) * t
            y = y0 + (y1 - y0) * t
            if width <= 1:
                self.dot(x, y, name)
                continue
            half = (width - 1) / 2.0
            for ox in range(width):
                self.dot(x - half + ox, y, name)

    def poly(self, points: Sequence[tuple[float, float]], name: Tone) -> None:
        if len(points) < 3:
            return
        xs = [point[0] for point in points]
        ys = [point[1] for point in points]
        for py in range(int(min(ys)), int(max(ys)) + 1):
            for px in range(int(min(xs)), int(max(xs)) + 1):
                if _point_in_poly(px + 0.5, py + 0.5, points):
                    self.dot(px, py, name)

    def gradient(self, y0: int, y1: int, stops: Sequence[Tone]) -> None:
        """Ordered-dithered vertical blend through the stops, full width."""
        span = max(1, y1 - y0)
        bands = len(stops) - 1
        for py in range(y0, y1):
            t = (py - y0) / span * bands
            index = min(bands - 1, int(t))
            local = t - index
            for px in range(self.width):
                threshold = (BAYER[py % 4][px % 4] + 0.5) / 16.0
                name = stops[index + 1] if local > threshold else stops[index]
                self.dot(px, py, name)

    def outline(self, name: Tone) -> None:
        """One-pixel outer outline around everything already painted."""
        marks: list[tuple[int, int]] = []
        for py in range(self.height):
            for px in range(self.width):
                if self.filled(px, py):
                    continue
                if any(self.filled(px + dx, py + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                    marks.append((px, py))
        for px, py in marks:
            self.dot(px, py, name)

    def bounds(self) -> pygame.Rect:
        return self.surface.get_bounding_rect(min_alpha=1)


def strip(frames: Sequence[Canvas]) -> pygame.Surface:
    width = frames[0].width
    height = frames[0].height
    sheet = pygame.Surface((width * len(frames), height), pygame.SRCALPHA)
    sheet.fill(_CLEAR)
    for index, frame in enumerate(frames):
        sheet.blit(frame.surface, (index * width, 0))
    return sheet


def _ellipse_pixels(cx: float, cy: float, rx: float, ry: float) -> list[tuple[int, int]]:
    if rx <= 0.0 or ry <= 0.0:
        return []
    pixels: list[tuple[int, int]] = []
    for py in range(int(cy - ry) - 1, int(cy + ry) + 2):
        for px in range(int(cx - rx) - 1, int(cx + rx) + 2):
            dx = (px + 0.5 - cx) / rx
            dy = (py + 0.5 - cy) / ry
            if dx * dx + dy * dy <= 1.0:
                pixels.append((px, py))
    return pixels


def _point_in_poly(x: float, y: float, points: Sequence[tuple[float, float]]) -> bool:
    inside = False
    count = len(points)
    for index in range(count):
        ax, ay = points[index]
        bx, by = points[(index + 1) % count]
        if (ay > y) != (by > y):
            cross = ax + (y - ay) * (bx - ax) / (by - ay)
            if x < cross:
                inside = not inside
    return inside
