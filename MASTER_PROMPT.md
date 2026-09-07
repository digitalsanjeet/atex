# MASTER PROMPT — 🔒 LOCKED

> **Status:** LOCKED · **Version:** v1.0 · **Locked on:** 2026-09-07
> **Rule of the lock:** this prompt is the fixed style spine for all artwork in this project.
> Never edit the locked block. Scene-specific details are **appended after** it (and only after it).

---

## The Locked Prompt (copy-paste ready)

```text
Clean 2D comic art style, detailed line art, flat cell shading, muted everyday color palette, warm ambient lighting, webcomic graphic novel aesthetic, semi-realistic character design, American man in his 30s, simple casual clothes, earthy brown and beige tones --ar 16:9 --niji 6
```

Raw file for tooling: [`prompts/master_prompt.txt`](prompts/master_prompt.txt)

---

## Prompt Anatomy

| # | Block | Tokens | Job |
|---|-------|--------|-----|
| 1 | **Art style** | `Clean 2D comic art style, detailed line art, flat cell shading` | Fixes the rendering pipeline — clean ink lines, flat colors, no painterly textures |
| 2 | **Color & light** | `muted everyday color palette, warm ambient lighting` | Muted, lived-in palette with warm fill light — no neon, no harsh contrast |
| 3 | **Aesthetic** | `webcomic graphic novel aesthetic, semi-realistic character design` | Puts it in the webcomic/graphic-novel lane; faces stay semi-real, not chibi or full anime |
| 4 | **Character** | `American man in his 30s, simple casual clothes` | The recurring protagonist — consistent age, build, wardrobe |
| 5 | **Palette anchor** | `earthy brown and beige tones` | Dominant color signature; keeps every panel in the same tonal family |
| 6 | **Parameters** | `--ar 16:9 --niji 6` | Widescreen frame (panel/cinematic) on Niji v6 |

## Parameters

| Flag | Value | Meaning |
|------|-------|---------|
| `--ar` | `16:9` | Widescreen aspect ratio — wide comic panels, cinematic framing |
| `--niji` | `6` | Niji Journey model v6 (SDXL-based, tuned for comic/anime looks) |

---

## How to Use (locked-prompt protocol)

1. **Start every generation with the locked block, untouched.**
2. **Append scene details after the palette anchor**, before the parameters:
   ```text
   Clean 2D comic art style, detailed line art, flat cell shading, muted everyday color palette, warm ambient lighting, webcomic graphic novel aesthetic, semi-realistic character design, American man in his 30s, simple casual clothes, earthy brown and beige tones, sitting on a park bench reading a newspaper, overcast afternoon --ar 16:9 --niji 6
   ```
3. **Negative prompts** (if your tool supports them) go separately — never mixed into the locked block.
4. **No reordering, no paraphrasing, no "synonym swaps".** Consistency beats cleverness.
5. Anything you must change → treat it as a **new version**: bump the version below, update the change log, keep the old version in the log.

## Change Log

| Date | Version | Change |
|------|---------|--------|
| 2026-09-07 | v1.0 | Prompt locked (initial) |
