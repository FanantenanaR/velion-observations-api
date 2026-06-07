"""Factory : choisit l'implémentation concrète de la source selon la config."""
from __future__ import annotations

from app.config import Settings, SourceKind
from app.sources.base import ObservationSource
from app.sources.in_memory_source import InMemoryObservationSource


def get_source(settings: Settings) -> ObservationSource:
    """Retourne l'instance de source selon settings.source_kind.

    Module 2 : seule l'implémentation InMemory est disponible.
    Modules 3-4 : BigQuerySource et MockLegacySource seront branchées ici.
    """
    if settings.source_kind == SourceKind.IN_MEMORY:
        return InMemoryObservationSource()

    raise NotImplementedError(
        f"Source '{settings.source_kind.value}' not yet implemented. "
        f"Set SOURCE_KIND=in_memory in your .env for the current module."
    )
