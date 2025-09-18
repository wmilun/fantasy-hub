# Fantasy Hub (Personal Project)

A single dashboard that pulls together everything I care about for fantasy football.

- ESPN Family League, full weekly matchup view
- Sleeper Friend League, full weekly matchup view
- ESPN Pick'em, weekly picks and results
- Impact Feed, scrolling feed of every scoring play and every play that affects my players or my opponents

This is not a general tool for others. It is tailored to my leagues, my players, and my pick'em entries.

---

## Technical Direction

**Frontend**: Vue 3 + Vite + TypeScript, Pinia (state), Vue Router, Tailwind CSS (utility styling)

**Backend**: FastAPI (Python), httpx for upstream calls, Uvicorn for local dev, simple in‑process cache

**Data**: local files at first (YAML + JSON), optional SQLite later

**Packaging**: Docker for both frontend and backend, docker compose for local orchestration, compatible with WSL today and a home server later

**Networking stance**: prefer **public endpoints** (Sleeper, ESPN scoreboard/play‑by‑play, ESPN Pick’em gambit API) with no auth where possible; fall back to cookies/keys only when required.

**Philosophy**: educational build. We will write every file line by line with Copilot in VS Code. This README is the scaffold for that journey.

---

## Run Modes

1. **Local dev, no containers (WSL)**
   - Separate dev servers for frontend and backend
   - Hot reload enabled
2. **Local dev, docker compose**
   - Same source code mount, dev servers inside containers
3. **Home server, docker compose**
   - Built images, env file only, persistent volume for data

We will keep parity between modes so behavior is consistent.

---

## Repository Layout (planned)

```
fantasy-hub/
  client/                     # Vue app (Vite)
    src/
      components/
      pages/
      stores/                 # Pinia
      router/
      lib/                    # client helpers and types
    index.html
    vite.config.ts
    package.json
    tailwind.config.ts
    postcss.config.js
    Dockerfile                # dev and prod stages
  server/                     # FastAPI app
    app/
      api/
        routes_sleeper.py
        routes_espn.py
        routes_picks.py
        routes_config.py
      core/
        settings.py
        cache.py
        clients.py            # shared httpx clients
      models/
        picks.py              # pydantic models
        config.py
      services/
        sleeper.py
        espn.py
        impact.py
      main.py
    tests/
    pyproject.toml
    Dockerfile
  data/
    picks-2025.json           # manual at first
    cache/                    # json snapshots, ignored in prod
    config.yaml               # league ids, team ids, player maps
  .env.example                # env var template
  docker-compose.yaml
  Makefile                    # convenience targets
  README.md                   # this file
```

We will create these files gradually. The tree is the north star, not a promise that everything exists yet.

---

## Data Sources

- **Sleeper API (public)** – documented, read‑only endpoints for leagues, rosters, users, players. No token required.
  - Docs and rate guidance in Sleeper’s site.
  - Key endpoints: `/league/{league_id}/matchups/{week}`, `/league/{league_id}/rosters`, `/league/{league_id}/users`, `/players/nfl`
- **ESPN Fantasy (unofficial, public JSON)** – matchup/scoreboard/play‑by‑play via ESPN’s public APIs.
  - Scoreboard: `https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard?dates=YYYYMMDD`
  - Core events list: `https://sports.core.api.espn.com/v2/sports/football/leagues/nfl/seasons/{year}/types/{type}/weeks/{week}/events`
  - Play‑by‑play for a game: `https://sports.core.api.espn.com/v2/sports/football/leagues/nfl/events/{eventId}/competitions/{eventId}/plays?limit=300`
  - Summary box: `https://site.api.espn.com/apis/site/v2/sports/football/nfl/summary?event={eventId}`
- **ESPN Pick’em (NFL only, Pigskin) – gambit API**
  - Entries (user‑scoped): `https://gambit-api.fantasy.espn.com/apis/v1/challenges/nfl-pigskin-pickem-{season}/entries/{user_guid}`
  - Notes:
    - These endpoints are readable without cookies for public data. Picks often become visible as games start; prior to kickoff, the API may not expose whether a given week’s picks are made (season list grows as games begin).
    - You’ll need your **ESPN account GUID** (`user_guid`) which is visible in the network tab when loading the Pick’em "My Entries" page. We’ll document the exact steps below.
- **MySportsFeeds (optional)** – free developer tier for personal/non‑commercial use; provides schedules, scores, box, and play‑by‑play. Use only if ESPN endpoints are insufficient.
- **Pick’em** – manual entry still supported as a fallback.

We will start read‑only. No writes to third‑party services.

---

## Features and Goals

1. **All matchups at once**
   - Show ESPN and Sleeper weekly matchups side by side
   - Include starters, benches, projected points, and live scores
2. **Impact feed (scoring + player impacts)**
   - Scrolling stream of every scoring play AND every play involving my or my opponents’ players
   - Each update annotated with:
     - Which team I picked in Pick’em for that game
     - Whether I or my opponent have any of the players involved
     - Otherwise, show who owns the players across my leagues (less priority)
   - Click on a play to expand details (drive context, box score, rosters involved)
   - Updates targeted at 30–120s during live games
   - Fallback: score change watcher when play‑by‑play is not available
