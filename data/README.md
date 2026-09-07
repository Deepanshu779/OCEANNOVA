# Data and Reproducibility

OCEANNOVA separates source data from generated processing outputs.

## External data

Development has been validated against a public Sentinel-1A oil-spill dataset containing paired SAR imagery and masks. Large raster files are intentionally excluded from Git via `.gitignore`.

Place local external datasets under `data/external/` and generated outputs under `data/processed/`.

## Current evidence

A real SAR sample has been validated locally with its paired mask and georeferencing. The classical dark-region segmentation baseline is retained as a benchmark to expose false positives and look-alike regions before production deep-learning segmentation is introduced.

## Reproducibility

Do not commit large satellite rasters, credentials, database dumps, or generated model weights. Document each dataset source, preprocessing step, coordinate system, and generated output used by experiments.
