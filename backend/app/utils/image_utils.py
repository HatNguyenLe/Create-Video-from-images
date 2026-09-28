from pathlib import Path

from PIL import Image, ImageOps


def load_image(path: Path) -> Image.Image:
    with Image.open(path) as img:
        return ImageOps.exif_transpose(img).convert("RGB")


def fit_cover(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    """Resize and center-crop so the image fully covers the target size."""
    return ImageOps.fit(image, size, Image.Resampling.LANCZOS, centering=(0.5, 0.5))
