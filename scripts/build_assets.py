from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageOps


ROOT = Path(__file__).resolve().parents[1]
BOARD_PATH = ROOT / "artwork" / "generated" / "feibi-jiubi-pose-board.png"
ATLAS_PATH = ROOT / "pet" / "spritesheet.webp"
MEDIA_DIR = ROOT / "media"
ACTIONS_DIR = MEDIA_DIR / "actions"

CELL_WIDTH = 192
CELL_HEIGHT = 208
ATLAS_COLUMNS = 8
ATLAS_ROWS = 9
ATLAS_SIZE = (CELL_WIDTH * ATLAS_COLUMNS, CELL_HEIGHT * ATLAS_ROWS)


@dataclass(frozen=True)
class FrameSpec:
    pose: int
    dx: int = 0
    dy: int = 0
    rotation: float = 0.0
    scale_x: float = 1.0
    scale_y: float = 1.0
    mirror: bool = False


@dataclass(frozen=True)
class ActionSpec:
    name: str
    frames: tuple[FrameSpec, ...]
    durations: tuple[int, ...]


RUN_CYCLE = (
    (1, -2, 2, -2.0, 1.02, 0.98),
    (2, 0, -1, 1.0, 0.98, 1.02),
    (1, 2, 1, 2.0, 1.01, 0.99),
    (2, 0, -2, -1.0, 0.98, 1.02),
    (1, -2, 2, -2.0, 1.02, 0.98),
    (2, 0, -1, 1.0, 0.98, 1.02),
    (1, 2, 1, 2.0, 1.01, 0.99),
    (2, 0, 0, 0.0, 1.0, 1.0),
)


def _run_frames(*, mirror: bool) -> tuple[FrameSpec, ...]:
    return tuple(
        FrameSpec(
            pose=pose,
            dx=dx,
            dy=dy,
            rotation=rotation,
            scale_x=scale_x,
            scale_y=scale_y,
            mirror=mirror,
        )
        for pose, dx, dy, rotation, scale_x, scale_y in RUN_CYCLE
    )


ACTIONS = (
    ActionSpec(
        "idle",
        (
            FrameSpec(0),
            FrameSpec(0, dy=-1, scale_y=1.01),
            FrameSpec(0, dy=-2, scale_x=1.01, scale_y=1.02),
            FrameSpec(0, dy=-1, rotation=0.5, scale_y=1.01),
            FrameSpec(0, rotation=-0.5, scale_x=0.995),
            FrameSpec(0),
        ),
        (280, 110, 110, 140, 140, 320),
    ),
    ActionSpec(
        "running-right",
        _run_frames(mirror=True),
        (120, 120, 120, 120, 120, 120, 120, 220),
    ),
    ActionSpec(
        "running-left",
        _run_frames(mirror=False),
        (120, 120, 120, 120, 120, 120, 120, 220),
    ),
    ActionSpec(
        "waving",
        (
            FrameSpec(3, rotation=-1.0),
            FrameSpec(3, dy=-2, rotation=1.5),
            FrameSpec(3, dy=-1, rotation=-1.5),
            FrameSpec(3),
        ),
        (140, 140, 140, 280),
    ),
    ActionSpec(
        "jumping",
        (
            FrameSpec(4, dy=10, scale_x=1.05, scale_y=0.95),
            FrameSpec(4, dy=-4, scale_x=0.98, scale_y=1.03),
            FrameSpec(4, dy=-16, scale_x=0.96, scale_y=1.06),
            FrameSpec(4, dy=-4, scale_x=0.98, scale_y=1.03),
            FrameSpec(4, dy=10, scale_x=1.05, scale_y=0.95),
        ),
        (140, 140, 140, 140, 280),
    ),
    ActionSpec(
        "failed",
        (
            FrameSpec(5, dx=-4, rotation=-2.0),
            FrameSpec(5, dx=4, rotation=2.0),
            FrameSpec(5, dx=-3, rotation=-1.5),
            FrameSpec(5, dx=3, rotation=1.5),
            FrameSpec(5, dx=-2, rotation=-1.0),
            FrameSpec(5, dx=2, rotation=1.0),
            FrameSpec(5, dx=-1, rotation=-0.5),
            FrameSpec(5),
        ),
        (140, 140, 140, 140, 140, 140, 140, 240),
    ),
    ActionSpec(
        "waiting",
        (
            FrameSpec(6, rotation=-1.0),
            FrameSpec(6, dy=-1),
            FrameSpec(6, dy=-2, rotation=1.0),
            FrameSpec(6, dy=-1),
            FrameSpec(6, rotation=-0.5),
            FrameSpec(6),
        ),
        (150, 150, 150, 150, 150, 260),
    ),
    ActionSpec(
        "running",
        (
            FrameSpec(7, dx=-1),
            FrameSpec(7, dx=1, dy=-1, rotation=0.5),
            FrameSpec(7, dy=-2, rotation=-0.5),
            FrameSpec(7, dx=-1, dy=-1),
            FrameSpec(7, dx=1, rotation=0.5),
            FrameSpec(7),
        ),
        (120, 120, 120, 120, 120, 220),
    ),
    ActionSpec(
        "review",
        (
            FrameSpec(8, rotation=-1.0),
            FrameSpec(8, dy=-2, rotation=0.5),
            FrameSpec(8, dy=-3, rotation=1.0),
            FrameSpec(8, dy=-2, rotation=0.5),
            FrameSpec(8, dy=-1, rotation=-0.5),
            FrameSpec(8),
        ),
        (150, 150, 150, 150, 150, 280),
    ),
)


