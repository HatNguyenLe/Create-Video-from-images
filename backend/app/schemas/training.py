from pydantic import BaseModel, Field


class TrainingJobRequest(BaseModel):
    dataset_id: str
    epochs: int = Field(10, ge=1, le=100)
    rank: int = Field(16, ge=4, le=64)
