"""
OCEANNOVA - Fast Oil Spill Segmentation Trainer

SIH prototype training configuration:
- Real Sentinel-1 SAR GeoTIFFs
- Real segmentation masks
- Positive-patch sampling
- Lightweight U-Net
- GPU training
- BCE + Dice loss
- IoU + Dice evaluation
"""

from pathlib import Path
import random

import numpy as np
import rasterio
from tqdm import tqdm

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader


# ============================================================
# CONFIG
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_ROOT = (
    PROJECT_ROOT
    / "data"
    / "external"
    / "Radar_data"
)

TRAIN_IMAGES = DATA_ROOT / "train" / "images"
TRAIN_MASKS = DATA_ROOT / "train" / "masks"

TEST_IMAGES = DATA_ROOT / "test" / "images"
TEST_MASKS = DATA_ROOT / "test" / "masks"

MODEL_DIR = PROJECT_ROOT / "ai-model" / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

MODEL_PATH = MODEL_DIR / "oceannova_unet.pth"


# Fast configuration for RTX 2050 4 GB
IMAGE_SIZE = 256
BATCH_SIZE = 4
EPOCHS = 8
LEARNING_RATE = 1e-3

MAX_TRAIN_PATCHES = 300
MAX_TEST_PATCHES = 200

POSITIVE_RATIO = 0.75

MIN_OIL_PIXELS = 100

SEED = 42

DEVICE = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)


# ============================================================
# REPRODUCIBILITY
# ============================================================

random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)

if torch.cuda.is_available():
    torch.cuda.manual_seed_all(SEED)


# ============================================================
# PATCH DATASET
# ============================================================

class OilSpillDataset(Dataset):

    def __init__(
        self,
        image_dir,
        mask_dir,
        max_patches,
        positive_ratio=0.75,
        augment=False,
    ):

        self.image_dir = Path(image_dir)
        self.mask_dir = Path(mask_dir)
        self.augment = augment

        all_positive = []
        all_negative = []

        image_files = sorted(
            self.image_dir.glob("*.tif")
        )

        if not image_files:
            raise FileNotFoundError(
                f"No TIFF files found in {self.image_dir}"
            )

        print(
            f"Scanning {len(image_files)} scenes..."
        )

        # ----------------------------------------------------
        # Find useful patches
        # ----------------------------------------------------

        for image_path in tqdm(
            image_files,
            desc="Scanning scenes"
        ):

            mask_path = (
                self.mask_dir
                / image_path.name
            )

            if not mask_path.exists():
                print(
                    f"Warning: missing mask: "
                    f"{image_path.name}"
                )
                continue

            with rasterio.open(mask_path) as src:

                height = src.height
                width = src.width

                for y in range(
                    0,
                    height - IMAGE_SIZE + 1,
                    IMAGE_SIZE
                ):

                    for x in range(
                        0,
                        width - IMAGE_SIZE + 1,
                        IMAGE_SIZE
                    ):

                        window = rasterio.windows.Window(
                            x,
                            y,
                            IMAGE_SIZE,
                            IMAGE_SIZE
                        )

                        mask = src.read(
                            1,
                            window=window
                        )

                        oil_pixels = np.count_nonzero(
                            mask > 0
                        )

                        sample = (
                            image_path,
                            mask_path,
                            x,
                            y
                        )

                        if oil_pixels >= MIN_OIL_PIXELS:
                            all_positive.append(sample)
                        else:
                            all_negative.append(sample)

        print(
            f"Positive patches found: "
            f"{len(all_positive)}"
        )

        print(
            f"Negative patches found: "
            f"{len(all_negative)}"
        )

        # ----------------------------------------------------
        # Select balanced/useful subset
        # ----------------------------------------------------

        random.shuffle(all_positive)
        random.shuffle(all_negative)

        positive_count = int(
            max_patches * positive_ratio
        )

        negative_count = (
            max_patches - positive_count
        )

        selected_positive = (
            all_positive[:positive_count]
        )

        selected_negative = (
            all_negative[:negative_count]
        )

        self.samples = (
            selected_positive
            + selected_negative
        )

        random.shuffle(self.samples)

        print(
            f"Using {len(self.samples)} patches "
            f"for this dataset."
        )

    def __len__(self):
        return len(self.samples)

    @staticmethod
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

    def __getitem__(self, index):

        image_path, mask_path, x, y = (
            self.samples[index]
        )

        window = rasterio.windows.Window(
            x,
            y,
            IMAGE_SIZE,
            IMAGE_SIZE
        )

        with rasterio.open(image_path) as src:
            image = src.read(
                1,
                window=window
            )

        with rasterio.open(mask_path) as src:
            mask = src.read(
                1,
                window=window
            )

        image = self.normalize(image)

        mask = (
            mask > 0
        ).astype(np.float32)

        # -------------------------------
        # Augmentation
        # -------------------------------

        if self.augment:

            if random.random() > 0.5:

                image = np.fliplr(
                    image
                ).copy()

                mask = np.fliplr(
                    mask
                ).copy()

            if random.random() > 0.5:

                image = np.flipud(
                    image
                ).copy()

                mask = np.flipud(
                    mask
                ).copy()

            if random.random() > 0.5:

                image = np.rot90(
                    image
                ).copy()

                mask = np.rot90(
                    mask
                ).copy()

        image = torch.from_numpy(
            image
        ).float().unsqueeze(0)

        mask = torch.from_numpy(
            mask
        ).float().unsqueeze(0)

        return image, mask


