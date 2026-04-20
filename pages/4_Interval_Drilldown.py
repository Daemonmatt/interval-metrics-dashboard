"""Native 15-min interval drilldown (created_at_interval)."""
from __future__ import annotations

import plotly.express as px
import streamlit as st

import action_plan as AP
import metrics as M
import theme
import ui


ui.set_page("Interval Metrics — Interval Drilldown")

df = ui.load_and_filter()
if df is None or df.empty:
    ui.banner("Interval Drilldown", "Select a data source to begin.")
    st.stop()

ui.banner(
    "Interval Drilldown",
    "Native 15-min buckets from <code>created_at_interval</code>.",
    eyebrow="15-MIN INTERVAL",
)
ui.filter_summary(df)

ti = M.by_team_interval(df).sort_values(["team", "created_at_interval"])
if ti.empty:
    st.info("No 15-min interval rows in the current filter.")
    st.stop()

teams = sorted(df["team"].dropna().unique().tolist())
picked = st.multiselect("Teams to show", teams, default=teams)
ti = ti[ti["team"].isin(picked)]

ui.section_title("Abandonment by interval")
fig = px.line(
    ti, x="created_at_interval", y="abn_pct", color="team", markers=True,
    title="ABN % by 15-min Interval",
    labels={"created_at_interval": "Interval (HH:MM)", "abn_pct": "ABN %"},
    color_discrete_sequence=theme.TABLEAU_10,
)
fig.update_yaxes(tickformat=".1%")
fig.add_hline(y=AP.ABN_PCT_TARGET, line_dash="dot", line_color=theme.COLORS["amber"],
              annotation_text="Target 3%", annotation_position="top right")
st.plotly_chart(fig, use_container_width=True)

ui.section_title("Chat TTA by interval")
fig = px.line(
    ti, x="created_at_interval", y="chat_tta_sec", color="team", markers=True,
    title="Chat TTA (seconds) by 15-min Interval",
    labels={"created_at_interval": "Interval", "chat_tta_sec": "Chat TTA (s)"},
    color_discrete_sequence=theme.TABLEAU_10,
)
fig.add_hline(y=AP.CHAT_TTA_TARGET_SEC, line_dash="dot", line_color=theme.COLORS["amber"],
              annotation_text="Target 60s", annotation_position="top right")
st.plotly_chart(fig, use_container_width=True)

ui.section_title("Interval table")
display = ti.rename(
    columns={
        "team": "Team",
        "created_at_interval": "Interval",
        "chat_volume": "Chat Vol",
        "email_volume": "Email Vol",
        "chat_tta_sec": "Chat TTA (s)",
        "chat_tfr_min": "Chat TFR (min)",
        "email_tfr_hr": "Email TFR (hr)",
        "abn": "ABN",
        "abn_pct": "ABN %",
    }
)[
    [
        "Team", "Interval", "Chat Vol", "Email Vol",
        "Chat TTA (s)", "Chat TFR (min)", "Email TFR (hr)", "ABN", "ABN %",
    ]
].copy()
display["ABN %"] = (display["ABN %"] * 100).round(2)
display["Chat TTA (s)"] = display["Chat TTA (s)"].round(1)
display["Chat TFR (min)"] = display["Chat TFR (min)"].round(2)
display["Email TFR (hr)"] = display["Email TFR (hr)"].round(2)
st.dataframe(display, use_container_width=True, hide_index=True)

st.download_button(
    "Download interval table (CSV)",
    display.to_csv(index=False).encode("utf-8"),
    file_name="interval_drilldown.csv",
    mime="text/csv",
)
