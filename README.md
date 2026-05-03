![ManTarang Banner](https://capsule-render.vercel.app/api?type=waving&color=0:2D1B69,50:7C3AED,100:C9A227&height=220&section=header&text=ManTarang&fontSize=80&fontColor=ffffff&fontAlignY=38&desc=AI-Powered%20Music%20Emotion%20Recognition%20%26%20Recommendation&descAlignY=60&descSize=16&animation=fadeIn)

<div align="center">

[![Typing SVG](https://readme-typing-svg.demolab.com?font=Inter&weight=700&size=20&pause=1000&color=C9A227&center=true&vCenter=true&width=650&lines=Music+Emotion+Recognition+%7C+MER+Project;4-Agent+Collaborative+AI+Architecture;Planner+%E2%86%92+GenreMood+%E2%86%92+Discovery+%E2%86%92+Judge;Explainable+Per-Track+Confidence+Metrics;Deployed+Free+on+HuggingFace+Spaces)](https://git.io/typing-svg)

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
- [4-Agent Architecture](#-4-agent-architecture)
- [Agent Collaboration Flow](#-agent-collaboration-flow)
- [Agent Deep Dive](#-agent-deep-dive)
- [Data Pipeline](#-data-pipeline)
- [Metric Formulas](#-metric--confidence-formulas)
- [Frontend Components](#-frontend-component-tree)
- [Tech Stack](#-tech-stack)
- [Run Locally](#-run-locally)
- [Project Structure](#-project-structure)
- [Team](#-built-by)

---

## 🎵 About the Project

**ManTarang** is a **Music Emotion Recognition (MER)** system built on a **4-agent collaborative AI architecture**. When a user types a natural-language query, four specialized AI agents coordinate in a pipeline — each with a distinct role — to produce ranked, explainable music recommendations.

> Each agent contributes its expertise. The Planner leads, two specialists generate candidates, and the Judge delivers the final verdict.

<div align="center">

| Query | Planner decides | Agents activated | Output |
|-------|----------------|-----------------|--------|
| `"songs like Radiohead"` | Similarity strategy | Discovery + GenreMood | Genre-DNA matched tracks |
| `"chill lo-fi for studying"` | Context strategy | GenreMood | lo-fi / chillhop ranked list |
| `"dark indie rock"` | Genre strategy | GenreMood + Discovery | Confidence-scored results |
| `"energetic hip hop"` | Mood strategy | GenreMood | High-energy ranked tracks |

</div>

---

## 🤖 4-Agent Architecture

```mermaid
graph TD
    USER["👤 User Query\nNatural Language Input"]

    subgraph AGENTS["  4-Agent Collaborative System  "]
        P["🧭 Planner Agent\n─────────────────\nOrchestrates the entire pipeline\nAnalyses query intent and complexity\nExtracts entities: artist, genre, mood\nCreates agent coordination plan\nDetermines which agents to activate"]

        G["🎼 GenreMood Agent\n─────────────────\nMood detection and analysis\nGenre matching and filtering\nTag generation and enhancement\nContext-aware intent adaptation\nCandidate generation by genre/mood"]

        D["🔭 Discovery Agent\n─────────────────\nMulti-hop similarity exploration\nUnderground and hidden gem detection\nSerendipitous discovery beyond mainstream\nNovelty-optimized recommendations\nArtist similarity graph traversal"]

        J["⚖️ Judge Agent\n─────────────────\nCollects all agent candidates\nScores and ranks with RankingEngine\nOptimizes diversity with DiversityOptimizer\nGenerates human-readable explanations\nDelivers final ranked recommendations"]
    end

    RESULT["✅ Final Recommendations\nRanked · Scored · Explained"]

    USER --> P
    P -->|genre/mood query| G
    P -->|similarity/discovery query| D
    G -->|genre candidates| J
    D -->|discovery candidates| J
    J --> RESULT

    style P fill:#2D1B69,stroke:#C9A227,color:#fff
    style G fill:#1e3a5f,stroke:#61DAFB,color:#fff
    style D fill:#1a3a1a,stroke:#6ee7b7,color:#fff
    style J fill:#3b1515,stroke:#f9a8d4,color:#fff
    style AGENTS fill:#0d0d1a,stroke:#7C3AED,color:#fff
```

---

## 🔄 Agent Collaboration Flow

```mermaid
sequenceDiagram
    actor User
    participant P as 🧭 Planner Agent
    participant G as 🎼 GenreMood Agent
    participant D as 🔭 Discovery Agent
    participant J as ⚖️ Judge Agent

    User->>P: Natural language query
    Note over P: Analyse intent, extract entities<br/>Determine strategy and complexity<br/>Build coordination plan

    P->>G: Activate with genre/mood parameters
    P->>D: Activate with similarity parameters

    Note over G: Detect mood signals<br/>Match genre tags<br/>Generate genre candidates
    Note over D: Explore artist similarity graph<br/>Detect underground gems<br/>Generate discovery candidates

    G-->>J: Genre/Mood candidate pool
    D-->>J: Discovery candidate pool

    Note over J: Merge all candidates<br/>Score with RankingEngine<br/>Optimise diversity<br/>Generate explanations

    J-->>User: Final ranked recommendations<br/>with metrics + confidence
```

---

## 🧠 Agent Deep Dive

### 🧭 Agent 1 — Planner Agent
> _The orchestrator. Runs first. Decides everything else._

```mermaid
flowchart TD
    QA["QueryAnalyzer\nParse query complexity\nDetect ambiguity\nExtract primary intent"]
    CA["ContextAnalyzer\nInterpret context signals\nHandle effective intent overrides\nTransform raw context"]
    EP["EntityProcessor\nExtract: artist name\nExtract: genre keywords\nExtract: mood signals\nExtract: context triggers"]
    SP["StrategyPlanner\nSelect recommendation strategy\nDecide agent activation order\nSet parameters per agent\nBuild coordination plan"]

    QA --> CA --> EP --> SP
```

**Outputs to:** GenreMood Agent + Discovery Agent with a structured coordination plan.

---

### 🎼 Agent 2 — GenreMood Agent
> _The emotion specialist. Translates feelings into music._

```mermaid
flowchart TD
    MA["MoodAnalyzer\nDetect mood from query\nhappy / sad / energetic\nchill / romantic / focused"]
    GP["GenreProcessor\nMatch genre tags\nExpand via alias maps\nFilter by genre overlap"]
    TG["TagGenerator\nGenerate enhanced tags\nCombine genre + mood signals\nContext-aware tag boost"]
    UCG["UnifiedCandidateGenerator\nGenerate candidates\nby genre and mood\nfrom dataset"]
    QS["QualityScorer\nScore genre fit\nScore mood alignment\nScore popularity balance"]

    MA --> TG
    GP --> TG
    TG --> UCG --> QS
```

**Outputs to:** Judge Agent with a pool of genre/mood-matched track candidates.

---

### 🔭 Agent 3 — Discovery Agent
> _The explorer. Finds what you didn't know you needed._

```mermaid
flowchart TD
    DC["DiscoveryConfig\nSet novelty parameters\nConfigure similarity depth\nSet underground threshold"]
    SE["SimilarityExplorer\nMulti-hop artist graph\nExplore genre neighbours\nFind sonic relatives"]
    UD["UndergroundDetector\nDetect hidden gems\nScore novelty vs popularity\nFind non-mainstream tracks"]
    DF["DiscoveryFilter\nFilter irrelevant candidates\nRemove duplicates\nApply quality threshold"]
    DD["DiscoveryDiversity\nManage variety\nPrevent artist clustering\nBalance mainstream vs niche"]

    DC --> SE
    DC --> UD
    SE --> DF
    UD --> DF
    DF --> DD
```

**Outputs to:** Judge Agent with a pool of discovery/similarity candidates.

---

### ⚖️ Agent 4 — Judge Agent
> _The final decision maker. Ranks, diversifies, and explains._

```mermaid
flowchart TD
    CS["CandidateSelector\nCollect all agent pools\nFilter by quality threshold\nRemove duplicates"]
    RE["RankingEngine\nMulti-criteria scoring\nGenre match weight\nPopularity fit weight\nArtist credibility weight"]
    DO["DiversityOptimizer\nPrevent artist repetition\nBalance genre spread\nOptimize result variety"]
    EG["ExplanationGenerator\nGenerate per-track reasons\nCalculate confidence score\nBuild human-readable text"]

    CS --> RE --> DO --> EG
```

**Outputs:** Final ranked recommendations with metrics, confidence, and explanations.

---

## 🗄 Data Pipeline

```mermaid
flowchart LR
    CSV1["📄 track_data_final.csv\n8,778 tracks\ntrack + artist + genres\npopularity + followers"]
    CSV2["📄 spotify_data clean.csv\nGenre enrichment source"]

    PARSE["Parse Genres\nast.literal_eval\nfallback string split"]
    MERGE["Build Artist-Genre Map\nMerge both sources\n61% genre coverage"]
    ENRICH["Enrich Missing Genres\nBack-fill from merged map"]
    INDEX["Index Columns\nartist_lower / track_lower\ngenres_lower"]
    RAM["Shared Agent Dataset\nLoaded once at startup\nShared across all agents"]

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

| Metric | Formula | Calculated By |
|--------|---------|--------------|
| Genre Match | `genre_overlap(track, target) × 100` | GenreMood + Discovery Agents |
| Popularity Fit | `popularity / 100 × 100` | Judge Agent |
| Artist Score | `min(100, log₁₀(followers)/8 × 100)` | Judge Agent |
| Overall Relevance | `GM×0.45 + PF×0.30 + AS×0.25` | Judge Agent |
| Track Confidence | `(GM×0.50 + AS×0.30 + PF×0.20) / 100` | Judge Agent |
| System Confidence | `avg×75 + strategy_premium + diversity_bonus` | Judge Agent |

</div>

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
| 🤖 Agents | Python 3.11 — 4 agent classes | Planner, GenreMood, Discovery, Judge |
| 🐍 Backend | FastAPI + Uvicorn | REST API, routing, lifespan |
| 📊 Data | Pandas + Spotify CSV | 8,778-track shared agent dataset |
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
├── mantarang/src/
│   ├── agents/
│   │   ├── planner/           ← Agent 1: Orchestrates pipeline
│   │   │   ├── agent.py
│   │   │   ├── query_analyzer.py
│   │   │   ├── context_analyzer.py
│   │   │   ├── strategy_planner.py
│   │   │   └── entity_processor.py
│   │   ├── genre_mood/        ← Agent 2: Emotion and genre specialist
│   │   │   ├── agent.py
│   │   │   └── components/
│   │   ├── discovery/         ← Agent 3: Similarity and novelty explorer
│   │   │   ├── agent.py
│   │   │   ├── similarity_explorer.py
│   │   │   └── underground_detector.py
│   │   └── judge/             ← Agent 4: Ranks and explains results
│   │       ├── agent.py
│   │       └── components/
│   │           ├── ranking_engine.py
│   │           ├── diversity_optimizer.py
│   │           └── explanation_generator.py
│   └── api/
│       └── backend.py         ← FastAPI routes
│
├── mantarang-ui/src/
│   ├── App.jsx
│   └── components/
│       ├── HeroTitle.jsx
│       ├── TrackCard.jsx
│       ├── MetricsBar.jsx
│       ├── SkeletonCard.jsx
│       ├── Stars.jsx
│       └── GlowCard.jsx
│
├── track_data_final.csv        ← Shared agent dataset (8,778 tracks)
├── Dockerfile
├── METRICS.md
└── PROJECT_REPORT.md
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

</div>

![footer](https://capsule-render.vercel.app/api?type=waving&color=0:C9A227,50:7C3AED,100:2D1B69&height=120&section=footer&animation=fadeIn)