# ============================================================
# LIGHTWEIGHT U-NET
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

        # Encoder
        self.enc1 = DoubleConv(1, 16)
        self.enc2 = DoubleConv(16, 32)
        self.enc3 = DoubleConv(32, 64)

        self.pool = nn.MaxPool2d(2)

        # Bottleneck
        self.bottleneck = DoubleConv(
            64,
            128
        )

        # Decoder
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
# DICE LOSS
# ============================================================

class DiceLoss(nn.Module):

    def forward(
        self,
        logits,
        targets
    ):

        probabilities = torch.sigmoid(
            logits
        )

        probabilities = probabilities.reshape(
            -1
        )

        targets = targets.reshape(
            -1
        )

        intersection = (
            probabilities * targets
        ).sum()

        dice = (
            2 * intersection + 1
        ) / (
            probabilities.sum()
            + targets.sum()
            + 1
        )

        return 1 - dice


# ============================================================
# METRICS
# ============================================================

def calculate_metrics(
    logits,
    targets
):

    probabilities = torch.sigmoid(
        logits
    )

    predictions = (
        probabilities > 0.5
    ).float()

    predictions = predictions.reshape(
        -1
    )

    targets = targets.reshape(
        -1
    )

    intersection = (
        predictions * targets
    ).sum()

    union = (
        predictions
        + targets
        - predictions * targets
    ).sum()

    iou = (
        intersection + 1e-7
    ) / (
        union + 1e-7
    )

    dice = (
        2 * intersection + 1e-7
    ) / (
        predictions.sum()
        + targets.sum()
        + 1e-7
    )

    return (
        iou.item(),
        dice.item()
    )


# ============================================================
# TRAIN
# ============================================================

