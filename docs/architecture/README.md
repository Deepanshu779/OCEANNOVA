# OCEANNOVA Architecture

## System flow

```text
Sentinel-1 SAR / EO
        |
        v
SAR preprocessing
        |
        v
Oil-spill segmentation
        |
        v
Look-alike filtering
        |
        v
Spill characterization
        |
        v
Ocean currents + wind
        |
        v
Drift hindcast / forecast
        |
        v
Probable spill origin
        |
        v
AIS vessel trajectories
        |
        v
Spatio-temporal correlation
        |
        v
Explainable attribution score
        |
        v
GIS investigation dashboard
```

## Evidence model

OCEANNOVA treats vessel attribution as investigative decision support. A higher score means stronger consistency with the available spatial, temporal, trajectory, and behavioral evidence. It is not a legal or definitive proof of responsibility.

## Current implementation status

- Real Sentinel-1A sample ingestion and geospatial validation: implemented.
- Classical SAR dark-region segmentation baseline: implemented for validation and benchmarking.
- Look-alike filtering prototype: implemented with geometry, radiometric, environmental rules, and a Random Forest baseline trained on synthetic features.
- Drift forward prediction and backward hindcasting MVP: implemented.
- FastAPI + PostgreSQL/PostGIS investigation API: implemented.
- React + Leaflet GIS investigation dashboard: implemented.
- Demonstration AIS candidate ranking: implemented and explicitly labelled as demonstration data.
- Production real-time AIS, live ocean/weather feeds, and production deep-learning model training: next phase.
