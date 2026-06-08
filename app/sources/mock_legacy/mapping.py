"""Mapping pure : record legacy (dict) -> Observation Pydantic.

Le format legacy diverge volontairement du contrat exposé :
- experimentCode 'EXP-IOWA-2022' -> essai_id 'IA'
- plotName 'linn-county' -> parcelle_id 'LINN'
- recordedAt 1672444800 (Unix) -> date_observation date(2022, 12, 31)
- value '185.2' (string) -> mesure_valeur 185.2 (float)
- metric 'corn.yield' -> mesure_type 'CORN_YIELD'

Cette fonction est testable unitairement sans aucun I/O.
"""
from __future__ import annotations

from datetime import date, datetime, timezone

from app.domain.models import Observation
from app.exceptions import LegacyParseError

_STATE_CODE_MAP = {
    "IOWA": "IA",
    "TEXAS": "TX",
    "KANSAS": "KS",
    "NEBRASKA": "NE",
}


def legacy_to_observation(record: dict) -> Observation:
    """Convertit un record legacy en Observation Pydantic.

    Lève LegacyParseError si le record est inexploitable (champ manquant,
    type invalide, valeur hors référentiel).
    """
    try:
        return Observation(
            essai_id=_parse_essai_id(record["experimentCode"]),
            parcelle_id=_normalize_plot(record["plotName"]),
            date_observation=_unix_to_date(record["recordedAt"]),
            mesure_valeur=_parse_value(record.get("value")),
            mesure_type=_normalize_metric(record["metric"]),
        )
    except (KeyError, ValueError, TypeError) as e:
        raise LegacyParseError(f"Cannot map record: {e}") from e


def _parse_essai_id(experiment_code: str) -> str:
    """'EXP-IOWA-2022' -> 'IA' (extrait le code état standard 2 lettres)."""
    parts = experiment_code.split("-")
    if len(parts) < 2:
        raise ValueError(f"Invalid experimentCode format: {experiment_code!r}")
    state_name = parts[1].upper()
    code = _STATE_CODE_MAP.get(state_name)
    if not code:
        raise ValueError(f"Unknown state in experimentCode: {state_name!r}")
    return code


def _normalize_plot(plot_name: str) -> str:
    """'linn-county' -> 'LINN' (strip suffix '-county', uppercase)."""
    return plot_name.split("-")[0].upper()


def _unix_to_date(ts: int) -> date:
    """Unix timestamp -> date (UTC)."""
    return datetime.fromtimestamp(int(ts), tz=timezone.utc).date()


def _parse_value(raw) -> float | None:
    """'185.2' -> 185.2. None ou '' -> None."""
    if raw is None or raw == "":
        return None
    return float(raw)


def _normalize_metric(metric: str) -> str:
    """'corn.yield' -> 'CORN_YIELD'."""
    return metric.upper().replace(".", "_")
