"""
AI service — calls Gemini or Groq depending on AI_PROVIDER env var.
Builds a concise prompt from the pandas DataFrame and returns a summary string.
"""
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

AI_PROVIDER = os.getenv("AI_PROVIDER", "gemini").lower()


def _build_prompt(df: pd.DataFrame) -> str:
    """Convert the top rows of the DataFrame into a plain-text table for the prompt."""
    preview = df.head(20).to_string(index=False)
    columns = ", ".join(df.columns.tolist())

    return (
        "You are a professional sales analyst. Analyze the following sales data and produce "
        "a concise, professional summary that highlights:\n"
        "1. Total revenue / units sold (if columns are present)\n"
        "2. Best-performing products or regions\n"
        "3. Notable trends or anomalies\n"
        "4. One actionable recommendation\n\n"
        f"Columns: {columns}\n\n"
        f"Data preview (first 20 rows):\n{preview}\n\n"
        "Write the summary in plain English, suitable for a non-technical executive audience."
    )


async def generate_summary(df: pd.DataFrame) -> str:
    prompt = _build_prompt(df)

    if AI_PROVIDER == "groq":
        return await _call_groq(prompt)
    return await _call_gemini(prompt)


# ── Gemini ────────────────────────────────────────────────────────────────────
async def _call_gemini(prompt: str) -> str:
    import google.generativeai as genai

    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    return response.text


# ── Groq ─────────────────────────────────────────────────────────────────────
async def _call_groq(prompt: str) -> str:
    from groq import AsyncGroq

    client = AsyncGroq(api_key=os.environ["GROQ_API_KEY"])
    chat = await client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[{"role": "user", "content": prompt}],
    )
    return chat.choices[0].message.content
