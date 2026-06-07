"""Routes de l'API observations."""
from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, Query

from app.config import Settings, get_settings
from app.domain.models import Observation, ObservationFilters
from app.domain.response import ApiResponse, Pagination, ResponseStatus
from app.sources.base import ObservationSource
from app.sources.factory import get_source

router = APIRouter(prefix="/observations", tags=["observations"])


def get_source_dependency(
    settings: Settings = Depends(get_settings),
) -> ObservationSource:
    """FastAPI dependency : résout la source active depuis les settings."""
    return get_source(settings)


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
    offset: int = Query(default=0, description="Décalage pour pagination."),
    source: ObservationSource = Depends(get_source_dependency),
) -> ApiResponse[list[Observation]]:
    """Récupère une page d'observations depuis la source active."""
    filters = ObservationFilters(
        essai_id=essai_id,
        date_min=date_min,
        date_max=date_max,
        limit=limit,
        offset=offset,
    )
    page_data, total_items = await source.list_observations(filters)
    pagination = _build_pagination(filters, total_items)

    return ApiResponse[list[Observation]](
        status=ResponseStatus.SUCCESS,
        message="Observations retrieved successfully.",
        data=page_data,
        size=len(page_data),
        pagination=pagination,
    )


def _build_pagination(filters: ObservationFilters, total_items: int) -> Pagination:
    """Construit la pagination depuis les filtres et le total non paginé."""
    limit = filters.limit if filters.limit > 0 else 1
    page = (filters.offset // limit) + 1
    total_pages = (total_items + limit - 1) // limit if total_items > 0 else 0

    return Pagination(
        page=page,
        limit=filters.limit,
        total_items=total_items,
        total_pages=total_pages,
    )
