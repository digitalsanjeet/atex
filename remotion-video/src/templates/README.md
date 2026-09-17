# 🎬 Mis Plantillas de Video (Video Templates)

Yahan 2 ready-made templates hain apne Spanish YouTube channel ke liye.
Dono ko **Remotion Studio ke left sidebar** me kholo, play karo, aur text badlo.

## 💰 Template 1: `FinanzasVideo`
- **Style:** Dark navy + gold, animated text slides, progress bar
- **Duration:** 20 sec (600 frames, 30fps) — 5 escenas × 4 sec
- **Use:** Finanzas / Dinero / Motivación videos

## 😱 Template 2: `TerrorVideo`
- **Style:** Black + blood red, flickering titles, typewriter narration
- **Duration:** 24 sec (720 frames, 30fps) — 3 casos × 8 sec
- **Use:** Terror / Misterio / Casos reales videos

---

## ✏️ Text kaise badlein? (bina code ke)

1. Studio me composition kholo (`FinanzasVideo` ya `TerrorVideo`)
2. Right side me **Props** panel me `scenes` dikhega
3. Wahan title/subtitle/text edit karo → preview turant update!
4. Permanent save ke liye `src/Root.tsx` me `defaultProps` edit karo

## ⏱️ Duration / scenes kaise badlein?

- Har scene ko **barabar time** milta hai = total frames ÷ scenes ki ginti
- Zyada scenes chahiye? `scenes` array me naya `{title, subtitle}` add karo
- Lamba video? `src/Root.tsx` me `durationInFrames` badhao (30 frames = 1 sec)

## 🎥 Render (MP4 banana) — apne PC par:

```bash
cd remotion-video
npx remotion render FinanzasVideo out/finanzas.mp4
npx remotion render TerrorVideo out/terror.mp4
```

## 🖼️ Thumbnail banana (1 frame as PNG):

```bash
npx remotion still FinanzasVideo out/thumb.png --frame=60
npx remotion still TerrorVideo out/thumb.png --frame=100
```

## 🔊 Voiceover add karna (next step):

Apni audio file ko `public/` folder me rakho (jaise `public/voz.mp3`),
phir template me `import {Audio} from "remotion"` karke `<Audio src={staticFile("voz.mp3")} />` add karo.
