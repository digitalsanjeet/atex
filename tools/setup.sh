#!/usr/bin/env bash
# Install the QC toolchain. Idempotent; safe to re-run.
#
# Needed because the sandbox filesystem for site-packages does not persist between
# turns, and because rapidocr-onnxruntime drags in non-headless opencv, which fails at
# import with "libGL.so.1: cannot open shared object file" in this container.
# opencv-python-headless must therefore be force-reinstalled AFTER rapidocr.
set -euo pipefail

pip install --quiet --break-system-packages Pillow numpy scipy rapidocr-onnxruntime
pip install --quiet --break-system-packages --force-reinstall --no-deps opencv-python-headless

python3 - <<'PY'
import PIL, numpy, scipy
print("core deps ok:", PIL.__version__, numpy.__version__, scipy.__version__)
try:
    from rapidocr_onnxruntime import RapidOCR
    RapidOCR()
    print("ocr ok (text_check.py --selftest will now run)")
except Exception as exc:
    raise SystemExit(f"ocr unavailable -> lettering gate disabled: {exc}")
PY
