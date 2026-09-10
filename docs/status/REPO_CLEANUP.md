# Repository Cleanup

The repository was reviewed before the SIH 2026 prototype freeze.

## Removed obsolete material

- Duplicate nested `frontend/frontend/` application scaffold.
- Obsolete training backup code.
- Empty root dependency placeholder.
- Empty contribution placeholder.
- Accidental nested repository pointer.

## Canonical application paths

- `frontend/` — active React + TypeScript + Leaflet application
- `backend/` — active FastAPI + PostgreSQL/PostGIS API
- `ai-model/` — oil-spill segmentation and evaluation
- `lookalike/` — SAR look-alike validation
- `drift/` — drift and origin modelling
- `ais/` — vessel trajectory and attribution
- `satellite/` — SAR preprocessing

This cleanup is intended to keep the SIH prototype repository focused on the actual demonstrable system.
