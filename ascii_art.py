#!/usr/bin/env python3
"""Picture to colored ASCII art.

Usage:
    python ascii_art.py input.png            -> input_ascii.png
    python ascii_art.py input.jpg output.png -> output.png (same WxH as input)
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

RAMP = "@%#*+=-:. "
FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    "/usr/share/fonts/truetype/noto/NotoSansMono-Regular.ttf",
]


def load_font(size):
    for path in FONT_CANDIDATES:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    src = Path(sys.argv[1])
    if not src.exists():
        print(f"File not found: {src}", file=sys.stderr)
        sys.exit(1)

    out = Path(sys.argv[2]) if len(sys.argv) > 2 else src.with_name(f"{src.stem}_ascii.png")

    img = Image.open(src).convert("RGB")
    w, h = img.size

    cols = max(40, min(240, w // 10))
    font_size = max(8, int((w / cols) / 0.62))
    font = load_font(font_size)
    ascent, descent = font.getmetrics()
    char_w = int(font.getlength("M"))
    char_h = ascent + descent

    rows = max(1, int(cols * (h / w) * (char_w / char_h)))

    sample = img.resize((cols, rows), Image.BOX)
    canvas = Image.new("RGB", (cols * char_w, rows * char_h), "black")
    draw = ImageDraw.Draw(canvas)

    ramp_len = len(RAMP)
    for cy in range(rows):
        for cx in range(cols):
            r, g, b = sample.getpixel((cx, cy))
            lum = (0.299 * r + 0.587 * g + 0.114 * b) / 255.0
            idx = int((1.0 - lum) * (ramp_len - 1))
            ch = RAMP[idx]
            x = cx * char_w
            y = cy * char_h
            draw.text((x, y), ch, font=font, fill=(r, g, b), anchor="lt")

    final = canvas.resize((w, h), Image.LANCZOS)
    if out.suffix.lower() in (".jpg", ".jpeg"):
        final = final.convert("RGB")
    final.save(out)

    print(f"Saved {cols}x{rows} chars to {out} ({w}x{h}px)")


if __name__ == "__main__":
    main()
