"""
Sales Insight Automator — FastAPI Entry Point
Swagger UI available at http://localhost:8000/docs
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import upload

app = FastAPI(
    title="Sales Insight Automator",
    description="Upload a CSV/XLSX sales file and receive an AI-generated summary via email.",
    version="1.0.0",
)

# Allow the React dev server to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router, prefix="/api", tags=["Upload"])


@app.get("/", tags=["Health"])
async def health_check():
    return {"status": "ok", "message": "Sales Insight Automator is running"}
