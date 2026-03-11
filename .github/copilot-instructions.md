# Copilot Instructions

## Big Picture
- React (Vite) frontend in `frontend/` calls a FastAPI service in `backend/app.py` via POST `/ask`.
- The backend wraps LangChain (`backend/langchain_pipeline.py`) to embed rows from `backend/drug_data.json` per request using `OpenAIEmbeddings` + in-memory Chroma before executing a `RetrievalQA` chain with `OpenAI`.
- There is no persistent database; every question rebuilds the vector store, so any heavy preprocessing must stay fast or be cached in memory/files.

## Critical Workflows
- Windows helper script: `pwsh -File scripts/dev.ps1 [-ApiBase ... [-SkipInstall]]` installs deps then launches backend (`uvicorn app:app --reload`) and frontend (`npm run dev`) in separate terminals.
- Manual backend loop: `cd backend && python -m venv .venv && .venv\Scripts\Activate.ps1 && pip install -r ..\requirements.txt && uvicorn app:app --reload`.
- Manual frontend loop: `cd frontend && npm install && npm run dev`; proxy to the backend via Vite (`server.proxy`), or set `VITE_API_BASE` to a remote API before `npm run dev/build`.
- Always export `OPENAI_API_KEY` in the backend shell before running pipelines; LangChain pulls it from the environment via `python-dotenv` (see `.env` lookup in `app.py`).

## Backend Patterns
- `AskPayload` validates input; blank questions raise `HTTP 400` and are counted as failures in metrics. Preserve this guard when changing request schemas.
- `ask_question()` already returns a plain string; keep additional metadata (e.g., latency) at the FastAPI layer so the front-end contract stays minimal (`{"answer": "..."}`).
- Drug rows in `drug_data.json` now include `indication` + `side_effects`; ensure any new data keeps that schema and that answers continue to mention side effects with each drug (prompt already enforces this).
- Instrumentation lives in `backend/metrics.py`; use `metrics.record()` for any new endpoints so `/metrics` stays accurate. Logs are emitted through the `ask_medical_rep` logger with `{question_chars, duration_ms}` extras.
- If you need async LangChain calls, convert `ask_question` carefully; the FastAPI route currently runs sync code inside an async function.

## Frontend Patterns
- `frontend/src/components/ChatBox.jsx` owns all state (question, answer, loading, errors) and posts `{question}` JSON to `/ask`. Handle new response fields as optional to avoid breaking this component.
- Styling is inline and minimalistic; keep additions simple unless you rework the design holistically.
- Respect `import.meta.env.VITE_API_BASE` any time you introduce new fetches so builds can target alternate backends without code changes.

## Testing & Quality
- Run `pytest backend/tests -q`. Tests monkeypatch `backend.app.ask_question`, so they execute without OpenAI access and assert that metrics and error paths behave correctly.
- When adding tests, reuse the helper pattern in `backend/tests/test_app.py` (`TestClient` + metrics reset fixture). Always reset metrics to avoid cross-test pollution.

## Instrumentation & Ops
- `GET /metrics` returns `{total_requests, total_failures, avg_latency_ms, success_rate}`; keep the shape backward-compatible if you extend it.
- Latency is measured with `time.perf_counter()`; if you introduce background tasks, ensure you still record meaningful timings or add new metrics fields.
- Errors from LangChain are wrapped into `HTTP 500` with a generic message; use logging (not responses) for detailed diagnostics to avoid leaking sensitive info.
