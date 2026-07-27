import React from "react";
import {
  AbsoluteFill,
  Composition,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

type Props = Record<string, never>;

const slides = [
  {
    kicker: "Research Trend Brief",
    title: "AI Readiness in Higher Education",
    subtitle: "Top-tier journals and conferences point to a fast-forming research cluster around AI literacy, faculty readiness, and institutional governance.",
    accent: "#60a5fa",
    bullets: ["AI literacy + digital competence", "Generative AI adoption", "Curriculum and assessment redesign"],
  },
  {
    kicker: "Trend 1",
    title: "Readiness is converging with AI literacy",
    subtitle: "The field rarely treats readiness as a single construct. It is operationalized through literacy, self-efficacy, competence, ethics, and adoption capability.",
    accent: "#34d399",
    bullets: ["AI literacy scales", "Teacher digital competence", "Responsible GenAI use"],
  },
  {
    kicker: "Trend 2",
    title: "The unit of analysis is expanding",
    subtitle: "Studies are moving from individual student attitudes toward multi-level readiness across students, faculty, programs, and institutions.",
    accent: "#f59e0b",
    bullets: ["Student readiness", "Faculty readiness", "Institutional readiness"],
  },
  {
    kicker: "Top-tier journal venues",
    title: "Where the conversation is happening",
    subtitle: "Search beyond the exact phrase “AI readiness.” Use AI literacy, AI competence, teacher readiness, GenAI adoption, and higher education governance.",
    accent: "#a78bfa",
    bullets: ["Computers & Education", "BJET / ETR&D", "IJETHE / IJAIEd / npj Science of Learning"],
  },
  {
    kicker: "Conference map",
    title: "Conference evidence is dispersed",
    subtitle: "Readiness appears indirectly through AI literacy, learning analytics, HCI, educational data mining, and information systems adoption.",
    accent: "#fb7185",
    bullets: ["AIED · LAK · EDM", "CHI · CSCW", "ICIS · ECIS · AOM/AMLE"],
  },
  {
    kicker: "Research gaps",
    title: "Four openings for publishable work",
    subtitle: "The opportunity is strongest where readiness is modeled as a multi-level capability rather than a simple attitude or intention measure.",
    accent: "#22d3ee",
    bullets: ["Conceptual overlap remains unresolved", "Institution-level measures are scarce", "Outcomes beyond intention are under-tested"],
  },
  {
    kicker: "Business school angle",
    title: "A distinctive management education opportunity",
    subtitle: "Business schools can connect AI readiness to responsible decision-making, critical thinking, career preparedness, and managerial judgment.",
    accent: "#f97316",
    bullets: ["Global MBA readiness", "Responsible GenAI workflows", "Critical evaluation behavior"],
  },
  {
    kicker: "Working model",
    title: "From readiness to responsible AI behavior",
    subtitle: "A practical model links AI literacy, self-efficacy, anxiety, and institutional support to responsible use, critical evaluation, and career readiness.",
    accent: "#10b981",
    bullets: ["Inputs: literacy, self-efficacy, support", "Mediators: responsible use + critical evaluation", "Outcomes: learning, employability, decision confidence"],
  },
];

const words = ["AI literacy", "Faculty", "Students", "Institution", "Governance", "Ethics", "GenAI", "Assessment", "Curriculum", "Readiness"];

const slideDuration = 150;
const fps = 30;

const Background: React.FC<{ accent: string }> = ({ accent }) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const drift = interpolate(frame, [0, durationInFrames], [0, 80]);
  return (
    <AbsoluteFill style={{ background: "linear-gradient(135deg,#020617 0%,#0f172a 55%,#111827 100%)", overflow: "hidden" }}>
      <div style={{ position: "absolute", width: 640, height: 640, borderRadius: 999, background: accent, opacity: 0.18, filter: "blur(120px)", right: -160 + drift, top: -180 }} />
      <div style={{ position: "absolute", width: 520, height: 520, borderRadius: 999, background: "#38bdf8", opacity: 0.10, filter: "blur(110px)", left: -180, bottom: -180 + drift / 2 }} />
      <div style={{ position: "absolute", inset: 0, backgroundImage: "linear-gradient(rgba(255,255,255,0.055) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.055) 1px, transparent 1px)", backgroundSize: "48px 48px", opacity: 0.35, transform: `translateY(${drift * -0.25}px)` }} />
    </AbsoluteFill>
  );
};

