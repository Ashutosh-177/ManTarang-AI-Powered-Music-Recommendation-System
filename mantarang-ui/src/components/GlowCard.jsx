// Glow-on-hover card — inspired by ReactBits SpotlightCard
import { useRef } from "react";

export default function GlowCard({ children, className = "", glowColor = "rgba(139,92,246,0.25)" }) {
  const cardRef = useRef(null);

  const handleMouseMove = (e) => {
    const card = cardRef.current;
    if (!card) return;
    const rect = card.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    card.style.setProperty("--gx", `${x}px`);
    card.style.setProperty("--gy", `${y}px`);
    card.style.setProperty("--glow", glowColor);
    card.classList.add("glow-active");
  };

  const handleMouseLeave = () => {
    cardRef.current?.classList.remove("glow-active");
  };

  return (
    <div
      ref={cardRef}
      className={`glow-card ${className}`}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
    >
      {children}
    </div>
  );
}
