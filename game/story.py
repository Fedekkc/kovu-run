"""Hitos narrativos livianos según la distancia recorrida."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from game.cycle import CYCLE_M


class BeatKind(StrEnum):
    TOAST = "toast"
    SETPIECE = "setpiece"


@dataclass(frozen=True)
class Beat:
    id: str
    at_m: float
    title: str
    line: str
    kind: BeatKind
    setpiece: str = ""


BEATS: tuple[Beat, ...] = (
    Beat("start", 80.0, "El barrio", "Kovu olfatea galletas. La abuela ya ajustó el cardigan.", BeatKind.TOAST),
    Beat(
        "te_veo",
        400.0,
        "¡Te veo!",
        "Se acerca. No mires atrás: saltá y seguí.",
        BeatKind.SETPIECE,
        setpiece="chase",
    ),
    Beat(
        "wagon_express",
        900.0,
        "Vagón express",
        "¡Arriba del tren! El piso se acaba en cualquier momento.",
        BeatKind.SETPIECE,
        setpiece="wagon",
    ),
    Beat(
        "storm",
        1550.0,
        "Tormenta",
        "El cielo se abre. El barrio se pone denso.",
        BeatKind.SETPIECE,
        setpiece="storm",
    ),
    Beat("midnight", 2000.0, "Medianoche", "Las farolas parpadean. Todavía podés sumar.", BeatKind.TOAST),
)

TOAST_TIME = 2.5
CHASE_BOOST_TIME = 4.5
STORM_PRESS_TIME = 8.0


@dataclass
class Toast:
    title: str
    line: str
    left: float


class StoryTracker:
    """Emite cada beat una vez por ciclo de distancia."""

    def __init__(self) -> None:
        self._fired: set[str] = set()
        self.toast: Toast | None = None
        self._pending: list[Beat] = []

    def reset(self) -> None:
        self._fired.clear()
        self.toast = None
        self._pending.clear()

    def update(self, distance: float, dt: float) -> list[Beat]:
        if self.toast is not None:
            self.toast.left -= dt
            if self.toast.left <= 0.0:
                self.toast = None
        fired: list[Beat] = []
        if distance < 0.0:
            return fired
        cycles = int(distance // CYCLE_M) + 1
        for cycle in range(cycles):
            for beat in BEATS:
                key = f"{cycle}:{beat.id}"
                if key in self._fired:
                    continue
                if distance < beat.at_m + cycle * CYCLE_M:
                    continue
                self._fired.add(key)
                self.toast = Toast(beat.title, beat.line, TOAST_TIME)
                fired.append(beat)
                self._pending.append(beat)
        return fired

    def drain_setpieces(self) -> list[Beat]:
        out = [beat for beat in self._pending if beat.kind == BeatKind.SETPIECE]
        self._pending.clear()
        return out
