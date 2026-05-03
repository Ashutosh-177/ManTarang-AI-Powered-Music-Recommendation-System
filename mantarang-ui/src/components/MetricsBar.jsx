import { useEffect, useRef } from "react";

function Bar({ label, value, color, delay = 0 }) {
  const fillRef = useRef(null);

  useEffect(() => {
    const el = fillRef.current;
    if (!el) return;
    el.style.width = "0%";
    const t = setTimeout(() => {
      el.style.transition = "width 0.9s cubic-bezier(.22,1,.36,1)";
      el.style.width = `${value}%`;
    }, delay);
    return () => clearTimeout(t);
  }, [value, delay]);

  return (
    <div style={{ marginBottom: 12 }}>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 5 }}>
        <span style={{ fontSize: 14, color: "#8b949e", fontWeight: 500 }}>{label}</span>
        <span style={{ fontSize: 14, color, fontWeight: 700 }}>{value}%</span>
      </div>
      <div style={{
        height: 5, background: "rgba(255,255,255,0.05)",
        borderRadius: 99, overflow: "hidden",
      }}>
        <div ref={fillRef} style={{
          height: "100%", width: 0,
          background: `linear-gradient(90deg, ${color}60, ${color})`,
          borderRadius: 99,
        }} />
      </div>
    </div>
  );
}

const confLabel = (v) => v >= 0.8 ? "High" : v >= 0.6 ? "Good" : v >= 0.4 ? "Moderate" : "Low";
const confColor = (v) => v >= 0.8 ? "#6ee7b7" : v >= 0.6 ? "#7eb8f7" : v >= 0.4 ? "#a78bfa" : "#f87171";

export default function MetricsBar({ metrics, confidence, explanation, visible, accent = "#7db0a0" }) {
  if (!metrics || !visible) return null;

  const { genre_match, popularity_fit, artist_score, relevance, target_genres } = metrics;
  const confPct  = Math.round((confidence ?? 0) * 100);
  const cc       = confColor(confidence ?? 0);
  const circ     = 2 * Math.PI * 22;

  const bars = [
    { label: "Genre Match",        value: genre_match    ?? 0, color: "#7eb8f7", delay: 0   },
    { label: "Popularity Fit",     value: popularity_fit ?? 0, color: "#6ee7b7", delay: 90  },
    { label: "Artist Credibility", value: artist_score   ?? 0, color: "#a78bfa", delay: 180 },
    { label: "Overall Relevance",  value: relevance      ?? 0, color: "#f9a8d4", delay: 270 },
  ];

  return (
    <div style={{
      background: "rgba(2,4,14,0.75)",
      backdropFilter: "blur(14px)",
      border: "1px solid rgba(255,255,255,0.06)",
      borderRadius: 12,
      padding: "18px 20px",
    }}>
      <div style={{ display: "flex", gap: 22, alignItems: "flex-start" }}>

        {/* Confidence ring */}
        <div style={{ flexShrink: 0, textAlign: "center" }}>
          <svg width="64" height="64" viewBox="0 0 64 64">
            <circle cx="32" cy="32" r="22"
              fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="4.5" />
            <circle cx="32" cy="32" r="22"
              fill="none" stroke={cc} strokeWidth="4.5"
              strokeLinecap="round"
              strokeDasharray={circ}
              strokeDashoffset={circ * (1 - (confidence ?? 0))}
              transform="rotate(-90 32 32)"
              style={{ transition: "stroke-dashoffset 1s cubic-bezier(.22,1,.36,1) 0.15s" }}
            />
            <text x="32" y="36" textAnchor="middle"
              fill={cc} fontSize="13" fontWeight="800">
              {confPct}%
            </text>
          </svg>
          <div style={{ fontSize: 12, color: "#58656f", marginTop: 4, fontWeight: 600 }}>
            {confLabel(confidence ?? 0)}
          </div>
          <div style={{ fontSize: 11, color: "#3d4554", marginTop: 1 }}>
            confidence
          </div>
        </div>

        {/* Bars */}
        <div style={{ flex: 1 }}>
          <div style={{
            fontSize: 11, color: "#3d4554",
            fontWeight: 700, textTransform: "uppercase",
            letterSpacing: "0.1em", marginBottom: 14,
          }}>
            Why this track?
          </div>
          {bars.map((b) => <Bar key={b.label} {...b} />)}

          {target_genres?.length > 0 && (
            <div style={{ display: "flex", flexWrap: "wrap", gap: 5, marginTop: 4 }}>
              <span style={{ fontSize: 12, color: "#3d4554", alignSelf: "center", marginRight: 2 }}>
                Matched:
              </span>
              {target_genres.map((g) => (
                <span key={g} style={{
                  fontSize: 12, color: "#58656f",
                  padding: "2px 9px",
                  background: "rgba(255,255,255,0.03)",
                  border: "1px solid rgba(255,255,255,0.07)",
                  borderRadius: 99,
                }}>{g}</span>
              ))}
            </div>
          )}

          {explanation && (
            <div style={{
              marginTop: 12, fontSize: 13, color: "#6e7b83",
              fontStyle: "italic", lineHeight: 1.55,
              borderTop: "1px solid rgba(255,255,255,0.05)",
              paddingTop: 10,
            }}>
              {explanation}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
