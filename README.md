# 🎤 DebateBot

**The Intelligent AI Debate Platform**

DebateBot is a next-generation debating platform powered by **LLaMA 3.3 70B** and **LangGraph**. It goes beyond simple chat by orchestrating complex, multi-stage debates between AI agents or conducting live debates where users can challenge the AI directly.

---

## 🚀 Key Features

- **🤖 Dual-AI Debates**: Watch comprehensive debates unfold (Opening → Rebuttal → Closing).
- **⚔️ Live Arena**: Step into the ring and debate the AI yourself.
- **📊 Smart Scoring**: Get detailed feedback on coherence, evidence, and logical fallacies.
- **⚡ Real-Time Streaming**: Experience fluid, animated arguments as they are generated.

👉 [**Read Detailed Features**](docs/features.md)

---

## 📚 Documentation

We have comprehensive documentation to help you understand, build, and deploy DebateBot.

| Topic | Description |
|-------|-------------|
| [**Architecture**](docs/architecture.md) | System diagrams, data flow, and component breakdown. |
| [**Tech Stack**](docs/tech_stack.md) | Details on Python, FastAPI, React, and Groq. |
| [**API Reference**](docs/api.md) | Endpoints for debates, scoring, and feedback. |
| [**Deployment**](docs/deployment.md) | Guides for deploying to Render and Vercel. |

---

## ⚡ Quick Start

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

Visit `http://localhost:5173` to start debating!

---

## 🤝 Contributing

We welcome contributions! Please check the [Issues](https://github.com/Krish1342/DebateBot/issues) page.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---
**Built with ❤️ by the DebateBot Team**
