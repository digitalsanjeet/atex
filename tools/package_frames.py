#!/usr/bin/env python3
"""Package the rendered frames for handoff, and emit a per-file download list.

    python3 tools/package_frames.py

Writes, into out/ (which is gitignored, so re-run it whenever you need the artefacts):

  * atex_frames_205.zip - every frame, flat filenames, stored not compressed (PNGs do not
    shrink, and -0 keeps the pack under a second),
  * frames_urls.txt      - one raw.githubusercontent.com URL per line, in beat order, for
    `aria2c -i out/frames_urls.txt` or `xargs -n1 curl -O < ...` on another machine,
  * SHA256SUMS.txt       - so a transfer can be checked after it lands.
"""
import hashlib
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = "digitalsanjeet/atex"
BRANCH = os.environ.get("FRAMES_BRANCH", "arena/01a0a3e9-atex")


def main():
    import json

    beats = json.load(open(os.path.join(ROOT, "beats.json")))["beats"]
    names = [b["timestamp"] + ".png" for b in beats]
    missing = [n for n in names if not os.path.exists(os.path.join(ROOT, "images", n))]
    if missing:
        print("refusing to package, missing frames: %s" % ", ".join(missing[:10]))
        return 1

    out = os.path.join(ROOT, "out")
    os.makedirs(out, exist_ok=True)
    zip_path = os.path.join(out, "atex_frames_%d.zip" % len(names))
    if os.path.exists(zip_path):
        os.remove(zip_path)
    # -j flattens so the timestamps stay the filenames; -0 stores (PNG is already compressed)
    subprocess.check_call(
        ["zip", "-0", "-q", "-X", zip_path, "-j"]
        + [os.path.join("images", n) for n in names],
        cwd=ROOT,
    )

    urls = "https://raw.githubusercontent.com/%s/%s/images/%s"
    with open(os.path.join(out, "frames_urls.txt"), "w") as fh:
        for n in names:
            fh.write(urls % (REPO, BRANCH, n) + "\n")

    with open(os.path.join(out, "SHA256SUMS.txt"), "w") as fh:
        for n in names:
            h = hashlib.sha256(open(os.path.join(ROOT, "images", n), "rb").read()).hexdigest()
            fh.write("%s  images/%s\n" % (h, n))

    size = os.path.getsize(zip_path) / 1e6
    print("wrote out/atex_frames_%d.zip (%d files, %.1f MB)" % (len(names), len(names), size))
    print("wrote out/frames_urls.txt (%d links, branch %s)" % (len(names), BRANCH))
    print("wrote out/SHA256SUMS.txt")
    return 0


if __name__ == "__main__":
    sys.exit(main())
