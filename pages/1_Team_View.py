"""Per-team drilldown: how does each team perform across the day?"""
from __future__ import annotations

import plotly.express as px
import streamlit as st

import metrics as M
import theme
import ui


ui.set_page("Interval Metrics — Team View")

df = ui.load_and_filter()
if df is None or df.empty:
    ui.banner("Team View", "Select a data source to begin.")
    st.stop()

teams = sorted(df["team"].dropna().unique().tolist())
team = st.sidebar.selectbox("Team", teams)

team_df = df[df["team"] == team]

ui.banner(
    f"{team} — Team Performance",
    f"Hourly breakdown across {len(team_df):,} records. Hour derived from "
    "<code>created_at_interval</code>.",
    eyebrow="TEAM VIEW",
)
ui.filter_summary(team_df)
st.markdown("")
ui.kpi_strip(team_df)

hourly = M.by_team_hour(team_df).sort_values("hour")
if hourly.empty:
    st.info("No hourly data for this team in the current filter.")
    st.stop()

ui.section_title("Hourly view", "Bars and lines use the team's filtered data.")

c1, c2 = st.columns(2)
with c1:
    fig = px.bar(
        hourly,
        x="hour",
        y="chat_volume",
        title="Chat Volume by Hour",
        labels={"hour": "Hour", "chat_volume": "Chat cases"},
    )
    fig.update_traces(marker_color=theme.COLORS["navy3"])
    st.plotly_chart(fig, use_container_width=True)

    fig = px.line(
        hourly,
        x="hour",
        y="chat_tta_sec",
        markers=True,
        title="Chat TTA (seconds) by Hour",
        labels={"chat_tta_sec": "Chat TTA (s)", "hour": "Hour"},
    )
    fig.update_traces(line_color=theme.COLORS["navy"], line_width=2.5,
                      marker=dict(size=7, color=theme.COLORS["navy"]))
    fig.add_hline(y=60, line_dash="dot", line_color=theme.COLORS["amber"],
                  annotation_text="Target 60s", annotation_position="top right")
    st.plotly_chart(fig, use_container_width=True)

with c2:
    fig = px.line(
        hourly,
        x="hour",
        y="abn_pct",
        markers=True,
        title="ABN % by Hour",
        labels={"abn_pct": "ABN %", "hour": "Hour"},
    )
    fig.update_traces(line_color=theme.COLORS["red"], line_width=2.5,
                      marker=dict(size=7, color=theme.COLORS["red"]))
    fig.update_yaxes(tickformat=".1%")
    fig.add_hline(y=0.03, line_dash="dot", line_color=theme.COLORS["amber"],
                  annotation_text="Target 3%", annotation_position="top right")
    st.plotly_chart(fig, use_container_width=True)

    fig = px.bar(
        hourly,
        x="hour",
        y="email_volume",
        title="Email Volume by Hour",
        labels={"email_volume": "Email cases", "hour": "Hour"},
    )
    fig.update_traces(marker_color=theme.COLORS["amber"])
    st.plotly_chart(fig, use_container_width=True)

ui.section_title("Hourly detail", "Raw values behind the charts above.")
display = hourly.rename(
    columns={
        "hour": "Hour",
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
        "Hour", "Chat Vol", "Email Vol", "Chat TTA (s)",
        "Chat TFR (min)", "Email TFR (hr)", "ABN", "ABN %",
    ]
].copy()
display["ABN %"] = (display["ABN %"] * 100).round(2)
display["Chat TTA (s)"] = display["Chat TTA (s)"].round(1)
display["Chat TFR (min)"] = display["Chat TFR (min)"].round(2)
display["Email TFR (hr)"] = display["Email TFR (hr)"].round(2)
st.dataframe(display, use_container_width=True, hide_index=True)
