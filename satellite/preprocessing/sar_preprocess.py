"""Lightweight Sentinel-1 SAR preprocessing utilities.

The functions operate on numpy arrays so the module can be reused by inference
code without coupling the core pipeline to a particular download service.
"""

import numpy as np


def percentile_normalize(image: np.ndarray, low: float = 2.0, high: float = 98.0) -> np.ndarray:
    """Normalize finite SAR backscatter values to uint8 [0, 255]."""
    values = image[np.isfinite(image)]
    if values.size == 0:
        raise ValueError("SAR image contains no finite pixels")
    lo = float(np.percentile(values, low))
    hi = float(np.percentile(values, high))
    if hi <= lo:
        return np.zeros(image.shape, dtype=np.uint8)
    normalized = np.clip((image - lo) / (hi - lo) * 255.0, 0, 255)
    return np.nan_to_num(normalized, nan=0.0).astype(np.uint8)


def prepare_sar(image: np.ndarray) -> np.ndarray:
    """Prepare a SAR array for segmentation while preserving its dimensions."""
    if image.ndim != 2:
        raise ValueError("Expected a single-band 2D SAR array")
    return percentile_normalize(image)
