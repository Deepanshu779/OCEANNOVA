import json
from pathlib import Path

import numpy as np
import rasterio
from rasterio.features import shapes
from rasterio.warp import transform_geom


IMAGE = Path(
    "data/external/Radar_data/test/images/2018_09_26.tif"
)

MASK = Path(
    "data/external/Radar_data/test/masks/2018_09_26.tif"
)


with rasterio.open(IMAGE) as image_src:
    image = image_src.read(1)
    image_crs = image_src.crs
    transform = image_src.transform

with rasterio.open(MASK) as mask_src:
    mask = mask_src.read(1)


# Basic validation
if image.shape != mask.shape:
    raise ValueError(
        f"Image/mask mismatch: {image.shape} vs {mask.shape}"
    )


# Treat non-zero mask pixels as spill pixels
spill_pixels = mask > 0

pixel_count = int(spill_pixels.sum())

if pixel_count == 0:
    raise ValueError("No spill pixels found in mask.")


# Pixel dimensions in projected CRS
pixel_width = abs(transform.a)
pixel_height = abs(transform.e)

pixel_area_m2 = pixel_width * pixel_height
area_km2 = (pixel_count * pixel_area_m2) / 1_000_000


# Spill bounding box
rows, cols = np.where(spill_pixels)

min_row, max_row = rows.min(), rows.max()
min_col, max_col = cols.min(), cols.max()


# Pixel centroid
centroid_row = float(rows.mean())
centroid_col = float(cols.mean())


# Convert centroid to map coordinates
x, y = rasterio.transform.xy(
    transform,
    centroid_row,
    centroid_col
)


# Convert UTM → WGS84
centroid_geom = {
    "type": "Point",
    "coordinates": [x, y]
}

centroid_wgs84 = transform_geom(
    image_crs,
    "EPSG:4326",
    centroid_geom
)

lon, lat = centroid_wgs84["coordinates"]


result = {
    "dataset": "Sentinel-1A oil spill sample",
    "image": str(IMAGE),
    "mask": str(MASK),
    "width": int(image.shape[1]),
    "height": int(image.shape[0]),
    "spill_pixels": pixel_count,
    "estimated_area_km2": round(area_km2, 4),
    "centroid": {
        "lat": round(lat, 6),
        "lon": round(lon, 6),
    },
    "crs": str(image_crs),
    "status": "validated",
}


output = Path("data/processed/real_sample_SP001.json")
output.parent.mkdir(parents=True, exist_ok=True)

output.write_text(
    json.dumps(result, indent=2),
    encoding="utf-8"
)


print("\n=== OCEANNOVA REAL DATA VALIDATION ===")
print(f"Image:        {IMAGE.name}")
print(f"Dimensions:   {image.shape[1]} x {image.shape[0]}")
print(f"Spill pixels: {pixel_count}")
print(f"Area:         {area_km2:.4f} km²")
print(f"Centroid:     {lat:.6f}, {lon:.6f}")
print(f"CRS:          {image_crs}")
print(f"\nSaved: {output}")