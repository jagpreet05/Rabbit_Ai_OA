"""
file_parser.py
──────────────
Responsible for reading the uploaded binary file (CSV or XLSX) into a
pandas DataFrame and producing a clean ParsedSalesData object.

All file-I/O and basic data-cleaning logic lives here.
The router and services remain unaware of file formats.
"""
import io
from typing import BinaryIO

import pandas as pd

from app.models.schemas import ParsedSalesData

# Maximum number of rows sent to the AI to keep prompt size reasonable
_PREVIEW_ROWS = 30


def parse_sales_file(file_bytes: BinaryIO, filename: str) -> ParsedSalesData:
    """
    Parse an uploaded CSV or XLSX file into a :class:`ParsedSalesData` object.

    Args:
        file_bytes: File content wrapped in a BytesIO (or any file-like object).
        filename:   Original filename, used only for extension detection.

    Returns:
        ParsedSalesData with row_count, column_names, and a plain-text preview.

    Raises:
        ValueError: if the file extension is unsupported.
        ValueError: if the file is empty after cleaning.
        Exception:  propagates pandas read errors so the caller can wrap them.
    """
    name = (filename or "").lower().strip()

    # ── 1. Detect format and read ────────────────────────────────────────────
    if name.endswith(".csv"):
        df = _read_csv(file_bytes)
    elif name.endswith(".xlsx") or name.endswith(".xls"):
        df = _read_excel(file_bytes)
    else:
        raise ValueError(
            f"Unsupported file type '{filename}'. "
            "Please upload a .csv or .xlsx file."
        )

    # ── 2. Clean ─────────────────────────────────────────────────────────────
    df = _clean(df)

    # ── 3. Validate ──────────────────────────────────────────────────────────
    if df.empty:
        raise ValueError(
            "The uploaded file has no data rows after removing empty lines."
        )

    # ── 4. Build preview text (for the AI prompt) ────────────────────────────
    preview_text = _build_preview(df)

    return ParsedSalesData(
        row_count=len(df),
        column_names=df.columns.tolist(),
        preview_text=preview_text,
    )


# ── Private helpers ────────────────────────────────────────────────────────────

def _read_csv(buf: BinaryIO) -> pd.DataFrame:
    """Try multiple common encodings so the parser is robust to real-world files."""
    for enc in ("utf-8", "utf-8-sig", "latin-1"):
        try:
            buf.seek(0)
            return pd.read_csv(buf, encoding=enc)
        except UnicodeDecodeError:
            continue
    raise ValueError("Could not decode CSV file. Try saving it as UTF-8.")


def _read_excel(buf: BinaryIO) -> pd.DataFrame:
    buf.seek(0)
    return pd.read_excel(buf, engine="openpyxl")


def _clean(df: pd.DataFrame) -> pd.DataFrame:
    """Drop fully empty rows and columns, strip whitespace from column names."""
    df = df.dropna(how="all").dropna(axis=1, how="all")
    df.columns = [str(c).strip() for c in df.columns]
    return df.reset_index(drop=True)


def _build_preview(df: pd.DataFrame) -> str:
    """
    Return a concise plain-text representation of the DataFrame.
    Includes column names, row count, and a statistical summary.
    """
    preview_rows = df.head(_PREVIEW_ROWS).to_string(index=False)

    # Numeric summary (only for numeric columns that exist)
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    stats_text = ""
    if numeric_cols:
        stats = df[numeric_cols].describe().round(2).to_string()
        stats_text = f"\n\nDescriptive statistics:\n{stats}"

    return (
        f"Total rows: {len(df)} | Columns: {', '.join(df.columns)}\n\n"
        f"Sample data (first {min(len(df), _PREVIEW_ROWS)} rows):\n"
        f"{preview_rows}"
        f"{stats_text}"
    )
