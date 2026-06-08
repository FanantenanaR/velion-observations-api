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


@router.get("", response_model=ApiResponse[list[Observation]])
async def list_observations(
    essai_id: str | None = Query(default=None),
    date_min: date | None = Query(default=None),
    date_max: date | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    include_total: bool = Query(
        default=True,
        description="Si false, l'API skip la query COUNT (économie coût/latence).",
    ),
    source: ObservationSource = Depends(get_source_dependency),
) -> ApiResponse[list[Observation]]:
    filters = ObservationFilters(
        essai_id=essai_id,
        date_min=date_min,
        date_max=date_max,
        limit=limit,
        offset=offset,
        include_total=include_total,
    )
    page_data, total_items = await source.list_observations(filters)
    pagination = _build_pagination(filters, total_items, len(page_data))

    return ApiResponse[list[Observation]](
        status=ResponseStatus.SUCCESS,
        message="Observations retrieved successfully.",
        data=page_data,
        size=len(page_data),
        pagination=pagination,
    )


def _build_pagination(
    filters: ObservationFilters,
    total_items: int | None,
    page_size: int,
) -> Pagination:
    limit = filters.limit if filters.limit > 0 else 1
    page = (filters.offset // limit) + 1

    if total_items is None:
        # Mode skip-count : has_next basé sur page_size vs limit
        # Note : pour être 100% fiable, il faudrait fetch limit+1 et trim.
        # Ici on assume has_next=True si page complète
        has_next = page_size >= limit
        total_pages = None
    else:
        total_pages = (total_items + limit - 1) // limit if total_items > 0 else 0
        has_next = page < total_pages if total_pages else False

    return Pagination(
        page=page,
        limit=filters.limit,
        total_items=total_items,
        total_pages=total_pages,
        has_next=has_next,
    )

