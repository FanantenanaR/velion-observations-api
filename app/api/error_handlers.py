"""Exception handlers : convertissent les exceptions domaine en ApiResponse[None].

Tous les endpoints renvoient la même envelope (status='error', error=ErrorDetail)
quel que soit le type d'erreur. Cohérence du contrat exposé au client.
"""
from __future__ import annotations

import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.domain.response import ApiResponse, ErrorCode, ErrorDetail, ResponseStatus
from app.exceptions import (
    InvalidFilterError,
    LegacyParseError,
    SourceUnavailableError,
)

logger = logging.getLogger(__name__)


def _error_response(
    http_status: int,
    code: ErrorCode,
    message: str,
    details: dict | None = None,
) -> JSONResponse:
    """Construit une réponse JSON ApiResponse[None] pour une erreur."""
    payload = ApiResponse[None](
        status=ResponseStatus.ERROR,
        message=message,
        data=None,
        size=None,
        pagination=None,
        error=ErrorDetail(code=code, message=message, details=details),
    )
    return JSONResponse(
        status_code=http_status,
        content=payload.model_dump(mode="json"),
    )


async def invalid_filter_handler(request: Request, exc: InvalidFilterError) -> JSONResponse:
    logger.warning("InvalidFilter on %s: %s", request.url.path, exc)
    return _error_response(
        http_status=status.HTTP_400_BAD_REQUEST,
        code=ErrorCode.INVALID_FILTER,
        message=str(exc),
    )


async def source_unavailable_handler(
    request: Request, exc: SourceUnavailableError
) -> JSONResponse:
    logger.error("SourceUnavailable on %s: %s", request.url.path, exc)
    return _error_response(
        http_status=status.HTTP_503_SERVICE_UNAVAILABLE,
        code=ErrorCode.SOURCE_UNAVAILABLE,
        message=str(exc),
    )


async def legacy_parse_handler(request: Request, exc: LegacyParseError) -> JSONResponse:
    logger.error("LegacyParseError on %s: %s", request.url.path, exc)
    return _error_response(
        http_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        code=ErrorCode.INTERNAL_ERROR,
        message="A legacy record could not be parsed.",
        details={"reason": str(exc)},
    )


async def request_validation_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Wrappe les ValidationErrors Pydantic (query/body invalides) en ApiResponse."""
    logger.info("ValidationError on %s: %s", request.url.path, exc.errors())
    return _error_response(
        http_status=status.HTTP_422_UNPROCESSABLE_ENTITY,
        code=ErrorCode.INVALID_FILTER,
        message="Request validation failed.",
        details={"errors": exc.errors()},
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled exception on %s", request.url.path)
    return _error_response(
        http_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        code=ErrorCode.INTERNAL_ERROR,
        message="An unexpected error occurred.",
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Enregistre tous les handlers sur l'app FastAPI."""
    app.add_exception_handler(InvalidFilterError, invalid_filter_handler)
    app.add_exception_handler(SourceUnavailableError, source_unavailable_handler)
    app.add_exception_handler(LegacyParseError, legacy_parse_handler)
    app.add_exception_handler(RequestValidationError, request_validation_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
