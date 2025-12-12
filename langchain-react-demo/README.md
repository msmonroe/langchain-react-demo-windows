# Ask a Medical Rep – COMPLETE (Windows friendly)

End‑to‑end demo: React (Vite) frontend + FastAPI backend + LangChain (OpenAI) using **Chroma** (no FAISS needed).

## Detailed Description
The project simulates a lightweight “Ask a Medical Rep” assistant that ingests the structured JSON data in `backend/drug_data.json`, embeds it with `OpenAIEmbeddings`, and serves grounded answers through a Vite-based React chat UI. Each drug entry tracks indications plus an explicit list of side effects, and the backend prompt enforces that responses always surface those effects alongside any recommended drug. A FastAPI service orchestrates question validation, retrieval, and LLM invocation while exposing `/metrics` for operational insight. Everything is wired for Windows-first workflows (PowerShell scripts, `.venv` paths) so demos can be spun up quickly on laptops without Docker.

### Architecture Highlights
- **Backend** – `backend/app.py` loads environment variables via `python-dotenv`, handles POST `/ask`, wraps `langchain_pipeline.ask_question`, and records latency counters with the custom `Metrics` helper.
- **Retrieval + LLM** – `backend/langchain_pipeline.py` rebuilds an in-memory Chroma store on each question, performs similarity search, then feeds a constrained prompt into the temperature-0 OpenAI LLM for deterministic responses.
- **Frontend** – `frontend/src/components/ChatBox.jsx` manages the chat UX, POSTing JSON to `/ask` (respecting `VITE_API_BASE`) and rendering answers/errors inline.
- **Dev Ergonomics** – `scripts/dev.ps1` installs dependencies and launches both services, while `backend/tests/test_app.py` ensures the API and metrics stay healthy without touching OpenAI.

## Key Deliverables
- **Interactive demo** connecting React (Vite) and FastAPI with real-time question answering grounded in `drug_data.json`.
- **LangChain retrieval pipeline** leveraging OpenAI embeddings + in-memory Chroma for reproducible, dependency-light experimentation with mandatory side-effect callouts in responses.
- **Operational tooling** including in-memory metrics (`GET /metrics`) and structured logging for each `/ask` call.
- **Automated tests** (`pytest backend/tests -q`) that mock the LLM layer, assert validation paths, and verify instrumentation.
- **Developer tooling** via `scripts/dev.ps1` for one-command setup plus documentation that captures troubleshooting, instrumentation, and testing guidance.

## Quick Start

### 0) One command (Windows)
```powershell
cd langchain-react-demo-complete
pwsh -ExecutionPolicy Bypass -File .\scripts\dev.ps1
```
This script ensures backend (Python) and frontend (Node) dependencies are installed, then launches two new terminals running `uvicorn app:app --reload` and `npm run dev`. Override the API base with `-ApiBase "https://your-api.example.com"` or skip the dependency checks via `-SkipInstall` after the first run.

### 1) Backend
```powershell
cd langchain-react-demo-complete\backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r ..\requirements.txt
$env:OPENAI_API_KEY = "sk-..."
uvicorn app:app --reload
```
Open http://127.0.0.1:8000/docs and test POST /ask.

### 2) Frontend (new terminal)
```powershell
cd langchain-react-demo-complete\frontend
npm install
npm run dev
```
Open the printed localhost URL (e.g., http://127.0.0.1:5173). Type a question and click **Ask**.

If your backend is not on 127.0.0.1:8000 in dev:
```powershell
$env:VITE_API_BASE = "http://127.0.0.1:8000"
npm run dev
```

### 3) Build for S3
```powershell
npm run build
# Upload frontend/dist to your S3 static site bucket
```
For production builds pointing at an API gateway/base URL:
```powershell
$env:VITE_API_BASE = "https://your-api.example.com"
npm run build
```

## Structure
```
langchain-react-demo-complete/
├── backend/
│   ├── app.py
│   ├── drug_data.json
│   └── langchain_pipeline.py
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── src/
│       ├── main.jsx
│       ├── App.jsx
│       └── components/ChatBox.jsx
└── requirements.txt
```

## Troubleshooting
- **“file not found” in browser**: make sure you ran `npm run dev` and are visiting the Vite server URL (don’t open index.html directly).
- **404 for /ask**: backend must be running on 127.0.0.1:8000 OR set VITE_API_BASE to your backend URL before starting `npm run dev`.
- **CORS in prod**: add CORSMiddleware in `app.py` (FastAPI) or configure CORS on API Gateway.

## Instrumentation
- Every `/ask` call is timed and logged by the `ask_medical_rep` logger with the character count and duration for quick tracing in Uvicorn.
- Basic counters live in-memory (see `backend/metrics.py`); fetch `GET /metrics` to view `total_requests`, `total_failures`, rolling average latency, and success rate.
- Validation failures (e.g., empty question) and downstream LLM issues increment `total_failures`, so the metrics endpoint is a quick health signal without opening tracing tools.

## Testing
1. Create/activate the backend virtual environment and install deps: `pip install -r requirements.txt` (this now includes `pytest`).
2. Run `pytest backend/tests -q` to execute the FastAPI endpoint tests.
3. Tests monkeypatch `ask_question`, so no OpenAI traffic occurs and no API key is required; they also verify the metrics endpoint and error handling.
