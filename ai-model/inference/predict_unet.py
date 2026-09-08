"""
OCEANNOVA
Full-scene Sentinel-1 Oil Spill Inference

Takes a large Sentinel-1 GeoTIFF, runs the trained U-Net
on 256x256 tiles, stitches the predictions together, and
produces:

    data/processed/ai_predictions/
        SP-001_predicted_mask.tif
        SP-001_prediction_overlay.png
        SP-001_prediction.json
"""

from pathlib import Path
import json

import numpy as np
import rasterio
from rasterio.windows import Window
from rasterio.transform import xy
from rasterio.plot import reshape_as_image

import torch
import torch.nn as nn

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

MODEL_PATH = (
    PROJECT_ROOT
    / "ai-model"
    / "models"
    / "oceannova_unet.pth"
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

MASK_PATH = (
    OUTPUT_DIR
    / "SP-001_predicted_mask.tif"
)

PROBABILITY_PATH = (
    OUTPUT_DIR
    / "SP-001_probability.npy"
)

OVERLAY_PATH = (
    OUTPUT_DIR
    / "SP-001_prediction_overlay.png"
)

JSON_PATH = (
    OUTPUT_DIR
    / "SP-001_prediction.json"
)


# ============================================================
# CONFIG
# ============================================================

IMAGE_SIZE = 256

THRESHOLD = 0.5

DEVICE = torch.device(
    "cuda"
    if torch.cuda.is_available()
    else "cpu"
)


# ============================================================
# U-NET
# ============================================================

class DoubleConv(nn.Module):

    def __init__(
        self,
        in_channels,
        out_channels
    ):

        super().__init__()

        self.block = nn.Sequential(

            nn.Conv2d(
                in_channels,
                out_channels,
                3,
                padding=1,
                bias=False
            ),

            nn.BatchNorm2d(
                out_channels
            ),

            nn.ReLU(inplace=True),

            nn.Conv2d(
                out_channels,
                out_channels,
                3,
                padding=1,
                bias=False
            ),

            nn.BatchNorm2d(
                out_channels
            ),

            nn.ReLU(inplace=True),
        )

    def forward(self, x):
        return self.block(x)


class UNet(nn.Module):

    def __init__(self):

        super().__init__()

        self.enc1 = DoubleConv(1, 16)
        self.enc2 = DoubleConv(16, 32)
        self.enc3 = DoubleConv(32, 64)

        self.pool = nn.MaxPool2d(2)

        self.bottleneck = DoubleConv(
            64,
            128
        )

        self.up3 = nn.ConvTranspose2d(
            128,
            64,
            2,
            stride=2
        )

        self.dec3 = DoubleConv(
            128,
            64
        )

        self.up2 = nn.ConvTranspose2d(
            64,
            32,
            2,
            stride=2
        )

        self.dec2 = DoubleConv(
            64,
            32
        )

        self.up1 = nn.ConvTranspose2d(
            32,
            16,
            2,
            stride=2
        )

        self.dec1 = DoubleConv(
            32,
            16
        )

        self.output = nn.Conv2d(
            16,
            1,
            1
        )

    def forward(self, x):

        e1 = self.enc1(x)

        e2 = self.enc2(
            self.pool(e1)
        )

        e3 = self.enc3(
            self.pool(e2)
        )

        b = self.bottleneck(
            self.pool(e3)
        )

        d3 = self.up3(b)

        d3 = torch.cat(
            [d3, e3],
            dim=1
        )

        d3 = self.dec3(d3)

        d2 = self.up2(d3)

        d2 = torch.cat(
            [d2, e2],
            dim=1
        )

        d2 = self.dec2(d2)

        d1 = self.up1(d2)

        d1 = torch.cat(
            [d1, e1],
            dim=1
        )

        d1 = self.dec1(d1)

        return self.output(d1)


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

    image = (
        image - low
    ) / (
        high - low
    )

    return image.astype(
        np.float32
    )


# ============================================================
# LOAD MODEL
# ============================================================

def load_model():

    print("Loading model...")

    model = UNet().to(DEVICE)

    checkpoint = torch.load(
        MODEL_PATH,
        map_location=DEVICE
    )

    model.load_state_dict(
        checkpoint["model_state_dict"]
    )

    model.eval()

    print(
        f"Model loaded: {MODEL_PATH}"
    )

    print(
        f"Training IoU: "
        f"{checkpoint.get('iou', 0):.4f}"
    )

    print(
        f"Training Dice: "
        f"{checkpoint.get('dice', 0):.4f}"
    )

    return model


# ============================================================
# FULL-SCENE PREDICTION
# ============================================================

def predict_scene(model):

    print()
    print("=" * 60)
    print("OCEANNOVA FULL-SCENE INFERENCE")
    print("=" * 60)

    print(f"Image : {IMAGE_PATH}")
    print(f"Device: {DEVICE}")
    print()

    with rasterio.open(IMAGE_PATH) as src:

        width = src.width
        height = src.height

        profile = src.profile.copy()

        print(
            f"Scene dimensions: "
            f"{width} x {height}"
        )

        # -----------------------------------------------
        # Probability accumulation
        # -----------------------------------------------

        probability_sum = np.zeros(
            (height, width),
            dtype=np.float32
        )

        prediction_count = np.zeros(
            (height, width),
            dtype=np.float32
        )

        # -----------------------------------------------
        # Generate tiles
        # -----------------------------------------------

        total_tiles_x = (
            (width + IMAGE_SIZE - 1)
            // IMAGE_SIZE
        )

        total_tiles_y = (
            (height + IMAGE_SIZE - 1)
            // IMAGE_SIZE
        )

        total_tiles = (
            total_tiles_x
            * total_tiles_y
        )

        tile_number = 0

        for y in range(
            0,
            height,
            IMAGE_SIZE
        ):

            for x in range(
                0,
                width,
                IMAGE_SIZE
            ):

                tile_number += 1

                actual_width = min(
                    IMAGE_SIZE,
                    width - x
                )

                actual_height = min(
                    IMAGE_SIZE,
                    height - y
                )

                window = Window(
                    x,
                    y,
                    actual_width,
                    actual_height
                )

                image = src.read(
                    1,
                    window=window
                )

                image = normalize(
                    image
                )

                # ---------------------------------------
                # Pad edge tiles
                # ---------------------------------------

                padded = np.zeros(
                    (
                        IMAGE_SIZE,
                        IMAGE_SIZE
                    ),
                    dtype=np.float32
                )

                padded[
                    :actual_height,
                    :actual_width
                ] = image

                tensor = torch.from_numpy(
                    padded
                ).float()

                tensor = tensor.unsqueeze(
                    0
                ).unsqueeze(
                    0
                )

                tensor = tensor.to(
                    DEVICE
                )

                # ---------------------------------------
                # AI prediction
                # ---------------------------------------

                with torch.no_grad():

                    logits = model(
                        tensor
                    )

                    probabilities = torch.sigmoid(
                        logits
                    )[0, 0]

                probabilities = (
                    probabilities
                    .detach()
                    .cpu()
                    .numpy()
                )

                probabilities = probabilities[
                    :actual_height,
                    :actual_width
                ]

                probability_sum[
                    y:y + actual_height,
                    x:x + actual_width
                ] += probabilities

                prediction_count[
                    y:y + actual_height,
                    x:x + actual_width
                ] += 1

                if (
                    tile_number % 50 == 0
                    or tile_number == total_tiles
                ):

                    print(
                        f"Processed "
                        f"{tile_number}/"
                        f"{total_tiles} tiles"
                    )

        # -----------------------------------------------
        # Stitch tiles
        # -----------------------------------------------

        probability_map = (
            probability_sum
            / np.maximum(
                prediction_count,
                1
            )
        )

        predicted_mask = (
            probability_map
            >= THRESHOLD
        ).astype(
            np.uint8
        )

        return (
            predicted_mask,
            probability_map,
            profile,
            width,
            height,
            src.transform,
            src.crs
        )


# ============================================================
# GEOSPATIAL STATISTICS
# ============================================================

def calculate_statistics(
    mask,
    probability_map,
    transform,
    crs
):

    spill_pixels = int(
        np.count_nonzero(mask)
    )

    # -----------------------------------------------
    # Pixel area
    # -----------------------------------------------

    pixel_width = abs(
        transform.a
    )

    pixel_height = abs(
        transform.e
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

    # -----------------------------------------------
    # Confidence
    # -----------------------------------------------

    predicted_probabilities = (
        probability_map[mask == 1]
    )

    if len(predicted_probabilities) > 0:

        confidence = float(
            np.mean(
                predicted_probabilities
            )
        )

    else:

        confidence = 0.0

    # -----------------------------------------------
    # Centroid
    # -----------------------------------------------

    ys, xs = np.where(
        mask == 1
    )

    if len(xs) > 0:

        center_x = float(
            np.mean(xs)
        )

        center_y = float(
            np.mean(ys)
        )

        center_lon, center_lat = xy(
            transform,
            center_y,
            center_x
        )

    else:

        center_lat = None
        center_lon = None

    return {
        "spill_pixels": spill_pixels,
        "pixel_area_m2": pixel_area_m2,
        "area_km2": area_km2,
        "confidence": confidence,
        "centroid": {
            "latitude": center_lat,
            "longitude": center_lon
        },
        "crs": str(crs)
    }


# ============================================================
# SAVE MASK
# ============================================================

def save_mask(
    mask,
    profile
):

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
        MASK_PATH,
        "w",
        **output_profile
    ) as dst:

        dst.write(
            mask,
            1
        )

    print(
        f"✓ Mask saved: {MASK_PATH}"
    )


# ============================================================
# SAVE OVERLAY
# ============================================================

def save_overlay(
    image_path,
    mask
):

    with rasterio.open(
        image_path
    ) as src:

        image = src.read(1)

    image = normalize(
        image
    )

    plt.figure(
        figsize=(12, 7)
    )

    plt.imshow(
        image,
        cmap="gray"
    )

    overlay = np.ma.masked_where(
        mask == 0,
        mask
    )

    plt.imshow(
        overlay,
        alpha=0.45
    )

    plt.title(
        "OCEANNOVA AI Oil Spill Detection"
    )

    plt.axis("off")

    plt.tight_layout()

    plt.savefig(
        OVERLAY_PATH,
        dpi=180,
        bbox_inches="tight"
    )

    plt.close()

    print(
        f"✓ Overlay saved: {OVERLAY_PATH}"
    )


# ============================================================
# SAVE JSON
# ============================================================

def save_json(
    statistics
):

    result = {
        "incident_id": "SP-001",

        "source": {
            "type": "Sentinel-1 SAR",
            "file": IMAGE_PATH.name
        },

        "model": {
            "architecture": "Lightweight U-Net",
            "model_file": MODEL_PATH.name,
            "threshold": THRESHOLD
        },

        "detection": statistics,

        "status": "prototype_ai_detection"
    }

    with open(
        JSON_PATH,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            result,
            f,
            indent=2
        )

    print(
        f"✓ JSON saved: {JSON_PATH}"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    if not IMAGE_PATH.exists():

        raise FileNotFoundError(
            f"SAR image not found:\n"
            f"{IMAGE_PATH}"
        )

    if not MODEL_PATH.exists():

        raise FileNotFoundError(
            f"Model not found:\n"
            f"{MODEL_PATH}"
        )

    model = load_model()

    (
        mask,
        probability_map,
        profile,
        width,
        height,
        transform,
        crs
    ) = predict_scene(
        model
    )

    statistics = calculate_statistics(
        mask,
        probability_map,
        transform,
        crs
    )

    save_mask(
        mask,
        profile
    )

    np.save(
        PROBABILITY_PATH,
        probability_map
    )

    print(
        f"✓ Probability map saved: "
        f"{PROBABILITY_PATH}"
    )

    save_overlay(
        IMAGE_PATH,
        mask
    )

    save_json(
        statistics
    )

    print()
    print("=" * 60)
    print("DETECTION COMPLETE")
    print("=" * 60)

    print(
        f"Detected pixels : "
        f"{statistics['spill_pixels']:,}"
    )

    print(
        f"Detected area   : "
        f"{statistics['area_km2']:.4f} km²"
    )

    print(
        f"Confidence      : "
        f"{statistics['confidence']:.4f}"
    )

    print(
        "Centroid        : "
        f"{statistics['centroid']['latitude']}, "
        f"{statistics['centroid']['longitude']}"
    )

    print()
    print(
        "Output directory:"
    )

    print(
        OUTPUT_DIR
    )


if __name__ == "__main__":
    main()