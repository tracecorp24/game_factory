import React from "react";
import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
  Sequence
} from "remotion";

export interface ShotProps {
  shot_id: string;
  start_sec: number;
  end_sec: number;
  headline: string;
  subtext: string;
  visual_type: string;
  accent_color: string;
}

export interface VideoProps {
  title: string;
  shots: ShotProps[];
  ctaUrl?: string;
}

export const HookShot: React.FC<{ shot: ShotProps }> = ({ shot }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const scale = spring({
    frame,
    fps,
    config: { damping: 12, mass: 0.5 }
  });

  const pulse = Math.sin(frame / 6) * 0.05 + 1;

  return (
    <AbsoluteFill
      style={{
        backgroundColor: "#0F172A",
        justifyContent: "center",
        alignItems: "center",
        padding: 40,
        textAlign: "center"
      }}
    >
      <div
        style={{
          transform: `scale(${scale * pulse})`,
          padding: "24px 36px",
          background: `linear-gradient(135deg, ${shot.accent_color}, #B91C1C)`,
          borderRadius: 24,
          boxShadow: `0 20px 60px ${shot.accent_color}66`
        }}
      >
        <h1
          style={{
            fontSize: 56,
            color: "#FFFFFF",
            fontWeight: 900,
            textTransform: "uppercase",
            marginBottom: 16
          }}
        >
          {shot.headline}
        </h1>
        <p style={{ fontSize: 28, color: "#FEF08A", fontWeight: 700 }}>
          {shot.subtext}
        </p>
      </div>
    </AbsoluteFill>
  );
};

export const GameplayShot: React.FC<{ shot: ShotProps }> = ({ shot }) => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [0, 15], [0, 1], {
    extrapolateRight: "clamp"
  });

  return (
    <AbsoluteFill
      style={{
        backgroundColor: "#1E293B",
        justifyContent: "space-around",
        alignItems: "center",
        padding: 30,
        opacity
      }}
    >
      <div
        style={{
          background: "rgba(255,255,255,0.1)",
          padding: "16px 32px",
          borderRadius: 30,
          border: `2px solid ${shot.accent_color}`
        }}
      >
        <h2 style={{ fontSize: 36, color: "#FFFFFF", fontWeight: 800 }}>
          {shot.headline}
        </h2>
      </div>

      {/* Simulated 4x4 mini-grid preview */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(4, 90px)",
          gap: 16,
          background: "#0F172A",
          padding: 24,
          borderRadius: 24,
          boxShadow: "0 10px 40px rgba(0,0,0,0.5)"
        }}
      >
        {[
          "#EF4444", "#3B82F6", "#10B981", "#F59E0B",
          "#3B82F6", "#EF4444", "#8B5CF6", "#10B981",
          "#10B981", "#F59E0B", "#EF4444", "#3B82F6",
          "#8B5CF6", "#10B981", "#3B82F6", "#EF4444"
        ].map((color, idx) => (
          <div
            key={idx}
            style={{
              width: 90,
              height: 90,
              backgroundColor: color,
              borderRadius: 18,
              boxShadow: `0 4px 12px ${color}88`,
              transform: `scale(${1 + Math.sin((frame + idx * 4) / 8) * 0.08})`
            }}
          />
        ))}
      </div>

      <div
        style={{
          fontSize: 32,
          fontWeight: 800,
          color: shot.accent_color
        }}
      >
        {shot.subtext}
      </div>
    </AbsoluteFill>
  );
};

export const CTAShot: React.FC<{ shot: ShotProps }> = ({ shot }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const scale = spring({
    frame,
    fps,
    config: { damping: 10, mass: 0.6 }
  });

  return (
    <AbsoluteFill
      style={{
        backgroundColor: "#0B1329",
        justifyContent: "center",
        alignItems: "center",
        padding: 40,
        textAlign: "center"
      }}
    >
      <div style={{ transform: `scale(${scale})` }}>
        <h1
          style={{
            fontSize: 64,
            fontWeight: 900,
            color: "#FFFFFF",
            marginBottom: 20
          }}
        >
          {shot.headline}
        </h1>
        <p style={{ fontSize: 32, color: "#94A3B8", marginBottom: 40 }}>
          {shot.subtext}
        </p>

        <button
          style={{
            padding: "24px 64px",
            fontSize: 40,
            fontWeight: 900,
            background: "linear-gradient(135deg, #10B981, #059669)",
            color: "#FFFFFF",
            border: "none",
            borderRadius: 50,
            boxShadow: "0 10px 40px rgba(16,185,129,0.5)",
            cursor: "pointer"
          }}
        >
          INSTALL NOW
        </button>
      </div>
    </AbsoluteFill>
  );
};

export const CreativeForgeAdComposition: React.FC<VideoProps> = ({ shots }) => {
  const { fps } = useVideoConfig();

  return (
    <AbsoluteFill style={{ backgroundColor: "#000000" }}>
      {shots.map((shot) => {
        const fromFrame = Math.round(shot.start_sec * fps);
        const durationInFrames = Math.round((shot.end_sec - shot.start_sec) * fps);

        let Component = GameplayShot;
        if (shot.visual_type === "hook_animation") Component = HookShot;
        if (shot.visual_type === "cta_endcard") Component = CTAShot;

        return (
          <Sequence
            key={shot.shot_id}
            from={fromFrame}
            durationInFrames={durationInFrames}
          >
            <Component shot={shot} />
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};
