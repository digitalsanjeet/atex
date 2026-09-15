#!/usr/bin/env python3
"""Build a labeled contact sheet of rendered frames for style review.

Writes out/contact_sheet.png \u2014 one thumbnail per frame in timestamp order, each
labeled with its mm-ss filename, so 10+ beats can be eyeballed at once.
Larger thumbnails, then a second denser sheet, so both detail and coverage are visible.
"""

import argparse
import os

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG_DIR = os.path.join(ROOT, "images")
OUT_DIR = os.path.join(ROOT, "out")


def font(size):
    for path in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ):
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def build(cols, thumb_w, out_name):
    files = sorted(f for f in os.listdir(IMG_DIR) if f.endswith(".png"))
    if not files:
        print("no frames rendered yet")
        return

    thumb_h = round(thumb_w * 9 / 16)
    pad, label_h = 10, 30
    cell_w, cell_h = thumb_w + pad, thumb_h + label_h + pad
    rows = -(-len(files) // cols)
    sheet = Image.new("RGB", (cols * cell_w + pad, rows * cell_h + pad), (245, 245, 242))
    draw = ImageDraw.Draw(sheet)
    lf = font(max(16, thumb_w // 22))

    for i, name in enumerate(files):
        r, c = divmod(i, cols)
        x = pad + c * cell_w
        y = pad + r * cell_h
        with Image.open(os.path.join(IMG_DIR, name)) as im:
            im = im.convert("RGB").resize((thumb_w, thumb_h), Image.LANCZOS)
            sheet.paste(im, (x, y))
        draw.rectangle([x, y, x + thumb_w, y + thumb_h], outline=(30, 30, 30), width=2)
        draw.text((x + 2, y + thumb_h + 6), name.replace(".png", ""), fill=(30, 30, 30), font=lf)

    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.join(OUT_DIR, out_name)
    sheet.save(path, "PNG", optimize=True)
    print(f"{path}: {len(files)} frames, {sheet.size[0]}x{sheet.size[1]}")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cols", type=int, default=5)
    ap.add_argument("--thumb", type=int, default=480)
    ap.add_argument("--name", default="contact_sheet.png")
    args = ap.parse_args()
    build(args.cols, args.thumb, args.name)


if __name__ == "__main__":
    main()
