#!/usr/bin/env python3
"""
Rebuild the financial-story video with TRUE frame-to-frame sync:
each image is shown for EXACTLY the duration of its audio segment
(from the user's script timestamps), with a gentle zoom-out (Ken Burns)
transition, and the user's WAV audio as the soundtrack.

Output: financial_story_video_synced.mp4 (1920x1080, 16:9, 30fps, + audio)
"""
import os
import glob
import re
import subprocess
import sys

FF = "/home/user/videoenv/lib/python3.11/site-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2"
IMG_DIR = "/home/user/atex/financial_story"
AUDIO = "/home/user/atex/Generated Audio September 02, 2026 - 12_44PM.wav"
WORK = "/home/user/atex/.video_work2"
OUT = "/home/user/atex/financial_story_video_synced.mp4"

W, H = 1920, 1080
FPS = 30

# ---------- Script timestamps (same order as images) ----------
script = [
    ("0:00","0:02"),("0:02","0:04"),("0:04","0:06"),("0:06","0:08"),
    ("0:08","0:10"),("0:10","0:12"),("0:12","0:14"),("0:14","0:16"),
    ("0:16","0:18"),("0:18","0:20"),("0:20","0:22"),("0:22","0:24"),
    ("0:24","0:26"),("0:26","0:28"),("0:28","0:30"),("0:30","0:32"),
    ("0:32","0:34"),("0:34","0:36"),("0:36","0:38"),("0:38","0:40"),
    ("0:40","0:42"),("0:42","0:44"),("0:44","0:46"),("0:46","0:48"),
    ("0:48","0:50"),("0:50","0:52"),("0:52","0:54"),("0:54","0:56"),
    ("0:56","0:58"),("0:58","1:00"),("1:00","1:02"),("1:02","1:04"),
    ("1:04","1:06"),("1:06","1:08"),("1:08","1:10"),("1:10","1:12"),
    ("1:12","1:14"),("1:14","1:16"),("1:16","1:18"),("1:18","1:20"),
    ("1:20","1:22"),("1:22","1:24"),("1:24","1:26"),("1:26","1:28"),
]

def ts(s):
    m, sec = s.split(":")
    return int(m) * 60 + float(sec)

durs = [ts(en) - ts(st) for st, en in script]
print("Segment durations:", [round(d,2) for d in durs])
print("Total script length:", round(sum(durs),2), "s")

os.makedirs(WORK, exist_ok=True)

files = sorted(glob.glob(os.path.join(IMG_DIR, "*.png")))
def sort_key(p):
    n = os.path.basename(p).split("_")[1].split(".")[0]
    return int(n)
files.sort(key=sort_key)
assert len(files) == 44, f"Expected 44 images, got {len(files)}"

# ---------- Build one zoom-out clip per image with EXACT duration ----------
clip_list = []
for i, f in enumerate(files):
    idx = i + 1
    dur = durs[i]
    frames = max(1, int(round(dur * FPS)))
    clip = os.path.join(WORK, f"clip_{idx:02d}.mp4")
    clip_list.append(clip)
    # Gentle zoom-out over the clip: 1.06 -> 1.00
    zexpr = "min(1.06-0.06*on/{},1.06)".format(max(frames, 1))
    vf = (
        f"scale={W}:{H}:force_original_aspect_ratio=increase,"
        f"crop={W}:{H},"
        f"zoompan=z='{zexpr}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
        f"d={frames}:s={W}x{H}:fps={FPS},"
        f"format=yuv420p"
    )
    cmd = [FF, "-y", "-loop", "1", "-i", f,
           "-vf", vf, "-t", str(dur), "-r", str(FPS),
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
           "-pix_fmt", "yuv420p", clip]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"[{idx:02d}] ERROR:", r.stderr[-500:]); sys.exit(1)
    print(f"[{idx:02d}] clip {dur:.2f}s {os.path.basename(f)}")

print("All clips built.")

# ---------- Concatenate (no timing shift -> frame-accurate) ----------
concat_file = os.path.join(WORK, "concat.txt")
with open(concat_file, "w") as fh:
    for c in clip_list:
        fh.write(f"file '{c}'\n")
concat_cmd = [FF, "-y", "-f", "concat", "-safe", "0", "-i", concat_file,
              "-c", "copy", os.path.join(WORK, "concat_base.mp4")]
r = subprocess.run(concat_cmd, capture_output=True, text=True)
if r.returncode != 0:
    print("concat ERROR:", r.stderr[-500:]); sys.exit(1)
print("Concatenated.")

# ---------- Mux audio (master clock = audio length) ----------
# Audio is ~87.48s; -shortest trims the very last image to match audio end.
final_cmd = [
    FF, "-y",
    "-i", os.path.join(WORK, "concat_base.mp4"),
    "-i", AUDIO,
    "-c:v", "copy",
    "-map", "0:v", "-map", "1:a",
    "-c:a", "aac", "-b:a", "192k", "-shortest",
    "-movflags", "+faststart", OUT,
]
r = subprocess.run(final_cmd, capture_output=True, text=True)
if r.returncode != 0:
    print("final ERROR:", r.stderr[-800:]); sys.exit(1)
print("DONE ->", OUT)
