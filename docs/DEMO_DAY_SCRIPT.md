# OCEANNOVA — SIH Demo-Day Runbook

## 90-second opening

> **“Most systems can show an oil-spill image. OCEANNOVA shows the investigation behind it.”**
>
> “We start from a real Sentinel-1 SAR observation. Our lightweight U-Net detects the potential slick, then we derive its geometry and place it on an interactive GIS map. The important part is explainability: every layer tells the reviewer whether it is real, AI-derived, ready for authoritative data, or demonstration-only.”
>
> “From here, the same case can be correlated with ocean drift and historical AIS to reconstruct origin and rank vessels. We deliberately do not call representative data historical evidence. That makes the platform safer, auditable and ready for operational integration.”
>
> “So OCEANNOVA is not only an oil-spill detector — it is an evidence-to-investigation workflow.”

## Live flow

### 1. Start on Overview

Point to:
- **REAL SAR** — the satellite observation is real.
- **AI signal** — the displayed confidence is confidence over the predicted mask, not model accuracy.
- **Geo-referenced footprint** — the geometry is derived from the AI mask.

### 2. Open the Investigation Map

Say:

> “The map is the spatial evidence layer. The red footprint is the model-derived spill candidate, and the coordinates are calculated from that prediction.”

### 3. Open Evidence Chain

Move through the five layers:

1. Satellite evidence — **REAL**
2. AI segmentation — **REAL**
3. Spill geometry — **DERIVED**
4. Origin / drift — **READY**
5. Vessel attribution — **DEMO / READY**

Say:

> “This is our differentiator. We never hide the boundary between measured evidence and simulated demonstration data.”

### 4. Open Scene Library

Select another processed observation.

Say:

> “The pipeline is not hard-coded to one screenshot. Processed Radar_data observations can be opened as separate investigations.”

### 5. Close with the investigation brief

Click **Brief** or **Copy brief**.

Say:

> “A reviewer can leave with a concise evidence brief rather than a black-box prediction.”

## Questions judges may ask

### “Why not NASA data?”

> “Our current evidence set uses real Sentinel-1 SAR observations. The source choice is driven by the oil-spill detection task, not by the name of the provider. The architecture is source-agnostic and can ingest additional authoritative datasets.”

### “Is the vessel responsible?”

> “No. A vessel attribution score is an investigative priority, not legal proof. Historical AIS, temporal consistency, drift reconstruction and independent corroboration are required before making such a conclusion.”

### “Are the drift and AIS data real?”

> “For the current demo case, those external evidence layers are not claimed as historical data. Their integration points are ready, and the UI explicitly labels representative demonstration content when it is used.”

### “What is your AI accuracy?”

> “We evaluated the final pipeline on a real test scene against its reference mask. The evaluated scene achieved 57.11% IoU, 72.70% Dice, 93.49% precision and 59.48% recall. We do not present a single scene as production-wide accuracy.”

## Do not say

- “The AI proved this ship caused the spill.”
- “95% confidence means 95% accuracy.”
- “Our demo AIS tracks are historical.”
- “The predicted area is the true spill area.”

## Strong closing line

> **“OCEANNOVA does not just answer where the spill is. It shows what the evidence says, how the answer was produced, and what data is still needed to act on it.”**
