from typing import Callable

import numpy as np
from PIL import Image

from app.utils.image_utils import fit_cover

FrameFn = Callable[[float], np.ndarray]

_EFFECTS = ("zoom_in", "pan_right", "zoom_out", "pan_left")
_OVERSCAN = 1.2


def _ease(p: float) -> float:
    return p * p * (3 - 2 * p)


def ken_burns(image: Image.Image, size: tuple[int, int], duration: float, index: int) -> FrameFn:
    """CPU-only zoom/pan animation; effect rotates per scene for variety."""
    w, h = size
    base = fit_cover(image, (int(w * _OVERSCAN), int(h * _OVERSCAN)))
    bw, bh = base.size
    effect = _EFFECTS[index % len(_EFFECTS)]

    def frame(t: float) -> np.ndarray:
        p = _ease(min(max(t / duration, 0.0), 1.0))
        if effect in ("zoom_in", "zoom_out"):
            scale = _OVERSCAN - (_OVERSCAN - 1) * (p if effect == "zoom_in" else 1 - p)
            cw, ch = w * scale, h * scale
            x0, y0 = (bw - cw) / 2, (bh - ch) / 2
        else:
            cw, ch = w, h
            x0 = (bw - cw) * (p if effect == "pan_right" else 1 - p)
            y0 = (bh - ch) / 2
        img = base.transform(size, Image.Transform.EXTENT, (x0, y0, x0 + cw, y0 + ch), Image.Resampling.BICUBIC)
        return np.asarray(img)

    return frame


def frames_player(frames: list[Image.Image], size: tuple[int, int], fps: int) -> FrameFn:
    """Play AI-generated frames, ping-pong looping if the scene is longer than the clip."""
    arrays = [np.asarray(f.convert("RGB").resize(size, Image.Resampling.BICUBIC)) for f in frames]
    n = len(arrays)
    period = max(2 * n - 2, 1)

    def frame(t: float) -> np.ndarray:
        i = int(t * fps) % period
        return arrays[i if i < n else period - i]

    return frame


def with_overlay(frame_fn: FrameFn, overlay: Image.Image | None) -> FrameFn:
    if overlay is None:
        return frame_fn
    rgba = np.asarray(overlay).astype(np.float32)
    alpha = rgba[..., 3:] / 255.0
    rgb = rgba[..., :3] * alpha
    inv = 1.0 - alpha

    def frame(t: float) -> np.ndarray:
        return (frame_fn(t).astype(np.float32) * inv + rgb).astype(np.uint8)

    return frame
