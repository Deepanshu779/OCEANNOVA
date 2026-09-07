# OCEANNOVA Demo Guide

## Local startup

### 1. Pull latest code

```powershell
cd D:\OCEANNOVA
git pull origin main
```

### 2. Seed PostgreSQL/PostGIS demonstration data

```powershell
cd backend
python seed_data.py
```

### 3. Start FastAPI

```powershell
cd backend
python -m uvicorn app.main:app --reload
```

API: `http://127.0.0.1:8000`

### 4. Start the React dashboard

```powershell
cd frontend
npm install
npm run dev
```

Dashboard: `http://localhost:5173`

## Recommended presentation flow

1. Open the India-wide maritime overview.
2. Introduce SP-001 as the detected spill event.
3. Click **Focus Investigation** to move from regional context to event detail.
4. Explain the red spill marker, orange probable origin, blue uncertainty region, drift path, and vessel candidates.
5. Open the top vessel candidate and show the attribution evidence fields.
6. Emphasize that the attribution score is an explainable investigation score, not proof of legal responsibility.
7. Mention the real Sentinel-1A validation sample and the SAR baseline benchmark.
8. Explain that live AIS/ocean/weather ingestion and a production deep-learning model are the next integration phase.
