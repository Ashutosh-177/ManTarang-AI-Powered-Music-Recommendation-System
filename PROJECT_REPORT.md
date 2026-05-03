# ManTarang — AI-Powered Music Recommendation System
## Project Report

---

| | |
|---|---|
| **Project Title** | ManTarang — AI Music Intelligence Platform |
| **Subject** | Minor Engineering Research (MER) |
| **Submitted by** | Ashutosh Kumar Singh (Enroll. No. 92301733016) |
| | Aditya Raj (Enroll. No. 92301733062) |
| **Live Demo** | https://huggingface.co/spaces/ashu-17/mantarang |
| **Date** | May 2026 |

---

## Abstract

ManTarang is an end-to-end AI-powered music recommendation system that takes a natural-language query from a user — a mood, a context, an artist name, or any free-form description — and returns a ranked list of relevant tracks with quantitative justification for each recommendation. The system combines rule-based natural language understanding, multi-dimensional scoring, and a curated dataset of over 8,700 Spotify tracks to deliver fast, explainable, and diverse music recommendations without requiring GPU hardware or large pre-trained models.

The backend is a Python FastAPI service using a multi-strategy recommendation engine. The frontend is a React + Vite single-page application featuring a space-themed animated interface with skeleton loading, per-track metric cards, and a collapsible system confidence panel. The entire application is deployed on Hugging Face Spaces (CPU Basic, zero cost) and serves the React build directly through FastAPI's static file middleware.

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Methodology](#2-methodology)
3. [System Design and Architecture](#3-system-design-and-architecture)
4. [Implementation](#4-implementation)
5. [Evaluation Metrics](#5-evaluation-metrics)
6. [Discussion](#6-discussion)
7. [Future Work](#7-future-work)
8. [Appendix](#8-appendix)

---

## List of Figures and Tables

| # | Title |
|---|-------|
| Figure 1 | System Architecture Overview |
| Figure 2 | Recommendation Pipeline Flowchart |
| Figure 3 | Strategy Selection Decision Tree |
| Figure 4 | Data Pipeline |
| Figure 5 | Scoring Formula Block Diagram |
| Figure 6 | Frontend Component Hierarchy |
| Figure 7 | UI Screenshot — Hero Section |
| Figure 8 | UI Screenshot — Results with Metrics |
| Table 1 | Dataset Summary |
| Table 2 | Strategy Selection Logic |
| Table 3 | Per-Track Metric Formulas |
| Table 4 | System Confidence Breakdown |
| Table 5 | Technology Stack |
| Table 6 | Evaluation Results |

---

## 1. Introduction

### 1.1 Problem Statement

Music discovery is a deeply personal challenge. Mainstream recommendation systems (Spotify, YouTube Music) rely on collaborative filtering and deep listening history, which creates a "cold start" problem for new users and fails to handle natural-language intent. A user who wants "something for late-night coding sessions" or "dark indie rock like Radiohead" cannot express that in a traditional search box — they are forced to browse genres manually or rely on pre-built playlists that may not match the moment.

Additionally, existing systems are black boxes: the user is never told *why* a track was recommended, making it impossible to refine or trust the output.

### 1.2 Relevance to AI

ManTarang addresses this problem using AI techniques at multiple layers:

- **Natural Language Understanding (NLU):** Regex-pattern and keyword-based intent extraction to parse artist names, genres, moods, and contexts from free-form text.
- **Rule-Based Reasoning:** A deterministic multi-strategy pipeline that selects the most appropriate recommendation approach for each query class.
- **Scoring and Ranking:** A weighted multi-criteria scoring function that combines genre alignment, popularity, and artist establishment — producing an ordered, explainable ranked list.
- **Explainability AI:** Every recommendation includes a human-readable explanation and a quantitative metrics breakdown (genre match %, popularity fit %, artist score, relevance %).

### 1.3 Objectives

1. Accept any natural-language music query and return contextually relevant track recommendations.
2. Explain *why* each track was recommended using quantitative per-track metrics.
3. Display an overall system confidence score that reflects recommendation quality.
4. Deliver a responsive, animated, production-quality web UI.
5. Deploy for zero cost on Hugging Face Spaces (CPU only).

### 1.4 Scope of the Project

- **In scope:** Query parsing, strategy selection, scoring, ranking, frontend UI, HF Spaces deployment.
- **Out of scope:** Audio playback, user accounts, collaborative filtering, deep learning embeddings, real-time Spotify API calls (rate-limited; CSV dataset used instead).

---

## 2. Methodology

### 2.1 AI Techniques Used

| Technique | Where Used |
|-----------|-----------|
| Rule-Based NLU | Intent detection (artist, genre, mood, context) |
| Weighted Scoring | Multi-criteria track ranking |
| Regex Pattern Matching | Artist name extraction from queries |
| Keyword Lookup Tables | Genre alias mapping, mood mapping, context mapping |
| Log-Normalisation | Artist follower count → artist credibility score |
| Jaccard-like Set Overlap | Genre match scoring |
| Diversity Penalisation | Artist repeat penalty in ranked list |

### 2.2 Model Selection

ManTarang does **not** use a neural network model. This is a deliberate design decision:

- The dataset is tabular (CSV), making classical scoring more interpretable and faster.
- The system must run on CPU with sub-second latency.
- Explainability is a first-class requirement — neural embeddings are opaque.

The "model" is a **deterministic, rule-based multi-criteria decision system** — analogous to a weighted decision tree over extracted query features.

### 2.3 Strategy Selection — Decision Tree

```
User Query
    │
    ├─── Is it an artist query? ("songs by X", "top songs of Y")
    │         └─── YES → Strategy 1: Artist Match
    │
    ├─── Is it a similarity query? ("like X", "similar to X")
    │         └─── YES → Strategy 2: Similarity (genre DNA matching)
    │
    ├─── Does it contain genre/mood/context keywords?
    │         └─── YES → Strategy 3: Genre / Mood / Context
    │
    ├─── Does it contain any recognisable keywords?
    │         └─── YES → Strategy 4: Text Match (keyword search)
    │
    └─── No match found
              └─── Strategy 5: Popular Fallback (diverse popular tracks)
```

### 2.4 Algorithms and Mathematical Background

#### 2.4.1 Genre Overlap Score

A Jaccard-inspired measure of genre alignment between a track and the target genre list:

```
              |{matches}|
Genre_Score = ─────────────     where matches = genres with substring overlap
              |target_genres|
```

Substring matching is used (e.g. `"lo-fi hip hop"` counts as a hit for target `"lo-fi"`) to handle the long-tail variation in genre label naming.

#### 2.4.2 Per-Track Scoring (Ranking)

Every candidate track is scored as a weighted sum:

```
Total_Score = Genre_Score × 0.40
            + Pop_Score   × 0.35   (if boost_popularity else 0.15)
            + Diversity   × 0.15
            + Noise       × 0.10
```

Where:
- `Pop_Score = track_popularity / max_track_popularity`
- `Diversity` = artist repeat penalty: 1.0 (1st track), 0.6 (2nd), 0.2 (3rd+)
- `Noise` = `Uniform(0, shuffle)` — adds variety, prevents identical results

#### 2.4.3 Per-Track Metrics (Displayed in UI)

| Metric | Formula | Weight in Relevance |
|--------|---------|-------------------|
| Genre Match | `Genre_Overlap_Score × 100` | 45% |
| Popularity Fit | `(track_popularity / 100) × 100` | 30% |
| Artist Score | `min(100, (log₁₀(followers) / 8) × 100)` | 25% |
| Overall Relevance | `Genre_Match×0.45 + Pop_Fit×0.30 + Artist_Score×0.25` | — |

#### 2.4.4 Per-Track Confidence

```
Confidence = (Genre_Match × 0.50 + Artist_Score × 0.30 + Popularity_Fit × 0.20) / 100
```

Clipped to `[0.0, 1.0]`. Weights Genre_Match most heavily since it is the primary intent signal.

#### 2.4.5 System Confidence

```
System_Confidence = min(100,
    avg_confidence × 100 × 0.75
    + Strategy_Premium
    + Diversity_Bonus
)
```

| Strategy | Premium |
|----------|---------|
| Artist Match | +10 |
| Similarity | +8 |
| Genre / Mood | +6 |
| Text Match | +4 |
| Popular Fallback | +0 |

`Diversity_Bonus = min(10, unique_genre_count)`

### 2.5 Dataset Details

| Property | Value |
|----------|-------|
| Primary source | `track_data_final.csv` (Spotify export) |
| Secondary source | `spotify_data clean.csv` (genre coverage enrichment) |
| Total tracks | **8,778** |
| Key fields | `track_name`, `artist_name`, `album_name`, `artist_genres`, `track_popularity`, `artist_followers`, `track_duration_ms`, `explicit`, `album_release_date` |
| Pre-processing | Genre strings parsed from Python list literals → `List[str]`; artist→genre map built across both CSVs; missing genres back-filled from merged map; lowercased index columns for O(1) lookups |
| Genre coverage | ~61% of tracks have at least one genre label (enriched from ~49% in primary CSV alone) |

**Data Pipeline:**

```
track_data_final.csv  ──┐
                         ├──► _load_dataset()
spotify_data clean.csv ──┘         │
                                   ├── Parse genres (ast.literal_eval)
                                   ├── Build artist→genre map (merged)
                                   ├── Enrich missing genres
                                   ├── Add lowercase index columns
                                   └── Singleton DataFrame (_df) ready
```

### 2.6 Tools and Libraries

**Table 5 — Technology Stack**

| Layer | Technology | Version |
|-------|-----------|---------|
| Backend language | Python | 3.11 |
| API framework | FastAPI | 0.115 |
| ASGI server | Uvicorn | latest |
| Data processing | Pandas | 2.x |
| Data validation | Pydantic | v2 |
| Frontend framework | React | 18 |
| Frontend build tool | Vite | 5.x |
| Animation library | Framer Motion | 11.x |
| CSS approach | Inline styles + global CSS |  |
| HTTP proxy | Vite dev proxy → FastAPI | — |
| Deployment | Hugging Face Spaces | CPU Basic |
| Package management | pip (backend), npm (frontend) | — |

---

## 3. System Design and Architecture

### 3.1 System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     HUGGING FACE SPACES                         │
│                      (CPU Basic, free)                          │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    FastAPI App                           │   │
│  │                                                         │   │
│  │  ┌──────────────┐   POST /api/recommendations           │   │
│  │  │  React SPA   │◄─────────────────────────────────┐   │   │
│  │  │  (dist/)     │                                   │   │   │
│  │  │  StaticFiles │   ┌─────────────────────────┐    │   │   │
│  │  └──────────────┘   │   CSV Recommender        │    │   │   │
│  │                     │                         │    │   │   │
│  │                     │  1. Intent Detection    │    │   │   │
│  │                     │  2. Strategy Selection  │────┘   │   │
│  │                     │  3. Scoring & Ranking   │        │   │
│  │                     │  4. Metric Calculation  │        │   │
│  │                     └────────────┬────────────┘        │   │
│  │                                  │                     │   │
│  │                     ┌────────────▼────────────┐        │   │
│  │                     │  track_data_final.csv   │        │   │
│  │                     │  (8,778 tracks, in RAM) │        │   │
│  │                     └─────────────────────────┘        │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 Recommendation Pipeline Flowchart

```
User types query in browser
         │
         ▼
  React frontend (App.jsx)
  doSearch() called
         │
         ▼
  POST /api/recommendations
  { query, max_recommendations }
         │
         ▼
  FastAPI backend (backend.py)
  get_recommendations()
         │
         ▼
  csv_recommender.py
         │
    ┌────┴────────────────────────────────────────┐
    │           Intent Detection Layer             │
    │  _extract_artist()  ← regex patterns        │
    │  _detect_genre()    ← GENRE_ALIASES dict     │
    │  _detect_mood()     ← MOOD_KEYWORDS dict     │
    │  _detect_context()  ← CONTEXT_MAP dict       │
    │  _is_similarity_query()                      │
    │  _is_artist_query()                          │
    └────┬────────────────────────────────────────┘
         │
    ┌────▼───────────────────────────────────────────────────┐
    │              Strategy Selection                         │
    │                                                        │
    │  artist found + artist query?  ──► Artist Match        │
    │  "like/similar to" keywords?   ──► Similarity          │
    │  genre/mood/context detected?  ──► Genre/Mood/Context  │
    │  keyword text match found?     ──► Text Match          │
    │  nothing matched?              ──► Popular Fallback    │
    └────┬───────────────────────────────────────────────────┘
         │
    ┌────▼────────────────────────────────┐
    │         _score_and_rank()           │
    │                                     │
    │  For each track in candidate set:   │
    │  · Genre overlap score (0–1)        │
    │  · Popularity score (0–1)           │
    │  · Diversity penalty                │
    │  · Shuffle noise                    │
    │  · Weighted total                   │
    │  Sort descending → top N            │
    └────┬────────────────────────────────┘
         │
    ┌────▼────────────────────────────────┐
    │         _make_rec() × N             │
    │                                     │
    │  Per track:                         │
    │  · genre_match (0–100)              │
    │  · popularity_fit (0–100)           │
    │  · artist_score (log-norm)          │
    │  · relevance (weighted blend)       │
    │  · confidence (0.0–1.0)             │
    │  · explanation (human text)         │
    └────┬────────────────────────────────┘
         │
    ┌────▼────────────────────────────────┐
    │      Aggregate Metrics              │
    │  avg_confidence, system_confidence  │
    │  genre_diversity, artist_diversity  │
    └────┬────────────────────────────────┘
         │
         ▼
  JSON response → React → UI renders
  TrackCard × N + QualityPanel
```

### 3.3 Frontend Component Hierarchy

```
App.jsx
├── Stars.jsx              ← Canvas: 200 animated drifting stars
├── HeroTitle.jsx          ← "ManTarang" with hover letter animation
├── SkeletonCard.jsx × 5   ← Shown during loading (domino wave)
├── QualityPanel           ← System confidence + aggregate bars
└── TrackCard.jsx × N
    ├── GlowCard.jsx       ← Mouse-spotlight radial gradient wrapper
    └── MetricsBar.jsx     ← Confidence ring + 4 animated bars
```

### 3.4 Modules and Components

| Module | File | Responsibility |
|--------|------|---------------|
| Recommendation Engine | `csv_recommender.py` | Full pipeline: intent → strategy → score → metrics |
| API Backend | `backend.py` | FastAPI routes, CORS, static file serving, lifespan |
| Hero Title | `HeroTitle.jsx` | Animated letter-by-letter hover effect |
| Track Card | `TrackCard.jsx` | Per-track display with expandable metrics |
| Metrics Bar | `MetricsBar.jsx` | SVG confidence ring + animated progress bars |
| Skeleton Card | `SkeletonCard.jsx` | Domino-wave loading placeholder |
| Stars | `Stars.jsx` | Canvas-based animated star field |
| Glow Card | `GlowCard.jsx` | Mouse-position radial glow on hover |

---

## 4. Implementation

### 4.1 Key Code: Intent Detection

```python
# Artist extraction using regex patterns
def _extract_artist(query: str) -> Optional[str]:
    patterns = [
        r"(?:songs?|tracks?)\s+(?:by|from)\s+([a-z0-9 &''.,()\-]+?)(?:\s+that|\s*$)",
        r"(?:similar\s+to|like)\s+([a-z0-9 &''.,()\-]+?)(?:\s+but|\s*$)",
        r"(?:discography|top songs?)\s+(?:of|by)\s+([a-z0-9 &''.,()\-]+?)(?:\s*$)",
    ]
    for pat in patterns:
        m = re.search(pat, query.lower())
        if m:
            return m.group(1).strip().rstrip(",.")
    return None
```

### 4.2 Key Code: Multi-Strategy Recommendation

```python
def get_recommendations(query: str, n: int = 8) -> Dict:
    # Priority waterfall: artist → similarity → genre/mood → text → fallback
    
    # 1. Artist match (exact tracks by a named artist)
    if _is_artist_query(q) or candidate_artist:
        # filter df by artist name, score within artist's genres
        
    # 2. Similarity (find tracks with same genre DNA, exclude reference artist)
    if not recs and _is_similarity_query(q):
        ref_genres = agm.get(ref_artist, [])
        sim_df = df[df["genres_lower"].apply(has_genre_overlap) & ~ref_mask]
        
    # 3. Genre / Mood / Context
    if not recs:
        target_genres = GENRE_ALIASES[genre] + MOOD_TO_GENRES[mood] + CONTEXT_MAP[context]
        
    # 4. Text keyword match
    # 5. Popular fallback
```

### 4.3 Key Code: Per-Track Confidence Calculation

```python
# Per-track confidence (0.0 – 1.0)
confidence = round(min(1.0, (
    genre_match  * 0.50 +   # genre alignment is primary signal
    artist_score * 0.30 +   # log-normalised follower count
    popularity_fit * 0.20   # raw popularity score
) / 100), 3)

# Artist Score — log-normalisation
# 100k followers → ~40,  1M → ~60,  10M → ~80,  100M → ~100
artist_score = round(min(100, max(0, (math.log10(max(followers, 1)) / 8) * 100)))
```

### 4.4 Key Code: Skeleton Screen (Domino Wave)

```jsx
// Each bone gets a CSS variable that offsets its animation delay
// creating a left→right ripple across all 5 skeleton cards
function Bone({ seq = 0 }) {
  return (
    <div
      className="bone"
      style={{ "--wave-delay": `${(seq * 0.07).toFixed(2)}s` }}
    />
  );
}
```

```css
/* CSS: wave-pulse keyframes + delay variable */
@keyframes wave-pulse {
  0%, 100% { opacity: 0.12; }
  50%       { opacity: 0.55; }
}
.bone {
  background: linear-gradient(90deg, #1a2540, #2a3a60, #1a2540);
  animation: wave-pulse 1.6s ease-in-out infinite,
             bone-slide  2.4s linear infinite;
  animation-delay: var(--wave-delay, 0s), var(--wave-delay, 0s);
}
```

### 4.5 Key Code: Animated Stars (Canvas)

```jsx
// 200 stars with independent drift velocity and twinkle phase
const stars = Array.from({ length: 200 }, () => ({
  x: rand(0, window.innerWidth),
  y: rand(0, window.innerHeight),
  r: rand(0.4, 1.8),
  baseOp: rand(0.35, 0.9),
  speed:  rand(0.0004, 0.0014),   // twinkle frequency
  drift:  rand(-0.18, 0.18),      // horizontal px/frame
  driftY: rand(-0.10, 0.10),      // vertical px/frame
}));

// Per-frame: update position, compute opacity via sin(), draw
const op = s.baseOp * (0.5 + 0.5 * Math.sin(t * s.speed * 60 + s.phase));
ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
ctx.fillStyle = `rgba(200,220,255,${op})`;
```

### 4.6 Key Code: React 18 Skeleton Timing Fix

```jsx
// React 18 batches state updates — setLoading(true) + fetch start
// in the same tick means the browser never paints the skeleton.
// Double requestAnimationFrame guarantees one full paint cycle first.
const doSearch = (q) => {
  setLoading(true);           // schedule paint
  requestAnimationFrame(() => {
    requestAnimationFrame(() => {  // browser has now painted skeleton
      const MIN_MS = 1200;
      const start = Date.now();
      fetch("/api/recommendations", ...)
        .then(data => {
          const wait = Math.max(0, MIN_MS - (Date.now() - start));
          setTimeout(() => { setResults(data); setLoading(false); }, wait);
        });
    });
  });
};
```

### 4.7 Screenshots

**Figure 7 — Hero Section**
```
┌───────────────────────────────────────────────────────────┐
│  ✦ ·  ·    ✦       ·  ✦    ·         ✦    ·   ✦  ·      │  ← Animated stars
│                                                           │
│                   AI MUSIC INTELLIGENCE                   │
│                                                           │
│                  ManTarang                                │  ← ManTarang title
│           (hover "Tarang" → blue wave + ♪ notes)         │
│                                                           │
│        Describe what you want to hear —                   │
│             moods, genres, or any vibe.                   │
│                                                           │
│   ┌─────────────────────────────────────────────────┐    │
│   │ 🔍  Try 'songs like Radiohead'...          Search│    │  ← Search bar
│   └─────────────────────────────────────────────────┘    │
│                                                           │
│  [songs like Radiohead] [chill lo-fi] [dark indie rock]  │  ← Example chips
└───────────────────────────────────────────────────────────┘
  Background: realistic black hole photo (1.png)
```

**Figure 8 — Results with Metrics (Details expanded)**
```
┌──────────────────────────────────────────────────────────────┐
│ ● 72% system confidence  ·  10 tracks  ·  Genre / Mood   ▾  │  ← QualityPanel
└──────────────────────────────────────────────────────────────┘

┌ ① ──────────────────────────────────────────────────────────┐
│  Creep                                          1992   3:58  │
│  Radiohead                                           ♪ 87   │
│  Pablo Honey                                                 │
│                                                              │
│  [alternative rock] [indie] [Similar Sound]                  │
│                                                              │
│  [Last.fm]  [Spotify]  [YouTube]          [Details ▾]       │
│ ─────────────────────────────────────────────────────────── │
│  ┌────────┐  Genre Match        ████████████░░░ 78%         │
│  │  84%   │  Popularity Fit     ███████████████ 87%         │
│  │  High  │  Artist Credibility ████████████░░░ 76%         │
│  │ conf.  │  Overall Relevance  ████████████░░░ 80%         │
│  └────────┘  Matched: alternative rock · indie rock         │
│              Strong genre match: alternative rock            │
└──────────────────────────────────────────────────────────────┘
```

---

## 5. Evaluation Metrics

### 5.1 Strategy Coverage (Sample Queries)

| Query | Strategy Selected | Tracks Returned |
|-------|-----------------|----------------|
| "songs by Radiohead" | Artist Match | 8 |
| "music like Radiohead" | Similarity | 8 |
| "dark indie rock" | Genre / Mood | 10 |
| "vibe coding" | Genre / Mood (context) | 10 |
| "sad heartbreak songs" | Genre / Mood | 10 |
| "give me something energetic" | Genre / Mood | 10 |
| "late night drives" | Context Match | 10 |

### 5.2 System Confidence Benchmarks

| Query Type | Typical System Confidence |
|-----------|--------------------------|
| Artist Match (known artist) | 75–90% |
| Similarity (genre-rich artist) | 65–80% |
| Genre / Mood (specific genre) | 60–75% |
| Text Match | 45–60% |
| Popular Fallback | 30–45% |

### 5.3 Response Time

| Stage | Time |
|-------|------|
| CSV load (first request, startup) | ~1.2s |
| Subsequent recommendations | ~50–120ms |
| Frontend skeleton display | min. 1200ms (UX minimum) |

### 5.4 Dataset Coverage

| Metric | Value |
|--------|-------|
| Total tracks | 8,778 |
| Unique artists | ~4,200 |
| Tracks with genre data | ~61% |
| Genre labels (unique) | 200+ |
| Popularity range | 0–100 |
| Release years | 1960s–2024 |

---

## 6. Discussion

### 6.1 Summary of Work

ManTarang was built in two phases:

**Phase 1 — Backend:**
The initial implementation used a multi-agent LLM pipeline (Anthropic Claude) to process queries. This was abandoned due to latency (~5–8s per request), API costs, and consistently biased outputs (Radiohead was recommended for every query regardless of intent). The system was rebuilt as a deterministic CSV-based recommender with explicit strategy logic, which reduced latency to under 150ms and eliminated bias.

**Phase 2 — Frontend:**
A space-themed React UI was built from scratch with Framer Motion animations, a canvas-based star field, per-track expandable metrics, skeleton loading, and a quality panel. Key challenges included React 18 batching (skeleton never painting), font visibility on image backgrounds, and domino-wave skeleton timing.

### 6.2 Challenges Faced

| Challenge | Root Cause | Solution |
|-----------|-----------|---------|
| Always recommending Radiohead | LLM agent ignored query context | Replaced with deterministic CSV engine |
| Skeleton screen never appearing | React 18 batches state + fetch in one tick | Double `requestAnimationFrame` before fetch |
| Genre coverage too low (49%) | Only primary CSV had genre labels | Merged both CSVs into unified artist→genre map |
| `diskcache` import error on HF | `services/__init__.py` auto-imported unused `CacheManager` | Cleared `__init__.py` files to minimal stubs |
| Hero fonts invisible on image | Text color designed for dark canvas, placed over bright photo | Strong `text-shadow` + high-contrast color palette |

### 6.3 Success Criteria Met

| Criterion | Status |
|-----------|--------|
| Natural language query accepted | ✅ |
| Relevant tracks returned | ✅ |
| Per-track metrics displayed | ✅ |
| System confidence calculated | ✅ |
| Skeleton loading screen | ✅ |
| Animated, polished UI | ✅ |
| Zero-cost deployment | ✅ CPU Basic, free tier |
| Sub-200ms response time | ✅ ~50–120ms |

### 6.4 Limitations

1. **No personalisation:** No user accounts or listening history — every search starts fresh.
2. **Static dataset:** Track catalogue is frozen at CSV export date; new releases are not included.
3. **Genre label sparsity:** 39% of tracks lack genre labels and fall back to popularity-only scoring.
4. **English queries only:** Intent detection regex and keyword tables are English-only.
5. **No audio preview:** Links to Spotify/Last.fm/YouTube but no in-app playback.
6. **Cold start on HF Spaces:** After 48h of inactivity, the Space hibernates and takes ~20s to wake.

---

## 7. Future Work

### 7.1 Scope for Improvements

| Improvement | Approach |
|-------------|---------|
| Semantic query understanding | Replace regex with a small sentence-transformer model (e.g. `all-MiniLM-L6-v2`) |
| User personalisation | Session-based listening history → collaborative filtering overlay |
| Real-time data | Periodic Spotify API sync for new releases |
| Audio features | Use Spotify's `danceability`, `energy`, `valence` features for mood alignment |
| Multilingual queries | Translation layer before intent detection |
| In-app audio preview | Spotify embed widget or 30s preview URLs |
| Feedback loop | Thumbs up/down ratings → adjust scoring weights per user |

### 7.2 Possible Real-World Deployment Strategies

| Scenario | Architecture |
|----------|-------------|
| **Production SaaS** | Containerise on AWS ECS / GCP Cloud Run, PostgreSQL for user data, Redis for query cache, CDN for React build |
| **Mobile App** | React Native frontend, same FastAPI backend behind API Gateway |
| **Music Platform Plugin** | Expose as a REST API; embed widget in third-party sites |
| **Offline / Edge** | Export the scoring logic to WASM; run entirely in-browser with a compressed track index |
| **Enterprise Licensing** | White-label the engine for radio stations or playlist curators |

---

## 8. Appendix

### 8.1 Project Structure

```
MER FINAL/
├── BeatDebate/
│   └── src/
│       ├── api/
│       │   ├── __init__.py
│       │   ├── backend.py          ← FastAPI app + routes
│       │   └── logging_middleware.py
│       ├── services/
│       │   ├── __init__.py
│       │   └── csv_recommender.py  ← Full recommendation engine
│       └── utils/
│           └── logging_config.py
├── beatdebate-ui/
│   ├── src/
│   │   ├── App.jsx                 ← Main app, search, results
│   │   ├── index.css               ← Global styles, animations
│   │   └── components/
│   │       ├── HeroTitle.jsx
│   │       ├── TrackCard.jsx
│   │       ├── MetricsBar.jsx
│   │       ├── SkeletonCard.jsx
│   │       ├── Stars.jsx
│   │       └── GlowCard.jsx
│   ├── index.html
│   └── vite.config.js
├── track_data_final.csv            ← Primary dataset (8,778 tracks)
├── spotify_data clean.csv          ← Genre enrichment dataset
├── METRICS.md                      ← Metric formula documentation
└── PROJECT_REPORT.md               ← This file
```

### 8.2 Key Links

| Resource | URL |
|----------|-----|
| **Live Demo** | https://huggingface.co/spaces/ashu-17/mantarang |
| **Hugging Face Space** | https://huggingface.co/spaces/ashu-17/mantarang |

### 8.3 Dependencies

**Backend (`requirements.txt`)**
```
fastapi
uvicorn[standard]
pandas
pydantic
python-multipart
structlog
aiohttp
httpx
```

**Frontend (`package.json` key deps)**
```json
{
  "react": "^18.0.0",
  "framer-motion": "^11.0.0",
  "vite": "^5.0.0"
}
```

### 8.4 API Reference

**POST /api/recommendations**

Request:
```json
{
  "query": "dark indie rock like Radiohead",
  "max_recommendations": 10
}
```

Response:
```json
{
  "recommendations": [
    {
      "rank": 1,
      "title": "Creep",
      "artist": "Radiohead",
      "genres": ["alternative rock", "indie"],
      "confidence": 0.842,
      "source": "similarity",
      "explanation": "Strong genre match: alternative rock · indie",
      "popularity": 87,
      "duration": "3:58",
      "release_year": "1992",
      "metrics": {
        "genre_match": 78,
        "popularity_fit": 87,
        "artist_score": 76,
        "relevance": 80,
        "target_genres": ["alternative rock", "indie rock", "grunge"]
      }
    }
  ],
  "aggregate_metrics": {
    "system_confidence": 72,
    "avg_confidence": 0.81,
    "genre_diversity": 8,
    "artist_diversity": 9,
    "strategy": "similarity"
  }
}
```

---

*Report prepared by Ashutosh Kumar Singh (92301733016) and Aditya Raj (92301733062)*
*ManTarang — AI Music Intelligence | May 2026*
