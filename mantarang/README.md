# ManTarang – Waves of thoughts

**ManTarang** is an AI-powered music discovery application that uses four specialized agents collaborating through strategic planning to recommend music tracks. The system understands natural language queries and returns personalized recommendations with transparent reasoning.

---

## What This Project Does

When a user types something like *"I want focus music for coding"* or *"songs similar to Radiohead but more underground"*, ManTarang:

1. Understands the intent behind the query
2. Creates a strategy for finding matching music
3. Searches multiple sources using different approaches
4. Ranks and filters the candidates
5. Returns recommendations with explanations of *why* each track was chosen

The key idea is that instead of one monolithic model doing everything, four specialized agents each handle a specific responsibility and pass their results to the next.

---

## How the System Works

### Full Data Flow

```
User Query (Gradio UI)
        |
        v  HTTP POST /recommendations
FastAPI backend.py
        |
        v  startup: initialize_agents()
AgentCoordinator
    ├── create_gemini_client()      →  Google Gemini ('gemini-2.0-flash-exp')
    ├── UnifiedRateLimiter          →  8 calls/min (Gemini free tier)
    ├── MetadataService             →  wraps LastFmClient
    └── instantiates all 4 agents  →  each gets gemini_client + api_service + rate_limiter
        |
        v  build_workflow_graph()
WorkflowOrchestrator (LangGraph StateGraph)
        |
        v  entry point
[PlannerAgent]
    QueryAnalyzer     →  1 LLM call  →  QueryUnderstanding + extracted entities
    StrategyPlanner   →  planning_strategy (sets agent_sequence for routing)
        |
        v  _route_agents() reads planning_strategy.agent_sequence
        |
        +-- "both_agents"     → [DiscoveryAgent] then [GenreMoodAgent]
        |
        +-- "discovery_only"  → [DiscoveryAgent] only
        |
        +-- "genre_mood_only" → [GenreMoodAgent] only
        |
[DiscoveryAgent]  (runs first when both agents are used)
    ChromaDB query               →  local CSV dataset candidates
    UnifiedCandidateGenerator    →  Last.fm API candidates
    DiscoveryScorer / Filter / Diversity
    _generate_batch_discovery_reasoning()  →  1 LLM call for all candidates
        |
        v  _route_after_discovery()
[GenreMoodAgent]
    UnifiedCandidateGenerator    →  Last.fm API candidates
    MoodAnalyzer / GenreProcessor / TagGenerator
    _generate_batch_reasoning()  →  1 LLM call for all candidates
        |
        v
[JudgeAgent]
    CandidateSelector   →  merges both agents' candidates, deduplicates
    RankingEngine       →  intent-aware scoring (contextual relevance)
    DiversityOptimizer  →  artist and genre diversity enforcement
    ExplanationGenerator →  LLM or rule-based per-track explanations
        |
        v  state.final_recommendations
StateManager.convert_to_unified_metadata()
transform_unified_to_ui_format()
        |
        v  JSON response
ResponseFormatter  →  Gradio chatbot + track panel
```

### The Four Agents

### PlannerAgent (`src/agents/planner/`)
Analyzes the user's query using Google Gemini. It:
- Extracts entities (artist names, genres, moods, activities) via `QueryAnalyzer`
- Detects the user's intent (discovery, artist similarity, mood-based, contextual)
- Handles multi-turn conversations and context from previous messages via `ContextAnalyzer`
- Produces a `planning_strategy` dict that controls which agents run and how
- Sub-components: `QueryAnalyzer`, `ContextAnalyzer`, `StrategyPlanner`, `EntityProcessor`

### GenreMoodAgent (`src/agents/genre_mood/`)
Takes the planner's strategy and fetches music candidates based on:
- Genre tags and mood descriptors via `MoodAnalyzer` and `GenreProcessor`
- Style matching using Last.fm tag data via `TagGenerator`
- Scores each candidate with a combined quality + genre/mood score
- Generates explanations in a single batch LLM call (one call for all candidates)

