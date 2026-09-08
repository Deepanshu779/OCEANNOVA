"""Transparent spill-age estimation helpers.

Age is reported as an estimate/range, not as a precise physical-age claim.
The estimator uses the hindcast window and observation timestamp supplied by
the investigation pipeline.
"""
from __future__ import annotations

from datetime import datetime, timedelta


def estimate_age_hours(observed_time: datetime, origin_time: datetime, uncertainty_hours: float = 2.0) -> dict:
    """Return an interpretable age estimate with an uncertainty interval."""
    age = max(0.0, (observed_time - origin_time).total_seconds() / 3600.0)
    return {
        "estimated_age_hours": round(age, 1),
        "lower_hours": round(max(0.0, age - uncertainty_hours), 1),
        "upper_hours": round(age + uncertainty_hours, 1),
        "status": "hindcast_window_estimate",
        "note": "Estimated from reconstructed origin-time window; not a direct chemical age measurement.",
    }
