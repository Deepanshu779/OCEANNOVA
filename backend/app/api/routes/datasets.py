import json
from pathlib import Path

from fastapi import APIRouter

router = APIRouter(prefix="/datasets", tags=["datasets"])

PROJECT_ROOT = Path(__file__).resolve().parents[4]
DATA_ROOT = PROJECT_ROOT / "data" / "external" / "Radar_data"
PROCESSED_ROOT = PROJECT_ROOT / "data" / "processed" / "all_scenes"
MANIFEST_PATH = PROCESSED_ROOT / "manifest.json"


def discover_scenes() -> list[dict]:
    scenes: list[dict] = []
    for split in ("test", "train"):
        image_dir = DATA_ROOT / split / "images"
        mask_dir = DATA_ROOT / split / "masks"
        if not image_dir.exists():
            continue
        for image_path in sorted(image_dir.glob("*.tif")):
            mask_path = mask_dir / image_path.name
            scenes.append({
                "scene_id": image_path.stem,
                "file": image_path.name,
                "split": split,
                "has_image": True,
                "has_mask": mask_path.exists(),
                "image_path": str(image_path.relative_to(PROJECT_ROOT)).replace("\\", "/"),
            })
    if scenes:
        return scenes

    if MANIFEST_PATH.exists():
        try:
            manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
            return [
                {
                    "scene_id": item["scene_id"],
                    "file": Path(item["source"]["image"]).name,
                    "split": item["split"],
                    "has_image": True,
                    "has_mask": bool(item["source"].get("ground_truth")),
                    "image_path": item["source"]["image"].replace("\\", "/"),
                }
                for item in manifest.get("scenes", [])
            ]
        except (OSError, json.JSONDecodeError, KeyError, TypeError):
            return []

    return []


@router.get("")
def list_datasets():
    scenes = discover_scenes()
    return {
        "source": "OCEANNOVA processed Radar_data",
        "total": len(scenes),
        "scenes": scenes,
    }
