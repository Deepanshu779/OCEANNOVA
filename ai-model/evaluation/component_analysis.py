from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage


PROJECT_ROOT = Path(__file__).resolve().parents[2]

PROBABILITY_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "ai_predictions"
    / "SP-001_probability.npy"
)

IMAGE_PATH = (
    PROJECT_ROOT
    / "data"
    / "external"
    / "Radar_data"
    / "test"
    / "images"
    / "2018_09_26.tif"
)

GROUND_TRUTH_PATH = (
    PROJECT_ROOT
    / "data"
    / "external"
    / "Radar_data"
    / "test"
    / "masks"
    / "2018_09_26.tif"
)


THRESHOLD = 0.80


def normalize(image):

    image = image.astype(np.float32)

    valid = np.isfinite(image)

    values = image[valid]

    low = np.percentile(values, 2)
    high = np.percentile(values, 98)

    image = np.clip(image, low, high)

    return (image - low) / (high - low)


def compactness(area, perimeter):

    if perimeter <= 0:
        return 0.0

    return (
        4 * np.pi * area
        / (perimeter ** 2)
    )


def main():

    probability = np.load(
        PROBABILITY_PATH
    )

    with rasterio.open(IMAGE_PATH) as src:
        image = normalize(src.read(1))

    with rasterio.open(GROUND_TRUTH_PATH) as src:
        truth = src.read(1) > 0

    raw_mask = (
        probability >= THRESHOLD
    )

    labels, count = ndimage.label(
        raw_mask,
        structure=np.ones((3, 3))
    )

    sizes = np.bincount(
        labels.ravel()
    )

    results = []

    for component_id in range(
        1,
        count + 1
    ):

        area = int(
            sizes[component_id]
        )

        if area < 100:
            continue

        component = (
            labels == component_id
        )

        values = probability[
            component
        ]

        intensities = image[
            component
        ]

        intersection = np.logical_and(
            component,
            truth
        ).sum()

        perimeter_mask = (
            component
            & ~ndimage.binary_erosion(
                component,
                structure=np.ones((3, 3))
            )
        )

        perimeter = (
            np.count_nonzero(
                perimeter_mask
            )
        )

        results.append({
            "id": component_id,
            "area": area,
            "mean_probability": float(
                np.mean(values)
            ),
            "mean_intensity": float(
                np.mean(intensities)
            ),
            "compactness": compactness(
                area,
                perimeter
            ),
            "gt_overlap": int(
                intersection
            ),
        })

    results.sort(
        key=lambda x: x["area"],
        reverse=True
    )

    print("=" * 95)
    print(
        "OCEANNOVA - COMPONENT ANALYSIS"
    )
    print("=" * 95)

    print(
        f"{'ID':>5} "
        f"{'Area':>10} "
        f"{'AI Prob':>10} "
        f"{'Intensity':>11} "
        f"{'Compact':>10} "
        f"{'GT overlap':>12}"
    )

    print("-" * 95)

    for r in results[:30]:

        print(
            f"{r['id']:>5} "
            f"{r['area']:>10,} "
            f"{r['mean_probability']:>10.4f} "
            f"{r['mean_intensity']:>11.4f} "
            f"{r['compactness']:>10.4f} "
            f"{r['gt_overlap']:>12,}"
        )


if __name__ == "__main__":
    main()