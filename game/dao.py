"""Ranking local de la máquina. El juego no sabe si el archivo es JSON."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Protocol

from game.accounts import NAME_MIN, LocalAccountDAO, normalize_name
from game.paths import data_dir
from game.settings import RANKING_LIMIT

CABINET_ID = "KOVU-LOCAL"
_LEGACY_ACCOUNT = "KOV"
_LEGACY_NAME = "highscore.json"


@dataclass(frozen=True)
class RankingEntry:
    name: str
    score: int
    biscuits: int
    played_at: str

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "score": self.score,
            "biscuits": self.biscuits,
            "played_at": self.played_at,
        }


class RankingDAO(Protocol):
    def top(self) -> list[RankingEntry]: ...

    def best(self) -> int: ...

    def qualifies(self, score: int) -> bool: ...

    def insert(self, name: str, score: int, biscuits: int) -> int: ...


def default_ranking_path() -> Path:
    return data_dir() / "ranking.json"


class LocalArcadeDAO:
    """Persiste el top 10 en JSON, con reemplazo atómico del archivo."""

    def __init__(
        self,
        path: Path | None = None,
        limit: int = RANKING_LIMIT,
        accounts: LocalAccountDAO | None = None,
    ) -> None:
        self._path = path if path is not None else default_ranking_path()
        self._limit = limit
        self._accounts = accounts if accounts is not None else LocalAccountDAO()

    def top(self) -> list[RankingEntry]:
        return self._read()

    def best(self) -> int:
        rows = self._read()
        if not rows:
            return 0
        return rows[0].score

    def qualifies(self, score: int) -> bool:
        if score <= 0:
            return False
        rows = self._read()
        if len(rows) < self._limit:
            return True
        return score > rows[-1].score

    def insert(self, name: str, score: int, biscuits: int) -> int:
        """Devuelve el puesto 1-based, o 0 si no hay cuenta o el puntaje no entra."""
        account_name = normalize_name(name)
        if score <= 0 or not self._accounts.is_registered(account_name):
            return 0
        current = self._read()
        previous = next((row for row in current if row.name == account_name), None)
        if previous is not None and score <= previous.score:
            return 0
        others = [row for row in current if row.name != account_name]
        if previous is None and len(others) >= self._limit and score <= others[-1].score:
            return 0
        entry = RankingEntry(
            name=account_name,
            score=score,
            biscuits=max(0, biscuits),
            played_at=datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        )
        rows = [*others, entry]
        rows.sort(key=lambda item: (-item.score, item.played_at))
        kept = rows[: self._limit]
        if entry not in kept:
            return 0
        self._write(kept)
        return kept.index(entry) + 1

    def _read(self) -> list[RankingEntry]:
        if not self._path.exists():
            migrated = self._migrate_legacy()
            if migrated:
                self._write(migrated)
            return migrated
        try:
            raw = json.loads(self._path.read_text(encoding="utf-8"))
        except (OSError, ValueError, TypeError):
            return []
        entries = raw.get("entries") if isinstance(raw, dict) else None
        if not isinstance(entries, list):
            return []
        parsed = [entry for item in entries if (entry := _parse_entry(item)) is not None]
        parsed = [entry for entry in parsed if self._accounts.is_registered(entry.name)]
        parsed.sort(key=lambda item: (-item.score, item.played_at))
        return parsed[: self._limit]

    def _migrate_legacy(self) -> list[RankingEntry]:
        legacy = self._path.parent.parent / _LEGACY_NAME
        try:
            raw = json.loads(legacy.read_text(encoding="utf-8"))
            score = raw["best"]
        except (OSError, ValueError, TypeError, KeyError):
            return []
        if type(score) is not int or score <= 0 or not self._accounts.is_registered(_LEGACY_ACCOUNT):
            return []
        return [
            RankingEntry(
                name=_LEGACY_ACCOUNT,
                score=score,
                biscuits=0,
                played_at=datetime.fromtimestamp(legacy.stat().st_mtime, timezone.utc)
                .replace(microsecond=0)
                .isoformat(),
            )
        ]

    def _write(self, entries: list[RankingEntry]) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"cabinet": CABINET_ID, "entries": [item.to_dict() for item in entries]}
        temporary = self._path.with_suffix(".json.tmp")
        temporary.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        temporary.replace(self._path)


def _parse_entry(raw: object) -> RankingEntry | None:
    if not isinstance(raw, dict):
        return None
    raw_name = raw.get("name")
    if not isinstance(raw_name, str):
        raw_name = raw.get("initials")
    score = raw.get("score")
    biscuits = raw.get("biscuits", 0)
    played_at = raw.get("played_at")
    if not isinstance(raw_name, str) or type(score) is not int or not isinstance(played_at, str):
        return None
    name = normalize_name(raw_name)
    if len(name) < NAME_MIN:
        return None
    if type(biscuits) is not int:
        biscuits = 0
    return RankingEntry(name, score, max(0, biscuits), played_at)
