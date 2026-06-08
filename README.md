# Velion Observations API

API d'abstraction multi-sources pour observations terrain agronomiques. Le contrat expose au frontend est stable independamment du backend de donnees utilise (BigQuery, source legacy JSON, in-memory). Test technique Velion, livre le 8 juin 2026.

## Quickstart

```bash
git clone https://github.com/FanantenanaR/velion-observations-api.git
cd velion-observations-api

python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -e ".[dev]"

cp .env.example .env
# Editer .env : SOURCE_KIND, GCP_PROJECT si bigquery
gcloud auth application-default login   # si SOURCE_KIND=bigquery
```
Pour lancer avec hot reload:
```bash
uvicorn app.main:app --reload --port 8000
```
Pour lancer sans:
```bash
uvicorn app.main:app --port 8000
```

Swagger UI : http://localhost:8000/docs

## Sources disponibles

| SOURCE_KIND  | Description                                                                                                                                                            |
| ------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `in_memory`  | Adapter avec 5 records hardcodes. Aucun credential requis. Utile pour tests offline.                                                                                   |
| `bigquery`   | Adapter sur `bigquery-public-data.usda_nass_agriculture.crops`. Auth ADC + GCP_PROJECT requis.                                                                         |
| `mock_legacy`| Adapter sur un JSON local au format deliberement etranger (camelCase, Unix timestamps, value en string, metric dotted). Demontre la stabilite du contrat.              |

Switch de source : un seul changement `SOURCE_KIND=` dans `.env`. Aucune ligne de code a modifier.

## Architecture (resume)

Architecture hexagonale (Ports & Adapters). Le domaine (`Observation`, `ObservationFilters`) est au centre, sans dependance technique. Les sources implementent un port (`ObservationSource` ABC). BigQuery suit en interne un pattern Gateway + Repository pour reutilisation entre ressources futures.

Details complets : [docs/01-architecture.MD](docs/01-architecture.MD).

## Brancher une nouvelle source

Guide complet : [docs/04-add-source.MD](docs/04-add-source.MD). Resume en 4 etapes :

1. Creer le sous-package `app/sources/<nom>/`
2. Implementer `ObservationSource` ABC (methodes `list_observations`, `health`)
3. Ajouter la valeur dans l'enum `SourceKind` (`app/config.py`)
4. Enregistrer dans `app/sources/factory.py`

Le contrat expose au frontend ne change pas. Aucune route ni modele Pydantic a modifier.

## Choix d'architecture (cinq points cles)

- **Configuration vs topologie separees** : `app/config.py` contient des parametres d'environnement (project, dataset, credentials path), pas les noms de tables ni le SQL (qui vivent dans les adapters). Reflete la pratique ORM/Repository.
- **Pattern Gateway + Repository pour BigQuery** : `BigQueryClient` generique + `BigQueryObservationSource` specialise. Permet l'ajout de `BigQueryEssaiSource`, `BigQueryParcelleSource`, etc., sans duplication.
- **Async via `asyncio.to_thread`** : le SDK BigQuery officiel est synchrone, on wrap pour ne pas bloquer l'event loop FastAPI. Count et fetch en parallele via `asyncio.gather` (gain typique 50% sur la latence).
- **`include_total` opt-in** : le client peut desactiver la query COUNT pour economiser scan et latence (mode scroll infini). Sur USDA non partitionnee, ~700 MB scannes economises par requete.
- **DDL hypothetique documente** : la table publique USDA n'est pas partitionnee. `sql/ddl_demo.sql` decrit la table qu'on creerait en production avec PARTITION BY date_observation + CLUSTER BY (essai_id, mesure_type, parcelle_id).

## Avec plus de temps

- Tests unitaires (factory, contract stability across sources, legacy mapping). Module 6 non implemente faute de temps, voir CHANGELOG.
- Cache LRU sur les COUNTs BigQuery (les paginations consecutives du meme filtre partagent le total).
- Pagination cursor-based pour eliminer le COUNT entierement.
- BigQuery BI Engine pour des reponses sub-seconde sur les queries chaudes.
- Materialized views pre-agregees par couple (essai, annee).
- OpenTelemetry traces (export Jaeger/Tempo) en plus du correlation ID.
- Rate limiting via slowapi sur les routes publiques.

## Points de doute

- Le mapping USDA NASS est arbitraire (state -> essai_id, county -> parcelle_id, year-end -> date_observation). En production chez Bayer Crop Science, le schema natif aurait probablement fact_observations + dim_essais + dim_parcelles avec des JOINs. L'adapter pattern absorbe ce changement sans toucher au contrat expose.
- `include_total=true` par defaut peut etre considere comme un cout cache cote API. A discuter selon les usages typiques du frontend.
- L'authentification est volontairement hors scope. En production, OAuth2 ou cle API a placer devant FastAPI.

## License

Test technique, pas de license open source specifique.