### DiscoveryAgent (`src/agents/discovery/`)
Runs before GenreMoodAgent (when both are needed) and focuses on:
- Querying the local ChromaDB vector database first, then falling back to Last.fm
- Underground and lesser-known track detection via `UndergroundDetector`
- Novelty scoring via `DiscoveryScorer` to avoid overplayed tracks
- Generates explanations in a single batch LLM call

### JudgeAgent (`src/agents/judge/`)
Receives candidates from both advocate agents and:
- Collects and deduplicates all candidates via `CandidateSelector`
- Scores each track against intent-aware criteria via `RankingEngine`
- Enforces artist and genre diversity via `DiversityOptimizer`
- Generates a human-readable explanation for each final recommendation via `ExplanationGenerator`

### Session and Context Management

- `SessionManagerService` stores per-user conversation history across requests
- `IntentOrchestrationService` detects whether a new query is a follow-up or a new search
- Follow-up queries (e.g. "more like that") reuse the existing candidate pool rather than regenerating
- A new session is automatically started when the user's intent changes significantly (e.g. switching from artist search to contextual/mood)

---

## Project Structure

```
BeatDebate/
├── app.py                      # Entry point for HuggingFace Spaces deployment
├── src/
│   ├── main.py                 # Local application entry point
│   ├── agents/
│   │   ├── base_agent.py       # Abstract base class all agents inherit from
│   │   ├── planner/            # PlannerAgent - query understanding and strategy
│   │   ├── genre_mood/         # GenreMoodAgent - style-based candidate generation
│   │   ├── discovery/          # DiscoveryAgent - similarity and novelty search
│   │   ├── judge/              # JudgeAgent - ranking, selection, explanation
│   │   └── components/         # Shared agent utilities
│   │       ├── unified_candidate_generator.py  # Fetches track candidates
│   │       ├── scoring/        # Quality scoring modules
│   │       └── generation_strategies/  # Different strategies for finding candidates
│   ├── api/
│   │   ├── backend.py          # FastAPI HTTP endpoints
│   │   ├── lastfm_client.py    # Last.fm API integration
│   │   ├── spotify_client.py   # Spotify API integration
│   │   └── rate_limiter.py     # Prevents hitting API rate limits
│   ├── services/
│   │   ├── recommendation_service.py       # Orchestrates the full agent workflow
│   │   ├── session_manager_service.py      # Manages per-user conversation state
│   │   ├── intent_orchestration_service.py # Handles follow-up query logic
│   │   ├── cache_manager.py                # Caches API responses to disk
│   │   └── metadata_service.py            # Combines data from multiple sources
│   ├── models/
│   │   ├── agent_models.py         # Pydantic models for agent state
│   │   ├── metadata_models.py      # Track and artist data schemas
│   │   └── recommendation_models.py # Request/response schemas
│   └── ui/
│       ├── chat_interface.py       # Gradio chat UI
│       ├── planning_display.py     # Shows agent reasoning in the UI
│       └── response_formatter.py  # Formats recommendations for display
├── scripts/
│   └── validate_lastfm.py          # Script to test Last.fm API connectivity
├── tests/                          # Unit and integration tests
├── Design/                         # Architecture and design documents
├── chroma_data/                    # ChromaDB vector database (local)
├── data/cache/                     # Disk cache for API responses
└── logs/                           # Application logs
```

---

## Technology Stack

| Component | Technology |
|---|---|
| Agent Orchestration | LangGraph |
| LLM (Language Model) | Google Gemini 2.5 Flash |
| Backend API | FastAPI |
| Frontend UI | Gradio |
| Music Data - Primary | Last.fm API |
| Music Data - Secondary | Spotify Web API |
| Vector Database | ChromaDB |
| Response Caching | diskcache |
| Data Validation | Pydantic |
| Logging | structlog |
| Dependency Management | uv |

---

## Setup and Installation

### Prerequisites
- Python 3.11 or higher
- API keys for: Google Gemini, Last.fm, and Spotify

### 1. Install the `uv` dependency manager
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Install dependencies
```bash
cd BeatDebate
uv venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
uv sync --dev
```

