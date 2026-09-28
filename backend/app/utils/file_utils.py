from io import BytesIO
from pathlib import Path

from fastapi import HTTPException, UploadFile
from PIL import Image

from app import config

ALLOWED_TYPES = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}


async def save_uploads(files: list[UploadFile], target_dir: Path) -> list[Path]:
    """Validate and store uploaded images under server-generated names."""
    target_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for idx, file in enumerate(files):
        ext = ALLOWED_TYPES.get(file.content_type or "")
        if ext is None:
            raise HTTPException(400, f"Định dạng không hỗ trợ: {file.filename}")

        data = await file.read(config.MAX_IMAGE_BYTES + 1)
        if len(data) > config.MAX_IMAGE_BYTES:
            raise HTTPException(400, f"Ảnh quá lớn (>10MB): {file.filename}")
        try:
            Image.open(BytesIO(data)).verify()
        except Exception:
            raise HTTPException(400, f"File ảnh không hợp lệ: {file.filename}")

        path = target_dir / f"{idx:02d}{ext}"
        path.write_bytes(data)
        paths.append(path)
    return paths
