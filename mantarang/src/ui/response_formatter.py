"""
Response Formatter for BeatDebate

Turns recommendation dicts into clean Markdown for the Gradio chatbot.
"""

from typing import Any, Dict, List


class ResponseFormatter:
    """Formats CSV recommendation responses into readable Markdown."""

    def format_recommendations(self, data: Dict[str, Any]) -> str:
        recs: List[Dict] = data.get("recommendations", [])
        strategy: Dict = data.get("strategy_used", {})
        reasoning: List[str] = data.get("reasoning", [])
        proc_time: float = data.get("processing_time", 0.0)

        if not recs:
            return (
                "**No results found.**\n\n"
                "Try something like:\n"
                "- `Songs by [artist name]`\n"
                "- `Music similar to [artist]`\n"
                "- `Chill lo-fi / sad indie / upbeat pop`"
            )

        strategy_name = strategy.get("strategy", "search").replace("_", " ").title()
        lines: List[str] = []

        # ── Header ────────────────────────────────────────────────────────────
        lines += [
            f"### Found **{len(recs)} tracks** &nbsp;·&nbsp; *{strategy_name}* &nbsp;·&nbsp; `{proc_time:.2f}s`",
            "",
        ]

        # ── Track list ────────────────────────────────────────────────────────
        for i, rec in enumerate(recs, 1):
            title = rec.get("title", "Unknown")
            artist = rec.get("artist", "Unknown")
            album = rec.get("album", "")
            genres = rec.get("genres", [])
            confidence = rec.get("confidence", 0.0)
            explanation = rec.get("explanation", "")
            year = rec.get("release_year", "")
            duration = rec.get("duration", "")
            popularity = rec.get("popularity", 0)
            explicit = rec.get("explicit", False)

            confidence_pct = int(confidence * 100)
            conf_bar = self._conf_bar(confidence_pct)

            genre_str = " · ".join(genres[:4]) if genres else ""
            meta_parts = []
            if year:
                meta_parts.append(year)
            if duration:
                meta_parts.append(duration)
            if popularity:
                meta_parts.append(f"pop {popularity}/100")
            if explicit:
                meta_parts.append("explicit")
            meta_str = " · ".join(meta_parts)

            lines.append(f"**{i}. {title}** — *{artist}*")
            if album:
                lines.append(f"&nbsp;&nbsp;&nbsp;📀 {album}")
            lines.append(f"&nbsp;&nbsp;&nbsp;{conf_bar} **{confidence_pct}%** match")
            if explanation:
                lines.append(f"&nbsp;&nbsp;&nbsp;💡 {explanation}")
            if genre_str:
                lines.append(f"&nbsp;&nbsp;&nbsp;🎸 {genre_str}")
            if meta_str:
                lines.append(f"&nbsp;&nbsp;&nbsp;ℹ️ {meta_str}")
            lines.append("")

        # ── Reasoning footer ──────────────────────────────────────────────────
        if reasoning:
            lines += ["---", "*" + " · ".join(reasoning[:3]) + "*"]

        return "\n".join(lines)

    @staticmethod
    def _conf_bar(pct: int) -> str:
        filled = round(pct / 10)
        empty = 10 - filled
        return "🟩" * filled + "⬜" * empty
