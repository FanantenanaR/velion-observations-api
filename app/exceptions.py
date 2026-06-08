"""Exceptions du domaine.

Pour l'instant, seul LegacyParseError est défini (utilisé par Module 4).
SourceUnavailableError et InvalidFilterError seront ajoutées en Module 5
et wirées aux exception handlers FastAPI.
"""


class LegacyParseError(Exception):
    """Levée quand un record legacy ne peut pas être normalisé en Observation."""
