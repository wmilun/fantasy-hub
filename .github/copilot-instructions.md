# Fantasy Hub - AI Coding Agent Instructions

Fantasy Hub is a personal fantasy football dashboard combining ESPN/Sleeper leagues and Pick'em data with a live Impact Feed. Uses Vue 3 + Vite frontend, FastAPI backend, and file-based persistence.

## Architecture

**Directory Structure:**
```
client/src/stores/     # Pinia state (matchupsSleeper, matchupsEspn, impactFeed)
server/app/services/   # External API integrations (sleeper.py, espn.py)  
server/app/core/       # Settings, cache, shared httpx clients
data/                  # config.yaml, picks-2025.json, cache/
```

**Service Layer Pattern:** Services transform upstream payloads → internal models → trimmed UI data
```python
# services/sleeper.py example
async def get_matchup(league_id: str, week: int) -> MatchupModel:
    # Cache check, upstream call, payload trimming
```

## Development Workflow

**Incremental Protocol:** Write minimal version → run locally → explain every line → commit → repeat

**Key Commands:**
```bash
# Server (WSL)
python -m venv .venv && source .venv/bin/activate  
pip install fastapi uvicorn httpx pydantic-settings python-dotenv pyyaml
uvicorn app.main:app --reload --port 8000

# Client
npm create vite@latest client -- --template vue-ts
npm install -D tailwindcss postcss autoprefixer
npm run dev -- --port 5173
```

## Configuration Patterns

- `data/config.yaml`: League IDs, team mappings, user GUIDs
- `.env`: API secrets (never committed), server boots without secrets for public paths
- **ESPN GUID Discovery:** DevTools → network filter `gambit-api.fantasy.espn.com` → copy `user_guid` from `/entries/` URL

## API & Caching Strategy

**Routes:** `/api/sleeper/matchup`, `/api/espn/scoreboard`, `/api/pickem/nfl/entry`
- Server handles all upstream calls (avoids CORS)
- Endpoint-specific TTLs: scoreboard 60s (live), play-by-play 20-30s (live), pick'em 5m
- File-based cache fallback in `data/cache/`

**Polling:** 30-60s normal, 15-20s live games, impact feed enriched with ownership data

## Project-Specific Conventions

- Prefer public APIs over authenticated endpoints
- File-based persistence before database complexity  
- Accessibility: color-safe Tailwind, keyboard navigation, visible loading states
- Educational approach: explain every line with Copilot
- Rate limiting and fair use design patterns