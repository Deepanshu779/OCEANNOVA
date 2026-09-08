# Real-data adapters

OCEANNOVA can run the complete investigation pipeline with provider-neutral exports. The adapters deliberately avoid hard-coding a commercial API so the same code can consume Copernicus/NOAA exports and other approved sources.

## Ocean forcing

Prepare `ocean_forcing.csv` with:

`timestamp,latitude,longitude,current_east_ms,current_north_ms,wind_east_ms,wind_north_ms`

The loader is `data_sources.ocean_forcing.load_forcing()` and selects the nearest record in space/time.

Recommended operational source: Copernicus Marine current data plus a meteorological wind product. Store credentials locally/in Render environment variables; never commit secrets.

## Historical AIS

Prepare `ais.csv` with at minimum:

`mmsi,timestamp,latitude,longitude`

Optional fields: `speed_knots`/`sog` and `course`/`cog`/`heading`.

Use `data_sources.ais_csv.load_ais_csv()` and `group_tracks()` before passing tracks into the attribution pipeline.

## Spill age

`data_sources.spill_age.estimate_age_hours()` reports an uncertainty-aware hindcast-window estimate. It is intentionally labelled as an estimate and must not be presented as a laboratory/chemical age measurement.

## What is still required for a real-data run

The code is ready, but the team must supply an approved **historical AIS export covering the SP-001 origin window and area** and a matching **ocean current + wind export**. These are data inputs, not software dependencies. Do not fabricate AIS evidence or API credentials.
