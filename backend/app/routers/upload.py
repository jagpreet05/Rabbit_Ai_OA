"""
routers/upload.py
─────────────────
Defines the POST /api/upload endpoint.

Responsibilities of THIS file (router layer):
  - Accept and validate the HTTP request (file + email).
  - Delegate all business logic to services.
  - Shape the HTTP response.

The router intentionally contains NO business logic.
"""
import io

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from pydantic import EmailStr

from app.models.schemas import UploadResponse
from app.services.ai_service import generate_summary
from app.services.email_service import send_summary_email
from app.utils.file_parser import parse_sales_file

router = APIRouter()

# Permitted MIME types for uploaded sales files
_ALLOWED_CONTENT_TYPES = {
    "text/csv",
    "application/vnd.ms-excel",                                          # .xls
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", # .xlsx
}

# Permitted file extensions (belt-and-suspenders check alongside MIME type)
_ALLOWED_EXTENSIONS = {".csv", ".xls", ".xlsx"}


@router.post(
    "/upload",
    response_model=UploadResponse,
    status_code=status.HTTP_200_OK,
    summary="Upload a sales file and receive an AI summary by email",
    response_description="Confirmation that the email was sent successfully",
    responses={
        400: {"description": "Invalid file type"},
        422: {"description": "File is empty or cannot be parsed"},
        500: {"description": "AI or email service failure"},
    },
)
async def upload_sales_file(
    file: UploadFile = File(
        ...,
        description="Sales data file (.csv or .xlsx, max ~10 MB)",
    ),
    email: EmailStr = Form(
        ...,
        description="Email address where the summary will be delivered",
    ),
) -> UploadResponse:
    """
    **Upload flow:**

    1. Validates file type (MIME + extension).
    2. Parses the CSV/XLSX into structured sales data.
    3. Sends data to Gemini to generate a professional executive summary.
    4. Emails the summary to the provided address.
    5. Returns a success JSON response.
    """

    # ── Step 1: Validate file type ───────────────────────────────────────────
    _validate_file_type(file)

    # ── Step 2: Read file bytes ──────────────────────────────────────────────
    try:
        raw_bytes = await file.read()
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to read uploaded file: {exc}",
        )

    # ── Step 3: Parse into structured data ──────────────────────────────────
    try:
        sales_data = parse_sales_file(io.BytesIO(raw_bytes), file.filename or "")
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Could not parse the file. Make sure it is valid. ({exc})",
        )

    # ── Step 4: Generate AI summary ──────────────────────────────────────────
    try:
        summary = await generate_summary(sales_data)
    except EnvironmentError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"AI service error: {exc}",
        )

    # ── Step 5: Send email ───────────────────────────────────────────────────
    try:
        await send_summary_email(
            recipient=str(email),
            summary=summary,
            rows_analyzed=sales_data.row_count,
        )
    except EnvironmentError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Email delivery failed: {exc}",
        )

    # ── Step 6: Return success ───────────────────────────────────────────────
    return UploadResponse(
        status="success",
        message="Summary generated and email sent",
        rows_analyzed=sales_data.row_count,
        recipient=email,
    )


# ── Validation helpers ─────────────────────────────────────────────────────────

def _validate_file_type(file: UploadFile) -> None:
    """
    Raise HTTP 400 if the file is not an accepted CSV or Excel file.
    We check both MIME type and file extension for robustness,
    because browsers sometimes send incorrect content-type headers.
    """
    content_type = (file.content_type or "").lower()
    filename = file.filename or ""
    extension = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    mime_ok = content_type in _ALLOWED_CONTENT_TYPES
    ext_ok = extension in _ALLOWED_EXTENSIONS

    if not mime_ok and not ext_ok:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Invalid file type '{filename}'. "
                "Only .csv and .xlsx files are accepted."
            ),
        )