def _clean_transparency(image: Image.Image) -> Image.Image:
    """Remove low-alpha chroma residue before affine transforms interpolate it."""
    cleaned: list[tuple[int, int, int, int]] = []
    for red, green, blue, alpha in image.get_flattened_data():
        green_residue = green > red + 40 and green > blue + 24
        if alpha < 96 or green_residue:
            cleaned.append((0, 0, 0, 0))
        else:
            cleaned.append((red, green, blue, alpha))
    result = Image.new("RGBA", image.size, (0, 0, 0, 0))
    result.putdata(cleaned)
    return result


def _clear_hidden_rgb(image: Image.Image) -> Image.Image:
    """Keep fully transparent pixels deterministic across WebP decoders."""
    pixels = [
        (0, 0, 0, 0) if alpha == 0 else (red, green, blue, alpha)
        for red, green, blue, alpha in image.get_flattened_data()
    ]
    cleaned = Image.new("RGBA", image.size, (0, 0, 0, 0))
    cleaned.putdata(pixels)
    return cleaned


def load_poses(path: Path = BOARD_PATH) -> list[Image.Image]:
    board = Image.open(path).convert("RGBA")
    if board.width % 3 or board.height % 3:
        raise ValueError(f"Pose board must divide into a 3x3 grid: {board.size}")

    cell_width = board.width // 3
    cell_height = board.height // 3
    poses: list[Image.Image] = []

    for index in range(9):
        column = index % 3
        row = index // 3
        cell = board.crop(
            (
                column * cell_width,
                row * cell_height,
                (column + 1) * cell_width,
                (row + 1) * cell_height,
            )
        )
        cell = _clean_transparency(cell)
        alpha = cell.getchannel("A")
        bbox = alpha.point(lambda value: 255 if value > 16 else 0).getbbox()
        if bbox is None:
            raise ValueError(f"Pose {index} is empty")
        left, top, right, bottom = bbox
        padding = 4
        poses.append(
            cell.crop(
                (
                    max(0, left - padding),
                    max(0, top - padding),
                    min(cell.width, right + padding),
                    min(cell.height, bottom + padding),
                )
            )
        )

    return poses


def _fit_pose(pose: Image.Image, *, max_width: int = 178, max_height: int = 188) -> Image.Image:
    scale = min(max_width / pose.width, max_height / pose.height)
    size = (
        max(1, round(pose.width * scale)),
        max(1, round(pose.height * scale)),
    )
    return pose.resize(size, Image.Resampling.LANCZOS)


def render_frame(poses: list[Image.Image], spec: FrameSpec) -> Image.Image:
    pose = _fit_pose(poses[spec.pose])
    if spec.mirror:
        pose = ImageOps.mirror(pose)

    if spec.scale_x != 1.0 or spec.scale_y != 1.0:
        pose = pose.resize(
            (
                max(1, round(pose.width * spec.scale_x)),
                max(1, round(pose.height * spec.scale_y)),
            ),
            Image.Resampling.LANCZOS,
        )

    if spec.rotation:
        pose = pose.rotate(
            spec.rotation,
            resample=Image.Resampling.BICUBIC,
            expand=True,
            fillcolor=(0, 0, 0, 0),
        )

    max_width = CELL_WIDTH - 4
    max_height = CELL_HEIGHT - 4
    if pose.width > max_width or pose.height > max_height:
        scale = min(max_width / pose.width, max_height / pose.height)
        pose = pose.resize(
            (round(pose.width * scale), round(pose.height * scale)),
            Image.Resampling.LANCZOS,
        )

    canvas = Image.new("RGBA", (CELL_WIDTH, CELL_HEIGHT), (0, 0, 0, 0))
    x = (CELL_WIDTH - pose.width) // 2 + spec.dx
    y = CELL_HEIGHT - pose.height - 6 + spec.dy
    x = min(max(x, 0), CELL_WIDTH - pose.width)
    y = min(max(y, 0), CELL_HEIGHT - pose.height)
    canvas.alpha_composite(pose, (x, y))
    return canvas


