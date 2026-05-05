"""
CSV-Based Music Recommendation Engine  v3

Sources:
  - track_data_final.csv   (8,778 Spotify tracks — genres, followers, popularity)
  - spotify_data clean.csv (genre enrichment)
  - MD-1M.csv              (1M tracks — emotion labels, audio features, playlist context)
                            top 100k by popularity are loaded to keep RAM manageable

MD-1M adds two new signals:
  1. Emotion scoring  — Primary_Emotion / Secondary_Emotion matched to detected mood
  2. Context scoring  — Primary_Playlist_Context matched to context keywords
"""

import ast
import os
import re
import random
import math
from typing import Dict, List, Optional, Tuple
from collections import Counter

import pandas as pd

# ── Dataset paths ──────────────────────────────────────────────────────────────
_BASE      = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
_MAIN_CSV  = os.path.join(_BASE, "track_data_final.csv")
_CLEAN_CSV = os.path.join(_BASE, "spotify_data clean.csv")
_MD1M_CSV  = os.path.join(_BASE, "MD-1M.csv")

# Max rows to load from MD-1M (top N by popularity keeps RAM under ~300 MB)
_MD1M_MAX_ROWS = 100_000


# ── Emotion → mood mapping (MD-1M Primary/Secondary_Emotion values) ────────────
_EMOTION_TO_MOOD: Dict[str, str] = {
    "melancholy": "sad",
    "sadness":    "sad",
    "longing":    "sad",
    "bittersweet":"sad",
    "joy":        "happy",
    "euphoria":   "happy",
    "excitement": "happy",
    "hope":       "happy",
    "empowerment":"happy",
    "love":       "romantic",
    "passion":    "romantic",
    "romance":    "romantic",
    "peace":      "chill",
    "serenity":   "chill",
    "anger":      "angry",
    "defiance":   "angry",
    "nostalgia":  "nostalgic",
    "fear":       "focused",
}

# MD-1M Primary_Playlist_Context → our context keywords
_PLAYLIST_CTX_MAP: Dict[str, str] = {
    "study session":      "studying",
    "focus":              "focus",
    "workout":            "workout",
    "late night vibes":   "night",
    "morning routine":    "morning",
    "chill":              "relax",
    "evening wind down":  "relax",
    "sleep":              "sleep",
    "party":              "party",
    "road trip":          "driving",
    "romance":            "romantic",
    "beach day":          "relax",
    "rainy day":          "relax",
}


# ── Genre / Mood / Context maps ────────────────────────────────────────────────
GENRE_ALIASES: Dict[str, List[str]] = {
    "pop":        ["pop", "synth-pop", "dream pop", "indie pop", "electropop",
                   "dark pop", "alternative pop", "soft pop", "art pop", "indie pop"],
    "rock":       ["rock", "indie rock", "alternative", "post-rock", "classic rock",
                   "punk rock", "grunge", "alternative rock", "garage rock"],
    "hip hop":    ["hip hop", "hip-hop", "rap", "trap", "drill", "boom bap",
                   "conscious rap", "cloud rap", "emo rap", "west coast hip hop"],
    "r&b":        ["r&b", "rnb", "soul", "neo soul", "contemporary r&b",
                   "dark r&b", "alternative r&b", "r&b pop"],
    "electronic": ["electronic", "edm", "house", "techno", "trance", "dubstep",
                   "drum and bass", "electro", "electronica", "progressive house"],
    "jazz":       ["jazz", "bebop", "swing", "fusion", "smooth jazz"],
    "classical":  ["classical", "orchestral", "opera", "symphony", "chamber",
                   "soundtrack", "score"],
    "country":    ["country", "americana", "bluegrass", "folk country",
                   "acoustic country", "classic country", "country hip hop"],
    "metal":      ["metal", "heavy metal", "death metal", "black metal",
                   "metalcore", "nu metal", "alternative metal", "rap metal"],
    "folk":       ["folk", "acoustic folk", "indie folk", "singer-songwriter", "acoustic"],
    "latin":      ["latin", "reggaeton", "salsa", "cumbia", "bachata",
                   "urbano latino", "trap latino"],
    "indie":      ["indie", "indie rock", "indie pop", "indie folk", "lo-fi indie",
                   "bedroom pop"],
    "lo-fi":      ["lo-fi", "lofi", "chillhop", "lo-fi hip hop", "lo-fi indie"],
    "dance":      ["dance", "dancehall", "house", "disco", "funk"],
    "k-pop":      ["k-pop", "k pop", "korean pop"],
    "anime":      ["anime", "j-pop", "j-rock", "vocaloid"],
    "bollywood":  ["bollywood", "hindi", "filmi", "item number"],
    "sufi":       ["sufi", "qawwali", "ghazal", "devotional"],
    "blues":      ["blues", "soul blues", "rhythm and blues"],
    "funk":       ["funk", "soul funk", "disco funk"],
}

