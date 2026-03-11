"""
Pydantic models used for request validation and API response shaping.
All models here are shared across routers and services.
"""
from pydantic import BaseModel, EmailStr, field_validator


# ── Request models ─────────────────────────────────────────────────────────────

class UploadRequest(BaseModel):
    """
    Represents the form-data fields that accompany the uploaded file.
    The file itself is handled by FastAPI's UploadFile, not a Pydantic model.
    """
    email: EmailStr


# ── Response models ────────────────────────────────────────────────────────────

class UploadResponse(BaseModel):
    """Returned by POST /api/upload on success."""
    status: str = "success"
    message: str
    rows_analyzed: int
    recipient: EmailStr


class ErrorResponse(BaseModel):
    """Returned on any handled error."""
    status: str = "error"
    detail: str


# ── Internal data-transfer models ─────────────────────────────────────────────

class ParsedSalesData(BaseModel):
    """Lightweight container passed between the parser, AI service, and email service."""
    row_count: int
    column_names: list[str]
    preview_text: str           # plain-text table used in the AI prompt
    summary: str = ""           # filled in by ai_service before email is sent

    model_config = {"arbitrary_types_allowed": True}

    @field_validator("row_count")
    @classmethod
    def must_have_rows(cls, v: int) -> int:
        if v == 0:
            raise ValueError("The uploaded file contains no data rows.")
        return v
