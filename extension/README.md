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
- **Google Flow** — tumhare khule hue `labs.google/fx/tools/flow` tab par automation (details niche)
- **Pollinations** — free, koi API key nahi. Default.
- **OpenAI Images** — apni API key + model (`gpt-image-1`). Key sirf local `chrome.storage` me save hoti hai.
- **Custom URL template** — koi bhi image API:
  `https://example.com/img?q={prompt}&w={width}&h={height}`
  Placeholders: `{prompt}` `{width}` `{height}` `{seed}` `{index}`

## Notes
- Har image par 3 retry hote hain (backoff ke saath).
- Files serial order me name hoti hain, isliye folder me sorting exact prompt order me rehti hai.
- Icons `icons/` me hain; apni branding chaho to replace kar do.


## Google Flow Mode (labs.google)
Extension me daale hue prompts seedhe Google Flow page par type hokar generate hote hain, aur result images serial number ke saath download ho jati hain.

### Steps
1. Chrome me `https://labs.google/fx/tools/flow` kholo aur Google account se sign in karo
2. Ek **project ke andar** jao jahan niche prompt bar dikhta ho
3. Flow me generation type **Image** select kar lo (aur model/aspect ratio jo chahiye)
4. Extension popup kholo → Advanced → Provider = **Google Flow**
5. Master prompt + prompts list bharo → **Start**

### Kaise kaam karta hai
- Har prompt Flow ke prompt box me type hota hai (React-safe native setter se)
- **Generate** button auto-detect hokar click hota hai (na mile to Enter key fallback)
- Nayi images DOM me aane ka intezar hota hai (default 180s timeout)
- Images fetch karke serial name se download: `image-001.png`, `image-002.png`, ...
- Agar ek prompt se multiple images chahiye to **Images / prompt** badhao → `image-001-a.png`, `image-001-b.png`

### Agar auto-detect fail ho
Flow ka UI badalta rehta hai. Us case me:
1. Flow page par prompt box par right-click → Inspect
2. Element ka CSS selector copy karo (e.g. `textarea[placeholder*="prompt"]`)
3. Extension me **Prompt box selector** / **Generate button selector** me paste kar do

### Notes
- Flow tab band mat karo aur us par kaam chalu rehne do; tab background me ho to bhi chalta hai
- Delay minimum 1500ms auto set hota hai taki Flow settle ho sake
- Google ke rate limits/credits lagu rehte hain — bahut fast mat chalao
- Ye unofficial automation hai, Google se affiliated nahi
