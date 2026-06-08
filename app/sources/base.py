"""Port secondaire : interface des sources d'observations.

L'API ne sait rien de l'implémentation concrète. Toute source (BigQuery,
MockLegacy, InMemory, future API legacy) doit implémenter cette interface.
"""
from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.models import Observation, ObservationFilters


class ObservationSource(ABC):
    """Contrat d'une source d'observations terrain.

    Méthodes :
    - list_observations : retourne une page de résultats + le total non paginé
      (le total est nécessaire pour construire la Pagination côté API).
    - health : probe de santé propre à la source.
    """

    @abstractmethod
    async def list_observations(
        self, filters: ObservationFilters
    ) -> tuple[list[Observation], int | None]:
        """Retourne (page_data, total_items_avant_pagination).

        Les filtres `date_min`/`date_max`/`essai_id` ainsi que la pagination
        `limit`/`offset` sont appliqués par la source (en SQL si BigQuery,
        en mémoire si InMemory, etc.).
        Si filters.include_total est False, l'implémentation DOIT retourner
        None pour total_items (et éviter d'effectuer le COUNT côté source).
        """
        ...

    @abstractmethod
    async def health(self) -> dict:
        """Vérifie la connectivité / disponibilité de la source.

        Retourne un dict avec au minimum :
        - 'source': nom de la source (str)
        - 'ok': bool
        """
        ...
