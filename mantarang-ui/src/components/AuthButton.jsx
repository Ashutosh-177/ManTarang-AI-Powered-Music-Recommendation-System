import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useAuth } from "../context/AuthContext";

/* Google "G" SVG icon */
function GoogleIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 48 48" style={{ flexShrink: 0 }}>
      <path fill="#EA4335" d="M24 9.5c3.5 0 6.6 1.2 9 3.2l6.7-6.7C35.8 2.5 30.2 0 24 0 14.6 0 6.6 5.4 2.7 13.3l7.8 6C12.3 13.1 17.7 9.5 24 9.5z"/>
      <path fill="#4285F4" d="M46.5 24.5c0-1.6-.1-3.1-.4-4.5H24v8.5h12.7c-.6 3-2.3 5.5-4.8 7.2l7.5 5.8C43.8 37.3 46.5 31.4 46.5 24.5z"/>
      <path fill="#FBBC05" d="M10.5 28.7A14.5 14.5 0 0 1 9.5 24c0-1.6.3-3.2.7-4.7l-7.8-6A23.9 23.9 0 0 0 0 24c0 3.9.9 7.5 2.7 10.7l7.8-6z"/>
      <path fill="#34A853" d="M24 48c6.2 0 11.4-2 15.2-5.5l-7.5-5.8c-2 1.4-4.6 2.2-7.7 2.2-6.3 0-11.6-3.6-13.5-9l-7.8 6C6.6 42.6 14.6 48 24 48z"/>
    </svg>
  );
}

export default function AuthButton() {
  const { user, signing, signIn, logOut } = useAuth();
  const [menuOpen, setMenuOpen] = useState(false);
  const menuRef = useRef(null);

  // Close menu on outside click
  useEffect(() => {
    if (!menuOpen) return;
    const handler = (e) => {
      if (menuRef.current && !menuRef.current.contains(e.target)) setMenuOpen(false);
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, [menuOpen]);

  // Still detecting auth state
  if (user === undefined) return null;

  /* ── Signed in ─────────────────────────────────────────── */
  if (user) {
    return (
      <div ref={menuRef} style={{ position: "relative" }}>
        <button
          onClick={() => setMenuOpen(v => !v)}
          style={{
            display: "flex", alignItems: "center", gap: 8,
            background: "rgba(255,255,255,0.06)",
            border: "1px solid rgba(255,255,255,0.12)",
            borderRadius: 99, padding: "5px 12px 5px 5px",
            cursor: "pointer", color: "#e8f0ff", fontFamily: "inherit",
            fontSize: 13, fontWeight: 500, backdropFilter: "blur(12px)",
            transition: "background 0.2s",
          }}
          onMouseEnter={e => e.currentTarget.style.background = "rgba(255,255,255,0.10)"}
          onMouseLeave={e => e.currentTarget.style.background = "rgba(255,255,255,0.06)"}
        >
          {user.photoURL ? (
            <img
              src={user.photoURL}
              alt={user.displayName}
              style={{ width: 26, height: 26, borderRadius: "50%", objectFit: "cover" }}
              referrerPolicy="no-referrer"
            />
          ) : (
            <div style={{
              width: 26, height: 26, borderRadius: "50%",
              background: "linear-gradient(135deg,#7C3AED,#C9A227)",
              display: "flex", alignItems: "center", justifyContent: "center",
              fontSize: 12, fontWeight: 700, color: "#fff",
            }}>
              {user.displayName?.[0] ?? "?"}
            </div>
          )}
          <span style={{ maxWidth: 90, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
            {user.displayName?.split(" ")[0]}
          </span>
          <motion.svg
            animate={{ rotate: menuOpen ? 180 : 0 }} transition={{ duration: 0.18 }}
            width="12" height="12" viewBox="0 0 24 24" fill="none"
            stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"
            style={{ color: "#8b9eb8", flexShrink: 0 }}
          >
            <polyline points="6 9 12 15 18 9" />
          </motion.svg>
        </button>

        <AnimatePresence>
          {menuOpen && (
            <motion.div
              initial={{ opacity: 0, y: -6, scale: 0.97 }}
              animate={{ opacity: 1, y: 0,  scale: 1 }}
              exit={{   opacity: 0, y: -6, scale: 0.97 }}
              transition={{ duration: 0.15 }}
              style={{
                position: "absolute", top: "calc(100% + 8px)", right: 0,
                background: "rgba(4,8,28,0.96)", backdropFilter: "blur(20px)",
                border: "1px solid rgba(255,255,255,0.1)",
                borderRadius: 12, padding: 8, minWidth: 200, zIndex: 1000,
                boxShadow: "0 8px 32px rgba(0,0,0,0.5)",
              }}
            >
              <div style={{ padding: "8px 12px 10px", borderBottom: "1px solid rgba(255,255,255,0.07)" }}>
                <p style={{ margin: 0, fontSize: 13, fontWeight: 600, color: "#e8f0ff" }}>
                  {user.displayName}
                </p>
                <p style={{ margin: "2px 0 0", fontSize: 12, color: "#6a7a90", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                  {user.email}
                </p>
              </div>
              <button
                onClick={() => { setMenuOpen(false); logOut(); }}
                style={{
                  width: "100%", marginTop: 4,
                  background: "transparent", border: "none",
                  padding: "8px 12px", cursor: "pointer",
                  color: "#f87171", fontSize: 13, fontWeight: 500,
                  fontFamily: "inherit", textAlign: "left", borderRadius: 8,
                  transition: "background 0.15s",
                }}
                onMouseEnter={e => e.currentTarget.style.background = "rgba(248,113,113,0.08)"}
                onMouseLeave={e => e.currentTarget.style.background = "transparent"}
              >
                Sign out
              </button>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    );
  }

  /* ── Signed out ────────────────────────────────────────── */
  return (
    <motion.button
      onClick={signIn}
      disabled={signing}
      whileHover={{ scale: 1.03 }}
      whileTap={{  scale: 0.97 }}
      style={{
        display: "flex", alignItems: "center", gap: 8,
        background: signing ? "rgba(255,255,255,0.04)" : "rgba(255,255,255,0.08)",
        border: "1px solid rgba(255,255,255,0.15)",
        borderRadius: 99, padding: "7px 16px 7px 10px",
        cursor: signing ? "not-allowed" : "pointer",
        color: "#e8f0ff", fontFamily: "inherit",
        fontSize: 13, fontWeight: 600, backdropFilter: "blur(12px)",
        opacity: signing ? 0.6 : 1,
      }}
    >
      <GoogleIcon />
      {signing ? "Signing in…" : "Sign in with Google"}
    </motion.button>
  );
}
