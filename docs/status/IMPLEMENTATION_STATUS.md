# OCEANNOVA Implementation Status

Last updated: 2026-09-07

| Workstream | Status | Notes |
|---|---|---|
| Satellite / SAR | MVP complete | Real Sentinel-1A sample validation and geospatial preprocessing are in place. |
| Oil-spill segmentation | Baseline complete | Classical dark-region benchmark is included; production deep-learning training remains next phase. |
| Look-alike validation | Prototype complete | Geometry + radiometric features, environmental rules, and Random Forest baseline on synthetic features. |
| Ocean drift | MVP complete | Forward simulation, backward hindcast, probable origin and uncertainty. |
| AIS attribution | Demo complete | Ranked demonstration candidates with explainable evidence fields. |
| Backend | Demo complete | FastAPI + PostgreSQL/PostGIS and investigation endpoint. |
| Frontend / GIS | Demo complete | React + Leaflet, India-wide view, investigation focus, legend, suspect cards. |
| Deployment | Configured | Render service blueprint and Vercel configuration added; cloud environment variables/database still need to be provisioned. |

## Demo honesty

The dashboard clearly labels seeded vessel records as demonstration AIS data. The current attribution score is an investigation aid, not a claim of legal responsibility.
