# API Reference

Spar with a Friend / DebateBot backend (FastAPI). All endpoints return JSON.

**Base URL**: `http://127.0.0.1:8000`

When the LLM provider is not ready, generation endpoints return **503** with:
```json
{ "detail": { "error": "...", "checklist": ["..."], "provider": "ollama", "model": "llama3.2:3b", "local": true } }
```

## 0. Status & presets

- `GET /api/status` — `{ provider, model, local, ready, checklist, detail, host }`
- `GET /api/presets` — friend profile TODOs, campus topics, tones, difficulties, practice card
- `GET /api/health` — `{ status: "healthy" }`
- `GET /api/history` — recent local SQLite sessions
- `GET /api/history/{id}` — one session with transcript + report

## 1. Debate Generation

Full dual-AI debate via LangGraph (`opening_prop` → … → `closing_opp`).

- **Endpoint**: `POST /api/debate`
- **Request Body**:
  ```json
  {
    "topic": "Social media does more harm than good",
    "friend_mode": true,
    "tone": "patient",
    "difficulty": "beginner"
  }
  ```
- **Response**: proposition/opposition opening/rebuttal/closing plus `practice_card`.

## 2. Live Debate Counter

- **Endpoint**: `POST /api/live-counter`
- **Request Body**:
  ```json
  {
    "topic": "string",
    "user_argument": "string",
    "round": "opening",
    "argument_history": [{ "type": "user", "text": "..." }],
    "friend_mode": true,
    "tone": "patient",
    "difficulty": "beginner"
  }
  ```
- **Response**: `{ "counter_argument": "...", "points": [...] }`

## 3. End-of-round report

- **Endpoint**: `POST /api/round-report`
- **Request Body**: `{ topic, user_turns, argument_history, tone, difficulty, friend_mode }`
- **Response**: `{ report: { headline, did_well, try_next, filler_note }, session_id }`

## 4. Score Argument

- **Endpoint**: `POST /api/score-argument`
- **Request Body**: `{ "argument": "...", "topic": "...", "friend_mode": true }`

## 5. Feedback

- **Endpoint**: `POST /api/get-feedback`
- **Request Body**: `{ argument, topic, scores, target_score, friend_mode }`
