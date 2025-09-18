# Fantasy Hub - AI Coding Agent Instructions

Fantasy Hub is a personal fantasy football dashboard combining ESPN/Sleeper leagues and Pick'em data with a live Impact Feed. Uses Vue 3 + Vite frontend, FastAPI backend, and file-based persistence.

## Architecture Principles

**Service Layer Pattern:** Transform external API payloads → internal models → trimmed UI data
- Services handle upstream API integration with caching and error handling
- Clear separation between external data formats and internal representation
- UI receives only the data it needs, reducing payload size

**State Management:** Domain-specific stores for different data types
- Separate stores for league matchups, impact feed, and pick'em data
- Reactive state updates for real-time game data

## Development Philosophy

**Incremental Protocol:** Write minimal version → run locally → explain every line → commit → repeat
- Each file starts with the smallest possible working version
- Every line of code should be understood and explained
- Commit frequently with descriptive messages

**Educational Approach:** 
- Prioritize code clarity and understanding over brevity
- Document architectural decisions and trade-offs
- Use Copilot as a teaching tool, not just code generation

## Configuration Strategy

**Graceful Degradation:** Application should boot without secrets for public endpoints
- Separate configuration for league IDs, team mappings, and API credentials  
- Public endpoints (scoreboard, play-by-play) work without authentication
- Private endpoints (fantasy league data) require API keys

**File-based Config:** YAML for structured data, environment variables for secrets

## API Design Patterns

**Server-side Proxy:** Backend handles all external API calls
- Avoids CORS issues in browser
- Centralizes rate limiting and caching logic
- Allows payload transformation before reaching UI

**Smart Caching:** Endpoint-specific TTLs based on data freshness needs
- Live game data: short TTL (15-30 seconds)
- Historical data: longer TTL (5+ minutes)
- File-based cache fallback for resilience

**Dynamic Polling:** Adjust update frequency based on game state
- Normal periods: 30-60 second intervals
- Live games: 15-20 second intervals for real-time updates

## Project-Specific Conventions

- Prefer public APIs over authenticated endpoints when possible
- File-based persistence before adding database complexity
- Design for fair use and rate limiting from the start
- Accessibility: color-safe design, keyboard navigation, visible loading states
- Impact feed enrichment: correlate plays with fantasy ownership and pick'em selections