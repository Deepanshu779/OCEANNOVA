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


AI_THRESHOLD = 0.80
MIN_COMPONENT_PIXELS = 1000
MAX_COMPONENT_PIXELS = 600000


def normalize(image):

    image = image.astype(np.float32)

    valid = np.isfinite(image)

    values = image[valid]

    low = np.percentile(values, 2)
    high = np.percentile(values, 98)

    image = np.clip(image, low, high)

    return (image - low) / (high - low)


def component_perimeter(component):

    eroded = ndimage.binary_erosion(
        component,
        structure=np.ones((3, 3), dtype=bool)
    )

    boundary = component & ~eroded

    return np.count_nonzero(boundary)


def compactness(area, perimeter):

    if perimeter <= 0:
        return 0.0

    return (
        4.0 * np.pi * area
        / (perimeter ** 2)
    )


def evaluate_threshold(
    probability,
    image,
    truth,
    intensity_threshold
):

    raw_mask = probability >= AI_THRESHOLD

    labels, number = ndimage.label(
        raw_mask,
        structure=np.ones(
            (3, 3),
            dtype=np.uint8
        )
    )

    sizes = np.bincount(
        labels.ravel()
    )

    filtered = np.zeros_like(
        raw_mask,
        dtype=bool
    )

    kept = 0

    for component_id in range(
        1,
        number + 1
    ):

        area = int(
            sizes[component_id]
        )

        if area < MIN_COMPONENT_PIXELS:
            continue

        if area > MAX_COMPONENT_PIXELS:
            continue

        component = (
            labels == component_id
        )

        mean_intensity = float(
            np.mean(
                image[component]
            )
        )

        if mean_intensity > intensity_threshold:
            continue

        # Keep the same geometry criterion used previously.
        perimeter = component_perimeter(
            component
        )

        shape = compactness(
            area,
            perimeter
        )

        if shape < 0.005:
            continue

        filtered[component] = True
        kept += 1

    intersection = np.logical_and(
        filtered,
        truth
    ).sum()

    union = np.logical_or(
        filtered,
        truth
    ).sum()

    predicted = filtered.sum()
    actual = truth.sum()

    iou = (
        intersection / union
        if union
        else 0
    )

    dice = (
        2 * intersection
        / (predicted + actual)
        if predicted + actual
        else 0
    )

    precision = (
        intersection / predicted
        if predicted
        else 0
    )

    recall = (
        intersection / actual
        if actual
        else 0
    )

    return (
        kept,
        predicted,
        iou,
        dice,
        precision,
        recall
    )


def main():

    print("=" * 90)
    print("OCEANNOVA - RADIOMETRIC THRESHOLD SEARCH")
    print("=" * 90)

    probability = np.load(
        PROBABILITY_PATH
    )

    with rasterio.open(
        IMAGE_PATH
    ) as src:

        image = normalize(
            src.read(1)
        )

    with rasterio.open(
        GROUND_TRUTH_PATH
    ) as src:

        truth = src.read(1) > 0

    thresholds = [
        0.05,
        0.08,
        0.10,
        0.15,
        0.20,
        0.25,
        0.30,
        0.35,
        0.40,
        0.45,
        0.50,
    ]

    print()
    print(
        "Intensity | Kept | Pixels | IoU     | "
        "Dice    | Precision | Recall"
    )

    print("-" * 90)

    results = []

    for threshold in thresholds:

        result = evaluate_threshold(
            probability,
            image,
            truth,
            threshold
        )

        (
            kept,
            pixels,
            iou,
            dice,
            precision,
            recall
        ) = result

        results.append(
            (
                threshold,
                kept,
                pixels,
                iou,
                dice,
                precision,
                recall
            )
        )

        print(
            f"{threshold:9.2f} | "
            f"{kept:4d} | "
            f"{pixels:7,d} | "
            f"{iou:.4f} | "
            f"{dice:.4f} | "
            f"{precision:.4f}   | "
            f"{recall:.4f}"
        )

    best = max(
        results,
        key=lambda x: x[3]
    )

    print()
    print("=" * 90)
    print("BEST RADIOMETRIC THRESHOLD")
    print("=" * 90)

    print(
        f"Intensity threshold : {best[0]:.2f}"
    )

    print(
        f"Components kept     : {best[1]}"
    )

    print(
        f"Predicted pixels    : {best[2]:,}"
    )

    print(
        f"IoU                 : {best[3]:.4f}"
    )

    print(
        f"Dice                : {best[4]:.4f}"
    )

    print(
        f"Precision           : {best[5]:.4f}"
    )

    print(
        f"Recall              : {best[6]:.4f}"
    )


if __name__ == "__main__":
    main()