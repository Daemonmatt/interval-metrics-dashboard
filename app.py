"""Interval Metrics Dashboard — Overview."""
from __future__ import annotations

import streamlit as st

import ui


def main() -> None:
    ui.set_page("Interval Metrics — Overview")

    df = ui.load_and_filter()
    if df is None or df.empty:
        ui.banner(
            "Interval Metrics",
            "Upload an Excel export from the sidebar to begin.",
            eyebrow="CX OPERATIONS",
        )
        return

    date_min, date_max = df["date"].min(), df["date"].max()
    subtitle = (
        f"Performance snapshot across {df['team'].nunique()} teams &middot; "
        f"{date_min} to {date_max} &middot; {len(df):,} records"
    )
    ui.banner("Interval Metrics — Performance at a Glance", subtitle)
    ui.filter_summary(df)

    st.markdown("")  # spacer
    ui.kpi_strip(df)

    ui.section_title(
        "Team scorecard",
        "Volume and service-level metrics by team. Green = on target, "
        "amber = at risk, red = breach.",
    )
    ui.render_scorecard(df)

    ui.render_action_plan(df)


main()