MOOD_KEYWORDS: Dict[str, List[str]] = {
    "happy":      ["happy", "joy", "upbeat", "feel-good", "fun", "cheerful",
                   "positive", "good vibes", "feel good"],
    "sad":        ["sad", "melancholy", "heartbreak", "emotional", "depressing",
                   "grief", "crying", "breakup", "heartbroken"],
    "energetic":  ["energetic", "upbeat", "pump", "hype", "adrenaline", "power",
                   "intense", "high energy"],
    "chill":      ["chill", "relax", "mellow", "calm", "lo-fi", "lofi",
                   "ambient", "easy", "laid back", "lowkey"],
    "romantic":   ["romantic", "love", "date", "sensual", "passion", "intimate",
                   "romance", "crush"],
    "angry":      ["angry", "aggressive", "rage", "metal", "hardcore", "brutal",
                   "mad", "pissed"],
    "focused":    ["study", "focus", "concentration", "work", "productive",
                   "background", "concentrate", "deep work"],
    "workout":    ["workout", "gym", "exercise", "running", "training", "sport",
                   "fitness", "pump up"],
    "party":      ["party", "dance", "club", "banger", "celebration",
                   "night out", "turn up"],
    "sleep":      ["sleep", "lullaby", "night", "dream", "soothing", "bedtime",
                   "insomnia", "sleepy"],
    "nostalgic":  ["nostalgic", "nostalgia", "throwback", "old school",
                   "classic", "retro", "memories"],
}

CONTEXT_MAP: Dict[str, List[str]] = {
    "vibe coding":   ["lo-fi", "chillhop", "ambient", "electronic", "instrumental"],
    "vibe code":     ["lo-fi", "chillhop", "ambient", "electronic"],
    "coding":        ["lo-fi", "electronic", "ambient", "chillhop", "instrumental"],
    "code":          ["lo-fi", "electronic", "ambient", "instrumental"],
    "studying":      ["lo-fi", "ambient", "instrumental", "chillhop", "classical"],
    "study":         ["lo-fi", "ambient", "instrumental", "chillhop"],
    "working":       ["lo-fi", "ambient", "instrumental", "focus"],
    "work":          ["lo-fi", "ambient", "electronic", "instrumental"],
    "focus":         ["lo-fi", "ambient", "instrumental", "chillhop"],
    "concentrate":   ["lo-fi", "ambient", "instrumental"],
    "vibing":        ["lo-fi", "chill", "ambient", "chillhop", "indie"],
    "vibe":          ["lo-fi", "chill", "ambient", "indie", "chillhop"],
    "workout":       ["edm", "hip hop", "pop", "electronic", "rock"],
    "gym":           ["edm", "hip hop", "pop", "electronic"],
    "running":       ["edm", "pop", "electronic", "hip hop"],
    "driving":       ["rock", "pop", "hip hop", "alternative"],
    "sleeping":      ["ambient", "classical", "acoustic", "dream pop"],
    "sleep":         ["ambient", "classical", "acoustic"],
    "relaxing":      ["ambient", "lo-fi", "acoustic", "chill", "indie"],
    "relax":         ["ambient", "lo-fi", "acoustic"],
    "party":         ["pop", "hip hop", "edm", "dance"],
    "dancing":       ["pop", "edm", "dance", "hip hop"],
    "morning":       ["pop", "indie pop", "acoustic", "folk"],
    "night":         ["r&b", "ambient", "lo-fi", "alternative"],
    "sad":           ["indie", "dream pop", "folk", "bedroom pop", "alternative"],
    "heartbreak":    ["pop", "r&b", "soul", "indie"],
    "road trip":     ["rock", "pop", "country", "alternative"],
    "cooking":       ["jazz", "funk", "soul", "pop"],
}

