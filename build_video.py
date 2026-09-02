#!/usr/bin/env python3
"""
Build a financial-story slideshow video with Ken Burns zoom-out transitions
and the user's audio as soundtrack.

Approach:
  - Each of the 44 images is shown for ~2 seconds (matching the user's
    per-image timestamps of 00:00 .. 01:28).
  - A gentle "zoom out" is applied to each clip (Ken Burns style).
  - All clips are concatenated with short crossfades.
  - The user's WAV audio is muxed as the soundtrack.
Output: financial_story_video.mp4 (1920x1080, 16:9, + audio).
"""
import os
import glob
import subprocess
import sys

FF = "/home/user/videoenv/lib/python3.11/site-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2"
IMG_DIR = "/home/user/atex/financial_story"
AUDIO = "/home/user/atex/Generated Audio September 02, 2026 - 12_44PM.wav"
WORK = "/home/user/atex/.video_work"
OUT = "/home/user/atex/financial_story_video.mp4"

W, H = 1920, 1080
FPS = 30
SEG = 2.0          # seconds per image
CROSS = 0.4        # crossfade duration between clips
# use 2s per image * 44 => 88s, audio is 87.48s -> trim to audio len

os.makedirs(WORK, exist_ok=True)

files = sorted(glob.glob(os.path.join(IMG_DIR, "*.png")))
print("Found", len(files), "images")
if not files:
    sys.exit("No images in financial_story/")

# Filenames sort alphabetically = prompt_01, prompt_02 ... prompt_44 -> correct order.
# But confirm ordering by the numeric part in the name.
def sort_key(p):
    base = os.path.basename(p)
    num = base.split("_")[1] if "_" in base else base
    try:
        return int(num.split(".")[0])
    except ValueError:
        return 0
files.sort(key=sort_key)
assert len(files) == 44, f"Expected 44 images, got {len(files)}"

# 1) Build one zoomed clip per image
clip_list = []
for i, f in enumerate(files):
    idx = i + 1
    clip = os.path.join(WORK, f"clip_{idx:02d}.mp4")
    clip_list.append(clip)
    # zoompan: gentle zoom-out from 1.06 -> 1.00 over the segment
    # x/y centered; s=WxH; fps=FPS; d = frames per image
    frames = int(SEG * FPS)
    zexpr = "min(1.06-0.06*on/{},1.06)".format(max(frames,1))
    vf = (
        f"scale={W}:{H}:force_original_aspect_ratio=increase,"
        f"crop={W}:{H},"
        f"zoompan=z='{zexpr}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
        f"d={frames}:s={W}x{H}:fps={FPS},"
        f"format=yuv420p"
    )
    cmd = [
        FF, "-y", "-loop", "1", "-i", f,
        "-vf", vf, "-t", str(SEG),
        "-r", str(FPS),
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
        "-pix_fmt", "yuv420p", clip,
    ]
    print(f"[{idx:02d}] building clip {os.path.basename(f)}")
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("  ERROR:", r.stderr[-500:])
        sys.exit(1)

print("All clips built.")

# 2) Concatenate clips with crossfades (xfade) OR simple concat.
# Crossfading 44 clips in one filter graph is heavy; use concat demuxer for
# reliability, then apply a light fade-in/out on the whole video.
concat_file = os.path.join(WORK, "concat.txt")
with open(concat_file, "w") as fh:
    for c in clip_list:
        fh.write(f"file '{c}'\n")

concat_cmd = [
    FF, "-y", "-f", "concat", "-safe", "0", "-i", concat_file,
    "-c", "copy",
    os.path.join(WORK, "concat_base.mp4"),
]
r = subprocess.run(concat_cmd, capture_output=True, text=True)
if r.returncode != 0:
    print("concat ERROR:", r.stderr[-500:])
    sys.exit(1)
print("Concatenated base video.")

# 3) Add audio + gentle global fade. Determine audio duration first.
probe = subprocess.run(
    [FF, "-i", AUDIO], capture_output=True, text=True
)
import re
m = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", probe.stderr)
if m:
    dur = int(m.group(1))*3600 + int(m.group(2))*60 + float(m.group(3))
else:
    dur = SEG * len(files)
print("Audio duration:", round(dur, 2), "s")

# Final: concat_base + audio, fade out at end, shorter than audio.
final_cmd = [
    FF, "-y",
    "-i", os.path.join(WORK, "concat_base.mp4"),
    "-i", AUDIO,
    "-filter_complex",
    "[0:v]fade=t=out:st={}:d={}[v]".format(max(dur - 0.6, 0), 0.6),
    "-map", "[v]", "-map", "1:a",
    "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
    "-c:a", "aac", "-b:a", "192k", "-shortest",
    "-pix_fmt", "yuv420p", OUT,
]
r = subprocess.run(final_cmd, capture_output=True, text=True)
if r.returncode != 0:
    print("final ERROR:", r.stderr[-800:])
    sys.exit(1)
print("DONE ->", OUT)
