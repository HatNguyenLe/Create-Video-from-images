from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from moviepy import AudioFileClip, VideoClip, concatenate_videoclips

from app.services.animation_service import FrameFn


@dataclass
class Segment:
    frame_fn: FrameFn
    duration: float
    audio_path: Optional[Path] = None


def compose(segments: list[Segment], out_path: Path, fps: int) -> None:
    clips, audios = [], []
    final = None
    try:
        for seg in segments:
            clip = VideoClip(seg.frame_fn, duration=seg.duration)
            if seg.audio_path:
                audio = AudioFileClip(str(seg.audio_path))
                audios.append(audio)
                clip = clip.with_audio(audio)
            clips.append(clip)

        final = concatenate_videoclips(clips)
        final.write_videofile(
            str(out_path), fps=fps, codec="libx264", audio_codec="aac", preset="medium", logger=None
        )
    finally:
        for c in [final, *clips, *audios]:
            if c is not None:
                c.close()
