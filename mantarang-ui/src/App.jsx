import { useState, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import HeroTitle from "./components/HeroTitle";
import TrackCard from "./components/TrackCard";
import SkeletonCard from "./components/SkeletonCard";
import Stars from "./components/Stars";
import blackhole from "./assets/blackhole.png";

const EXAMPLES = [
  "songs like Radiohead",
  "chill lo-fi for studying",
  "dark indie rock",
  "music for late night drives",
  "energetic hip hop",
  "classic rock anthems",
];

const STRATEGY_LABEL = {
  artist_match:     "Artist Match",
  similarity:       "Similarity",
  genre_mood:       "Genre / Mood",
  text_match:       "Text Match",
  popular_fallback: "Popular",
};

const confColor = (v) =>
  v >= 80 ? "#6ee7b7" : v >= 60 ? "#7eb8f7" : v >= 40 ? "#a78bfa" : "#f87171";

const BONES_PER_CARD = 13;

/* ── Quality panel ───────────────────────────────────────── */
function QualityPanel({ metrics }) {
  const [open, setOpen] = useState(false);
  if (!metrics) return null;
  const sysConf = metrics.system_confidence ?? 0;
  const cc = confColor(sysConf);

  const bars = [
    { label: "Avg Genre Match",  value: Math.round(metrics.avg_genre_match ?? 0),                        color: "#7eb8f7" },
    { label: "Avg Relevance",    value: Math.round(metrics.avg_relevance ?? 0),                           color: "#a78bfa" },
    { label: "Genre Diversity",  value: Math.min(100, Math.round((metrics.genre_diversity ?? 0) * 5)),   color: "#6ee7b7" },
    { label: "Artist Diversity", value: Math.min(100, Math.round((metrics.artist_diversity ?? 0) * 10)), color: "#f9a8d4" },
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.1 }}
      style={{
        background: "rgba(4,6,20,0.82)",
        border: "1px solid rgba(255,255,255,0.1)",
        borderRadius: 14, marginBottom: 20, overflow: "hidden",
        backdropFilter: "blur(20px)",
      }}
    >
      <button
        onClick={() => setOpen(v => !v)}
        style={{
          width: "100%", background: "transparent", border: "none",
          padding: "13px 18px", cursor: "pointer", fontFamily: "inherit",
          display: "flex", alignItems: "center", gap: 10,
        }}
      >
        <div style={{ width: 8, height: 8, borderRadius: "50%", background: cc, flexShrink: 0 }} />
        <span style={{ fontSize: 14, fontWeight: 700, color: cc }}>{sysConf}%</span>
        <span style={{ fontSize: 14, color: "#8b9eb8", fontWeight: 400 }}>system confidence</span>
        <span style={{ width: 1, height: 12, background: "rgba(255,255,255,0.1)", flexShrink: 0 }} />
        <span style={{ fontSize: 13, color: "#6a7a90" }}>
          {metrics.total_results ?? 0} tracks
          {metrics.strategy ? ` · ${STRATEGY_LABEL[metrics.strategy] ?? metrics.strategy}` : ""}
        </span>
        <motion.svg
          animate={{ rotate: open ? 180 : 0 }} transition={{ duration: 0.2 }}
          style={{ marginLeft: "auto", flexShrink: 0, color: "#6a7a90" }}
          width="14" height="14" viewBox="0 0 24 24" fill="none"
          stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"
        >
          <polyline points="6 9 12 15 18 9" />
        </motion.svg>
      </button>

      <AnimatePresence initial={false}>
        {open && (
          <motion.div
            initial={{ height: 0, opacity: 0 }} animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }} transition={{ duration: 0.28, ease: [0.22, 1, 0.36, 1] }}
            style={{ overflow: "hidden" }}
          >
            <div style={{ padding: "14px 18px 16px", borderTop: "1px solid rgba(255,255,255,0.07)" }}>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px 28px" }}>
                {bars.map(({ label, value, color }) => (
                  <div key={label}>
                    <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 4 }}>
                      <span style={{ fontSize: 13, color: "#8b9eb8" }}>{label}</span>
                      <span style={{ fontSize: 13, color, fontWeight: 700 }}>{value}%</span>
                    </div>
                    <div style={{ height: 3, background: "rgba(255,255,255,0.07)", borderRadius: 99, overflow: "hidden" }}>
                      <motion.div
                        initial={{ width: 0 }} animate={{ width: `${value}%` }}
                        transition={{ duration: 0.9, ease: [0.22, 1, 0.36, 1] }}
                        style={{ height: "100%", background: color, opacity: 0.7, borderRadius: 99 }}
                      />
                    </div>
                  </div>
                ))}
              </div>
              <p style={{ margin: "10px 0 0", fontSize: 13, color: "#6a7a90" }}>
                Avg confidence:{" "}
                <span style={{ color: cc, fontWeight: 700 }}>{Math.round((metrics.avg_confidence ?? 0) * 100)}%</span>
              </p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

