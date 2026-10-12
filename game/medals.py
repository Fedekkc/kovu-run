"""Medallas de distancia por cuenta (solo bragging rights)."""

from __future__ import annotations

from game.settings import MEDAL_THRESHOLDS

COPY_MEDAL = {
    "barrio": "Barrio (500 m)",
    "avenida": "Avenida (1000 m)",
    "autopista": "Autopista (2000 m)",
    "leyenda": "Leyenda (5000 m)",
}


def label_for(medal_id: str) -> str:
    return COPY_MEDAL.get(medal_id, medal_id)


def unlocked_by(distance: float) -> list[str]:
    return [medal_id for medal_id, need in MEDAL_THRESHOLDS if distance >= need]


def award(account_medals: list[str], distance: float) -> list[str]:
    """Devuelve los ids nuevos y muta account_medals in-place."""
    have = set(account_medals)
    fresh: list[str] = []
    for medal_id in unlocked_by(distance):
        if medal_id in have:
            continue
        account_medals.append(medal_id)
        have.add(medal_id)
        fresh.append(medal_id)
    return fresh
