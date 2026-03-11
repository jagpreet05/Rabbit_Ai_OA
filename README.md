# Sales Insight Automator

Upload a CSV/XLSX sales file → get an AI-powered summary emailed to you instantly.

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React + Vite |
| Backend | FastAPI (Python) |
| AI | Google Gemini or Groq (switchable) |
| Email | SMTP via aiosmtplib |
| Container | Docker + docker-compose |
| CI | GitHub Actions |

## Quick Start

### 1. Set up environment variables
```bash
cp .env.example .env
# Edit .env and fill in your API keys and SMTP credentials
```

### 2. Run with Docker (recommended)
```bash
docker compose up --build
```
- Frontend → http://localhost:5173  
- Backend API → http://localhost:8000  
- Swagger docs → http://localhost:8000/docs

### 3. Run locally (without Docker)

**Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## Project Structure

```
The-Sales-Insight-Automator/
├── .env.example                 # Environment variable template
├── .gitignore
├── docker-compose.yml           # Runs frontend + backend together
├── .github/
│   └── workflows/
│       └── ci.yml               # GitHub Actions CI pipeline
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py              # FastAPI app entry point
│       ├── routers/
│       │   └── upload.py        # POST /api/upload endpoint
│       ├── services/
│       │   ├── ai_service.py    # Gemini / Groq integration
│       │   └── email_service.py # SMTP email sending
│       ├── utils/
│       │   └── file_parser.py   # CSV / XLSX → DataFrame
│       └── models/
│           └── schemas.py       # Pydantic response models
└── frontend/
    ├── Dockerfile               # Multi-stage build + nginx
    ├── package.json
    ├── vite.config.js
    ├── index.html
    └── src/
        ├── main.jsx
        ├── App.jsx
        ├── index.css
        ├── api/
        │   └── client.js        # Axios wrapper for the API
        └── components/
            ├── UploadForm.jsx   # File + email form
            └── StatusMessage.jsx # Loading / success / error UI
```

## Environment Variables

| Variable | Description |
|---|---|
| `GEMINI_API_KEY` | Google Gemini API key |
| `GROQ_API_KEY` | Groq API key (alternative) |
| `AI_PROVIDER` | `gemini` or `groq` |
| `SMTP_HOST` | SMTP server hostname |
| `SMTP_PORT` | SMTP port (default 587) |
| `SMTP_USER` | SMTP username / email |
| `SMTP_PASSWORD` | SMTP password / app password |
| `EMAIL_FROM` | From address in sent emails |
| `VITE_API_BASE_URL` | Frontend → Backend URL |

## API Docs

Open http://localhost:8000/docs for the interactive Swagger UI after starting the backend.
