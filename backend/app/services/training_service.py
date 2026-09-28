import json
import logging
import shutil
import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile

from app import config
from app.services.job_manager import job_manager

logger = logging.getLogger(__name__)
VIDEO_TYPES = {"video/mp4": ".mp4", "video/quicktime": ".mov", "video/webm": ".webm"}
DATASET_INDEX = config.TRAINING_DIR / "datasets.json"


def _read_index() -> list[dict]:
    if not DATASET_INDEX.exists():
        return []
    try:
        return json.loads(DATASET_INDEX.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []


def _write_index(items: list[dict]) -> None:
    DATASET_INDEX.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")


def list_datasets() -> list[dict]:
    return _read_index()


async def import_dataset(name: str, videos: list[UploadFile], captions: list[str]) -> dict:
    if not videos:
        raise HTTPException(400, "Cần chọn ít nhất một video.")
    if len(videos) > config.MAX_TRAINING_VIDEOS:
        raise HTTPException(400, f"Tối đa {config.MAX_TRAINING_VIDEOS} video mỗi dataset.")

    dataset_id = uuid.uuid4().hex
    dataset_dir = config.TRAINING_DIR / dataset_id
    dataset_dir.mkdir(parents=True, exist_ok=True)
    records = []
    try:
        for index, video in enumerate(videos):
            extension = VIDEO_TYPES.get(video.content_type or "")
            if extension is None:
                raise HTTPException(400, f"Định dạng video không hỗ trợ: {video.filename}")
            data = await video.read(config.MAX_TRAINING_VIDEO_BYTES + 1)
            if len(data) > config.MAX_TRAINING_VIDEO_BYTES:
                raise HTTPException(400, f"Video quá lớn (tối đa 200MB): {video.filename}")
            path = dataset_dir / f"{index:04d}{extension}"
            path.write_bytes(data)
            records.append({
                "file": path.name,
                "original_name": video.filename or path.name,
                "caption": captions[index].strip() if index < len(captions) else "",
                "bytes": len(data),
            })

        metadata_path = dataset_dir / "metadata.jsonl"
        metadata_path.write_text(
            "".join(json.dumps(record, ensure_ascii=False) + "\n" for record in records),
            encoding="utf-8",
        )
        item = {
            "id": dataset_id,
            "name": name.strip() or f"Dataset {dataset_id[:8]}",
            "video_count": len(records),
            "total_bytes": sum(record["bytes"] for record in records),
            "path": str(dataset_dir),
            "status": "ready",
        }
        index = _read_index()
        index.append(item)
        _write_index(index)
        return item
    except Exception:
        shutil.rmtree(dataset_dir, ignore_errors=True)
        raise


def delete_dataset(dataset_id: str) -> None:
    datasets = _read_index()
    item = next((dataset for dataset in datasets if dataset["id"] == dataset_id), None)
    if item is None:
        raise HTTPException(404, "Không tìm thấy dataset.")
    shutil.rmtree(config.TRAINING_DIR / dataset_id, ignore_errors=True)
    _write_index([dataset for dataset in datasets if dataset["id"] != dataset_id])


def start_training(dataset_id: str, epochs: int, rank: int) -> str:
    dataset = next((item for item in _read_index() if item["id"] == dataset_id), None)
    if dataset is None:
        raise HTTPException(404, "Không tìm thấy dataset.")
    job_id = f"train-{uuid.uuid4().hex}"
    job_manager.create(job_id)
    job_manager.update(job_id, message="Dataset đã sẵn sàng; đang kiểm tra GPU")
    try:
        import torch
        if not torch.cuda.is_available():
            job_manager.update(
                job_id,
                status="failed",
                progress=100,
                message="Chưa chạy training",
                error="Fine-tuning LTX-Video cần GPU CUDA. Máy hiện tại chỉ có MX130 2GB VRAM; hãy dùng máy/cloud GPU mạnh hơn.",
            )
            return job_id
    except ImportError:
        job_manager.update(job_id, status="failed", progress=100, message="Thiếu PyTorch", error="Cài requirements-ai.txt trước khi training.")
        return job_id

    # The training backend is deliberately gated until a CUDA training environment is available.
    job_manager.update(
        job_id,
        status="failed",
        progress=100,
        message="Dataset đã chuẩn bị xong",
        error=f"Đã nhận cấu hình epochs={epochs}, rank={rank}. Cần tích hợp trainer LTX-Video trên GPU CUDA để bắt đầu fine-tuning.",
    )
    return job_id
