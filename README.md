# DebateBot → Spar with a Friend

![License](https://img.shields.io/badge/license-MIT-blue)
![Python](https://img.shields.io/badge/python-3.12-blue)
![React](https://img.shields.io/badge/react-18-blue)
![Local](https://img.shields.io/badge/LLM-Ollama%20local-cyan)

**DebateBot** is the base project. The hackathon product is **Spar with a Friend**: a local, open-weight practice partner so a friend can rehearse debates and GDs without sending speech to a cloud chat app.

Open-source AI at the core:

- **Open-weight model** via [Ollama](https://ollama.com) (default `llama3.2:3b`)
- **Open agent harness** via [LangGraph](https://langchain-ai.github.io/langgraph/) (Opening → Rebuttal → Closing + Live Arena)
- Optional Groq cloud fallback only — **never required** to run the demo

---

## Friend story (fill before handoff)

| Field | Value |
|-------|--------|
| Name | Sobaan |
| Relation | debate classmate |
| Problem | Freezes in group discussions; needs patient GD/viva practice |
| Constraints | Weak laptop, no paid APIs, no cloud transcripts |
| Success | Finish a 10-min practice round and get kind, specific feedback |

Friend profile lives in [`backend/coaching.py`](backend/coaching.py).

---

## Key Features

- **Friend Practice setup**: one screen for provider status, tone, difficulty, campus presets, practice card
- **Live Arena**: user vs local AI through Opening / Rebuttal / Closing
- **Dual-AI Debates**: watch Proposition vs Opposition (still LangGraph-driven)
- **End-of-round report**: short, kind feedback saved to local SQLite
- **Local mode badge**: UI shows `Local · Ollama` when running offline-capable inference

---

## Quick Start (Windows + Linux/macOS)

### Prerequisites

- Python 3.12+
- Node.js 18+
- [Ollama](https://ollama.com) installed and running
- **No** `GROQ_API_KEY` needed for the default path

### 0. Pull the local model

```bash
ollama pull llama3.2:3b
```

(~2GB download; fits an 8GB laptop. For tighter RAM: `ollama pull llama3.2:1b`)

### 1. Backend

```bash
# from repo root
cp .env.example .env
# Windows PowerShell: Copy-Item .env.example .env

cd backend
python -m venv venv

# Windows:
venv\Scripts\activate
# macOS / Linux:
# source venv/bin/activate

pip install -r requirements.txt
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Confirm: open `http://127.0.0.1:8000/api/status` — `"provider":"ollama"`, `"ready":true`.

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:5173` → **Start friend practice**.

### Offline after models are pulled

Once Ollama and `llama3.2:3b` are local, disconnect from the internet and run a full Live Arena round. With `LLM_PROVIDER=ollama`, transcripts stay on this machine.

---

## Optional Groq fallback

Only if you explicitly want cloud speed:

```env
LLM_PROVIDER=groq
GROQ_API_KEY=...
LLM_MODEL=llama-3.3-70b-versatile
```

The app will **not** silently call Groq when Ollama is down.

---

## Smoke test

```bash
# with backend running on :8000
python scripts/smoke_local.py
```

Manual checklist:

1. `ollama pull llama3.2:3b`
2. Start backend + frontend (no `GROQ_API_KEY`)
3. Complete Opening → Rebuttal → Closing in Live Arena **or** one dual-AI debate
4. See end-of-round report / scoring feedback
5. Confirm navbar shows **Local · Ollama**

---

## Documentation

| Topic | Description |
|-------|-------------|
| [Architecture](docs/architecture.md) | LangGraph + Ollama data flow |
| [Tech Stack](docs/tech_stack.md) | Python, FastAPI, React, Ollama |
| [API Reference](docs/api.md) | Endpoints |
| [SUBMISSION.md](SUBMISSION.md) | Hackathon paste-ready writeup |

---

## Screenshots

_Add screenshots of Practice setup, Live Arena, and end-of-round report here._

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) and [Issues](https://github.com/Krish1342/DebateBot/issues).

## License

MIT — see LICENSE.
