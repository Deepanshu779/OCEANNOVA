# AIS (Task 5)
# AIS Data, Vessel Tracking & Attribution (Task 5)

## Overview
Processes raw AIS trajectory data, applies spatio-temporal filtering around the estimated spill origin (from Task 4), and calculates explainable suspicion/attribution scores for candidate vessels.

## Attribution Scoring Formula
The attribution score is an explainable decision-support metric (0-100):
- **Proximity Score (50%)**: Inverse linear decay based on the Point of Closest Approach (PCA) within a 25 km threshold.
- **Temporal Score (35%)**: Proximity in time between vessel transit and the estimated spill window (12-hour window).
- **Trajectory Score (15%)**: Evaluates speed/course variability near the origin area.

## Output Schema (Task 6 Interface)
```json
{
  "spill_id": "SP-001",
  "vessels": [
    {
      "mmsi": "123456789",
      "name": "Vessel Alpha",
      "score": 91.2,
      "evidence": {
        "proximity_score": 95.0,
        "temporal_score": 90.0,
        "trajectory_score": 88.0,
        "closest_distance_km": 0.45,
        "closest_timestamp": "2026-09-06 10:05:00"
      }
    }
  ]
}