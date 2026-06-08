# Changelog

Toutes les modifications notables de ce projet sont documentées dans ce fichier.

Le format suit [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/)
et le versioning suit [Semantic Versioning](https://semver.org/lang/fr/).

## [Unreleased]

### Added
- [TASK-14] [TASK-15] `BigQueryClient` gateway + `BigQueryObservationSource` repository on `bigquery-public-data.usda_nass_agriculture.crops`. Gateway/Repository pattern (analogous to SQLAlchemy Session + Repository) — enables future BQ sources for other resources without code duplication
- [TASK-15] Pure `row_to_observation` mapping function isolated in `bigquery/mapping.py`
- [TASK-16] `sql/ddl_demo.sql`: hypothetical CREATE TABLE with partition + cluster rationale
- [TASK-17] `sql/analytics_query.sql`: parameterized analytics query with scan-reduction rationale documented
- [TASK-18] Manually verified the BigQuery → API → response pipeline end-to-end
- New filter `include_total` (default true) for clients to opt-out of the COUNT query (cost/latency optimization)
- `Pagination.has_next` field (always computable without COUNT)

### Changed
- `ObservationSource.list_observations` signature: returns `tuple[list[Observation], int | None]` (None when include_total=False)
- `Pagination.total_items` and `total_pages` are now `int | None` to support skip-count mode
- BigQuery count + fetch queries run in parallel via `asyncio.gather` (~50% latency reduction)
- Factory composes `BigQueryClient + BigQueryObservationSource` instead of returning a monolithic source

### Fixed
- Duplicate `source_kind` declaration in `Settings` was silently overriding the BIGQUERY default with IN_MEMORY

## [0.2.0] - 2026-06-08

### Added
- [TASK-11] `ObservationSource` ABC (secondary port) defining the contract for any source backend (`list_observations`, `health`)
- [TASK-12] `InMemoryObservationSource`: durable in-memory adapter useful for tests, demos, and smoke checks (filtering + pagination in memory)
- [TASK-12] `get_source(settings)` factory: returns the concrete source implementation according to `SourceKind`. BigQuery and MockLegacy raise `NotImplementedError` (will land in Modules 3-4)
- [TASK-12] `SourceKind.IN_MEMORY` enum value (default temporarily set to IN_MEMORY; will revert to BIGQUERY in Module 3)

### Changed
- [TASK-13] `GET /observations` route uses `ObservationSource` via FastAPI `Depends`, decoupled from any concrete implementation. Mocked data removed from the route file (moved to `InMemoryObservationSource`)

## [0.1.0] - 2026-06-07

### Added
- [TASK-5] Project skeleton (`pyproject.toml`, project structure, `.gitignore`)
- [TASK-5] Initial documentation (`README.md`, `CHANGELOG.md`)
- [TASK-6] Pydantic v2 domain models for the stable client contract (`Observation`, `ObservationFilters`)
- [TASK-6] Normalized API response envelope (`ApiResponse[T]`, `Pagination`, `ErrorDetail`, `ErrorCode`, `ResponseStatus`)
- [TASK-7] Application settings via `pydantic-settings` (env-only, no topology) and `SourceKind` enum
- [TASK-8] `GET /observations` router with query params and paginated `ApiResponse[list[Observation]]`
- [TASK-10] FastAPI entry point with `GET /healthz` wrapped in `ApiResponse[dict]` and `GET /` root metadata
- [TASK-9] Manually verified endpoints via curl + Swagger UI

[Unreleased]: https://github.com/FanantenanaR/velion-observations-api/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/FanantenanaR/velion-observations-api/releases/tag/v0.1.0
