"""Shared UI helpers: sidebar filters, KPI grid, scorecard, action plan."""
from __future__ import annotations

import html
import os
from typing import Optional

import pandas as pd
import streamlit as st

import action_plan as AP
import loader
import metrics as M
import theme


def set_page(title: str) -> None:
    st.set_page_config(
        page_title=title,
        layout="wide",
        page_icon=":bar_chart:",
        initial_sidebar_state="expanded",
    )
    theme.apply_theme()


def banner(title: str, subtitle: str = "", eyebrow: str = "CX OPERATIONS") -> None:
    st.markdown(
        f"""
        <div class="cx-banner">
          <div class="cx-eyebrow">{eyebrow}</div>
          <div class="cx-title">{title}</div>
          <div class="cx-sub">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def filter_summary(df: pd.DataFrame) -> None:
    chips = []
    dmin = df["date"].min()
    dmax = df["date"].max()
    if dmin and dmax:
        chips.append(f"Dates &middot; {dmin} to {dmax}")
    chips.append(f"Teams &middot; {df['team'].nunique()}")
    chips.append(f"Origins &middot; {df['origin'].nunique()}")
    chips.append(f"Records &middot; {len(df):,}")
    html_str = "".join(f'<span class="cx-filter-chip">{c}</span>' for c in chips)
    st.markdown(html_str, unsafe_allow_html=True)


def _load_from_sidebar() -> Optional[pd.DataFrame]:
    st.sidebar.markdown("### Data source")
    uploaded = st.sidebar.file_uploader("Upload Excel export", type=["xlsx"])
    default_exists = os.path.exists(loader.DEFAULT_FILE)
    use_default = st.sidebar.checkbox(
        "Use default file",
        value=(uploaded is None and default_exists),
        help=loader.DEFAULT_FILE,
        disabled=not default_exists and uploaded is None,
    )

    try:
        if uploaded is not None:
            return loader.load_data(uploaded.getvalue())
        if use_default and default_exists:
            return loader.load_data(loader.DEFAULT_FILE)
    except Exception as exc:  # noqa: BLE001
        st.sidebar.error(f"Failed to load: {exc}")
        return None

    st.info("Upload an Excel export in the sidebar to begin.")
    return None


def sidebar_filters(df: pd.DataFrame) -> pd.DataFrame:
    st.sidebar.markdown("### Filters")
    dates = sorted({d for d in df["date"].dropna().tolist()})
    date_range = None
    if dates:
        date_range = st.sidebar.date_input(
            "Date range",
            value=(dates[0], dates[-1]),
            min_value=dates[0],
            max_value=dates[-1],
            help="From created_at (sole source of truth for dates).",
        )
        if not isinstance(date_range, tuple) or len(date_range) != 2:
            date_range = (dates[0], dates[-1])

    teams = sorted(df["team"].dropna().unique().tolist())
    picked_teams = st.sidebar.multiselect("Teams", teams, default=teams)

    origins = sorted(df["origin"].dropna().unique().tolist())
    picked_origins = st.sidebar.multiselect("Origins", origins, default=origins)

    hour_range = st.sidebar.slider(
        "Hour range",
        min_value=0,
        max_value=23,
        value=(0, 23),
        help="Hour derived from created_at_interval.",
    )

    st.sidebar.markdown("---")
    st.sidebar.caption(
        "Hour and 15-min interval views use created_at_interval. "
        "Day-level views use created_at."
    )

    return loader.filter_frame(
        df,
        teams=picked_teams or None,
        origins=picked_origins or None,
        date_range=date_range,
        hour_range=hour_range,
    )


def load_and_filter() -> Optional[pd.DataFrame]:
    df = _load_from_sidebar()
    if df is None:
        return None
    return sidebar_filters(df)


# ---------- Status helpers (single place) ----------

def _status(value, target, lower_is_better: bool = True) -> str:
    if value is None or pd.isna(value) or target is None:
        return "neu"
    if lower_is_better:
        if value > target * 1.25:
            return "bad"
        if value > target:
            return "warn"
        return "ok"
    if value < target * 0.75:
        return "bad"
    if value < target:
        return "warn"
    return "ok"


STATUS_ACCENT = {
    "ok":   theme.COLORS["green"],
    "warn": theme.COLORS["amber"],
    "bad":  theme.COLORS["red"],
    "neu":  theme.COLORS["navy3"],
}
STATUS_LABEL = {
    "ok":   "ON TARGET",
    "warn": "AT RISK",
    "bad":  "BREACH",
    "neu":  "",
}


# ---------- KPI grid (single <div> -> consistent spacing) ----------

def kpi_strip(df: pd.DataFrame) -> None:
    o = M.overall(df)

    def card(label: str, value: str, sub: str, status: str) -> str:
        accent = STATUS_ACCENT[status]
        status_html = ""
        if STATUS_LABEL[status]:
            status_html = (
                f'<span class="cx-status"><span class="cx-dot"></span>'
                f'{STATUS_LABEL[status]}</span>'
            )
        return (
            f'<div class="cx-kpi status-{status}" style="--accent:{accent};">'
            f'  <div>'
            f'    <div class="cx-label">{label}</div>'
            f'    <div class="cx-value">{value}</div>'
            f'  </div>'
            f'  <div class="cx-sub">{status_html}{sub}</div>'
            f'</div>'
        )

    cards = [
        card("Chat Volume",  f"{int(o['chat_volume']):,}", "chat cases", "neu"),
        card("Email Volume", f"{int(o['email_volume']):,}", "email cases", "neu"),
        card(
            "Chat TTA",
            M.format_seconds(o["chat_tta_sec"]),
            f"p90 {M.format_seconds(o['chat_tta_p90_sec'])} &middot; target {int(AP.CHAT_TTA_TARGET_SEC)}s",
            _status(o["chat_tta_sec"], AP.CHAT_TTA_TARGET_SEC),
        ),
        card(
            "Chat TFR",
            M.format_minutes(o["chat_tfr_min"]),
            f"p90 {M.format_minutes(o['chat_tfr_p90_min'])} &middot; target {AP.CHAT_TFR_TARGET_MIN:.0f} min",
            _status(o["chat_tfr_min"], AP.CHAT_TFR_TARGET_MIN),
        ),
        card(
            "Email TFR",
            M.format_hours(o["email_tfr_hr"]),
            f"p90 {M.format_hours(o['email_tfr_p90_hr'])} &middot; target {AP.EMAIL_TFR_TARGET_HR:.0f} hr",
            _status(o["email_tfr_hr"], AP.EMAIL_TFR_TARGET_HR),
        ),
        card(
            "Abandons",
            f"{int(o['abn']):,}",
            "abandoned chats",
            "bad" if o["abn"] else "ok",
        ),
        card(
            "ABN %",
            M.format_pct(o["abn_pct"]),
            f"target {M.format_pct(AP.ABN_PCT_TARGET)}",
            _status(o["abn_pct"], AP.ABN_PCT_TARGET),
        ),
    ]

    st.markdown(
        f'<div class="cx-kpi-grid">{"".join(cards)}</div>',
        unsafe_allow_html=True,
    )


def section_title(title: str, subtitle: str = "") -> None:
    st.markdown(f'<div class="cx-section-title">{title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="cx-section-sub">{subtitle}</div>', unsafe_allow_html=True)


# ---------- Scorecard (hand-rolled HTML for full control) ----------

def _tint_class(value, target, lower_is_better: bool = True) -> str:
    s = _status(value, target, lower_is_better)
    return {"ok": "tint-ok", "warn": "tint-warn", "bad": "tint-bad", "neu": ""}[s]


def render_scorecard(df: pd.DataFrame) -> None:
    team = M.by_team(df)
    if team.empty:
        st.info("No rows in current filter selection.")
        return

    headers = [
        "Team", "Chat Vol", "Email Vol",
        "Chat TTA", "Chat TFR", "Email TFR", "Abandons", "ABN %",
    ]
    thead = "".join(f"<th>{h}</th>" for h in headers)

    rows_html = []
    for _, r in team.iterrows():
        abn_pct = r["abn_pct"]
        tta = r["chat_tta_sec"]
        tfr_min = r["chat_tfr_min"]
        tfr_hr = r["email_tfr_hr"]
        abn = r["abn"]

        abn_cls = _tint_class(abn_pct, AP.ABN_PCT_TARGET)
        tta_cls = _tint_class(tta, AP.CHAT_TTA_TARGET_SEC)
        tfr_min_cls = _tint_class(tfr_min, AP.CHAT_TFR_TARGET_MIN)
        tfr_hr_cls = _tint_class(tfr_hr, AP.EMAIL_TFR_TARGET_HR)

        abn_pct_txt = f"{abn_pct * 100:.2f}%" if pd.notna(abn_pct) else "—"
        tta_txt = M.format_seconds(tta)
        tfr_min_txt = f"{tfr_min:.2f}" if pd.notna(tfr_min) else "—"
        tfr_hr_txt = f"{tfr_hr:.2f}" if pd.notna(tfr_hr) else "—"

        cells = [
            f'<td class="team-name">{html.escape(str(r["team"]))}</td>',
            f'<td class="num">{int(r["chat_volume"]):,}</td>',
            f'<td class="num">{int(r["email_volume"]):,}</td>',
            f'<td class="num {tta_cls}">{tta_txt}</td>',
            f'<td class="num {tfr_min_cls}">{tfr_min_txt}</td>',
            f'<td class="num {tfr_hr_cls}">{tfr_hr_txt}</td>',
            f'<td class="num">{int(abn):,}</td>',
            f'<td class="num {abn_cls}">{abn_pct_txt}</td>',
        ]
        rows_html.append("<tr>" + "".join(cells) + "</tr>")

    table_html = (
        f'<table class="cx-score">'
        f'<thead><tr>{thead}</tr></thead>'
        f'<tbody>{"".join(rows_html)}</tbody>'
        f'</table>'
    )
    st.markdown(table_html, unsafe_allow_html=True)


# ---------- Action plan (card panels) ----------

def _finding_html(f) -> str:
    badge = {"high": "HIGH", "medium": "MEDIUM", "low": "LOW", "win": "WIN"}[f.severity]
    rec_label = "Keep" if f.severity == "win" else "Action"
    return (
        f'<div class="cx-finding {f.severity}">'
        f'  <div class="cx-ftitle">'
        f'    <span class="cx-fchip">{badge}</span>{html.escape(f.title)}'
        f'  </div>'
        f'  <div class="cx-fdetail">{html.escape(f.detail)}</div>'
        f'  <div class="cx-frec"><b>{rec_label}:</b> {html.escape(f.recommendation)}</div>'
        f'</div>'
    )


def render_action_plan(df: pd.DataFrame) -> None:
    issues, wins = AP.generate(df)

    section_title(
        "Action plan",
        "Auto-generated from SLA thresholds and hotspot rules. Thresholds live "
        "in action_plan.py.",
    )

    left, right = st.columns([3, 2])
    with left:
        st.markdown(
            '<div class="cx-section-sub">Issues to address</div>',
            unsafe_allow_html=True,
        )
        if not issues:
            st.markdown(
                '<div class="cx-finding win"><div class="cx-ftitle">'
                '<span class="cx-fchip">OK</span>No SLA breaches detected</div></div>',
                unsafe_allow_html=True,
            )
        for f in issues:
            st.markdown(_finding_html(f), unsafe_allow_html=True)
    with right:
        st.markdown(
            '<div class="cx-section-sub">What\'s working</div>',
            unsafe_allow_html=True,
        )
        if not wins:
            st.markdown(
                '<div class="cx-finding low"><div class="cx-ftitle">'
                '<span class="cx-fchip">INFO</span>No clear wins yet</div>'
                '<div class="cx-fdetail">Focus on closing high-severity issues first.</div>'
                '</div>',
                unsafe_allow_html=True,
            )
        for f in wins:
            st.markdown(_finding_html(f), unsafe_allow_html=True)
