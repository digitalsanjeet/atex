# THE ECONOMICS OF OWNING A DOLLAR STORE — visual beats

Timestamped 16:9 illustration frames for the ~16:10 narration track
(`Imagine opening your (1).mp3`).

## Layout

| Path | What |
| --- | --- |
| `beats.json` | Machine-readable spec: all 205 beats with full expanded image prompt, negative prompt and camera note. |
| `prompts.md` | Human-readable mirror of the original prompt sheet (one section per timestamp). |
| `images/<mm-ss>.png` | Generated frames, 1920×1080, named by timestamp (e.g. `00-00.png`, `00-06.png`). **Not committed** — see `.gitignore`. |
| `tools/beats_source.py` | Source of truth: compact (timestamp, scene, narration beat) table + shared style constants. |
| `tools/build_manifest.py` | Regenerates `beats.json` and `prompts.md`. |
| `tools/normalize_frames.py` | Crops/rescales every frame in `images/` to an exact 1920×1080 16:9 frame (idempotent). |
| `tools/status.py` | Reports which beats have frames and which are still missing. |

## Conventions

- **Naming:** timestamp-based, `mm-ss.png`. The timestamp is the filename/header only —
  no timestamp metadata is embedded in the artwork.
- **Look:** clean 2D hand-drawn editorial illustration — thick black ink outlines,
  imperfect hand-sketched linework, subtle marker texture, flat muted pastel colors,
  simple geometric forms, white/simple background, lots of negative space, 1–3 main elements.
- **Avoid:** photorealism, 3D, cinematic lighting, glossy product photography, clutter,
  realistic faces, text-heavy infographics, watermarks, logos.
- **Camera:** medium-wide editorial framing, eye level, slight three-quarter perspective.
- **Framing:** every prompt ends with a 16:9 landscape directive; frames are then
  normalized to exactly 1920×1080.

## Regenerating

```bash
python3 tools/build_manifest.py     # rebuild beats.json + prompts.md
python3 tools/normalize_frames.py   # force every frame to 1920x1080
python3 tools/status.py             # what's rendered, what's missing
```

## Status

10 of 205 frames rendered (`00-00` → `00-44`). The image generator allows 10 renders
per turn, so the remaining 195 continue in batches of 10 across subsequent turns.
