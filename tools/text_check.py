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
    python3 tools/text_check.py --crops         # dump flagged regions for review
"""

import argparse
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG_DIR = os.path.join(ROOT, "images")
QUEUE = os.path.join(ROOT, "rerender.txt")
ADJUDICATED = os.path.join(ROOT, "qc_adjudicated.txt")


def load_adjudicated():
    """Return {stamp: {lowercased text}} for hits already reviewed and dismissed.

    OCR reads shelf hatching and squiggle "signage" as pseudo-words. Once a flag has been
    checked against the crop and found to be artwork rather than type, re-flagging it every
    scan would either re-queue a good frame forever or train everyone to ignore the gate.
    The decision is therefore recorded in a file and printed as skipped: auditable, not silent.
    """
    out = {}
    if os.path.exists(ADJUDICATED):
        with open(ADJUDICATED, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                stamp, _, text = line.partition("\t")
                out.setdefault(stamp.strip(), set()).add(text.strip().lower())
    return out

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


def glyph_evidence(path, box, min_frac):
    """Count separate letter-scale marks inside a detection box.

    Genuine type decomposes into many discrete glyphs of similar height. The abstract
    strokes we deliberately ask for instead ("signs must read as blank panels or
    horizontal strokes") are one or two continuous wavy lines. Without this, 04-17 was
    flagged as "annarc" for containing exactly the squiggle the prompt requested.
    """
    from PIL import Image
    import numpy as np
    from scipy import ndimage
    xs = [b[0] for b in box]; ys = [b[1] for b in box]
    im = Image.open(path).convert("L")
    a = np.asarray(im)
    x0, x1 = int(min(xs)), int(max(xs)); y0, y1 = int(min(ys)), int(max(ys))
    x0, y0 = max(x0 - 6, 0), max(y0 - 6, 0)
    x1, y1 = min(x1 + 6, a.shape[1]), min(y1 + 6, a.shape[0])
    sub = a[y0:y1, x0:x1] < 240
    if sub.sum() == 0:
        return 0, 0
    lab, n = ndimage.label(sub)
    band_h = max(y1 - y0, 1)
    heights = []
    for sl in ndimage.find_objects(lab):
        h = sl[0].stop - sl[0].start
        w = sl[1].stop - sl[1].start
        if h >= 0.45 * band_h and w <= 1.6 * h and h <= band_h:
            heights.append(h)
    if not heights:
        return 0, n
    return len(heights), n


def scan(path, min_conf, min_len, glyph_frac=0.45):
    """Return [(text, conf, height_px, box)] for detections that count as lettering."""
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
        glyphs, _total = glyph_evidence(path, box, glyph_frac)
        # require that most characters resolved as separate marks, i.e. it is type
        if glyphs < max(2, int(glyph_frac * letters)):
            continue
        hits.append((s, conf, h, [tuple(map(int, pt)) for pt in box]))
    return hits


def selftest(tmp="/tmp/txtcheck"):
    """Render a real-word frame and a squiggle frame; require flag / no-flag."""
    import subprocess
    from PIL import Image, ImageDraw, ImageFont
    os.makedirs(tmp, exist_ok=True)
    fpath = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    def panel(draw, box):
        draw.rectangle(box, outline=(20, 20, 20), width=5)
    # A: genuine lettering on a sign panel
    im = Image.new("RGB", (1920, 1080), (255, 255, 255))
    d = ImageDraw.Draw(im)
    f = ImageFont.truetype(fpath, 72) if os.path.exists(fpath) else ImageFont.load_default()
    panel(d, (620, 380, 1300, 560))
    d.text((680, 430), "DISCOUNT STORE", fill=(15, 15, 15), font=f)
    im.save(f"{tmp}/letters.png")
    # B: the abstract strokes the prompt asks for instead of lettering
    im2 = Image.new("RGB", (1920, 1080), (255, 255, 255))
    d2 = ImageDraw.Draw(im2)
    panel(d2, (620, 380, 1300, 560))
    for i, y in enumerate(range(425, 520, 26)):
        pts = [(680 + k * 9, y + (10 if (k + i) % 4 == 1 else -10 if (k + i) % 4 == 3 else 0))
               for k in range(68)]
        d2.line(pts, fill=(90, 90, 90), width=7)
    im2.save(f"{tmp}/squiggle.png")

    def run(p):
        out = subprocess.run([sys.executable, os.path.abspath(__file__), "--only",
                              os.path.basename(p).replace(".png", "")],
                             cwd=os.path.join(ROOT, ".."), capture_output=True, text=True)
        return out.stdout

    # run against the temp images directly
    a = scan(f"{tmp}/letters.png", 0.6, 2)
    b = scan(f"{tmp}/squiggle.png", 0.6, 2)
    print("letters.png  ->", a if a else "no lettering detected",
          "  EXPECTED: detected")
    print("squiggle.png ->", b if b else "no lettering detected",
          "  EXPECTED: none")
    ok = bool(a) and not bool(b)
    print("SELF-TEST", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--selftest", action="store_true", help="verify the detector on synthetic frames")
    ap.add_argument("--min-conf", type=float, default=0.6)
    ap.add_argument("--min-len", type=int, default=2)
    ap.add_argument("-v", "--verbose", action="store_true")
    ap.add_argument("--only", help="single timestamp, e.g. 03-44")
    ap.add_argument("--write-queue", action="store_true")
    ap.add_argument("--crops", action="store_true",
                    help="save the flagged regions to out/text_flags.png for review")
    args = ap.parse_args()

    if args.selftest:
        return selftest()

    if args.only:
        files = [f"{args.only}.png"]
    else:
        files = sorted(f for f in os.listdir(IMG_DIR) if f.endswith(".png"))
    if not files:
        print("nothing rendered yet")
        return 0

    adj = load_adjudicated()
    skipped = 0
    flagged = []
    crops = []
    from PIL import Image
    for name in files:
        hits = scan(os.path.join(IMG_DIR, name), args.min_conf, args.min_len)
        stamp = name.replace(".png", "")
        if stamp in adj:
            keep = [h for h in hits if h[0].strip().lower() not in adj[stamp]]
            skipped += len(hits) - len(keep)
            hits = keep
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
          f"(conf>={args.min_conf}, >={args.min_len} chars)"
          + (f"; {skipped} adjudicated hit(s) skipped" if skipped else ""))
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