const FloatingKeywords: React.FC<{ accent: string }> = ({ accent }) => {
  const frame = useCurrentFrame();
  return (
    <>
      {words.map((w, i) => {
        const x = 58 + ((i * 137) % 960);
        const y = 78 + ((i * 91) % 500);
        const opacity = 0.09 + (i % 3) * 0.035;
        return (
          <div key={w} style={{ position: "absolute", left: x, top: y + Math.sin((frame + i * 18) / 42) * 10, color: i % 2 ? "#e5e7eb" : accent, opacity, fontSize: 22 + (i % 3) * 8, fontWeight: 700, letterSpacing: -0.4 }}>
            {w}
          </div>
        );
      })}
    </>
  );
};

const Slide: React.FC<{ index: number }> = ({ index }) => {
  const frame = useCurrentFrame();
  const { fps: videoFps } = useVideoConfig();
  const slide = slides[index];
  const local = frame - index * slideDuration;
  const enter = spring({ frame: Math.max(0, local), fps: videoFps, config: { damping: 16, mass: 0.8 } });
  const exit = interpolate(local, [slideDuration - 24, slideDuration], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const opacity = Math.min(enter, exit);
  const translateY = interpolate(enter, [0, 1], [26, 0]);

  return (
    <AbsoluteFill style={{ opacity, transform: `translateY(${translateY}px)` }}>
      <Background accent={slide.accent} />
      <FloatingKeywords accent={slide.accent} />
      <div style={{ position: "absolute", left: 72, top: 56, color: "#94a3b8", fontSize: 18, fontWeight: 700, letterSpacing: 1.8, textTransform: "uppercase" }}>
        Innovation Analytics Lab · 2026
      </div>
      <div style={{ position: "absolute", right: 72, top: 56, color: slide.accent, fontSize: 20, fontWeight: 800 }}>
        {String(index + 1).padStart(2, "0")} / {String(slides.length).padStart(2, "0")}
      </div>
      <main style={{ position: "absolute", left: 78, right: 78, top: 126, bottom: 72, display: "grid", gridTemplateColumns: "1.1fr 0.9fr", gap: 46, alignItems: "center" }}>
        <section>
          <div style={{ display: "inline-flex", alignItems: "center", gap: 12, color: slide.accent, fontSize: 24, fontWeight: 900, marginBottom: 20 }}>
            <span style={{ width: 44, height: 4, background: slide.accent, borderRadius: 99 }} />
            {slide.kicker}
          </div>
          <h1 style={{ margin: 0, color: "#f8fafc", fontSize: index === 0 ? 72 : 62, lineHeight: 0.96, letterSpacing: -3.2, fontWeight: 950, maxWidth: 720 }}>
            {slide.title}
          </h1>
          <p style={{ color: "#cbd5e1", fontSize: 26, lineHeight: 1.35, maxWidth: 760, marginTop: 28, marginBottom: 0 }}>
            {slide.subtitle}
          </p>
        </section>
        <aside style={{ background: "rgba(15,23,42,0.72)", border: "1px solid rgba(148,163,184,0.25)", boxShadow: "0 24px 80px rgba(0,0,0,0.35)", borderRadius: 32, padding: 34 }}>
          <div style={{ fontSize: 18, color: "#94a3b8", fontWeight: 800, textTransform: "uppercase", letterSpacing: 1.5, marginBottom: 22 }}>Key signals</div>
          {slide.bullets.map((b, i) => (
            <div key={b} style={{ display: "flex", gap: 16, alignItems: "flex-start", marginBottom: 22 }}>
              <div style={{ flex: "0 0 auto", width: 34, height: 34, borderRadius: 999, background: slide.accent, color: "#020617", display: "grid", placeItems: "center", fontWeight: 950, fontSize: 18 }}>{i + 1}</div>
              <div style={{ color: "#f1f5f9", fontSize: 27, fontWeight: 760, lineHeight: 1.18 }}>{b}</div>
            </div>
          ))}
        </aside>
      </main>
      <div style={{ position: "absolute", left: 78, right: 78, bottom: 34, height: 8, borderRadius: 999, background: "rgba(148,163,184,0.22)", overflow: "hidden" }}>
        <div style={{ height: "100%", width: `${((local + 1) / slideDuration) * 100}%`, background: slide.accent, borderRadius: 999 }} />
      </div>
    </AbsoluteFill>
  );
};

export const MyComposition = () => {
  return <Composition id="AIReadinessTrends" component={MyComponent} durationInFrames={slides.length * slideDuration} fps={fps} width={1280} height={720} />;
};

export const MyComponent: React.FC<Props> = () => {
  const frame = useCurrentFrame();
  const index = Math.min(slides.length - 1, Math.floor(frame / slideDuration));
  return <Slide index={index} />;
};
