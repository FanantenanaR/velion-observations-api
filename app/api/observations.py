"""Routes de l'API observations."""
from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Query

from app.domain.models import Observation, ObservationFilters
from app.domain.response import ApiResponse, Pagination, ResponseStatus

router = APIRouter(prefix="/observations", tags=["observations"])


@router.get(
    "",
    response_model=ApiResponse[list[Observation]],
    summary="Liste les observations selon les filtres fournis",
)
async def list_observations(
    essai_id: str | None = Query(default=None, description="Filtre exact sur l'essai (ex: 'IA')."),
    date_min: date | None = Query(default=None, description="Date minimum (incluse)."),
    date_max: date | None = Query(default=None, description="Date maximum (incluse)."),
    limit: int = Query(default=100, description="Nombre maximum d'observations par page."),
    offset: int = Query(default=0, description="Décalage pour pagination (nombre d'éléments à sauter)."),
) -> ApiResponse[list[Observation]]:
    """Retourne une page d'observations enveloppée dans ApiResponse.

    Module 1 : data mockée pour valider le contrat exposé.
    """
    filters = ObservationFilters(
        essai_id=essai_id,
        date_min=date_min,
        date_max=date_max,
        limit=limit,
        offset=offset,
    )
    page_data, total_items = _mock_observations(filters)

    pagination = _build_pagination(filters, total_items)

    return ApiResponse[list[Observation]](
        status=ResponseStatus.SUCCESS,
        message="Observations retrieved successfully.",
        data=page_data,
        size=len(page_data),
        pagination=pagination,
    )


def _mock_observations(filters: ObservationFilters) -> tuple[list[Observation], int]:
    """Retourne (page_data, total_items) — data mockée Module 1."""
    samples: list[Observation] = [
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

    filtered = samples
    if filters.essai_id:
        filtered = [o for o in filtered if o.essai_id == filters.essai_id]
    if filters.date_min:
        filtered = [o for o in filtered if o.date_observation >= filters.date_min]
    if filters.date_max:
        filtered = [o for o in filtered if o.date_observation <= filters.date_max]

    total = len(filtered)
    page_data = filtered[filters.offset : filters.offset + filters.limit]
    return page_data, total


def _build_pagination(filters: ObservationFilters, total_items: int) -> Pagination:
    """Construit l'objet Pagination depuis les filtres + total."""
    limit = filters.limit if filters.limit > 0 else 1
    page = (filters.offset // limit) + 1
    total_pages = (total_items + limit - 1) // limit if total_items > 0 else 0

    return Pagination(
        page=page,
        limit=filters.limit,
        total_items=total_items,
        total_pages=total_pages,
    )
