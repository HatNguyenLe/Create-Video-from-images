import threading

from PIL import Image

from app import config

NEGATIVE_PROMPT = "worst quality, blurry, jittery, distorted, deformed, watermark, text, low resolution"


class ImageToVideoModel:
    """LTX-Video image-to-video wrapper (lazy-loaded singleton)."""

    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        import torch
        from diffusers import LTXImageToVideoPipeline

        if not torch.cuda.is_available():
            raise RuntimeError("Chế độ AI cần GPU CUDA. Hãy chọn chế độ 'Ken Burns'.")
        self.torch = torch
        self.pipe = LTXImageToVideoPipeline.from_pretrained(config.I2V_MODEL_ID, torch_dtype=torch.bfloat16)
        self.pipe.enable_model_cpu_offload()
        self.pipe.vae.enable_tiling()

    @classmethod
    def get(cls) -> "ImageToVideoModel":
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
        return cls._instance

    def generate(
        self,
        image: Image.Image,
        prompt: str,
        width: int,
        height: int,
        num_frames: int = 97,  # must be 8k+1
        steps: int = 40,
        seed: int = 42,
    ) -> list[Image.Image]:
        generator = self.torch.Generator().manual_seed(seed)
        result = self.pipe(
            image=image,
            prompt=prompt,
            negative_prompt=NEGATIVE_PROMPT,
            width=width,
            height=height,
            num_frames=num_frames,
            num_inference_steps=steps,
            generator=generator,
        )
        return result.frames[0]
