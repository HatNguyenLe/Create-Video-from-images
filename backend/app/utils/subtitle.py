from PIL import Image, ImageDraw, ImageFont

from app import config


def _load_font(size: int) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype(config.FONT_PATH, size)
    except OSError:
        return ImageFont.load_default(size=size)


def _wrap(text: str, font, max_width: float, draw: ImageDraw.ImageDraw) -> list[str]:
    lines, current = [], ""
    for word in text.split():
        candidate = f"{current} {word}".strip()
        if draw.textlength(candidate, font=font) <= max_width or not current:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def make_subtitle_overlay(text: str, size: tuple[int, int]) -> Image.Image:
    """Render a transparent RGBA layer with the subtitle box in the lower third."""
    w, h = size
    font_size = max(18, int(min(w, h) * 0.055))
    font = _load_font(font_size)
    overlay = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    lines = _wrap(text, font, w * 0.84, draw)
    line_h = int(font_size * 1.35)
    pad = int(font_size * 0.5)
    box_h = len(lines) * line_h + pad * 2
    top = max(0, min(int(h * 0.78 - box_h / 2), h - box_h - pad))

    draw.rounded_rectangle([w * 0.05, top, w * 0.95, top + box_h], radius=16, fill=(0, 0, 0, 150))
    y = top + pad
    for line in lines:
        tw = draw.textlength(line, font=font)
        draw.text(((w - tw) / 2, y), line, font=font, fill="white", stroke_width=2, stroke_fill="black")
        y += line_h
    return overlay
