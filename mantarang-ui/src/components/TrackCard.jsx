import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import GlowCard from "./GlowCard";
import MetricsBar from "./MetricsBar";

/*
  Relaxing palette — warm sage, dusty teal, muted slate.
  All text colors are high-contrast against the dark background.
*/
const ACCENTS = [
  "#7eb8f7", // star blue
  "#a78bfa", // nebula violet
  "#6ee7b7", // aurora green
  "#f9a8d4", // cosmic rose
  "#fcd34d", // distant star yellow
  "#67e8f9", // ice-blue pulsar
  "#c4b5fd", // deep violet
  "#86efac", // soft galaxy green
];

const STRATEGY_LABELS = {
  artist_match:     "Artist Match",
  similarity:       "Similar Sound",
  genre_mood:       "Genre / Mood",
  text_match:       "Text Match",
  popular_fallback: "Trending",
};

function Chevron({ open }) {
  return (
    <motion.svg
      animate={{ rotate: open ? 180 : 0 }}
      transition={{ duration: 0.22, ease: [0.22, 1, 0.36, 1] }}
      width="15" height="15" viewBox="0 0 24 24"
      fill="none" stroke="currentColor" strokeWidth="2.5"
      strokeLinecap="round" strokeLinejoin="round"
      style={{ display: "block" }}
    >
      <polyline points="6 9 12 15 18 9" />
    </motion.svg>
  );
}

