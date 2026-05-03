"""
Gradio Chat Interface for BeatDebate Music Recommendation System

Modern dark-themed UI powered by the local track_data_final.csv dataset.
"""

import logging
import uuid
from typing import Dict, List, Optional, Tuple

import gradio as gr
import requests

from .response_formatter import ResponseFormatter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── Example queries shown in the UI ──────────────────────────────────────────
QUERY_EXAMPLES = {
    "By Artist": [
        "Songs by Taylor Swift",
        "Tracks by Kendrick Lamar",
        "Give me Billie Eilish songs",
        "Play some Lana Del Rey",
    ],
    "Similarity": [
        "Music similar to Lana Del Rey",
        "Songs like Ed Sheeran",
        "Similar artists to Kali Uchis",
        "Sounds like Porter Robinson",
    ],
    "Genre / Mood": [
        "Sad indie songs",
        "Upbeat pop music",
        "Chill lo-fi hip hop",
        "Electronic dance tracks",
    ],
    "Context": [
        "Music for studying",
        "Workout playlist songs",
        "Background music for coding",
        "Songs for a night drive",
    ],
}

# ── CSS ───────────────────────────────────────────────────────────────────────
CUSTOM_CSS = """
/* ── Base ─────────────────────────────────────────── */
.gradio-container {
    background: #0b0f1a !important;
    color: #e2e8f0 !important;
    font-family: 'Inter', 'Segoe UI', system-ui, sans-serif !important;
}
footer { display: none !important; }

/* ── Header ───────────────────────────────────────── */
#app-header {
    background: linear-gradient(135deg, #1a1f35 0%, #0f172a 100%);
    border: 1px solid rgba(139,92,246,0.25);
    border-radius: 16px;
    padding: 28px 32px;
    text-align: center;
    margin-bottom: 8px;
}
#app-header h1 {
    font-size: 2.2rem;
    font-weight: 800;
    background: linear-gradient(135deg, #a78bfa, #60a5fa, #34d399);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0 0 6px 0;
    letter-spacing: -0.5px;
}
#app-header p {
    color: #94a3b8;
    font-size: 0.95rem;
    margin: 0;
}

/* ── Example chips section ────────────────────────── */
#examples-section {
    background: #111827;
    border: 1px solid rgba(75,85,99,0.4);
    border-radius: 14px;
    padding: 20px 24px;
    margin-bottom: 8px;
}
#examples-section .label-wrap { display: none; }

.example-btn {
    background: rgba(30,41,59,0.9) !important;
    border: 1px solid rgba(100,116,139,0.4) !important;
    border-radius: 20px !important;
    color: #cbd5e1 !important;
    font-size: 13px !important;
    padding: 6px 14px !important;
    transition: all 0.18s ease !important;
    white-space: nowrap !important;
}
.example-btn:hover {
    background: rgba(139,92,246,0.2) !important;
    border-color: rgba(139,92,246,0.6) !important;
    color: #e2e8f0 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(139,92,246,0.2) !important;
}

/* ── Chatbot ──────────────────────────────────────── */
#chatbot-container .wrap {
    background: #111827 !important;
    border: 1px solid rgba(75,85,99,0.4) !important;
    border-radius: 14px !important;
}
#chatbot-container .message.user {
    background: linear-gradient(135deg, rgba(139,92,246,0.25), rgba(99,102,241,0.25)) !important;
    border: 1px solid rgba(139,92,246,0.3) !important;
    color: #e2e8f0 !important;
    border-radius: 14px 14px 4px 14px !important;
}
#chatbot-container .message.bot {
    background: rgba(30,41,59,0.8) !important;
    border: 1px solid rgba(75,85,99,0.35) !important;
    color: #cbd5e1 !important;
    border-radius: 14px 14px 14px 4px !important;
}
#chatbot-container .message p,
#chatbot-container .message li,
#chatbot-container .message h2,
#chatbot-container .message h3 {
    color: #cbd5e1 !important;
}
#chatbot-container .message h2 { color: #a78bfa !important; font-size: 1.05rem !important; }
#chatbot-container .message h3 { color: #7dd3fc !important; font-size: 0.95rem !important; }
#chatbot-container .message strong { color: #f1f5f9 !important; }
#chatbot-container .message a { color: #60a5fa !important; }

/* ── Input row ────────────────────────────────────── */
#input-row textarea {
    background: #1e2a3a !important;
    border: 1px solid rgba(100,116,139,0.5) !important;
    border-radius: 12px !important;
    color: #f1f5f9 !important;
    font-size: 15px !important;
    padding: 12px 16px !important;
    resize: none !important;
}
#input-row textarea:focus {
    border-color: rgba(139,92,246,0.7) !important;
    box-shadow: 0 0 0 3px rgba(139,92,246,0.15) !important;
    outline: none !important;
}
#input-row textarea::placeholder { color: #64748b !important; }

#send-btn {
    background: linear-gradient(135deg, #7c3aed, #4f46e5) !important;
    border: none !important;
    border-radius: 12px !important;
    color: white !important;
    font-weight: 600 !important;
    font-size: 15px !important;
    min-width: 90px !important;
    transition: all 0.18s ease !important;
}
#send-btn:hover {
    background: linear-gradient(135deg, #6d28d9, #4338ca) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(124,58,237,0.4) !important;
}

/* ── Track panel ──────────────────────────────────── */
#track-panel {
    background: #111827;
    border: 1px solid rgba(75,85,99,0.4);
    border-radius: 14px;
    overflow: hidden;
}

/* ── Sidebar info cards ───────────────────────────── */
.info-card {
    background: #111827;
    border: 1px solid rgba(75,85,99,0.35);
    border-radius: 14px;
    padding: 18px 20px;
    color: #94a3b8;
    font-size: 13.5px;
    line-height: 1.7;
}
.info-card h3 { color: #a78bfa !important; margin: 0 0 10px 0; font-size: 0.95rem; }
.info-card li { color: #cbd5e1 !important; }
.info-card strong { color: #e2e8f0 !important; }

/* ── Section labels ───────────────────────────────── */
.section-label {
    color: #64748b;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 8px;
}
"""


