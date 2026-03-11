"""
Pydantic models / schemas shared across the application.
"""
from pydantic import BaseModel, EmailStr


class UploadResponse(BaseModel):
    message: str
    recipient: EmailStr
    rows_analyzed: int
