"""
OCEANNOVA - Lightweight U-Net Oil Spill Segmentation Trainer

Input:
    D:/OCEANNOVA/data/external/Radar_data/

Expected structure:
    train/images/*.tif
    train/masks/*.tif
    test/images/*.tif
    test/masks/*.tif

The model is trained on Sentinel-1 SAR imagery and corresponding
oil-spill segmentation masks.
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
# CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_ROOT = PROJECT_ROOT / "data" / "external" / "Radar_data"

TRAIN_IMAGE_DIR = DATA_ROOT / "train" / "images"
TRAIN_MASK_DIR = DATA_ROOT / "train" / "masks"

TEST_IMAGE_DIR = DATA_ROOT / "test" / "images"
TEST_MASK_DIR = DATA_ROOT / "test" / "masks"

MODEL_DIR = PROJECT_ROOT / "ai-model" / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

MODEL_PATH = MODEL_DIR / "oceannova_unet.pth"

IMAGE_SIZE = 256
BATCH_SIZE = 4
EPOCHS = 15
LEARNING_RATE = 1e-3

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
# DATASET
# ============================================================

class OilSpillDataset(Dataset):
    """
    Loads Sentinel-1 SAR images and oil-spill masks.

    Large satellite scenes are divided into 256x256 patches.
    """

    def __init__(self, image_dir, mask_dir, augment=False):

        self.image_dir = Path(image_dir)
        self.mask_dir = Path(mask_dir)
        self.augment = augment

        self.samples = []

        image_files = sorted(self.image_dir.glob("*.tif"))

        if not image_files:
            raise FileNotFoundError(
                f"No .tif images found in {self.image_dir}"
            )

        for image_path in image_files:

            mask_path = self.mask_dir / image_path.name

            if not mask_path.exists():
                print(
                    f"Warning: mask missing for {image_path.name}"
                )
                continue

            with rasterio.open(image_path) as src:
                height = src.height
                width = src.width

            # Generate non-overlapping patches.
            for y in range(0, height - IMAGE_SIZE + 1, IMAGE_SIZE):
                for x in range(
                    0,
                    width - IMAGE_SIZE + 1,
                    IMAGE_SIZE
                ):
                    self.samples.append(
                        (
                            image_path,
                            mask_path,
                            x,
                            y
                        )
                    )

        if not self.samples:
            raise RuntimeError(
                "No valid image/mask patches were generated."
            )

        print(
            f"Loaded {len(self.samples)} training patches "
            f"from {len(image_files)} scenes."
        )

    def __len__(self):
        return len(self.samples)

    @staticmethod
    def normalize(image):

        image = image.astype(np.float32)

        valid = np.isfinite(image)

        if not np.any(valid):
            return np.zeros_like(image, dtype=np.float32)

        values = image[valid]

        low = np.percentile(values, 2)
        high = np.percentile(values, 98)

        if high <= low:
            return np.zeros_like(image, dtype=np.float32)

        image = np.clip(image, low, high)

        image = (image - low) / (high - low)

        return image.astype(np.float32)

    def __getitem__(self, index):

        image_path, mask_path, x, y = self.samples[index]

        with rasterio.open(image_path) as src:
            image = src.read(
                1,
                window=rasterio.windows.Window(
                    x,
                    y,
                    IMAGE_SIZE,
                    IMAGE_SIZE
                )
            )

        with rasterio.open(mask_path) as src:
            mask = src.read(
                1,
                window=rasterio.windows.Window(
                    x,
                    y,
                    IMAGE_SIZE,
                    IMAGE_SIZE
                )
            )

        image = self.normalize(image)

        # Convert mask to binary.
        mask = (mask > 0).astype(np.float32)

        # Simple augmentation.
        if self.augment:

            if random.random() > 0.5:
                image = np.fliplr(image).copy()
                mask = np.fliplr(mask).copy()

            if random.random() > 0.5:
                image = np.flipud(image).copy()
                mask = np.flipud(mask).copy()

        image = torch.from_numpy(
            image
        ).float().unsqueeze(0)

        mask = torch.from_numpy(
            mask
        ).float().unsqueeze(0)

        return image, mask


# ============================================================
# U-NET
# ============================================================

class DoubleConv(nn.Module):

    def __init__(self, in_channels, out_channels):

        super().__init__()

        self.block = nn.Sequential(

            nn.Conv2d(
                in_channels,
                out_channels,
                kernel_size=3,
                padding=1
            ),

            nn.BatchNorm2d(out_channels),

            nn.ReLU(inplace=True),

            nn.Conv2d(
                out_channels,
                out_channels,
                kernel_size=3,
                padding=1
            ),

            nn.BatchNorm2d(out_channels),

            nn.ReLU(inplace=True)
        )

    def forward(self, x):
        return self.block(x)


class UNet(nn.Module):

    def __init__(self):

        super().__init__()

        self.enc1 = DoubleConv(1, 32)
        self.enc2 = DoubleConv(32, 64)
        self.enc3 = DoubleConv(64, 128)

        self.pool = nn.MaxPool2d(2)

        self.bottleneck = DoubleConv(128, 256)

        self.up3 = nn.ConvTranspose2d(
            256,
            128,
            kernel_size=2,
            stride=2
        )

        self.dec3 = DoubleConv(256, 128)

        self.up2 = nn.ConvTranspose2d(
            128,
            64,
            kernel_size=2,
            stride=2
        )

        self.dec2 = DoubleConv(128, 64)

        self.up1 = nn.ConvTranspose2d(
            64,
            32,
            kernel_size=2,
            stride=2
        )

        self.dec1 = DoubleConv(64, 32)

        self.output = nn.Conv2d(
            32,
            1,
            kernel_size=1
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

    def forward(self, logits, targets):

        probabilities = torch.sigmoid(logits)

        probabilities = probabilities.reshape(-1)
        targets = targets.reshape(-1)

        intersection = (
            probabilities * targets
        ).sum()

        dice = (
            2.0 * intersection + 1.0
        ) / (
            probabilities.sum()
            + targets.sum()
            + 1.0
        )

        return 1.0 - dice


# ============================================================
# METRICS
# ============================================================

def calculate_metrics(logits, targets):

    probabilities = torch.sigmoid(logits)

    predictions = (
        probabilities > 0.5
    ).float()

    predictions = predictions.reshape(-1)
    targets = targets.reshape(-1)

    intersection = (
        predictions * targets
    ).sum()

    union = (
        predictions
        + targets
        - predictions * targets
    ).sum()

    iou = (
        (intersection + 1e-7)
        / (union + 1e-7)
    )

    dice = (
        (2 * intersection + 1e-7)
        / (
            predictions.sum()
            + targets.sum()
            + 1e-7
        )
    )

    return iou.item(), dice.item()


# ============================================================
# TRAINING
# ============================================================

def train():

    print("=" * 60)
    print("OCEANNOVA AI — Oil Spill Segmentation")
    print("=" * 60)

    print(f"Device: {DEVICE}")
    print(f"Dataset: {DATA_ROOT}")
    print(f"Epochs: {EPOCHS}")
    print(f"Batch size: {BATCH_SIZE}")
    print()

    train_dataset = OilSpillDataset(
        TRAIN_IMAGE_DIR,
        TRAIN_MASK_DIR,
        augment=True
    )

    test_dataset = OilSpillDataset(
        TEST_IMAGE_DIR,
        TEST_MASK_DIR,
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

    model = UNet().to(DEVICE)

    bce_loss = nn.BCEWithLogitsLoss()
    dice_loss = DiceLoss()

    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=LEARNING_RATE
    )

    best_iou = 0.0

    for epoch in range(EPOCHS):

        # -------------------------------
        # TRAIN
        # -------------------------------

        model.train()

        running_loss = 0.0

        progress = tqdm(
            train_loader,
            desc=f"Epoch {epoch + 1}/{EPOCHS}"
        )

        for images, masks in progress:

            images = images.to(DEVICE)
            masks = masks.to(DEVICE)

            optimizer.zero_grad()

            logits = model(images)

            loss = (
                0.5 * bce_loss(logits, masks)
                + 0.5 * dice_loss(logits, masks)
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

        # -------------------------------
        # VALIDATION / TEST
        # -------------------------------

        model.eval()

        total_iou = 0.0
        total_dice = 0.0

        with torch.no_grad():

            for images, masks in test_loader:

                images = images.to(DEVICE)
                masks = masks.to(DEVICE)

                logits = model(images)

                iou, dice = calculate_metrics(
                    logits,
                    masks
                )

                total_iou += iou
                total_dice += dice

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
            f"Epoch {epoch + 1}/{EPOCHS} | "
            f"Loss: {train_loss:.4f} | "
            f"IoU: {mean_iou:.4f} | "
            f"Dice: {mean_dice:.4f}"
        )

        # Save best model.
        if mean_iou > best_iou:

            best_iou = mean_iou

            torch.save(
                {
                    "model_state_dict": model.state_dict(),
                    "iou": mean_iou,
                    "dice": mean_dice,
                    "epoch": epoch + 1,
                },
                MODEL_PATH
            )

            print(
                f"✓ Best model saved → {MODEL_PATH}"
            )

    print()
    print("=" * 60)
    print("TRAINING COMPLETE")
    print("=" * 60)

    print(f"Best IoU : {best_iou:.4f}")
    print(f"Model    : {MODEL_PATH}")


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    train()