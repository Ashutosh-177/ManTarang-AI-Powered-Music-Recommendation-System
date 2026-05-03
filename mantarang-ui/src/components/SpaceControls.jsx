import { motion } from "framer-motion";

function Slider({ label, icon, value, min, max, step, onChange, color }) {
  const pct = ((value - min) / (max - min)) * 100;
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <span style={{ fontSize: 12, color: "#3d5070", fontWeight: 600, letterSpacing: "0.08em", textTransform: "uppercase" }}>
          {icon} {label}
        </span>
        <span style={{ fontSize: 12, color, fontWeight: 700, fontVariantNumeric: "tabular-nums" }}>
          {Math.round(value * 100)}%
        </span>
      </div>
      <div style={{ position: "relative", height: 4, background: "rgba(255,255,255,0.06)", borderRadius: 99 }}>
        {/* Filled track */}
        <div style={{
          position: "absolute", left: 0, top: 0, height: "100%",
          width: `${pct}%`, borderRadius: 99,
          background: `linear-gradient(90deg, ${color}60, ${color})`,
          transition: "width 0.05s",
        }} />
        <input
          type="range" min={min} max={max} step={step}
          value={value}
          onChange={e => onChange(parseFloat(e.target.value))}
          style={{
            position: "absolute", inset: 0,
            width: "100%", height: "100%",
            opacity: 0, cursor: "pointer", margin: 0,
          }}
        />
      </div>
    </div>
  );
}

export default function SpaceControls({ gravity, ozone, onGravity, onOzone }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 1.2 }}
      style={{
        position: "fixed",
        bottom: 28, right: 24,
        zIndex: 50,
        background: "rgba(8,12,28,0.82)",
        border: "1px solid rgba(255,255,255,0.07)",
        borderRadius: 14,
        padding: "14px 18px",
        width: 210,
        backdropFilter: "blur(12px)",
        display: "flex", flexDirection: "column", gap: 14,
      }}
    >
      <div style={{ fontSize: 11, color: "#2a3a5c", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.12em" }}>
        ◉ Black Hole Controls
      </div>

      <Slider
        label="Gravity"
        icon="⚫"
        value={gravity}
        min={0.1} max={1.0} step={0.01}
        onChange={onGravity}
        color="#fbbf24"
      />

      <Slider
        label="Ozone Density"
        icon="🌿"
        value={ozone}
        min={0.0} max={1.5} step={0.01}
        onChange={onOzone}
        color="#34d399"
      />
    </motion.div>
  );
}
