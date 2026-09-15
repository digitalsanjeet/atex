#!/usr/bin/env python3
"""Shrink rendered frames so all 205 can live in git.

Why: uncommitted files in this workspace do NOT reliably survive between turns. The
generated frames were gitignored at the start of the project, and 51 finished frames
were silently dropped by the sandbox while text files remained. A 205-frame film only
exists if the frames are committed, and 205 x 1.4MB PNG busts the ~128MB artifact cap.

These are flat pastel illustrations with a limited palette, so a 256-color adaptive
quantization loses almost nothing visually and cuts size by ~4x.

    python3 tools/pack_frames.py            # quantize every frame in place
    python3 tools/pack_frames.py --report   # sizes + projection, no changes
"""

import argparse
import glob
import os

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG_DIR = os.path.join(ROOT, "images")
TOTAL_BEATS = 205


def pack(path, colors):
    im = Image.open(path).convert("RGB")
    q = im.quantize(colors=colors, method=Image.MEDIANCUT, dither=Image.NONE)
    tmp = path + ".tmp.png"
    q.save(tmp, optimize=True)
    os.replace(tmp, path)
    return im.size


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--colors", type=int, default=256)
    ap.add_argument("--report", action="store_true", help="measure only")
    args = ap.parse_args()

    files = sorted(glob.glob(os.path.join(IMG_DIR, "*.png")))
    if not files:
        print("no frames")
        return 0

    before = sum(os.path.getsize(f) for f in files)
    for f in files:
        if not args.report:
            pack(f, args.colors)
    after = sum(os.path.getsize(f) for f in files)
    avg = after / len(files)

    print(f"{len(files)} frames: {before/1e6:.1f}MB -> {after/1e6:.1f}MB "
          f"({avg/1e6:.2f}MB avg)")
    print(f"projected for all {TOTAL_BEATS}: {avg * TOTAL_BEATS / 1e6:.0f}MB "
          f"(artifact cap ~128MB)")
    if not args.report:
        print("frames are now small enough to commit; do it before the turn ends")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
