"""Exceptions du domaine.

Conventions :
- Chaque exception domaine porte un message clair.
- Elles seront mappées vers des ApiResponse[None] structurés par les handlers
  FastAPI (cf. app/api/error_handlers.py).
"""


class LegacyParseError(Exception):
    """Levée quand un record legacy ne peut pas être normalisé en Observation."""


class SourceUnavailableError(Exception):
    """Levée quand la source de données backend est indisponible.

    Exemples : timeout BigQuery, fichier de fixtures manquant, credentials
    invalides, quota dépassé. Le code mappé est 503 SERVICE_UNAVAILABLE.
    """


class InvalidFilterError(Exception):
    """Levée quand un filtre de requête est invalide au niveau métier.

    Exemples : date_min > date_max, valeur hors référentiel.
    Différent des erreurs de validation Pydantic structurelles (types, formats),
    qui sont gérées par FastAPI RequestValidationError. Code mappé : 400.
    """
