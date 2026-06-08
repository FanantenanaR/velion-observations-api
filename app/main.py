"""Point d'entrée de l'application FastAPI."""
from __future__ import annotations

from fastapi import Depends, FastAPI

from app.api import observations
from app.api.error_handlers import register_exception_handlers
from app.config import get_settings
from app.domain.response import ApiResponse, ResponseStatus
from app.logging_config import configure_logging
from app.middleware import CorrelationIdMiddleware
from app.sources.base import ObservationSource

# Configuration globale (logs + settings)
_settings = get_settings()
configure_logging(_settings.log_level)


app = FastAPI(
    title="Velion Observations API",
    description=(
        "API d'abstraction multi-sources pour observations terrain agronomiques. "
        "Le contrat exposé est stable indépendamment du backend."
    ),
    version="0.1.0",
)

app.add_middleware(CorrelationIdMiddleware)
register_exception_handlers(app)

app.include_router(observations.router)



@app.get("/healthz", response_model=ApiResponse[dict], tags=["health"])
async def healthcheck(
    source: ObservationSource = Depends(observations.get_source_dependency),
) -> ApiResponse[dict]:
    """Probe de santé applicative + connectivité backend."""
    source_health = await source.health()
    ok = bool(source_health.get("ok", False))

    return ApiResponse[dict](
        status=ResponseStatus.SUCCESS if ok else ResponseStatus.ERROR,
        message="Service is healthy." if ok else "Backend source is not healthy.",
        data={
            "version": "0.1.0",
            "source": source_health,
        },
    )


@app.get("/", include_in_schema=False)
async def root() -> dict:
    """Racine — pointe vers les ressources utiles."""
    return {
        "name": "velion-observations-api",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/healthz",
    }
