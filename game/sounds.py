"""Catálogo de samples. Los nombres coinciden con assets/audio/*.wav."""

from __future__ import annotations

from enum import StrEnum

from game.events import Kind


class Clip(StrEnum):
    MUSIC = "music"
    JUMP = "jump"
    LAND = "land"
    BISCUIT = "biscuit"
    BONUS = "bonus"
    CRASH = "crash"
    SLIDE = "slide"
    CLICK = "click"
    START = "start"


EVENT_CLIP = {
    Kind.JUMP: Clip.JUMP,
    Kind.LAND: Clip.LAND,
    Kind.BISCUIT: Clip.BISCUIT,
    Kind.BONUS: Clip.BONUS,
    Kind.CRASH: Clip.CRASH,
    Kind.SLIDE: Clip.SLIDE,
}

SFX = (
    Clip.JUMP,
    Clip.LAND,
    Clip.BISCUIT,
    Clip.BONUS,
    Clip.CRASH,
    Clip.SLIDE,
    Clip.CLICK,
    Clip.START,
)
