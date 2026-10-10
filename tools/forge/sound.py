"""Síntesis arcade: WAV cortos para música y SFX. Sin dependencias extra."""

from __future__ import annotations

import math
import struct
import wave
from pathlib import Path

RATE = 22050
AMP = 12000


def write_catalog(folder: Path) -> list[Path]:
    folder.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for name, samples in (
        ("music.wav", music_loop()),
        ("jump.wav", jump()),
        ("land.wav", land()),
        ("biscuit.wav", biscuit()),
        ("bonus.wav", bonus()),
        ("crash.wav", crash()),
        ("slide.wav", slide()),
        ("click.wav", click()),
        ("start.wav", start()),
    ):
        path = folder / name
        _save(path, samples)
        written.append(path)
    return written


def music_loop() -> list[int]:
    """Loop ~8 s: bajo + arpegio + kick suave, vibe barrio pixel."""
    bpm = 112.0
    beat = 60.0 / bpm
    bars = 4
    steps = 16 * bars
    out: list[int] = []
    bass = (36, 36, 43, 41, 36, 36, 31, 34)
    lead = (60, 64, 67, 72, 67, 64, 62, 60, 55, 60, 64, 67, 64, 60, 55, 52)
    for step in range(steps):
        length = beat / 2
        note = bass[step % len(bass)]
        chunk = _note(note, length, wave="square", volume=0.28)
        chunk = _mix(chunk, _note(lead[step % len(lead)], length * 0.85, wave="triangle", volume=0.18))
        if step % 4 == 0:
            chunk = _mix(chunk, _kick(length * 0.35))
        if step % 4 == 2:
            chunk = _mix(chunk, _hat(length * 0.2))
        out.extend(chunk)
    return out


def jump() -> list[int]:
    return _sweep(220.0, 660.0, 0.12, wave="square", volume=0.4)


def land() -> list[int]:
    return _mix(_noise(0.06, volume=0.22), _note(40, 0.08, wave="sine", volume=0.3))


def biscuit() -> list[int]:
    a = _note(76, 0.06, wave="triangle", volume=0.35)
    b = _note(83, 0.08, wave="triangle", volume=0.35)
    return a + b


def bonus() -> list[int]:
    out: list[int] = []
    for midi in (60, 64, 67, 72, 79):
        out.extend(_note(midi, 0.07, wave="square", volume=0.28))
    return out


def crash() -> list[int]:
    body = _noise(0.28, volume=0.45)
    thud = _sweep(140.0, 40.0, 0.22, wave="sine", volume=0.5)
    return _mix(body, thud)


def slide() -> list[int]:
    return _sweep(400.0, 120.0, 0.16, wave="saw", volume=0.28)


def click() -> list[int]:
    return _note(84, 0.04, wave="square", volume=0.22)


def start() -> list[int]:
    out: list[int] = []
    for midi in (48, 55, 60, 67):
        out.extend(_note(midi, 0.09, wave="square", volume=0.3))
    return out


def _save(path: Path, samples: list[int]) -> None:
    with wave.open(str(path), "w") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(RATE)
        handle.writeframes(b"".join(struct.pack("<h", _clip(sample)) for sample in samples))


def _clip(value: float) -> int:
    return max(-32767, min(32767, int(value)))


def _hz(midi: int) -> float:
    return 440.0 * (2.0 ** ((midi - 69) / 12.0))


def _note(midi: int, seconds: float, wave: str = "square", volume: float = 0.3) -> list[int]:
    return _tone(_hz(midi), seconds, wave=wave, volume=volume)


def _tone(freq: float, seconds: float, wave: str = "square", volume: float = 0.3) -> list[int]:
    total = max(1, int(RATE * seconds))
    out: list[int] = []
    for index in range(total):
        t = index / RATE
        phase = t * freq
        if wave == "sine":
            value = math.sin(math.tau * phase)
        elif wave == "triangle":
            value = 2.0 * abs(2.0 * (phase % 1.0) - 1.0) - 1.0
        elif wave == "saw":
            value = 2.0 * (phase % 1.0) - 1.0
        else:
            value = 1.0 if (phase % 1.0) < 0.5 else -1.0
        env = _envelope(index, total)
        out.append(int(AMP * volume * env * value))
    return out


def _sweep(start: float, end: float, seconds: float, wave: str = "square", volume: float = 0.3) -> list[int]:
    total = max(1, int(RATE * seconds))
    out: list[int] = []
    for index in range(total):
        t = index / RATE
        progress = index / total
        freq = start + (end - start) * progress
        phase = t * freq
        if wave == "sine":
            value = math.sin(math.tau * phase)
        elif wave == "saw":
            value = 2.0 * (phase % 1.0) - 1.0
        else:
            value = 1.0 if (phase % 1.0) < 0.5 else -1.0
        env = _envelope(index, total)
        out.append(int(AMP * volume * env * value))
    return out


def _noise(seconds: float, volume: float = 0.3) -> list[int]:
    total = max(1, int(RATE * seconds))
    seed = 1234567
    out: list[int] = []
    for index in range(total):
        seed = (1103515245 * seed + 12345) & 0x7FFFFFFF
        value = (seed / 0x40000000) - 1.0
        env = _envelope(index, total)
        out.append(int(AMP * volume * env * value))
    return out


def _kick(seconds: float) -> list[int]:
    return _sweep(140.0, 48.0, seconds, wave="sine", volume=0.45)


def _hat(seconds: float) -> list[int]:
    return _noise(seconds, volume=0.12)


def _envelope(index: int, total: int) -> float:
    attack = max(1, int(total * 0.04))
    release = max(1, int(total * 0.2))
    if index < attack:
        return index / attack
    if index > total - release:
        return max(0.0, (total - index) / release)
    return 1.0


def _mix(a: list[int], b: list[int]) -> list[int]:
    length = max(len(a), len(b))
    out = [0] * length
    for index in range(length):
        left = a[index] if index < len(a) else 0
        right = b[index] if index < len(b) else 0
        out[index] = _clip(left + right)
    return out
