"""Source d'observations BigQuery sur USDA NASS Agriculture / crops.

Encapsule :
- La topologie (table `crops` du dataset USDA NASS)
- Le SQL spécifique au domaine
- L'orchestration (count + fetch + mapping)

Utilise BigQueryClient comme passerelle générique. Si demain on ajoute
une autre ressource BigQuery (BigQueryEssaiSource), elle partagera le
même client et ce fichier ne change pas.
"""

from __future__ import annotations

import asyncio 

from google.cloud import bigquery

from app.domain.models import Observation, ObservationFilters
from app.sources.base import ObservationSource
from app.sources.bigquery.client import BigQueryClient
from app.sources.bigquery.mapping import row_to_observation


class BigQueryObservationSource(ObservationSource):
    """Source d'observations terrain via BigQuery (dataset USDA NASS crops)."""

    # Topologie : encodée dans la classe, pas dans la config
    _FACT_TABLE = "crops"

    def __init__(self, client: BigQueryClient) -> None:
        self._client = client

    @property
    def _fact_fqn(self) -> str:
        return self._client.table_fqn(self._FACT_TABLE)

    # Port methods (ObservationSource)
    async def list_observations(
        self, filters: ObservationFilters
    ) -> tuple[list[Observation], int | None]:
        """Retourne (page_data, total_or_None).

        Si filters.include_total=True : lance count + fetch en parallèle.
        Si False : skip le COUNT.
        """
        if filters.include_total:
            total, rows = await asyncio.gather(
                self._fetch_count(filters),
                self._fetch_rows(filters),
            )
        else:
            rows = await self._fetch_rows(filters)
            total = None
        return [row_to_observation(r) for r in rows], total

    async def health(self) -> dict:
        """Health = health du client BQ + métadonnées de la source."""
        client_health = await self._client.health()
        return {
            "source": "bigquery",
            "table": self._FACT_TABLE,
            **client_health,
        }
    
    # Obtenir le nombre total de manière asynchrone (pour pagination)
    async def _fetch_count(self, filters: ObservationFilters) -> int:
        scalar = await self._client.query_scalar(
            self._count_sql(),
            params=self._params_for_filters(filters, with_pagination=False),
            column="total",
        )
        return int(scalar)

    # Obtenir les lignes de données de manière asynchrone
    async def _fetch_rows(self, filters: ObservationFilters):
        return await self._client.query(
            self._fetch_sql(),
            params=self._params_for_filters(filters, with_pagination=True),
        )

    # SQL building (Observation-specific)
    def _count_sql(self) -> str:
        """Query COUNT(*) avec les mêmes filtres que _fetch_sql."""
        return f"""
        SELECT COUNT(*) AS total
        FROM {self._fact_fqn}
        WHERE agg_level_desc = 'COUNTY'
          AND value IS NOT NULL
          AND (@essai_id IS NULL OR state_alpha = @essai_id)
          AND (@year_min IS NULL OR year >= @year_min)
          AND (@year_max IS NULL OR year <= @year_max)
        """

    def _fetch_sql(self) -> str:
        """Query principale paginée — projette les colonnes vers le contrat."""
        return f"""
        SELECT
          state_alpha AS essai_id,
          county_name AS parcelle_id,
          DATE(year, 12, 31) AS date_observation,
          value AS mesure_valeur,
          CONCAT(commodity_desc, '_', statisticcat_desc) AS mesure_type
        FROM {self._fact_fqn}
        WHERE agg_level_desc = 'COUNTY'
          AND value IS NOT NULL
          AND (@essai_id IS NULL OR state_alpha = @essai_id)
          AND (@year_min IS NULL OR year >= @year_min)
          AND (@year_max IS NULL OR year <= @year_max)
        ORDER BY year DESC, county_name ASC
        LIMIT @limit OFFSET @offset
        """

    @staticmethod
    def _params_for_filters(
        filters: ObservationFilters, *, with_pagination: bool
    ) -> list[bigquery.ScalarQueryParameter]:
        """Construit les ScalarQueryParameter à partir des filtres typés."""
        year_min = filters.date_min.year if filters.date_min else None
        year_max = filters.date_max.year if filters.date_max else None

        params: list[bigquery.ScalarQueryParameter] = [
            bigquery.ScalarQueryParameter("essai_id", "STRING", filters.essai_id),
            bigquery.ScalarQueryParameter("year_min", "INT64", year_min),
            bigquery.ScalarQueryParameter("year_max", "INT64", year_max),
        ]
        if with_pagination:
            params.extend(
                [
                    bigquery.ScalarQueryParameter("limit", "INT64", filters.limit),
                    bigquery.ScalarQueryParameter("offset", "INT64", filters.offset),
                ]
            )
        return params
