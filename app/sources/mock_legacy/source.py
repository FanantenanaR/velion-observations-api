"""Source d'observations depuis un fichier JSON legacy.

Démontre la stabilité du contrat exposé : le format de stockage interne est
volontairement différent (camelCase, Unix timestamps, dotted metrics).
L'adapter normalise tout ça vers Observation au constructor.
"""
from __future__ import annotations

import logging

from app.config import Settings
from app.domain.models import Observation, ObservationFilters
from app.exceptions import LegacyParseError
from app.sources.base import ObservationSource
from app.sources.mock_legacy.loader import MockLegacyLoader
from app.sources.mock_legacy.mapping import legacy_to_observation

logger = logging.getLogger(__name__)


class MockLegacyObservationSource(ObservationSource):
    """Source de fixtures JSON legacy normalisées vers Observation."""

    def __init__(self, settings: Settings) -> None:
        self._loader = MockLegacyLoader(settings.mock_fixtures_path)
        self._observations: list[Observation] = self._normalize_all()

    def _normalize_all(self) -> list[Observation]:
        """Pré-normalise tous les records ; skippe + logge ceux qui sont invalides."""
        result: list[Observation] = []
        skipped = 0
        for i, record in enumerate(self._loader.records):
            try:
                result.append(legacy_to_observation(record))
            except LegacyParseError as e:
                skipped += 1
                logger.warning(
                    "MockLegacy: skipping invalid record #%d (%s) — %s",
                    i, record.get("experimentCode", "<no-code>"), e,
                )
        if skipped:
            logger.warning("MockLegacy: %d/%d records skipped", skipped, len(self._loader.records))
        return result

    async def list_observations(
        self, filters: ObservationFilters
    ) -> tuple[list[Observation], int | None]:
        filtered = self._observations
        if filters.essai_id:
            filtered = [o for o in filtered if o.essai_id == filters.essai_id]
        if filters.date_min:
            filtered = [o for o in filtered if o.date_observation >= filters.date_min]
        if filters.date_max:
            filtered = [o for o in filtered if o.date_observation <= filters.date_max]

        total = len(filtered) if filters.include_total else None
        page = filtered[filters.offset : filters.offset + filters.limit]
        return page, total

    async def health(self) -> dict:
        return {
            "source": "mock_legacy",
            "ok": self._loader.is_loaded,
            "fixtures_path": self._loader.path,
            "raw_records_count": len(self._loader.records),
            "valid_observations_count": len(self._observations),
        }
