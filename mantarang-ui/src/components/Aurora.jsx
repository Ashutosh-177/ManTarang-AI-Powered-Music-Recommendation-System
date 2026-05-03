import { useEffect, useRef, useState } from "react";

const NOTES = ["♩", "♪", "♫", "♬", "𝄞", "𝄢", "𝅗𝅥", "♭", "♮", "♯", "𝄽", "𝄾"];

/*
  Layers (back → front):
  1. Deep space: pure black + distant stars
  2. Ozone atmosphere: multi-ring concentric bands around the black hole
     — colours shift green → teal → blue → deep violet → black
  3. Accretion disk: thin glowing ellipse around the event horizon
  4. Musical notes: spawn on right, drift left, get pulled toward
     singularity — rotate, skew, scale down, fade through atmosphere layers
  5. Event horizon: solid black circle (masks everything behind it)
  6. Gravitational lensing ring: bright thin ring just outside horizon
*/
export default function Aurora({ gravity = 0.55, ozone = 0.7 }) {
  const canvasRef = useRef(null);
  const gravRef   = useRef(gravity);
  const ozoneRef  = useRef(ozone);

  // Keep refs in sync with props
  useEffect(() => { gravRef.current  = gravity; }, [gravity]);
  useEffect(() => { ozoneRef.current = ozone;   }, [ozone]);

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx    = canvas.getContext("2d");
    let raf;
    let t = 0;

    /* ── Stars ─────────────────────────────────────────── */
    let stars = [];
    const buildStars = (w, h) => {
      stars = Array.from({ length: 180 }, () => ({
        x: Math.random() * w, y: Math.random() * h,
        r: Math.random() * 1.3 + 0.2,
        phase: Math.random() * Math.PI * 2,
        spd: 0.5 + Math.random(),
      }));
    };

    /* ── Notes ─────────────────────────────────────────── */
    let notes = [];
    let noteId = 0;

    const spawnNote = (w, h, bh) => {
      const g = gravRef.current;
      notes.push({
        id:      noteId++,
        x:       w * 0.95 + Math.random() * w * 0.05,
        y:       bh.cy + (Math.random() - 0.5) * h * 0.65,
        vx:      -(0.18 + Math.random() * 0.22) * (0.6 + g * 0.8),
        vy:      (Math.random() - 0.5) * 0.3,
        symbol:  NOTES[Math.floor(Math.random() * NOTES.length)],
        size:    16 + Math.random() * 14,
        rot:     Math.random() * Math.PI * 2,
        opacity: 0.85 + Math.random() * 0.15,
        age:     0,
      });
    };

    /* ── Resize ─────────────────────────────────────────── */
    const resize = () => {
      canvas.width  = canvas.offsetWidth;
      canvas.height = canvas.offsetHeight;
      buildStars(canvas.width, canvas.height);
    };
    resize();
    window.addEventListener("resize", resize);

    /* ── Main loop ──────────────────────────────────────── */
    let spawnTimer = 0;

    const draw = () => {
      t += 0.01;
      const { width: w, height: h } = canvas;
      const g = gravRef.current;
      const oz = ozoneRef.current;

      /* Black hole position: left side, vertically centred */
      const bh = {
        cx: w * 0.13,
        cy: h * 0.50,
        r:  Math.min(w, h) * 0.072,   // event horizon radius
      };

      /* ── 1. Deep space background ──────────────────────── */
      ctx.fillStyle = "#02030a";
      ctx.fillRect(0, 0, w, h);

      /* ── 2. Distant stars ──────────────────────────────── */
      for (const s of stars) {
        const a = 0.25 + 0.6 * (0.5 + 0.5 * Math.sin(s.phase + t * s.spd));
        ctx.beginPath();
        ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(190,210,255,${a})`;
        ctx.fill();
      }

      /* ── 3. Ozone atmosphere bands ─────────────────────── */
      /*
        Bands are concentric ellipses. Outer bands are wide and
        green-teal; inner bands narrow and deepen to violet-black.
        ozone prop controls overall opacity / density.
      */
      const atmBands = [
        { rMul: 5.2, color: [34, 197, 94],   alpha: 0.028 * oz },  // outer green
        { rMul: 4.2, color: [20, 184, 166],  alpha: 0.038 * oz },  // teal
        { rMul: 3.3, color: [6,  182, 212],  alpha: 0.042 * oz },  // cyan
        { rMul: 2.6, color: [59, 130, 246],  alpha: 0.045 * oz },  // blue
        { rMul: 2.0, color: [99, 102, 241],  alpha: 0.048 * oz },  // indigo
        { rMul: 1.65,color: [139, 92, 246],  alpha: 0.052 * oz },  // violet
        { rMul: 1.38,color: [88,  28, 135],  alpha: 0.055 * oz },  // deep purple
        { rMul: 1.18,color: [30,  10,  60],  alpha: 0.06  * oz },  // near-black
      ];

      for (const band of atmBands) {
        const rx = bh.r * band.rMul * 1.55;
        const ry = bh.r * band.rMul * 0.80;
        const [r, g2, b] = band.color;

        // Gradient from center of band outward
        const grd = ctx.createRadialGradient(
          bh.cx, bh.cy, bh.r * (band.rMul - 0.5),
          bh.cx, bh.cy, bh.r * band.rMul * 1.4
        );
        grd.addColorStop(0,   `rgba(${r},${g2},${b},${band.alpha * 1.4})`);
        grd.addColorStop(0.5, `rgba(${r},${g2},${b},${band.alpha})`);
        grd.addColorStop(1,   `rgba(${r},${g2},${b},0)`);

        ctx.save();
        ctx.scale(1, ry / rx);
        ctx.beginPath();
        ctx.arc(bh.cx, bh.cy * (rx / ry), rx, 0, Math.PI * 2);
        ctx.fillStyle = grd;
        ctx.fill();
        ctx.restore();
      }

      /* ── 4. Accretion disk ──────────────────────────────── */
      const diskRx = bh.r * 2.1;
      const diskRy = bh.r * 0.32;
      // Back half (behind black hole)
      ctx.save();
      ctx.scale(1, diskRy / diskRx);
      const diskGrad = ctx.createLinearGradient(
        bh.cx - diskRx, 0, bh.cx + diskRx, 0
      );
      diskGrad.addColorStop(0,    "rgba(251,191,36,0)");
      diskGrad.addColorStop(0.2,  "rgba(251,191,36,0.55)");
      diskGrad.addColorStop(0.42, "rgba(251,146,60,0.80)");
      diskGrad.addColorStop(0.5,  "rgba(255,255,255,0.90)");
      diskGrad.addColorStop(0.58, "rgba(251,146,60,0.80)");
      diskGrad.addColorStop(0.8,  "rgba(251,191,36,0.55)");
      diskGrad.addColorStop(1,    "rgba(251,191,36,0)");

      ctx.beginPath();
      ctx.ellipse(bh.cx, bh.cy * (diskRx / diskRy), diskRx, diskRx, 0, Math.PI, Math.PI * 2);
      ctx.strokeStyle = diskGrad;
      ctx.lineWidth   = diskRx * 0.18 * (diskRy / diskRx);
      ctx.stroke();
      ctx.restore();

      /* ── 5. Spawn / update notes ─────────────────────────── */
      spawnTimer++;
      const spawnRate = Math.max(4, Math.round(18 - g * 12));
      if (spawnTimer >= spawnRate) { spawnNote(w, h, bh); spawnTimer = 0; }

      const toRemove = new Set();

      for (const n of notes) {
        n.age++;

        /* Distance to singularity */
        const dx = n.x - bh.cx;
        const dy = n.y - bh.cy;
        const dist = Math.sqrt(dx * dx + dy * dy);

        /* Gravity pull — stronger closer in, modulated by g prop */
        const pull = (g * 1.8 * bh.r * bh.r) / (dist * dist + 1);
        n.vx += (-dx / dist) * pull;
        n.vy += (-dy / dist) * pull * 0.6;

        /* Spiral effect: slight tangential nudge */
        n.vx += ( dy / dist) * pull * 0.18;
        n.vy += (-dx / dist) * pull * 0.18;

        n.x  += n.vx;
        n.y  += n.vy;

        /* Rotation: faster as it gets closer */
        const spinRate = 0.015 + (1 - Math.min(1, dist / (bh.r * 4))) * 0.12;
        n.rot += spinRate * (n.vx < 0 ? 1 : -1);

        /* Scale shrinks near horizon */
        const scaleFactor = Math.max(0.05, Math.min(1, (dist - bh.r * 0.95) / (bh.r * 3)));

        /* Opacity: fades inside atmosphere */
        const atmFade = Math.min(1, (dist - bh.r * 1.05) / (bh.r * 1.8));
        const alpha   = n.opacity * Math.max(0, atmFade) * scaleFactor;

        /* Skew toward singularity */
        const skew = Math.min(0.9, pull * 4);

        /* Remove if swallowed or too old */
        if (dist < bh.r * 0.98 || n.age > 1800) { toRemove.add(n.id); continue; }

        /* Pick colour based on distance band (mirrors ozone layers) */
        let noteColor;
        const ratio = dist / (bh.r * 5.5);
        if      (ratio > 0.85) noteColor = `rgba(200,230,200,${alpha})`;   // far: pale green
        else if (ratio > 0.65) noteColor = `rgba(100,220,200,${alpha})`;   // teal
        else if (ratio > 0.45) noteColor = `rgba(100,170,255,${alpha})`;   // blue
        else if (ratio > 0.28) noteColor = `rgba(160,120,255,${alpha})`;   // violet
        else                   noteColor = `rgba(220,100,200,${alpha * 0.6})`; // near-horizon pink

        ctx.save();
        ctx.translate(n.x, n.y);
        ctx.rotate(n.rot);
        ctx.transform(1, 0, skew, 1, 0, 0);   // horizontal skew toward BH
        ctx.scale(scaleFactor, scaleFactor * (1 - skew * 0.4));
        ctx.font      = `${n.size}px serif`;
        ctx.fillStyle = noteColor;
        ctx.fillText(n.symbol, 0, 0);
        ctx.restore();
      }

      notes = notes.filter(n => !toRemove.has(n.id));

      /* ── 6. Accretion disk front half ──────────────────── */
      ctx.save();
      ctx.scale(1, diskRy / diskRx);
      ctx.beginPath();
      ctx.ellipse(bh.cx, bh.cy * (diskRx / diskRy), diskRx, diskRx, 0, 0, Math.PI);
      ctx.strokeStyle = diskGrad;
      ctx.lineWidth   = diskRx * 0.18 * (diskRy / diskRx);
      ctx.stroke();
      ctx.restore();

      /* ── 7. Event horizon (solid black circle) ──────────── */
      ctx.beginPath();
      ctx.arc(bh.cx, bh.cy, bh.r, 0, Math.PI * 2);
      ctx.fillStyle = "#000000";
      ctx.fill();

      /* ── 8. Gravitational lensing ring ──────────────────── */
      const lensGrad = ctx.createRadialGradient(
        bh.cx, bh.cy, bh.r * 0.92,
        bh.cx, bh.cy, bh.r * 1.22
      );
      lensGrad.addColorStop(0,   "rgba(255,240,180,0)");
      lensGrad.addColorStop(0.45,"rgba(255,240,180,0.55)");
      lensGrad.addColorStop(0.55,"rgba(255,255,255,0.75)");
      lensGrad.addColorStop(0.65,"rgba(255,210,100,0.45)");
      lensGrad.addColorStop(1,   "rgba(255,200,80,0)");
      ctx.beginPath();
      ctx.arc(bh.cx, bh.cy, bh.r * 1.08, 0, Math.PI * 2);
      ctx.strokeStyle = lensGrad;
      ctx.lineWidth   = bh.r * 0.28;
      ctx.stroke();

      /* Faint outer halo */
      const haloGrad = ctx.createRadialGradient(
        bh.cx, bh.cy, bh.r,
        bh.cx, bh.cy, bh.r * 2.8
      );
      haloGrad.addColorStop(0,   "rgba(251,191,36,0.12)");
      haloGrad.addColorStop(0.5, "rgba(251,146,60,0.04)");
      haloGrad.addColorStop(1,   "transparent");
      ctx.beginPath();
      ctx.arc(bh.cx, bh.cy, bh.r * 2.8, 0, Math.PI * 2);
      ctx.fillStyle = haloGrad;
      ctx.fill();

      raf = requestAnimationFrame(draw);
    };
    draw();

    return () => {
      cancelAnimationFrame(raf);
      window.removeEventListener("resize", resize);
    };
  }, []);  // runs once; gravity/ozone read live from refs

  return (
    <canvas
      ref={canvasRef}
      style={{
        position: "fixed", inset: 0,
        width: "100%", height: "100%",
        zIndex: 0, pointerEvents: "none",
      }}
    />
  );
}