MOOD_TO_GENRES: Dict[str, List[str]] = {
    "happy":     ["pop", "indie pop", "funk", "dance", "reggaeton"],
    "sad":       ["indie", "dream pop", "folk", "bedroom pop", "alternative"],
    "energetic": ["edm", "hip hop", "rock", "pop", "electronic"],
    "chill":     ["lo-fi", "ambient", "chillhop", "indie", "dream pop"],
    "romantic":  ["r&b", "soul", "pop", "jazz", "indie pop"],
    "angry":     ["metal", "rock", "hip hop", "grunge", "nu metal"],
    "focused":   ["lo-fi", "ambient", "classical", "chillhop", "instrumental"],
    "workout":   ["edm", "hip hop", "pop", "rock", "electronic"],
    "party":     ["pop", "edm", "hip hop", "dance", "reggaeton"],
    "sleep":     ["ambient", "classical", "acoustic", "dream pop"],
    "nostalgic": ["classic rock", "pop", "r&b", "country"],
}


# ── Singleton dataset ──────────────────────────────────────────────────────────
_df: Optional[pd.DataFrame] = None
_artist_genre_map: Optional[Dict[str, List[str]]] = None


def _parse_genre_list(raw) -> List[str]:
    if not isinstance(raw, str) or raw.strip() in ("", "[]", "nan", "NaN"):
        return []
    try:
        result = ast.literal_eval(raw)
        if isinstance(result, list):
            return [str(g).strip() for g in result if str(g).strip()]
    except Exception:
        pass
    cleaned = raw.strip("[]").replace("'", "").replace('"', "")
    return [g.strip() for g in cleaned.split(",") if g.strip()]


def _build_artist_genre_map(dfs: List[pd.DataFrame]) -> Dict[str, List[str]]:
    mapping: Dict[str, set] = {}
    for df in dfs:
        if "artist_name" not in df.columns or "genres_list" not in df.columns:
            continue
        for artist, genres in zip(df["artist_name"].str.lower().fillna(""), df["genres_list"]):
            if not artist or artist == "nan":
                continue
            if isinstance(genres, list) and genres:
                if artist not in mapping:
                    mapping[artist] = set()
                mapping[artist].update(genres)
    return {k: list(v) for k, v in mapping.items()}


def _load_md1m(max_rows: int = _MD1M_MAX_ROWS) -> pd.DataFrame:
    """Load MD-1M.csv, normalise to shared schema, cap at max_rows."""
    if not os.path.exists(_MD1M_CSV):
        return pd.DataFrame()

    cols_needed = [
        "Song_Name", "Primary_Singer", "Album_Name",
        "Genre", "Sub_Genre",
        "Platform_Popularity_Index", "Song_Duration_ms", "Explicit_Content",
        "Primary_Emotion", "Secondary_Emotion",
        "Valence", "Energy", "Danceability",
        "Primary_Playlist_Context", "Typical_Listening_Time",
        "Language",
    ]
    try:
        df = pd.read_csv(_MD1M_CSV, usecols=cols_needed)
    except Exception:
        return pd.DataFrame()

    df = df.rename(columns={
        "Song_Name":               "track_name",
        "Primary_Singer":          "artist_name",
        "Album_Name":              "album_name",
        "Platform_Popularity_Index": "track_popularity",
        "Song_Duration_ms":        "track_duration_ms",
        "Explicit_Content":        "explicit",
    })

    df["track_popularity"] = (
        pd.to_numeric(df["track_popularity"], errors="coerce")
        .fillna(50).clip(0, 100).round().astype(int)
    )
    df["track_duration_ms"] = pd.to_numeric(df["track_duration_ms"], errors="coerce").fillna(0)

    def build_genres(row) -> List[str]:
        genres: List[str] = []
        g = str(row.get("Genre", "") or "").strip()
        s = str(row.get("Sub_Genre", "") or "").strip()
        if g and g.lower() != "nan":
            genres.append(g)
        if s and s.lower() != "nan" and s not in genres:
            genres.append(s)
        return genres

    df["genres_list"] = df.apply(build_genres, axis=1)

    # Fields the shared pipeline expects
    df["artist_genres"]    = df["genres_list"].apply(str)
    df["artist_followers"] = 0
    df["artist_popularity"] = df["track_popularity"]
    df["album_release_date"] = ""
    df["source_dataset"]   = "md1m"

    df = df.dropna(subset=["track_name", "artist_name"])
    # Dedup first so nlargest picks from unique tracks only
    df = df.drop_duplicates(subset=["track_name", "artist_name"], keep="first")
    df = df.nlargest(max_rows, "track_popularity")
    return df


