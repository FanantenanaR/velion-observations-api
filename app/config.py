"""Configuration globale — paramètres d'environnement uniquement.

Cette config ne contient PAS la topologie (noms de tables, schémas).
La topologie de chaque source est encodée dans le code de l'adapter
(voir app/sources/*). Cela reflète la pratique ORM/repository standard :
- config = "où je me connecte"
- code adapter = "quelles tables je requête et comment"
"""
from __future__ import annotations

from enum import Enum
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class SourceKind(str, Enum):
    """Backends de données supportés."""

    IN_MEMORY = "in_memory"
    BIGQUERY = "bigquery"
    MOCK_LEGACY = "mock_legacy"


class Settings(BaseSettings):
    """Paramètres d'environnement de l'application."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    source_kind: SourceKind = Field(
        default=SourceKind.BIGQUERY,
        description="Backend actif pour la résolution des observations.",
    )
    gcp_project: str | None = Field(
        default=None,
        description="ID du projet GCP utilisé pour lancer les queries.",
    )
    bq_dataset: str = Field(
        default="bigquery-public-data.usda_nass_agriculture",
        description="Dataset BigQuery cible (FQN: project.dataset).",
    )
    mock_fixtures_path: str = Field(
        default="./data/mock_legacy_fixtures.json",
        description="Chemin vers les fixtures de la source mock legacy.",
    )
    log_level: str = Field(
        default="INFO",
        description="Niveau de logs (DEBUG, INFO, WARNING, ERROR, CRITICAL).",
    )


@lru_cache
def get_settings() -> Settings:
    """Retourne l'instance unique de Settings (Singleton via lru_cache)."""
    return Settings()
