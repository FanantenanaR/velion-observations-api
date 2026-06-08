"""Middleware FastAPI : correlation ID par requête.

Génère un UUID v4 si le header X-Correlation-Id n'est pas fourni par le client.
L'ID est lié au contexte structlog (visible dans tous les logs de la requête)
et renvoyé dans le header de réponse pour traçabilité bout-en-bout.
"""
from __future__ import annotations

import uuid

import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    HEADER = "X-Correlation-Id"

    async def dispatch(self, request: Request, call_next) -> Response:
        correlation_id = request.headers.get(self.HEADER) or str(uuid.uuid4())

        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            correlation_id=correlation_id,
            method=request.method,
            path=request.url.path,
        )

        response = await call_next(request)
        response.headers[self.HEADER] = correlation_id
        return response
