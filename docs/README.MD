# Documentation — Velion Observations API

> Documentation technique du projet. Pour démarrer rapidement, voir le [README racine](../README.MD).

## Sommaire

| # | Doc | Contenu |
|---|---|---|
| 1 | [Architecture](./01-architecture.MD) | Pattern hexagonal, sources interchangeables, règle de dépendance |
| 2 | [Contrat API](./02-api-contract.MD) | Endpoints, envelope `ApiResponse`, gestion d'erreurs, observabilité |
| 3 | [Source BigQuery](./03-bigquery.MD) | Gateway + Repository, mapping, optimisation du scan |
| 4 | [Ajouter une source](./04-add-source.MD) | Guide pas-à-pas pour brancher un nouveau backend |

## Conventions

- Diagrammes au format [Mermaid](https://mermaid.js.org/) — rendus nativement par GitHub.
- Tous les chemins relatifs à la racine du projet.
- Exemples `curl` supposent l'API lancée sur `http://localhost:8000`.
