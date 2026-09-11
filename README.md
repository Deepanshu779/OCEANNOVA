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

OCEANNOVA is designed around **evidence transparency**. The platform distinguishes between real satellite evidence, AI-derived measurements, integration-ready modules, and representative demonstration data instead of presenting simulated information as fact.

- **REAL** — Sentinel-1 SAR observations and reference-mask evaluation.
- **DERIVED** — spill footprint, area, perimeter, compactness and coordinates calculated from AI prediction masks.
- **READY** — interfaces for authoritative oceanographic and historical AIS data.
- **DEMO** — representative vessel positions/routes used only when real historical AIS is not loaded.

## 🚀 Live Demo

- **Web:** https://oceannova-ochre.vercel.app/
- **API:** https://oceannova-api.onrender.com
- **Investigation API:** `GET /api/v1/spills/{spill_id}/investigation`

## 🎯 Problem We Solve

Oil spills are difficult to investigate because detection alone does not explain **where the slick came from, how it evolved, or which vessels should be investigated**.

OCEANNOVA creates an end-to-end investigation workflow:

**Detect → Validate → Characterize → Reconstruct → Correlate → Rank**

The vessel score is investigative decision support. It does **not** establish legal responsibility.

## 🧠 End-to-End Pipeline

```text
Sentinel-1 SAR Radar_data
        ↓
SAR preprocessing / normalization
        ↓
Lightweight U-Net segmentation
        ↓
Confidence + radiometric + look-alike filtering
        ↓
Spill geometry characterization
        ↓
Ocean current + wind integration
        ↓
Backward / forward drift modelling
        ↓
Probable spill origin + uncertainty
        ↓
Historical AIS integration
        ↓
Spatial + temporal correlation
        ↓
Explainable vessel attribution ranking
        ↓
GIS Investigation Command Center
```

---

# 🛰️ Datasets Used

## 1. Radar_data — Primary Project Dataset

**Dataset used:** the project's local `Radar_data` collection of **Sentinel-1 SAR oil-spill image/mask pairs**.

Repository location:

```text
data/external/Radar_data/
├── train/
│   ├── images/
│   └── masks/
└── test/
    ├── images/
    └── masks/
```

The processed dataset manifest contains **21 Radar_data scenes** mapped to OCEANNOVA incident IDs (`SP-001` onward). Each available scene is processed through the same evidence pipeline and exposed through the Scene Library.

### What the Radar_data contains

| Data | Purpose |
|---|---|
| Sentinel-1 SAR `.tif` images | Radar observations used for oil-spill detection |
| Ground-truth mask `.tif` files | Reference masks for supervised training/evaluation |
| Train scenes | U-Net model training and in-sample validation evidence |
| Test scenes | Held-out/reference evaluation where available |
| CRS metadata | Geo-referencing of satellite observations |

The dataset includes Gulf of Mexico observations. A representative real scene used for held-out evaluation is `2018_09_26.tif`.

### Processed Radar_data outputs

For each processed scene, OCEANNOVA stores evidence under:

```text
data/processed/all_scenes/<SP-ID>/
├── probability.npy
├── predicted_mask.tif
├── filtered_mask.tif
├── characterization.json
└── spill.geojson
```

A central manifest is maintained at:

```text
data/processed/all_scenes/manifest.json
```

This makes every processed Radar_data scene traceable from the original SAR observation to its AI prediction and GIS footprint.

## 2. AI-Generated Spill Footprints

The AI pipeline generates probability maps and prediction masks from the Sentinel-1 SAR imagery. Radiometric, component-size and shape filtering is then applied before exporting the final spill footprint.

Important distinction:

> Predicted spill area, perimeter, compactness and mean AI confidence describe the model output. They are **not** ground-truth accuracy measurements.

## 3. Ground-Truth Masks

Where a Radar_data scene has a corresponding mask, the mask is used as reference evidence for segmentation evaluation.

For the evaluated real test scene `2018_09_26.tif`, the recorded results are:

| Metric | Evaluated result |
|---|---:|
| IoU | **57.11%** |
| Dice | **72.70%** |
| Precision | **93.49%** |
| Recall | **59.48%** |

These values describe the evaluated real test scene only and are **not claimed as production-wide model accuracy**.

---

# 🚫 External Data Status

OCEANNOVA currently keeps the demonstration dataset scope focused on the committed `Radar_data` collection.

### Oceanographic forcing

The drift/origin architecture is ready for authoritative ocean-current and wind forcing, but external environmental forcing is **not claimed as loaded historical evidence** for the current Radar_data investigations.

### AIS data

The repository contains an explainable AIS attribution engine and representative vessel visualization. **Real historical AIS is not currently loaded into the demonstrated investigations.** Representative candidates are explicitly labelled in the interface so they cannot be confused with historical vessel evidence.

Therefore, OCEANNOVA does **not** claim that a representative vessel caused a real spill.

---

## 🔍 Explainable Evidence Chain

For every investigation, the system separates evidence by provenance:

