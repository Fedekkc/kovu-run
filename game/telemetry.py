"""Contadores locales opcionales: partidas del día y score medio. Sin red."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from game.paths import data_dir


@dataclass(frozen=True)
class DayStats:
    runs: int
    score_sum: int

    @property
    def average(self) -> int:
        if self.runs <= 0:
            return 0
        return self.score_sum // self.runs


def default_stats_path() -> Path:
    return data_dir() / "stats.json"


class Telemetry:
    def __init__(self, path: Path | None = None) -> None:
        self._path = path if path is not None else default_stats_path()

    def record(self, score: int, enabled: bool) -> None:
        if not enabled or score < 0:
            return
        payload = self._read()
        key = date.today().isoformat()
        day = payload.get(key, {"runs": 0, "score_sum": 0})
        if not isinstance(day, dict):
            day = {"runs": 0, "score_sum": 0}
        runs = day.get("runs", 0)
        total = day.get("score_sum", 0)
        if type(runs) is not int or runs < 0:
            runs = 0
        if type(total) is not int or total < 0:
            total = 0
        payload[key] = {"runs": runs + 1, "score_sum": total + score}
        self._write(payload)

    def today(self) -> DayStats:
        payload = self._read()
        day = payload.get(date.today().isoformat(), {})
        if not isinstance(day, dict):
            return DayStats(0, 0)
        runs = day.get("runs", 0)
        total = day.get("score_sum", 0)
        if type(runs) is not int or runs < 0:
            runs = 0
        if type(total) is not int or total < 0:
            total = 0
        return DayStats(runs, total)

    def _read(self) -> dict[str, object]:
        if not self._path.exists():
            return {}
        try:
            raw = json.loads(self._path.read_text(encoding="utf-8"))
        except (OSError, ValueError, TypeError):
            return {}
        return raw if isinstance(raw, dict) else {}

    def _write(self, payload: dict[str, object]) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self._path.with_suffix(".json.tmp")
        temporary.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        temporary.replace(self._path)
