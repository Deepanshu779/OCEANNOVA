"""Spill geometry and age-estimation helpers for detected masks."""

from datetime import datetime, timezone
from math import sqrt


def characterize_spill(mask_pixels: int, pixel_area_m2: float, width_px: int, height_px: int) -> dict:
    """Return demo-friendly geometric properties from a binary spill mask."""
    area_m2 = max(0, mask_pixels) * max(0.0, pixel_area_m2)
    area_km2 = area_m2 / 1_000_000.0
    perimeter_px = 2.0 * (sqrt(max(1, mask_pixels)) * 2.0)
    compactness = min(1.0, (4.0 * 3.141592653589793 * max(1.0, mask_pixels)) / max(1.0, perimeter_px**2))
    return {
        "area_km2": round(area_km2, 4),
        "mask_pixels": int(mask_pixels),
        "image_width_px": int(width_px),
        "image_height_px": int(height_px),
        "perimeter_estimate_px": round(perimeter_px, 2),
        "compactness_estimate": round(compactness, 4),
    }


def estimate_age_hours(acquisition_time: datetime, reference_time: datetime | None = None) -> float:
    """Estimate elapsed age from an observed timestamp when a reference time exists."""
    if acquisition_time.tzinfo is None:
        acquisition_time = acquisition_time.replace(tzinfo=timezone.utc)
    if reference_time is None:
        reference_time = datetime.now(timezone.utc)
    elif reference_time.tzinfo is None:
        reference_time = reference_time.replace(tzinfo=timezone.utc)
    return round(max(0.0, (reference_time - acquisition_time).total_seconds() / 3600.0), 2)
