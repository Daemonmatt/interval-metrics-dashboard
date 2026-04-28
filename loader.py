"""Excel loader for the interval-level metrics export.

Time handling is strict:
- Hour / interval are derived from `created_at_interval` only (HH:MM).
- Calendar date is parsed from `created_at` only.
No other column is consulted for time calculations.
"""
from __future__ import annotations

import io
import os
from pathlib import Path
from typing import Optional, Union

import pandas as pd
import streamlit as st


DEFAULT_FILE = os.environ.get(
    "INTERVAL_METRICS_FILE",
    "/Users/matsyendrashukla/Downloads/"
    "Drilldown_in_Interval_Level_Metrics-69e674ab093f334cba5c0911.xlsx",
)

REQUIRED_COLUMNS = [
    "team",
    "origin",
    "created_at",
    "created_at_interval",
    "case_specialization",
    "Chat Volume (Actual)",
    "Email Volume (Actual)",
    "Chat TTA",
    "Chat TFR",
    "Email TFR",
    "ABN",
]


def _normalise_interval(val) -> Optional[str]:
    """Return 'HH:MM' string (zero-padded) or None."""
    if pd.isna(val):
        return None
    s = str(val).strip()
    if not s:
        return None
    if ":" in s:
        h, _, m = s.partition(":")
        try:
            return f"{int(h):02d}:{int(m):02d}"
        except ValueError:
            return None
    return None


@st.cache_data(show_spinner="Loading Excel...")
def load_data(source: Union[str, Path, bytes, None] = None) -> pd.DataFrame:
    """Load the workbook and return a tidy dataframe with derived time columns.

    `source` may be a path, file-like bytes, or None (uses DEFAULT_FILE).
    """
    if source is None:
        source = DEFAULT_FILE
    if isinstance(source, (bytes, bytearray)):
        source = io.BytesIO(source)
    df = pd.read_excel(source, sheet_name=0, engine="openpyxl")

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    df["created_at_interval"] = df["created_at_interval"].map(_normalise_interval)
    df["hour"] = df["created_at_interval"].str.slice(0, 2)

    created_dt = pd.to_datetime(df["created_at"], errors="coerce", utc=True)
    df["date"] = created_dt.dt.tz_convert("America/Los_Angeles").dt.date

    for col in ["Chat TTA", "Chat TFR", "Email TFR"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["has_chat"] = df["Chat Volume (Actual)"].notna()
    df["has_email"] = df["Email Volume (Actual)"].notna()
    df["has_abn"] = df["ABN"].notna()

    df["team"] = df["team"].fillna("Unknown")
    df["origin"] = df["origin"].fillna("Unknown")
    df["case_specialization"] = df["case_specialization"].fillna("Unspecified")

    return df


def filter_frame(
    df: pd.DataFrame,
    teams: Optional[list[str]] = None,
    origins: Optional[list[str]] = None,
    specializations: Optional[list[str]] = None,
    date_range: Optional[tuple] = None,
    hour_range: Optional[tuple[int, int]] = None,
) -> pd.DataFrame:
    out = df
    if teams:
        out = out[out["team"].isin(teams)]
    if origins:
        out = out[out["origin"].isin(origins)]
    if specializations:
        out = out[out["case_specialization"].isin(specializations)]
    if date_range and len(date_range) == 2 and all(date_range):
        d0, d1 = date_range
        out = out[(out["date"] >= d0) & (out["date"] <= d1)]
    if hour_range:
        h0, h1 = hour_range
        hours = out["hour"].astype("string")
        mask = hours.notna() & hours.between(f"{h0:02d}", f"{h1:02d}")
        out = out[mask]
    return out
