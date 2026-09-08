# Master Prompt Style Lock

## Base style suffix

Append this exact suffix to every image-generation prompt:

```text
2D flat cartoon animation style, simple round cartoon face character, dot eyes, warm cinematic amber lighting, semi-realistic background, clean line art, flat colors, 16:9 widescreen --ar 16:9 --v 6
```

## Lock rules

- This suffix is mandatory on every prompt.
- Keep the wording, punctuation, order, aspect ratio, and version flag unchanged.
- Add scene-specific instructions before the suffix.
- Do not remove or override the suffix unless the master prompt is explicitly updated.
- The normalized 128-image prompt pack is maintained in [`IMAGE_PROMPTS.md`](IMAGE_PROMPTS.md).