class BeatDebateChatInterface:
    """Main chat interface for BeatDebate."""

    def __init__(self, backend_url: str = "http://localhost:8000"):
        self.backend_url = backend_url
        self.formatter = ResponseFormatter()

    # ── Backend call ──────────────────────────────────────────────────────────

    def _get_recommendations(self, query: str, session_id: str) -> Optional[Dict]:
        try:
            resp = requests.post(
                f"{self.backend_url}/recommendations",
                json={
                    "query": query,
                    "session_id": session_id,
                    "max_recommendations": 8,
                    "include_previews": True,
                },
                timeout=30,
            )
            if resp.status_code == 200:
                return resp.json()
            logger.error(f"Backend returned {resp.status_code}: {resp.text[:200]}")
            return None
        except Exception as e:
            logger.error(f"Request failed: {e}")
            return None

    # ── Track panel HTML ──────────────────────────────────────────────────────

    def _build_track_panel(self, recommendations: List[Dict]) -> str:
        if not recommendations:
            return """
            <div style="padding:32px;text-align:center;color:#475569;">
                <div style="font-size:2.5rem;margin-bottom:12px;">🎵</div>
                <p style="margin:0;font-size:14px;">Ask for music to see tracks here</p>
            </div>
            """

        cards = []
        for i, rec in enumerate(recommendations):
            rank = i + 1
            title = rec.get("title", "Unknown")
            artist = rec.get("artist", "Unknown")
            album = rec.get("album", "")
            genres = rec.get("genres", [])
            popularity = rec.get("popularity", 0)
            duration = rec.get("duration", "")
            year = rec.get("release_year", "")
            confidence = rec.get("confidence", 0.0)
            explicit = rec.get("explicit", False)
            confidence_pct = int(confidence * 100)

            # Colour palette cycling
            palette = [
                ("#a78bfa", "rgba(167,139,250,0.12)"),
                ("#60a5fa", "rgba(96,165,250,0.12)"),
                ("#34d399", "rgba(52,211,153,0.12)"),
                ("#f472b6", "rgba(244,114,182,0.12)"),
                ("#fb923c", "rgba(251,146,60,0.12)"),
                ("#e879f9", "rgba(232,121,249,0.12)"),
                ("#38bdf8", "rgba(56,189,248,0.12)"),
                ("#a3e635", "rgba(163,230,53,0.12)"),
            ]
            accent, bg = palette[i % len(palette)]

            # Genre chips
            genre_chips = "".join(
                f'<span style="background:rgba(255,255,255,0.07);border:1px solid rgba(255,255,255,0.1);'
                f'border-radius:10px;padding:2px 8px;font-size:11px;color:#94a3b8;margin:2px;">{g}</span>'
                for g in genres[:3]
            )

            # Search URLs
            sq = f"{artist} {title}".replace(" ", "+")
            lfm = f"https://www.last.fm/search?q={sq}"
            spo = f"https://open.spotify.com/search/{sq}"
            ytb = f"https://www.youtube.com/results?search_query={sq}"

            meta_bits = []
            if year:
                meta_bits.append(year)
            if duration:
                meta_bits.append(duration)
            if popularity:
                meta_bits.append(f"Pop {popularity}")
            if explicit:
                meta_bits.append("E")
            meta_str = " · ".join(meta_bits)

            cards.append(f"""
            <div style="
                margin:10px 14px;
                padding:14px 16px;
                background:{bg};
                border:1px solid {accent}33;
                border-left:3px solid {accent};
                border-radius:10px;
                position:relative;
            ">
                <div style="position:absolute;top:-9px;left:12px;
                    background:{accent};color:#0b0f1a;
                    width:20px;height:20px;border-radius:50%;
                    display:flex;align-items:center;justify-content:center;
                    font-size:11px;font-weight:800;">
                    {rank}
                </div>

                <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-top:4px;">
                    <div style="flex:1;min-width:0;">
                        <div style="font-weight:700;color:#f1f5f9;font-size:14px;
                            white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">
                            {title}
                        </div>
                        <div style="color:{accent};font-size:13px;margin-top:2px;">{artist}</div>
                        {f'<div style="color:#64748b;font-size:11px;margin-top:1px;">{album}</div>' if album else ''}
                    </div>
                    <div style="background:{accent};color:#0b0f1a;padding:2px 8px;
                        border-radius:10px;font-size:11px;font-weight:700;
                        margin-left:10px;white-space:nowrap;">
                        {confidence_pct}%
                    </div>
                </div>

                {f'<div style="margin-top:6px;">{genre_chips}</div>' if genre_chips else ''}

                {f'<div style="color:#475569;font-size:11px;margin-top:5px;">{meta_str}</div>' if meta_str else ''}

                <div style="display:flex;gap:6px;margin-top:10px;">
                    <a href="{lfm}" target="_blank" style="
                        color:#ef4444;text-decoration:none;font-size:11px;font-weight:600;
                        padding:3px 9px;border-radius:6px;
                        background:rgba(239,68,68,0.12);border:1px solid rgba(239,68,68,0.3);">
                        Last.fm
                    </a>
                    <a href="{spo}" target="_blank" style="
                        color:#22c55e;text-decoration:none;font-size:11px;font-weight:600;
                        padding:3px 9px;border-radius:6px;
                        background:rgba(34,197,94,0.12);border:1px solid rgba(34,197,94,0.3);">
                        Spotify
                    </a>
                    <a href="{ytb}" target="_blank" style="
                        color:#f97316;text-decoration:none;font-size:11px;font-weight:600;
                        padding:3px 9px;border-radius:6px;
                        background:rgba(249,115,22,0.12);border:1px solid rgba(249,115,22,0.3);">
                        YouTube
                    </a>
                </div>
            </div>
            """)

        header = """
        <div style="padding:14px 18px 6px;
            background:linear-gradient(135deg,rgba(139,92,246,0.15),rgba(99,102,241,0.1));
            border-bottom:1px solid rgba(75,85,99,0.3);">
            <span style="color:#a78bfa;font-weight:700;font-size:14px;">Latest Tracks</span>
            <span style="color:#475569;font-size:12px;margin-left:8px;">click to listen</span>
        </div>
        <div style="max-height:520px;overflow-y:auto;padding-bottom:8px;">
        """
        return header + "".join(cards) + "</div>"

    # ── Message handler ───────────────────────────────────────────────────────

    def process_message(
        self,
        message: str,
        history: List[Tuple[str, str]],
        session_id: Optional[str],
    ) -> Tuple[str, List[Tuple[str, str]], str, str]:
        if not message.strip():
            return "", history, self._build_track_panel([]), session_id or ""

        if not session_id:
            session_id = str(uuid.uuid4())

        logger.info(f"Query: '{message}' | session={session_id[:8]}")

        data = self._get_recommendations(message, session_id)

        if data and data.get("recommendations"):
            reply = self.formatter.format_recommendations(data)
            track_html = self._build_track_panel(data["recommendations"])
        else:
            reply = (
                "**No results found.**\n\n"
                "Try queries like:\n"
                "- `Songs by Taylor Swift`\n"
                "- `Chill lo-fi music`\n"
                "- `Similar to Lana Del Rey`"
            )
            track_html = self._build_track_panel([])

        history.append((message, reply))
        return "", history, track_html, session_id

    # ── Build Gradio interface ────────────────────────────────────────────────

    def create_interface(self) -> gr.Blocks:
        with gr.Blocks(
            title="ManTarang – Music Discovery",
            theme=gr.themes.Base(
                primary_hue="violet",
                secondary_hue="indigo",
                neutral_hue="slate",
                font=gr.themes.GoogleFont("Inter"),
            ),
            css=CUSTOM_CSS,
        ) as interface:

            session_state = gr.State(None)

            # ── Header ──────────────────────────────────────────────────
            with gr.Column(elem_id="app-header"):
                gr.HTML("""
                <h1>ManTarang</h1>
                <p>Waves of sound &nbsp;·&nbsp; AI Music Discovery from 8,778 tracks</p>
                """)

            # ── Example query chips ──────────────────────────────────────
            with gr.Column(elem_id="examples-section"):
                gr.HTML('<p class="section-label">Try an example</p>')
                example_buttons: List[Tuple[gr.Button, str]] = []
                with gr.Row():
                    for category, examples in QUERY_EXAMPLES.items():
                        with gr.Column(min_width=160):
                            gr.HTML(f'<p style="color:#7c3aed;font-size:12px;font-weight:700;margin:0 0 6px 0;">{category}</p>')
                            for ex in examples:
                                btn = gr.Button(
                                    ex,
                                    elem_classes=["example-btn"],
                                    size="sm",
                                    variant="secondary",
                                )
                                example_buttons.append((btn, ex))

            # ── Main content ─────────────────────────────────────────────
            with gr.Row(equal_height=False):

                # Left: chat + input
                with gr.Column(scale=7):
                    chatbot = gr.Chatbot(
                        label="",
                        height=480,
                        elem_id="chatbot-container",
                        show_label=False,
                        render_markdown=True,
                        bubble_full_width=False,
                        type="tuples",
                    )
                    with gr.Row(elem_id="input-row"):
                        msg_input = gr.Textbox(
                            placeholder="What are you in the mood for?  e.g. 'sad indie songs' or 'tracks by Frank Ocean'",
                            label="",
                            scale=5,
                            lines=1,
                            show_label=False,
                            max_lines=3,
                        )
                        send_btn = gr.Button(
                            "Search",
                            scale=1,
                            variant="primary",
                            elem_id="send-btn",
                        )

                # Right: track panel + info
                with gr.Column(scale=3):
                    track_display = gr.HTML(
                        value=self._build_track_panel([]),
                        elem_id="track-panel",
                        label="",
                    )

                    gr.HTML("""
                    <div class="info-card" style="margin-top:10px;">
                        <h3>How it works</h3>
                        <ul style="margin:0;padding-left:18px;">
                            <li><strong>Artist search</strong> – "Songs by X"</li>
                            <li><strong>Similarity</strong> – "Like X" or "Similar to Y"</li>
                            <li><strong>Genre/Mood</strong> – "Sad indie", "Lo-fi chill"</li>
                            <li><strong>Context</strong> – "Music for studying"</li>
                        </ul>
                        <p style="margin:10px 0 0 0;color:#475569;font-size:12px;">
                            Powered by 8,778 tracks from Spotify data
                        </p>
                    </div>
                    """)

            # ── Wire events ──────────────────────────────────────────────

            def handle_message(message, history, session_id):
                return self.process_message(message, history, session_id)

            send_btn.click(
                fn=handle_message,
                inputs=[msg_input, chatbot, session_state],
                outputs=[msg_input, chatbot, track_display, session_state],
            )
            msg_input.submit(
                fn=handle_message,
                inputs=[msg_input, chatbot, session_state],
                outputs=[msg_input, chatbot, track_display, session_state],
            )

            for btn, text in example_buttons:
                btn.click(fn=lambda t=text: t, inputs=[], outputs=[msg_input])

        return interface


def create_chat_interface(backend_url: str = "http://localhost:8000") -> gr.Blocks:
    """Factory used by main.py / app.py."""
    return BeatDebateChatInterface(backend_url).create_interface()


if __name__ == "__main__":
    create_chat_interface().launch(server_name="0.0.0.0", server_port=7860)