/* ── App ─────────────────────────────────────────────────── */
export default function App() {
  const [query,     setQuery]     = useState("");
  const [results,   setResults]   = useState(null);
  const [aggregate, setAggregate] = useState(null);
  const [loading,   setLoading]   = useState(false);
  const [error,     setError]     = useState(null);
  const [searched,  setSearched]  = useState(false);
  const inputRef   = useRef(null);
  const resultsRef = useRef(null);

  const doSearch = (q) => {
    const trimmed = (q ?? query).trim();
    if (!trimmed) return;
    setLoading(true);
    setError(null);
    setResults(null);
    setAggregate(null);
    setSearched(true);

    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        const MIN_MS = 1200;
        const start  = Date.now();
        fetch("/api/recommendations", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ query: trimmed, max_recommendations: 10 }),
        })
          .then(r => { if (!r.ok) throw new Error(`${r.status}`); return r.json(); })
          .then(data => {
            const wait = Math.max(0, MIN_MS - (Date.now() - start));
            setTimeout(() => {
              setResults(data.recommendations ?? []);
              setAggregate(data.aggregate_metrics ?? null);
              setLoading(false);
              setTimeout(() => resultsRef.current?.scrollIntoView({ behavior: "smooth", block: "start" }), 80);
            }, wait);
          })
          .catch(e => {
            const wait = Math.max(0, MIN_MS - (Date.now() - start));
            setTimeout(() => { setError(e.message); setResults([]); setLoading(false); }, wait);
          });
      });
    });
  };

  const reset = () => {
    setResults(null); setAggregate(null);
    setSearched(false); setQuery(""); setError(null); setLoading(false);
  };

  return (
    <div style={{ minHeight: "100vh", position: "relative", fontFamily: "'Inter', system-ui, sans-serif" }}>

      {/* ── Background image fixed ─────────────────────────── */}
      <div style={{
        position: "fixed", inset: 0, zIndex: 0,
        backgroundImage: `url(${blackhole})`,
        backgroundSize: "cover",
        backgroundPosition: "center center",
        backgroundRepeat: "no-repeat",
      }} />

      {/* ── Moving stars layer ─────────────────────────────── */}
      <Stars />

      {/* ── Content centered ───────────────────────────────── */}
      <div style={{
        position: "relative", zIndex: 2,
        maxWidth: 760, margin: "0 auto 0 auto",
        marginLeft: "auto", marginRight: "8%",
        padding: "0 24px 100px",
      }}>

        {/* ── Hero ─────────────────────────────────────────── */}
        <AnimatePresence>
          {!searched && (
            <motion.div
              key="hero"
              initial={{ opacity: 1 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.35 }}
              style={{
                textAlign: "center",
                minHeight: "55vh",
                display: "flex",
                flexDirection: "column",
                justifyContent: "center",
                alignItems: "center",
                paddingTop: 40,
                paddingBottom: 40,
              }}
            >
              <motion.p
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4 }}
                style={{
                  fontSize: 12, fontWeight: 700,
                  color: "#93c5fd",
                  letterSpacing: "0.26em", textTransform: "uppercase",
                  margin: "0 0 18px",
                  textShadow: "0 0 20px rgba(0,0,0,1), 0 2px 8px rgba(0,0,0,1)",
                }}
              >
                AI Music Intelligence
              </motion.p>

              <motion.div
                initial={{ opacity: 0, y: 14 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.1 }}
              >
                <HeroTitle />
              </motion.div>

              <motion.p
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.45, delay: 0.5 }}
                style={{
                  color: "#e2e8f0",
                  fontSize: 17,
                  maxWidth: 400, margin: "18px auto 0",
                  lineHeight: 1.7,
                  textShadow: "0 0 20px rgba(0,0,0,1), 0 2px 8px rgba(0,0,0,1)",
                }}
              >
                Describe what you want to hear — moods, genres, or any vibe.
              </motion.p>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Breadcrumb after search */}
        {searched && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            style={{ paddingTop: 36, paddingBottom: 22, display: "flex", alignItems: "center", gap: 8 }}
          >
            <button onClick={reset} style={{
              background: "transparent", border: "none",
              color: "#e8f0ff", fontSize: 20, fontWeight: 900,
              letterSpacing: "-0.5px", cursor: "pointer", padding: 0, fontFamily: "inherit",
            }}>ManTarang</button>
            <span style={{ color: "#2a3a54", fontSize: 18 }}>/</span>
            <span style={{ color: "#6a7a90", fontSize: 15 }}>results</span>
          </motion.div>
        )}

        {/* ── Search bar ───────────────────────────────────── */}
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.45, delay: searched ? 0 : 0.65 }}
          style={{
            background: "rgba(5,8,28,0.75)",
            border: "1.5px solid rgba(126,184,247,0.35)",
            borderRadius: 14,
            display: "flex", alignItems: "center", gap: 10,
            padding: "13px 18px",
            marginBottom: searched ? 22 : 18,
            backdropFilter: "blur(12px)",
          }}
        >
          <svg width="17" height="17" viewBox="0 0 24 24" fill="none"
            stroke="#6a7a90" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
            style={{ flexShrink: 0 }}>
            <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
          </svg>
          <input
            ref={inputRef}
            value={query}
            onChange={e => setQuery(e.target.value)}
            onKeyDown={e => e.key === "Enter" && doSearch()}
            placeholder="Try 'songs like Radiohead' or 'dark indie rock'…"
            style={{
              flex: 1, background: "transparent", border: "none", outline: "none",
              color: "#e8f0ff", fontSize: 15, fontFamily: "inherit",
              caretColor: "#7eb8f7",
            }}
          />
          <button
            onClick={() => doSearch()}
            disabled={loading || !query.trim()}
            style={{
              background: !query.trim() || loading ? "rgba(255,255,255,0.05)" : "rgba(126,184,247,0.15)",
              color: !query.trim() || loading ? "#3a4a64" : "#7eb8f7",
              border: `1px solid ${!query.trim() || loading ? "rgba(255,255,255,0.08)" : "rgba(126,184,247,0.3)"}`,
              borderRadius: 10, padding: "8px 22px",
              fontSize: 14, fontWeight: 600,
              cursor: !query.trim() || loading ? "not-allowed" : "pointer",
              transition: "all 0.2s", whiteSpace: "nowrap", fontFamily: "inherit",
            }}
          >
            {loading ? "Searching…" : "Search"}
          </button>
        </motion.div>

        {/* ── Example chips ────────────────────────────────── */}
        <AnimatePresence>
          {!searched && (
            <motion.div
              key="chips"
              initial={{ opacity: 0 }} animate={{ opacity: 1 }}
              exit={{ opacity: 0 }} transition={{ duration: 0.3, delay: 0.8 }}
              style={{ display: "flex", flexWrap: "wrap", gap: 8, justifyContent: "center" }}
            >
              {EXAMPLES.map((eq, i) => (
                <motion.button
                  key={eq}
                  initial={{ opacity: 0, scale: 0.92 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 0.84 + i * 0.04 }}
                  onClick={() => { setQuery(eq); doSearch(eq); }}
                  style={{
                    background: "rgba(4,6,20,0.65)",
                    border: "1px solid rgba(255,255,255,0.1)",
                    borderRadius: 99, padding: "7px 16px",
                    fontSize: 13, color: "#8b9eb8",
                    cursor: "pointer", transition: "all 0.15s",
                    fontFamily: "inherit", backdropFilter: "blur(12px)",
                  }}
                  onMouseEnter={e => { e.currentTarget.style.borderColor = "rgba(126,184,247,0.35)"; e.currentTarget.style.color = "#7eb8f7"; }}
                  onMouseLeave={e => { e.currentTarget.style.borderColor = "rgba(255,255,255,0.1)"; e.currentTarget.style.color = "#8b9eb8"; }}
                >
                  {eq}
                </motion.button>
              ))}
            </motion.div>
          )}
        </AnimatePresence>

        {/* ── Error ────────────────────────────────────────── */}
        <AnimatePresence>
          {error && (
            <motion.div
              initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
              style={{
                marginTop: 14,
                background: "rgba(248,113,113,0.08)",
                border: "1px solid rgba(248,113,113,0.2)",
                borderRadius: 12, padding: "13px 16px",
                color: "#f87171", fontSize: 14,
              }}
            >
              Backend unreachable: {error}. Make sure FastAPI is running on port 8000.
            </motion.div>
          )}
        </AnimatePresence>

        {/* ── Skeleton ─────────────────────────────────────── */}
        <AnimatePresence>
          {loading && (
            <motion.div
              key="skeleton" ref={resultsRef}
              initial={{ opacity: 1 }} animate={{ opacity: 1 }}
              exit={{ opacity: 0, transition: { duration: 0.2 } }}
              style={{ marginTop: 28 }}
            >
              <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 20 }}>
                <div style={{
                  width: 15, height: 15, flexShrink: 0,
                  border: "2px solid rgba(126,184,247,0.15)",
                  borderTopColor: "#7eb8f7",
                  borderRadius: "50%",
                  animation: "spin 0.75s linear infinite",
                }} />
                <span style={{ fontSize: 14, color: "#8b9eb8" }}>Scanning the cosmos…</span>
              </div>
              <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
                {Array.from({ length: 5 }, (_, i) => (
                  <SkeletonCard key={i} index={i} seqStart={i * BONES_PER_CARD} />
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* ── Results ──────────────────────────────────────── */}
        <AnimatePresence>
          {!loading && results && results.length > 0 && (
            <motion.div
              key="results" ref={resultsRef}
              initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
              style={{ marginTop: 28 }}
            >
              <QualityPanel metrics={aggregate} />

              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
                <span style={{ fontSize: 14, color: "#8b9eb8" }}>
                  <span style={{ color: "#c8d6e8", fontWeight: 600 }}>{results.length}</span> tracks found
                </span>
                <button
                  onClick={reset}
                  style={{
                    background: "transparent",
                    border: "1px solid rgba(255,255,255,0.1)",
                    borderRadius: 8, padding: "5px 14px",
                    fontSize: 13, color: "#6a7a90", cursor: "pointer",
                    fontFamily: "inherit", transition: "all 0.15s",
                  }}
                  onMouseEnter={e => { e.currentTarget.style.borderColor = "rgba(255,255,255,0.2)"; e.currentTarget.style.color = "#c8d6e8"; }}
                  onMouseLeave={e => { e.currentTarget.style.borderColor = "rgba(255,255,255,0.1)"; e.currentTarget.style.color = "#6a7a90"; }}
                >
                  New search
                </button>
              </div>

              <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
                {results.map((rec, i) => (
                  <TrackCard key={`${rec.artist}-${rec.title}-${i}`} rec={rec} index={i} source={rec.source} />
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* ── Empty state ───────────────────────────────────── */}
        <AnimatePresence>
          {!loading && results?.length === 0 && (
            <motion.div
              initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
              style={{ textAlign: "center", padding: "64px 0" }}
            >
              <div style={{ fontSize: 34, marginBottom: 12 }}>🎵</div>
              <p style={{ fontSize: 16, color: "#8b9eb8", margin: 0 }}>
                No tracks found. Try a different genre or mood.
              </p>
            </motion.div>
          )}
        </AnimatePresence>

      </div>
    </div>
  );
}
