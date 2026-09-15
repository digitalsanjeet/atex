#!/usr/bin/env python3
"""Normalize every frame in images/ to an exact 1920x1080 (16:9) PNG.

The generator returns ~1376x768 (~1.79:1). This crops the long edge to a true
16:9 box and rescales to 1080p so every beat is a consistent video frame.

Idempotent: already-normalized frames are skipped.
"""

import os
import sys

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG_DIR = os.path.join(ROOT, "images")
TARGET = (1920, 1080)
TARGET_RATIO = TARGET[0] / TARGET[1]


def normalize(path):
    with Image.open(path) as img:
        img = img.convert("RGB")
        if img.size == TARGET:
            return False, img.size
        w, h = img.size
        if w / h > TARGET_RATIO:  # too wide -> trim sides
            new_w = round(h * TARGET_RATIO)
            left = (w - new_w) // 2
            img = img.crop((left, 0, left + new_w, h))
        elif w / h < TARGET_RATIO:  # too tall -> trim top/bottom
            new_h = round(w / TARGET_RATIO)
            top = (h - new_h) // 2
            img = img.crop((0, top, w, top + new_h))
        img = img.resize(TARGET, Image.LANCZOS)
        img.save(path, "PNG", optimize=True)
        return True, (w, h)


def main():
    files = sorted(f for f in os.listdir(IMG_DIR) if f.endswith(".png"))
    if not files:
        print("no frames found")
        return
    changed = 0
    for name in files:
        did, old = normalize(os.path.join(IMG_DIR, name))
        if did:
            changed += 1
            print(f"  {name}: {old[0]}x{old[1]} -> {TARGET[0]}x{TARGET[1]}")
    print(f"{changed} normalized / {len(files)} frames")


if __name__ == "__main__":
    sys.exit(main())
