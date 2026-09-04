# Bulk Image Prompt Downloader (Chrome Extension)

Bulk me prompts daalo → har prompt se image generate hogi → serial number ke saath auto-download.

## Install (Load unpacked)
1. Chrome me `chrome://extensions` kholo
2. Top-right **Developer mode** ON karo
3. **Load unpacked** → is `extension/` folder ko select karo
4. Toolbar me extension icon pin kar lo

## Master Prompt
Top wale **Master prompt** box me ek common style/quality text daalo — wo har line par apply hoga.

- **`{prompt}` ke saath:** `photo of {prompt}, 35mm, cinematic` → line `a cat` → `photo of a cat, 35mm, cinematic`
- **`{prompt}` ke bina:** Position dropdown se decide karo
  - *Suffix*: `a cat, 8k, cinematic lighting`
  - *Prefix*: `8k, cinematic lighting, a cat`
- **Enable** checkbox se master prompt temporarily band kar sakte ho
- Niche live **Preview** dikhata hai ki pehla final prompt kaisa banega

## Use
1. (Optional) Master prompt set karo
2. Textarea me har line par ek prompt likho
3. **File prefix**, **Start no.**, **Digits** set karo
   - prefix `image`, start `1`, digits `3` → `image-001.png`, `image-002.png`, ...
4. **Download folder** (Downloads ke andar subfolder), **Delay** (rate-limit se bachne ke liye)
5. **Start** dabao — progress bar aur log niche dikhega. **Stop** se beech me rok sakte ho.

## Providers (Advanced section)
- **Pollinations** — free, koi API key nahi. Default.
- **OpenAI Images** — apni API key + model (`gpt-image-1`). Key sirf local `chrome.storage` me save hoti hai.
- **Custom URL template** — koi bhi image API:
  `https://example.com/img?q={prompt}&w={width}&h={height}`
  Placeholders: `{prompt}` `{width}` `{height}` `{seed}` `{index}`

## Notes
- Har image par 3 retry hote hain (backoff ke saath).
- Files serial order me name hoti hain, isliye folder me sorting exact prompt order me rehti hai.
- Icons `icons/` me hain; apni branding chaho to replace kar do.
