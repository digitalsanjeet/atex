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
QUEUE = os.path.join(ROOT, "rerender.txt")


def missing(beats):
    return [b for b in beats if not os.path.exists(os.path.join(IMG_DIR, b["file"]))]


def queued(by_stamp):
    """Timestamps listed in rerender.txt, in order \u2014 these go ahead of new beats."""
    if not os.path.exists(QUEUE):
        return []
    out = []
    with open(QUEUE, encoding="utf-8") as fh:
        for line in fh:
            stamp = line.strip()
            if stamp in by_stamp:
                out.append(by_stamp[stamp])
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("-n", "--count", type=int, default=10, help="how many beats (default 10)")
    ap.add_argument("--ids", action="store_true", help="print timestamps only")
    ap.add_argument("--all", action="store_true", help="list every missing timestamp")
    args = ap.parse_args()

    with open(os.path.join(ROOT, "beats.json"), encoding="utf-8") as fh:
        data = json.load(fh)
    beats = data["beats"]
    by_stamp = {b["timestamp"]: b for b in beats}

    todo = missing(beats)
    requeue = [b for b in queued(by_stamp) if b in todo or os.path.exists(os.path.join(IMG_DIR, b["file"]))]
    batch_ids = [b["timestamp"] for b in requeue]

    if args.ids or args.all:
        pick = todo if args.all else (requeue + [b for b in todo if b["timestamp"] not in batch_ids])[: args.count]
        print(" ".join(b["timestamp"] for b in pick))
        return 0

    if not todo and not requeue:
        print("all 205 frames rendered \u2014 nothing queued")
        return 0

    fresh = [b for b in todo if b["timestamp"] not in batch_ids]
    batch = (requeue + fresh)[: args.count]
    if not batch:
        print("nothing to do")
        return 0

    print(f"# {len(batch)} beats  |  {len(todo)} never rendered, "
          f"{len(requeue)} queued for re-render  (generator cap: 10 per turn)")
    if requeue:
        print("# re-render first: " + " ".join(b["timestamp"] for b in requeue))
    print(f"# target files: {' '.join(b['file'] for b in batch)}")
    for beat in batch:
        print(f"\n## {beat['file']}")
        print("PROMPT:")
        print(beat["image_prompt"])
    print(
        "\n# after rendering:  python3 tools/normalize_frames.py"
        " && python3 tools/sparse_check.py --write-queue",
        file=sys.stderr,
    )
    print("# clear finished entries from rerender.txt so they stop jumping the queue",
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
