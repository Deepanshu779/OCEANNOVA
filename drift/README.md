# Drift (Task 4)
# OCEANNOVA - Task 4: Ocean Drift & Spill-Origin Prediction

## Objective

Estimate the probable origin and movement of an oil spill using
ocean-current and wind-driven surface drift.

The module supports:

- Forward drift forecasting
- Backward spill hindcasting
- Probable origin estimation
- Environmental uncertainty
- Origin uncertainty radius
- Timestamped trajectories
- JSON output for downstream AIS and GIS modules

---

## Pipeline

```text
Observed Spill
      |
      v
Current + Wind
      |
      v
Surface Drift Model
      |
      +----------------+
      |                |
      v                v
Forward             Backward
Forecast            Hindcast
      |                |
      v                v
Future Path       Probable Origin
                       |
                       v
                Origin Time Window
                       |
                       v
                  AIS Analysis