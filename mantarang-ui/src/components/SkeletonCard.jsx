import { motion } from "framer-motion";

/*
  Each <Bone> has a --wave-delay CSS variable.
  The global CSS animates opacity using wave-pulse keyframes
  so bones ripple in sequence like dominoes left → right.
  `seq` is a global sequence number that increments across
  all bones in all cards so the wave flows continuously.
*/
function Bone({ w = "100%", h = 14, seq = 0, round = false, style = {} }) {
  const delay = (seq * 0.07).toFixed(2);
  return (
    <div
      className="bone"
      style={{
        width: w, height: h,
        borderRadius: round ? 99 : 7,
        "--wave-delay": `${delay}s`,
        ...style,
      }}
    />
  );
}

export default function SkeletonCard({ index = 0, seqStart = 0 }) {
  // seqStart lets the parent offset the wave so each card
  // continues where the previous one left off.
  let s = seqStart;
  const next = () => s++;

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25, delay: index * 0.05, ease: [0.22, 1, 0.36, 1] }}
      style={{
        background: "rgba(8,12,32,0.82)",
        backdropFilter: "blur(16px)",
        border: "1px solid rgba(255,255,255,0.08)",
        borderLeft: "3px solid rgba(126,184,247,0.20)",
        borderRadius: 14,
        padding: "22px 24px",
        position: "relative",
      }}
    >
      {/* Rank circle */}
      <div style={{ position: "absolute", top: -12, left: 18 }}>
        <Bone w={26} h={26} seq={next()} round style={{ borderRadius: "50%" }} />
      </div>

      {/* Top row */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 16, marginTop: 6 }}>
        <div style={{ flex: 1, display: "flex", flexDirection: "column", gap: 9 }}>
          <Bone w="58%" h={18} seq={next()} />
          <Bone w="38%" h={15} seq={next()} />
          <Bone w="28%" h={13} seq={next()} />
        </div>
        {/* Meta column */}
        <div style={{ display: "flex", flexDirection: "column", gap: 7, alignItems: "flex-end" }}>
          <Bone w={38} h={13} seq={next()} />
          <Bone w={32} h={13} seq={next()} />
        </div>
      </div>

      {/* Genre chips */}
      <div style={{ display: "flex", gap: 7, marginTop: 16 }}>
        <Bone w={72} h={24} seq={next()} round />
        <Bone w={88} h={24} seq={next()} round />
        <Bone w={60} h={24} seq={next()} round />
        <Bone w={76} h={24} seq={next()} round />
      </div>

      {/* Link row */}
      <div style={{ display: "flex", gap: 8, marginTop: 18 }}>
        <Bone w={74} h={30} seq={next()} style={{ borderRadius: 8 }} />
        <Bone w={74} h={30} seq={next()} style={{ borderRadius: 8 }} />
        <Bone w={74} h={30} seq={next()} style={{ borderRadius: 8 }} />
        <div style={{ marginLeft: "auto" }}>
          <Bone w={88} h={30} seq={next()} style={{ borderRadius: 8 }} />
        </div>
      </div>
    </motion.div>
  );
}
