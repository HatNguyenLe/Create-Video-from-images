import asyncio
from pathlib import Path

import edge_tts
from edge_tts.exceptions import NoAudioReceived
from moviepy import AudioFileClip

VOICES = {
    "vi-VN-HoaiMyNeural": "Hoài My (Nữ - Tiếng Việt)",
    "vi-VN-NamMinhNeural": "Nam Minh (Nam - Tiếng Việt)",
    "en-US-JennyNeural": "Jenny (Female - English)",
    "en-US-GuyNeural": "Guy (Male - English)",
}


async def _synthesize(text: str, voice: str, out_path: Path, rate: str) -> None:
    last_error = None
    for attempt in range(3):
        try:
            out_path.unlink(missing_ok=True)
            await edge_tts.Communicate(text, voice, rate=rate).save(str(out_path))
            if out_path.stat().st_size > 0:
                return
        except (NoAudioReceived, OSError) as exc:
            last_error = exc
            if attempt < 2:
                await asyncio.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"Không nhận được audio từ Edge TTS với giọng {voice}: {last_error}")


def synthesize(text: str, voice: str, out_path: Path, rate: str = "+5%") -> float:
    """Generate speech to an mp3 file and return its duration in seconds."""
    asyncio.run(_synthesize(text, voice, out_path, rate))
    clip = AudioFileClip(str(out_path))
    try:
        return clip.duration
    finally:
        clip.close()