def _load_dataset() -> Tuple[pd.DataFrame, Dict[str, List[str]]]:
    # ── Load primary Spotify dataset ──────────────────────────────────────────
    df_main = pd.read_csv(_MAIN_CSV)
    df_main["genres_list"]    = df_main["artist_genres"].apply(_parse_genre_list)
    df_main["source_dataset"] = "spotify"

    # ── Load genre-enrichment CSV ──────────────────────────────────────────────
    df_clean = pd.DataFrame()
    if os.path.exists(_CLEAN_CSV):
        df_clean = pd.read_csv(_CLEAN_CSV)
        df_clean["genres_list"] = df_clean["artist_genres"].apply(_parse_genre_list)

    # ── Load MD-1M ─────────────────────────────────────────────────────────────
    df_md1m = _load_md1m()

    # ── Build merged artist→genre map across all sources ──────────────────────
    artist_genre_map = _build_artist_genre_map(
        [df_main]
        + ([df_clean] if len(df_clean) > 0 else [])
        + ([df_md1m]  if len(df_md1m) > 0 else [])
    )

    # ── Enrich main df: back-fill missing genres from merged map ──────────────
    def enrich_genres(row):
        if row["genres_list"]:
            return row["genres_list"]
        artist = str(row["artist_name"]).lower().strip()
        return artist_genre_map.get(artist, [])

    df_main["genres_list"] = df_main.apply(enrich_genres, axis=1)
    df_main = df_main.dropna(subset=["track_name", "artist_name"])

    # Add emotion columns absent in Spotify data
    for col in ["Primary_Emotion", "Secondary_Emotion", "Valence", "Energy",
                "Danceability", "Primary_Playlist_Context", "Typical_Listening_Time"]:
        if col not in df_main.columns:
            df_main[col] = None

    # ── Merge all into one DataFrame ──────────────────────────────────────────
    frames = [df_main]
    if len(df_md1m) > 0:
        for col in df_main.columns:
            if col not in df_md1m.columns:
                df_md1m[col] = None
        frames.append(df_md1m[df_main.columns])

    df_combined = pd.concat(frames, ignore_index=True)
    df_combined = df_combined.drop_duplicates(
        subset=["track_name", "artist_name"], keep="first"
    )

    # ── Index columns for fast lookup ─────────────────────────────────────────
    df_combined["genres_lower"] = df_combined["genres_list"].apply(
        lambda lst: [g.lower() for g in (lst if isinstance(lst, list) else [])]
    )
    df_combined["artist_lower"] = df_combined["artist_name"].str.lower().fillna("")
    df_combined["track_lower"]  = df_combined["track_name"].str.lower().fillna("")

    return df_combined, artist_genre_map


def get_df() -> pd.DataFrame:
    global _df, _artist_genre_map
    if _df is None:
        _df, _artist_genre_map = _load_dataset()
    return _df


def get_artist_genre_map() -> Dict[str, List[str]]:
    global _df, _artist_genre_map
    if _artist_genre_map is None:
        _df, _artist_genre_map = _load_dataset()
    return _artist_genre_map


# ── Query intent detection ─────────────────────────────────────────────────────

def _extract_artist(query: str) -> Optional[str]:
    q = query.lower()
    patterns = [
        r"(?:songs?|tracks?|music)\s+(?:by|from)\s+([a-z0-9 &''.,()\-]+?)(?:\s+that|\s+which|\s+but|\s+and|\s*$)",
        r"(?:give me|play|show me|recommend)\s+(?:some\s+)?([a-z0-9 &''.,()\-]+?)\s+(?:songs?|tracks?|music)",
        r"(?:similar\s+(?:to|artists?\s+to)|like|sounds like)\s+([a-z0-9 &''.,()\-]+?)(?:\s+but|\s+and|\s*$)",
        r"(?:discography|top songs?|best songs?)\s+(?:of|by|from)\s+([a-z0-9 &''.,()\-]+?)(?:\s*$)",
    ]
    for pat in patterns:
        m = re.search(pat, q)
        if m:
            c = m.group(1).strip().rstrip(",.")
            if len(c) > 1:
                return c
    return None


