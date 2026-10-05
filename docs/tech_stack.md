# Technology Stack

## Backend

| Component | Technology | Description |
|-----------|------------|-------------|
| **Language** | [Python 3.12](https://www.python.org/) | Modern, high-performance scripting. |
| **Framework** | [FastAPI](https://fastapi.tiangolo.com/) | High-performance web framework for APIs. |
| **Orchestration** | [LangGraph](https://langchain-ai.github.io/langgraph/) | Open agent harness for debate stages. |
| **Primary LLM** | [Ollama](https://ollama.com) + LLaMA 3.2 3B | Local open-weight inference (default). |
| **Optional LLM** | [Groq](https://groq.com/) LLaMA 3.3 | Cloud fallback only when `LLM_PROVIDER=groq`. |
| **History** | SQLite | Offline practice session storage. |
| **Validation** | [Pydantic](https://docs.pydantic.dev/) | Request/response models. |

## Frontend

| Component | Technology | Description |
|-----------|------------|-------------|
| **Library** | [React 18](https://react.dev/) | UI library. |
| **Build Tool** | [Vite](https://vitejs.dev/) | Dev server and bundler. |
| **Routing** | [React Router 6](https://reactrouter.com/) | Client routing. |
| **Styling** | CSS3 | Custom variables and animations. |
| **Icons** | [Lucide React](https://lucide.dev/) | Icon toolkit. |

## Development & Ops

- **Environment Config**: `python-dotenv` — Ollama first in `.env.example`.
- **Local demo**: `uvicorn` + `npm run dev` (no Vercel/Render required).
- **Linting**: Ruff / ESLint as configured.
