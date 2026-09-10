# OCEANNOVA — SIH Judge Demo

## 60–90 second story

**Detect → Characterize → Trace → Correlate → Rank**

1. **Detect:** Open SP-001. Explain that the spill footprint is derived from a real Sentinel-1A test scene.
2. **Characterize:** Show 27.04 km² predicted area, 95.94% mean model confidence over predicted pixels, perimeter and compactness.
3. **Trace:** Show the probable origin and ±8.5 km uncertainty region. Explain backward drift reconstruction.
4. **Forecast:** Show the forward drift path and explain that the prototype uses representative environmental forcing in the deployed demo.
5. **Correlate:** Show AIS trajectories around the reconstructed origin window.
6. **Rank:** Open the candidate panel. OCEAN STAR is #1 at 96.21%, with proximity, temporal, trajectory and behavioural evidence visible.
7. **Close carefully:** “This is an explainable investigative ranking, not legal proof of responsibility.”

## What is real vs demonstration

| Evidence | Status |
|---|---|
| Sentinel-1A scene + reference mask | REAL |
| U-Net test-scene validation | REAL |
| AI spill GeoJSON | REAL DERIVED |
| Drift forcing in seeded deployment | DEMO / REPRESENTATIVE |
| AIS vessel identities and tracks in seeded deployment | DEMO / REPRESENTATIVE |
| NOAA AIS adapter | READY FOR REAL CLIPPED DATA |
| HYCOM historical-data adapter | READY FOR REAL INTEGRATION |

## Real test-scene metrics

The final evaluated real test scene produced:

- IoU: **57.11%**
- Dice: **72.70%**
- Precision: **93.49%**
- Recall: **59.48%**

Do not describe these as production-wide model accuracy.

## Attribution explanation

The ranking uses:

- Proximity: **35%**
- Trajectory match: **30%**
- Temporal consistency: **20%**
- Behavioural evidence: **15%**

Use the phrase **“ranked investigative candidate”**, not “proven polluter.”

## Backup if a live service is slow

The deployed dashboard contains seeded SP-001 data so the full workflow remains demonstrable even if an external data provider is unavailable. The evidence panel visibly distinguishes real satellite evidence from representative demo inputs.

## Judge questions — short answers

**Why not just satellite detection?**  
Detection tells us where the slick is. OCEANNOVA continues through origin reconstruction, drift, AIS correlation and explainable candidate ranking.

**What is innovative?**  
The innovation is the unified evidence chain: real SAR-derived spill geometry, uncertainty-aware drift/origin reasoning, spatio-temporal AIS filtering and explainable multi-factor attribution in one investigation interface.

**Can you prove the vessel caused it?**  
No. The system prioritizes candidates for investigation. Legal responsibility requires independent corroboration.

**What happens with real AIS?**  
The AIS module includes a NOAA MarineCadastre ingestion path. The deployed seeded case uses representative tracks until a clipped historical AIS dataset is supplied for the event.