def _detect_genre(query: str) -> Optional[str]:
    q = query.lower()
    for genre, aliases in GENRE_ALIASES.items():
        for alias in aliases:
            if alias in q:
                return genre
    return None


def _detect_mood(query: str) -> Optional[str]:
    q = query.lower()
    for mood, keywords in MOOD_KEYWORDS.items():
        for kw in keywords:
            if kw in q:
                return mood
    return None


def _detect_context(query: str) -> Optional[str]:
    q = query.lower()
    for ctx in sorted(CONTEXT_MAP.keys(), key=len, reverse=True):
        if ctx in q:
            return ctx
    return None


def _is_similarity_query(query: str) -> bool:
    q = query.lower()
    return any(kw in q for kw in [
        "like ", "similar to", "sounds like", "reminds me of",
        "vibes like", "in the style of", "similar artists",
    ])


def _is_artist_query(query: str) -> bool:
    q = query.lower()
    return bool(re.search(
        r"(songs?|tracks?|music)\s+(by|from)|"
        r"(give me|play|show me)\s+.*(songs?|tracks?)|"
        r"(discography|top songs?|best songs?)",
        q,
    ))


# ── Scoring ────────────────────────────────────────────────────────────────────

def _genre_overlap_score(track_genres: List[str], target_genres: List[str]) -> float:
    if not track_genres or not target_genres:
        return 0.0
    tg = set(track_genres)
    tt = set(target_genres)
    matches = sum(1 for g in tg if any(t in g or g in t for t in tt))
    return min(1.0, matches / max(len(tt), 1))


def _emotion_score(row: pd.Series, target_mood: Optional[str]) -> float:
    """Score 0-1 based on how well track's emotion matches the target mood."""
    if not target_mood:
        return 0.0
    primary   = str(row.get("Primary_Emotion",   "") or "").lower().strip()
    secondary = str(row.get("Secondary_Emotion", "") or "").lower().strip()
    mapped_primary   = _EMOTION_TO_MOOD.get(primary,   "")
    mapped_secondary = _EMOTION_TO_MOOD.get(secondary, "")
    score = 0.0
    if mapped_primary   == target_mood: score += 1.0
    if mapped_secondary == target_mood: score += 0.5
    return min(1.0, score)


def _context_score(row: pd.Series, target_context: Optional[str]) -> float:
    """Score 0-1 based on Primary_Playlist_Context match."""
    if not target_context:
        return 0.0
    ctx = str(row.get("Primary_Playlist_Context", "") or "").lower().strip()
    mapped = _PLAYLIST_CTX_MAP.get(ctx, "")
    return 1.0 if mapped == target_context else 0.0


def _score_and_rank(
    df: pd.DataFrame,
    target_genres: List[str],
    target_mood: Optional[str] = None,
    target_context: Optional[str] = None,
    boost_popularity: bool = True,
    shuffle: float = 0.12,
) -> pd.DataFrame:
    scored = df.copy()
    n = len(scored)
    if n == 0:
        return scored

    # 1. Popularity score (0-1)
    max_pop = max(scored["track_popularity"].max(), 1)
    scored["_pop_score"] = scored["track_popularity"] / max_pop

    # 2. Genre match score (0-1)
    if target_genres:
        tg_lower = [g.lower() for g in target_genres]
        scored["_genre_score"] = scored["genres_lower"].apply(
            lambda gl: _genre_overlap_score(gl, tg_lower)
        )
    else:
        scored["_genre_score"] = 0.0

    # 3. Emotion score (0-1) — uses MD-1M emotion labels where available
    if target_mood:
        scored["_emotion_score"] = scored.apply(
            lambda row: _emotion_score(row, target_mood), axis=1
        )
    else:
        scored["_emotion_score"] = 0.0

    # 4. Context score (0-1) — uses MD-1M Primary_Playlist_Context
    if target_context:
        scored["_context_score"] = scored.apply(
            lambda row: _context_score(row, target_context), axis=1
        )
    else:
        scored["_context_score"] = 0.0

    # 5. Artist diversity penalty
    artist_counts: Counter = Counter()
    diversity_pen = []
    for artist in scored["artist_lower"]:
        artist_counts[artist] += 1
        cnt = artist_counts[artist]
        pen = 1.0 if cnt == 1 else (0.6 if cnt == 2 else 0.2)
        diversity_pen.append(pen)
    scored["_diversity_score"] = diversity_pen

    # 6. Shuffle noise
    scored["_noise"] = [random.uniform(0, shuffle) for _ in range(n)]

    # 7. Weighted total
    # When emotion/context signals are strong, reduce genre weight slightly
    has_emotion  = target_mood    is not None
    has_context  = target_context is not None
    pop_w     = 0.30 if boost_popularity else 0.12
    genre_w   = 0.32 if (has_emotion or has_context) else 0.40
    emotion_w = 0.15 if has_emotion  else 0.0
    context_w = 0.10 if has_context  else 0.0
    div_w     = 0.10
    noise_w   = 0.08

    scored["_total"] = (
        scored["_pop_score"]      * pop_w     +
        scored["_genre_score"]    * genre_w   +
        scored["_emotion_score"]  * emotion_w +
        scored["_context_score"]  * context_w +
        scored["_diversity_score"] * div_w    +
        scored["_noise"]          * noise_w
    )

    return scored.sort_values("_total", ascending=False)