3. **Pick'em tracking**
   - Separate view for weekly picks and results
   - Also integrated into impact feed annotations
   - Store weekly picks and results, easy entry and update
4. **Reminders**
   - Waiver deadlines, lineup lock, and final pick deadlines
   - Visible on dashboard, no push required at first

Must haves: side‑by‑side ESPN + Sleeper matchups, scrolling impact feed with annotations, minimal copy and paste, simple maintenance.

Nice to haves: red zone alerts, color coding, season charts, CSV export, better lineup alerts, free agent alerts.

---

## Configuration and Secrets

- `data/config.yaml`
  - `sleeper.league_id`
  - `espn.league_id`, `espn.team_id`, `espn.user_guid`
  - `me.player_map` for quick lookups if needed
- `.env` (never commit)
  - `ESPN_S2`, `ESPN_SWID` (only needed for private fantasy league data; **not** required for public scoreboard, play‑by‑play, or Pick’em entries)
  - `MSF_API_KEY` if used later
- `data/picks-2025.json` for pick'em entries
- `data/cache/` to hold the last successful responses for resilience and rate limit friendliness

We will design the server to boot without secrets for public data paths.

---

## Backend API (planned)

- `GET /api/sleeper/matchup?league={id}&week={w}`
- `GET /api/espn/scoreboard?date=YYYYMMDD`
- `GET /api/espn/playbyplay?event={id}`
- `GET /api/espn/events?season={yyyy}&type={2|3}&week={w}`
- `GET /api/pickem/nfl/entry?guid={user_guid}&season={yyyy}` → returns normalized picks, week grouping, and completion heuristics
- `GET /api/picks?week={w}` and `POST /api/picks` (local file writes only)
- `GET /api/config`

Rules:

- Server performs all upstream requests (avoid CORS in the browser, keep URLs centralized)
- Server trims payloads to just what the UI needs
- Each impact feed event enriched with Pick’em pick + fantasy ownership mapping
- Caching: per‑endpoint TTLs (scoreboard 30–60s in live windows; play‑by‑play 15–30s; pick’em 5m except just before kickoff)
- Respect fair use; exponential backoff with jitter

---

## Frontend UI (planned)

- Layout: side‑by‑side ESPN matchup and Sleeper matchup, with a scrolling impact feed alongside
- Separate view for Pick’em picks, but integrated data also shown in the feed
- Impact feed: scrollable list, click to expand details
- Settings page for league ids, team mapping, and ESPN `user_guid`
- Polling every 30–60s; faster (15–20s) when live plays are happening
- Pinia stores: `matchupsSleeper`, `matchupsEspn`, `impactFeed`, `pickem`
- Heuristic badges: "Picks complete?" (computed from pick’em entry + schedule)

---

## Caching, Rate Limits, and Resilience

- In‑memory TTL cache for dev; optional file cache of last good payloads in `data/cache/`
- Endpoint defaults (tune as we test):
  - Scoreboard 60s (live windows), 5m otherwise
  - Play‑by‑play 20–30s (live), 10m post‑final
  - Sleeper matchups 5m
  - Pick’em entries 5m, 60s in the 2‑hour window before first kickoff
- Circuit breaker + retries with backoff; always return the last good payload to the UI

---

## Dev Setup, No Containers (WSL)

These are the commands we will type and explain line by line with Copilot later. Listing here for planning only.

**Server**

```
python -m venv .venv
source .venv/bin/activate
pip install fastapi uvicorn httpx pydantic-settings python-dotenv pyyaml
uvicorn app.main:app --reload --port 8000
```

**Client**

```
npm create vite@latest client -- --template vue-ts
cd client
npm install
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
npm run dev -- --port 5173
```

WSL notes: expose `localhost` correctly, verify firewall rules in Windows, prefer Node LTS inside WSL.

**Discovering your ESPN `user_guid` for Pick’em**

1. Open your Pick’em "My Entries" page in a desktop browser.
2. Open DevTools → Network tab.
3. Filter for `gambit-api.fantasy.espn.com`.
4. Click any `/entries/` request; copy the 32‑char `user_guid` from the URL.
5. Add it to `data/config.yaml` under `espn.user_guid`.

---

## Docker and Compose (planned)

We will build both services in containers. The goal is: dev parity now, easy move to the home server later.

**docker-compose.yaml (outline)**

```
services:
  server:
    build: ./server
    env_file: .env
    volumes:
      - ./server:/app
      - ./data:/data
    ports:
      - "8000:8000"
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  client:
    build: ./client
    environment:
      - VITE_API_BASE=http://server:8000
    depends_on:
      - server
    volumes:
      - ./client:/app
    ports:
      - "5173:5173"
    command: npm run dev -- --host 0.0.0.0 --port 5173
```

**Server Dockerfile (outline)**

