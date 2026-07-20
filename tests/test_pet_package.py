from __future__ import annotations

import json
from pathlib import Path

from PIL import Image

from scripts.build_assets import ACTIONS, ATLAS_SIZE, CELL_HEIGHT, CELL_WIDTH
from scripts.validate_pet import validate_pet


ROOT = Path(__file__).resolve().parents[1]


def test_package_is_valid() -> None:
    result = validate_pet(ROOT)
    assert result["ok"], result["errors"]


def test_metadata_uses_stable_identity() -> None:
    metadata = json.loads((ROOT / "pet" / "pet.json").read_text(encoding="utf-8"))
    assert metadata["id"] == "feibi-jiubi"
    assert metadata["displayName"] == "菲比啾比"
    assert metadata["spriteVersionNumber"] == 2


def test_atlas_geometry_and_unused_cells() -> None:
    with Image.open(ROOT / "pet" / "spritesheet.webp") as image:
        assert image.size == ATLAS_SIZE
        alpha = image.convert("RGBA").getchannel("A")
        for row, action in enumerate(ACTIONS):
            assert len(action.frames) == len(action.durations)
            for column in range(len(action.frames), 8):
                box = (
                    column * CELL_WIDTH,
                    row * CELL_HEIGHT,
                    (column + 1) * CELL_WIDTH,
                    (row + 1) * CELL_HEIGHT,
                )
                assert alpha.crop(box).getbbox() is None


def test_action_previews_are_animated() -> None:
    for action in ACTIONS:
        path = ROOT / "media" / "actions" / f"{action.name}.gif"
        with Image.open(path) as image:
            assert image.is_animated
            assert image.n_frames == len(action.frames)
