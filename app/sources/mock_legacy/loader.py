"""Loader : lit le fichier JSON des fixtures et expose les records bruts."""
from __future__ import annotations

import json
from pathlib import Path


class MockLegacyLoader:
    """Charge les fixtures JSON au constructor (eager) et expose les records bruts.

    Un seul accès I/O à la construction. Pour rafraîchir, il faut recréer
    l'instance — c'est le comportement attendu pour un source legacy "snapshot".
    """

    def __init__(self, fixtures_path: str | Path) -> None:
        self._path = Path(fixtures_path)
        self._records: list[dict] = self._load()

    def _load(self) -> list[dict]:
        if not self._path.exists():
            raise FileNotFoundError(
                f"Mock legacy fixtures not found at: {self._path.absolute()}"
            )
        with self._path.open(encoding="utf-8") as f:
            payload = json.load(f)
        return payload.get("records", [])

    @property
    def records(self) -> list[dict]:
        return self._records

    @property
    def path(self) -> str:
        return str(self._path)

    @property
    def is_loaded(self) -> bool:
        return bool(self._records)
