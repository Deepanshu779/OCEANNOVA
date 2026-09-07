# OCEANNOVA Final Demo Guide

## 1. Start the final demo

Pull the latest `main` first:

```powershell
cd D:\OCEANNOVA
git pull origin main
```

Seed/update the PostgreSQL + PostGIS demo case:

```powershell
cd backend
python seed_data.py
```

Start FastAPI:

```powershell
python -m uvicorn app.main:app --reload
```

In a second terminal:

```powershell
cd D:\OCEANNOVA\frontend
npm install
npm run dev
```

Open the Vite URL shown by the terminal.

## 2. Exact jury/demo story

### Step 1 — Detect

Show **SP-001** on the India-wide maritime overview.

Say:

> “OCEANNOVA starts from a satellite-derived oil-spill candidate and characterises the event using confidence, area, perimeter, compactness and observation-age metadata.”

### Step 2 — Trace

Click **Focus Investigation**.

Point out:

- 🔴 detected spill
- 🟠 probable origin
- 🔵 origin uncertainty region
- solid line = oil drift path

Say:

> “We use ocean-current and wind-driven drift information to reconstruct the slick backward toward a probable origin and project its forward movement. Because drift is uncertain, we show an origin region instead of claiming a precise point.”

### Step 3 — AIS reconstruction

Point to the dashed lines.

Say:

> “Around the reconstructed origin window, we reconstruct historic vessel trajectories. Traffic that is spatially or temporally irrelevant is filtered before attribution.”

The seeded demo contains **4 vessels**, of which **1 is deliberately irrelevant** and **3 are ranked candidates**.

### Step 4 — Attribution

Click the top suspect card.

Explain the evidence:

- proximity
- temporal consistency
- trajectory alignment
- behavioural anomaly
- final explainable attribution score

Say:

> “The score is decision support. It ranks vessels by consistency with the available evidence; it does not prove that a vessel legally caused the spill.”

### Step 5 — Real satellite evidence

Briefly mention that the repository contains a real Sentinel-1A sample validation workflow and a classical SAR dark-region baseline. Do not call the classical baseline the final AI model.

### Step 6 — Close with the value proposition

> “Detect the slick, reconstruct where and when it likely originated, predict where it will move, reconstruct the relevant vessel traffic, and rank the strongest investigative leads in one geospatial console.”

## 3. If a judge asks what is real vs demo

**Real-data validation:** Sentinel-1A raster ingestion, CRS handling, paired ground-truth analysis and SAR baseline benchmarking.

**Demonstration integration:** seeded offshore incident, AIS vessel identities/trajectories and the displayed attribution scenario.

**Production next phase:** live AIS feeds, live ocean/weather feeds and a trained deep-learning segmentation model.
