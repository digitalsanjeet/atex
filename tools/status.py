#!/usr/bin/env python3
"""Report which beats have rendered frames and which are still missing."""

import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG_DIR = os.path.join(ROOT, "images")


def main():
    with open(os.path.join(ROOT, "beats.json"), encoding="utf-8") as fh:
        data = json.load(fh)

    done, missing = [], []
    for beat in data["beats"]:
        path = os.path.join(IMG_DIR, beat["file"])
        (done if os.path.exists(path) else missing).append(beat["timestamp"])

    total = len(data["beats"])
    print(f"{len(done)}/{total} frames rendered")
    if done:
        print(f"  done:    {done[0]} \u2192 {done[-1]}")
    if missing:
        print(f"  missing: {len(missing)}")
        print("  next up: " + ", ".join(missing[:10]))
        rest = missing[10:]
        if rest:
            print("  then:    " + ", ".join(rest))


if __name__ == "__main__":
    main()
