import uuid
import json

from fastapi import APIRouter, BackgroundTasks, File, Form, HTTPException, UploadFile
from pydantic import ValidationError

from app import config
from app.schemas.video import JobCreated, JobStatus, ScriptResponse, VideoRequest
from app.services.job_manager import job_manager
from app.services.pipeline import run_pipeline
from app.services.script_service import generate_script
from app.services.tts_service import VOICES
from app.services.job_manager import job_manager
from app.services.training_service import delete_dataset, import_dataset, list_datasets, start_training
from app.utils.file_utils import save_uploads

router = APIRouter(prefix="/api")


@router.get("/voices")
def list_voices():
    return [{"id": k, "label": v} for k, v in VOICES.items()]


@router.get("/training/datasets")
def get_training_datasets():
    return list_datasets()


@router.post("/training/datasets")
async def create_training_dataset(
    videos: list[UploadFile] = File(...),
    name: str = Form(""),
    captions: str = Form("[]"),
):
    try:
        parsed_captions = json.loads(captions)
        if not isinstance(parsed_captions, list):
            raise ValueError
    except (TypeError, ValueError, json.JSONDecodeError):
        raise HTTPException(422, "captions phải là JSON array.")
    return await import_dataset(name, videos, parsed_captions)


@router.delete("/training/datasets/{dataset_id}")
def remove_training_dataset(dataset_id: str):
    delete_dataset(dataset_id)
    return {"status": "deleted"}


@router.post("/training/jobs", response_model=JobStatus)
def create_training_job(
    dataset_id: str = Form(...),
    epochs: int = Form(10, ge=1, le=100),
    rank: int = Form(16, ge=4, le=64),
):
    job_id = start_training(dataset_id, epochs, rank)
    job = job_manager.get(job_id)
    return JobStatus(**job.__dict__)


@router.post("/scripts/generate", response_model=ScriptResponse)
def create_script(
    product_name: str = Form("", max_length=200),
    description: str = Form("", max_length=3000),
    duration: int = Form(35, ge=30, le=40),
    num_scenes: int = Form(5, ge=1, le=config.MAX_IMAGES),
):
    if not product_name.strip() and not description.strip():
        raise HTTPException(400, "Cần nhập tên sản phẩm hoặc mô tả.")
    lines = generate_script(product_name, description, duration, num_scenes)
    return ScriptResponse(script="\n".join(lines))


@router.post("/videos", response_model=JobCreated)
async def create_video(
    background_tasks: BackgroundTasks,
    images: list[UploadFile] = File(...),
    product_name: str = Form(""),
    description: str = Form(""),
    script: str = Form(""),
    voice: str = Form("vi-VN-HoaiMyNeural"),
    aspect_ratio: str = Form("9:16"),
    duration: int = Form(35),
    mode: str = Form("kenburns"),
    subtitles: bool = Form(True),
):
    try:
        req = VideoRequest(
            product_name=product_name,
            description=description,
            script=script,
            voice=voice,
            aspect_ratio=aspect_ratio,
            duration=duration,
            mode=mode,
            subtitles=subtitles,
        )
    except ValidationError as exc:
        raise HTTPException(422, [err["msg"] for err in exc.errors()])

    if not 1 <= len(images) <= config.MAX_IMAGES:
        raise HTTPException(400, f"Cần từ 1 đến {config.MAX_IMAGES} ảnh.")

    job_id = uuid.uuid4().hex
    image_paths = await save_uploads(images, config.UPLOAD_DIR / job_id)
    job_manager.create(job_id)
    background_tasks.add_task(run_pipeline, job_id, req, image_paths)
    return JobCreated(job_id=job_id)


@router.get("/videos/{job_id}", response_model=JobStatus)
def get_video(job_id: str):
    job = job_manager.get(job_id)
    if job is None:
        raise HTTPException(404, "Không tìm thấy job.")
    return JobStatus(**job.__dict__)
