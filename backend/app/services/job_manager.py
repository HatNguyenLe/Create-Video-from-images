import threading
from dataclasses import dataclass
from typing import Optional


@dataclass
class Job:
    id: str
    status: str = "queued"
    progress: int = 0
    message: str = "Đang chờ xử lý"
    video_url: Optional[str] = None
    script: Optional[str] = None
    error: Optional[str] = None


class JobManager:
    """In-memory job store; replace with Redis/DB for multi-process deployments."""

    def __init__(self):
        self._jobs: dict[str, Job] = {}
        self._lock = threading.Lock()

    def create(self, job_id: str) -> Job:
        with self._lock:
            job = Job(id=job_id)
            self._jobs[job_id] = job
            return job

    def update(self, job_id: str, **fields) -> None:
        with self._lock:
            job = self._jobs[job_id]
            for key, value in fields.items():
                setattr(job, key, value)

    def get(self, job_id: str) -> Optional[Job]:
        with self._lock:
            return self._jobs.get(job_id)


job_manager = JobManager()
