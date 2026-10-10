"""Dónde vive la data local del juego (cuentas, opciones, logs)."""

from __future__ import annotations

import sys
from pathlib import Path


def root() -> Path:
    """Carpeta escribible: junto al .exe si está empaquetado, si no el repo."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


def assets_dir() -> Path:
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass is not None:
        bundled = Path(meipass) / "assets"
        if bundled.is_dir():
            return bundled
    return root() / "assets"


ROOT = root()
ASSETS = assets_dir()
DATA = ROOT / "data"


def data_dir() -> Path:
    DATA.mkdir(parents=True, exist_ok=True)
    return DATA


def asset(name: str) -> Path:
    return ASSETS / name
