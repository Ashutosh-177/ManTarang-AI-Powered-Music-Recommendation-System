import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

const TARANG_LETTERS = "Tarang".split("");
const NOTES = ["♪", "♫", "♩", "♬"];

export default function HeroTitle() {
  const [hovered, setHovered] = useState(false);

  return (
    <h1
      style={{
        margin: 0,
        fontSize: "clamp(56px, 10vw, 92px)",
        fontWeight: 900,
        lineHeight: 1,
        letterSpacing: "-2.5px",
        display: "inline-block",
        userSelect: "none",
        color: "#e8f0ff",
        textShadow: "0 0 24px rgba(0,0,0,1), 0 2px 10px rgba(0,0,0,1)",
      }}
    >
      {/* "Man" — static */}
      <span style={{ color: "#e6edf3" }}>Man</span>

      {/* "Tarang" — color wave + music notes inside each letter */}
      <span
        onMouseEnter={() => setHovered(true)}
        onMouseLeave={() => setHovered(false)}
        style={{ display: "inline-block", cursor: "default", position: "relative" }}
      >
        {TARANG_LETTERS.map((ch, i) => (
          <span key={i} style={{ display: "inline-block", position: "relative" }}>

            {/* Music note that rises inside this letter slot */}
            <AnimatePresence>
              {hovered && (
                <motion.span
                  key={`note-${i}`}
                  initial={{ opacity: 0, y: 0, scale: 0.5 }}
                  animate={{ opacity: [0, 1, 1, 0], y: -32, scale: [0.5, 1, 1, 0.7] }}
                  exit={{ opacity: 0 }}
                  transition={{
                    duration: 1.2,
                    delay: i * 0.08,
                    ease: "easeOut",
                    repeat: Infinity,
                    repeatDelay: 0.4,
                  }}
                  style={{
                    position: "absolute",
                    top: "15%",
                    left: "50%",
                    transform: "translateX(-50%)",
                    fontSize: "clamp(10px, 1.4vw, 18px)",
                    color: "#7eb8f7",
                    pointerEvents: "none",
                    zIndex: 10,
                    lineHeight: 1,
                  }}
                >
                  {NOTES[i % NOTES.length]}
                </motion.span>
              )}
            </AnimatePresence>

            {/* Letter with smooth color transition */}
            <motion.span
              animate={{ color: hovered ? "#7eb8f7" : "#e6edf3" }}
              transition={{
                duration: 0.4,
                delay: hovered ? i * 0.06 : (TARANG_LETTERS.length - 1 - i) * 0.04,
                ease: "easeInOut",
              }}
              style={{ display: "inline-block" }}
            >
              {ch}
            </motion.span>
          </span>
        ))}
      </span>
    </h1>
  );
}
