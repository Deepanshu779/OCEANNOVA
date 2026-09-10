<div align="center">

# 🌊 OCEANNOVA

### Marine Oil Spill Intelligence & Vessel Attribution Platform

**Detect. Trace. Protect.**

[![SIH 2026](https://img.shields.io/badge/SIH%202026-PS%2026143-blue?style=for-the-badge)](https://sih2026.vuce.in/ps/SIH26143)
[![Frontend](https://img.shields.io/badge/Frontend-Vercel-black?style=for-the-badge&logo=vercel)](https://oceannova-ochre.vercel.app/)
[![Backend](https://img.shields.io/badge/Backend-Render-46E3B7?style=for-the-badge&logo=render)](https://oceannova-api.onrender.com)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

**Smart India Hackathon 2026 • PS 26143 • Team OCEANNOVA**

</div>

---

## 🚀 Live Demo

- **Web:** https://oceannova-ochre.vercel.app/
- **API:** https://oceannova-api.onrender.com
- **Investigation:** `GET /api/v1/spills/SP-001/investigation`

## 🎯 What We Solve

OCEANNOVA turns a satellite-detected oil slick into an explainable maritime investigation workflow:

**Detect → Characterize → Trace → Correlate → Rank**

The platform combines Sentinel-1 SAR, spill geometry, ocean drift modelling, AIS vessel trajectories and explainable attribution in one GIS interface. It is designed as decision support: attribution scores prioritize candidates but do not establish legal responsibility.

## 🧠 End-to-End Pipeline

```text
Sentinel-1 SAR
     ↓
SAR preprocessing
     ↓
U-Net spill segmentation
     ↓
Radiometric / look-alike validation
     ↓
Area + perimeter + compactness
     ↓
Ocean current + wind forcing
     ↓
Backward / forward drift modelling
     ↓
Probable origin + uncertainty
     ↓
Historical AIS traffic
     ↓
Spatial + temporal filtering
     ↓
Explainable vessel ranking
     ↓
GIS investigation dashboard
```

## 🛰️ Real Satellite Evidence

The repository includes a real Sentinel-1A Gulf of Mexico test scene (`2018_09_26.tif`) with a reference mask. The evaluated real test scene produced the following validation result after the final segmentation/validation pipeline:

| Metric | Evaluated result |
|---|---:|
| IoU | **57.11%** |
| Dice | **72.70%** |
| Precision | **93.49%** |
| Recall | **59.48%** |

These metrics describe the **evaluated real test scene only** and are not claimed as production-wide model accuracy.

The current filtered AI prediction for SP-001 covers **27.0378 km²**, with mean model confidence **95.94%** over predicted spill pixels. These are prediction characteristics, not accuracy metrics.

## 🌊 Drift & Origin Reconstruction

SP-001 uses the drift/origin pipeline to demonstrate backward hindcasting and forward forecasting. The current prototype reconstructs a probable origin near **28.8523°N, 89.1530°W** with an uncertainty radius of approximately **8.5 km**.

Environmental forcing in the seeded deployment is representative prototype data. The codebase also contains a HYCOM adapter for real historical environmental-data integration.

## 🚢 AIS Attribution

Candidate ranking uses an explainable weighted score:

| Evidence | Weight |
|---|---:|
| Proximity | 35% |
| Trajectory match | 30% |
| Temporal consistency | 20% |
| Behavioural evidence | 15% |

The seeded SP-001 demo ranks **OCEAN STAR** highest at **96.21%**, followed by **SEA HORIZON (87.74%)** and **MARINE EXPRESS (75.63%)**. These seeded vessel trajectories are **representative demonstration data**, not historical AIS evidence for the Sentinel-1 scene.

The repository includes adapters for NOAA MarineCadastre AIS and HYCOM data so the same investigation architecture can consume real external datasets when supplied.

## 🗺️ GIS Dashboard

The deployed interface shows:

- Real AI spill footprint
- Spill area and confidence
- Probable origin and uncertainty radius
- Backward and forward drift paths
- AIS trajectories and ranked candidates
- Evidence/provenance status
- Traffic filtering summary
- Explainable candidate scoring

## 🏗️ Architecture

```text
                OCEANNOVA
                    │
       ┌────────────┴────────────┐
       │                         │
   Data / AI                Application
       │                         │
 Sentinel-1 SAR          React + Leaflet
 Segmentation             GIS Dashboard
 Look-alikes                    │
 Drift / Origin              FastAPI
 AIS scoring                    │
       └────────────── PostgreSQL + PostGIS

Deployment: GitHub → Vercel (frontend) + Render (API) + Supabase (PostGIS)
```

## 🧰 Technology Stack

**Frontend:** React, TypeScript, Vite, Leaflet, React Leaflet, CSS  
**Backend:** Python, FastAPI, SQLAlchemy, GeoAlchemy2, Shapely  
**AI/Data:** Sentinel-1 SAR processing, U-Net inference, look-alike validation, drift modelling, AIS analytics  
**Database:** PostgreSQL + PostGIS  
**Deployment:** Vercel, Render, Supabase, GitHub Actions

## 📁 Repository Structure

```text
OCEANNOVA/
├── ai-model/          # Spill segmentation and evaluation
├── ais/               # AIS matching and attribution
├── backend/           # FastAPI + PostGIS API
├── data/              # Data policies and processed evidence
├── docs/              # Architecture and SIH demo documentation
├── drift/             # Drift and origin modelling
├── frontend/          # React + Leaflet dashboard
├── lookalike/         # Look-alike validation
├── satellite/         # SAR preprocessing
└── tests/              # Automated tests
```

## 💻 Local Development

```bash
git clone https://github.com/Deepanshu779/OCEANNOVA.git
cd OCEANNOVA

# Backend
cd backend
python seed_data.py
python -m uvicorn app.main:app --reload

# Frontend (second terminal)
cd frontend
npm install
npm run dev
```

For the deployed frontend:

```env
VITE_API_BASE_URL=https://oceannova-api.onrender.com/api/v1
```

Never commit database passwords, API keys or provider credentials.

## 🔌 API

```http
GET /api/v1/health
GET /api/v1/spills/{spill_id}/investigation
```

The investigation endpoint returns spill characterization, origin, drift points, traffic filtering, ranked vessels and vessel tracks.

## 🔬 Current Evidence Status

| Source / module | Status | Meaning |
|---|---|---|
| Sentinel-1 SAR scene | **REAL** | Real test scene and reference mask |
| U-Net segmentation validation | **REAL** | Evaluated on the real test scene |
| Spill GeoJSON | **REAL DERIVED** | Exported from the AI prediction mask |
| Drift forcing in deployed seed | **DEMO** | Representative prototype forcing |
| AIS identities/tracks in deployed seed | **DEMO** | Representative trajectories |
| NOAA AIS adapter | **READY** | Real clipped CSV can be ingested |
| HYCOM adapter | **READY** | Real historical forcing can be integrated |

This separation is intentional: the demo proves the architecture without overstating prototype data as operational evidence.

## 🔮 Roadmap

- [x] End-to-end detection → trace → attribution architecture
- [x] Real Sentinel-1 validation workflow
- [x] U-Net inference and GeoJSON export
- [x] Drift hindcast/forecast prototype
- [x] Explainable AIS attribution
- [x] FastAPI + PostGIS backend
- [x] Deployed GIS dashboard
- [ ] Real NOAA AIS event ingestion into the deployed case
- [ ] Real HYCOM forcing wired into the deployed case
- [ ] Multi-scene satellite ingestion and automated alerts
- [ ] Production-scale look-alike training and uncertainty-aware ensembles

## ⚠️ Responsible Use

OCEANNOVA is an investigative decision-support prototype. A high attribution score means a vessel is a high-priority candidate under the available evidence; it does **not** prove that the vessel caused the spill. Operational or legal decisions require independent corroboration and authoritative data.

## 👥 Team OCEANNOVA

**OCEANNOVA — Detect. Trace. Protect.**

- **Deepanshu** — Full-Stack, GIS Dashboard & System Integration
- **Harshit Raj** — AI/ML, Oil-Spill Detection & Segmentation
- **Harshit Rastogi** — AIS Data, Vessel Tracking & Attribution
- **Kunal** — Look-Alike Detection & Validation
- **Lakshay** — Satellite/SAR Data & Preprocessing
- **Ishika** — Ocean Drift & Spill-Origin Prediction

## 📄 License

MIT License. See [LICENSE](LICENSE).
