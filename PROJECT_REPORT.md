# ManTarang — AI-Powered Music Emotion Recognition System
## Project Report

---

| | |
|---|---|
| **Project Title** | ManTarang — AI-Powered Music Emotion Recognition (MER) |
| **Subject** | Minor Engineering Research (MER) |
| **Submitted by** | Ashutosh Kumar Singh (Enroll. No. 92301733016) |
| | Aditya Raj (Enroll. No. 92301733062) |
| **Live Demo** | https://huggingface.co/spaces/ashu-17/mantarang |
| **Repository** | https://github.com/Ashutosh-177/ManTarang-AI-Powered-Music-Recommendation-System |
| **Date** | May 2026 |

---

## Abstract

ManTarang is an **AI-Powered Music Emotion Recognition (MER)** system built on a **4-agent collaborative AI architecture**. When a user types a natural-language query — a mood, context, artist name, or any free-form description — four specialized AI agents coordinate in a structured pipeline to produce ranked, explainable music recommendations.

The system employs a **Planner Agent** that orchestrates the full pipeline, a **GenreMood Agent** that translates emotional intent into music candidates, a **Discovery Agent** that explores similarity graphs and uncovers hidden gems, and a **Judge Agent** that scores, diversifies, and explains the final results. Each agent operates with dedicated sub-components following the Single Responsibility Principle, resulting in a modular, testable, and maintainable agentic system.

