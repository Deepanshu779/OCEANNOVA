"""
OCEANNOVA - AI Prediction Post-Processing

Purpose:
    Reduce false positives from the U-Net prediction using:
    1. Confidence threshold
    2. Connected-component filtering
    3. Component size filtering
    4. SAR radiometric darkness
    5. Shape compactness

This is a prototype look-alike filtering stage.
"""

from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage
import matplotlib.pyplot as plt


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

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

PROBABILITY_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "ai_predictions"
    / "SP-001_probability.npy"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "ai_predictions"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

OUTPUT_MASK = (
    OUTPUT_DIR
    / "SP-001_filtered_mask.tif"
)

OUTPUT_OVERLAY = (
    OUTPUT_DIR
    / "SP-001_filtered_overlay.png"
)


# ============================================================
# FILTER CONFIGURATION
# ============================================================

CONFIDENCE_THRESHOLD = 0.80

# Component size in pixels.
MIN_COMPONENT_PIXELS = 1000
MAX_COMPONENT_PIXELS = 600000

# A component should generally be darker than this
# scene-relative intensity percentile.
CONFIDENCE_THRESHOLD = 0.80

MIN_COMPONENT_PIXELS = 1000
MAX_COMPONENT_PIXELS = 600000

INTENSITY_THRESHOLD = 0.15

# Minimum compactness.
# Compactness = 4*pi*area / perimeter^2
MIN_COMPACTNESS = 0.005


# ============================================================
# NORMALIZATION
# ============================================================

def normalize(image):

    image = image.astype(
        np.float32
    )

    valid = np.isfinite(image)

    if not np.any(valid):
        return np.zeros_like(
            image,
            dtype=np.float32
        )

    values = image[valid]

    low = np.percentile(
        values,
        2
    )

    high = np.percentile(
        values,
        98
    )

    if high <= low:
        return np.zeros_like(
            image,
            dtype=np.float32
        )

    image = np.clip(
        image,
        low,
        high
    )

    return (
        (image - low)
        / (high - low)
    ).astype(np.float32)


# ============================================================
# COMPONENT COMPACTNESS
# ============================================================

def component_perimeter(component):

    """
    Approximate perimeter using binary erosion.
    """

    eroded = ndimage.binary_erosion(
        component,
        structure=np.ones(
            (3, 3),
            dtype=bool
        )
    )

    boundary = (
        component
        & ~eroded
    )

    return float(
        np.count_nonzero(boundary)
    )


def compactness(
    area,
    perimeter
):

    if perimeter <= 0:
        return 0.0

    return (
        4.0
        * np.pi
        * area
        / (perimeter ** 2)
    )


# ============================================================
# MAIN FILTER
# ============================================================

