from pathlib import Path

import numpy as np
import rasterio


PROJECT_ROOT = Path(__file__).resolve().parents[2]

PROBABILITY_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "ai_predictions"
    / "SP-001_probability.npy"
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


def calculate_metrics(prediction, truth):

    prediction = prediction.astype(bool)
    truth = truth.astype(bool)

    intersection = np.logical_and(
        prediction,
        truth
    ).sum()

    union = np.logical_or(
        prediction,
        truth
    ).sum()

    pred_count = prediction.sum()
    truth_count = truth.sum()

    iou = (
        intersection / union
        if union > 0
        else 0
    )

    dice = (
        2 * intersection
        / (pred_count + truth_count)
        if (pred_count + truth_count) > 0
        else 0
    )

    precision = (
        intersection / pred_count
        if pred_count > 0
        else 0
    )

    recall = (
        intersection / truth_count
        if truth_count > 0
        else 0
    )

    return (
        iou,
        dice,
        precision,
        recall,
        pred_count
    )


def main():

    print("=" * 70)
    print("OCEANNOVA - THRESHOLD OPTIMIZATION")
    print("=" * 70)

    probability = np.load(
        PROBABILITY_PATH
    )

    with rasterio.open(
        GROUND_TRUTH_PATH
    ) as src:

        truth = src.read(1) > 0

    print(
        f"Probability shape: "
        f"{probability.shape}"
    )

    print(
        f"Ground truth shape: "
        f"{truth.shape}"
    )

    print()

    thresholds = [
        0.30,
        0.40,
        0.45,
        0.50,
        0.55,
        0.60,
        0.65,
        0.70,
        0.75,
        0.80,
    ]

    results = []

    print(
        "Threshold | IoU     | Dice    | "
        "Precision | Recall  | Pixels"
    )

    print("-" * 70)

    for threshold in thresholds:

        prediction = (
            probability >= threshold
        )

        (
            iou,
            dice,
            precision,
            recall,
            pixels
        ) = calculate_metrics(
            prediction,
            truth
        )

        results.append(
            (
                threshold,
                iou,
                dice,
                precision,
                recall,
                pixels
            )
        )

        print(
            f"{threshold:9.2f} | "
            f"{iou:.4f} | "
            f"{dice:.4f} | "
            f"{precision:.4f}   | "
            f"{recall:.4f} | "
            f"{pixels:,}"
        )

    best = max(
        results,
        key=lambda x: x[1]
    )

    print()
    print("=" * 70)
    print("BEST THRESHOLD")
    print("=" * 70)

    print(
        f"Threshold : {best[0]:.2f}"
    )

    print(
        f"IoU       : {best[1]:.4f}"
    )

    print(
        f"Dice      : {best[2]:.4f}"
    )

    print(
        f"Precision : {best[3]:.4f}"
    )

    print(
        f"Recall    : {best[4]:.4f}"
    )

    print(
        f"Pixels    : {best[5]:,}"
    )


if __name__ == "__main__":
    main()