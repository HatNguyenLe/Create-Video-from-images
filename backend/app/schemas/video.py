from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator, model_validator

from app.services.tts_service import VOICES


class VideoRequest(BaseModel):
    product_name: str = Field("", max_length=200)
    description: str = Field("", max_length=3000)
    script: str = Field("", max_length=5000)
    voice: str = "vi-VN-HoaiMyNeural"
    aspect_ratio: Literal["9:16", "16:9", "1:1"] = "9:16"
    duration: int = Field(35, ge=30, le=40)
    mode: Literal["kenburns", "ai"] = "kenburns"
    subtitles: bool = True

    @field_validator("voice")
    @classmethod
    def check_voice(cls, v: str) -> str:
        if v not in VOICES:
            raise ValueError("Giọng đọc không hợp lệ.")
        return v

    @model_validator(mode="after")
    def check_content(self):
        if not (self.script.strip() or self.description.strip() or self.product_name.strip()):
            raise ValueError("Cần nhập kịch bản, mô tả hoặc tên sản phẩm.")
        return self


class JobCreated(BaseModel):
    job_id: str


class JobStatus(BaseModel):
    id: str
    status: Literal["queued", "running", "completed", "failed"]
    progress: int
    message: str
    video_url: Optional[str] = None
    script: Optional[str] = None
    error: Optional[str] = None


class ScriptResponse(BaseModel):
    script: str
