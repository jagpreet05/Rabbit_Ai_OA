"""
main.py
───────
FastAPI application factory.

What lives here:
  - App metadata (used by Swagger/OpenAPI)
  - CORS middleware
  - Router registration
  - The health-check endpoint

What does NOT live here:
  - Business logic (→ services/)
  - Route handlers (→ routers/)
  - Data models (→ models/)
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import upload

# ── App instance ───────────────────────────────────────────────────────────────
app = FastAPI(
    title="Sales Insight Automator",
    description=(
        "Upload a CSV or XLSX sales file and an email address. "
        "The API parses the data, generates a professional executive summary "
        "using Google Gemini, and emails it to you — all in one request.\n\n"
        "**Try it out:** use the `/api/upload` endpoint below."
    ),
    version="1.0.0",
    docs_url="/docs",         # Swagger UI
    redoc_url="/redoc",       # ReDoc alternative
    openapi_url="/openapi.json",
)

# ── CORS ───────────────────────────────────────────────────────────────────────
# Allows the Vite dev server (port 5173) and a production domain to call the API.
# Update the list with your production frontend URL before deploying.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",   # Vite dev server
        "http://localhost:3000",   # CRA dev server (if used)
        "http://localhost:80",     # nginx in Docker
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ────────────────────────────────────────────────────────────────────
app.include_router(upload.router, prefix="/api", tags=["Sales Upload"])


# ── Health check ───────────────────────────────────────────────────────────────
@app.get(
    "/",
    tags=["Health"],
    summary="Health check",
    response_description="Service status",
)
async def health_check() -> dict:
    """
    Simple liveness probe endpoint.
    Returns `200 OK` when the service is running.
    Used by docker-compose and the GitHub Actions smoke test.
    """
    return {"status": "ok", "message": "Sales Insight Automator is running"}
