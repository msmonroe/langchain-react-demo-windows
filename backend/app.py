import logging
import time
from pathlib import Path

from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from langchain_pipeline import ask_question
from metrics import Metrics

load_dotenv(dotenv_path=Path(__file__).with_name(".env"))

logger = logging.getLogger("ask_medical_rep")
if not logger.handlers:
    logging.basicConfig(level=logging.INFO)

metrics = Metrics()

app = FastAPI(title="Ask a Medical Rep")

app.state.metrics = metrics

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://your-site.example.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AskPayload(BaseModel):
    question: str

@app.get("/")
def health():
    return {
        "status": "ok",
        "hint": 'Use POST /ask with JSON {"question": "..."}'
    }

@app.get("/metrics")
def get_metrics():
    return metrics.snapshot()

@app.post("/ask")
async def ask(payload: AskPayload):
    q = (payload.question or "").strip()
    if not q:
        metrics.record(duration_ms=None, success=False)
        raise HTTPException(status_code=400, detail="`question` is required")
    start = time.perf_counter()
    try:
        answer = ask_question(q)
    except HTTPException:
        metrics.record(duration_ms=None, success=False)
        logger.exception("ask_question_http_exception", extra={"question_preview": q[:80]})
        raise
    except Exception as exc:  # pragma: no cover - defensive but tested via unit tests
        metrics.record(duration_ms=None, success=False)
        logger.exception("ask_question_failure", extra={"question_preview": q[:80]})
        raise HTTPException(status_code=500, detail="Unable to generate an answer") from exc
    duration_ms = (time.perf_counter() - start) * 1000
    metrics.record(duration_ms=duration_ms, success=True)
    logger.info(
        "ask_question_success",
        extra={
            "question_chars": len(q),
            "duration_ms": round(duration_ms, 2),
        },
    )
    return {"answer": answer, "latency_ms": round(duration_ms, 2)}
