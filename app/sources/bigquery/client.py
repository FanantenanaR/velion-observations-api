"""Gateway BigQuery : encapsule l'auth, le client SDK et l'exécution de queries.

Ne contient AUCUN SQL spécifique au domaine ni mapping. C'est juste une
passerelle générique sur BigQuery, réutilisable par toutes les sources
BQ qu'on aura besoin (BigQueryObservationSource, futur BigQueryEssaiSource, etc.).

Équivalent conceptuel : une Session SQLAlchemy. Les Repositories l'utilisent.
"""
from __future__ import annotations

import asyncio
from typing import Iterable

from google.cloud import bigquery

from app.config import Settings


class BigQueryClient:
    """Wrapper async sur google.cloud.bigquery.Client.

    Connaît l'environnement (project GCP, dataset cible) et expose des
    primitives génériques : exécuter une query paramétrée, résoudre un FQN
    de table, prober la connectivité.
    """

    def __init__(self, settings: Settings) -> None:
        self._client = bigquery.Client(project=settings.gcp_project)
        self._dataset = settings.bq_dataset

    @property
    def dataset(self) -> str:
        """Dataset FQN configuré (ex: 'bigquery-public-data.usda_nass_agriculture')."""
        return self._dataset

    def table_fqn(self, table_name: str) -> str:
        """Construit le FQN backtické d'une table du dataset configuré.

        Exemple : table_fqn('crops') -> '`bigquery-public-data.usda_nass_agriculture.crops`'
        """
        return f"`{self._dataset}.{table_name}`"

    async def query(
        self,
        sql: str,
        params: Iterable[bigquery.ScalarQueryParameter] | None = None,
    ) -> list[bigquery.Row]:
        """Exécute une query paramétrée et retourne toutes les lignes.

        Args:
            sql: la requête SQL (avec params @nom)
            params: les ScalarQueryParameter à injecter (typés, anti-SQL-injection)

        Returns:
            La liste des lignes (lazy -> matérialisée).

        Notes:
            Le client BigQuery SDK n'est pas natif async — on wrap via
            asyncio.to_thread pour ne pas bloquer l'event loop FastAPI.
        """
        job_config = bigquery.QueryJobConfig(query_parameters=list(params or []))

        def _run() -> list[bigquery.Row]:
            job = self._client.query(sql, job_config=job_config)
            return list(job.result())

        return await asyncio.to_thread(_run)

    async def query_scalar(
        self,
        sql: str,
        params: Iterable[bigquery.ScalarQueryParameter] | None = None,
        column: str = "value",
    ) -> object:
        """Exécute une query et retourne UN seul scalaire (1ère ligne, 1 colonne).

        Pratique pour les SELECT COUNT(*), SELECT 1, etc.
        """
        rows = await self.query(sql, params)
        if not rows:
            raise RuntimeError(f"Scalar query returned no row: {sql.strip()[:80]}...")
        return rows[0][column]

    async def health(self) -> dict:
        """Probe générique : SELECT 1.

        Retourne un dict avec 'ok' bool et 'dataset' pour traçabilité.
        Les sources spécialisées peuvent enrichir avec leurs propres champs.
        """

        def _probe() -> dict:
            try:
                job = self._client.query("SELECT 1 AS ok")
                next(iter(job.result()))
                return {"ok": True, "dataset": self._dataset}
            except Exception as exc:  # noqa: BLE001 — production handlers in Module 5
                return {"ok": False, "dataset": self._dataset, "error": str(exc)}

        return await asyncio.to_thread(_probe)
