#!/usr/bin/env python3
"""Detect burned-in lettering, which composition QC cannot see.

Why OCR and not geometry: the no-text policy is the project's strictest rule, but
sparse_check.py only measures composition, so 03-44 passed QC while carrying three
labels. Two geometric attempts failed in opposite directions -- connected components
miss text drawn inside a sign panel (the letters merge with the panel outline into one
oversized component), and row ink-run density fires on the drawings themselves, since a
busy map already has hundreds of high-run-count rows. Real recognition is the only
substrate that separates type from arbitrary detail.

Requires rapidocr-onnxruntime (pip install --break-system-packages
rapidocr-onnxruntime opencv-python-headless).

    python3 tools/text_check.py                 # scan every rendered frame
    python3 tools/text_check.py -v              # list per-frame detections
    python3 tools/text_check.py --write-queue   # append offenders to rerender.txt
    python3 tools/text_check.py --only 03-44    # single frame
"""

import argparse
import os
import sys

IMG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "images")
QUEUE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "rerender.txt")

_OCR = None


def ocr():
    global _OCR
    if _OCR is None:
        try:
            from rapidocr_onnxruntime import RapidOCR
        except ImportError as exc:  # pragma: no cover
            sys.exit(
                "need rapidocr-onnxruntime:\n"
                "  pip install --break-system-packages rapidocr-onnxruntime "
                "opencv-python-headless\n"
                f"({exc})"
            )
        _OCR = RapidOCR()
    return _OCR


def scan(path, min_conf, min_len):
    """Return [(text, conf, height_px)] for detections that count as lettering."""
    result, _ = ocr()(path)
    hits = []
    for box, text, conf in (result or []):
        try:
            conf = float(conf)
        except (TypeError, ValueError):
            continue
        ys = [p[1] for p in box]
        h = int(max(ys) - min(ys))
        s = str(text).strip()
        if conf < min_conf or not s.isascii():
            continue
        # OCR hallucinates digits and lone symbols on cross-hatching, shelf rows and
        # coin stacks, so a violation must be a word: >= --min-len ASCII letters.
        letters = sum(ch.isalpha() for ch in s)
        if letters < max(min_len, 3):
            continue
        hits.append((s, conf, h, [tuple(map(int, pt)) for pt in box]))
    return hits


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--min-conf", type=float, default=0.6)
    ap.add_argument("--min-len", type=int, default=2)
    ap.add_argument("-v", "--verbose", action="store_true")
    ap.add_argument("--only", help="single timestamp, e.g. 03-44")
    ap.add_argument("--write-queue", action="store_true")
    ap.add_argument("--crops", action="store_true",
                    help="save the flagged regions to out/text_flags.png for review")
    args = ap.parse_args()

    if args.only:
        files = [f"{args.only}.png"]
    else:
        files = sorted(f for f in os.listdir(IMG_DIR) if f.endswith(".png"))
    if not files:
        print("nothing rendered yet")
        return 0

    flagged = []
    crops = []
    from PIL import Image
    for name in files:
        hits = scan(os.path.join(IMG_DIR, name), args.min_conf, args.min_len)
        if args.crops:
            im = Image.open(os.path.join(IMG_DIR, name)).convert("RGB")
            for t, c, h, box in hits:
                xs = [b[0] for b in box]; ys = [b[1] for b in box]
                x0, x1 = max(min(xs) - 30, 0), min(max(xs) + 30, im.width)
                y0, y1 = max(min(ys) - 24, 0), min(max(ys) + 24, im.height)
                cr = im.crop((x0, y0, x1, y1))
                sc = max(2, min(6, 300 // max(cr.height, 1)))
                crops.append((f"{name.replace('.png','')}  {t} {c:.2f}",
                              cr.resize((cr.width * sc, cr.height * sc), Image.LANCZOS)))
        if hits:
            flagged.append((name, hits))
            print(f"{name.replace('.png',''):<10} LETTERING  " +
                  " | ".join(f"{t} ({c:.2f})" for t, c, _, _ in hits[:4]))
        elif args.verbose:
            print(f"{name.replace('.png',''):<10} clean")

    print(f"\n{len(files) - len(flagged)}/{len(files)} frames free of lettering "
          f"(conf>={args.min_conf}, >={args.min_len} chars)")
    if flagged:
        print("offenders: " + " ".join(n.replace(".png", "") for n, _ in flagged))
        if args.write_queue:
            stamps = [n.replace(".png", "") for n, _ in flagged]
            existing = []
            if os.path.exists(QUEUE):
                existing = [l.strip() for l in open(QUEUE) if l.strip()]
            merged = list(dict.fromkeys(stamps + existing))
            with open(QUEUE, "w", encoding="utf-8") as fh:
                fh.write("\n".join(merged) + "\n")
            print(f"wrote {QUEUE}: {len(merged)} beats queued")
    if args.crops and crops:
        out_dir = os.path.join(os.path.dirname(IMG_DIR), "out")
        os.makedirs(out_dir, exist_ok=True)
        gap, w = 12, max(c.width for _, c in crops)
        tot = sum(c.height for _, c in crops) + gap * (len(crops) + 1) + 20 * len(crops)
        sheet = Image.new("RGB", (w + 8, tot), (250, 250, 248))
        from PIL import ImageDraw
        d = ImageDraw.Draw(sheet)
        y = gap
        for label, c in crops:
            d.text((4, y), label, fill=(200, 30, 30)); y += 18
            sheet.paste(c, (4, y)); y += c.height + gap
        path = os.path.join(out_dir, "text_flags.png")
        sheet.save(path, optimize=True)
        print(f"wrote {path} ({sheet.size[0]}x{sheet.size[1]})")
    return 1 if flagged else 0


if __name__ == "__main__":
    sys.exit(main())
