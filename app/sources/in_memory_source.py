"""Source en mémoire — adapter durable pour tests, démos, fallback offline.

C'est une implémentation 'jouet' qui contient des observations hardcodées.
À ne pas confondre avec MockLegacySource (Module 4) qui simulera un format
de données étranger nécessitant une normalisation.
"""
from __future__ import annotations

from datetime import date

from app.domain.models import Observation, ObservationFilters
from app.sources.base import ObservationSource

_SAMPLES: list[Observation] = [
    Observation(
        essai_id="IA",
        parcelle_id="LINN",
        date_observation=date(2022, 12, 31),
        mesure_valeur=215.4,
        mesure_type="CORN_YIELD",
    ),
    Observation(
        essai_id="IA",
        parcelle_id="POLK",
        date_observation=date(2022, 12, 31),
        mesure_valeur=185.2,
        mesure_type="CORN_YIELD",
    ),
    Observation(
        essai_id="IA",
        parcelle_id="LINN",
        date_observation=date(2022, 12, 31),
        mesure_valeur=143000.0,
        mesure_type="CORN_AREA_PLANTED",
    ),
    Observation(
        essai_id="IA",
        parcelle_id="CHEROKEE",
        date_observation=date(2022, 12, 31),
        mesure_valeur=26997000.0,
        mesure_type="CORN_PRODUCTION",
    ),
    Observation(
        essai_id="TX",
        parcelle_id="TRAVIS",
        date_observation=date(2022, 12, 31),
        mesure_valeur=542.0,
        mesure_type="COTTON_YIELD",
    ),
]


class InMemoryObservationSource(ObservationSource):
    """Source statique en mémoire (utile pour tests et smoke checks)."""

    async def list_observations(
        self, filters: ObservationFilters
    ) -> tuple[list[Observation], int]:
        filtered = _SAMPLES
        if filters.essai_id:
            filtered = [o for o in filtered if o.essai_id == filters.essai_id]
        if filters.date_min:
            filtered = [o for o in filtered if o.date_observation >= filters.date_min]
        if filters.date_max:
            filtered = [o for o in filtered if o.date_observation <= filters.date_max]

        total = len(filtered)
        page = filtered[filters.offset : filters.offset + filters.limit]
        return page, total

    async def health(self) -> dict:
        return {
            "source": "in_memory",
            "ok": True,
            "samples_count": len(_SAMPLES),
        }
