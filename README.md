# OCEANNOVA — Marine Oil Spill Intelligence Platform

**SIH 2026 | PS: SIH26143 | Team: OCEANNOVA**  
**Tagline: Detect. Trace. Protect.**

OCEANNOVA is a geospatial decision-support platform for marine oil-spill investigation. It combines satellite/SAR evidence, spill segmentation, look-alike validation, ocean-drift reconstruction, AIS vessel correlation, and an interactive GIS dashboard.

> **Important:** vessel attribution is presented as an explainable investigation score, not proof of legal responsibility.

## What is implemented

- **Satellite/SAR:** real Sentinel-1A sample ingestion, CRS validation, spill-mask analysis, and a classical SAR dark-region segmentation benchmark.
- **AI/ML:** segmentation inference scaffolding with a clear path to production deep-learning models.
- **Look-alike validation:** geometric and radiometric feature extraction, environmental rule checks, and a Random Forest baseline using synthetic training features.
- **Ocean drift:** forward drift simulation, backward/hindcast reconstruction, probable-origin estimation, uncertainty radius, and timestamped trajectories.
- **AIS attribution:** vessel records, spatio-temporal evidence fields, trajectory/behavior scores, and ranked candidates.
- **Backend:** FastAPI with PostgreSQL + PostGIS for spatially aware persistence and investigation APIs.
- **Frontend:** React + TypeScript + Leaflet GIS dashboard with India-wide maritime context and event-focused investigation mode.

## Architecture

```text
Sentinel-1 SAR / EO
      ↓
SAR preprocessing
      ↓
Oil-spill segmentation
      ↓
Look-alike filtering
      ↓
Spill characterization
      ↓
Ocean currents + wind
      ↓
Drift hindcast / forecast
      ↓
Probable spill origin
      ↓
AIS vessel trajectories
      ↓
Spatio-temporal correlation
      ↓
Explainable attribution score
      ↓
GIS investigation dashboard
```

## Repository structure

```text
ai-model/      Segmentation validation and inference
ais/           AIS preprocessing, trajectory matching, attribution
backend/       FastAPI + PostgreSQL/PostGIS
frontend/      React + Leaflet dashboard
driving data/  Local data policy and processing outputs
drift/         Drift simulation and origin reconstruction
lookalike/     Spill look-alike filtering and validation
satellite/     Satellite/SAR pipeline
```

## Local demo

See [`docs/demo/DEMO_GUIDE.md`](docs/demo/DEMO_GUIDE.md) for the exact pull, database seed, backend startup, and frontend startup sequence.

```powershell
cd D:\OCEANNOVA
git pull origin main

cd backend
python seed_data.py
python -m uvicorn app.main:app --reload
```

In a second terminal:

```powershell
cd D:\OCEANNOVA\frontend
npm install
npm run dev
```

## Data and reproducibility

Large satellite rasters and generated artifacts are intentionally excluded from Git. Keep external datasets under `data/external/` and generated outputs under `data/processed/`.

The current demo AIS vessels are explicitly marked as **demonstration data** in the UI. Real-time AIS, live ocean/weather services, and production model weights require the next integration phase.
