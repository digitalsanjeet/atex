#!/usr/bin/env python3
"""Objective composition QC: flag frames whose main subject is too small.

The generator resolves "lots of negative space" vs "make the subject large"
inconsistently, so this measures it instead of eyeballing 205 frames.

Bounding-box extent is NOT the signal: a tiny figure plus a shelf near the top of
the frame spans the whole canvas. The honest proxy for "the subject is big enough"
is the largest contiguous run of drawn ink, i.e. the height of the single biggest
object in the frame.

Method
  1. mask everything darker than near-white (drawn ink)
  2. dilate a few px so one sketched object's strokes merge into one blob, while
     separate objects stay separate
  3. longest vertical run of ink over all columns   -> subj_h (fraction of height)
     longest horizontal run of ink over all rows     -> subj_w (fraction of width)

A frame passes when subj_h >= --min-subj-h (default 0.45) or spans >= --min-span-w.
The number is a coarse net for the egregious "tiny vignette in a white field" failure,
calibrated by eye against rendered frames -- out/contact_sheet.png stays the final
arbiter, since subjH alone cannot tell a small figure in a sparse frame from a
deliberately wide diagram.

    python3 tools/sparse_check.py                 # report offenders
    python3 tools/sparse_check.py -v              # every frame
    python3 tools/sparse_check.py --write-queue   # write rerender.txt for next.py
"""

import argparse
import os
import sys

import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG_DIR = os.path.join(ROOT, "images")
QUEUE = os.path.join(ROOT, "rerender.txt")


def longest_run_any(mask):
    """Longest contiguous True run along axis 1, for every row; returns (max, where)."""
    p = np.concatenate([np.zeros((mask.shape[0], 1), dtype=np.int64),
                        mask.astype(np.int64),
                        np.zeros((mask.shape[0], 1), dtype=np.int64)], axis=1)
    idx = np.arange(p.shape[1], dtype=np.int64)
    start = np.maximum.accumulate(np.where(p == 0, idx, 0), axis=1)
    run = idx[None, :] - start
    run = np.where(p == 1, run, 0)
    return int(run.max())


def metrics(path, white_thresh=242, dilate=4):
    with Image.open(path) as im:
        gray = np.asarray(im.convert("L"), dtype=np.int16)
    ink = gray < white_thresh
    if ink.sum() == 0:
        return 0.0, 0.0, 0.0
    # dilate by shifts (cheap, no scipy dependency) so strokes of one object merge
    dil = ink.copy()
    for _ in range(max(dilate, 0)):
        d = dil.copy()
        d[1:, :] |= dil[:-1, :]
        d[:-1, :] |= dil[1:, :]
        d[:, 1:] |= dil[:, :-1]
        d[:, :-1] |= dil[:, 1:]
        dil = d
    h, w = dil.shape
    # longest_run_any scans axis 1, so: vertical runs come from the transposed mask
    subj_h = longest_run_any(dil.T) / h
    subj_w = longest_run_any(dil) / w
    return dil.mean(), subj_h, subj_w


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    # 0.45 not 0.55: calibrated against visual review of 29 frames. Everything that
    # actually read as "tiny subject lost in white" measured <=0.42, while frames at
    # 0.47-0.54 (00-29, 01-30) looked correct on screen. A tighter bar spends render
    # budget re-rolling good frames and makes the metric cry wolf.
    ap.add_argument("--min-subj-h", type=float, default=0.45)
    ap.add_argument("--max-cover", type=float, default=0.80,
                    help="flag full-bleed frames: the style calls for a white ground")
    ap.add_argument("--min-span-w", type=float, default=0.75,
                    help="a subject spanning this much width passes even if short")
    ap.add_argument("--dilate", type=int, default=4)
    ap.add_argument("-v", "--verbose", action="store_true")
    ap.add_argument("--write-queue", action="store_true", help="write rerender.txt")
    args = ap.parse_args()

    files = sorted(f for f in os.listdir(IMG_DIR) if f.endswith(".png"))
    if not files:
        print("nothing rendered yet")
        return 0

    flagged, rows = [], []
    for name in files:
        cov, subj_h, subj_w = metrics(os.path.join(IMG_DIR, name), dilate=args.dilate)
        # A subject that spans nearly the full width is fine even when short: maps,
        # street-level landscapes and horizon scenes legitimately read that way.
        small = subj_h < args.min_subj_h and subj_w < args.min_span_w
        overfull = cov > args.max_cover
        rows.append((name, cov, subj_h, subj_w, small, overfull))
        if small or overfull:
            flagged.append(name)

    print(f"{'frame':<10} {'cover':>6} {'subjH':>6} {'subjW':>6}  verdict")
    for name, cov, subj_h, subj_w, small, overfull in rows:
        if small or overfull or args.verbose:
            verdict = "ok"
            if small:
                verdict = "SMALL SUBJECT"
            if overfull:
                verdict = "OVERFULL (no white ground)"
            if small and overfull:
                verdict = "SMALL + OVERFULL"
            print(f"{name.replace('.png',''):<10} {cov:>6.3f} {subj_h:>6.3f} {subj_w:>6.3f}  {verdict}")

    ok = len(files) - len(flagged)
    print(f"\n{ok}/{len(files)} pass; {len(flagged)} flagged "
          f"(small if subjH<{args.min_subj_h} and subjW<{args.min_span_w}; "
          f"overfull if cover>{args.max_cover})")
    # Write the queue unconditionally: a clean sweep must CLEAR stale entries too,
    # otherwise a beat that already passed gets re-rendered forever (costs a slot).
    stamps = [n.replace(".png", "") for n in flagged]
    if flagged:
        print("flagged: " + " ".join(stamps))
    if args.write_queue:
        with open(QUEUE, "w", encoding="utf-8") as fh:
            fh.write("\n".join(stamps) + ("\n" if stamps else ""))
        print(f"wrote {QUEUE} ({len(stamps)} beats queued ahead of new renders)")
    elif flagged:
        print("rerun with --write-queue to queue these for re-render")
    return 0


if __name__ == "__main__":
    sys.exit(main())
