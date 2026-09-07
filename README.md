# OCEANNOVA — Marine Oil Spill Intelligence Platform

**SIH 2026 | PS: 26143 / SIH26143 | Team: OCEANNOVA**  
**Tagline: Detect. Trace. Protect.**

OCEANNOVA is a geospatial decision-support platform for marine oil-spill investigation. It follows the problem statement end-to-end: detect and characterise a slick from SAR evidence, reconstruct its probable origin, hindcast and forecast movement, reconstruct AIS traffic around the origin window, filter irrelevant vessels, rank candidates with explainable evidence, and present the investigation in a GIS console.

> **Important:** vessel attribution is an investigative ranking, not proof of legal responsibility. The current AIS records and the showcased incident are explicitly demonstration data.

## PS 26143 coverage

| Requirement | OCEANNOVA implementation |
|---|---|
| Detect oil slick from satellite imagery | Real Sentinel-1A sample ingestion + SAR preprocessing + segmentation benchmark |
| Characterise spill | Area, perimeter estimate, compactness estimate, observation timestamp and age estimate |
| Trace to origin | Backward drift hindcast + uncertainty region |
| Predict future flow | Timestamped forward drift forecast points |
| Oceanographic / meteorological inputs | Current and wind fields are carried through the drift pipeline; live providers are a next integration |
| Historic AIS reconstruction | Timestamped vessel trajectories around the reconstructed origin window |
| Filter irrelevant traffic | Origin-window proximity and temporal-consistency filtering; final demo includes an irrelevant vessel that is excluded from ranking |
| Score suspect vessels | Explainable proximity + temporal + trajectory + behavioural-anomaly evidence |
| Visual interface | React + TypeScript + Leaflet investigation dashboard |

## Implemented modules

- **Satellite/SAR:** reusable Sentinel-1 preprocessing, real Sentinel-1A sample ingestion, CRS validation, spill-mask analysis and classical dark-region benchmark.
- **AI/ML:** inference scaffolding and benchmarking path for production segmentation models.
- **Look-alike validation:** geometric/radiometric features, environmental rules and Random Forest baseline using synthetic training features.
- **Spill characterisation:** area, perimeter estimate, compactness estimate and age metadata when a reliable observation timestamp is available.
- **Ocean drift:** forward simulation, backward/hindcast reconstruction, probable origin, uncertainty radius and timestamped trajectories.
- **AIS:** trajectory reconstruction, irrelevant-traffic filtering, explainable attribution scoring and ranked candidates.
- **Backend:** FastAPI + PostgreSQL/PostGIS investigation API.
- **Frontend:** React + TypeScript + Leaflet GIS dashboard with India-wide maritime overview, historic AIS tracks, drift path, origin uncertainty and evidence panels.

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
Spill characterisation
        ↓
Ocean currents + wind
        ↓
Drift hindcast / forecast
        ↓
Probable origin + uncertainty
        ↓
Historic AIS reconstruction
        ↓
Irrelevant traffic filtering
        ↓
Proximity + temporal + trajectory + behaviour scoring
        ↓
Ranked suspect vessels
        ↓
GIS investigation dashboard
```

## Demo incident

The seeded `SP-001` investigation is an **offshore India demonstration scenario** designed to exercise the complete pipeline without putting ships on land or presenting synthetic AIS as real-world evidence.

The dashboard demonstrates:

1. SAR-derived spill candidate and characterisation.
2. Probable origin with an uncertainty radius.
3. Backward and forward slick movement.
4. Historic AIS trajectories around the origin window.
5. Irrelevant vessel filtering.
6. Ranked candidates with proximity, temporal, trajectory and behavioural evidence.
7. Click-to-focus vessel investigation.

## Local demo

```powershell
cd D:\OCEANNOVA
git pull origin main

cd backend
python seed_data.py
python -m uvicorn app.main:app --reload
```

Second terminal:

```powershell
cd D:\OCEANNOVA\frontend
npm install
npm run dev
```

Open the Vite URL shown in the terminal. Use **Focus Investigation** for the event-level view and click a suspect card to focus its map location.

## Data

The repository intentionally excludes large rasters and generated outputs. Keep datasets under `data/external/` and generated artifacts under `data/processed/`.

Recommended sources for the next production training/integration phase:

- NOAA/MarineCadastre AIS data format and bulk AIS data.
- Sentinel-1 SAR oil-spill datasets on Zenodo, including oil, no-oil and look-alike samples.
- Copernicus Sentinel-1 products and catalogue APIs.
- Copernicus Marine currents and other oceanographic/meteorological providers.

## Honesty boundary

The repository separates **real-data validation** from **demo integration**:

- The included real Sentinel-1A sample is used for geospatial validation and a classical segmentation benchmark.
- The look-alike Random Forest baseline is trained on synthetic feature vectors and is not presented as a production classifier.
- The seeded AIS trajectories and vessel identities are demonstration data.
- Live AIS, live ocean/weather feeds and production deep-learning model weights are the next deployment phase.
- Attribution is decision support and must be corroborated by investigators before any operational or legal conclusion.

## Repository structure

```text
ai-model/      Segmentation validation and inference
 ais/          AIS scoring and attribution
backend/       FastAPI + PostgreSQL/PostGIS
frontend/      React + Leaflet dashboard
data/          Local data policy and processing outputs
drift/         Drift simulation and origin reconstruction
lookalike/     Spill look-alike filtering and validation
satellite/     Sentinel-1 preprocessing and characterisation
docs/          Architecture, demo and research notes
```

## Team

**OCEANNOVA — Detect. Trace. Protect.**
