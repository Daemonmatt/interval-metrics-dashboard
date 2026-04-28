"""Pure pandas aggregations for the interval-level metrics dashboard.

All functions accept a pre-filtered dataframe from `loader.load_data` and
return a dataframe suitable for display or charting.
"""
from __future__ import annotations

from typing import Iterable

import numpy as np
import pandas as pd


METRIC_UNITS = {
    "chat_tta_sec": "seconds",
    "chat_tfr_min": "minutes",
    "email_tfr_hr": "hours",
    "chat_volume": "cases",
    "email_volume": "cases",
    "abn": "cases",
    "abn_pct": "%",
}


def _safe_mean(s: pd.Series) -> float:
    s = pd.to_numeric(s, errors="coerce").dropna()
    return float(s.mean()) if len(s) else np.nan


def _safe_p90(s: pd.Series) -> float:
    s = pd.to_numeric(s, errors="coerce").dropna()
    return float(s.quantile(0.9)) if len(s) else np.nan


def _aggregate(df: pd.DataFrame) -> pd.Series:
    chat_vol = int(df["has_chat"].sum())
    email_vol = int(df["has_email"].sum())
    abn = int(df["has_abn"].sum())
    abn_pct = (abn / chat_vol) if chat_vol else np.nan
    return pd.Series(
        {
            "chat_volume": chat_vol,
            "email_volume": email_vol,
            "abn": abn,
            "abn_pct": abn_pct,
            "chat_tta_sec": _safe_mean(df["Chat TTA"]),
            "chat_tta_p90_sec": _safe_p90(df["Chat TTA"]),
            "chat_tfr_min": _safe_mean(df["Chat TFR"]),
            "chat_tfr_p90_min": _safe_p90(df["Chat TFR"]),
            "email_tfr_hr": _safe_mean(df["Email TFR"]),
            "email_tfr_p90_hr": _safe_p90(df["Email TFR"]),
        }
    )


def overall(df: pd.DataFrame) -> pd.Series:
    return _aggregate(df)


def _by(df: pd.DataFrame, group_cols: Iterable[str]) -> pd.DataFrame:
    group_cols = list(group_cols)
    if df.empty:
        return pd.DataFrame(columns=group_cols + list(_aggregate(df).index))
    grouped = df.groupby(group_cols, dropna=False, observed=False).apply(
        _aggregate, include_groups=False
    )
    return grouped.reset_index()


def by_team(df: pd.DataFrame) -> pd.DataFrame:
    return _by(df, ["team"]).sort_values("chat_volume", ascending=False)


def by_specialization(df: pd.DataFrame) -> pd.DataFrame:
    out = _by(df, ["case_specialization"])
    out = out.rename(columns={"case_specialization": "specialization"})
    return out.sort_values("chat_volume", ascending=False)


def by_team_specialization(df: pd.DataFrame) -> pd.DataFrame:
    out = _by(df, ["team", "case_specialization"])
    out = out.rename(columns={"case_specialization": "specialization"})
    return out.sort_values(["team", "chat_volume"], ascending=[True, False])


def by_specialization_hour(df: pd.DataFrame) -> pd.DataFrame:
    out = _by(df, ["case_specialization", "hour"])
    out = out.rename(columns={"case_specialization": "specialization"})
    return out


def by_team_hour(df: pd.DataFrame) -> pd.DataFrame:
    return _by(df, ["team", "hour"])


def by_team_date(df: pd.DataFrame) -> pd.DataFrame:
    return _by(df, ["team", "date"])


def by_team_interval(df: pd.DataFrame) -> pd.DataFrame:
    return _by(df, ["team", "created_at_interval"])


def by_hour(df: pd.DataFrame) -> pd.DataFrame:
    return _by(df, ["hour"]).sort_values("hour")


def by_date(df: pd.DataFrame) -> pd.DataFrame:
    return _by(df, ["date"]).sort_values("date")


def format_seconds(v: float) -> str:
    if v is None or pd.isna(v):
        return "—"
    v = int(round(v))
    m, s = divmod(v, 60)
    return f"{m:d}:{s:02d}"


def format_minutes(v: float) -> str:
    if v is None or pd.isna(v):
        return "—"
    return f"{v:.1f} min"


def format_hours(v: float) -> str:
    if v is None or pd.isna(v):
        return "—"
    return f"{v:.2f} hr"


def format_pct(v: float) -> str:
    if v is None or pd.isna(v):
        return "—"
    return f"{v * 100:.2f}%"
