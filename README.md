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
  and avoids typos baked into 200+ renders. A lone `$` glyph on drawn banknotes is
  tolerated as an icon, not lettering.
- **Three distinct ways text leaks into a frame, and the clause for each.** The narration's own
  wording appears as signage when a beat reads like a slogan (`01-06` rendered "BUY CHEAP / SELL
  CHEAP" as a flow chart). Words from a scene description appear as diagram labels (`05-26`
  rendered "Rent / Payroll / Logistics" straight out of the `economics` lead). And the model
  invents explanatory captions that are in no input at all (`03-47` typeset "HIGH VOLUME/LOW
  MARGIN" on a blank-looking panel). The three are fixed independently in `TEXT_POLICY`; a frame
  that passes after all three clauses is the evidence they work, not a prior.
- **Text is verified by OCR, not by eye:** `tools/text_check.py` runs RapidOCR over every
  frame and flags any detected word. It exists because I had certified frames as
  lettering-free from contact-sheet thumbnails and OCR then found real lettering in 6 of
  57 ("SOUP" on a can, "TIN" on a box, "DISCOUNT STORE" and "BIG RETAILER" signs,
  "PAYROLL" in a ledger, "store" on a plaque). Two geometric detectors were tried first
  and both failed: connected components miss text inside a sign panel (letters merge with
  the outline), and row ink-run density fires on the drawings themselves. After filtering
  to alphabetic words, precision on that set was 6/6 true. Treat thumbnail review as
  insufficient; run the check.
- **Blank-panel instruction:** the root cause of leaked text is that the model fills any
  sign-shaped region with words, because that is what signs are for. Prompts now require
  signs, packaging, newspaper fronts and ledger pages to be blank panels or abstract
  horizontal strokes.
- **Subject scale (locked, measurable):** "lots of negative space" and "uncluttered" made
  the model shrink subjects into tiny vignettes that fail at 1080p, so the style text no
  longer asks for negative space in the abstract — it asks for clean space *around the
  subject*, plus a mandatory rule that the main subject claim 55–75% of frame height.
  `tools/sparse_check.py` verifies it numerically instead of by eye, and exempts scenes
  that legitimately span wide rather than tall (maps, street-level landscapes).
- **No trademarked marks (locked):** beats name real chains (Walmart, Target, CVS,
  McDonald's, Starbucks, Subway), so prompts ban logos, wordmarks, mascots and trade
  dress and ask for generic anonymous buildings instead — the narration carries the
  names. For a published video this is a legal requirement, not a style preference.
  `03-14` is the argument for it: "more locations than McDonald's and Starbucks" reads as
  a scale balancing a burger against a coffee cup on a US outline, which is clearer than
  any logo would be. Added after `03-19` was rendered, so the 48 frames from earlier turns
  relied on the `logo` term in the negative prompt alone — reviewed by eye, none carry marks.
- **Two-sided guard:** telling the model to draw the subject large can overcorrect into
  full-bleed artwork with no white ground (`01-30`, `00-29`). Prompts now also forbid
  filling the frame edge to edge, and QC flags ink coverage above 80% as OVERFULL.
  Both failure modes are therefore measured, not just the one I noticed first.
- **Threshold honesty:** the small-subject floor is 0.45 frame height, not the 0.55 first
  drafted — frames at 0.47–0.54 were verified good by eye, and a stricter bar burns render
  budget re-rolling fine frames while teaching everyone to ignore the warning. The contact
  sheet remains the final arbiter; `subjH` cannot tell a sparse frame from a deliberate
  wide diagram.

## Regenerating

```bash
python3 tools/build_manifest.py     # rebuild beats.json + prompts.md
python3 tools/normalize_frames.py   # force every frame to 1920x1080
python3 tools/sparse_check.py -v    # composition QC; --write-queue to queue offenders
python3 tools/text_check.py -v      # OCR QC for lettering; --write-queue, --crops
python3 tools/status.py             # what's rendered, what's missing (authoritative)
python3 tools/next.py               # exact prompts for the next batch of 10
python3 tools/contact_sheet.py      # labeled review grid of everything rendered so far
```

Per-batch loop: render the 10 from `next.py` → `normalize_frames.py` → **`pack_frames.py`**
→ `sparse_check.py` and `text_check.py` (both with `--write-queue`) → commit. `sparse_check
--write-queue` rewrites the queue and `text_check --write-queue` merges into it, so failures
jump ahead.

Pack runs BEFORE QC on purpose: quantization is lossy, so an unpacked frame is not the
artifact that ships. Skipping that order once let `00-44` pass the lettering gate, then get
re-flagged ("KAW", conf 0.63) after packing - an OCR hallucination off shelf hatching, but it
cost a turn to adjudicate. Verify what you commit, not what the generator handed back.
of new beats automatically.

QC deps: numpy, scipy, Pillow, rapidocr-onnxruntime + opencv-python-headless
(the headless build is required — the default opencv wheel needs libGL, absent here).

## Progress

`python3 tools/status.py` is always authoritative. The generator allows 10 image renders
per user turn, so frames accumulate in batches of 10 across turns.