def train():

    print("=" * 60)
    print(
        "OCEANNOVA AI - FAST SEGMENTATION TRAINING"
    )
    print("=" * 60)

    print(f"Device       : {DEVICE}")
    print(f"Image size   : {IMAGE_SIZE}")
    print(f"Batch size   : {BATCH_SIZE}")
    print(f"Epochs       : {EPOCHS}")
    print(f"Train limit  : {MAX_TRAIN_PATCHES}")
    print(f"Test limit   : {MAX_TEST_PATCHES}")
    print()

    # --------------------------------------------------------
    # Dataset
    # --------------------------------------------------------

    train_dataset = OilSpillDataset(
        TRAIN_IMAGES,
        TRAIN_MASKS,
        MAX_TRAIN_PATCHES,
        positive_ratio=POSITIVE_RATIO,
        augment=True
    )

    test_dataset = OilSpillDataset(
        TEST_IMAGES,
        TEST_MASKS,
        MAX_TEST_PATCHES,
        positive_ratio=0.70,
        augment=False
    )

    train_loader = DataLoader(
        train_dataset,
        batch_size=BATCH_SIZE,
        shuffle=True,
        num_workers=0,
        pin_memory=torch.cuda.is_available()
    )

    test_loader = DataLoader(
        test_dataset,
        batch_size=BATCH_SIZE,
        shuffle=False,
        num_workers=0,
        pin_memory=torch.cuda.is_available()
    )

    # --------------------------------------------------------
    # Model
    # --------------------------------------------------------

    model = UNet().to(DEVICE)

    bce = nn.BCEWithLogitsLoss()

    dice = DiceLoss()

    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=LEARNING_RATE
    )

    best_iou = -1

    # --------------------------------------------------------
    # Training loop
    # --------------------------------------------------------

    for epoch in range(EPOCHS):

        model.train()

        running_loss = 0.0

        progress = tqdm(
            train_loader,
            desc=(
                f"Epoch "
                f"{epoch + 1}/{EPOCHS}"
            )
        )

        for images, masks in progress:

            images = images.to(
                DEVICE,
                non_blocking=True
            )

            masks = masks.to(
                DEVICE,
                non_blocking=True
            )

            optimizer.zero_grad(
                set_to_none=True
            )

            logits = model(images)

            loss = (
                0.5 * bce(
                    logits,
                    masks
                )
                +
                0.5 * dice(
                    logits,
                    masks
                )
            )

            loss.backward()

            optimizer.step()

            running_loss += loss.item()

            progress.set_postfix(
                loss=f"{loss.item():.4f}"
            )

        train_loss = (
            running_loss
            / len(train_loader)
        )

        # ----------------------------------------------------
        # Evaluation
        # ----------------------------------------------------

        model.eval()

        total_iou = 0.0
        total_dice = 0.0

        with torch.no_grad():

            for images, masks in test_loader:

                images = images.to(
                    DEVICE,
                    non_blocking=True
                )

                masks = masks.to(
                    DEVICE,
                    non_blocking=True
                )

                logits = model(images)

                iou, dice_score = (
                    calculate_metrics(
                        logits,
                        masks
                    )
                )

                total_iou += iou
                total_dice += dice_score

        mean_iou = (
            total_iou
            / len(test_loader)
        )

        mean_dice = (
            total_dice
            / len(test_loader)
        )

        print()
        print(
            f"Epoch {epoch + 1}/{EPOCHS}"
        )

        print(
            f"Loss : {train_loss:.4f}"
        )

        print(
            f"IoU  : {mean_iou:.4f}"
        )

        print(
            f"Dice : {mean_dice:.4f}"
        )

        # ----------------------------------------------------
        # Save best model
        # ----------------------------------------------------

        if mean_iou > best_iou:

            best_iou = mean_iou

            torch.save(
                {
                    "model_state_dict":
                        model.state_dict(),

                    "iou":
                        mean_iou,

                    "dice":
                        mean_dice,

                    "epoch":
                        epoch + 1,

                    "image_size":
                        IMAGE_SIZE,
                },
                MODEL_PATH
            )

            print(
                f"✓ Best model saved"
            )

    print()
    print("=" * 60)
    print("TRAINING COMPLETE")
    print("=" * 60)

    print(
        f"Best IoU : {best_iou:.4f}"
    )

    print(
        f"Model    : {MODEL_PATH}"
    )


if __name__ == "__main__":
    train()