### 3. Add your API keys to `.env`
Open the `.env` file and replace the placeholder values:
```
GEMINI_API_KEY=your_gemini_api_key_here
LASTFM_API_KEY=your_lastfm_api_key_here
SPOTIFY_CLIENT_ID=your_spotify_client_id_here
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret_here
LASTFM_SHARED_SECRET=your_lastfm_shared_secret_here
```

**Where to get these keys:**
- **Gemini**: https://aistudio.google.com/ → Get API Key (free)
- **Last.fm**: https://www.last.fm/api/account/create (free)
- **Spotify**: https://developer.spotify.com/dashboard → Create App (free)

### 4. Run the application
```bash
uv run python -m src.main
```

This starts both:
- **Gradio UI** at `http://localhost:7860`
- **FastAPI backend** at `http://localhost:8000`

---

## Example Queries

```
"Play me something like Radiohead but more underground"
"I need chill lo-fi beats for studying"
"Find me electronic music similar to Four Tet"
"Give me energetic workout music"
"More tracks like the last ones but slower"
```

The system handles follow-up context — if you ask for "more underground" after an initial recommendation, it remembers what was already recommended and adjusts.

---

## Running Tests

```bash
# All tests
uv run pytest

# With coverage
uv run pytest --cov=src --cov-report=html

# Specific test file
uv run pytest tests/agents/test_planner_agent.py
```

## Code Quality

```bash
uv run black src/ tests/       # Format
uv run isort src/ tests/       # Sort imports
uv run ruff check src/ tests/  # Lint
uv run mypy src/               # Type check
```

---

## Bugs Fixed

The following issues were identified by tracing the full agent connection chain and corrected:

| # | File | Bug | Fix Applied |
|---|------|-----|-------------|
| 1 | `src/agents/judge/agent.py` | `JudgeAgent` used absolute imports (`from src.models...`) which break when the app is not run from the project root | Changed to relative imports (`from ...models...`) matching all other agents |
| 2 | `src/services/recommendation_service.py` | `_get_fallback_recommendations` imported `LLMFallbackService` via `from ..llm_fallback_service` (wrong parent path) | Fixed to `from .llm_fallback_service` (same package) |
| 3 | `src/api/backend.py` | `lifespan` still declared `context_manager` in the `global` statement after it was removed, causing a `NameError` on startup | Removed the stale reference from the `global` declaration |
| 4 | `src/ui/chat_interface.py` | Fallback service init imported `create_gemini_client` from `services.enhanced_recommendation_service`, a module that does not exist | Fixed to `from ..services.components.agent_coordinator import create_gemini_client` |
| 5 | `src/api/backend.py` | `GET /sessions/{id}/history` returned a hardcoded placeholder and never read actual session data | Wired to `smart_context_manager.get_session_context()` with structured response |
| 6 | `src/agents/genre_mood/agent.py` | `_generate_reasoning` was hardcoded to skip LLM entirely and called once per candidate (rate-limit risk) | Replaced with `_generate_batch_reasoning` — one LLM call covering all candidates, matching the pattern already used by `DiscoveryAgent` |

---

## Key Design Decisions

**Why four agents instead of one?**
Each agent can be specialized and improved independently. The PlannerAgent doesn't need to know how to fetch Last.fm data; the GenreMoodAgent doesn't need to understand conversation context. Separation of concerns makes the system easier to debug and extend.

**Why LangGraph for orchestration?**
LangGraph manages the state machine between agents — each agent reads from and writes to a shared `MusicRecommenderState` object. This makes the data flow explicit and auditable.

**Why both Last.fm and Spotify?**
Last.fm has richer tag/similarity data for underground music discovery. Spotify provides audio previews. Using both gives broader coverage.

**Caching strategy:**
All Last.fm and Spotify responses are cached to disk with configurable TTL. This reduces API calls during development and keeps the system within free-tier rate limits.

---

## Logs and Debugging

Logs are written to `logs/beatdebate.log` and `logs/errors.log`. The Gradio UI also displays the agent reasoning process in real-time under each recommendation, showing what each agent decided and why.
