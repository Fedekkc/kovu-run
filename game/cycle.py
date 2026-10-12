"""La hora del barrio según los metros: atardecer, noche, lluvia y vuelta a empezar."""

from __future__ import annotations

from dataclasses import dataclass

CYCLE_M = 2400.0


@dataclass(frozen=True)
class Mood:
    night: float
    rain: float


SUNSET = Mood(0.0, 0.0)
NIGHT = Mood(1.0, 0.0)
STORM = Mood(1.0, 1.0)

# Keyframes ordenados en [0, CYCLE_M]. El tramo entre dos keys interpola.
_KEYS: tuple[tuple[float, Mood], ...] = (
    (0.0, SUNSET),
    (400.0, SUNSET),
    (1000.0, NIGHT),
    (1300.0, NIGHT),
    (1600.0, STORM),
    (1950.0, STORM),
    (2200.0, NIGHT),
    (CYCLE_M, SUNSET),
)


def mood_at(distance: float) -> Mood:
    at = distance % CYCLE_M
    for (start, low), (end, high) in zip(_KEYS, _KEYS[1:]):
        if at <= end:
            span = end - start
            t = 0.0 if span <= 0.0 else (at - start) / span
            return Mood(
                low.night + (high.night - low.night) * t,
                low.rain + (high.rain - low.rain) * t,
            )
    return SUNSET
