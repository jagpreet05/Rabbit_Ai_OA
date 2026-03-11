"""
Utility to parse uploaded CSV or XLSX files into a pandas DataFrame.
"""
import io
import pandas as pd


def parse_sales_file(file_bytes: io.BytesIO, filename: str) -> pd.DataFrame:
    """
    Read a CSV or XLSX file and return a clean DataFrame.

    Args:
        file_bytes: file content as a BytesIO object.
        filename:   original filename (used to detect extension).

    Returns:
        pd.DataFrame with the parsed data.

    Raises:
        ValueError: if the file extension is not supported.
    """
    name = (filename or "").lower()

    if name.endswith(".csv"):
        df = pd.read_csv(file_bytes)
    elif name.endswith(".xlsx") or name.endswith(".xls"):
        df = pd.read_excel(file_bytes, engine="openpyxl")
    else:
        raise ValueError(f"Unsupported file type: {filename}")

    # Drop completely empty rows/columns
    df.dropna(how="all", inplace=True)
    df.dropna(axis=1, how="all", inplace=True)

    return df
