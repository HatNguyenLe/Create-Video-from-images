import logging
import shutil
import threading
from pathlib import Path

from app import config
from app.schemas.video import VideoRequest
from app.services.animation_service import frames_player, ken_burns, with_overlay
from app.services.job_manager import job_manager
from app.services.script_service import generate_script, split_into_scenes
from app.services.tts_service import synthesize
from app.services.video_composer import Segment, compose
from app.utils.image_utils import fit_cover, load_image
from app.utils.subtitle import make_subtitle_overlay

logger = logging.getLogger(__name__)

# One render at a time to avoid GPU/CPU contention
_render_lock = threading.Lock()


def _motion_prompt(product_name: str) -> str:
    return (
        f"Product commercial video of {product_name or 'the product'}. "
        "Slow smooth camera orbit, soft studio lighting, clean background, "
        "high detail, professional advertising footage."
    )


def run_pipeline(job_id: str, req: VideoRequest, image_paths: list[Path]) -> None:
    update = lambda **kw: job_manager.update(job_id, **kw)  # noqa: E731
    work_dir = config.TEMP_DIR / job_id
    try:
        update(message="Đang chờ tới lượt render")
        with _render_lock:
            _render(job_id, req, image_paths, work_dir, update)
    except Exception as exc:
        logger.exception("Job %s failed", job_id)
        update(status="failed", error=str(exc), message="Tạo video thất bại")
    finally:
        shutil.rmtree(work_dir, ignore_errors=True)


def _render(job_id, req: VideoRequest, image_paths, work_dir: Path, update) -> None:
    work_dir.mkdir(parents=True, exist_ok=True)
    size = config.RESOLUTIONS[req.aspect_ratio]
    n = len(image_paths)

    update(status="running", progress=5, message="Đang chuẩn bị kịch bản")
    script = req.script.strip() or "\n".join(
        generate_script(req.product_name, req.description, req.duration, n)
    )
    scenes = split_into_scenes(script, n)

    update(progress=20, message="Đang tạo giọng đọc")
    audio_paths, audio_durations = [], []
    for i, text in enumerate(scenes):
        if text:
            path = work_dir / f"scene_{i}.mp3"
            audio_durations.append(synthesize(text, req.voice, path))
            audio_paths.append(path)
        else:
            audio_durations.append(0.0)
            audio_paths.append(None)

    base = req.duration / n
    durations = [max(base, d + 0.4) for d in audio_durations]

    i2v = None
    if req.mode == "ai":
        update(progress=30, message="Đang tải model LTX-Video")
        from app.models.i2v_model import ImageToVideoModel

        i2v = ImageToVideoModel.get()

    segments = []
    for i, (path, text, dur) in enumerate(zip(image_paths, scenes, durations)):
        update(progress=30 + int(55 * i / n), message=f"Đang tạo cảnh {i + 1}/{n}")
        image = load_image(path)
        if i2v:
            frames = i2v.generate(fit_cover(image, size), _motion_prompt(req.product_name), *size)
            frame_fn = frames_player(frames, size, config.FPS)
        else:
            frame_fn = ken_burns(image, size, dur, i)
        overlay = make_subtitle_overlay(text, size) if req.subtitles and text else None
        segments.append(Segment(with_overlay(frame_fn, overlay), dur, audio_paths[i]))

    update(progress=85, message="Đang ghép video")
    compose(segments, config.OUTPUT_DIR / f"{job_id}.mp4", config.FPS)

    update(
        status="completed",
        progress=100,
        message="Hoàn thành",
        video_url=f"/outputs/{job_id}.mp4",
        script=script,
    )
