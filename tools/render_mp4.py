#!/usr/bin/env python3
"""
Render REAL .mp4 files for the Spanish channel templates (no browser needed).

Matches the Remotion templates in remotion-video/src/templates/:
  - FinanzasVideo (navy + gold slides)
  - TerrorVideo   (black + blood-red horror)

Usage:
  python3 tools/render_mp4.py              # render BOTH videos to out/
  python3 tools/render_mp4.py finanzas     # only FinanzasVideo.mp4
  python3 tools/render_mp4.py terror       # only TerrorVideo.mp4

Content below mirrors remotion-video/src/Root.tsx defaultProps — keep in sync.
"""

import math
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "out"
sys.path.insert(0, str(ROOT / ".pylibs"))

from PIL import Image, ImageDraw, ImageFont  # noqa: E402

import imageio_ffmpeg  # noqa: E402

# ---------------------------------------------------------------- constants

W, H, FPS = 1920, 1080, 30
FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")
F_SANS_B = str(FONT_DIR / "DejaVuSans-Bold.ttf")
F_SANS = str(FONT_DIR / "DejaVuSans.ttf")
F_SERIF_B = str(FONT_DIR / "DejaVuSerif-Bold.ttf")
F_SERIF = str(FONT_DIR / "DejaVuSerif.ttf")

GOLD = (245, 192, 68)
NAVY_TOP = (11, 27, 51)
NAVY_BOTTOM = (6, 13, 26)
BLOOD = (193, 18, 31)
BONE = (237, 237, 237)

# ------------------------------------------------------------- content

FINANZAS_CHANNEL = "FINANZAS SIN MIEDO"
FINANZAS_SCENES = [
    ("Gasta menos de lo que ganas", "La regla #1 del dinero que el 90% ignora"),
    ("Elimina tus deudas caras", "La tarjeta cobra hasta 60% de interés al año"),
    ("Crea un fondo de emergencia", "Ahorra de 3 a 6 meses de gastos primero"),
    ("Invierte todos los meses", "El interés compuesto premia la constancia"),
    ("Haz crecer tus ingresos", "Ahorrar te protege. Ganar más te libera."),
]
FINANZAS_FRAMES = 600  # 20s

TERROR_CHANNEL = "RELATOS DE LA NOCHE"
TERROR_FOOTER = "USA AURICULARES"
TERROR_SCENES = [
    (
        "EL PUEBLO FANTASMA",
        "En 1987, los 300 habitantes de San Miguel abandonaron sus casas "
        "en una sola noche. Nadie sabe por qué. Las luces siguen encendidas.",
    ),
    (
        "LA LLAMADA",
        "Recibió una llamada de su propio número. Al contestar, escuchó su "
        "propia voz susurrando: no contestes.",
    ),
    (
        "ARCHIVO 13",
        "La cinta fue encontrada en una casa abandonada. Dura 4 minutos. "
        "Los últimos 30 segundos nadie ha podido explicarlos.",
    ),
]
TERROR_FRAMES = 720  # 24s

# ------------------------------------------------------------- helpers


def clamp(v, lo=0.0, hi=1.0):
    return max(lo, min(hi, v))


def lerp(a, b, t):
    return a + (b - a) * t


def ease_out(t):
    t = clamp(t)
    return 1 - (1 - t) ** 3


def interp(frame, start, end, out_start, out_end):
    if end == start:
        return out_end
    t = clamp((frame - start) / (end - start))
    return lerp(out_start, out_end, t)


def rand(seed: int) -> float:
    x = math.sin(seed * 12.9898) * 43758.5453
    return x - math.floor(x)


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap_text(text, font_obj, max_width):
    words, lines, line = text.split(" "), [], ""
    for w in words:
        trial = (line + " " + w).strip()
        if font_obj.getlength(trial) <= max_width or not line:
            line = trial
        else:
            lines.append(line)
            line = w
    if line:
        lines.append(line)
    return lines


def with_alpha(img_rgba, factor):
    """Return copy of RGBA image with global alpha scaled by factor (0..1)."""
    factor = clamp(factor)
    if factor >= 1.0:
        return img_rgba
    if factor <= 0.0:
        return Image.new("RGBA", img_rgba.size, (0, 0, 0, 0))
    r, g, b, a = img_rgba.split()
    a = a.point(lambda v: int(v * factor))
    out = img_rgba.copy()
    out.putalpha(a)
    return out


