<div align="center">

# 🌊 OCEANNOVA

### Marine Oil Spill Intelligence & Vessel Attribution Platform

**Detect. Trace. Protect.**

[![SIH 2026](https://img.shields.io/badge/SIH%202026-PS%2026143-blue?style=for-the-badge)](https://sih2026.vuce.in/ps/SIH26143)
[![Frontend](https://img.shields.io/badge/Frontend-Vercel-black?style=for-the-badge&logo=vercel)](https://oceannova-ochre.vercel.app/)
[![Backend](https://img.shields.io/badge/Backend-Render-46E3B7?style=for-the-badge&logo=render)](https://oceannova-api.onrender.com)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

**SIH 2026 • Problem Statement 26143 • Team OCEANNOVA**

</div>

---

## 📌 Overview

**OCEANNOVA** is a geospatial decision-support platform designed to investigate marine oil spills by combining **satellite SAR imagery, spill characterization, ocean drift modelling, historical AIS vessel trajectories, and explainable vessel attribution** in a single GIS interface.

Instead of stopping at spill detection, OCEANNOVA follows the investigation chain:

> **Detect the slick → characterize it → reconstruct where it likely originated → estimate how it will move → reconstruct relevant vessel traffic → filter irrelevant vessels → rank investigative candidates.**

The platform is being developed for **Smart India Hackathon 2026 — PS 26143**, focused on leveraging satellite imagery and AIS correlations to investigate vessels potentially responsible for marine oil spills.

> ⚠️ **Attribution disclaimer:** OCEANNOVA produces an explainable investigative ranking based on available evidence. It does **not** establish legal responsibility or prove that a particular vessel caused a spill.

---

## 🚀 Live Demo

### 🌐 Web Application

**https://oceannova-ochre.vercel.app/**

### ⚙️ Backend API

**https://oceannova-api.onrender.com**

### 🔎 Demo Investigation

**SP-001** is a seeded offshore demonstration scenario that exercises the complete investigation workflow, including spill characterization, origin reconstruction, drift, AIS filtering and vessel ranking.

---

## 🎯 Problem Statement

**SIH26143 / PS 26143** — *Leveraging satellite imagery to determine oil spills at sea along with AIS data correlations to identify the vessel responsible for the spill.*

The system is designed around the following investigation requirements:

- Detect and characterize marine oil spills from satellite imagery.
- Estimate geometric properties and spill age where feasible.
- Combine oceanographic and meteorological information for drift analysis.
- Reconstruct the probable spill origin and time window.
- Forecast future spill movement.
- Reconstruct historical AIS vessel traffic around the origin window.
- Remove irrelevant vessel traffic using spatial and temporal constraints.
- Rank candidate vessels using explainable multi-factor evidence.
- Provide an integrated visual investigation interface.

---

## ✨ Key Capabilities

| Capability | OCEANNOVA Approach |
|---|---|
| 🛰️ **Satellite Detection** | Sentinel-1 SAR ingestion, preprocessing and segmentation benchmarking |
| 🛢️ **Spill Characterization** | Area, perimeter estimate, compactness and observation/age metadata |
| 🧭 **Origin Reconstruction** | Backward drift hindcasting with an uncertainty region |
| 🌊 **Drift Forecasting** | Timestamped forward movement simulation |
| 🌬️ **Environmental Context** | Current and wind fields represented in the drift pipeline |
| 🚢 **AIS Reconstruction** | Historical vessel tracks around the reconstructed origin window |
| 🔎 **Traffic Filtering** | Spatial proximity + temporal consistency filtering |
| 📊 **Explainable Attribution** | Proximity, temporal, trajectory and behavioural evidence |
| 🗺️ **GIS Investigation** | Interactive React + Leaflet maritime dashboard |
| 🗄️ **Geospatial Storage** | PostgreSQL + PostGIS |
| ⚡ **API Layer** | FastAPI investigation endpoints |

---

## 🧠 Investigation Pipeline

```text
┌─────────────────────────┐
│ Sentinel-1 SAR / EO     │
└────────────┬────────────┘
             ↓
┌─────────────────────────┐
│ SAR Preprocessing       │
└────────────┬────────────┘
             ↓
┌─────────────────────────┐
│ Oil-Spill Segmentation  │
└────────────┬────────────┘
             ↓
┌─────────────────────────┐
│ Look-Alike Filtering    │
└────────────┬────────────┘
             ↓
┌─────────────────────────┐
│ Spill Characterization  │
└────────────┬────────────┘
             ↓
┌─────────────────────────┐
│ Currents + Wind         │
└────────────┬────────────┘
             ↓
┌─────────────────────────┐
│ Drift Hindcast/Forecast │
└────────────┬────────────┘
             ↓
┌─────────────────────────┐
│ Probable Origin + Error │
└────────────┬────────────┘
             ↓
┌─────────────────────────┐
│ Historical AIS Tracks   │
└────────────┬────────────┘
             ↓
┌─────────────────────────┐
│ Irrelevant Traffic      │
│ Filtering               │
└────────────┬────────────┘
             ↓
┌─────────────────────────┐
│ Explainable Attribution │
└────────────┬────────────┘
             ↓
┌─────────────────────────┐
│ GIS Investigation       │
│ Dashboard               │
└─────────────────────────┘
```

---

## 🏗️ System Architecture

```text
                        OCEANNOVA
                            │
          ┌─────────────────┴─────────────────┐
          │                                   │
     Data & AI Layer                    Application Layer
          │                                   │
   ┌──────┴──────┐                    ┌───────┴────────┐
   │ Satellite   │                    │ React + Leaflet│
   │ SAR / EO    │                    │ GIS Dashboard  │
   └──────┬──────┘                    └───────┬────────┘
          │                                   │
   ┌──────▼──────┐                    ┌───────▼────────┐
   │ Segmentation│                    │ FastAPI        │
   │ + Lookalike │◄───────────────────┤ REST API       │
   └──────┬──────┘                    └───────┬────────┘
          │                                   │
   ┌──────▼──────┐                    ┌───────▼────────┐
   │ Drift +     │                    │ PostgreSQL +   │
   │ Origin      │                    │ PostGIS        │
   └──────┬──────┘                    └────────────────┘
          │
   ┌──────▼──────┐
   │ AIS Scoring │
   │ + Attribution│
   └─────────────┘
```

### Deployment

```text
GitHub
  │
  ├── Vercel ──────► React + TypeScript + Leaflet
  │                         │
  │                         ▼
  └── Render ──────► FastAPI Backend
                            │
                            ▼
                     Supabase PostgreSQL
                         + PostGIS
```

---

## 🧮 Explainable Vessel Attribution

Candidate vessels are ranked using four evidence components:

| Component | Weight | Purpose |
|---|---:|---|
| **Proximity** | 35% | Distance from reconstructed spill origin |
| **Trajectory Match** | 30% | Consistency between vessel movement and spill-origin geometry |
| **Temporal Consistency** | 20% | Compatibility with the reconstructed spill time window |
| **Behavioural Anomaly** | 15% | Supporting abnormal-behaviour evidence |

The resulting score is an **investigative prioritization signal**, not a legal conclusion.

---

## 🛰️ Satellite & SAR Validation

OCEANNOVA includes a real Sentinel-1A sample workflow for geospatial validation and classical segmentation benchmarking.

The validation path covers:

- Raster ingestion.
- CRS validation and coordinate transformation.
- Ground-truth mask analysis.
- Spill area estimation from the reference mask.
- Classical dark-region segmentation benchmark.
- Quantitative comparison using IoU and Dice metrics.

The current classical baseline is intentionally treated as a benchmark rather than the final production model. This provides a measurable starting point for future deep-learning segmentation models.

---

## 🔬 Look-Alike Validation

SAR imagery can contain dark regions that are not oil, creating an important false-positive problem.

The prototype therefore includes:

- Geometric features.
- Radiometric contrast features.
- Edge-gradient features.
- Environmental rule checks.
- Random Forest classification scaffolding.

The current Random Forest baseline uses **synthetic feature vectors** and is explicitly not presented as a production classifier. Real multi-source training and validation are part of the next development phase.

---

## 📡 AIS Investigation

The AIS module reconstructs vessel movement around the estimated origin window and applies explainable ranking logic.

The prototype supports:

- Vessel trajectory reconstruction.
- Haversine distance calculation.
- Spatial candidate filtering.
- Temporal consistency scoring.
- Trajectory matching.
- Behavioural evidence.
- Weighted attribution scoring.
- Ranked candidate output.

The seeded demonstration contains **four vessels**, including an intentionally irrelevant vessel that is filtered from the final candidate ranking.

---

## 🗺️ GIS Dashboard

The frontend provides an event-level investigation view with:

- India-wide maritime overview.
- Spill location and characterization.
- Probable origin marker.
- Origin uncertainty radius.
- Backward and forward drift paths.
- Historic AIS tracks.
- Ranked vessel markers.
- Candidate evidence panels.
- Traffic filtering summary.
- Investigation workflow summary.

The interface is designed for rapid investigation rather than simply displaying raw data.

---

## 🧰 Technology Stack

### Frontend

- React
- TypeScript
- Vite
- Leaflet
- React Leaflet
- CSS

### Backend

- Python
- FastAPI
- SQLAlchemy
- GeoAlchemy2
- Shapely
- PostgreSQL
- PostGIS

### AI / Data Processing

- Python scientific stack
- Raster/SAR preprocessing
- Classical segmentation baseline
- Random Forest look-alike baseline
- Drift simulation and hindcasting
- AIS trajectory analytics

### Infrastructure

- GitHub
- Vercel
- Render
- Supabase
- GitHub Actions

---

## 📁 Repository Structure

```text
OCEANNOVA/
├── .github/
│   └── workflows/          # CI / build checks
├── ai-model/                # Segmentation inference & validation
├── ais/                     # AIS scoring & vessel attribution
├── backend/                 # FastAPI + PostgreSQL/PostGIS API
│   └── app/
├── data/                    # Local/external data policy & outputs
├── docs/                    # Architecture, research & demo guides
├── drift/                   # Drift simulation & origin reconstruction
├── frontend/                # React + TypeScript + Leaflet UI
├── lookalike/               # Spill look-alike validation
├── satellite/               # Sentinel-1 preprocessing
├── tests/                   # Test suite
├── CONTRIBUTING.md
├── LICENSE
├── README.md
└── requirements.txt
```

---

## 💻 Local Development

### 1. Clone

```bash
git clone https://github.com/Deepanshu779/OCEANNOVA.git
cd OCEANNOVA
```

### 2. Backend

```powershell
cd backend
python seed_data.py
python -m uvicorn app.main:app --reload
```

The API runs locally at:

```text
http://127.0.0.1:8000
```

### 3. Frontend

Open a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open the Vite URL displayed in the terminal.

### 4. API Configuration

For production or a deployed frontend, set:

```env
VITE_API_BASE_URL=https://oceannova-api.onrender.com/api/v1
```

Do not commit database credentials or other secrets to GitHub.

---

## 🔌 API Highlights

### Health

```http
GET /api/v1/health
```

### Investigation

```http
GET /api/v1/spills/{spill_id}/investigation
```

Example:

```http
GET /api/v1/spills/SP-001/investigation
```

The investigation response combines spill characterization, probable origin, drift points, traffic filtering statistics, vessel attribution and historical vessel tracks.

---

## 📊 Demo Scenario

The current seeded **SP-001** scenario is an offshore India demonstration event.

It is designed to show the complete investigation workflow:

1. Detect and characterize a spill candidate.
2. Reconstruct a probable origin.
3. Hindcast the spill movement.
4. Forecast future drift.
5. Reconstruct relevant AIS traffic.
6. Filter an irrelevant vessel.
7. Rank the remaining candidates.
8. Inspect evidence for an individual vessel.

The demonstration data is clearly separated from real satellite validation data.

---

## 📚 Data Sources & Research Direction

The project is structured to support integration with authoritative maritime and Earth-observation sources, including:

- Sentinel-1 SAR imagery.
- Copernicus Sentinel data services.
- Copernicus Marine oceanographic products.
- MarineCadastre / AccessAIS datasets.
- AISStream for real-time AIS integration.
- Public oil-spill datasets containing oil, look-alike and no-oil samples.

Large raster datasets and generated artifacts are intentionally excluded from the repository.

---

## 🛡️ Responsible Use & Limitations

OCEANNOVA is a **decision-support prototype**. The current implementation has clear boundaries:

- The included Sentinel-1A sample is used for real-data geospatial validation and benchmarking.
- The current look-alike Random Forest baseline uses synthetic training features.
- The seeded AIS vessel identities and trajectories are demonstration data.
- Live AIS, live ocean/weather feeds and production deep-learning model weights are not yet the default deployed pipeline.
- Some demo characterization fields are seeded values used to exercise the complete dashboard workflow.
- Attribution scores should be corroborated by qualified investigators before operational or legal action.

These boundaries are intentionally documented so that prototype results are not presented as operational evidence.

---

## 🔮 Roadmap

### Phase 1 — Prototype ✅

- [x] End-to-end investigation architecture
- [x] Sentinel-1 sample validation
- [x] SAR preprocessing baseline
- [x] Look-alike validation scaffolding
- [x] Drift hindcast/forecast engine
- [x] AIS attribution scoring
- [x] FastAPI + PostGIS backend
- [x] GIS dashboard
- [x] Cloud deployment

### Phase 2 — Production Data Integration

- [ ] Multi-scene Sentinel-1 ingestion
- [ ] Production oil-spill segmentation model
- [ ] Real look-alike training and validation
- [ ] Live/historical AIS provider integration
- [ ] Live ocean-current and weather feeds
- [ ] Automated event ingestion

### Phase 3 — Operational Intelligence

- [ ] Near-real-time satellite monitoring
- [ ] Multi-model drift ensembles
- [ ] Uncertainty-aware origin estimation
- [ ] Automated alerts
- [ ] Evidence provenance and audit trails
- [ ] Scalable multi-event investigation
- [ ] Explainable AI reporting

---

## 👥 Team OCEANNOVA

**OCEANNOVA — Detect. Trace. Protect.**

Built for **Smart India Hackathon 2026 — PS 26143**.

### Team Contributions

- **Deepanshu** — Full-Stack, GIS Dashboard & System Integration
- **Harshit Raj** — AI/ML, Oil-Spill Detection & Segmentation
- **Harshit Rastogi** — AIS Data, Vessel Tracking & Attribution
- **Kunal** — Look-Alike Detection & Validation
- **Lakshay** — Satellite/SAR Data & Preprocessing
- **Ishika** — Ocean Drift & Spill-Origin Prediction

---

## 📄 License

This project is licensed under the **MIT License**. See [LICENSE](LICENSE) for details.

---

<div align="center">

### 🌊 OCEANNOVA

**Detect. Trace. Protect.**

</div>
