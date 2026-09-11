<div align="center">

# 🌊 OCEANNOVA

### Marine Oil Spill Intelligence & Explainable Investigation Platform

**Detect. Trace. Protect.**

[![Frontend](https://img.shields.io/badge/Frontend-Vercel-black?style=for-the-badge&logo=vercel)](https://oceannova-ochre.vercel.app/)
[![Backend](https://img.shields.io/badge/Backend-Render-46E3B7?style=for-the-badge&logo=render)](https://oceannova-api.onrender.com)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

**Team OCEANNOVA**

</div>

---

## 🏆 Competition Pitch

**Most oil-spill demos stop at detection. OCEANNOVA turns a radar pixel into an investigation trail.**

Our key differentiator is **evidence transparency**. The dashboard explicitly separates:

- **REAL** — satellite observations and evaluated AI evidence;
- **DERIVED** — measurements calculated from the AI prediction mask;
- **READY** — interfaces prepared for authoritative environmental/vessel data;
- **DEMO** — representative data used only where external feeds are not loaded.

This makes the system impressive without pretending that simulated evidence is real-world proof.

## 🚀 Live Demo

- **Web:** https://oceannova-ochre.vercel.app/
- **API:** https://oceannova-api.onrender.com
- **Investigation:** `GET /api/v1/spills/SP-001/investigation`

## 🎯 What We Solve

OCEANNOVA turns a satellite-detected oil slick into an explainable maritime investigation workflow:

**Detect → Validate → Characterize → Reconstruct → Correlate → Rank**

The platform is designed as decision support. A candidate score prioritizes vessels for investigation; it does **not** establish legal responsibility.

## 🧠 End-to-End Pipeline

```text
Sentinel-1 SAR
     ↓
SAR preprocessing
     ↓
Lightweight U-Net segmentation
     ↓
Radiometric / look-alike filtering
     ↓
Area + perimeter + compactness
     ↓
Ocean current + wind forcing (integration ready)
     ↓
Backward / forward drift modelling (integration ready)
     ↓
Probable origin + uncertainty
     ↓
Historical AIS traffic (integration ready)
     ↓
Spatial + temporal filtering
     ↓
Explainable vessel ranking
     ↓
GIS investigation command center
```

## 🛰️ Real Satellite Evidence

The repository includes a real Sentinel-1A Gulf of Mexico observation (`2018_09_26.tif`) with a reference mask. The evaluated real test scene produced:

| Metric | Evaluated result |
|---|---:|
| IoU | **57.11%** |
| Dice | **72.70%** |
| Precision | **93.49%** |
| Recall | **59.48%** |

These metrics describe the **evaluated real test scene only** and are not claimed as production-wide model accuracy.

The processed Radar_data library also contains multiple scenes with AI-generated prediction masks, characterization JSON and GeoJSON outputs. Prediction area and mean confidence describe the model output; they are not ground-truth accuracy measures.

## 🔍 Explainable Evidence Console

The web dashboard now includes a competition-oriented **Evidence Chain**:

1. **Satellite evidence — REAL:** Sentinel-1 SAR observation.
2. **AI segmentation — REAL:** U-Net inference and radiometric/look-alike filtering.
3. **Spill geometry — DERIVED:** footprint, area, perimeter and coordinates calculated from the prediction mask.
4. **Origin / drift — READY:** architecture is prepared for authoritative environmental forcing.
5. **Vessel attribution — DEMO/READY:** the scoring pipeline is prepared for historical AIS, while representative candidates are clearly marked when used for demonstration.

The **Investigation Brief** can be copied directly from the interface for a presentation or review panel.

## 🌊 Drift & Origin Reconstruction

The codebase contains backward/forward drift modelling and origin reconstruction interfaces. Where authoritative environmental forcing is not loaded for a case, the dashboard says so instead of presenting representative forcing as historical evidence.

## 🚢 AIS Attribution

Candidate ranking uses an explainable weighted score:

| Evidence | Weight |
|---|---:|
| Proximity | 35% |
| Trajectory match | 30% |
| Temporal consistency | 20% |
| Behavioural evidence | 15% |

The architecture supports historical AIS ingestion and candidate ranking. Demonstration vessel tracks are explicitly labelled as representative and must never be presented as historical proof.

## 🗺️ GIS Command Center

The deployed interface provides:

- Real satellite-derived spill evidence
- AI confidence and predicted footprint
- Geo-referenced spill geometry
- Interactive investigation map
- Evidence Chain / audit view
- Scene Library across processed Radar_data observations
- Investigation Brief generation
- Explicit data provenance and limitation labels
- AIS and environmental-data integration points

## 🏗️ Architecture

```text
                  OCEANNOVA
                       │
          ┌────────────┴────────────┐
          │                         │
      Evidence / AI             Application
          │                         │
   Sentinel-1 SAR             React + TypeScript
   U-Net segmentation          Leaflet GIS
   Look-alike filtering              │
   Drift / origin               FastAPI API
   AIS attribution                   │
          └──────────── PostgreSQL + PostGIS

Deployment: GitHub → Vercel + Render + Supabase
```

## 🧰 Technology Stack

**Frontend:** React, TypeScript, Vite, Leaflet, React Leaflet, CSS  
**Backend:** Python, FastAPI, SQLAlchemy, GeoAlchemy2, Shapely  
**AI/Data:** Sentinel-1 SAR processing, U-Net inference, look-alike filtering, drift modelling, AIS analytics  
**Database:** PostgreSQL + PostGIS  
**Deployment:** Vercel, Render, Supabase, GitHub Actions

## 📁 Repository Structure

```text
OCEANNOVA/
├── ai-model/          # Spill segmentation and evaluation
├── ais/               # AIS matching and attribution
├── backend/           # FastAPI + PostGIS API
├── data/              # Radar_data and processed evidence
├── docs/              # Architecture and project documentation
├── drift/             # Drift and origin modelling
├── frontend/          # React + Leaflet command center
├── lookalike/         # Look-alike validation
├── satellite/         # SAR preprocessing
└── tests/              # Automated tests
```

## 🔬 Evidence Policy

| Source / module | Status | Meaning |
|---|---|---|
| Sentinel-1 SAR | **REAL** | Real satellite observation in the project evidence set |
| U-Net test evaluation | **REAL** | Evaluated against a reference mask on a real test scene |
| Spill GeoJSON | **REAL DERIVED** | Exported from the AI prediction mask |
| Drift forcing when absent | **NOT LOADED** | No external environmental evidence is claimed |
| AIS identities/tracks when absent | **NOT LOADED** | No historical vessel evidence is claimed |
| AIS scoring engine | **READY** | Can rank authoritative historical AIS when supplied |
| Environmental forcing adapter | **READY** | Can consume authoritative forcing when supplied |

## ⚡ Why This Wins a Demo

**1. It looks like an operational system.** A command-center UI, geospatial map and investigation workflow make the pipeline understandable in seconds.

**2. It is technically honest.** Every evidence layer carries a provenance state instead of mixing real and simulated data.

**3. It is explainable.** The system exposes how a spill moves through detection, characterization and future correlation rather than returning a black-box answer.

**4. It is extensible.** The same investigation contract can consume authoritative AIS and oceanographic feeds without redesigning the dashboard.

**5. It is judge-friendly.** A reviewer can open a scene, see the actual footprint, inspect the evidence chain and copy an investigation brief in one flow.

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
GET /api/v1/spills/{spill_id}/geojson
```

## 🔮 Roadmap

- [x] Real Sentinel-1 validation workflow
- [x] U-Net inference and GeoJSON export
- [x] Multi-scene processed Radar_data library
- [x] Explainable AIS attribution engine
- [x] Drift/origin architecture
- [x] FastAPI + PostGIS backend
- [x] Deployed GIS command center
- [x] Evidence provenance / audit view
- [x] Investigation brief generation
- [ ] Real historical AIS event ingestion into a selected case
- [ ] Real environmental forcing wired into a selected case
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
