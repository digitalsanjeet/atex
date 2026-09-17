import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
  Sequence,
} from "remotion";

/* ------------------------------------------------------------------ */
/*  💰 FINANZAS TEMPLATE — "7 errores..." style educational video       */
/*  Edit text via props (sidebar) — no code change needed.             */
/* ------------------------------------------------------------------ */

export type FinanzasScene = {
  title: string;
  subtitle: string;
};

export type FinanzasVideoProps = {
  channelName: string;
  scenes: FinanzasScene[];
};

const GOLD = "#F5C044";
const BG_TOP = "#0B1B33";
const BG_BOTTOM = "#060D1A";

const FinanzasSceneView: React.FC<{
  scene: FinanzasScene;
  index: number;
  total: number;
  startFrame: number;
  sceneFrames: number;
}> = ({ scene, index, total, startFrame, sceneFrames }) => {
  const frame = useCurrentFrame() - startFrame;
  const { fps } = useVideoConfig();

  // Title entrance
  const titleEnter = spring({
    frame,
    fps,
    config: { damping: 100, stiffness: 200 },
  });
  const titleY = interpolate(titleEnter, [0, 1], [90, 0]);
  const titleOpacity = interpolate(titleEnter, [0, 1], [0, 1]);

  // Subtitle entrance (slightly delayed)
  const subEnter = spring({
    frame: frame - 12,
    fps,
    config: { damping: 100, stiffness: 160 },
  });
  const subOpacity = interpolate(subEnter, [0, 1], [0, 1]);
  const subY = interpolate(subEnter, [0, 1], [40, 0]);

  // Number badge pop-in
  const badgeScale = spring({
    frame: frame - 6,
    fps,
    config: { damping: 12, stiffness: 180 },
  });

  // Fade whole scene out at the end
  const fadeOut = interpolate(
    frame,
    [sceneFrames - 15, sceneFrames],
    [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
  );

  // Pulsing gold glow + drifting background symbol
  const glow = 0.45 + 0.15 * Math.sin(frame / 12);
  const driftX = interpolate(frame, [0, sceneFrames], [-40, 40]);

  return (
    <AbsoluteFill
      style={{
        opacity: fadeOut,
        background: `linear-gradient(160deg, ${BG_TOP} 0%, ${BG_BOTTOM} 70%)`,
        fontFamily:
          "system-ui, -apple-system, 'Segoe UI', Roboto, Arial, sans-serif",
      }}
    >
      {/* Giant drifting € symbol in background */}
      <AbsoluteFill
        style={{
          justifyContent: "center",
          alignItems: "center",
        }}
      >
        <div
          style={{
            fontSize: 900,
            fontWeight: 900,
            color: `rgba(245, 192, 68, 0.05)`,
            transform: `translateX(${driftX}px)`,
            lineHeight: 1,
            userSelect: "none",
          }}
        >
          €
        </div>
      </AbsoluteFill>

      {/* Gold glow blob */}
      <div
        style={{
          position: "absolute",
          top: -200,
          right: -150,
          width: 700,
          height: 700,
          borderRadius: "50%",
          background: `radial-gradient(circle, rgba(245,192,68,${glow}) 0%, rgba(245,192,68,0) 65%)`,
          filter: "blur(40px)",
        }}
      />

      {/* Scene counter */}
      <div
        style={{
          position: "absolute",
          top: 70,
          left: 110,
          display: "flex",
          alignItems: "center",
          gap: 24,
          transform: `scale(${badgeScale})`,
        }}
      >
        <div
          style={{
            background: GOLD,
            color: "#060D1A",
            fontWeight: 900,
            fontSize: 44,
            padding: "10px 34px",
            borderRadius: 999,
            letterSpacing: 2,
          }}
        >
          {String(index + 1).padStart(2, "0")}
        </div>
        <div
          style={{
            color: "rgba(255,255,255,0.55)",
            fontSize: 36,
            fontWeight: 600,
            letterSpacing: 3,
          }}
        >
          / {String(total).padStart(2, "0")}
        </div>
      </div>

      {/* Main text block */}
      <AbsoluteFill
        style={{
          justifyContent: "center",
          paddingLeft: 110,
          paddingRight: 110,
        }}
      >
        <div
          style={{
            opacity: titleOpacity,
            transform: `translateY(${titleY}px)`,
            color: "#FFFFFF",
            fontSize: 104,
            fontWeight: 900,
            lineHeight: 1.12,
            maxWidth: 1500,
          }}
        >
          {scene.title}
        </div>
        <div
          style={{
            marginTop: 36,
            height: 8,
            width: 220,
            borderRadius: 4,
            background: GOLD,
            opacity: subOpacity,
          }}
        />
        <div
          style={{
            marginTop: 36,
            opacity: subOpacity,
            transform: `translateY(${subY}px)`,
            color: GOLD,
            fontSize: 52,
            fontWeight: 500,
            lineHeight: 1.35,
            maxWidth: 1400,
          }}
        >
          {scene.subtitle}
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

export const FinanzasVideo: React.FC<FinanzasVideoProps> = ({
  channelName = "",
  scenes = [],
}) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();

  if (scenes.length === 0) {
    return (
      <AbsoluteFill
        style={{
          background: BG_BOTTOM,
          justifyContent: "center",
          alignItems: "center",
          color: "#fff",
          fontSize: 42,
          textAlign: "center",
          padding: 80,
          fontFamily:
            "system-ui, -apple-system, 'Segoe UI', Roboto, Arial, sans-serif",
        }}
      >
        Sin escenas — añade texto en el panel Props → scenes
      </AbsoluteFill>
    );
  }

  const total = scenes.length;
  const sceneFrames = Math.max(1, Math.floor(durationInFrames / total));

  const progress = interpolate(frame, [0, durationInFrames - 1], [0, 100], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill
      style={{
        background: BG_BOTTOM,
        fontFamily:
          "system-ui, -apple-system, 'Segoe UI', Roboto, Arial, sans-serif",
      }}
    >
      {scenes.map((scene, i) => (
        <Sequence
          key={i}
          from={i * sceneFrames}
          durationInFrames={sceneFrames}
          name={`Escena ${i + 1}`}
        >
          <FinanzasSceneView
            scene={scene}
            index={i}
            total={total}
            startFrame={i * sceneFrames}
            sceneFrames={sceneFrames}
          />
        </Sequence>
      ))}

      {/* Channel watermark */}
      <div
        style={{
          position: "absolute",
          bottom: 64,
          left: 110,
          color: "rgba(255,255,255,0.6)",
          fontSize: 30,
          fontWeight: 700,
          letterSpacing: 6,
        }}
      >
        {channelName}
      </div>

      {/* Progress bar */}
      <div
        style={{
          position: "absolute",
          bottom: 0,
          left: 0,
          right: 0,
          height: 14,
          background: "rgba(255,255,255,0.12)",
        }}
      >
        <div
          style={{
            width: `${progress}%`,
            height: "100%",
            background: `linear-gradient(90deg, #F5C044, #FFE29A)`,
          }}
        />
      </div>
    </AbsoluteFill>
  );
};
