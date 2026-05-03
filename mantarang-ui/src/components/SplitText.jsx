// ReactBits SplitText — letter-by-letter entrance animation
import { useEffect, useRef } from "react";

export default function SplitText({ text = "", className = "", delay = 30, duration = 500 }) {
  const containerRef = useRef(null);

  useEffect(() => {
    const spans = containerRef.current?.querySelectorAll("span[data-char]");
    if (!spans) return;
    spans.forEach((span, i) => {
      span.style.opacity = "0";
      span.style.transform = "translateY(18px)";
      setTimeout(() => {
        span.style.transition = `opacity ${duration}ms cubic-bezier(.22,1,.36,1), transform ${duration}ms cubic-bezier(.22,1,.36,1)`;
        span.style.opacity = "1";
        span.style.transform = "translateY(0)";
      }, i * delay);
    });
  }, [text, delay, duration]);

  return (
    <span ref={containerRef} className={className} style={{ display: "inline" }}>
      {text.split("").map((ch, i) => (
        <span
          key={i}
          data-char
          style={{ display: "inline-block", whiteSpace: ch === " " ? "pre" : "normal" }}
        >
          {ch}
        </span>
      ))}
    </span>
  );
}
