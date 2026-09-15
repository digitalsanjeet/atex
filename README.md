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
| `tools/sparse_check.py` | Composition QC: measures each frame's dominant subject size and flags ones too small for 1080p. |
| `tools/next.py` | Prints the exact prompts for the next batch, re-render queue first. |
| `rerender.txt` | Beats queued to be drawn again (one timestamp per line); `next.py` puts these ahead of new beats. |
| `out/contact_sheet.png` | Labeled review grid of everything rendered so far (not committed). |

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
- **No lettering (locked):** frames contain no text of any kind — no words, numbers,
  price tags with digits, captions, signage or speech bubbles. Narration and any
  on-screen type live in the edit, not in the artwork. This keeps every frame animatable
  and avoids typos baked into 200+ renders. Verified on `00-00`→`00-44`: all 10 came
  back clean. A lone `$` glyph on drawn banknotes is tolerated as an icon, not lettering.
- **Subject scale (locked, measurable):** "lots of negative space" and "uncluttered" made
  the model shrink subjects into tiny vignettes that fail at 1080p, so the style text no
  longer asks for negative space in the abstract — it asks for clean space *around the
  subject*, plus a mandatory rule that the main subject claim 55–75% of frame height.
  `tools/sparse_check.py` verifies it numerically instead of by eye, and exempts scenes
  that legitimately span wide rather than tall (maps, street-level landscapes).

## Regenerating

```bash
python3 tools/build_manifest.py     # rebuild beats.json + prompts.md
python3 tools/normalize_frames.py   # force every frame to 1920x1080
python3 tools/sparse_check.py -v    # composition QC; --write-queue to queue offenders
python3 tools/status.py             # what's rendered, what's missing (authoritative)
python3 tools/next.py               # exact prompts for the next batch of 10
python3 tools/contact_sheet.py      # labeled review grid of everything rendered so far
```

Per-batch loop: render the 10 from `next.py` → `normalize_frames.py` →
`sparse_check.py --write-queue` → delete re-rendered stamps from `rerender.txt` → commit.

## Progress

`python3 tools/status.py` is always authoritative. The generator allows 10 image renders
per user turn, so frames accumulate in batches of 10 across turns.
