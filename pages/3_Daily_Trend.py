"""Per-date trend. Date is parsed from `created_at` (sole source of truth for date)."""
from __future__ import annotations

import plotly.express as px
import streamlit as st

import metrics as M
import theme
import ui


ui.set_page("Interval Metrics — Daily Trend")

df = ui.load_and_filter()
if df is None or df.empty:
    ui.banner("Daily Trend", "Select a data source to begin.")
    st.stop()

ui.banner(
    "Daily Trend",
    "Date comes from <code>created_at</code>. Dotted lines show SLA targets.",
    eyebrow="DAY OVER DAY",
)
ui.filter_summary(df)

td = M.by_team_date(df).sort_values(["date", "team"])
if td.empty:
    st.info("No per-date rows in the current filter.")
    st.stop()

td["date"] = td["date"].astype(str)

ui.section_title("Service levels by day")

c1, c2 = st.columns(2)
with c1:
    fig = px.line(
        td, x="date", y="abn_pct", color="team", markers=True,
        title="ABN % by Day",
        labels={"abn_pct": "ABN %", "date": "Date"},
        color_discrete_sequence=theme.TABLEAU_10,
    )
    fig.update_yaxes(tickformat=".1%")
    fig.add_hline(y=0.03, line_dash="dot", line_color=theme.COLORS["amber"],
                  annotation_text="Target 3%", annotation_position="top right")
    st.plotly_chart(fig, use_container_width=True)

    fig = px.line(
        td, x="date", y="chat_tta_sec", color="team", markers=True,
        title="Chat TTA (seconds) by Day",
        labels={"chat_tta_sec": "Chat TTA (s)", "date": "Date"},
        color_discrete_sequence=theme.TABLEAU_10,
    )
    fig.add_hline(y=60, line_dash="dot", line_color=theme.COLORS["amber"],
                  annotation_text="Target 60s", annotation_position="top right")
    st.plotly_chart(fig, use_container_width=True)

with c2:
    fig = px.line(
        td, x="date", y="chat_tfr_min", color="team", markers=True,
        title="Chat TFR (minutes) by Day",
        labels={"chat_tfr_min": "Chat TFR (min)", "date": "Date"},
        color_discrete_sequence=theme.TABLEAU_10,
    )
    fig.add_hline(y=2, line_dash="dot", line_color=theme.COLORS["amber"],
                  annotation_text="Target 2 min", annotation_position="top right")
    st.plotly_chart(fig, use_container_width=True)

    fig = px.line(
        td, x="date", y="email_tfr_hr", color="team", markers=True,
        title="Email TFR (hours) by Day",
        labels={"email_tfr_hr": "Email TFR (hr)", "date": "Date"},
        color_discrete_sequence=theme.TABLEAU_10,
    )
    fig.add_hline(y=4, line_dash="dot", line_color=theme.COLORS["amber"],
                  annotation_text="Target 4 hr", annotation_position="top right")
    st.plotly_chart(fig, use_container_width=True)

ui.section_title("Daily volume mix", "Chat vs email contribution by team.")
vol = td.melt(
    id_vars=["date", "team"],
    value_vars=["chat_volume", "email_volume"],
    var_name="Channel",
    value_name="Volume",
)
vol["Channel"] = vol["Channel"].map({"chat_volume": "Chat", "email_volume": "Email"})
fig = px.bar(
    vol, x="date", y="Volume", color="team", facet_col="Channel",
    barmode="stack", title="Daily Volume",
    color_discrete_sequence=theme.TABLEAU_10,
)
st.plotly_chart(fig, use_container_width=True)

ui.section_title("Daily table")
display = td.rename(
    columns={
        "date": "Date",
        "team": "Team",
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
        "Date", "Team", "Chat Vol", "Email Vol",
        "Chat TTA (s)", "Chat TFR (min)", "Email TFR (hr)", "ABN", "ABN %",
    ]
].copy()
display["ABN %"] = (display["ABN %"] * 100).round(2)
display["Chat TTA (s)"] = display["Chat TTA (s)"].round(1)
display["Chat TFR (min)"] = display["Chat TFR (min)"].round(2)
display["Email TFR (hr)"] = display["Email TFR (hr)"].round(2)
st.dataframe(display, use_container_width=True, hide_index=True)
