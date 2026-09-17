import {
  AbsoluteFill,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
  Sequence,
} from "remotion";

/* ------------------------------------------------------------------ */
/*  😱 TERROR / MISTERIO TEMPLATE — dark horror narration style        */
/*  Edit text via props (sidebar) — no code change needed.             */
/* ------------------------------------------------------------------ */

export type TerrorScene = {
  title: string;
  text: string;
};

export type TerrorVideoProps = {
  channelName: string;
  footerText: string;
  scenes: TerrorScene[];
};

const BLOOD = "#C1121F";
const BONE = "#EDEDED";

/** Deterministic pseudo-random from frame number (for flicker). */
const rand = (seed: number) => {
  const x = Math.sin(seed * 12.9898) * 43758.5453;
  return x - Math.floor(x);
};

const TerrorSceneView: React.FC<{
  scene: TerrorScene;
  index: number;
  startFrame: number;
  sceneFrames: number;
}> = ({ scene, index, startFrame, sceneFrames }) => {
  const frame = useCurrentFrame() - startFrame;

  // Title flicker (like a dying neon sign)
  const r = rand(frame + index * 1000);
  const flicker = r > 0.88 ? 0.25 : r > 0.8 ? 0.6 : 1;
  const titleOpacity = interpolate(frame, [0, 20], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Typewriter narration
  const charsToShow = Math.floor(
    interpolate(frame, [25, 25 + scene.text.length * 1.4], [0, scene.text.length], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    }),
  );
  const visibleText = scene.text.slice(0, charsToShow);
  const cursorVisible = Math.floor(frame / 12) % 2 === 0 && charsToShow < scene.text.length;

  // Red flash at scene start
  const flash = interpolate(frame, [0, 4], [0.35, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Fade out at end
  const fadeOut = interpolate(
    frame,
    [sceneFrames - 20, sceneFrames],
    [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
  );

  // Slow zoom (dread effect) + breathing red glow
  const zoom = interpolate(frame, [0, sceneFrames], [1, 1.07]);
  const breath = 0.5 + 0.22 * Math.sin(frame / 18);

  return (
    <AbsoluteFill
      style={{
        opacity: fadeOut,
        background: "#000000",
        fontFamily: "Georgia, 'Times New Roman', serif",
      }}
    >
      {/* Zooming background layer */}
      <AbsoluteFill
        style={{
          transform: `scale(${zoom})`,
          justifyContent: "center",
          alignItems: "center",
        }}
      >
        {/* Giant faint scene number */}
        <div
          style={{
            position: "absolute",
            fontSize: 700,
            fontWeight: 900,
            color: "rgba(193, 18, 31, 0.07)",
            lineHeight: 1,
            userSelect: "none",
          }}
        >
          {String(index + 1).padStart(2, "0")}
        </div>
      </AbsoluteFill>

      {/* Breathing blood-red glow from below */}
      <div
        style={{
          position: "absolute",
          bottom: -250,
          left: "50%",
          marginLeft: -500,
          width: 1000,
          height: 600,
          borderRadius: "50%",
          background: `radial-gradient(ellipse, rgba(193,18,31,${0.35 * breath}) 0%, rgba(193,18,31,0) 65%)`,
          filter: "blur(30px)",
        }}
      />

      {/* Main text */}
      <AbsoluteFill
        style={{
          justifyContent: "center",
          alignItems: "center",
          paddingLeft: 160,
          paddingRight: 160,
          textAlign: "center",
        }}
      >
        <div
          style={{
            opacity: titleOpacity * flicker,
            color: BLOOD,
            fontSize: 92,
            fontWeight: 900,
            letterSpacing: 10,
            textShadow: "0 0 60px rgba(193,18,31,0.8)",
            lineHeight: 1.15,
          }}
        >
          {scene.title}
        </div>
        <div
          style={{
            marginTop: 28,
            width: 140,
            height: 3,
            background: "rgba(193,18,31,0.6)",
          }}
        />
        <div
          style={{
            marginTop: 44,
            color: BONE,
            fontSize: 54,
            fontStyle: "italic",
            lineHeight: 1.5,
            minHeight: 320,
            maxWidth: 1400,
            textShadow: "0 2px 20px rgba(0,0,0,0.9)",
          }}
        >
          {visibleText}
          <span style={{ opacity: cursorVisible ? 1 : 0, color: BLOOD }}>▌</span>
        </div>
      </AbsoluteFill>

      {/* Vignette */}
      <AbsoluteFill
        style={{
          background:
            "radial-gradient(ellipse at center, rgba(0,0,0,0) 40%, rgba(0,0,0,0.85) 100%)",
          pointerEvents: "none",
        }}
      />

      {/* Scene-start red flash */}
      <AbsoluteFill
        style={{
          background: `rgba(193, 18, 31, ${flash})`,
          pointerEvents: "none",
        }}
      />
    </AbsoluteFill>
  );
};

export const TerrorVideo: React.FC<TerrorVideoProps> = ({
  channelName = "",
  footerText = "",
  scenes = [],
}) => {
  const { durationInFrames } = useVideoConfig();

  if (scenes.length === 0) {
    return (
      <AbsoluteFill
        style={{
          background: "#000",
          justifyContent: "center",
          alignItems: "center",
          color: "#EDEDED",
          fontSize: 42,
          textAlign: "center",
          padding: 80,
          fontFamily: "Georgia, 'Times New Roman', serif",
        }}
      >
        Sin escenas — añade texto en el panel Props → scenes
      </AbsoluteFill>
    );
  }

  const total = scenes.length;
  const sceneFrames = Math.max(1, Math.floor(durationInFrames / total));

  return (
    <AbsoluteFill
      style={{
        background: "#000",
        fontFamily: "Georgia, 'Times New Roman', serif",
      }}
    >
      {scenes.map((scene, i) => (
        <Sequence
          key={i}
          from={i * sceneFrames}
          durationInFrames={sceneFrames}
          name={`Caso ${i + 1}`}
        >
          <TerrorSceneView
            scene={scene}
            index={i}
            startFrame={i * sceneFrames}
            sceneFrames={sceneFrames}
          />
        </Sequence>
      ))}

      {/* Channel header */}
      <div
        style={{
          position: "absolute",
          top: 56,
          left: 0,
          right: 0,
          textAlign: "center",
          color: "rgba(193,18,31,0.9)",
          fontSize: 30,
          letterSpacing: 14,
          fontWeight: 700,
        }}
      >
        {channelName}
      </div>

      {/* Footer */}
      <div
        style={{
          position: "absolute",
          bottom: 54,
          left: 0,
          right: 0,
          textAlign: "center",
          color: "rgba(237,237,237,0.4)",
          fontSize: 26,
          letterSpacing: 6,
        }}
      >
        {footerText}
      </div>
    </AbsoluteFill>
  );
};
