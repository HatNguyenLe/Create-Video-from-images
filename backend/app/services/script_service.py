import logging
import re

from app import config

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "Bạn là copywriter chuyên viết kịch bản lồng tiếng cho video affiliate ngắn "
    "(TikTok, Reels, Shorts). Văn phong tự nhiên, cuốn hút, đúng sự thật về sản phẩm."
)

_NUMBERING = re.compile(r"^\s*(\d+[.):]|[-*•]|Câu\s*\d+\s*:)\s*", re.IGNORECASE)
_SENTENCE_END = re.compile(r"(?<=[.!?…])\s+")


def _template_script(product_name: str, description: str) -> list[str]:
    name = product_name.strip() or "sản phẩm này"
    lines = [f"Bạn đang tìm kiếm {name}? Xem ngay video này nhé!"]
    lines += [s for s in _SENTENCE_END.split(description.strip()) if s]
    lines.append(f"{name[0].upper() + name[1:]} đang có giá ưu đãi, bấm vào link bên dưới để mua ngay!")
    return lines


def generate_script(product_name: str, description: str, duration: int, num_images: int) -> list[str]:
    num_sentences = max(num_images, round(duration / 5))
    words = int(duration * 2.6)  # ~2.6 Vietnamese words per second of narration

    if config.USE_LLM:
        try:
            from app.models.llm_model import ScriptLLM

            prompt = (
                f"Viết kịch bản lồng tiếng cho video {duration} giây giới thiệu sản phẩm "
                f"\"{product_name}\".\nThông tin sản phẩm: {description}\n\n"
                f"Yêu cầu:\n- Đúng {num_sentences} câu, mỗi câu một dòng.\n"
                f"- Tổng khoảng {words} từ.\n"
                "- Câu đầu là hook gây tò mò, các câu giữa nêu lợi ích nổi bật, "
                "câu cuối kêu gọi bấm link mua hàng.\n"
                "- Chỉ trả về các câu, không đánh số, không giải thích."
            )
            raw = ScriptLLM.get().chat(SYSTEM_PROMPT, prompt)
            lines = [_NUMBERING.sub("", ln).strip(" \"'") for ln in raw.splitlines()]
            lines = [ln for ln in lines if ln]
            if lines:
                return lines
        except Exception:
            logger.exception("LLM script generation failed, falling back to template")

    return _template_script(product_name, description)


def split_into_scenes(script: str, num_scenes: int) -> list[str]:
    """Distribute script sentences evenly across scenes (one scene per image)."""
    text = script.strip()
    units = [ln.strip() for ln in text.splitlines() if ln.strip()] if "\n" in text else _SENTENCE_END.split(text)
    units = [u for u in units if u]

    scenes: list[list[str]] = [[] for _ in range(num_scenes)]
    for i, unit in enumerate(units):
        scenes[i * num_scenes // len(units)].append(unit)
    return [" ".join(s) for s in scenes]
