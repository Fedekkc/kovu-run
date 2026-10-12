"""Cuentas locales. Cada una guarda galletas y el nivel de las mejoras."""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from game.paths import data_dir

NAME_MIN = 3
NAME_MAX = 10

COPY_NAME_SHORT = "El nombre necesita al menos 3 letras."
COPY_NAME_TAKEN = "Esa cuenta ya existe."
COPY_MISSING = "Esa cuenta no existe."


class AccountError(Exception):
    """El nombre no sirve o la cuenta no está en el archivo."""


@dataclass
class Account:
    name: str
    biscuits: int = 0
    levels: dict[str, int] = field(default_factory=dict)
    medals: list[str] = field(default_factory=list)


@dataclass
class _File:
    active: str | None
    accounts: list[Account]


def normalize_name(raw: str) -> str:
    letters = [char for char in raw.upper() if "A" <= char <= "Z"]
    return "".join(letters[:NAME_MAX])


def default_accounts_path() -> Path:
    return data_dir() / "accounts.json"


class LocalAccountDAO:
    """Persiste las cuentas en JSON, con reemplazo atómico del archivo."""

    def __init__(self, path: Path | None = None) -> None:
        self._path = path if path is not None else default_accounts_path()

    def list(self) -> list[Account]:
        return list(self._read().accounts)

    def is_registered(self, raw: str) -> bool:
        name = normalize_name(raw)
        if len(name) < NAME_MIN:
            return False
        return any(account.name == name for account in self._read().accounts)

    def active(self) -> Account | None:
        data = self._read()
        if data.active is None:
            return None
        for account in data.accounts:
            if account.name == data.active:
                return account
        return None

    def create(self, raw: str) -> Account:
        name = normalize_name(raw)
        if len(name) < NAME_MIN:
            raise AccountError(COPY_NAME_SHORT)
        data = self._read()
        if any(account.name == name for account in data.accounts):
            raise AccountError(COPY_NAME_TAKEN)
        account = Account(name, 0, {}, [])
        data.accounts.append(account)
        data.active = name
        self._write(data)
        return account

    def select(self, raw: str) -> None:
        name = normalize_name(raw)
        data = self._read()
        if not any(account.name == name for account in data.accounts):
            raise AccountError(COPY_MISSING)
        data.active = name
        self._write(data)

    def update(self, account: Account) -> None:
        data = self._read()
        medals = [
            medal
            for medal in account.medals
            if isinstance(medal, str) and medal
        ]
        # Orden estable, sin duplicados.
        seen: set[str] = set()
        clean_medals: list[str] = []
        for medal in medals:
            if medal in seen:
                continue
            seen.add(medal)
            clean_medals.append(medal)
        stored = Account(
            account.name,
            max(0, account.biscuits),
            {
                key: value
                for key, value in account.levels.items()
                if isinstance(key, str) and type(value) is int and value > 0
            },
            clean_medals,
        )
        for index, row in enumerate(data.accounts):
            if row.name == stored.name:
                data.accounts[index] = stored
                self._write(data)
                return
        raise AccountError(COPY_MISSING)

    def _read(self) -> _File:
        if not self._path.exists():
            return _File(None, [])
        try:
            text = self._path.read_text(encoding="utf-8")
            raw = json.loads(text)
        except (OSError, ValueError, TypeError):
            self._quarantine()
            return _File(None, [])
        if not isinstance(raw, dict):
            self._quarantine()
            return _File(None, [])
        accounts: list[Account] = []
        seen: set[str] = set()
        rows = raw.get("accounts")
        if isinstance(rows, list):
            for item in rows:
                account = _parse_account(item)
                if account is None or account.name in seen:
                    continue
                seen.add(account.name)
                accounts.append(account)
        active = raw.get("active")
        active_name = normalize_name(active) if isinstance(active, str) else None
        if active_name not in seen:
            active_name = None
        return _File(active_name, accounts)

    def _quarantine(self) -> None:
        """Guarda el archivo roto y deja el camino libre para arrancar de cero."""
        if not self._path.exists():
            return
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        backup = self._path.with_name(f"accounts.corrupt-{stamp}.json")
        try:
            shutil.move(str(self._path), str(backup))
        except OSError:
            try:
                self._path.unlink()
            except OSError:
                pass

    def _write(self, data: _File) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "active": data.active,
            "accounts": [
                {
                    "name": account.name,
                    "biscuits": account.biscuits,
                    "levels": account.levels,
                    "medals": account.medals,
                }
                for account in data.accounts
            ],
        }
        temporary = self._path.with_suffix(".json.tmp")
        temporary.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        temporary.replace(self._path)


def _parse_account(raw: object) -> Account | None:
    if not isinstance(raw, dict):
        return None
    name = raw.get("name")
    if not isinstance(name, str):
        return None
    name = normalize_name(name)
    if len(name) < NAME_MIN:
        return None
    biscuits = raw.get("biscuits", 0)
    if type(biscuits) is not int or biscuits < 0:
        biscuits = 0
    levels: dict[str, int] = {}
    raw_levels = raw.get("levels", {})
    if isinstance(raw_levels, dict):
        for key, value in raw_levels.items():
            if isinstance(key, str) and type(value) is int and value > 0:
                levels[key] = value
    medals: list[str] = []
    raw_medals = raw.get("medals", [])
    if isinstance(raw_medals, list):
        seen: set[str] = set()
        for item in raw_medals:
            if isinstance(item, str) and item and item not in seen:
                seen.add(item)
                medals.append(item)
    return Account(name, biscuits, levels, medals)
