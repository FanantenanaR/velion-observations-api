"""Mapping BigQuery row -> Observation domain entity.

Fonction pure isolée : facile à tester unitairement (sans aucun mock
de client BQ), facile à faire évoluer si le schéma SQL change.
"""
from __future__ import annotations

from google.cloud.bigquery import Row

from app.domain.models import Observation


def row_to_observation(row: Row) -> Observation:
    """Mappe une ligne BigQuery (avec les alias SQL attendus) vers Observation.

    Aliases SQL attendus dans la query :
    - essai_id          (STRING)
    - parcelle_id       (STRING)
    - date_observation  (DATE)
    - mesure_valeur     (FLOAT64, peut être None)
    - mesure_type       (STRING)
    """
    return Observation(
        essai_id=row["essai_id"],
        parcelle_id=row["parcelle_id"],
        date_observation=row["date_observation"],
        mesure_valeur=row["mesure_valeur"],
        mesure_type=row["mesure_type"],
    )
