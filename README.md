<div align="center">

![header](https://capsule-render.vercel.app/api?type=waving&color=0:2D1B69,50:7C3AED,100:C9A227&height=220&section=header&text=ManTarang&fontSize=80&fontColor=ffffff&fontAlignY=38&desc=AI-Powered%20Music%20Emotion%20Recognition%20%26%20Recommendation&descAlignY=60&descSize=16&animation=fadeIn)

[![Typing SVG](https://readme-typing-svg.demolab.com?font=Inter&weight=700&size=20&pause=1000&color=C9A227&center=true&vCenter=true&width=650&lines=Music+Emotion+Recognition+%7C+MER+Project;Natural+Language+%E2%86%92+Ranked+Tracks+in+120ms;5-Strategy+AI+Recommendation+Engine;Explainable+Per-Track+Confidence+Metrics;Deployed+Free+on+HuggingFace+Spaces)](https://git.io/typing-svg)

<br/>

[![Live Demo](https://img.shields.io/badge/Live_Demo-HuggingFace_Spaces-FF6B00?style=for-the-badge)](https://huggingface.co/spaces/ashu-17/mantarang)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-Deployed-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://huggingface.co/spaces/ashu-17/mantarang)

</div>

---

## 📌 Table of Contents

- [About the Project](#-about-the-project)
- [System Architecture](#-system-architecture)
- [Recommendation Pipeline](#-recommendation-pipeline)
- [Strategy Selection](#-strategy-selection--decision-tree)
- [Data Pipeline](#-data-pipeline)
- [Metric Formulas](#-metric--confidence-formulas)
- [Frontend Components](#-frontend-component-tree)
- [Tech Stack](#-tech-stack)
- [Run Locally](#-run-locally)
- [Project Structure](#-project-structure)
- [Team](#-built-by)

---

## 🎵 About the Project

**ManTarang** is a **Music Emotion Recognition (MER)** system that maps free-form natural-language queries to emotionally and contextually relevant music tracks. It combines rule-based NLU, multi-criteria scoring, and a curated Spotify dataset to deliver fast, diverse, and **fully explainable** recommendations — with no GPU required.

> _"Why did you recommend this track?"_ — ManTarang tells you, with numbers.

<div align="center">

| Input | Strategy | Output |
|-------|----------|--------|
| `"songs like Radiohead"` | Similarity | 10 alt-rock tracks with genre DNA match |
| `"chill lo-fi for studying"` | Genre + Context | lo-fi / chillhop, ranked by relevance |
| `"dark indie rock"` | Genre / Mood | genre-matched, confidence scored |
| `"energetic hip hop"` | Genre / Mood | high-popularity hip-hop tracks |
| `"late night drives"` | Context Map | rock / pop / alternative blend |

</div>

---

## 🏗 System Architecture

```mermaid
graph TB
    User["👤 User Browser"]:::user
    React["⚛️ React + Vite SPA\nmantarang-ui"]:::frontend
    API["🐍 FastAPI Backend\n/api/recommendations"]:::backend
    Engine["🧠 CSV Recommender\ncsv_recommender.py"]:::engine
    DB1["📊 track_data_final.csv\n8,778 tracks"]:::data
    DB2["📊 spotify_data clean.csv\nGenre enrichment"]:::data
    HF["☁️ HuggingFace Spaces\nDocker · CPU Basic · Free"]:::deploy

    User -->|types query| React
    React -->|POST /api/recommendations| API
    API --> Engine
    Engine -->|loads once at startup| DB1
    Engine -->|genre enrichment| DB2
    Engine -->|ranked recs + metrics| API
    API -->|JSON response| React
    React -->|renders cards + metrics| User
    HF -->|hosts| API
    HF -->|serves| React

    classDef user fill:#2D1B69,stroke:#C9A227,color:#fff
    classDef frontend fill:#1a1a3e,stroke:#61DAFB,color:#61DAFB
    classDef backend fill:#1a1a3e,stroke:#009688,color:#009688
    classDef engine fill:#1a1a3e,stroke:#C9A227,color:#C9A227
    classDef data fill:#1a1a3e,stroke:#6ee7b7,color:#6ee7b7
    classDef deploy fill:#2D1B69,stroke:#FFD21E,color:#FFD21E
```

---

## 🔄 Recommendation Pipeline

```mermaid
flowchart TD
    Q["📝 User Query"]
    I["🔍 Intent Detection\n_extract_artist\n_detect_genre\n_detect_mood\n_detect_context"]
    S{"🎯 Strategy\nSelector"}

    AM["🎤 Strategy 1\nArtist Match"]
    SM["🔗 Strategy 2\nSimilarity"]
    GM["🎼 Strategy 3\nGenre / Mood / Context"]
    TM["📝 Strategy 4\nText Match"]
    PF["📈 Strategy 5\nPopular Fallback"]

    SC["⚖️ Score and Rank\nGenre x 0.40\nPopularity x 0.35\nDiversity x 0.15\nNoise x 0.10"]
    MX["📊 Build Metrics\nGenre Match 0-100\nPopularity Fit 0-100\nArtist Score log-norm\nRelevance blend\nConfidence 0.0-1.0"]
    AGG["🏆 Aggregate\navg_confidence\nsystem_confidence\ngenre_diversity"]
    OUT["✅ JSON Response\nReact renders TrackCards\nand QualityPanel"]

    Q --> I --> S
    S -->|artist query| AM
    S -->|like / similar to| SM
    S -->|genre mood context| GM
    S -->|keywords found| TM
    S -->|no match| PF
    AM & SM & GM & TM & PF --> SC --> MX --> AGG --> OUT
```

---

## 🌿 Strategy Selection — Decision Tree

```mermaid
graph TD
    START["User Query"]
    A{"Artist query?\nsongs by X\ntop songs of Y"}
    B{"Similarity query?\nlike X\nsimilar to X"}
    C{"Genre Mood Context?\nlo-fi, sad, coding\nworkout, party"}
    D{"Keywords match\ntrack or artist?"}

    S1["Strategy 1\nArtist Match\n+10 confidence"]
    S2["Strategy 2\nSimilarity\n+8 confidence"]
    S3["Strategy 3\nGenre Mood\n+6 confidence"]
    S4["Strategy 4\nText Match\n+4 confidence"]
    S5["Strategy 5\nPopular Fallback\n+0 confidence"]

    START --> A
    A -->|YES| S1
    A -->|NO| B
    B -->|YES| S2
    B -->|NO| C
    C -->|YES| S3
    C -->|NO| D
    D -->|YES| S4
    D -->|NO| S5

    style S1 fill:#166534,color:#fff
    style S2 fill:#1e3a5f,color:#fff
    style S3 fill:#4a1942,color:#fff
    style S4 fill:#713f12,color:#fff
    style S5 fill:#3b1515,color:#fff
```

---

## 🗄 Data Pipeline

```mermaid
flowchart LR
    CSV1["📄 track_data_final.csv\n8778 rows\ntrack + artist + genres\npopularity + followers"]
    CSV2["📄 spotify_data clean.csv\nGenre enrichment source"]

    PARSE["🔧 Parse Genres\nast.literal_eval\nfallback string split"]
    MERGE["🔀 Build Artist-Genre Map\nMerge both CSVs\n61% coverage\nwas 49% before merge"]
    ENRICH["✨ Enrich Missing Genres\nBack-fill from merged map"]
    INDEX["🗂 Add Index Columns\nartist_lower\ntrack_lower\ngenres_lower"]
    RAM["🧠 Singleton DataFrame\nLoaded once at startup\nLives in RAM\n50ms query time"]

    CSV1 --> PARSE
    CSV2 --> PARSE
    PARSE --> MERGE
    MERGE --> ENRICH
    ENRICH --> INDEX
    INDEX --> RAM
```

---

## 📐 Metric & Confidence Formulas

```mermaid
graph LR
    GM["Genre Match\nJaccard overlap x 100\nWeight 45%"]
    PF["Popularity Fit\ntrack_popularity / 100\nWeight 30%"]
    AS["Artist Score\nlog10 followers / 8 x 100\nWeight 25%"]
    RV["Overall Relevance\nGM x 0.45\nPF x 0.30\nAS x 0.25"]
    CF["Track Confidence\nGM x 0.50\nAS x 0.30\nPF x 0.20\ndivided by 100"]

    GM --> RV
    PF --> RV
    AS --> RV
    GM --> CF
    PF --> CF
    AS --> CF
```

<div align="center">

| Metric | Formula | Display |
|--------|---------|---------|
| Genre Match | `genre_overlap(track, target) × 100` | Animated bar |
| Popularity Fit | `popularity / 100 × 100` | Animated bar |
| Artist Score | `min(100, log₁₀(followers)/8 × 100)` | Animated bar |
| Overall Relevance | `GM×0.45 + PF×0.30 + AS×0.25` | Animated bar |
| Track Confidence | `(GM×0.50 + AS×0.30 + PF×0.20) / 100` | SVG ring |
| System Confidence | `avg×75 + strategy_premium + diversity_bonus` | Quality panel |

</div>

```
System_Confidence = min(100,
    avg_track_confidence × 100 × 0.75
    + Strategy_Premium   ← artist=10, similarity=8, genre=6, text=4, fallback=0
    + Diversity_Bonus    ← min(10, unique_genre_count)
)
```

---

## 🖥 Frontend Component Tree

```mermaid
graph TD
    APP["App.jsx\nSearch · Results · State"]

    STARS["Stars.jsx\n200 canvas stars\ndrift + twinkle"]
    HERO["HeroTitle.jsx\nLetter hover animation\nColor wave + music notes"]
    SKEL["SkeletonCard x5\nDomino wave loading\n--wave-delay CSS var"]
    QP["QualityPanel\nSystem confidence\nCollapsible metric bars"]
    TC["TrackCard x N\nRank · Title · Artist\nGenre chips · Links"]

    GC["GlowCard\nMouse spotlight\n--gx --gy CSS vars"]
    MB["MetricsBar\nSVG confidence ring\n4 animated progress bars"]

    APP --> STARS
    APP --> HERO
    APP --> SKEL
    APP --> QP
    APP --> TC
    TC --> GC
    TC --> MB
```

---

## 🛠 Tech Stack

<div align="center">

| Layer | Technology | Purpose |
|-------|-----------|---------|
| 🐍 Backend | Python 3.11 + FastAPI | REST API, routing, lifespan |
| 📊 Data | Pandas + CSV | 8,778-track in-memory dataset |
| ⚛️ Frontend | React 18 + Vite | SPA, hot reload, /api proxy |
| 🎞 Animation | Framer Motion | Transitions, AnimatePresence |
| 🌌 Canvas | HTML5 Canvas API | 200-star animated starfield |
| 🐳 Container | Docker multi-stage | Node build then Python serve |
| ☁️ Deploy | HuggingFace Spaces | CPU Basic, free, port 7860 |

</div>

---

## 🚀 Run Locally

```bash
# 1. Clone
git clone https://github.com/Ashutosh-177/ManTarang-AI-Powered-Music-Recommendation-System.git
cd ManTarang-AI-Powered-Music-Recommendation-System

# 2. Backend  (terminal 1)
pip install -r requirements-hf.txt
uvicorn mantarang.src.api.backend:app --host 0.0.0.0 --port 8000 --reload

# 3. Frontend  (terminal 2)
cd mantarang-ui
npm install
npm run dev
# open http://localhost:5173
```

---

## 📁 Project Structure

```
ManTarang/
├── mantarang/                       ← Python backend
│   └── src/
│       ├── api/backend.py           ← FastAPI routes + SPA fallback
│       └── services/
│           └── csv_recommender.py   ← 5-strategy recommendation engine
│
├── mantarang-ui/                    ← React frontend
│   └── src/
│       ├── App.jsx                  ← Search, results, quality panel
│       └── components/
│           ├── HeroTitle.jsx        ← Letter animation on hover
│           ├── TrackCard.jsx        ← Result card with details toggle
│           ├── MetricsBar.jsx       ← Confidence ring + 4 bars
│           ├── SkeletonCard.jsx     ← Domino-wave loading state
│           ├── Stars.jsx            ← Canvas animated starfield
│           └── GlowCard.jsx         ← Mouse spotlight effect
│
├── track_data_final.csv             ← Primary dataset (8,778 tracks)
├── spotify_data clean.csv           ← Genre enrichment
├── Dockerfile                       ← Multi-stage: Node then Python
├── METRICS.md                       ← Full formula reference
└── PROJECT_REPORT.md                ← MER project report
```

---

## 👥 Built By

<div align="center">

<table>
<tr>
<td align="center" width="50%">
<h3>Ashutosh Kumar Singh</h3>
<code>Enrollment No. 92301733016</code>
</td>
<td align="center" width="50%">
<h3>Aditya Raj</h3>
<code>Enrollment No. 92301733062</code>
</td>
</tr>
</table>

<br/>

**Music Emotion Recognition (MER) — 2026**

<br/>

![footer](https://capsule-render.vercel.app/api?type=waving&color=0:C9A227,50:7C3AED,100:2D1B69&height=120&section=footer&animation=fadeIn)

</div>