1. **Satellite evidence — REAL:** Sentinel-1 SAR observation from Radar_data.
2. **AI segmentation — REAL:** U-Net inference on the SAR observation.
3. **Spill geometry — DERIVED:** footprint, area, perimeter, compactness and coordinates calculated from the prediction mask.
4. **Ground-truth evaluation — REAL WHERE AVAILABLE:** comparison against the supplied Radar_data reference mask.
5. **Origin / drift — READY:** architecture prepared for authoritative environmental forcing.
6. **Vessel attribution — DEMO/READY:** scoring pipeline prepared for historical AIS; representative candidates are used only for demonstration when AIS is absent.

This provenance model is one of OCEANNOVA's main competition differentiators.

## 🌊 Drift & Origin Reconstruction

The codebase contains backward/forward drift and origin-reconstruction modules. The system is structured to consume current and wind forcing and produce a probable origin with uncertainty.

When authoritative environmental forcing is not loaded, the platform does not present representative forcing as historical evidence.

## 🚢 AIS Attribution

The explainable attribution engine combines four evidence dimensions:

| Evidence | Weight |
|---|---:|
| Proximity | 35% |
| Trajectory match | 30% |
| Temporal consistency | 20% |
| Behavioural evidence | 15% |

The output is a **ranked investigative candidate score**, not proof of causation.

## 🗺️ GIS Investigation Command Center

The deployed interface provides:

- Interactive Sentinel-1-derived spill investigation map
- Scene Library covering the processed Radar_data observations
- AI confidence and predicted spill footprint
- Geo-referenced spill geometry
- Vessel correlation visualization
- Evidence provenance labels
- Investigation Brief generation
- Dark/light map views
- Integration points for authoritative AIS and environmental data

---

## 🏗️ Architecture

```text
                         OCEANNOVA
                              │
             ┌────────────────┴────────────────┐
             │                                 │
       Evidence / AI                     Application
             │                                 │
      Sentinel-1 SAR                    React + TypeScript
      Radar_data                        Vite + Leaflet
      U-Net segmentation                     │
      Look-alike filtering              FastAPI API
      Geometry characterization               │
      Drift / origin                    PostgreSQL + PostGIS
      AIS attribution
             └─────────────────────────────────┘

Deployment: GitHub → Vercel + Render + Supabase
```

## 🧰 Technology Stack

**Frontend:** React, TypeScript, Vite, Leaflet, React Leaflet, CSS  
**Backend:** Python, FastAPI, SQLAlchemy, GeoAlchemy2, Shapely  
**AI/Data:** Sentinel-1 SAR, Radar_data preprocessing, U-Net inference, radiometric filtering, look-alike filtering, geometry analysis, drift modelling, AIS analytics  
**Database:** PostgreSQL + PostGIS  
**Deployment:** Vercel, Render, Supabase, GitHub Actions

## 📁 Repository Structure

```text
OCEANNOVA/
├── ai-model/          # U-Net segmentation and evaluation
├── ais/               # AIS matching and attribution engine
├── backend/           # FastAPI + PostGIS API
├── data/
│   ├── external/      # Radar_data Sentinel-1 images and masks
│   └── processed/     # AI predictions, characterization and GeoJSON
├── docs/              # Architecture and project documentation
├── drift/             # Drift and origin modelling
├── frontend/          # React + Leaflet GIS command center
├── lookalike/         # Look-alike validation
├── satellite/         # SAR preprocessing
├── scripts/           # Dataset processing and export utilities
└── tests/             # Automated tests
```

## 🔬 Evidence Policy

| Source / module | Status | Meaning |
|---|---|---|
| Sentinel-1 SAR Radar_data | **REAL** | Real satellite observations in the project dataset |
| Ground-truth masks | **REAL** | Supplied reference masks where available |
| U-Net test evaluation | **REAL** | Reference-mask evaluation on a real test scene |
| AI spill GeoJSON | **REAL DERIVED** | Exported from AI prediction masks |
| Spill geometry | **DERIVED** | Calculated from predicted spill regions |
| Environmental forcing | **NOT LOADED** | No external historical forcing is claimed |
| Historical AIS | **NOT LOADED** | No real vessel history is claimed in the demo |
| AIS scoring engine | **READY / DEMO** | Ready for authoritative AIS; representative candidates used for visualization |
| Environmental forcing adapter | **READY** | Ready for authoritative current/wind data |

## ⚡ Why OCEANNOVA

**1. Detection becomes investigation.** The system moves beyond a simple oil-spill segmentation result.

**2. Real evidence is separated from derived and demonstration data.** This prevents misleading claims during a technical demo.

**3. Explainability is built into the pipeline.** Investigators can follow the evidence from SAR pixels to spill geometry and candidate correlation.

**4. The architecture is extensible.** Authoritative AIS and environmental feeds can be connected without redesigning the investigation workflow.

**5. The complete processed Radar_data library is accessible through the Scene Library.** Each scene has a traceable incident ID and processed evidence artifacts.

---

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

- [x] Real Sentinel-1 Radar_data workflow
- [x] U-Net inference and GeoJSON export
- [x] Multi-scene processed Radar_data library
- [x] Scene Library with selectable processed scenes
- [x] Explainable AIS attribution engine
- [x] Drift/origin architecture
- [x] FastAPI + PostGIS backend
- [x] Deployed GIS command center
- [x] Evidence provenance / audit view
- [x] Investigation brief generation
- [ ] Real historical AIS event ingestion into a selected case
- [ ] Real environmental forcing wired into a selected case
- [ ] Multi-scene automated satellite ingestion and alerts
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
