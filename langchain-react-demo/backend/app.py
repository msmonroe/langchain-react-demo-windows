from pathlib import Path
from dotenv import load_dotenv
load_dotenv(dotenv_path=Path(__file__).with_name(".env"))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_pipeline import ask_question

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Ask a Medical Rep")

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

@app.post("/ask")
async def ask(payload: AskPayload):
    q = (payload.question or "").strip()
    if not q:
        raise HTTPException(status_code=400, detail="`question` is required")
    answer = ask_question(q)
    return {"answer": answer}
