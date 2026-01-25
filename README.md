# DebateBot

![License](https://img.shields.io/badge/license-MIT-blue)
![Python](https://img.shields.io/badge/python-3.12-blue)
![React](https://img.shields.io/badge/react-18-blue)
![Build Status](https://img.shields.io/badge/build-passing-brightgreen)

DebateBot is an intelligent debating platform powered by **LLaMA 3.3 70B** and **LangGraph**. It goes beyond simple chat interfaces by orchestrating complex, multi-stage debates between AI agents and conducting live debates where users can challenge the AI directly.

---

## Key Features

- **Dual-AI Debates**: Observes comprehensive debates unfold through formal stages (Opening, Rebuttal, Closing).
- **Live Arena**: Allows users to debate against the AI with real-time responses.
- **Smart Scoring**: Provides detailed feedback on coherence, evidence usage, and logical fallacies.
- **Real-Time Streaming**: Delivers fluid argument generation with low latency.

[Read Detailed Features](docs/features.md)

---

## Documentation

Comprehensive documentation is available to assist with building and deploying DebateBot.

| Topic                                | Description                                          |
| ------------------------------------ | ---------------------------------------------------- |
| [Architecture](docs/architecture.md) | System diagrams, data flow, and component breakdown. |
| [Tech Stack](docs/tech_stack.md)     | Details on Python, FastAPI, React, and Groq.         |
| [API Reference](docs/api.md)         | Endpoints for debates, scoring, and feedback.        |
| [Deployment](docs/deployment.md)     | Guides for deploying to Render and Vercel.           |

---

## Quick Start

### Prerequisites

- Python 3.12+
- Node.js 18+
- [Groq API Key](https://console.groq.com)

### 1. Backend Setup

```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate | Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env # Add your GROQ_API_KEY
python -m uvicorn main:app --reload
```

### 2. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:5173` to start debating.

---

## Contributing

We welcome contributions. Please check the [Issues](https://github.com/Krish1342/DebateBot/issues) page for current tasks or to report bugs.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
