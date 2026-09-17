# atex — Spanish YouTube Channel Video Factory 🇪🇸

React (Remotion) + Python se Spanish YouTube videos banao.

## Structure

| Folder | Kya hai |
|---|---|
| `remotion-video/` | Remotion project — edit + preview in Studio (`npm run dev`) |
| `remotion-video/src/templates/` | 💰 Finanzas + 😱 Terror video templates |
| `tools/render_mp4.py` | Bina browser ke seedha **MP4 render** karne wali script |
| `videos/` | Ready MP4 files (direct download ke liye) |
| `out/` | Bani hui MP4 files (git me nahi jati) |

## MP4 banana (easiest — yahi use karo)

```bash
pip3 install --target=.pylibs -r requirements.txt
python3 tools/render_mp4.py              # dono videos
python3 tools/render_mp4.py finanzas     # sirf FinanzasVideo.mp4
python3 tools/render_mp4.py terror       # sirf TerrorVideo.mp4
```

Files `out/` folder me milengi — seedha YouTube par upload karo.

## Remotion Studio (edit + preview)

```bash
cd remotion-video
npm install
npm run dev
```

> Note: `npx remotion render` ko Chrome chahiye (apne PC par chalega).
> Isliye yahan Python renderer diya hai jo kahin bhi MP4 bana deta hai.
> Text badalna ho to `remotion-video/src/Root.tsx` (Studio) aur
> `tools/render_mp4.py` (MP4) dono me same rakho.