export default function TrackCard({ rec, index, source }) {
  const [open, setOpen] = useState(false);
  const accent = ACCENTS[index % ACCENTS.length];

  const sq = encodeURIComponent(`${rec.artist} ${rec.title}`);
  const links = [
    { label: "Last.fm",  href: `https://www.last.fm/search?q=${sq}`,                   color: "#e07878" },
    { label: "Spotify",  href: `https://open.spotify.com/search/${sq}`,                color: "#6dbf82" },
    { label: "YouTube",  href: `https://www.youtube.com/results?search_query=${sq}`,   color: "#d4924a" },
  ];

  const stratLabel = STRATEGY_LABELS[source] ?? source ?? "";

  return (
    <motion.div
      initial={{ opacity: 0, y: 18 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.42, delay: index * 0.055, ease: [0.22, 1, 0.36, 1] }}
    >
      <GlowCard glowColor={`${accent}16`}>
        <div style={{
          background: "rgba(2,4,14,0.68)",
          border: "1px solid rgba(255,255,255,0.08)",
          backdropFilter: "blur(18px)",
          borderLeft: `3px solid ${accent}`,
          borderRadius: 14,
          padding: "22px 24px",
          position: "relative",
        }}>

          {/* Rank badge */}
          <div style={{
            position: "absolute", top: -12, left: 18,
            width: 26, height: 26, borderRadius: "50%",
            background: "#02030a",
            border: `1.5px solid ${accent}60`,
            color: accent,
            display: "flex", alignItems: "center", justifyContent: "center",
            fontSize: 12, fontWeight: 800,
          }}>
            {rec.rank}
          </div>

          {/* ── Main row ──────────────────────────────────── */}
          <div style={{ display: "flex", gap: 16, alignItems: "flex-start", marginTop: 6 }}>
            {/* Left: text */}
            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{
                fontWeight: 700, fontSize: 18, color: "#e6edf3",
                overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap",
              }}>
                {rec.title}
              </div>
              <div style={{ color: accent, fontSize: 15, marginTop: 4, fontWeight: 600 }}>
                {rec.artist}
              </div>
              {rec.album && (
                <div style={{ color: "#58656f", fontSize: 13, marginTop: 2 }}>
                  {rec.album}
                </div>
              )}

              {/* Genre + strategy chips */}
              <div style={{ display: "flex", flexWrap: "wrap", gap: 6, marginTop: 12 }}>
                {(rec.genres ?? []).slice(0, 3).map((g) => (
                  <span key={g} style={{
                    fontSize: 13, color: "#8b949e",
                    padding: "3px 11px",
                    background: "rgba(255,255,255,0.04)",
                    border: "1px solid rgba(255,255,255,0.08)",
                    borderRadius: 99,
                  }}>{g}</span>
                ))}
                {stratLabel && (
                  <span style={{
                    fontSize: 13, padding: "3px 11px",
                    background: `${accent}14`,
                    color: accent,
                    border: `1px solid ${accent}35`,
                    borderRadius: 99, fontWeight: 600,
                  }}>{stratLabel}</span>
                )}
              </div>
            </div>

            {/* Right: meta */}
            <div style={{
              flexShrink: 0, display: "flex", flexDirection: "column",
              alignItems: "flex-end", gap: 5, paddingTop: 2,
            }}>
              {rec.release_year && (
                <span style={{ fontSize: 13, color: "#58656f" }}>{rec.release_year}</span>
              )}
              {rec.duration && (
                <span style={{ fontSize: 13, color: "#58656f" }}>{rec.duration}</span>
              )}
              {rec.explicit && (
                <span style={{
                  fontSize: 11, fontWeight: 700,
                  background: "rgba(220,80,80,0.12)", color: "#e07878",
                  padding: "2px 7px", borderRadius: 4,
                }}>E</span>
              )}
              {rec.popularity > 0 && (
                <span style={{ fontSize: 13, color: "#8b949e" }}>
                  ♪ {rec.popularity}
                </span>
              )}
            </div>
          </div>

          {/* ── Bottom row: links + Details toggle ─────────── */}
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginTop: 18, flexWrap: "wrap" }}>
            {links.map(({ label, href, color }) => (
              <a
                key={label}
                href={href}
                target="_blank"
                rel="noreferrer"
                style={{
                  fontSize: 13, fontWeight: 600, color,
                  padding: "6px 14px", borderRadius: 8,
                  background: `${color}12`,
                  border: `1px solid ${color}30`,
                  transition: "background 0.15s",
                }}
                onMouseEnter={e => e.currentTarget.style.background = `${color}22`}
                onMouseLeave={e => e.currentTarget.style.background = `${color}12`}
              >
                {label}
              </a>
            ))}

            {/* Details arrow */}
            <button
              onClick={() => setOpen(v => !v)}
              style={{
                marginLeft: "auto",
                display: "flex", alignItems: "center", gap: 6,
                fontSize: 13, fontWeight: 500,
                color: open ? accent : "#6e7b83",
                background: open ? `${accent}12` : "rgba(255,255,255,0.03)",
                border: `1px solid ${open ? accent + "40" : "rgba(255,255,255,0.07)"}`,
                padding: "6px 14px", borderRadius: 8,
                cursor: "pointer", transition: "all 0.18s",
                fontFamily: "inherit",
              }}
              onMouseEnter={e => { if (!open) { e.currentTarget.style.color = "#c9d1d9"; e.currentTarget.style.borderColor = "rgba(255,255,255,0.14)"; }}}
              onMouseLeave={e => { if (!open) { e.currentTarget.style.color = "#6e7b83"; e.currentTarget.style.borderColor = "rgba(255,255,255,0.07)"; }}}
            >
              Details <Chevron open={open} />
            </button>
          </div>

          {/* ── Collapsible metrics ────────────────────────── */}
          <AnimatePresence initial={false}>
            {open && (
              <motion.div
                key="panel"
                initial={{ opacity: 0, height: 0, marginTop: 0 }}
                animate={{ opacity: 1, height: "auto", marginTop: 16 }}
                exit={{ opacity: 0, height: 0, marginTop: 0 }}
                transition={{ duration: 0.28, ease: [0.22, 1, 0.36, 1] }}
                style={{ overflow: "hidden" }}
              >
                <MetricsBar
                  metrics={rec.metrics}
                  confidence={rec.confidence}
                  explanation={rec.explanation}
                  visible
                  accent={accent}
                />
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </GlowCard>
    </motion.div>
  );
}
