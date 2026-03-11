"""
ai_service.py
─────────────
Calls the Google Gemini API to generate a professional executive summary
from the parsed sales data.

Configuration (via .env):
    GEMINI_API_KEY  — required
    GEMINI_MODEL    — optional, defaults to "gemini-1.5-flash"
"""
import os
import textwrap

import google.generativeai as genai
from dotenv import load_dotenv

from app.models.schemas import ParsedSalesData

load_dotenv()

# ── Configuration ──────────────────────────────────────────────────────────────
_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
_MODEL_NAME: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

# Safety: configure once at import time (idempotent)
if _API_KEY:
    genai.configure(api_key=_API_KEY)


# ── Public API ─────────────────────────────────────────────────────────────────

async def generate_summary(data: ParsedSalesData) -> str:
    """
    Send the sales data preview to Gemini and return the generated summary.

    Args:
        data: A ParsedSalesData object produced by file_parser.parse_sales_file.

    Returns:
        A professional executive summary as a plain string.

    Raises:
        EnvironmentError: if GEMINI_API_KEY is not set.
        RuntimeError:     if the Gemini API returns an unusable response.
    """
    if not _API_KEY:
        raise EnvironmentError(
            "GEMINI_API_KEY is not set. "
            "Please add it to your .env file."
        )

    prompt = _build_prompt(data)

    try:
        model = genai.GenerativeModel(_MODEL_NAME)
        response = model.generate_content(prompt)
    except Exception as exc:
        raise RuntimeError(f"Gemini API call failed: {exc}") from exc

    # Gemini returns a `text` property; guard against blocked/empty responses
    summary = getattr(response, "text", "").strip()
    if not summary:
        raise RuntimeError(
            "Gemini returned an empty response. "
            "The content may have been blocked by safety filters."
        )

    return summary


# ── Private helpers ────────────────────────────────────────────────────────────

def _build_prompt(data: ParsedSalesData) -> str:
    """
    Construct the prompt sent to Gemini.
    Keeping the prompt in one place makes it easy to iterate on.
    """
    column_list = ", ".join(data.column_names)

    return textwrap.dedent(f"""
        You are a senior sales analyst writing a report for C-suite executives.
        Analyze the sales data provided below and produce a **professional executive summary**.

        Your summary MUST include the following sections:
        1. **Overview** — Total records analyzed, key columns present.
        2. **Performance Highlights** — Best-performing products, regions, or sales reps (use actual values from the data).
        3. **Key Trends** — Any noticeable patterns, growth, or decline.
        4. **Concerns / Anomalies** — Anything unusual that deserves attention.
        5. **Recommendation** — One concrete, actionable recommendation based on the data.

        Rules:
        - Use plain English. Avoid jargon.
        - Be specific — reference actual numbers from the data.
        - Keep the summary under 400 words.
        - Do NOT mention these instructions in your output.

        ---
        Dataset info:
        - Total rows: {data.row_count}
        - Columns: {column_list}

        {data.preview_text}
        ---

        Begin the executive summary now:
    """).strip()