# ── Build recommendation records ───────────────────────────────────────────────

def _make_rec(row: pd.Series, rank: int, source: str,
              target_genres: List[str]) -> Dict:
    genres     = row["genres_list"] if isinstance(row["genres_list"], list) else []
    genres_low = row["genres_lower"] if isinstance(row["genres_lower"], list) else []
    pop        = int(row["track_popularity"])

    # Genre Match (0-100)
    genre_match = round(
        _genre_overlap_score(genres_low, [g.lower() for g in target_genres]) * 100
    ) if target_genres else 0

    # Popularity Fit (0-100)
    popularity_fit = round((pop / 100) * 100)

    # Artist Score (0-100) — log-normalised followers; fallback to popularity for MD-1M
    followers = float(row.get("artist_followers", 0) or 0)
    if followers > 0:
        artist_score = round(min(100, max(0, (math.log10(max(followers, 1)) / 8) * 100)))
    else:
        artist_score = round(min(100, max(0, pop * 0.85)))

    # Overall Relevance
    relevance = round(genre_match * 0.45 + popularity_fit * 0.30 + artist_score * 0.25)

    # Explanation
    reasons = []
    emotion = str(row.get("Primary_Emotion", "") or "").strip()
    if emotion and emotion.lower() != "nan":
        reasons.append(f"{emotion} mood")
    if genre_match >= 60:
        matched = [g for g in genres_low
                   if any(t in g or g in t for t in [x.lower() for x in target_genres])]
        reasons.append(f"Strong genre match: {', '.join(matched[:2]) or ', '.join(genres[:2])}")
    elif genre_match > 0:
        reasons.append(f"Partial genre overlap ({genre_match}%)")
    if pop >= 75:
        reasons.append(f"High popularity ({pop}/100)")
    elif pop >= 50:
        reasons.append(f"Moderate popularity ({pop}/100)")
    if source == "artist_match":
        reasons.append("Direct artist match")
    elif source == "similarity":
        reasons.append("Shares genre DNA with reference artist")
    if not reasons:
        reasons.append(f"Curated from {source.replace('_', ' ')}")

    duration_ms  = row.get("track_duration_ms", 0)
    duration_sec = int(duration_ms / 1000) if duration_ms else 0
    mins, secs   = divmod(duration_sec, 60)

    return {
        "rank":         rank,
        "title":        row["track_name"],
        "artist":       row["artist_name"],
        "album":        row["album_name"] if pd.notna(row.get("album_name", "")) else "",
        "genres":       genres[:4],
        "confidence":   round(min(1.0, (
            genre_match * 0.50 + artist_score * 0.30 + popularity_fit * 0.20
        ) / 100), 3),
        "source":       source,
        "explanation":  " · ".join(reasons),
        "popularity":   pop,
        "duration":     f"{mins}:{secs:02d}",
        "release_year": str(row.get("album_release_date", ""))[:4],
        "explicit":     bool(row.get("explicit", False)),
        "emotion":      emotion or None,
        "metrics": {
            "genre_match":    genre_match,
            "popularity_fit": popularity_fit,
            "artist_score":   artist_score,
            "relevance":      relevance,
            "target_genres":  target_genres[:4],
        },
    }


