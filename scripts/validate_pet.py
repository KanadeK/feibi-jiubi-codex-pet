from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
PET_JSON = ROOT / "pet" / "pet.json"
SPRITESHEET = ROOT / "pet" / "spritesheet.webp"
CELL_WIDTH = 192
CELL_HEIGHT = 208
ATLAS_SIZE = (1536, 1872)
MAX_FILE_SIZE = 20 * 1024 * 1024
USED_FRAMES = (6, 8, 8, 4, 5, 8, 6, 6, 6)


def validate_pet(root: Path = ROOT) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    pet_json = root / "pet" / "pet.json"
    spritesheet = root / "pet" / "spritesheet.webp"

    if not pet_json.exists():
        return {"ok": False, "errors": ["pet/pet.json is missing"], "warnings": []}
    if not spritesheet.exists():
        return {"ok": False, "errors": ["pet/spritesheet.webp is missing"], "warnings": []}

    try:
        metadata = json.loads(pet_json.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"ok": False, "errors": [f"pet.json is invalid: {exc}"], "warnings": []}

    required = {"id", "displayName", "description", "spritesheetPath"}
    allowed = required | {"spriteVersionNumber"}
    missing = required - set(metadata)
    extra = set(metadata) - allowed
    if missing:
        errors.append(f"pet.json is missing keys: {sorted(missing)}")
    if extra:
        errors.append(f"pet.json has unsupported keys: {sorted(extra)}")
    if metadata.get("id") != "feibi-jiubi":
        errors.append("pet.json id must be feibi-jiubi")
    if metadata.get("displayName") != "菲比啾比":
        errors.append("pet.json displayName must be 菲比啾比")
    if metadata.get("spritesheetPath") != "spritesheet.webp":
        errors.append("pet.json spritesheetPath must be spritesheet.webp")
    if metadata.get("spriteVersionNumber", 1) not in (1, 2):
        errors.append("spriteVersionNumber must be 1 or 2")

    if spritesheet.stat().st_size > MAX_FILE_SIZE:
        errors.append("spritesheet.webp exceeds the official 20 MiB upload limit")

    with Image.open(spritesheet) as atlas:
        if atlas.size != ATLAS_SIZE:
            errors.append(f"spritesheet size is {atlas.size}, expected {ATLAS_SIZE}")
        if atlas.format != "WEBP":
            errors.append(f"spritesheet format is {atlas.format}, expected WEBP")
        rgba = atlas.convert("RGBA")
        alpha = rgba.getchannel("A")
        alpha_extrema = alpha.getextrema()
        if alpha_extrema[0] != 0:
            errors.append("spritesheet has no fully transparent pixels")
        if alpha_extrema[1] != 255:
            warnings.append("spritesheet has no fully opaque pixels")

        hidden_rgb = sum(
            1
            for red, green, blue, pixel_alpha in rgba.get_flattened_data()
            if pixel_alpha == 0 and (red or green or blue)
        )
        if hidden_rgb:
            errors.append(
                f"spritesheet has {hidden_rgb} fully transparent pixels with hidden RGB data"
            )

        for row, used_count in enumerate(USED_FRAMES):
            for column in range(8):
                cell_alpha = alpha.crop(
                    (
                        column * CELL_WIDTH,
                        row * CELL_HEIGHT,
                        (column + 1) * CELL_WIDTH,
                        (row + 1) * CELL_HEIGHT,
                    )
                )
                bbox = cell_alpha.getbbox()
                if column < used_count and bbox is None:
                    errors.append(f"used cell row {row}, column {column} is empty")
                if column >= used_count and bbox is not None:
                    errors.append(f"unused cell row {row}, column {column} is not transparent")

    return {
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "spritesheetBytes": spritesheet.stat().st_size,
        "dimensions": list(ATLAS_SIZE),
        "usedFrames": list(USED_FRAMES),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate the Feibi Jiubi Codex pet package")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()

    result = validate_pet(args.root.resolve())
    if args.as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        status = "PASS" if result["ok"] else "FAIL"
        print(f"[{status}] Codex pet package")
        print(f"Spritesheet: {result.get('dimensions')} / {result.get('spritesheetBytes', 0)} bytes")
        for warning in result["warnings"]:
            print(f"Warning: {warning}")
        for error in result["errors"]:
            print(f"Error: {error}")

    raise SystemExit(0 if result["ok"] else 1)


if __name__ == "__main__":
    main()
