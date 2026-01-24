# 🔌 API Reference

The DebateBot backend exposes a RESTful API built with FastAPI. All endpoints return JSON.

**Base URL**: `http://127.0.0.1:8000` (Local)

## 1. Debate Generation
generate a full debate flow (Opening -> Rebuttal -> Closing) for a given topic.

- **Endpoint**: `POST /api/debate`
- **Request Body**:
  ```json
  {
    "topic": "Social media does more harm than good"
  }
  ```
- **Response**:
  ```json
  {
    "topic": "Social media does more harm than good",
    "proposition": {
      "opening": { "summary": "...", "full": "..." },
      "rebuttal": { "summary": "...", "full": "..." },
      "closing": { "summary": "...", "full": "..." }
    },
    "opposition": { ... }
  }
  ```

## 2. Live Debate Counter
Generate a counter-argument for a specific round in the user-vs-AI mode.

- **Endpoint**: `POST /api/live-counter`
- **Request Body**:
  ```json
  {
    "topic": "string",
    "user_argument": "string",
    "round": "opening" | "rebuttal" | "closing",
    "argument_history": [
      { "type": "user", "text": "..." },
      { "type": "ai", "text": "..." }
    ]
  }
  ```
- **Response**:
  ```json
  {
    "counter_argument": "Full text string...",
    "points": [
      { "id": 1, "text": "First counter point..." },
      { "id": 2, "text": "Second counter point..." }
    ]
  }
  ```

## 3. Score Argument
Analyze an argument and provide detailed scoring metrics.

- **Endpoint**: `POST /api/score-argument`
- **Request Body**:
  ```json
  {
    "argument": "The user's argument text...",
    "topic": "The debate topic..."
  }
  ```
- **Response**:
  ```json
  {
    "coherence": 0.85,
    "relevance": 0.9,
    "evidenceStrength": 0.7,
    "fallacyPenalty": 0.0,
    "argumentStrength": 0.82,
    "details": {
       "fallaciesDetected": []
    }
  }
  ```

## 4. Get Feedback
Get actionable advice on how to improve an argument.

- **Endpoint**: `POST /api/get-feedback`
- **Request Body**:
  ```json
  {
    "argument": "...",
    "topic": "...",
    "scores": { ... }, 
    "target_score": 90
  }
  ```
- **Response**:
  ```json
  {
    "type": "improvement",
    "message": "You are 8 points away from your target.",
    "tips": [
      {
        "metric": "Evidence",
        "tip": "Try adding a statistic to back up your second claim."
      }
    ]
  }
  ```

## 5. Health Check
- **Endpoint**: `GET /api/health`
- **Response**: `{"status": "healthy"}`
