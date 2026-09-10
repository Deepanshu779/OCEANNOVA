from pathlib import Path

from fastapi import APIRouter

router = APIRouter(prefix="/datasets", tags=["datasets"])

PROJECT_ROOT = Path(__file__).resolve().parents[4]
DATA_ROOT = PROJECT_ROOT / "data" / "external" / "Radar_data"


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
    return scenes


@router.get("")
def list_datasets():
    scenes = discover_scenes()
    return {
        "source": "Zenodo Oil Spill Segmentation / Radar_data",
        "total": len(scenes),
        "scenes": scenes,
    }
