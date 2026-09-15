#!/usr/bin/env python3
"""Regenerate beats.json and prompts.md from tools/beats_source.py."""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import beats_source as src  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    beats = src.build_beats()

    payload = {
        "title": src.TITLE,
        "beat_count": len(beats),
        "naming": "<mm-ss>.png",
        "style_suffix": src.STYLE_SUFFIX,
        "text_policy": src.TEXT_POLICY,
        "negative_prompt": src.NEGATIVE_PROMPT,
        "camera": src.CAMERA,
        "framing": src.FRAMING,
        "scale": src.SCALE,
        "scenes": src.SCENES,
        "beats": beats,
    }
    with open(os.path.join(ROOT, "beats.json"), "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

    lines = [
        f"# {src.TITLE} \u2014 ALL IMAGE PROMPTS",
        "",
        f"**Visual beats:** {len(beats)} \u2014 **Audio coverage:** timestamped script",
        "",
        "**Naming:** timestamp-based, e.g. `00-00.png`, `00-06.png`, `00-10.png`",
        "",
        "No separate TIMESTAMP metadata is included. The timestamp is used only as the "
        "image filename/header.",
        "",
        "---",
        "",
    ]
    for beat in beats:
        lines += [
            f"## {beat['timestamp']}",
            "",
            f"**IMAGE PROMPT:** {beat['image_prompt']}",
            "",
            f"**NEGATIVE PROMPT:** {beat['negative_prompt']}",
            "",
            f"**CAMERA:** {beat['camera']}",
            "",
        ]

    with open(os.path.join(ROOT, "prompts.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))

    print(f"wrote beats.json + prompts.md ({len(beats)} beats)")


if __name__ == "__main__":
    main()