The backend is a Python FastAPI service with a 4-agent pipeline over a curated dataset of 8,778 Spotify tracks. The frontend is a React + Vite single-page application with a space-themed animated UI. The system is deployed on Hugging Face Spaces (CPU Basic, zero cost) and delivers recommendations in under 200 ms.

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Methodology](#2-methodology)
3. [4-Agent Architecture](#3-4-agent-architecture)
4. [Agent Deep Dive](#4-agent-deep-dive)
5. [Data Pipeline](#5-data-pipeline)
6. [Metric and Confidence Formulas](#6-metric-and-confidence-formulas)
7. [Frontend and UI](#7-frontend-and-ui)
8. [Implementation](#8-implementation)
9. [Evaluation](#9-evaluation)
10. [Discussion](#10-discussion)
11. [Future Work](#11-future-work)
12. [Appendix](#12-appendix)

---

## List of Figures and Tables

| # | Title |
|---|-------|
| Figure 1 | 4-Agent System Architecture |
| Figure 2 | Agent Collaboration Sequence Diagram |
| Figure 3 | Planner Agent Internal Workflow |
| Figure 4 | GenreMood Agent Internal Workflow |
| Figure 5 | Discovery Agent Internal Workflow |
| Figure 6 | Judge Agent Internal Workflow |
| Figure 7 | Data Pipeline Flowchart |
| Figure 8 | Metric and Confidence Formula Block Diagram |
| Figure 9 | Frontend Component Hierarchy |
| Figure 10 | UI — Hero Section (ASCII) |
| Figure 11 | UI — Results with Metrics (ASCII) |
| Table 1 | Dataset Summary |
| Table 2 | Agent Responsibilities |
| Table 3 | Per-Track Metric Formulas |
| Table 4 | System Confidence Breakdown |
| Table 5 | Technology Stack |
| Table 6 | Evaluation Results |

---

## 1. Introduction

### 1.1 Problem Statement

Music discovery is a deeply personal challenge. Mainstream recommendation systems rely on collaborative filtering and deep listening history, which creates a "cold start" problem for new users and fails to handle natural-language intent. A user who wants *"something for late-night coding sessions"* or *"dark indie rock like Radiohead"* cannot express that in a traditional search box.

Existing systems are also black boxes — users are never told *why* a track was recommended, making it impossible to refine or trust the output.

### 1.2 Project Goal

ManTarang addresses this using a **4-agent collaborative AI architecture** where:

- Each agent has a **single, well-defined responsibility**
- Agents **communicate through a shared state** object
- The pipeline is **explainable** — every recommendation includes a human-readable reason and quantitative metrics
- The system runs on **CPU only** with sub-200ms latency

### 1.3 What is MER?

**Music Emotion Recognition (MER)** is the discipline of identifying the emotional content of music — happy, sad, energetic, calm, romantic — and using those signals to match music to a listener's current emotional state or intent.

ManTarang applies MER through its GenreMood Agent, which maps user-expressed emotions and moods to musical genre signals, enabling recommendations that match *how you feel* rather than just *what you've listened to before*.

### 1.4 Objectives

1. Accept any natural-language music query and return emotionally relevant track recommendations.
2. Coordinate four specialized AI agents in a structured pipeline.
3. Explain *why* each track was recommended using quantitative per-track metrics.
4. Display an overall system confidence score reflecting recommendation quality.
5. Deliver a responsive, animated, production-quality web UI.
6. Deploy at zero cost on Hugging Face Spaces (CPU only).

### 1.5 Scope

| In Scope | Out of Scope |
|----------|-------------|
| Query parsing and intent extraction | Audio playback |
| 4-agent pipeline coordination | User accounts and profiles |
| Scoring, ranking, and diversity | Real-time Spotify API calls |
| Per-track metric calculation | Deep learning embeddings |
| Frontend UI and animations | Collaborative filtering |
| HuggingFace Spaces deployment | GPU-accelerated models |

---

## 2. Methodology

### 2.1 AI Techniques Used

| Technique | Agent / Layer |
|-----------|--------------|
| LLM-assisted query understanding | Planner (QueryAnalyzer) |
| Rule-based intent extraction | Planner (EntityProcessor) |
| Mood-to-genre signal mapping | GenreMood (MoodAnalyzer) |
| Genre alias expansion and tag generation | GenreMood (TagGenerator, GenreProcessor) |
| Multi-hop artist similarity graph exploration | Discovery (SimilarityExplorer) |
| Underground / novelty scoring | Discovery (UndergroundDetector) |
| Multi-criteria weighted scoring | Judge (RankingEngine) |
| Diversity-aware selection (MMR-style) | Judge (DiversityOptimizer) |
| Per-track confidence calculation | Judge (ExplanationGenerator) |
| Log-normalised artist credibility | Judge (RankingEngine) |
| Jaccard-inspired genre overlap | GenreMood + Discovery + Judge |

### 2.2 Design Philosophy

ManTarang is built as a **deterministic, explainable agentic system**. Rather than using a single neural model, the system decomposes the recommendation problem into four focused tasks — each handled by a specialized agent. This design:

- Is fully **interpretable** — every decision can be traced back to a specific agent and sub-component
- Runs **on CPU** with no GPU requirement
- Produces **consistent, non-biased** results (earlier LLM-only prototypes recommended Radiohead for every query regardless of intent — see Section 10.2)

### 2.3 Query Intent Taxonomy

The Planner Agent classifies every query into one of the following intents:

| Intent | Trigger | Example |
|--------|---------|---------|
| `by_artist` | "songs by X", "top tracks of Y" | "songs by Radiohead" |
| `artist_similarity` | "like X", "similar to X" | "music like Radiohead" |
| `genre_mood` | genre/mood keywords present | "dark indie rock" |
| `contextual` | context signal present | "late night drives" |
| `discovery` | novelty/explore keywords | "discover underground electronic" |
| `hybrid` | multiple signals | "dark indie like Radiohead but energetic" |

---

## 3. 4-Agent Architecture

### 3.1 Architecture Overview

**Figure 1 — 4-Agent System Architecture**

```
┌─────────────────────────────────────────────────────────────────────────┐
│                       ManTarang Agent System                            │
│                                                                         │
│   User Query                                                            │
│       │                                                                 │
│       ▼                                                                 │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  Agent 1 — Planner Agent (Orchestrator)                         │   │
│  │  ┌──────────────┐ ┌──────────────────┐ ┌──────────────────────┐ │   │
│  │  │QueryAnalyzer │ │ContextAnalyzer   │ │StrategyPlanner       │ │   │
│  │  │- Parse intent│ │- Context signals │ │- Agent activation    │ │   │
│  │  │- LLM assist  │ │- Effective intent│ │- Coordination plan   │ │   │
│  │  └──────────────┘ └──────────────────┘ └──────────────────────┘ │   │
│  │  ┌──────────────────────────────────────────────────────────┐   │   │
│  │  │EntityProcessor — artist, genre, mood, activity entities  │   │   │
│  │  └──────────────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│            │ coordination plan                                          │
│     ┌──────┴──────────┐                                                │
│     ▼                 ▼                                                 │
│  ┌──────────────┐  ┌──────────────────────────────────────────────┐   │
│  │ Agent 2      │  │ Agent 3 — Discovery Agent                    │   │
│  │ GenreMood    │  │  ┌────────────────┐  ┌──────────────────────┐│   │
│  │ Agent        │  │  │SimilarityExp.  │  │UndergroundDetector   ││   │
│  │  MoodAnalyzer│  │  │- Multi-hop     │  │- Hidden gems         ││   │
│  │  GenreProc.  │  │  │  artist graph  │  │- Novelty scoring     ││   │
│  │  TagGenerator│  │  │- Genre neighb. │  │- Non-mainstream      ││   │
│  │  CandidateGen│  │  └────────────────┘  └──────────────────────┘│   │
│  └──────────────┘  │  ┌──────────────────────────────────────────┐│   │
│         │          │  │DiscoveryFilter + DiscoveryDiversity       ││   │
│         │          │  └──────────────────────────────────────────┘│   │
│         │          └──────────────────────────────────────────────┘   │
│         │ candidate pool       │ candidate pool                        │
│         └──────────┬───────────┘                                       │
│                    ▼                                                    │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  Agent 4 — Judge Agent (Final Decision Maker)                   │   │
│  │  ┌──────────────────┐  ┌──────────────┐  ┌──────────────────┐  │   │
│  │  │CandidateSelector │  │RankingEngine │  │DiversityOptimizer│  │   │
│  │  │- Merge pools     │  │- Contextual  │  │- Artist variety  │  │   │
│  │  │- Quality filter  │  │  relevance   │  │- Genre spread    │  │   │
│  │  │- Deduplication   │  │- Multi-score │  │- MMR-style select│  │   │
│  │  └──────────────────┘  └──────────────┘  └──────────────────┘  │   │
│  │  ┌──────────────────────────────────────────────────────────┐   │   │
│  │  │ExplanationGenerator — confidence score + human-readable  │   │   │
│  │  └──────────────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                    │                                                    │
│                    ▼                                                    │
│         Final Ranked Recommendations                                    │
│         (ranked · scored · explained · diverse)                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Agent Responsibilities

**Table 2 — Agent Responsibilities**

| Agent | Role | Key Components | Output |
|-------|------|---------------|--------|
| Planner | Orchestrator — runs first, decides everything else | QueryAnalyzer, ContextAnalyzer, StrategyPlanner, EntityProcessor | Coordination plan + structured entities |
| GenreMood | Emotion specialist — translates feelings into music | MoodAnalyzer, GenreProcessor, TagGenerator, UnifiedCandidateGenerator, QualityScorer | Genre/mood candidate pool |
| Discovery | Explorer — finds what you didn't know you needed | DiscoveryConfig, SimilarityExplorer, UndergroundDetector, DiscoveryFilter, DiscoveryDiversity | Discovery candidate pool |
| Judge | Decision maker — ranks, diversifies, explains | CandidateSelector, RankingEngine, DiversityOptimizer, ExplanationGenerator | Final ranked recommendations |

### 3.3 Agent Collaboration Sequence

**Figure 2 — Agent Collaboration Sequence Diagram**

```
User          Planner            GenreMood          Discovery          Judge
 │                │                   │                  │               │
 │──── query ────►│                   │                  │               │
 │                │                   │                  │               │
 │           ┌────┴──────────────┐    │                  │               │
 │           │ Phase 1: Query    │    │                  │               │
 │           │ Understanding     │    │                  │               │
 │           │ - QueryAnalyzer   │    │                  │               │
 │           │ - ContextAnalyzer │    │                  │               │
 │           │ - EntityProcessor │    │                  │               │
 │           └────┬──────────────┘    │                  │               │
 │                │                   │                  │               │
 │           ┌────┴──────────────┐    │                  │               │
 │           │ Phase 2: Task     │    │                  │               │
 │           │ Analysis          │    │                  │               │
 │           │ Complexity +      │    │                  │               │
 │           │ Intent type       │    │                  │               │
 │           └────┬──────────────┘    │                  │               │
 │                │                   │                  │               │
 │           ┌────┴──────────────┐    │                  │               │
 │           │ Phase 3+4:        │    │                  │               │
 │           │ Strategy +        │    │                  │               │
 │           │ Coordination Plan │    │                  │               │
 │           └────┬──────────────┘    │                  │               │
 │                │                   │                  │               │
 │                │── genre/mood ─────►│                  │               │
 │                │── params          │                  │               │
 │                │                   │                  │               │
 │                │── similarity ─────────────────────►  │               │
 │                │── params          │                  │               │
 │                │                   │                  │               │
 │                │              ┌────┴─────────┐        │               │
 │                │              │Mood detection│        │               │
 │                │              │Genre matching│        │               │
 │                │              │Tag generation│        │               │
 │                │              │Candidate gen │        │               │
 │                │              └────┬─────────┘        │               │
 │                │                   │                  │               │
 │                │                   │         ┌────────┴──────────┐    │
 │                │                   │         │Multi-hop graph    │    │
 │                │                   │         │Underground detect.│    │
 │                │                   │         │Diversity mgmt     │    │
 │                │                   │         └────────┬──────────┘    │
 │                │                   │                  │               │
 │                │                   │── candidates ────────────────►   │
 │                │                   │                  │── candidates ►│
 │                │                   │                  │               │
 │                │                   │                  │    ┌──────────┴──────┐
 │                │                   │                  │    │Phase 1: Collect │
 │                │                   │                  │    │+ Filter         │
 │                │                   │                  │    ├─────────────────┤
 │                │                   │                  │    │Phase 2: Score   │
 │                │                   │                  │    │+ Rank           │
 │                │                   │                  │    ├─────────────────┤
 │                │                   │                  │    │Phase 3: Diversify│
 │                │                   │                  │    ├─────────────────┤
 │                │                   │                  │    │Phase 4: Explain │
 │                │                   │                  │    └──────────┬──────┘
 │                │                   │                  │               │
 │◄──────── ranked recommendations ──────────────────────────────────────│
```

---

## 4. Agent Deep Dive

### 4.1 Agent 1 — Planner Agent

> *The orchestrator. Runs first. Decides everything else.*

The Planner Agent is the entry point of the pipeline. It receives the raw user query and is responsible for understanding it completely before any music candidate is generated.

**Internal Workflow (Figure 3)**

```
User Query
     │
     ▼
┌─────────────────────────────────────────────────┐
│  QueryAnalyzer                                  │
│  ─────────────────────────────────────────────  │
│  1. LLM-assisted intent detection               │
│  2. Complexity analysis (simple / complex /     │
│     ambiguous)                                  │
│  3. Ambiguity detection and resolution          │
│  4. convert_understanding_to_entities()         │
└──────────────────────┬──────────────────────────┘
                       │  QueryUnderstanding
                       ▼
┌─────────────────────────────────────────────────┐
│  ContextAnalyzer                                │
│  ─────────────────────────────────────────────  │
│  1. Interpret context signals (activity, time,  │
│     setting)                                    │
│  2. Handle effective_intent overrides           │
│     (follow-up queries reuse prior context)     │
│  3. Transform raw context → effective intent    │
└──────────────────────┬──────────────────────────┘
                       │  effective_intent
                       ▼
┌─────────────────────────────────────────────────┐
│  EntityProcessor                                │
│  ─────────────────────────────────────────────  │
│  1. Extract: artist names                       │
│  2. Extract: genre keywords                     │
│  3. Extract: mood signals (happy, sad, chill…)  │
│  4. Extract: activity / context triggers        │
└──────────────────────┬──────────────────────────┘
                       │  entities dict
                       ▼
┌─────────────────────────────────────────────────┐
│  StrategyPlanner                                │
│  ─────────────────────────────────────────────  │
│  1. Select recommendation strategy              │
│  2. Decide which agents to activate             │
│  3. Set parameters per agent                    │
│  4. Determine candidate pool size               │
│  5. Build coordination plan                     │
└──────────────────────┬──────────────────────────┘
                       │  coordination plan
                       ▼
           GenreMood + Discovery Agents
```

**State outputs written by Planner:**

| State Field | Type | Description |
|-------------|------|-------------|
| `query_understanding` | `QueryUnderstanding` | Intent, complexity, entities |
| `entities` | `Dict` | artists, genres, moods, activities |
| `intent_analysis` | `Dict` | complexity level, intent type |
| `planning_strategy` | `Dict` | pool sizes, strategy parameters |
| `agent_coordination` | `Dict` | which agents activate, in what order |

---

### 4.2 Agent 2 — GenreMood Agent

> *The emotion specialist. Translates feelings into music.*

The GenreMood Agent receives the coordination plan from the Planner and is activated for genre, mood, context, and hybrid queries. Its primary role is to detect emotional content in the query and map it to music genre signals.

**Internal Workflow (Figure 4)**

```
Planner Coordination Plan (genre/mood params)
     │
     ▼
┌─────────────────────────────────────────────────┐
│  GenreMoodConfig                                │
│  ─────────────────────────────────────────────  │
│  Load intent-specific parameters:               │
│  - candidate pool size                          │
│  - mood weight vs genre weight                  │
│  - context boost flags                          │
└──────────────────────┬──────────────────────────┘
                       │
              ┌────────┴──────────┐
              ▼                   ▼
┌─────────────────┐   ┌──────────────────────────┐
│ MoodAnalyzer    │   │ GenreProcessor            │
│ ─────────────── │   │ ──────────────────────── │
│ Detect mood     │   │ Match genre tags          │
│ from query:     │   │ Expand via alias maps     │
│  happy/sad/     │   │ (e.g. "lo-fi" →           │
│  energetic/     │   │  lo-fi hip hop, chillhop) │
│  chill/romantic │   │ Filter by genre overlap   │
│  /focused       │   └──────────────┬────────────┘
└────────┬────────┘                  │
         │                           │
         └──────────┬────────────────┘
                    ▼
┌─────────────────────────────────────────────────┐
│  TagGenerator                                   │
│  ─────────────────────────────────────────────  │
│  Generate enhanced search tags by combining:    │
│  - Genre signals from GenreProcessor            │
│  - Mood signals from MoodAnalyzer               │
│  - Context-aware tag boost                      │
│  - Activity-based tag augmentation              │
└──────────────────────┬──────────────────────────┘
                       │  enhanced_tags
                       ▼
┌─────────────────────────────────────────────────┐
│  UnifiedCandidateGenerator                      │
│  ─────────────────────────────────────────────  │
│  Generate candidates from shared dataset:       │
│  - Filter by genre match (Jaccard overlap)      │
│  - Filter by mood signal alignment              │
│  - Apply popularity range filters               │
└──────────────────────┬──────────────────────────┘
                       │  candidates
                       ▼
┌─────────────────────────────────────────────────┐
│  QualityScorer                                  │
│  ─────────────────────────────────────────────  │
│  Score each candidate:                          │
│  - genre_fit: overlap between track and target  │
│  - mood_alignment: mood signal match            │
│  - popularity_balance: avoid over-mainstream    │
└──────────────────────┬──────────────────────────┘
                       │
                       ▼
             genre_mood_recommendations
             (candidate pool → Judge)
```

---

### 4.3 Agent 3 — Discovery Agent

> *The explorer. Finds what you didn't know you needed.*

The Discovery Agent is activated for similarity, discovery, and artist queries. It specializes in multi-hop graph exploration — starting from a known artist and traversing genre neighbours to find both mainstream matches and underground hidden gems.

**Internal Workflow (Figure 5)**

```
Planner Coordination Plan (similarity/discovery params)
     │
     ▼
┌─────────────────────────────────────────────────┐
│  DiscoveryConfig                                │
│  ─────────────────────────────────────────────  │
│  Set discovery parameters:                      │
│  - novelty_weight (0.0 – 1.0)                   │
│  - similarity_depth (hop count)                 │
│  - underground_threshold (popularity ceiling)   │
│  - final_recommendations count                  │
└──────────────────────┬──────────────────────────┘
                       │
            ┌──────────┴──────────┐
            ▼                     ▼
┌─────────────────────┐  ┌─────────────────────────────┐
│  SimilarityExplorer │  │  UndergroundDetector        │
│  ───────────────── │  │  ─────────────────────────  │
│  Multi-hop artist   │  │  Detect hidden gems:        │
│  similarity graph:  │  │  - Score novelty vs pop.    │
│  - Hop 1: same      │  │  - Filter pop < threshold   │
│    genre artist     │  │  - Prioritise tracks with   │
│  - Hop 2: genre     │  │    followers < mainstream   │
│    neighbours       │  │    ceiling                  │
│  - Hop 3: sonic     │  │  - Serendipity bonus        │
│    relatives        │  └──────────────┬──────────────┘
└──────────┬──────────┘                 │
            └──────────┬────────────────┘
                       ▼
┌─────────────────────────────────────────────────┐
│  DiscoveryFilter                                │
│  ─────────────────────────────────────────────  │
│  Post-processing:                               │
│  - Remove irrelevant candidates                 │
│  - Deduplicate (same track from multiple hops)  │
│  - Apply quality floor threshold                │
│  - Remove reference artist tracks (similarity) │
└──────────────────────┬──────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────┐
│  DiscoveryDiversity                             │
│  ─────────────────────────────────────────────  │
│  Manage variety in candidate pool:              │
│  - Prevent artist clustering (max N per artist) │
│  - Balance mainstream vs niche ratio            │
│  - Ensure genre spread within pool              │
└──────────────────────┬──────────────────────────┘
                       │
                       ▼
             discovery_recommendations
             (candidate pool → Judge)
```

---

### 4.4 Agent 4 — Judge Agent

> *The final decision maker. Ranks, diversifies, and explains.*

The Judge Agent receives candidate pools from both GenreMood and Discovery, merges them, and applies a four-phase evaluation pipeline to produce the final recommendations.

**Internal Workflow (Figure 6)**

```
genre_mood_recommendations + discovery_recommendations
                       │
                       ▼
┌─────────────────────────────────────────────────┐
│  Phase 1 — CandidateSelector                    │
│  ─────────────────────────────────────────────  │
│  1. Collect all agent candidate pools           │
│  2. Validate each candidate (required fields)   │
│  3. Filter by quality threshold                 │
│  4. Deduplicate (same track from 2 agents)      │
│  5. Get candidate statistics (source breakdown) │
└──────────────────────┬──────────────────────────┘
                       │  validated candidates
                       ▼
┌─────────────────────────────────────────────────┐
│  Phase 2 — RankingEngine                        │
│  ─────────────────────────────────────────────  │
│  For each candidate:                            │
│  1. calculate_contextual_relevance()            │
│     - genre match against Planner entities      │
│     - mood alignment from intent analysis       │
│  2. Combine with agent-assigned scores:         │
│     - quality score (from QualityScorer)        │
│     - novelty score (from DiscoveryScorer)      │
│     - source priority weight                    │
│  3. rank_candidates() → sorted list             │
│                                                 │
│  Final Score = Σ(weight_i × score_i)            │
│  where weights are intent-specific              │
└──────────────────────┬──────────────────────────┘
                       │  scored + ranked candidates
                       ▼
┌─────────────────────────────────────────────────┐
│  Phase 3 — DiversityOptimizer                   │
│  ─────────────────────────────────────────────  │
│  MMR-style (Maximal Marginal Relevance) select: │
│  1. select_with_diversity(candidates, state, N) │
│  2. Penalise if same artist already in list     │
│  3. Ensure genre spread across final N          │
│  4. calculate_diversity_score() for metadata    │
└──────────────────────┬──────────────────────────┘
                       │  diverse selections
                       ▼
┌─────────────────────────────────────────────────┐
│  Phase 4 — ExplanationGenerator                 │
│  ─────────────────────────────────────────────  │
│  For each selected track:                       │
│  1. Calculate genre_match (0–100)               │
│  2. Calculate popularity_fit (0–100)            │
│  3. Calculate artist_score (log-normalised)     │
│  4. Calculate overall_relevance (weighted)      │
│  5. Calculate per-track confidence (0.0–1.0)    │
│  6. Generate human-readable explanation text    │
│  7. Attach to TrackRecommendation object        │
└──────────────────────┬──────────────────────────┘
                       │
                       ▼
         final_recommendations
         + judge_metadata (diversity + score stats)
```

---

## 5. Data Pipeline

**Figure 7 — Data Pipeline Flowchart**

```
┌─────────────────────┐   ┌──────────────────────────┐
│ track_data_final.csv│   │ spotify_data clean.csv   │
│ 8,778 tracks        │   │ Genre enrichment source  │
│ track + artist      │   │                          │
│ genres + popularity │   │                          │
│ followers + album   │   │                          │
└──────────┬──────────┘   └──────────────┬───────────┘
           │                              │
           └──────────────┬───────────────┘
                          ▼
              ┌────────────────────────┐
              │  Parse Genres          │
              │  ─────────────────── │
              │  ast.literal_eval()   │
              │  fallback string split│
              │  handle malformed     │
              │  genre strings        │
              └──────────┬────────────┘
                         │
                         ▼
              ┌────────────────────────┐
              │  Build Artist-Genre Map│
              │  ─────────────────── │
              │  Merge both CSVs       │
              │  artist_name →         │
              │  List[genre]           │
              │  ~61% genre coverage   │
              │  (vs 49% primary only) │
              └──────────┬────────────┘
                         │
                         ▼
              ┌────────────────────────┐
              │  Enrich Missing Genres │
              │  ─────────────────── │
              │  Back-fill tracks with │
              │  no genre label from   │
              │  merged artist map     │
              └──────────┬────────────┘
                         │
                         ▼
              ┌────────────────────────┐
              │  Index Columns         │
              │  ─────────────────── │
              │  artist_lower          │
              │  track_lower           │
              │  genres_lower          │
              │  (for O(1) lookups)    │
              └──────────┬────────────┘
                         │
                         ▼
              ┌────────────────────────┐
              │  Shared Agent Dataset  │
              │  ─────────────────── │
              │  Loaded once at        │
              │  application startup   │
              │  Shared in-memory      │
              │  across all 4 agents   │
              │  (singleton DataFrame) │
              └────────────────────────┘
```

**Table 1 — Dataset Summary**

| Property | Value |
|----------|-------|
| Primary source | `track_data_final.csv` |
| Secondary source | `spotify_data clean.csv` |
| Total tracks | **8,778** |
| Unique artists | ~4,200 |
| Key fields | `track_name`, `artist_name`, `artist_genres`, `track_popularity`, `artist_followers`, `album_release_date` |
| Genre coverage (primary only) | ~49% |
| Genre coverage (after enrichment) | **~61%** |
| Genre labels (unique) | 200+ |
| Popularity range | 0–100 |
| Release years | 1960s–2024 |

---

## 6. Metric and Confidence Formulas

**Figure 8 — Metric and Confidence Formula Block Diagram**

```
                    ┌───────────────┐
                    │  Track t      │
                    │  Target G     │
                    └──────┬────────┘
                           │
          ┌────────────────┼─────────────────────┐
          ▼                ▼                      ▼
┌──────────────────┐ ┌──────────────┐  ┌──────────────────────┐
│  Genre Match     │ │Popularity Fit│  │  Artist Score        │
│  ─────────────── │ │──────────────│  │  ──────────────────  │
│  genre_overlap   │ │track_pop     │  │  min(100,            │
│  (t, G) × 100   │ │────────── ×  │  │  (log10(followers)   │
│                  │ │100           │  │  / 8) × 100)         │
│  Jaccard-inspired│ │              │  │                      │
│  substring match │ │              │  │  100k → ~40          │
└────────┬─────────┘ └──────┬───────┘  └──────────┬───────────┘
         │                  │                      │
         │ w=0.45           │ w=0.30               │ w=0.25
         └──────────────────┼──────────────────────┘
                            ▼
              ┌──────────────────────────────┐
              │  Overall Relevance           │
              │  ────────────────────────── │
              │  GM×0.45 + PF×0.30 + AS×0.25│
              └──────────────┬───────────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │  Per-Track Confidence        │
              │  ────────────────────────── │
              │  (GM×0.50 + AS×0.30          │
              │   + PF×0.20) / 100          │
              │  clipped to [0.0, 1.0]       │
              └──────────────┬───────────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │  System Confidence           │
              │  ────────────────────────── │
              │  min(100,                    │
              │   avg_conf × 75             │
              │   + strategy_premium        │
              │   + diversity_bonus)        │
              └──────────────────────────────┘
```

**Table 3 — Per-Track Metric Formulas**

| Metric | Formula | Weight in Relevance | Calculated By |
|--------|---------|-------------------|---------------|
| Genre Match | `genre_overlap(track, target) × 100` | 45% | GenreMood / Discovery / Judge |
| Popularity Fit | `(track_popularity / 100) × 100` | 30% | Judge (ExplanationGenerator) |
| Artist Score | `min(100, (log₁₀(followers) / 8) × 100)` | 25% | Judge (ExplanationGenerator) |
| Overall Relevance | `GM×0.45 + PF×0.30 + AS×0.25` | — | Judge |
| Per-Track Confidence | `(GM×0.50 + AS×0.30 + PF×0.20) / 100` | — | Judge |

**Table 4 — System Confidence Breakdown**

| Component | Contribution |
|-----------|-------------|
| `avg_confidence × 75` | Base — average per-track confidence |
| Strategy Premium | +10 artist_similarity, +8 similarity, +6 genre_mood, +4 text, +0 fallback |
| Diversity Bonus | `min(10, unique_genre_count)` |
| System Confidence | `min(100, base + premium + bonus)` |

---

## 7. Frontend and UI

### 7.1 Frontend Component Hierarchy

**Figure 9 — Frontend Component Tree**

```
App.jsx  (search state · results state · loading state)
├── Stars.jsx
│   └── HTML5 Canvas — 200 stars, independent drift + twinkle
│       Each star: x, y, r, baseOp, speed, drift, driftY, phase
│       requestAnimationFrame loop at 60fps
│
├── HeroTitle.jsx
│   └── "ManTarang" — letter-by-letter hover animation
│       Colour wave: idle → hover → blue + gold
│       Music note particles on hover
│
├── SkeletonCard.jsx × 5  (shown during loading)
│   └── Bone components with --wave-delay CSS variable
│       Domino-wave left→right ripple effect
│       wave-pulse + bone-slide keyframes
│
├── QualityPanel
│   ├── System confidence % badge
│   ├── Strategy name + track count
│   └── Collapsible metric bars
│       (avg_confidence, genre_diversity, artist_diversity)
│
└── TrackCard.jsx × N  (one per recommendation)
    ├── Rank badge + title + artist + album
    ├── Genre chips  (coloured by source)
    ├── External links: Last.fm · Spotify · YouTube
    ├── GlowCard.jsx  (mouse spotlight radial gradient)
    │   CSS vars: --gx --gy track cursor position
    └── MetricsBar.jsx  (expandable, shown on Details ▾)
        ├── SVG confidence ring  (animated stroke-dashoffset)
        └── 4 animated progress bars:
            Genre Match · Popularity Fit · Artist Score · Relevance
```

### 7.2 Key UI Features

| Feature | Implementation |
|---------|---------------|
| Animated star field | Canvas API, 200 stars, ±0.18px/frame drift, twinkle via sin() |
| Hero letter animation | CSS transform per letter, colour wave + music note particles |
| Skeleton loading | 5 placeholder cards with CSS domino-wave, min 1200ms display |
| Mouse spotlight | CSS `radial-gradient` centred on cursor via `--gx`/`--gy` CSS vars |
| Confidence ring | SVG circle + `stroke-dashoffset` animation |
| React 18 fix | Double `requestAnimationFrame` before fetch to guarantee skeleton paint |
| Space background | `blackhole.png` fixed cover, `rgba(2,4,16,0.55)` overlay |

---

## 8. Implementation

### 8.1 Key Code: Planner Agent — Query Understanding

```python
async def process(self, state: MusicRecommenderState) -> MusicRecommenderState:
    # Phase 1: Query Understanding and Entity Extraction
    query_understanding, entities = await self._handle_query_understanding(state)
    state.query_understanding = query_understanding
    state.entities = entities

    # Phase 2: Task Complexity Analysis
    task_analysis = await self._analyze_task_complexity(
        state.user_query, query_understanding
    )
    state.intent_analysis = task_analysis

    # Phase 3: Planning Strategy
    state.planning_strategy = await self._create_planning_strategy(
        query_understanding, task_analysis
    )

    # Phase 4: Agent Coordination Plan
    state.agent_coordination = await self._plan_agent_coordination(
        state.user_query, task_analysis
    )
    return state
```

### 8.2 Key Code: Judge Agent — Four-Phase Pipeline

```python
async def process(self, state: MusicRecommenderState) -> MusicRecommenderState:
    # Phase 1: Candidate Collection and Filtering
    candidates = await self._collect_and_filter_candidates(state)

    # Phase 2: Scoring and Ranking
    scored_candidates = await self._score_and_rank_candidates(candidates, state)

    # Phase 3: Diversity Optimization
    diverse_selections = self._apply_diversity_optimization(scored_candidates, state)

    # Phase 4: Explanation Generation
    explained_selections = await self._generate_explanations(diverse_selections, state)

    state.final_recommendations = explained_selections
    state.judge_metadata = self._create_judge_metadata(
        candidates, scored_candidates, diverse_selections, explained_selections
    )
    return state
```

### 8.3 Key Code: Per-Track Confidence Formula

```python
# Artist Score — log-normalisation
# 100k followers → ~40,  1M → ~60,  10M → ~80,  100M → ~100
artist_score = round(min(100, max(0,
    (math.log10(max(followers, 1)) / 8) * 100
)))

# Per-track confidence (0.0 – 1.0)
confidence = round(min(1.0, (
    genre_match   * 0.50 +   # genre alignment is primary signal
    artist_score  * 0.30 +   # log-normalised follower count
    popularity_fit * 0.20    # raw popularity score
) / 100), 3)
```

### 8.4 Key Code: Animated Stars (Canvas)

```jsx
// 200 stars with independent drift velocity and twinkle phase
const stars = Array.from({ length: 200 }, () => ({
  x:      rand(0, window.innerWidth),
  y:      rand(0, window.innerHeight),
  r:      rand(0.4, 1.8),
  baseOp: rand(0.35, 0.9),
  speed:  rand(0.0004, 0.0014),  // twinkle frequency
  drift:  rand(-0.18, 0.18),     // horizontal px/frame
  driftY: rand(-0.10, 0.10),     // vertical px/frame
  phase:  rand(0, Math.PI * 2),
}));

// Per-frame: update position, compute opacity via sin(), draw
const op = s.baseOp * (0.5 + 0.5 * Math.sin(t * s.speed * 60 + s.phase));
ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
ctx.fillStyle = `rgba(200,220,255,${op})`;
```

### 8.5 Key Code: React 18 Skeleton Timing Fix

```jsx
// React 18 batches state updates — setLoading(true) + fetch in the same
// tick means the browser never paints the skeleton first.
// Double requestAnimationFrame guarantees one full browser paint cycle.
const doSearch = (q) => {
  setLoading(true);
  requestAnimationFrame(() => {
    requestAnimationFrame(() => {      // skeleton is now painted
      const MIN_MS = 1200;
      const start  = Date.now();
      fetch("/api/recommendations", { method: "POST", body: ... })
        .then(data => {
          const wait = Math.max(0, MIN_MS - (Date.now() - start));
          setTimeout(() => { setResults(data); setLoading(false); }, wait);
        });
    });
  });
};
```

### 8.6 API Contract

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
      "genres": ["alternative rock", "indie rock"],
      "confidence": 0.842,
      "source": "genre_mood",
      "explanation": "Strong genre match: alternative rock · indie rock",
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
    "strategy": "genre_mood",
    "agents_used": ["planner", "genre_mood", "judge"]
  }
}
```

---

## 9. Evaluation

### 9.1 Query Coverage by Intent

| Query | Intent Selected | Agents Activated | Tracks |
|-------|----------------|-----------------|--------|
| "songs by Radiohead" | `by_artist` | Planner + GenreMood + Judge | 8 |
| "music like Radiohead" | `artist_similarity` | Planner + Discovery + Judge | 10 |
| "dark indie rock" | `genre_mood` | Planner + GenreMood + Judge | 10 |
| "vibe coding" | `contextual` | Planner + GenreMood + Judge | 10 |
| "sad heartbreak songs" | `genre_mood` | Planner + GenreMood + Judge | 10 |
| "discover underground electronic" | `discovery` | Planner + Discovery + Judge | 10 |
| "dark indie but energetic" | `hybrid` | Planner + GenreMood + Discovery + Judge | 10 |

### 9.2 System Confidence Benchmarks

| Intent Type | Typical System Confidence |
|-------------|--------------------------|
| Artist Match | 75–90% |
| Similarity | 65–80% |
| Genre / Mood (specific) | 60–75% |
| Contextual | 55–70% |
| Discovery | 50–65% |
| Popular Fallback | 30–45% |

### 9.3 Response Time

| Stage | Time |
|-------|------|
| Dataset load (application startup) | ~1.2s |
| Planner Agent processing | ~15–40ms |
| GenreMood + Discovery (parallel) | ~20–60ms |
| Judge Agent (scoring + diversity) | ~10–30ms |
| Full pipeline (typical) | **50–150ms** |
| Skeleton display minimum | 1200ms (UX minimum) |

### 9.4 Dataset Coverage

| Metric | Value |
|--------|-------|
| Total tracks | 8,778 |
| Unique artists | ~4,200 |
| Tracks with genre data | ~61% |
| Genre labels (unique) | 200+ |
| Popularity range | 0–100 |
| Release years | 1960s–2024 |

---

## 10. Discussion

### 10.1 Summary of Work

**Phase 1 — Agent Architecture Design:**
The system was designed as a 4-agent pipeline from the ground up, following the Single Responsibility Principle. Each agent was further decomposed into focused sub-components (e.g., PlannerAgent → QueryAnalyzer + ContextAnalyzer + StrategyPlanner + EntityProcessor), reducing the main agent files from 1,000+ lines to ~400 lines each.

**Phase 2 — Backend Implementation:**
The 4-agent pipeline was implemented in Python with FastAPI, using a shared `MusicRecommenderState` object passed through the agents. The dataset was enriched by merging two Spotify CSV sources, raising genre coverage from 49% to 61%. Agents are initialized once at startup and share the in-memory DataFrame.

**Phase 3 — Frontend Implementation:**
A space-themed React UI was built with Framer Motion animations, a canvas-based star field, per-track expandable metrics, domino-wave skeleton loading, and a system quality panel. Key engineering challenges included React 18 batching (skeleton never painting) and font visibility on the blackhole image background.

### 10.2 Challenges Faced

| Challenge | Root Cause | Solution |
|-----------|-----------|---------|
| LLM-only prototype recommended Radiohead for every query | LLM hallucinated or over-anchored on the example artist | Replaced with deterministic 4-agent rule-based pipeline |
| Skeleton screen never appearing | React 18 batches state + fetch in one render tick | Double `requestAnimationFrame` before fetch call |
| Genre coverage too low (49%) | Only primary CSV had genre labels | Merged both CSVs into unified artist→genre map |
| `diskcache` import error on HuggingFace | `services/__init__.py` auto-imported unused CacheManager | Cleared `__init__.py` stubs to minimum |
| GitHub README XML error | Bare `&` in HTML `<img src="">` attributes | Rewrote README in pure markdown, zero HTML divs |
| Hero fonts invisible on image background | Text colour designed for dark canvas, not photo | Strong `text-shadow` + bright `#e8f0ff` palette |

### 10.3 Success Criteria Met

| Criterion | Status |
|-----------|--------|
| Natural-language query accepted | Done |
| 4-agent pipeline coordinated | Done |
| Per-track metrics displayed | Done |
| System confidence calculated | Done |
| Explainable recommendations | Done |
| Animated, polished UI | Done |
| Zero-cost deployment (CPU) | Done — HuggingFace CPU Basic, free |
| Sub-200ms response time | Done — typically 50–150ms |

### 10.4 Limitations

1. **No personalisation:** No user accounts or listening history — every search is fresh.
2. **Static dataset:** Track catalogue frozen at CSV export date; new releases not included.
3. **Genre label sparsity:** 39% of tracks lack genre labels, falling back to popularity-only scoring.
4. **English queries only:** Intent detection and keyword tables are English-only.
5. **No audio preview:** Links to Spotify/Last.fm/YouTube but no in-app playback.
6. **Cold start on HF Spaces:** After 48h inactivity the Space hibernates (~20s to wake).

---

## 11. Future Work

### 11.1 Scope for Improvements

| Improvement | Approach |
|-------------|---------|
| Semantic query understanding | Replace rule-based NLU with a small sentence-transformer (e.g. `all-MiniLM-L6-v2`) |
| Audio feature-based MER | Incorporate Spotify's `danceability`, `energy`, `valence` features for richer emotion alignment |
| Real-time data | Periodic Spotify API sync for new releases |
| Fifth Agent — Personalisation Agent | Maintain session-based listening history, feed preferences into Planner coordination plan |
| Multilingual queries | Translation layer before Planner Agent |
| In-app audio preview | Spotify embed widget or 30s preview URLs |
| Feedback loop | Thumbs up/down ratings → adjust Judge Agent scoring weights per user |
| Vector similarity search | Replace Jaccard overlap with dense embeddings + approximate nearest neighbour search |

### 11.2 Possible Real-World Deployment Strategies

| Scenario | Architecture |
|----------|-------------|
| **Production SaaS** | AWS ECS / GCP Cloud Run, PostgreSQL for user data, Redis query cache, CDN for React build |
| **Mobile App** | React Native frontend, same FastAPI backend behind API Gateway |
| **Embedded Widget** | REST API exposed to third-party sites (radio stations, playlist curators) |
| **Offline / Edge** | Scoring logic compiled to WASM; run entirely in-browser with a compressed track index |
| **Enterprise** | White-label the 4-agent engine; custom datasets per music platform |

---

## 12. Appendix

### 12.1 Project Structure

```
MER FINAL/
├── mantarang/
│   └── src/
│       ├── agents/
│       │   ├── planner/                 ← Agent 1: Orchestrator
│       │   │   ├── agent.py
│       │   │   ├── query_analyzer.py
│       │   │   ├── context_analyzer.py
│       │   │   ├── strategy_planner.py
│       │   │   └── entity_processor.py
│       │   ├── genre_mood/              ← Agent 2: Emotion Specialist
│       │   │   ├── agent.py
│       │   │   └── components/
│       │   │       ├── genre_mood_config.py
│       │   │       ├── mood_analyzer.py
│       │   │       ├── genre_processor.py
│       │   │       └── tag_generator.py
│       │   ├── discovery/               ← Agent 3: Explorer
│       │   │   ├── agent.py
│       │   │   ├── discovery_config.py
│       │   │   ├── discovery_scorer.py
│       │   │   ├── discovery_filter.py
│       │   │   └── discovery_diversity.py
│       │   └── judge/                   ← Agent 4: Decision Maker
│       │       ├── agent.py
│       │       └── components/
│       │           ├── candidate_selector.py
│       │           ├── ranking_engine.py
│       │           ├── diversity_optimizer.py
│       │           └── explanation_generator.py
│       ├── api/
│       │   └── backend.py               ← FastAPI routes + static serving
│       ├── models/
│       │   ├── agent_models.py          ← MusicRecommenderState, AgentConfig
│       │   └── recommendation_models.py ← TrackRecommendation
│       └── services/
│           ├── api_service.py
│           └── metadata_service.py
├── mantarang-ui/
│   ├── src/
│   │   ├── App.jsx                      ← Search · Results · State
│   │   ├── index.css                    ← Global styles + keyframes
│   │   └── components/
│   │       ├── HeroTitle.jsx            ← Letter hover animation
│   │       ├── TrackCard.jsx            ← Per-track display
│   │       ├── MetricsBar.jsx           ← SVG ring + progress bars
│   │       ├── SkeletonCard.jsx         ← Domino-wave loading
│   │       ├── Stars.jsx                ← Canvas 200-star field
│   │       └── GlowCard.jsx             ← Mouse spotlight wrapper
│   ├── index.html
│   └── vite.config.js
├── track_data_final.csv                 ← Primary dataset (8,778 tracks)
├── spotify_data clean.csv              ← Genre enrichment dataset
├── Dockerfile                          ← Multi-stage: Node build → Python
├── requirements-hf.txt                 ← Python dependencies
├── METRICS.md                          ← Metric formula reference
└── PROJECT_REPORT.md                   ← This file
```

### 12.2 Technology Stack

**Table 5 — Technology Stack**

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| Agent Framework | Python — 4 agent classes | 3.11 | Planner, GenreMood, Discovery, Judge |
| Backend API | FastAPI + Uvicorn | 0.115 | REST API, CORS, static file serving |
| Data Processing | Pandas | 2.x | Dataset loading, enrichment, indexing |
| Data Validation | Pydantic | v2 | State models, request/response schemas |
| Frontend Framework | React | 18 | SPA, component tree, state management |
| Frontend Build | Vite | 5.x | Hot reload, /api proxy, production build |
| Animation Library | Framer Motion | 11.x | Page transitions, AnimatePresence |
| Canvas Animation | HTML5 Canvas API | — | 200-star animated star field |
| Containerisation | Docker (multi-stage) | — | Node build then Python serve |
| Deployment | HuggingFace Spaces | CPU Basic | Zero-cost, port 7860 |

### 12.3 Key Links

| Resource | URL |
|----------|-----|
| **Live Demo** | https://huggingface.co/spaces/ashu-17/mantarang |
| **GitHub Repository** | https://github.com/Ashutosh-177/ManTarang-AI-Powered-Music-Recommendation-System |

### 12.4 Dependencies

**Backend (`requirements-hf.txt`)**
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

**Frontend (`package.json` key dependencies)**
```json
{
  "react": "^18.0.0",
  "framer-motion": "^11.0.0",
  "vite": "^5.0.0"
}
```

---

---

## Project Pitch Prompt

> *Use this paragraph to describe ManTarang in presentations, posters, or introductions:*

**ManTarang** is an AI-powered **Music Emotion Recognition (MER)** system that accepts natural-language queries and returns ranked, explained music recommendations through a **4-agent collaborative AI pipeline**. A **Planner Agent** orchestrates the workflow by analysing query intent and coordinating the other agents. A **GenreMood Agent** maps the user's emotional signals to musical genre tags and generates mood-matched candidates. A **Discovery Agent** traverses artist similarity graphs to surface both mainstream matches and underground hidden gems. Finally, a **Judge Agent** merges all candidates, applies a multi-criteria ranking algorithm, optimises diversity, and generates human-readable explanations with quantitative confidence metrics for every recommendation. The system is built on Python FastAPI and React, deployed on HuggingFace Spaces (CPU only, zero cost), and delivers recommendations in under 200 milliseconds over a curated dataset of 8,778 Spotify tracks.

---

*Report prepared by Ashutosh Kumar Singh (92301733016) and Aditya Raj (92301733062)*
*ManTarang — AI-Powered Music Emotion Recognition | May 2026*
