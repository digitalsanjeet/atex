#!/usr/bin/env python3
"""Turn beats.json into an ffmpeg concat list so the frames land on the narration clock.

Frames are named by the mm-ss they belong at, and the beats are unevenly spaced, so the
edit is a duration problem, not a manual one. Each frame is held until the next beat, and
the last frame is extended to the end of the narration audio.

    python3 tools/build_edit_list.py            # writes out/frames.txt + out/edit_list.csv
    ffmpeg -f concat -safe 0 -i out/frames.txt -i "Imagine opening your (1).mp3" \
           -vsync vfr -pix_fmt yuv420p -crf 18 out/video.mp4
"""
import csv
import json
import os
import sys


def secs(ts):
    m, s = ts.split("-")
    return int(m) * 60 + int(s)


def audio_seconds(path):
    try:
        import subprocess

        out = subprocess.check_output(
            [
                "ffprobe", "-v", "error", "-show_entries", "format=duration",
                "-of", "default=nw=1:nk=1", path,
            ],
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))) or ".",
        )
        return float(out.decode().strip())
    except Exception:
        return None


def main():
    tail = 10.0
    for i, a in enumerate(sys.argv):
        if a == "--tail":
            tail = float(sys.argv[i + 1])
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data = json.load(open(os.path.join(root, "beats.json")))
    beats = data["beats"]
    ts = [b["timestamp"] for b in beats]
    start = [secs(t) for t in ts]
    end_of_audio = audio_seconds(os.path.join(root, "Imagine opening your (1).mp3"))
    final = end_of_audio if end_of_audio else start[-1] + tail

    out_dir = os.path.join(root, "out")
    os.makedirs(out_dir, exist_ok=True)
    lines = []
    rows = []
    for i, t in enumerate(ts):
        dur = (start[i + 1] if i + 1 < len(ts) else final) - start[i]
        dur = max(dur, 0.5)
        rows.append((t, start[i], round(dur, 2)))
        lines.append("file '../images/%s.png'" % t)
        lines.append("duration %.2f" % dur)
    # ffmpeg concat needs the last image emitted once more without a duration
    lines.append("file '../images/%s.png'" % ts[-1])

    with open(os.path.join(out_dir, "frames.txt"), "w") as fh:
        fh.write("\n".join(lines) + "\n")
    with open(os.path.join(out_dir, "edit_list.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["timestamp", "start_seconds", "hold_seconds"])
        w.writerows(rows)

    total = sum(r[2] for r in rows)
    print("wrote out/frames.txt and out/edit_list.csv")
    print("%d frames, total %.1fs (%.2f min)" % (len(rows), total, total / 60))
    print("audio: %s" % ("%.1fs" % end_of_audio if end_of_audio
                          else "not probed (no ffprobe) - last frame held %.0fs, pass --tail to change" % tail))
    short = final - total
    if abs(short) > 1:
        print("WARNING: total and audio differ by %.1fs" % short)
    missing = [t for t in ts if not os.path.exists(os.path.join(root, "images", t + ".png"))]
    if missing:
        print("MISSING IMAGES: %s" % ", ".join(missing))
        return 1
    print("all frames present")
    return 0


if __name__ == "__main__":
    sys.exit(main())
