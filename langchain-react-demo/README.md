# Ask a Medical Rep – COMPLETE (Windows friendly)

End‑to‑end demo: React (Vite) frontend + FastAPI backend + LangChain (OpenAI) using **Chroma** (no FAISS needed).

## Quick Start

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
