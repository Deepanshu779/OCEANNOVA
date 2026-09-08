# Real AIS input

Place a **clipped NOAA MarineCadastre AIS CSV** for SP-001 here as:

`SP-001_noaa_ais.csv`

Recommended source: NOAA/MarineCadastre **AIS Vessel Tracks 2018**.

Archive index:
https://ocmgeodatastor1.blob.core.windows.net/marinecadastre/ais/aistrack/index-aistrack.html

The full annual archive is large and must not be committed to Git. Clip it to:

- Longitude: approximately -90.0 to -88.3
- Latitude: approximately 28.0 to 29.7
- Time: 2018-09-25 through 2018-09-27

Keep at least `MMSI`, `BaseDateTime`, `LAT`, and `LON`. `SOG`, `COG`, `VesselName`, and `VesselType` are useful when available.

Then run from the repository root:

```bash
python ais/run_noaa_real_attribution.py data/real/ais/SP-001_noaa_ais.csv
```

The generated result is deliberately not committed automatically because AIS files may be large and because the source archive remains the authoritative provenance record.
