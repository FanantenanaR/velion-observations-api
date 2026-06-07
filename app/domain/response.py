"""Envelope de réponse normalisée pour toutes les routes de l'API.

Convention : toute réponse de l'API a la même forme, qu'elle porte un objet,
un tableau, ou une erreur. Le client peut donc parser uniformément.

Forme :
{
  "status": "success" | "error",
  "message": "<message contextuel>",
  "data": <objet | tableau | null>,
  "size": <int | null>,           # taille de data si tableau
  "pagination": <Pagination | null>,
  "error": <ErrorDetail | null>   # rempli si status="error"
}
"""
from __future__ import annotations

from enum import Enum
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")

class ResponseStatus(str, Enum):
    """Statut d'une réponse API."""

    SUCCESS = "success"
    ERROR = "error"

class ErrorCode(str, Enum):
    """Codes d'erreur normalisés exposés au client.

    Liste ouverte — sera enrichie au fur et à mesure des besoins.
    """

    MISSING_VALUE = "MISSING_VALUE"
    INVALID_FILTER = "INVALID_FILTER"
    INVALID_DATE_RANGE = "INVALID_DATE_RANGE"
    SOURCE_UNAVAILABLE = "SOURCE_UNAVAILABLE"
    NOT_FOUND = "NOT_FOUND"
    INTERNAL_ERROR = "INTERNAL_ERROR"

class ErrorDetail(BaseModel):
    """Détail d'une erreur exposée au client."""

    code: ErrorCode = Field(
        description="Code machine de l'erreur (utilisé par le client pour brancher de la logique).",
        examples=["MISSING_VALUE", "SOURCE_UNAVAILABLE"],
    )
    message: str = Field(
        description="Message humain expliquant l'erreur.",
        examples=["The parameter 'essai_id' is required."],
    )
    details: dict | None = Field(
        default=None,
        description="Contexte additionnel optionnel (champ fautif, valeur reçue, etc.).",
    )

class Pagination(BaseModel):
    """Informations de pagination pour une réponse paginée."""

    page: int = Field(
        description="Numéro de la page courante (1-indexé).",
        examples=[1],
    )
    limit: int = Field(
        description="Nombre d'éléments par page.",
        examples=[100],
    )
    total_items: int = Field(
        description="Nombre total d'éléments correspondant aux filtres (avant pagination).",
        examples=[1158],
    )
    total_pages: int = Field(
        description="Nombre total de pages.",
        examples=[12],
    )

class ApiResponse(BaseModel, Generic[T]):
    """Envelope unique pour toutes les réponses de l'API.

    Le type T paramètre le contenu du champ `data` (Observation, list[Observation],
    HealthcheckData, etc.).
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    status: ResponseStatus = Field(
        default=ResponseStatus.SUCCESS,
        description="Statut global de la réponse.",
    )
    message: str = Field(
        description="Message contextuel humain (toujours présent).",
    )
    data: T | None = Field(
        default=None,
        description="Charge utile : objet, tableau, ou null en cas d'erreur.",
    )
    size: int | None = Field(
        default=None,
        description="Taille de `data` si c'est un tableau, sinon null.",
    )
    pagination: Pagination | None = Field(
        default=None,
        description="Métadonnées de pagination si la ressource est paginée.",
    )
    error: ErrorDetail | None = Field(
        default=None,
        description="Détail de l'erreur si status='error', sinon null.",
    )