def main():

    print("=" * 70)
    print("OCEANNOVA - LOOK-ALIKE FILTER")
    print("=" * 70)

    # --------------------------------------------------------
    # Load probability map
    # --------------------------------------------------------

    probability = np.load(
        PROBABILITY_PATH
    )

    # --------------------------------------------------------
    # Load SAR image
    # --------------------------------------------------------

    with rasterio.open(
        IMAGE_PATH
    ) as src:

        image = src.read(1)

        profile = src.profile.copy()

    normalized = normalize(
        image
    )

    # --------------------------------------------------------
    # Load ground truth for evaluation
    # --------------------------------------------------------

    with rasterio.open(
        GROUND_TRUTH_PATH
    ) as src:

        ground_truth = (
            src.read(1) > 0
        )

    # --------------------------------------------------------
    # Initial AI mask
    # --------------------------------------------------------

    raw_mask = (
        probability
        >= CONFIDENCE_THRESHOLD
    )

    print(
        f"Raw AI pixels: "
        f"{np.count_nonzero(raw_mask):,}"
    )

    # --------------------------------------------------------
    # Connected components
    # --------------------------------------------------------

    labels, number = (
        ndimage.label(
            raw_mask,
            structure=np.ones(
                (3, 3),
                dtype=np.uint8
            )
        )
    )

    print(
        f"Connected components: "
        f"{number:,}"
    )

    component_sizes = np.bincount(
        labels.ravel()
    )

    # Scene-level intensity threshold.
    intensity_threshold = INTENSITY_THRESHOLD

    print(
        f"Radiometric intensity threshold: "
        f"{intensity_threshold:.4f}"
    )

    # --------------------------------------------------------
    # Filter components
    # --------------------------------------------------------

    filtered_mask = np.zeros_like(
        raw_mask,
        dtype=bool
    )

    kept = 0
    rejected_small = 0
    rejected_large = 0
    rejected_bright = 0
    rejected_shape = 0

    for component_id in range(
        1,
        number + 1
    ):

        area = int(
            component_sizes[
                component_id
            ]
        )

        # Size filter
        if area < MIN_COMPONENT_PIXELS:

            rejected_small += 1

            continue

        if area > MAX_COMPONENT_PIXELS:

            rejected_large += 1

            continue

        component = (
            labels
            == component_id
        )

        # ----------------------------------------------------
        # Radiometric feature
        # ----------------------------------------------------

        component_values = (
            normalized[component]
        )

        mean_intensity = float(
            np.mean(
                component_values
            )
        )

        # Reject bright SAR structures.
        if mean_intensity > intensity_threshold:

            rejected_bright += 1

            continue

        # ----------------------------------------------------
        # Geometry
        # ----------------------------------------------------

        perimeter = component_perimeter(
            component
        )

        shape_score = compactness(
            area,
            perimeter
        )

        if shape_score < MIN_COMPACTNESS:

            rejected_shape += 1

            continue

        # Keep component
        filtered_mask[
            component
        ] = True

        kept += 1

    # --------------------------------------------------------
    # Results
    # --------------------------------------------------------

    print()
    print(
        "Filtering results:"
    )

    print(
        f"Kept components       : {kept}"
    )

    print(
        f"Rejected small        : "
        f"{rejected_small}"
    )

    print(
        f"Rejected large        : "
        f"{rejected_large}"
    )

    print(
        f"Rejected bright       : "
        f"{rejected_bright}"
    )

    print(
        f"Rejected shape        : "
        f"{rejected_shape}"
    )

    print()

    raw_pixels = int(
        np.count_nonzero(
            raw_mask
        )
    )

    filtered_pixels = int(
        np.count_nonzero(
            filtered_mask
        )
    )

    gt_pixels = int(
        np.count_nonzero(
            ground_truth
        )
    )

    # --------------------------------------------------------
    # Metrics
    # --------------------------------------------------------

    intersection = np.logical_and(
        filtered_mask,
        ground_truth
    ).sum()

    union = np.logical_or(
        filtered_mask,
        ground_truth
    ).sum()

    iou = (
        intersection / union
        if union > 0
        else 0.0
    )

    dice = (
        2 * intersection
        / (
            filtered_pixels
            + gt_pixels
        )
        if (
            filtered_pixels
            + gt_pixels
        ) > 0
        else 0.0
    )

    precision = (
        intersection
        / filtered_pixels
        if filtered_pixels > 0
        else 0.0
    )

    recall = (
        intersection
        / gt_pixels
        if gt_pixels > 0
        else 0.0
    )

    print("=" * 70)
    print("FILTERED RESULT")
    print("=" * 70)

    print(
        f"Raw pixels      : "
        f"{raw_pixels:,}"
    )

    print(
        f"Filtered pixels : "
        f"{filtered_pixels:,}"
    )

    print(
        f"Ground truth    : "
        f"{gt_pixels:,}"
    )

    print()

    print(
        f"IoU             : "
        f"{iou:.4f}"
    )

    print(
        f"Dice            : "
        f"{dice:.4f}"
    )

    print(
        f"Precision       : "
        f"{precision:.4f}"
    )

    print(
        f"Recall          : "
        f"{recall:.4f}"
    )

    # --------------------------------------------------------
    # Save GeoTIFF
    # --------------------------------------------------------

    output_profile = profile.copy()

    output_profile.update(
        {
            "driver": "GTiff",
            "dtype": "uint8",
            "count": 1,
            "compress": "lzw",
            "nodata": 0,
        }
    )

    with rasterio.open(
        OUTPUT_MASK,
        "w",
        **output_profile
    ) as dst:

        dst.write(
            filtered_mask.astype(
                np.uint8
            ),
            1
        )

    print()
    print(
        f"✓ Filtered mask saved:"
    )

    print(
        OUTPUT_MASK
    )

    # --------------------------------------------------------
    # Save visualization
    # --------------------------------------------------------

    plt.figure(
        figsize=(12, 7)
    )

    plt.imshow(
        normalized,
        cmap="gray"
    )

    overlay = np.ma.masked_where(
        ~filtered_mask,
        filtered_mask
    )

    plt.imshow(
        overlay,
        alpha=0.50
    )

    plt.title(
        "OCEANNOVA - Validated Oil Spill Candidate"
    )

    plt.axis("off")

    plt.tight_layout()

    plt.savefig(
        OUTPUT_OVERLAY,
        dpi=180,
        bbox_inches="tight"
    )

    plt.close()

    print(
        f"✓ Overlay saved:"
    )

    print(
        OUTPUT_OVERLAY
    )


if __name__ == "__main__":
    main()