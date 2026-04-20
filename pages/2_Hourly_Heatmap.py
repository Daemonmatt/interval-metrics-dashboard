"""Team x Hour heatmaps — one per metric. Quickly spots intraday hotspots."""
from __future__ import annotations

import plotly.express as px
import streamlit as st

import metrics as M
import theme
import ui


ui.set_page("Interval Metrics — Heatmaps")

df = ui.load_and_filter()
if df is None or df.empty:
    ui.banner("Hourly Heatmaps", "Select a data source to begin.")
    st.stop()

ui.banner(
    "Hourly Heatmaps — Team × Hour",
    "Hour is derived from <code>created_at_interval</code>. Darker shades "
    "highlight intraday hotspots.",
    eyebrow="INTRADAY",
)
ui.filter_summary(df)

th = M.by_team_hour(df)
if th.empty:
    st.info("No team/hour combinations in the current filter.")
    st.stop()

hours_all = [f"{h:02d}" for h in range(24)]


def heatmap(metric_col: str, title: str, color_scale, fmt: str = ".2f"):
    pivot = th.pivot_table(
        index="team", columns="hour", values=metric_col, aggfunc="first"
    ).reindex(columns=hours_all)
    fig = px.imshow(
        pivot.values,
        x=pivot.columns,
        y=pivot.index,
        color_continuous_scale=color_scale,
        aspect="auto",
        labels=dict(x="Hour", y="Team", color=title),
    )
    fig.update_xaxes(side="top", showline=False, ticks="")
    fig.update_yaxes(showline=False, ticks="")
    fig.update_traces(hovertemplate="Team=%{y}<br>Hour=%{x}<br>Value=%{z:" + fmt + "}<extra></extra>")
    fig.update_layout(title=title, margin=dict(l=10, r=10, t=50, b=10))
    st.plotly_chart(fig, use_container_width=True)


ui.section_title("Abandonment %", "Darker cells show where customers are giving up on chats.")
heatmap("abn_pct", "ABN % by Team × Hour", theme.SEQ_RED, fmt=".2%")

ui.section_title("Chat responsiveness", "How fast chats are being picked up and answered.")
c1, c2 = st.columns(2)
with c1:
    heatmap("chat_tta_sec", "Chat TTA (seconds)", theme.SEQ_AMBER, fmt=".0f")
with c2:
    heatmap("chat_tfr_min", "Chat TFR (minutes)", theme.SEQ_AMBER, fmt=".2f")

ui.section_title("Email & volume", "Email response time and where chat volume concentrates.")
c3, c4 = st.columns(2)
with c3:
    heatmap("email_tfr_hr", "Email TFR (hours)", theme.SEQ_AMBER, fmt=".2f")
with c4:
    heatmap("chat_volume", "Chat Volume", theme.SEQ_NAVY, fmt=".0f")
