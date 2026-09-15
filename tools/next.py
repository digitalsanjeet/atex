#!/usr/bin/env python3
"""Print the exact image prompts for the next unrendered beats.

The generator caps image renders at 10 per user turn, so this script exists to
make each continuation turn mechanical: ask for the next batch, paste the prompts,
run `normalize_frames.py`, commit. Nothing has to be remembered between turns.

Usage:
    python3 tools/next.py            # next 10 missing beats
    python3 tools/next.py -n 5       # next 5
    python3 tools/next.py --ids      # just the timestamps, space separated
"""

import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG_DIR = os.path.join(ROOT, "images")


def missing(beats):
    return [b for b in beats if not os.path.exists(os.path.join(IMG_DIR, b["file"]))]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("-n", "--count", type=int, default=10, help="how many beats (default 10)")
    ap.add_argument("--ids", action="store_true", help="print timestamps only")
    ap.add_argument("--all", action="store_true", help="list every missing timestamp")
    args = ap.parse_args()

    with open(os.path.join(ROOT, "beats.json"), encoding="utf-8") as fh:
        beats = json.load(fh)["beats"]

    todo = missing(beats)
    if args.ids or args.all:
        print(" ".join(b["timestamp"] for b in (todo if args.all else todo[: args.count])))
        return 0

    if not todo:
        print("all 205 frames rendered")
        return 0

    batch = todo[: args.count]
    print(f"# {len(batch)} beats  |  {len(todo)} still missing of {len(beats)} total")
    print(f"# target files: {' '.join(b['file'] for b in batch)}")
    for beat in batch:
        print(f"\n## {beat['file']}\nPROMPT:\n{beat['image_prompt']}")
    print(
        f"\n# then run: python3 tools/normalize_frames.py && python3 tools/status.py",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
