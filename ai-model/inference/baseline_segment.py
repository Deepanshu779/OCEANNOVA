import json
from pathlib import Path

import cv2
import numpy as np
import rasterio
from rasterio.transform import xy
from rasterio.warp import transform_geom


IMAGE = Path(
    "data/external/Radar_data/test/images/2018_09_26.tif"
)

MASK = Path(
    "data/external/Radar_data/test/masks/2018_09_26.tif"
)


with rasterio.open(IMAGE) as src:
    image = src.read(1).astype(np.float32)
    transform = src.transform
    crs = src.crs


with rasterio.open(MASK) as src:
    ground_truth = src.read(1) > 0


# Normalize SAR backscatter for image processing
valid = np.isfinite(image)

low = np.percentile(image[valid], 2)
high = np.percentile(image[valid], 98)

normalized = np.clip(
    (image - low) / (high - low + 1e-8) * 255,
    0,
    255,
).astype(np.uint8)


# Smooth SAR speckle
blurred = cv2.GaussianBlur(
    normalized,
    (5, 5),
    0,
)


# Dark-region baseline segmentation
_, predicted = cv2.threshold(
    blurred,
    0,
    255,
    cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU,
)


predicted = predicted > 0


# Remove tiny components
num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(
    predicted.astype(np.uint8),
    connectivity=8,
)

clean = np.zeros_like(predicted)

MIN_PIXELS = 100

for label in range(1, num_labels):
    area = stats[label, cv2.CC_STAT_AREA]

    if area >= MIN_PIXELS:
        clean[labels == label] = True


predicted = clean


# Evaluation against ground truth
intersection = np.logical_and(
    predicted,
    ground_truth,
).sum()

union = np.logical_or(
    predicted,
    ground_truth,
).sum()

predicted_pixels = predicted.sum()
truth_pixels = ground_truth.sum()

iou = intersection / (union + 1e-8)

dice = (
    2 * intersection
    / (predicted_pixels + truth_pixels + 1e-8)
)


# Predicted centroid
rows, cols = np.where(predicted)

if len(rows) > 0:

    row = float(rows.mean())
    col = float(cols.mean())

    x, y = xy(
        transform,
        row,
        col,
    )

    centroid = transform_geom(
        crs,
        "EPSG:4326",
        {
            "type": "Point",
            "coordinates": [x, y],
        },
    )

    lon, lat = centroid["coordinates"]

else:
    lat = None
    lon = None


# Pixel area
pixel_area_m2 = abs(
    transform.a * transform.e
)

area_km2 = (
    predicted_pixels
    * pixel_area_m2
    / 1_000_000
)


# Save predicted mask
output_mask = Path(
    "data/processed/real_sample_prediction.tif"
)

with rasterio.open(
    output_mask,
    "w",
    driver="GTiff",
    height=predicted.shape[0],
    width=predicted.shape[1],
    count=1,
    dtype="uint8",
    crs=crs,
    transform=transform,
) as dst:

    dst.write(
        predicted.astype(np.uint8),
        1,
    )


result = {
    "image": str(IMAGE),
    "method": "SAR dark-region baseline",
    "ground_truth_pixels": int(truth_pixels),
    "predicted_pixels": int(predicted_pixels),
    "iou": round(float(iou), 4),
    "dice": round(float(dice), 4),
    "predicted_area_km2": round(float(area_km2), 4),
    "predicted_centroid": {
        "lat": round(float(lat), 6)
        if lat is not None else None,
        "lon": round(float(lon), 6)
        if lon is not None else None,
    },
    "prediction_mask": str(output_mask),
}


output_json = Path(
    "data/processed/real_sample_prediction.json"
)

output_json.write_text(
    json.dumps(result, indent=2),
    encoding="utf-8",
)


print()
print("=== OCEANNOVA REAL SAR BASELINE ===")
print(f"Image:             {IMAGE.name}")
print(f"Ground truth:      {truth_pixels:,} pixels")
print(f"Predicted pixels:  {predicted_pixels:,}")
print(f"IoU:               {iou:.4f}")
print(f"Dice:              {dice:.4f}")
print(f"Predicted area:    {area_km2:.4f} km²")
print(f"Predicted center:  {lat}, {lon}")
print(f"Prediction mask:   {output_mask}")
print(f"Result JSON:       {output_json}")