from pathlib import Path
import json
import os

# Prevent PostgreSQL's bundled PROJ database from overriding
# the PROJ installation used by Rasterio/Python.
os.environ.pop("PROJ_DATA", None)
os.environ.pop("PROJ_LIB", None)

import numpy as np
import rasterio
from scipy import ndimage
from rasterio.transform import xy
from rasterio.warp import transform as warp_transform


PROJECT_ROOT = Path(__file__).resolve().parents[2]

MASK_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "ai_predictions"
    / "SP-001_filtered_mask.tif"
)

PROBABILITY_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "ai_predictions"
    / "SP-001_probability.npy"
)

OUTPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "ai_predictions"
    / "SP-001_characterization.json"
)


def calculate_perimeter(mask):

    eroded = ndimage.binary_erosion(
        mask,
        structure=np.ones(
            (3, 3),
            dtype=bool
        )
    )

    boundary = mask & ~eroded

    return int(
        np.count_nonzero(boundary)
    )


def main():

    print("=" * 70)
    print("OCEANNOVA - SPILL CHARACTERIZATION")
    print("=" * 70)

    with rasterio.open(MASK_PATH) as src:

        mask = src.read(1) > 0

        transform = src.transform

        crs = src.crs

        pixel_width = abs(
            transform.a
        )

        pixel_height = abs(
            transform.e
        )

    probability = np.load(
        PROBABILITY_PATH
    )

    # --------------------------------------------------------
    # Basic geometry
    # --------------------------------------------------------

    spill_pixels = int(
        np.count_nonzero(mask)
    )

    pixel_area_m2 = (
        pixel_width
        * pixel_height
    )

    area_km2 = (
        spill_pixels
        * pixel_area_m2
        / 1_000_000
    )

    perimeter_pixels = (
        calculate_perimeter(mask)
    )

    # Approximate perimeter using mean pixel dimension.
    mean_pixel_size = (
        pixel_width
        + pixel_height
    ) / 2

    perimeter_km = (
        perimeter_pixels
        * mean_pixel_size
        / 1000
    )

    # --------------------------------------------------------
    # Compactness
    # --------------------------------------------------------

    if perimeter_km > 0:

        compactness = (
            4
            * np.pi
            * area_km2
            / (
                perimeter_km ** 2
            )
        )

    else:

        compactness = 0.0

    # --------------------------------------------------------
    # Centroid
    # --------------------------------------------------------

    rows, cols = np.where(
        mask
    )

    if len(rows) > 0:

        center_row = float(
            np.mean(rows)
        )

        center_col = float(
            np.mean(cols)
        )

        center_x, center_y = xy(
    transform,
            center_row,
            center_col
        )

        # Convert projected CRS coordinates to WGS84.
        center_lon, center_lat = warp_transform(
            crs,
            "EPSG:4326",
            [center_x],
            [center_y]
        )

        center_lon = center_lon[0]
        center_lat = center_lat[0]

    else:

        center_lat = None
        center_lon = None

    # --------------------------------------------------------
    # AI confidence
    # --------------------------------------------------------

    selected_probabilities = (
        probability[mask]
    )

    if len(
        selected_probabilities
    ) > 0:

        mean_confidence = float(
            np.mean(
                selected_probabilities
            )
        )

        max_confidence = float(
            np.max(
                selected_probabilities
            )
        )

    else:

        mean_confidence = 0.0
        max_confidence = 0.0

    # --------------------------------------------------------
    # Connected components
    # --------------------------------------------------------

    labels, component_count = (
        ndimage.label(
            mask,
            structure=np.ones(
                (3, 3)
            )
        )
    )

    component_sizes = np.bincount(
        labels.ravel()
    )

    valid_sizes = (
        component_sizes[1:]
    )

    largest_component = (
        int(
            valid_sizes.max()
        )
        if len(valid_sizes)
        else 0
    )

    # --------------------------------------------------------
    # Result
    # --------------------------------------------------------

    result = {

        "incident_id": "SP-001",

        "source": {
            "type": "Sentinel-1 SAR",
            "scene": "2018_09_26.tif",
            "crs": str(crs)
        },

        "detection": {
            "method": (
                "U-Net segmentation + "
                "radiometric filtering"
            ),
            "spill_pixels": spill_pixels,
            "area_km2": round(
                area_km2,
                4
            ),
            "perimeter_km": round(
                perimeter_km,
                4
            ),
            "compactness": round(
                compactness,
                4
            ),
            "mean_ai_confidence": round(
                mean_confidence,
                4
            ),
            "max_ai_confidence": round(
                max_confidence,
                4
            ),
            "components": int(
                component_count
            ),
            "largest_component_pixels": (
                largest_component
            )
        },

        "centroid": {
            "latitude": (
                float(center_lat)
                if center_lat is not None
                else None
            ),
            "longitude": (
                float(center_lon)
                if center_lon is not None
                else None
            )
        },

        "status": (
            "prototype_spill_characterization"
        )
    }

    with open(
        OUTPUT_PATH,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            result,
            f,
            indent=2
        )

    print()
    print("=" * 70)
    print("CHARACTERIZATION COMPLETE")
    print("=" * 70)

    print(
        f"Spill pixels       : "
        f"{spill_pixels:,}"
    )

    print(
        f"Area               : "
        f"{area_km2:.4f} km²"
    )

    print(
        f"Perimeter          : "
        f"{perimeter_km:.4f} km"
    )

    print(
        f"Compactness        : "
        f"{compactness:.4f}"
    )

    print(
        f"Components         : "
        f"{component_count}"
    )

    print(
        f"Mean AI confidence : "
        f"{mean_confidence:.4f}"
    )

    print(
        f"Centroid           : "
        f"{center_lat}, {center_lon}"
    )

    print()
    print(
        f"✓ Saved: {OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()