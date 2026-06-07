"""Modèles Pydantic exposés au client de l'API.

Ces modèles définissent le CONTRAT STABLE qui est servi au frontend,
indépendamment du backend (BigQuery, mock legacy, ou demain une autre source).
"""
from __future__ import annotations

from datetime import date
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class Observation(BaseModel):
    """Une observation terrain mesurée à une date donnée sur une parcelle.

    C'est le format de réponse exposé au client de l'API.
    """

    model_config = ConfigDict(frozen=True, populate_by_name=True)

    essai_id: Annotated[
        str,
        Field(
            description="Identifiant de l'essai (cadre expérimental régional). "
            "Dans le mapping USDA NASS, correspond au code état US (ex: 'IA', 'TX').",
            examples=["IA", "TX"],
            min_length=1,
            max_length=10,
        ),
    ]
    parcelle_id: Annotated[
        str,
        Field(
            description="Identifiant de la parcelle (lieu physique d'observation). "
            "Dans le mapping USDA NASS, correspond au nom du comté.",
            examples=["LINN", "POLK", "PALO ALTO"],
            min_length=1,
            max_length=100,
        ),
    ]
    date_observation: Annotated[
        date,
        Field(
            description="Date de l'observation (au format ISO YYYY-MM-DD).",
            examples=["2022-12-31"],
        ),
    ]
    mesure_valeur: Annotated[
        float | None,
        Field(
            description="Valeur numérique de la mesure. "
            "Peut être None si la donnée a été supprimée pour confidentialité.",
            examples=[185.2, 26997000.0],
        ),
    ] = None
    mesure_type: Annotated[
        str,
        Field(
            description="Type de mesure, composé de la culture et de la statistique. "
            "Format : '<COMMODITY>_<STATISTIC>'.",
            examples=["CORN_YIELD", "CORN_PRODUCTION", "CORN_AREA_PLANTED"],
            min_length=1,
            max_length=100,
        ),
    ]


class ObservationFilters(BaseModel):
    """Filtres pour récupérer des observations via l'API.

    Tous les filtres sont optionnels — l'absence de filtre signifie
    'tout retourner', ce qui sera plafonné par `limit` et `require_partition_filter`
    côté source pour éviter les scans massifs.
    """

    model_config = ConfigDict(extra="forbid")

    essai_id: Annotated[
        str | None,
        Field(
            default=None,
            description="Filtre exact sur l'essai (code 2 lettres).",
            min_length=1,
            max_length=10,
        ),
    ] = None
    date_min: Annotated[
        date | None,
        Field(
            default=None,
            description="Date minimum (incluse) de l'observation.",
        ),
    ] = None
    date_max: Annotated[
        date | None,
        Field(
            default=None,
            description="Date maximum (incluse) de l'observation.",
        ),
    ] = None
    limit: Annotated[
        int,
        Field(
            default=100,
            ge=1,
            le=1000,
            description="Nombre maximum d'observations par page.",
        ),
    ] = 100
    offset: Annotated[
        int,
        Field(
            default=0,
            ge=0,
            description="Décalage pour pagination (nombre d'éléments à sauter).",
        ),
    ] = 0
    include_total: Annotated[
        bool,
        Field(
            default=True,
            description=(
                "Si False, l'API ne calcule pas le total_items (skip la query COUNT). "
                "Utile pour réduire le coût/la latence quand seul le 'next/prev' est nécessaire "
                "(scroll infini, pas d'affichage 'page X / Y')."
            ),
        ),
    ] = True