def radial_glow_sprite(size, color, power=2.0):
    """Small radial glow (RGBA) that can be resized/pasted. One-time cost."""
    s = 200
    glow = Image.new("L", (s, s), 0)
    px = glow.load()
    for y in range(s):
        for x in range(s):
            dx, dy = (x - s / 2) / (s / 2), (y - s / 2) / (s / 2)
            d = math.sqrt(dx * dx + dy * dy)
            px[x, y] = int(255 * clamp(1 - d) ** power)
    glow = glow.resize((size, size), Image.BILINEAR)
    rgba = Image.new("RGBA", (size, size), color + (0,))
    rgba.putalpha(glow)
    return rgba


def vertical_gradient(top, bottom):
    strip = Image.new("RGB", (1, H))
    px = strip.load()
    for y in range(H):
        t = y / max(1, H - 1)
        px[0, y] = tuple(int(lerp(a, b, t)) for a, b in zip(top, bottom))
    return strip.resize((W, H))


def ffmpeg_exe():
    return imageio_ffmpeg.get_ffmpeg_exe()


def has_x264():
    r = subprocess.run(
        [ffmpeg_exe(), "-hide_banner", "-h", "encoder=libx264"],
        capture_output=True,
    )
    return r.returncode == 0


def open_encoder(path: Path, codec: str):
    cmd = [
        ffmpeg_exe(), "-y", "-hide_banner", "-nostats", "-loglevel", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
        "-r", str(FPS), "-i", "-",
        "-c:v", codec,
        "-pix_fmt", "yuv420p",
        "-crf", "20", "-preset", "veryfast",
        "-movflags", "+faststart",
        str(path),
    ]
    return subprocess.Popen(cmd, stdin=subprocess.PIPE,
                            stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)


def encode_frames(path: Path, frames_fn, total: int, label: str):
    codec = "libx264" if has_x264() else "mpeg4"
    print(f"[{label}] codec={codec} frames={total} -> {path.name}", flush=True)
    proc = open_encoder(path, codec)
    assert proc.stdin is not None
    try:
        for i in range(total):
            frame = frames_fn(i)
            proc.stdin.write(frame.tobytes())
            if (i + 1) % 120 == 0 or i + 1 == total:
                print(f"[{label}] frame {i + 1}/{total}", flush=True)
    finally:
        assert proc.stdin is not None
        proc.stdin.close()
    proc.wait()
    err = proc.stderr.read() if proc.stderr else b""
    if proc.returncode != 0:
        print(err.decode()[-2000:])
        raise RuntimeError(f"ffmpeg failed for {path.name}")
    size_mb = path.stat().st_size / 1e6
    print(f"[{label}] DONE {path.name} ({size_mb:.1f} MB)", flush=True)


# ------------------------------------------------------------- FINANZAS

