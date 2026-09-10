"""OCEANNOVA - process every local Radar_data scene.

This script is intentionally local-first: the 23-scene Sentinel-1 archive is
large and should not be committed to GitHub. It scans data/external/Radar_data,
runs the existing U-Net on every image, applies the existing look-alike
filtering logic, computes scene geometry/metrics against the supplied mask,
and exports frontend-ready GeoJSON plus one aggregate manifest.

Run from the repository root:
    python scripts/process_all_radar_scenes.py

Optional:
    python scripts/process_all_radar_scenes.py --split test
    python scripts/process_all_radar_scenes.py --split all --limit 3

Outputs:
    data/processed/all_scenes/<scene_id>/
        probability.npy
        predicted_mask.tif
        filtered_mask.tif
        characterization.json
        spill.geojson
    data/processed/all_scenes/manifest.json

The script does NOT invent AIS attribution or ocean forcing. Those stages are
marked as pending unless real source data is supplied separately.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
from pathlib import Path

# Avoid PostgreSQL's bundled PROJ database overriding Rasterio/pyproj.
os.environ.pop("PROJ_DATA", None)
os.environ.pop("PROJ_LIB", None)

import numpy as np
import rasterio
from rasterio.features import shapes
from rasterio.warp import transform as warp_transform
from scipy import ndimage
from shapely.geometry import mapping, shape
from shapely.ops import transform as shapely_transform
from pyproj import Transformer

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = PROJECT_ROOT / "data" / "external" / "Radar_data"
OUTPUT_ROOT = PROJECT_ROOT / "data" / "processed" / "all_scenes"
MODEL_PATH = PROJECT_ROOT / "ai-model" / "models" / "oceannova_unet.pth"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def filter_prediction(image: np.ndarray, probability: np.ndarray) -> tuple[np.ndarray, dict]:
    """Apply the same prototype post-processing thresholds used by OCEANNOVA."""
    normalized = image.astype(np.float32)
    valid = np.isfinite(normalized)
    if np.any(valid):
        values = normalized[valid]
        low, high = np.percentile(values, 2), np.percentile(values, 98)
        if high > low:
            normalized = np.clip(normalized, low, high)
            normalized = (normalized - low) / (high - low)
        else:
            normalized = np.zeros_like(normalized)
    else:
        normalized = np.zeros_like(normalized)

    raw_mask = probability >= 0.80
    labels, number = ndimage.label(raw_mask, structure=np.ones((3, 3), dtype=np.uint8))
    component_sizes = np.bincount(labels.ravel())
    filtered = np.zeros_like(raw_mask, dtype=bool)

    kept = rejected_small = rejected_large = rejected_bright = rejected_shape = 0
    for component_id in range(1, number + 1):
        area = int(component_sizes[component_id])
        if area < 1000:
            rejected_small += 1
            continue
        if area > 600000:
            rejected_large += 1
            continue
        component = labels == component_id
        mean_intensity = float(np.mean(normalized[component]))
        if mean_intensity > 0.15:
            rejected_bright += 1
            continue
        eroded = ndimage.binary_erosion(component, structure=np.ones((3, 3), dtype=bool))
        perimeter = int(np.count_nonzero(component & ~eroded))
        compactness = (4.0 * np.pi * area / (perimeter ** 2)) if perimeter else 0.0
        if compactness < 0.005:
            rejected_shape += 1
            continue
        filtered[component] = True
        kept += 1

    return filtered, {
        "raw_pixels": int(raw_mask.sum()),
        "filtered_pixels": int(filtered.sum()),
        "components": int(number),
        "kept_components": kept,
        "rejected_small": rejected_small,
        "rejected_large": rejected_large,
        "rejected_bright": rejected_bright,
        "rejected_shape": rejected_shape,
        "threshold": 0.80,
        "intensity_threshold": 0.15,
        "min_component_pixels": 1000,
        "max_component_pixels": 600000,
        "min_compactness": 0.005,
    }


def metrics(predicted: np.ndarray, truth: np.ndarray) -> dict:
    pred = predicted.astype(bool)
    gt = truth.astype(bool)
    intersection = int(np.logical_and(pred, gt).sum())
    union = int(np.logical_or(pred, gt).sum())
    p = int(pred.sum())
    g = int(gt.sum())
    return {
        "iou": round(intersection / union, 6) if union else 0.0,
        "dice": round((2 * intersection) / (p + g), 6) if (p + g) else 0.0,
        "precision": round(intersection / p, 6) if p else 0.0,
        "recall": round(intersection / g, 6) if g else 0.0,
        "predicted_pixels": p,
        "ground_truth_pixels": g,
        "intersection_pixels": intersection,
    }


def characterization(mask: np.ndarray, probability: np.ndarray, transform, crs) -> dict:
    spill_pixels = int(mask.sum())
    pixel_width = abs(float(transform.a))
    pixel_height = abs(float(transform.e))
    pixel_area_m2 = pixel_width * pixel_height
    area_km2 = spill_pixels * pixel_area_m2 / 1_000_000.0

    eroded = ndimage.binary_erosion(mask, structure=np.ones((3, 3), dtype=bool))
    perimeter_pixels = int(np.count_nonzero(mask & ~eroded))
    perimeter_km = perimeter_pixels * ((pixel_width + pixel_height) / 2.0) / 1000.0
    compactness = 4.0 * np.pi * area_km2 / (perimeter_km ** 2) if perimeter_km else 0.0

    rows, cols = np.where(mask)
    if len(rows):
        row, col = float(np.mean(rows)), float(np.mean(cols))
        x, y = rasterio.transform.xy(transform, row, col)
        lon, lat = warp_transform(crs, "EPSG:4326", [x], [y])
        centroid = {"latitude": float(lat[0]), "longitude": float(lon[0])}
    else:
        centroid = {"latitude": None, "longitude": None}

    selected = probability[mask]
    confidence = float(np.mean(selected)) if len(selected) else 0.0
    max_confidence = float(np.max(selected)) if len(selected) else 0.0
    labels, count = ndimage.label(mask, structure=np.ones((3, 3), dtype=np.uint8))
    sizes = np.bincount(labels.ravel())[1:]

    return {
        "spill_pixels": spill_pixels,
        "area_km2": round(area_km2, 4),
        "perimeter_km": round(perimeter_km, 4),
        "compactness": round(compactness, 6),
        "mean_ai_confidence": round(confidence, 6),
        "max_ai_confidence": round(max_confidence, 6),
        "components": int(count),
        "largest_component_pixels": int(sizes.max()) if len(sizes) else 0,
        "centroid": centroid,
        "crs": str(crs),
    }


def write_geojson(mask_path: Path, output_path: Path, incident_id: str) -> None:
    with rasterio.open(mask_path) as src:
        mask = src.read(1) > 0
        source_crs = src.crs
        transform = src.transform
        raw_shapes = shapes(mask.astype("uint8"), mask=mask, transform=transform)

    transformer = Transformer.from_crs(source_crs, "EPSG:4326", always_xy=True)
    features = []
    for geometry, value in raw_shapes:
        if value != 1:
            continue
        polygon = shape(geometry).buffer(0)
        if polygon.is_empty:
            continue
        polygon = shapely_transform(transformer.transform, polygon)
        if polygon.is_empty:
            continue
        features.append({
            "type": "Feature",
            "geometry": mapping(polygon),
            "properties": {
                "incident_id": incident_id,
                "type": "AI-detected-slick",
                "source": "Sentinel-1 SAR",
                "method": "U-Net segmentation + radiometric filtering",
            },
        })

    output_path.write_text(json.dumps({
        "type": "FeatureCollection",
        "name": f"{incident_id}_AI_Spill_Footprint",
        "features": features,
    }, indent=2), encoding="utf-8")


def discover_scenes(split: str) -> list[tuple[str, Path, Path, str]]:
    splits = [split] if split in {"train", "test"} else ["train", "test"]
    scenes = []
    for current_split in splits:
        image_dir = DATA_ROOT / current_split / "images"
        mask_dir = DATA_ROOT / current_split / "masks"
        if not image_dir.exists():
            continue
        for image_path in sorted(image_dir.glob("*.tif")):
            mask_path = mask_dir / image_path.name
            if not mask_path.exists():
                print(f"[WARN] Missing mask for {image_path.name}; skipping")
                continue
            scene_id = image_path.stem
            incident_id = "SP-" + str(len(scenes) + 1).zfill(3)
            scenes.append((scene_id, image_path, mask_path, current_split))
    return scenes


def process_scene(scene_id: str, incident_id: str, image_path: Path, mask_path: Path, split: str, model_module, model) -> dict:
    output_dir = OUTPUT_ROOT / incident_id
    output_dir.mkdir(parents=True, exist_ok=True)

    model_module.IMAGE_PATH = image_path
    with rasterio.open(image_path) as src:
        image = src.read(1)
        profile = src.profile.copy()
        transform = src.transform
        crs = src.crs

    model_module.OUTPUT_DIR = output_dir
    model_module.MASK_PATH = output_dir / "predicted_mask.tif"
    model_module.PROBABILITY_PATH = output_dir / "probability.npy"
    model_module.OVERLAY_PATH = output_dir / "prediction_overlay.png"
    model_module.JSON_PATH = output_dir / "prediction.json"

    predicted, probability, profile, width, height, transform, crs = model_module.predict_scene(model)
    model_module.save_mask(predicted, profile)
    np.save(model_module.PROBABILITY_PATH, probability)

    filtered, filter_info = filter_prediction(image, probability)
    filtered_mask_path = output_dir / "filtered_mask.tif"
    filtered_profile = profile.copy()
    filtered_profile.update(driver="GTiff", dtype="uint8", count=1, compress="lzw", nodata=0)
    with rasterio.open(filtered_mask_path, "w", **filtered_profile) as dst:
        dst.write(filtered.astype(np.uint8), 1)

    with rasterio.open(mask_path) as gt_src:
        ground_truth = gt_src.read(1) > 0

    characterization_result = characterization(filtered, probability, transform, crs)
    eval_metrics = metrics(filtered, ground_truth)
    write_geojson(filtered_mask_path, output_dir / "spill.geojson", incident_id)

    result = {
        "incident_id": incident_id,
        "scene_id": scene_id,
        "split": split,
        "source": {
            "type": "Sentinel-1 SAR",
            "image": str(image_path.relative_to(PROJECT_ROOT)),
            "ground_truth": str(mask_path.relative_to(PROJECT_ROOT)),
            "crs": str(crs),
        },
        "detection": {
            "method": "Lightweight U-Net + prototype radiometric/look-alike filtering",
            **characterization_result,
        },
        "validation": {
            "ground_truth_available": True,
            **eval_metrics,
            "metric_note": "Reference-mask evaluation; train split metrics are in-sample and must not be reported as held-out performance.",
        },
        "investigation": {
            "drift": {"status": "PENDING_REAL_HYCOM_FORCING"},
            "ais": {"status": "PENDING_REAL_AIS_DATA"},
            "attribution": {"status": "NOT_COMPUTED_WITHOUT_REAL_AIS"},
        },
        "postprocessing": filter_info,
    }
    (output_dir / "characterization.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Process all local OCEANNOVA Sentinel-1 scenes")
    parser.add_argument("--split", choices=["all", "train", "test"], default="all")
    parser.add_argument("--limit", type=int, default=0, help="Process only the first N scenes (0 = all)")
    args = parser.parse_args()

    if not DATA_ROOT.exists():
        raise FileNotFoundError(f"Dataset not found: {DATA_ROOT}")
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"U-Net checkpoint not found: {MODEL_PATH}")

    scenes = discover_scenes(args.split)
    if args.limit > 0:
        scenes = scenes[:args.limit]
    if not scenes:
        raise RuntimeError(f"No image/mask pairs found under {DATA_ROOT}")

    predict_module = load_module(PROJECT_ROOT / "ai-model" / "inference" / "predict_unet.py", "oceannova_predict")
    model = predict_module.load_model()

    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    manifest = {
        "project": "OCEANNOVA",
        "dataset_root": str(DATA_ROOT.relative_to(PROJECT_ROOT)),
        "scene_count": len(scenes),
        "pipeline": [
            "scene discovery",
            "Sentinel-1 normalization",
            "U-Net segmentation",
            "confidence/component/radiometric/shape filtering",
            "geometry characterization",
            "ground-truth validation",
            "GeoJSON export",
            "drift and AIS stages explicitly pending real source data",
        ],
        "scenes": [],
    }

    for index, (scene_id, image_path, mask_path, split) in enumerate(scenes, start=1):
        incident_id = "SP-" + str(index).zfill(3)
        print(f"\n[{index}/{len(scenes)}] {incident_id} | {split} | {image_path.name}")
        try:
            result = process_scene(scene_id, incident_id, image_path, mask_path, split, predict_module, model)
            manifest["scenes"].append(result)
            print(f"  area={result['detection']['area_km2']} km² | IoU={result['validation']['iou']:.4f} | Dice={result['validation']['dice']:.4f}")
        except Exception as exc:
            print(f"[ERROR] {scene_id}: {exc}")
            manifest["scenes"].append({
                "incident_id": incident_id,
                "scene_id": scene_id,
                "split": split,
                "status": "ERROR",
                "error": str(exc),
            })

    (OUTPUT_ROOT / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    ok = sum(1 for scene in manifest["scenes"] if scene.get("status") != "ERROR")
    print(f"\nDONE: {ok}/{len(scenes)} scenes processed")
    print(f"Manifest: {OUTPUT_ROOT / 'manifest.json'}")
    return 0 if ok == len(scenes) else 1


if __name__ == "__main__":
    sys.exit(main())
