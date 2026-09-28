"""Pre-download model weights into backend/model_weights/.

Usage (from backend/):  python -m scripts.download_models [--skip-i2v] [--skip-llm]
"""
import argparse

from app import config  # noqa: F401  (sets HF_HOME)
from huggingface_hub import snapshot_download

parser = argparse.ArgumentParser()
parser.add_argument("--skip-i2v", action="store_true")
parser.add_argument("--skip-llm", action="store_true")
args = parser.parse_args()

if not args.skip_llm:
    print(f"Downloading {config.LLM_MODEL_ID} ...")
    snapshot_download(config.LLM_MODEL_ID)

if not args.skip_i2v:
    print(f"Downloading {config.I2V_MODEL_ID} ...")
    snapshot_download(config.I2V_MODEL_ID, allow_patterns=["*.json", "*.txt", "*.model", "*.safetensors"],
                      ignore_patterns=["ltx-video-*.safetensors", "ltxv-*.safetensors"])

print(f"Done. Weights stored in {config.MODEL_DIR}")
