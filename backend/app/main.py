import logging

from app import config  # noqa: F401  (sets HF_HOME before model imports)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes import router

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Affiliate Video Generator", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_ORIGINS,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(router)
app.mount("/outputs", StaticFiles(directory=config.OUTPUT_DIR), name="outputs")


@app.get("/health")
def health():
    return {"status": "ok"}
