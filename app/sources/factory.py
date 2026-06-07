"""Factory : choisit l'implémentation concrète de la source selon la config."""
from __future__ import annotations

from app.config import Settings, SourceKind
from app.sources.base import ObservationSource
from app.sources.bigquery.client import BigQueryClient
from app.sources.bigquery.observation_source import BigQueryObservationSource
from app.sources.in_memory_source import InMemoryObservationSource


def get_source(settings: Settings) -> ObservationSource:
    """Retourne l'instance de source selon settings.source_kind.

    BigQuery est composé : on crée un BigQueryClient générique (gateway)
    puis on l'injecte dans BigQueryObservationSource (repository).
    Si demain on ajoute d'autres sources BQ (BigQueryEssaiSource,
    BigQueryParcelleSource, etc.), elles partageront le même client.
    """
    if settings.source_kind == SourceKind.IN_MEMORY:
        return InMemoryObservationSource()

    if settings.source_kind == SourceKind.BIGQUERY:
        client = BigQueryClient(settings)
        return BigQueryObservationSource(client)

    # MockLegacy arrive dans le Module 4
    raise NotImplementedError(
        f"Source '{settings.source_kind.value}' not yet implemented. "
        f"Set SOURCE_KIND to one of: in_memory, bigquery."
    )
