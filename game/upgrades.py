"""Mejoras que se pagan con galletas. El recorrido solo recibe el resultado."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Protocol

from game.settings import (
    BANK_RATE,
    DOUBLE_HOLD,
    DOUBLE_JUMP,
    DOUBLE_JUMP_SCALE,
    DOUBLE_JUMP_TIME,
    JUMP_TIME,
    LANE_SWITCH,
    LUCK_WEIGHT,
    PICKUP_SPAN,
    ROCKET,
    ROCKET_SPEED,
    ROCKET_TIME,
    SLIDE_TIME,
    SUPER_HOLD,
    SUPER_JUMP,
    SUPER_JUMP_SCALE,
    SUPER_JUMP_TIME,
)
from game.sprites import AGILITY_ICON, BISCUIT, JUMP_ICON, SLIDE_ICON

MAX_LEVEL = 8

COPY_ROCKET = "Cohete"
COPY_SUPER = "Super salto"
COPY_DOUBLE = "Doble salto"
COPY_JUMP = "Salto"
COPY_AGILITY = "Agilidad"
COPY_SLIDE = "Deslizamiento"
COPY_MAGNET = "Imán"
COPY_LUCK = "Suerte"
COPY_VAULT = "Alcancía"
COPY_MISSING = "Esa mejora no existe."
COPY_MAXED = "Ya está al máximo."
COPY_BROKE = "No alcanzan las galletas."
COPY_LABEL = {
    "rocket": "vuelo",
    "super": "ventana",
    "double": "ventana",
    "jump": "altura",
    "agility": "más rápido",
    "slide": "agachado",
    "magnet": "radio",
    "lucky": "rutas",
    "vault": "guardado",
}
POWER_LABEL = {
    ROCKET: COPY_ROCKET,
    SUPER_JUMP: COPY_SUPER,
    DOUBLE_JUMP: COPY_DOUBLE,
}

_BASE_COST: dict[str, int] = {
    "rocket": 45,
    "super": 40,
    "double": 40,
    "jump": 28,
    "agility": 26,
    "slide": 26,
    "magnet": 32,
    "lucky": 34,
    "vault": 50,
}
_COST_STEP = 22


@dataclass(frozen=True)
class RunMods:
    """Números de una partida. En nivel 0 coinciden con las constantes base."""

    rocket_time: float = ROCKET_TIME
    rocket_speed: float = ROCKET_SPEED
    super_hold: float = SUPER_HOLD
    super_jump_time: float = SUPER_JUMP_TIME
    super_jump_scale: float = SUPER_JUMP_SCALE
    double_hold: float = DOUBLE_HOLD
    double_jump_time: float = DOUBLE_JUMP_TIME
    double_jump_scale: float = DOUBLE_JUMP_SCALE
    jump_time: float = JUMP_TIME
    jump_scale: float = 1.0
    lane_switch: float = LANE_SWITCH
    slide_time: float = SLIDE_TIME
    pickup_span: float = PICKUP_SPAN
    luck_weight: int = LUCK_WEIGHT
    bank_rate: float = BANK_RATE


@dataclass(frozen=True)
class Upgrade:
    id: str
    name: str
    sprite: str


@dataclass(frozen=True)
class UpgradeLine:
    id: str
    name: str
    level: int
    max_level: int
    effect: str
    cost: int | None
    sprite: str


class Progress(Protocol):
    biscuits: int
    levels: dict[str, int]


CATALOG: tuple[Upgrade, ...] = (
    Upgrade("rocket", COPY_ROCKET, ROCKET),
    Upgrade("super", COPY_SUPER, SUPER_JUMP),
    Upgrade("double", COPY_DOUBLE, DOUBLE_JUMP),
    Upgrade("jump", COPY_JUMP, JUMP_ICON),
    Upgrade("agility", COPY_AGILITY, AGILITY_ICON),
    Upgrade("slide", COPY_SLIDE, SLIDE_ICON),
    Upgrade("magnet", COPY_MAGNET, BISCUIT),
    Upgrade("lucky", COPY_LUCK, JUMP_ICON),
    Upgrade("vault", COPY_VAULT, BISCUIT),
)

_BY_ID = {item.id: item for item in CATALOG}


def level_of(levels: Mapping[str, int], upgrade_id: str) -> int:
    raw = levels.get(upgrade_id, 0)
    if type(raw) is not int:
        return 0
    return min(MAX_LEVEL, max(0, raw))


def cost_for(upgrade_id: str, level: int) -> int:
    """Precio para subir desde `level` al siguiente."""
    base = _BASE_COST.get(upgrade_id, 30)
    return base + _COST_STEP * max(0, level)


def run_mods(levels: Mapping[str, int] | None = None) -> RunMods:
    src: Mapping[str, int] = {} if levels is None else levels
    rocket = level_of(src, "rocket")
    super_level = level_of(src, "super")
    double = level_of(src, "double")
    jump = level_of(src, "jump")
    agility = level_of(src, "agility")
    slide = level_of(src, "slide")
    magnet = level_of(src, "magnet")
    lucky = level_of(src, "lucky")
    vault = level_of(src, "vault")
    return RunMods(
        rocket_time=ROCKET_TIME + 0.45 * rocket,
        rocket_speed=ROCKET_SPEED + 0.04 * rocket,
        super_hold=SUPER_HOLD + 0.45 * super_level,
        super_jump_time=SUPER_JUMP_TIME,
        super_jump_scale=SUPER_JUMP_SCALE + 0.08 * super_level,
        double_hold=DOUBLE_HOLD + 0.45 * double,
        double_jump_time=DOUBLE_JUMP_TIME,
        double_jump_scale=DOUBLE_JUMP_SCALE + 0.10 * double,
        jump_time=JUMP_TIME + 0.03 * jump,
        jump_scale=1.0 + 0.05 * jump,
        lane_switch=LANE_SWITCH * (1.0 - 0.06 * agility),
        slide_time=SLIDE_TIME + 0.06 * slide,
        pickup_span=PICKUP_SPAN + 0.14 * magnet,
        luck_weight=LUCK_WEIGHT + lucky,
        bank_rate=BANK_RATE + 0.07 * vault,
    )


def lines_for(levels: Mapping[str, int]) -> list[UpgradeLine]:
    rows: list[UpgradeLine] = []
    for spec in CATALOG:
        level = level_of(levels, spec.id)
        price = None if level >= MAX_LEVEL else cost_for(spec.id, level)
        rows.append(
            UpgradeLine(
                spec.id,
                spec.name,
                level,
                MAX_LEVEL,
                describe(spec.id, level),
                price,
                spec.sprite,
            )
        )
    return rows


def describe(upgrade_id: str, level: int) -> str:
    current = _measure(upgrade_id, level)
    label = COPY_LABEL.get(upgrade_id, "")
    head = f"{label} {current}".strip()
    if level >= MAX_LEVEL:
        return head
    return f"{head} → {_measure(upgrade_id, level + 1)}"


def purchase(progress: Progress, upgrade_id: str) -> str:
    """Vacío si la compra se hizo. Si no, el motivo para mostrar en el menú."""
    if upgrade_id not in _BY_ID:
        return COPY_MISSING
    level = level_of(progress.levels, upgrade_id)
    if level >= MAX_LEVEL:
        return COPY_MAXED
    price = cost_for(upgrade_id, level)
    if progress.biscuits < price:
        return COPY_BROKE
    progress.biscuits -= price
    progress.levels[upgrade_id] = level + 1
    return ""


def banked_biscuits(taken: int, rate: float) -> int:
    """Galletas que entran a la cuenta tras una carrera."""
    if taken <= 0:
        return 0
    bonus = max(0.0, rate)
    return max(taken, int(round(taken * (1.0 + bonus))))


def _measure(upgrade_id: str, level: int) -> str:
    mods = run_mods({upgrade_id: level})
    if upgrade_id == "rocket":
        return f"{_num(mods.rocket_time)} s · x{_num(mods.rocket_speed)}"
    if upgrade_id == "super":
        return f"{_num(mods.super_hold)} s · x{_num(mods.super_jump_scale)}"
    if upgrade_id == "double":
        return f"{_num(mods.double_hold)} s · x{_num(mods.double_jump_scale)}"
    if upgrade_id == "jump":
        return f"x{_num(mods.jump_scale)}"
    if upgrade_id == "agility":
        return f"{_num(mods.lane_switch)} s"
    if upgrade_id == "slide":
        return f"{_num(mods.slide_time)} s"
    if upgrade_id == "magnet":
        return f"x{_num(mods.pickup_span)}"
    if upgrade_id == "lucky":
        return f"+{mods.luck_weight}"
    if upgrade_id == "vault":
        return f"+{int(round(mods.bank_rate * 100))} %"
    return ""


def _num(value: float) -> str:
    text = f"{value:.2f}".rstrip("0").rstrip(".")
    return text.replace(".", ",")
