"""Si algo explota, queda un log y el proceso se cierra limpio."""

from __future__ import annotations

import traceback
from datetime import datetime, timezone
from pathlib import Path

from game.paths import data_dir


def default_crash_path() -> Path:
    return data_dir() / "crash.log"


def write_crash(error: BaseException, path: Path | None = None) -> Path:
    target = path if path is not None else default_crash_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    body = "".join(traceback.format_exception(type(error), error, error.__traceback__))
    with target.open("a", encoding="utf-8") as handle:
        handle.write(f"--- {stamp} ---\n")
        handle.write(body)
        if not body.endswith("\n"):
            handle.write("\n")
    return target