def build_frames(poses: list[Image.Image]) -> dict[str, list[Image.Image]]:
    return {
        action.name: [render_frame(poses, frame) for frame in action.frames]
        for action in ACTIONS
    }


def build_atlas(frames: dict[str, list[Image.Image]]) -> Image.Image:
    atlas = Image.new("RGBA", ATLAS_SIZE, (0, 0, 0, 0))
    for row, action in enumerate(ACTIONS):
        for column, frame in enumerate(frames[action.name]):
            atlas.alpha_composite(frame, (column * CELL_WIDTH, row * CELL_HEIGHT))
    return atlas


def _gif_frame(frame: Image.Image) -> Image.Image:
    rgb = frame.convert("RGB")
    paletted = rgb.quantize(colors=255, method=Image.Quantize.MEDIANCUT)
    transparent = frame.getchannel("A").point(lambda value: 255 if value < 96 else 0)
    paletted.paste(255, mask=transparent)
    paletted.info["transparency"] = 255
    paletted.info["disposal"] = 2
    return paletted


def save_gif(
    frames: Iterable[Image.Image],
    durations: Iterable[int],
    output: Path,
) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    gif_frames = [_gif_frame(frame) for frame in frames]
    duration_values = list(durations)
    gif_frames[0].save(
        output,
        save_all=True,
        append_images=gif_frames[1:],
        loop=0,
        duration=duration_values,
        disposal=2,
        transparency=255,
        optimize=False,
    )


def checkerboard(size: tuple[int, int], square: int = 12) -> Image.Image:
    background = Image.new("RGBA", size, (235, 239, 250, 255))
    pixels = background.load()
    for y in range(size[1]):
        for x in range(size[0]):
            if (x // square + y // square) % 2:
                pixels[x, y] = (214, 222, 241, 255)
    return background


def build_preview(frames: dict[str, list[Image.Image]]) -> Image.Image:
    preview = checkerboard((CELL_WIDTH * 3, CELL_HEIGHT * 3), square=16)
    for index, action in enumerate(ACTIONS):
        x = (index % 3) * CELL_WIDTH
        y = (index // 3) * CELL_HEIGHT
        preview.alpha_composite(frames[action.name][0], (x, y))
    return preview


def main() -> None:
    ATLAS_PATH.parent.mkdir(parents=True, exist_ok=True)
    ACTIONS_DIR.mkdir(parents=True, exist_ok=True)

    poses = load_poses()
    frames = build_frames(poses)
    atlas = _clear_hidden_rgb(build_atlas(frames))
    atlas.save(
        ATLAS_PATH,
        format="WEBP",
        lossless=True,
        quality=100,
        method=6,
        exact=True,
    )

    for action in ACTIONS:
        save_gif(
            frames[action.name],
            action.durations,
            ACTIONS_DIR / f"{action.name}.gif",
        )
        frames[action.name][0].save(
            ACTIONS_DIR / f"{action.name}.png",
            optimize=True,
        )

    build_preview(frames).save(MEDIA_DIR / "preview.png", optimize=True)
    frames["idle"][0].save(MEDIA_DIR / "hero.png", optimize=True)
    showcase_frames: list[Image.Image] = []
    showcase_durations: list[int] = []
    for action in ACTIONS:
        showcase_frames.extend(frames[action.name])
        showcase_durations.extend(action.durations)
    save_gif(showcase_frames, showcase_durations, MEDIA_DIR / "showcase.gif")

    checksums: list[str] = []
    for relative_path in (Path("pet/pet.json"), Path("pet/spritesheet.webp")):
        digest = hashlib.sha256(ROOT.joinpath(relative_path).read_bytes()).hexdigest()
        checksums.append(f"{digest}  {relative_path.as_posix()}")
    ROOT.joinpath("checksums.txt").write_text(
        "\n".join(checksums) + "\n",
        encoding="utf-8",
        newline="\n",
    )

    print(f"Wrote {ATLAS_PATH.relative_to(ROOT)} ({ATLAS_SIZE[0]}x{ATLAS_SIZE[1]})")
    print(f"Wrote {len(ACTIONS)} action previews to {ACTIONS_DIR.relative_to(ROOT)}")
    print(f"Wrote {MEDIA_DIR.joinpath('preview.png').relative_to(ROOT)}")
    print(f"Wrote {MEDIA_DIR.joinpath('showcase.gif').relative_to(ROOT)}")
    print("Wrote checksums.txt")


if __name__ == "__main__":
    main()
