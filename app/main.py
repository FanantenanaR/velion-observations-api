"""Point d'entrée de l'application FastAPI."""
from __future__ import annotations

from fastapi import FastAPI

from app.api import observations
from app.domain.response import ApiResponse, ResponseStatus

app = FastAPI(
    title="Velion Observations API",
    description=(
        "API d'abstraction multi-sources pour observations terrain agronomiques. "
        "Le contrat exposé est stable indépendamment du backend."
    ),
    version="0.1.0",
)

app.include_router(observations.router)


@app.get("/healthz", response_model=ApiResponse[dict], tags=["health"])
async def healthcheck() -> ApiResponse[dict]:
    """Probe de santé basique de l'application."""
    return ApiResponse[dict](
        status=ResponseStatus.SUCCESS,
        message="Service is healthy.",
        data={"version": "0.1.0"},
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
