"""
/api/upload — receives the CSV/XLSX file + recipient email,
orchestrates parsing → AI analysis → email delivery.
"""
import io
from fastapi import APIRouter, File, Form, UploadFile, HTTPException
from pydantic import EmailStr

from app.utils.file_parser import parse_sales_file
from app.services.ai_service import generate_summary
from app.services.email_service import send_summary_email
from app.models.schemas import UploadResponse

router = APIRouter()


@router.post(
    "/upload",
    response_model=UploadResponse,
    summary="Upload sales file and trigger AI summary email",
)
async def upload_sales_file(
    file: UploadFile = File(..., description="CSV or XLSX sales data file"),
    email: EmailStr = Form(..., description="Recipient email address"),
):
    # ── 1. Validate file type ────────────────────────────────────────────────
    allowed = {"text/csv", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"}
    if file.content_type not in allowed:
        raise HTTPException(status_code=400, detail="Only CSV or XLSX files are accepted.")

    contents = await file.read()

    # ── 2. Parse into a DataFrame ────────────────────────────────────────────
    try:
        df = parse_sales_file(io.BytesIO(contents), file.filename)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Could not parse file: {exc}")

    if df.empty:
        raise HTTPException(status_code=422, detail="The uploaded file contains no data rows.")

    # ── 3. Generate AI summary ───────────────────────────────────────────────
    try:
        summary = await generate_summary(df)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"AI service error: {exc}")

    # ── 4. Send email ────────────────────────────────────────────────────────
    try:
        await send_summary_email(recipient=email, summary=summary)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Email service error: {exc}")

    return UploadResponse(
        message="Summary generated and sent successfully!",
        recipient=email,
        rows_analyzed=len(df),
    )