```
FROM python:3.12-slim
WORKDIR /app
# (we'll choose pip/poetry later)
RUN pip install --no-cache-dir fastapi uvicorn httpx pydantic-settings python-dotenv pyyaml
COPY server/ ./
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Client Dockerfile (outline)**

```
FROM node:22-alpine AS dev
WORKDIR /app
COPY client/package*.json ./
RUN npm ci
COPY client/ .
EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]

# Production image stage to be added later
```

We will fill these line by line and explain every argument.

---

## Testing Plan

- Unit tests for services that transform upstream payloads
- Contract tests for API routes, fixture snapshots for cache behavior
- Simple e2e smoke in dev: start compose, hit a couple of endpoints, ensure 200s

---

## Accessibility and UX Notes

- Color safe choices in Tailwind, no red‑green only cues
- Loading and error states visible on each card
- Keyboard navigation for the dashboard

---

## Iteration Protocol with Copilot

We will work in very small steps. For each file:

1. Write the smallest possible version
2. Run it locally
3. Discuss what the line does and why
4. Commit with a descriptive message
5. Repeat

Prompts to use with Copilot:

- “Propose a minimal `main.py` for FastAPI with health and `/api/config`.”
- “Generate a Pinia store skeleton for matchup state with types only.”
- “Draft a `sleeper.py` service that calls one endpoint and returns a trimmed model.”

We will ask Copilot to explain every line and we will adjust to match our style.

---

## Milestones

1. Repo scaffold builds and runs, one blank page renders
2. `/api/config` returns data from `config.yaml`
3. Sleeper matchup renders in the UI for a given week
4. ESPN matchup renders
5. Pick'em: implement `/api/pickem/nfl/entry`, show weekly picks, annotate impact feed with picks
6. Impact feed shows simulated events, then real polling from ESPN play‑by‑play
7. Docker dev flow works, then production build works

---

## Future Home Server Notes

- Compose file can be reused as is, change `VITE_API_BASE` to point at server hostname
- Add a named volume for `data/` so picks and caches persist
- Add Traefik or Caddy later for TLS and routing

---

## Open Questions

- Which free play‑by‑play source is reliable enough for a season
- How strict should caching and backoff be to respect fair use
- Do we want SQLite now or later
- Can we reliably enrich every play with Pick’em picks + fantasy ownership without too much overhead?

---

## License and Attribution

Personal use only. Do not redistribute or use this to scrape at scale. Respect upstream terms and rate limits.

---

## GitHub Workflow Addendum

This section outlines how GitHub Pro, Copilot, and VS Code can be used together to manage, track, and complete this project while keeping all runtime local.

---

### 1. Repository and Protection

* **Private repository** named `fantasy-hub`.
* Protect the `main` branch:

  * Require pull requests for changes.
  * Require status checks to pass before merging.
  * Dismiss stale reviews on new commits.
* Turn on **Dependabot alerts** and **CodeQL code scanning** for security.

---

### 2. Issues, Templates, and Project Board

* Add **issue templates** (`bug_report.md`, `feature_request.md`) for consistency.
* Add a **pull request template** with a checklist: tests, docs, screenshots, linked issues.
* Create a **GitHub Projects board** with columns: Backlog, Ready, In Progress, In Review, Done.
* Use labels for filtering: `feature`, `bug`, `api`, `ui`, `infra`, `docs`, `chore`, plus priorities (`P1`, `P2`, `P3`).
* Break down milestones into small, trackable issues linked to the README milestones.

---

### 3. Branching and Commits

* Use short-lived feature branches (e.g., `feat/impact-feed`, `fix/espn-parse`, `chore/ci`).
* Follow **Conventional Commits**:

  * `feat: add impact feed drawer`
  * `fix(server): retry espn calls`
  * `chore(ci): cache pip and npm`
* Keep pull requests small and focused.

---

### 4. CI/CD with GitHub Actions

* Start with GitHub-hosted CI/CD for learning purposes.
* Add a `.github/workflows/ci.yml` file with jobs:

  * **Client**: install, lint, type-check, test, build.
  * **Server**: install, lint, type-check, test.
  * Optional: build docker images for smoke testing.
* Cache Node.js and pip dependencies.
* Upload test reports and coverage.
* Mark CI checks as required on `main`.

> **Future Direction**: Once the home server cluster is ready, migrate these CI/CD jobs to a self-hosted runner. This keeps the workflow identical but runs entirely on your own infrastructure.

---

### 5. Configuration and Secrets

* All secrets live in a local `.env` file (never committed).
* Example: `ESPN_S2`, `ESPN_SWID`, `MSF_API_KEY`.
* Add a `.env.example` to document required variables.
* Application reads config from `data/config.yaml` and `.env`.
* GitHub Actions can inject secrets into jobs via the repository’s **Secrets and Variables** settings.

---

### 6. Project Rhythm

* Each milestone = a GitHub milestone.
* Each task = a GitHub issue.
* Issues → branches → pull requests → review → merge.
* Projects board shows real-time status of progress.

---

This workflow ensures:

* Every change is tracked and reviewed.
* GitHub CI/CD gives immediate feedback.
* Copilot helps generate and explain code line by line.
* Everything still runs **locally** (WSL + Docker Compose), with an option to move CI/CD to your home server later.