def _rows_to_recs(df: pd.DataFrame, n: int, source: str,
                  target_genres: List[str]) -> List[Dict]:
    recs, seen = [], set()
    for _, row in df.iterrows():
        key = (row["artist_lower"], row["track_lower"])
        if key in seen:
            continue
        seen.add(key)
        recs.append(_make_rec(row, len(recs) + 1, source, target_genres))
        if len(recs) >= n:
            break
    return recs


# ── Main recommendation entry point ───────────────────────────────────────────

def get_recommendations(query: str, n: int = 8) -> Dict:
    df  = get_df()
    agm = get_artist_genre_map()
    q   = query.strip().lower()

    recs:          List[Dict] = []
    strategy:      str        = "general"
    reasoning:     List[str]  = []
    target_genres: List[str]  = []

    # Detect mood and context upfront — passed to scoring
    mood    = _detect_mood(q)
    context = _detect_context(q)

    # ── 1. Artist-by-name ─────────────────────────────────────────────────────
    candidate_artist = _extract_artist(q)
    if _is_artist_query(q) or (
        candidate_artist
        and not _is_similarity_query(q)
        and not _detect_genre(q)
    ):
        if candidate_artist:
            mask = df["artist_lower"].str.contains(
                re.escape(candidate_artist), regex=True, na=False
            )
            adf = df[mask]
            if len(adf) >= 2:
                tg = agm.get(candidate_artist, [])
                if not tg:
                    tg = [g for gl in adf["genres_lower"].tolist()[:20] for g in gl]
                target_genres = list(set(tg))[:6]
                scored = _score_and_rank(adf, target_genres, mood, context,
                                         boost_popularity=True, shuffle=0.08)
                recs = _rows_to_recs(scored, n, "artist_match", target_genres)
                strategy = "artist_match"
                reasoning.append(f"Found {len(adf)} tracks by '{candidate_artist.title()}'")
                if target_genres:
                    reasoning.append(f"Artist genres: {', '.join(target_genres[:4])}")

    # ── 2. Similarity ─────────────────────────────────────────────────────────
    if not recs and _is_similarity_query(q):
        ref_artist = _extract_artist(q) or candidate_artist
        if ref_artist:
            ref_mask = df["artist_lower"].str.contains(
                re.escape(ref_artist), regex=True, na=False
            )
            ref_df = df[ref_mask]

            ref_genres: List[str] = agm.get(ref_artist, [])
            if not ref_genres and len(ref_df) > 0:
                ref_genres = [g for gl in ref_df["genres_lower"].tolist()[:20] for g in gl]
            ref_genres    = list(set(ref_genres))[:8]
            target_genres = ref_genres
            reasoning.append(f"Reference: '{ref_artist.title()}' → genres: {ref_genres[:4]}")

            if ref_genres:
                rg_set = set(r.lower() for r in ref_genres)
                def has_genre_overlap(gl):
                    return any(any(r in g or g in r for r in rg_set) for g in gl)
                sim_df = df[df["genres_lower"].apply(has_genre_overlap) & ~ref_mask]
                if len(sim_df) >= 3:
                    scored = _score_and_rank(sim_df, ref_genres, mood, context,
                                             boost_popularity=False, shuffle=0.15)
                    recs = _rows_to_recs(scored, n, "similarity", target_genres)
                    strategy = "similarity"
                    reasoning.append(f"{len(sim_df)} tracks share genre DNA")

            if not recs and len(ref_df) > 0:
                ref_pop = ref_df["artist_popularity"].dropna().mean() if "artist_popularity" in ref_df else None
                if ref_pop and not pd.isna(ref_pop):
                    tier_df = df[
                        ~ref_mask &
                        (df["artist_popularity"] >= max(0, ref_pop - 25)) &
                        (df["artist_popularity"] <= min(100, ref_pop + 25))
                    ]
                    if len(tier_df) >= 3:
                        scored = _score_and_rank(tier_df, [], mood, context,
                                                 boost_popularity=True, shuffle=0.2)
                        recs = _rows_to_recs(scored, n, "similarity", target_genres)
                        strategy = "similarity"
                        reasoning.append(f"Matched by popularity tier (~{int(ref_pop)})")

    # ── 3. Genre / Mood / Context ─────────────────────────────────────────────
    if not recs:
        genre = _detect_genre(q)

        tg: List[str] = []
        if genre:   tg += GENRE_ALIASES.get(genre, [genre])
        if mood:    tg += MOOD_TO_GENRES.get(mood, [])
        if context: tg += CONTEXT_MAP.get(context, [])

        seen_tg: set = set()
        target_genres = []
        for g in tg:
            if g not in seen_tg:
                seen_tg.add(g)
                target_genres.append(g)

        if target_genres or mood or context:
            scored = _score_and_rank(df, target_genres, mood, context,
                                     boost_popularity=True, shuffle=0.12)
            recs = _rows_to_recs(scored, n, "genre_mood", target_genres)
            strategy = "genre_mood"
            parts = []
            if genre:   parts.append(f"genre={genre}")
            if mood:    parts.append(f"mood={mood}")
            if context: parts.append(f"context={context}")
            reasoning.append(" | ".join(parts))
            if target_genres:
                reasoning.append(f"Matched against: {', '.join(target_genres[:5])}")

    # ── 4. Keyword text match ─────────────────────────────────────────────────
    STOPWORDS = {
        "song", "songs", "track", "tracks", "music", "play", "give", "show",
        "some", "more", "like", "that", "this", "with", "from", "want", "need",
        "find", "good", "best", "cool", "vibe", "vibes", "feel", "mood", "for",
        "the", "and", "please", "recommend", "something", "anything",
    }
    if not recs:
        words = [w for w in re.split(r"\W+", q) if len(w) > 3 and w not in STOPWORDS]
        if words:
            pat = "|".join(re.escape(w) for w in words[:6])
            mask = (
                df["artist_lower"].str.contains(pat, regex=True, na=False) |
                df["track_lower"].str.contains(pat, regex=True, na=False)
            )
            mdf = df[mask]
            if len(mdf) >= 2:
                scored = _score_and_rank(mdf, [], mood, context, shuffle=0.2)
                recs = _rows_to_recs(scored, n, "text_match", [])
                strategy = "text_match"
                reasoning.append(f"Keyword match: {words[:4]}")

    # ── 5. Popular fallback ───────────────────────────────────────────────────
    if not recs:
        scored = _score_and_rank(df, [], mood, context,
                                 boost_popularity=True, shuffle=0.25)
        recs = _rows_to_recs(scored, n, "popular_fallback", [])
        strategy = "popular_fallback"
        reasoning.append("No strong match found — showing popular diverse tracks")

    # ── Aggregate metrics ─────────────────────────────────────────────────────
    if recs:
        avg_relevance    = round(sum(r["metrics"]["relevance"]    for r in recs) / len(recs))
        avg_genre_match  = round(sum(r["metrics"]["genre_match"]  for r in recs) / len(recs))
        avg_confidence   = round(sum(r["confidence"]              for r in recs) / len(recs), 3)
        genre_diversity  = len(set(g for r in recs for g in r["genres"]))
        artist_diversity = len(set(r["artist"] for r in recs))
        strategy_premium = {"artist_match": 10, "similarity": 8, "genre_mood": 6,
                            "text_match": 4, "popular_fallback": 0}.get(strategy, 5)
        diversity_bonus  = min(10, genre_diversity)
        system_confidence = round(min(100, avg_confidence * 100 * 0.75
                                      + strategy_premium + diversity_bonus))
    else:
        avg_relevance = avg_genre_match = genre_diversity = artist_diversity = 0
        avg_confidence = 0.0
        system_confidence = 0

    return {
        "recommendations": recs,
        "strategy_used":   {"strategy": strategy},
        "reasoning":       reasoning,
        "query":           query.strip(),
        "aggregate_metrics": {
            "avg_relevance":     avg_relevance,
            "avg_genre_match":   avg_genre_match,
            "avg_confidence":    avg_confidence,
            "system_confidence": system_confidence,
            "genre_diversity":   genre_diversity,
            "artist_diversity":  artist_diversity,
            "total_results":     len(recs),
            "target_genres":     target_genres[:5],
            "strategy":          strategy,
        },
    }
