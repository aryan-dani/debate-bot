# Submission notes — Spar with a Friend

Paste / adapt this for the hackathon form.

## Who the friend is

- **First name:** `TODO_FRIEND_NAME`
- **Relation:** `TODO_RELATION` (roommate / classmate / debate-club mate / placement prep friend)

## What problem we solved

They freeze in group discussions and need patient GD/viva practice — a place to rehearse Opening → Rebuttal → Closing, get kind specific feedback, and finish a ~10-minute round without judgment from a public cloud chatbot.

## Why open / local beat a closed chatbot here

- **Privacy:** with `LLM_PROVIDER=ollama`, practice speech never leaves the laptop.
- **No paid API:** demo runs after `ollama pull llama3.2:3b` — no Groq/OpenAI key.
- **Open agent harness:** LangGraph stages are editable in `backend/graph.py` and coaching tone/difficulty in `backend/coaching.py`.
- **Open-weight model:** Meta LLaMA 3.2 via Ollama is what actually generates counters and reports.

## How to run offline

1. Install [Ollama](https://ollama.com) and run `ollama pull llama3.2:3b`
2. Copy `.env.example` → `.env` (defaults already use Ollama)
3. `cd backend && pip install -r requirements.txt && python -m uvicorn main:app --reload --port 8000`
4. `cd frontend && npm install && npm run dev`
5. Open Practice → pick a campus preset → Live Arena → Finish round

No internet required after the model is pulled. No `GROQ_API_KEY` required.

## What they said after trying it

> TODO: quote their reaction after the handoff demo.
