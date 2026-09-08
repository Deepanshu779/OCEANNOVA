from pathlib import Path
import json

import rasterio
from rasterio.features import shapes
from shapely.geometry import shape, mapping
from shapely.ops import transform as shapely_transform
from pyproj import Transformer


PROJECT_ROOT = Path(__file__).resolve().parents[2]

MASK_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "ai_predictions"
    / "SP-001_filtered_mask.tif"
)

OUTPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "ai_predictions"
    / "SP-001_spill.geojson"
)


def main():

    print("=" * 75)
    print("OCEANNOVA - AI SPILL MASK → GEOJSON")
    print("=" * 75)

    with rasterio.open(MASK_PATH) as src:

        mask = src.read(1) > 0
        transform = src.transform
        source_crs = src.crs

        print()
        print(f"Source CRS : {source_crs}")
        print(f"Raster size: {src.width} x {src.height}")
        print(f"Mask pixels: {int(mask.sum()):,}")

        # Extract connected mask regions.
        raw_shapes = shapes(
            mask.astype("uint8"),
            mask=mask,
            transform=transform
        )

    # Convert projected coordinates → WGS84.
    transformer = Transformer.from_crs(
        source_crs,
        "EPSG:4326",
        always_xy=True
    )

    features = []

    for geometry, value in raw_shapes:

        if value != 1:
            continue

        polygon = shape(geometry)

        if polygon.is_empty:
            continue

        polygon = shapely_transform(
            transformer.transform,
            polygon
        )

        # Remove tiny numerical artifacts.
        polygon = polygon.buffer(0)

        if polygon.is_empty:
            continue

        area_km2 = polygon.area * 111.32 * 111.32

        features.append({
            "type": "Feature",
            "geometry": mapping(polygon),
            "properties": {
                "incident_id": "SP-001",
                "type": "AI-detected-slick",
                "source": "Sentinel-1 SAR",
                "method": (
                    "U-Net segmentation + "
                    "radiometric filtering"
                ),
                "area_note": (
                    "Approximate geographic area"
                )
            }
        })

    geojson = {
        "type": "FeatureCollection",
        "name": "SP-001_AI_Spill_Footprint",
        "features": features
    }

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        OUTPUT_PATH,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            geojson,
            f,
            indent=2
        )

    print()
    print("=" * 75)
    print("EXPORT COMPLETE")
    print("=" * 75)

    print(
        f"Polygons exported : {len(features)}"
    )

    print(
        f"Output            : {OUTPUT_PATH}"
    )

    print()
    print("✓ CRS converted to EPSG:4326")
    print("✓ Ready for Leaflet")


if __name__ == "__main__":
    main()