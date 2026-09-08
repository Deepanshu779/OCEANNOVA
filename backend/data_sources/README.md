# Real-data adapters

OCEANNOVA now includes provider-specific adapters for the SP-001 Gulf of Mexico case while keeping the application deployable without large binary datasets.

## 1. Real ocean forcing — HYCOM

For the 2018 Sentinel-1 scene, the recommended historical forcing source is the **HYCOM-TSIS Gulf of Mexico 1/25° reanalysis**. HYCOM publishes hourly current and wind-related fields and provides an NCSS subset service, so OCEANNOVA requests only the incident point/time instead of downloading the full year.

- Dataset catalog: https://ncss.hycom.org/thredds/catalogs/GOMb0.04/reanalysis.html
- Current variables: `u`, `v`
- Wind variables: `wnd_ewd`, `wnd_nwd`
- Adapter: `data_sources.hycom_gulf.fetch_point_forcing()`
- Real-data drift runner: `drift/real_hycom_drift.py`

Example:

```bash
python drift/real_hycom_drift.py
```

The runner writes `data/processed/ai_predictions/SP-001_real_hycom_drift.json` and marks the source as `REAL_HYCOM_HISTORICAL_FORCING`.

## 2. Real historical AIS — NOAA MarineCadastre

NOAA MarineCadastre publishes the annual **AIS Vessel Tracks 2018** archive. The public archive is about 3.23 GB, so it must not be committed to Git or downloaded by the Render web service.

- Index: https://ocmgeodatastor1.blob.core.windows.net/marinecadastre/ais/aistrack/index-aistrack.html
- 2018 archive: https://ocmgeodatastor1.blob.core.windows.net/marinecadastre/ais/aistrack/AISVesselTracks2018.zip
- Adapter: `data_sources.noaa_ais`
- Attribution runner: `ais/run_noaa_real_attribution.py`

Prepare a **clipped CSV** containing the SP-001 origin region/time window and run:

```bash
python ais/run_noaa_real_attribution.py data/real/ais/SP-001_noaa_ais.csv
```

The output is marked `REAL_NOAA_AIS`; representative demo tracks are never silently relabelled as real.

Minimum normalized AIS fields:

`MMSI, BaseDateTime, LAT, LON`

Optional fields:

`SOG, COG, VesselName, VesselType`

## 3. Provider-neutral fallback

`data_sources/ocean_forcing.py` accepts a CSV/JSON forcing export with:

`timestamp,latitude,longitude,current_east_ms,current_north_ms,wind_east_ms,wind_north_ms`

`data_sources/ais_csv.py` accepts a normalized AIS CSV when a different approved provider is used.

## 4. Spill age

`data_sources.spill_age.estimate_age_hours()` provides an uncertainty-aware hindcast-window estimate. It is intentionally labelled as an estimate and must not be presented as a laboratory/chemical age measurement.

## Evidence policy

The dashboard must distinguish:

- **REAL** — directly sourced public/approved data.
- **MODEL OUTPUT** — produced by OCEANNOVA algorithms from the supplied inputs.
- **DERIVED** — calculated from real data/model outputs.
- **DEMO** — representative data used only when the corresponding real source is unavailable.

Never fabricate vessel identities, AIS positions, environmental values, or legal responsibility claims.
