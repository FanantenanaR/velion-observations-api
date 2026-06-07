# Changelog

Toutes les modifications notables de ce projet sont documentées dans ce fichier.

Le format suit [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/)
et le versioning suit [Semantic Versioning](https://semver.org/lang/fr/).

## [Unreleased]

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
