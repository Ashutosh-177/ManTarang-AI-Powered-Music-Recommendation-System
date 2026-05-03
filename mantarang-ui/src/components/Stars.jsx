import { useEffect, useRef } from "react";

const STAR_COUNT = 200;

function rand(min, max) { return Math.random() * (max - min) + min; }

export default function Stars() {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");
    let animId;

    const resize = () => {
      canvas.width  = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    resize();
    window.addEventListener("resize", resize);

    // Generate stars once
    const stars = Array.from({ length: STAR_COUNT }, () => ({
      x:      rand(0, window.innerWidth),
      y:      rand(0, window.innerHeight),
      r:      rand(0.4, 1.8),
      baseOp: rand(0.35, 0.9),
      speed:  rand(0.0004, 0.0014), // twinkle speed
      phase:  rand(0, Math.PI * 2),
      drift:  rand(-0.18, 0.18),      // horizontal drift
      driftY: rand(-0.10, 0.10),     // vertical drift
    }));

    let t = 0;
    const draw = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      t += 1;

      stars.forEach(s => {
        // Slow drift
        s.x += s.drift;
        s.y += s.driftY;
        if (s.x < -2) s.x = canvas.width + 2;
        if (s.x > canvas.width + 2) s.x = -2;
        if (s.y < -2) s.y = canvas.height + 2;
        if (s.y > canvas.height + 2) s.y = -2;

        // Twinkle
        const op = s.baseOp * (0.5 + 0.5 * Math.sin(t * s.speed * 60 + s.phase));

        ctx.beginPath();
        ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(200,220,255,${op.toFixed(3)})`;
        ctx.fill();
      });

      animId = requestAnimationFrame(draw);
    };
    draw();

    return () => {
      cancelAnimationFrame(animId);
      window.removeEventListener("resize", resize);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      style={{
        position: "fixed",
        inset: 0,
        zIndex: 1,
        pointerEvents: "none",
      }}
    />
  );
}