def render_finanzas():
    per = FINANZAS_FRAMES // len(FINANZAS_SCENES)
    bg_base = vertical_gradient(NAVY_TOP, NAVY_BOTTOM).convert("RGBA")
    glow = radial_glow_sprite(700, GOLD)
    glow_pos = (W - 550, -200)

    f_title = font(F_SANS_B, 104)
    f_sub = font(F_SANS, 52)
    f_badge = font(F_SANS_B, 44)
    f_small = font(F_SANS_B, 36)
    f_water = font(F_SANS_B, 30)
    f_euro = font(F_SANS_B, 900)

    total = len(FINANZAS_SCENES)

    def frame_at(n):
        idx = min(n // per, total - 1)
        f = n - idx * per
        title, subtitle = FINANZAS_SCENES[idx]

        img = bg_base.copy()

        # drifting giant euro
        drift = int(interp(f, 0, per, -40, 40))
        euro_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(euro_layer)
        d.text((W / 2 + drift, H / 2), "€", font=f_euro,
               anchor="mm", fill=GOLD + (13,))
        img = Image.alpha_composite(img, euro_layer)

        # pulsing glow
        pulse = 0.45 + 0.15 * math.sin(f / 12)
        img = Image.alpha_composite(
            img, _paste_at(with_alpha(glow, pulse / 0.6), glow_pos))

        # badge (fade+rise in)
        be = ease_out(f / 18)
        badge = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        db = ImageDraw.Draw(badge)
        num = str(idx + 1).zfill(2)
        nw = f_badge.getlength(num)
        bx, by = 110, int(70 + (1 - be) * 30)
        db.rounded_rectangle([bx, by, bx + nw + 68, by + 84],
                             radius=42, fill=GOLD + (255,))
        db.text((bx + 34, by + 42), num, font=f_badge,
                anchor="lm", fill=(6, 13, 26, 255))
        db.text((bx + nw + 92, by + 42), f"/ {str(total).zfill(2)}",
                font=f_small, anchor="lm", fill=(255, 255, 255, 140))
        img = Image.alpha_composite(img, with_alpha(badge, be))

        # title (slide up + fade)
        te = ease_out(f / 20)
        title_lines = wrap_text(title, f_title, 1500)
        title_only = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        dtt = ImageDraw.Draw(title_only)
        ty2 = int(300 + (1 - te) * 90)
        for ln in title_lines:
            dtt.text((110, ty2), ln, font=f_title,
                     fill=(255, 255, 255, 255))
            ty2 += 122
        img = Image.alpha_composite(img, with_alpha(title_only, te))

        # divider + subtitle (delayed fade, stable position)
        se = ease_out((f - 12) / 20)
        sub_lines = wrap_text(subtitle, f_sub, 1400)
        div_y = 300 + len(title_lines) * 122 + 10
        sub_only = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ds = ImageDraw.Draw(sub_only)
        ds.rounded_rectangle([110, div_y, 330, div_y + 8],
                             radius=4, fill=GOLD + (255,))
        sy = div_y + 44
        for ln in sub_lines:
            ds.text((110, sy), ln, font=f_sub, fill=GOLD + (255,))
            sy += 72
        img = Image.alpha_composite(img, with_alpha(sub_only, se))

        # watermark (separate layer so alpha blends correctly)
        wm = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(wm).text((110, H - 110), FINANZAS_CHANNEL,
                                font=f_water, fill=(255, 255, 255, 255))
        img = Image.alpha_composite(img, with_alpha(wm, 0.6))

        # progress bar
        p = interp(n, 0, FINANZAS_FRAMES - 1, 0, 1)
        track = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(track).rectangle([0, H - 14, W, H],
                                        fill=(255, 255, 255, 255))
        img = Image.alpha_composite(img, with_alpha(track, 0.12))
        bw = int(W * p)
        if bw > 0:
            fill_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            df = ImageDraw.Draw(fill_layer)
            for x in range(0, bw, 8):  # cheap horizontal gradient
                t = x / max(1, W - 1)
                c = (245, int(lerp(192, 226, t)), int(lerp(68, 154, t)))
                df.rectangle([x, H - 14, min(x + 8, bw), H], fill=c + (255,))
            img = Image.alpha_composite(img, fill_layer)

        # fade out at scene end
        fo = interp(f, per - 15, per, 1, 0)
        if fo < 1:
            black = Image.new("RGBA", (W, H), (0, 0, 0, 255))
            img = Image.blend(img, black, 1 - fo)

        return img.convert("RGB")

    return frame_at


def _paste_at(sprite, pos):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    layer.alpha_composite(sprite, pos)
    return layer


# ------------------------------------------------------------- TERROR

def render_terror():
    per = TERROR_FRAMES // len(TERROR_SCENES)
    red_glow = radial_glow_sprite(1000, BLOOD)

    # vignette overlay (built once)
    vw, vh = 480, 270
    vmask = Image.new("L", (vw, vh), 0)
    vpx = vmask.load()
    for y in range(vh):
        for x in range(vw):
            dx, dy = (x - vw / 2) / (vw / 2), (y - vh / 2) / (vh / 2)
            d = math.sqrt(dx * dx + dy * dy) / math.sqrt(2)
            vpx[x, y] = int(217 * clamp((d - 0.45) / 0.55) ** 1.5)
    vmask = vmask.resize((W, H), Image.BILINEAR)
    vignette = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    vignette.putalpha(vmask)

    f_title = font(F_SERIF_B, 92)
    f_text = font(F_SERIF, 54)
    f_head = font(F_SERIF_B, 30)
    f_foot = font(F_SERIF, 26)
    f_num = font(F_SERIF_B, 700)

    TRACKING = 10

    def spaced_width(text, font_obj):
        w = sum(font_obj.getlength(ch) for ch in text)
        return w + TRACKING * max(0, len(text) - 1)

    def draw_spaced(draw_obj, cx, y, text, font_obj, fill):
        total_w = spaced_width(text, font_obj)
        x = cx - total_w / 2
        for ch in text:
            draw_obj.text((x, y), ch, font=font_obj, fill=fill)
            x += font_obj.getlength(ch) + TRACKING

    # per-scene static layers (number + header + footer + sharp title + glow)
    scene_cache = []
    for idx, (title, text) in enumerate(TERROR_SCENES):
        # Base is opaque black; all text goes on separate layers and is
        # composited (ImageDraw overwrites RGBA pixels instead of blending).
        static = Image.new("RGBA", (W, H), (0, 0, 0, 255))
        num_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(num_layer).text(
            (W / 2, H / 2), str(idx + 1).zfill(2), font=f_num,
            anchor="mm", fill=BLOOD + (255,))
        static = Image.alpha_composite(static, with_alpha(num_layer, 0.07))
        head_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        draw_spaced(ImageDraw.Draw(head_layer), W / 2, 56, TERROR_CHANNEL,
                    f_head, BLOOD + (255,))
        static = Image.alpha_composite(static, with_alpha(head_layer, 0.9))
        foot_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(foot_layer).text(
            (W / 2, H - 100), TERROR_FOOTER, font=f_foot,
            anchor="ma", fill=BONE + (255,))
        static = Image.alpha_composite(static, with_alpha(foot_layer, 0.4))

        sharp = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        dsh = ImageDraw.Draw(sharp)
        draw_spaced(dsh, W / 2, 200, title, f_title, BLOOD + (255,))

        glow_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        dgl = ImageDraw.Draw(glow_layer)
        draw_spaced(dgl, W / 2, 200, title, f_title, (255, 60, 60, 255))
        glow_layer = glow_layer.filter(
            __import__("PIL.ImageFilter", fromlist=["GaussianBlur"])
            .GaussianBlur(25)
        )
        lines = wrap_text(text, f_text, 1400)
        full = "\n".join(lines)
        scene_cache.append((static, sharp, glow_layer, lines, full))

    cx = W // 2

    def frame_at(n):
        idx = min(n // per, len(TERROR_SCENES) - 1)
        f = n - idx * per
        static, sharp, glow_layer, _lines, full = scene_cache[idx]

        img = static.copy()

        # breathing red glow from below
        breath = 0.5 + 0.22 * math.sin(f / 18)
        img = Image.alpha_composite(
            img, _paste_at(with_alpha(red_glow, 0.35 * breath / 0.6),
                           (cx - 500, H - 350)))

        # flickering title
        r = rand(f + idx * 1000)
        flick = 0.25 if r > 0.88 else (0.6 if r > 0.8 else 1.0)
        fade_in = interp(f, 0, 20, 0, 1)
        a = fade_in * flick
        img = Image.alpha_composite(img, with_alpha(glow_layer, a * 0.8))
        img = Image.alpha_composite(img, with_alpha(sharp, a))

        # divider under title (fades with title)
        div = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(div).rectangle(
            [cx - 70, 340, cx + 70, 343], fill=BLOOD + (153,))
        img = Image.alpha_composite(img, with_alpha(div, fade_in))

        # typewriter narration
        total_chars = len(full)
        shown = int(interp(f, 25, 25 + total_chars * 1.4, 0, total_chars))
        partial = full[:shown]
        dt = ImageDraw.Draw(img)
        dt.multiline_text((cx, 400), partial or " ", font=f_text,
                          anchor="ma", align="center", fill=BONE + (255,))
        # blinking cursor (red bar after last char)
        if shown < total_chars and (f // 12) % 2 == 0:
            last = partial.split("\n")[-1] if partial else ""
            lw = f_text.getlength(last)
            dt.rectangle([cx + lw / 2 + 8, 404 + 54 * partial.count("\n"),
                          cx + lw / 2 + 26,
                          404 + 54 * partial.count("\n") + 62],
                         fill=BLOOD + (255,))

        # vignette
        img = Image.alpha_composite(img, vignette)

        # red flash at scene start
        if f < 4:
            flash = Image.new(
                "RGBA", (W, H),
                BLOOD + (int(255 * 0.35 * (1 - f / 4)),))
            img = Image.alpha_composite(img, flash)

        # fade out at scene end
        fo = interp(f, per - 20, per, 1, 0)
        if fo < 1:
            black = Image.new("RGBA", (W, H), (0, 0, 0, 255))
            img = Image.blend(img, black, 1 - fo)

        return img.convert("RGB")

    return frame_at


# ------------------------------------------------------------- main

def main():
    OUT_DIR.mkdir(exist_ok=True)
    which = sys.argv[1].lower() if len(sys.argv) > 1 else "both"

    if which in ("both", "finanzas"):
        encode_frames(OUT_DIR / "FinanzasVideo.mp4", render_finanzas(),
                      FINANZAS_FRAMES, "FINANZAS")
    if which in ("both", "terror"):
        encode_frames(OUT_DIR / "TerrorVideo.mp4", render_terror(),
                      TERROR_FRAMES, "TERROR")
    print("All done. Files in out/")


if __name__ == "__main__":
    main()
