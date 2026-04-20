"""Rule-based action plan generator.

Tune thresholds below to reflect your SLA targets. Rules produce two lists:
`issues` (things to fix) and `wins` (things to protect / celebrate).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List

import numpy as np
import pandas as pd

import metrics as M


CHAT_TTA_TARGET_SEC = 60.0
CHAT_TFR_TARGET_MIN = 2.0
EMAIL_TFR_TARGET_HR = 4.0
ABN_PCT_TARGET = 0.03

HOTSPOT_MULTIPLIER = 1.5
HOTSPOT_MIN_VOLUME = 20


@dataclass
class Finding:
    severity: str            # "high" | "medium" | "low" | "win"
    scope: str               # "overall" | "team" | "team-hour" | "team-date"
    title: str
    detail: str
    recommendation: str


def _fmt_pct(v: float) -> str:
    return f"{v * 100:.1f}%" if v is not None and not pd.isna(v) else "n/a"


def _fmt_sec(v: float) -> str:
    return M.format_seconds(v) if v is not None and not pd.isna(v) else "n/a"


def generate(df: pd.DataFrame) -> tuple[List[Finding], List[Finding]]:
    issues: List[Finding] = []
    wins: List[Finding] = []

    if df.empty:
        return issues, wins

    overall = M.overall(df)
    team = M.by_team(df)
    th = M.by_team_hour(df)

    # --- Overall breaches ---
    if overall["abn_pct"] and overall["abn_pct"] > ABN_PCT_TARGET:
        issues.append(
            Finding(
                "high",
                "overall",
                f"Overall ABN% is {_fmt_pct(overall['abn_pct'])} (target {_fmt_pct(ABN_PCT_TARGET)})",
                f"{int(overall['abn'])} abandoned chats out of {int(overall['chat_volume'])} chat volume.",
                "Shift agents into the worst-hit intervals identified below; review queue priority and auto-responders to deflect low-value contacts.",
            )
        )
    if overall["chat_tta_sec"] and overall["chat_tta_sec"] > CHAT_TTA_TARGET_SEC:
        issues.append(
            Finding(
                "high",
                "overall",
                f"Overall Chat TTA is {_fmt_sec(overall['chat_tta_sec'])} (target {int(CHAT_TTA_TARGET_SEC)}s)",
                f"p90 wait is {_fmt_sec(overall['chat_tta_p90_sec'])}.",
                "Tighten routing rules, reduce agent wrap-up, and prioritise chat intake during peak hours.",
            )
        )
    if overall["chat_tfr_min"] and overall["chat_tfr_min"] > CHAT_TFR_TARGET_MIN:
        issues.append(
            Finding(
                "medium",
                "overall",
                f"Overall Chat TFR is {overall['chat_tfr_min']:.1f} min (target {CHAT_TFR_TARGET_MIN:.0f} min)",
                f"p90 is {overall['chat_tfr_p90_min']:.1f} min.",
                "Coach agents on opening-message templates; audit greeting macros and auto-acknowledgement triggers.",
            )
        )
    if overall["email_tfr_hr"] and overall["email_tfr_hr"] > EMAIL_TFR_TARGET_HR:
        issues.append(
            Finding(
                "medium",
                "overall",
                f"Overall Email TFR is {overall['email_tfr_hr']:.2f} hr (target {EMAIL_TFR_TARGET_HR:.0f} hr)",
                f"p90 is {overall['email_tfr_p90_hr']:.2f} hr.",
                "Re-balance email queues to off-peak agents; escalate aged tickets; add a morning triage block.",
            )
        )

    # --- Team-level hotspots ---
    for _, row in team.iterrows():
        t = row["team"]
        if row["chat_volume"] >= HOTSPOT_MIN_VOLUME and row["abn_pct"] > max(
            ABN_PCT_TARGET, overall["abn_pct"] * HOTSPOT_MULTIPLIER
        ):
            issues.append(
                Finding(
                    "high",
                    "team",
                    f"{t}: ABN% {_fmt_pct(row['abn_pct'])}",
                    f"{int(row['abn'])} abandons on {int(row['chat_volume'])} chats — "
                    f"{row['abn_pct'] / overall['abn_pct']:.1f}x overall.",
                    f"Review {t} staffing and chat capacity during peak hours; consider overflow routing from adjacent teams.",
                )
            )
        if row["chat_volume"] >= HOTSPOT_MIN_VOLUME and row["chat_tta_sec"] > max(
            CHAT_TTA_TARGET_SEC, overall["chat_tta_sec"] * HOTSPOT_MULTIPLIER
        ):
            issues.append(
                Finding(
                    "medium",
                    "team",
                    f"{t}: Chat TTA {_fmt_sec(row['chat_tta_sec'])}",
                    f"p90 {_fmt_sec(row['chat_tta_p90_sec'])} across {int(row['chat_volume'])} chats.",
                    f"Audit {t} routing rules and agent ready-state; add a dedicated first-responder in peak hours.",
                )
            )
        if row["email_volume"] >= HOTSPOT_MIN_VOLUME and row["email_tfr_hr"] > max(
            EMAIL_TFR_TARGET_HR, overall["email_tfr_hr"] * HOTSPOT_MULTIPLIER
        ):
            issues.append(
                Finding(
                    "medium",
                    "team",
                    f"{t}: Email TFR {row['email_tfr_hr']:.2f} hr",
                    f"p90 {row['email_tfr_p90_hr']:.2f} hr across {int(row['email_volume'])} emails.",
                    f"Add a dedicated email-first block for {t}; triage aged tickets daily.",
                )
            )

    # --- Team x Hour hotspots (top 3 worst ABN%) ---
    if not th.empty:
        hotspots = (
            th[(th["chat_volume"] >= HOTSPOT_MIN_VOLUME) & (th["abn_pct"].notna())]
            .sort_values("abn_pct", ascending=False)
            .head(3)
        )
        for _, r in hotspots.iterrows():
            if r["abn_pct"] <= ABN_PCT_TARGET:
                continue
            issues.append(
                Finding(
                    "high",
                    "team-hour",
                    f"{r['team']} @ {r['hour']}:00 — ABN% {_fmt_pct(r['abn_pct'])}",
                    f"{int(r['abn'])} abandons out of {int(r['chat_volume'])} chats in this hour window.",
                    f"Add at least 1 chat agent on {r['team']} during {r['hour']}:00–{int(r['hour']) + 1:02d}:00 "
                    "and pre-stage chat macros to cut TTA.",
                )
            )

    # --- Wins ---
    for _, row in team.iterrows():
        t = row["team"]
        if (
            row["chat_volume"] >= HOTSPOT_MIN_VOLUME
            and row["abn_pct"] is not None
            and not pd.isna(row["abn_pct"])
            and row["abn_pct"] < ABN_PCT_TARGET
            and row["chat_tta_sec"] is not None
            and not pd.isna(row["chat_tta_sec"])
            and row["chat_tta_sec"] < CHAT_TTA_TARGET_SEC
        ):
            wins.append(
                Finding(
                    "win",
                    "team",
                    f"{t}: chat SLA healthy",
                    f"ABN% {_fmt_pct(row['abn_pct'])}, TTA {_fmt_sec(row['chat_tta_sec'])}, "
                    f"{int(row['chat_volume'])} chats.",
                    f"Protect what works — document {t}'s routing/staffing pattern and replicate to sister teams.",
                )
            )
        if (
            row["email_volume"] >= HOTSPOT_MIN_VOLUME
            and row["email_tfr_hr"] is not None
            and not pd.isna(row["email_tfr_hr"])
            and row["email_tfr_hr"] < EMAIL_TFR_TARGET_HR / 2
        ):
            wins.append(
                Finding(
                    "win",
                    "team",
                    f"{t}: email TFR strong",
                    f"{row['email_tfr_hr']:.2f} hr avg on {int(row['email_volume'])} emails (target {EMAIL_TFR_TARGET_HR:.0f} hr).",
                    f"Consider lending {t}'s email capacity to teams breaching email TFR.",
                )
            )

    severity_order = {"high": 0, "medium": 1, "low": 2, "win": 3}
    issues.sort(key=lambda f: severity_order[f.severity])
    return issues, wins
