import os
import platform
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")
STORAGE_DIR = BASE_DIR / "storage"
UPLOAD_DIR = STORAGE_DIR / "uploads"
OUTPUT_DIR = STORAGE_DIR / "outputs"
TEMP_DIR = STORAGE_DIR / "temp"
MODEL_DIR = BASE_DIR / "model_weights"
TRAINING_DIR = STORAGE_DIR / "training"

for _dir in (UPLOAD_DIR, OUTPUT_DIR, TEMP_DIR, MODEL_DIR, TRAINING_DIR):
    _dir.mkdir(parents=True, exist_ok=True)

# Must be set before diffusers/transformers are imported so weights are cached in model_weights/
os.environ.setdefault("HF_HOME", str(MODEL_DIR))

I2V_MODEL_ID = os.getenv("I2V_MODEL_ID", "Lightricks/LTX-Video")
LLM_MODEL_ID = os.getenv("LLM_MODEL_ID", "Qwen/Qwen2.5-1.5B-Instruct")
USE_LLM = os.getenv("USE_LLM", "1") == "1"

_DEFAULT_FONT = (
    "C:/Windows/Fonts/arialbd.ttf"
    if platform.system() == "Windows"
    else "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
)
FONT_PATH = os.getenv("FONT_PATH", _DEFAULT_FONT)

FPS = 24
MAX_IMAGES = 10
MAX_IMAGE_BYTES = 10 * 1024 * 1024
MAX_TRAINING_VIDEOS = 20
MAX_TRAINING_VIDEO_BYTES = 200 * 1024 * 1024
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")

# Width/height divisible by 32 as required by LTX-Video
RESOLUTIONS = {
    "9:16": (480, 832),
    "16:9": (832, 480),
    "1:1": (640, 640),
}
