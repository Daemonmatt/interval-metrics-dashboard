"""Specialization-level performance — uses case_specialization."""
from __future__ import annotations

import html

import pandas as pd
import plotly.express as px
import streamlit as st

import action_plan as AP
import metrics as M
import theme
import ui


ui.set_page("Interval Metrics — Specialization View")

df = ui.load_and_filter()
if df is None or df.empty:
    ui.banner("Specialization View", "Select a data source to begin.")
    st.stop()

ui.banner(
    "Specialization Performance",
    "Slices the same metrics by <code>case_specialization</code>. "
    "Use it to find the queues that drag SLAs down.",
    eyebrow="SPECIALIZATION",
)
ui.filter_summary(df)
st.markdown("")

ui.kpi_strip(df)


def _scorecard_html(table: pd.DataFrame, name_col: str, label: str) -> str:
    """Render a styled scorecard table (matches the Overview look)."""
    headers = [
        label, "Chat Vol", "Email Vol",
        "Chat TTA", "Chat TFR", "Email TFR", "Abandons", "ABN %",
    ]
    thead = "".join(f"<th>{h}</th>" for h in headers)

    def _tint(value, target, lower_is_better=True):
        if value is None or pd.isna(value):
            return ""
        if lower_is_better:
            if value > target * 1.25: return "tint-bad"
            if value > target:        return "tint-warn"
            return "tint-ok"
        return ""

    rows = []
    for _, r in table.iterrows():
        abn_pct, tta = r["abn_pct"], r["chat_tta_sec"]
        tfr_min, tfr_hr = r["chat_tfr_min"], r["email_tfr_hr"]

        tta_txt = M.format_seconds(tta)
        tfr_min_txt = f"{tfr_min:.2f}" if pd.notna(tfr_min) else "—"
        tfr_hr_txt = f"{tfr_hr:.2f}" if pd.notna(tfr_hr) else "—"
        abn_pct_txt = f"{abn_pct * 100:.2f}%" if pd.notna(abn_pct) else "—"

        cells = [
            f'<td class="team-name">{html.escape(str(r[name_col]))}</td>',
            f'<td class="num">{int(r["chat_volume"]):,}</td>',
            f'<td class="num">{int(r["email_volume"]):,}</td>',
            f'<td class="num {_tint(tta, AP.CHAT_TTA_TARGET_SEC)}">{tta_txt}</td>',
            f'<td class="num {_tint(tfr_min, AP.CHAT_TFR_TARGET_MIN)}">{tfr_min_txt}</td>',
            f'<td class="num {_tint(tfr_hr, AP.EMAIL_TFR_TARGET_HR)}">{tfr_hr_txt}</td>',
            f'<td class="num">{int(r["abn"]):,}</td>',
            f'<td class="num {_tint(abn_pct, AP.ABN_PCT_TARGET)}">{abn_pct_txt}</td>',
        ]
        rows.append("<tr>" + "".join(cells) + "</tr>")

    return (
        f'<table class="cx-score">'
        f'<thead><tr>{thead}</tr></thead>'
        f'<tbody>{"".join(rows)}</tbody></table>'
    )


# ---------- Top-N specializations by volume ----------

ui.section_title(
    "Top specializations by volume",
    "Volume tells you where to focus. Bars colored by team.",
)

spec = M.by_specialization(df)
top_n = st.slider("Show top N specializations", 5, 30, 15)
spec_top = spec.head(top_n)

# add team for color coding
team_map = (
    df.dropna(subset=["case_specialization"])
    .groupby("case_specialization")["team"]
    .agg(lambda s: s.mode().iat[0] if not s.mode().empty else "Unknown")
)
spec_top = spec_top.assign(team=spec_top["specialization"].map(team_map))

vol_long = spec_top.melt(
    id_vars=["specialization", "team"],
    value_vars=["chat_volume", "email_volume"],
    var_name="Channel",
    value_name="Volume",
)
vol_long["Channel"] = vol_long["Channel"].map(
    {"chat_volume": "Chat", "email_volume": "Email"}
)

fig = px.bar(
    vol_long,
    y="specialization",
    x="Volume",
    color="team",
    facet_col="Channel",
    orientation="h",
    title=f"Top {top_n} specializations — volume by channel",
    color_discrete_sequence=theme.TABLEAU_10,
    category_orders={"specialization": spec_top["specialization"].tolist()[::-1]},
)
fig.update_layout(height=max(420, 22 * top_n))
st.plotly_chart(fig, use_container_width=True)


# ---------- Specialization scorecard ----------

ui.section_title(
    "Specialization scorecard",
    "Same SLA tints as the team scorecard. Sortable by chat volume.",
)

scorecard = spec.copy()
scorecard = scorecard[scorecard["chat_volume"] + scorecard["email_volume"] > 0]
st.markdown(
    _scorecard_html(scorecard.head(top_n), "specialization", "Specialization"),
    unsafe_allow_html=True,
)


# ---------- Worst offenders ----------

ui.section_title(
    "Worst offenders by ABN %",
    "Specializations with at least 20 chats, ranked by abandonment.",
)

worst_abn = (
    spec[(spec["chat_volume"] >= 20) & spec["abn_pct"].notna()]
    .sort_values("abn_pct", ascending=False)
    .head(10)
    .assign(team=lambda d: d["specialization"].map(team_map))
)
if worst_abn.empty:
    st.info("No specializations with enough chat volume to flag.")
else:
    fig = px.bar(
        worst_abn,
        y="specialization",
        x="abn_pct",
        color="team",
        orientation="h",
        title="Top 10 specializations by ABN %",
        color_discrete_sequence=theme.TABLEAU_10,
        category_orders={"specialization": worst_abn["specialization"].tolist()[::-1]},
    )
    fig.update_xaxes(tickformat=".1%")
    fig.add_vline(
        x=AP.ABN_PCT_TARGET, line_dash="dot",
        line_color=theme.COLORS["amber"],
        annotation_text="Target 3%", annotation_position="top",
    )
    fig.update_layout(height=420)
    st.plotly_chart(fig, use_container_width=True)


# ---------- Specialization x Hour heatmap (ABN%) ----------

ui.section_title(
    "Intraday hotspots — ABN % by specialization × hour",
    "Limited to the top specializations chosen above to keep the chart legible.",
)

sh = M.by_specialization_hour(df)
sh = sh[sh["specialization"].isin(spec_top["specialization"].tolist())]

if sh.empty:
    st.info("Not enough data for a specialization × hour view.")
else:
    hours_all = [f"{h:02d}" for h in range(24)]
    pivot = sh.pivot_table(
        index="specialization", columns="hour", values="abn_pct", aggfunc="first"
    ).reindex(columns=hours_all)
    pivot = pivot.reindex(spec_top["specialization"].tolist())

    fig = px.imshow(
        pivot.values,
        x=pivot.columns,
        y=pivot.index,
        color_continuous_scale=theme.SEQ_RED,
        aspect="auto",
        labels=dict(x="Hour", y="Specialization", color="ABN %"),
    )
    fig.update_xaxes(side="top", showline=False, ticks="")
    fig.update_yaxes(showline=False, ticks="")
    fig.update_traces(
        hovertemplate="Specialization=%{y}<br>Hour=%{x}<br>ABN%=%{z:.2%}<extra></extra>"
    )
    fig.update_layout(
        title="ABN % heatmap (top specializations × hour)",
        height=max(420, 28 * top_n),
        margin=dict(l=10, r=10, t=60, b=10),
    )
    st.plotly_chart(fig, use_container_width=True)


# ---------- Per-team breakdown ----------

ui.section_title(
    "Specializations within each team",
    "Drill into one team to see which queue is the weak link.",
)

teams = sorted(df["team"].dropna().unique().tolist())
team_pick = st.selectbox("Team", teams)
team_slice = df[df["team"] == team_pick]
team_spec = M.by_specialization(team_slice)
team_spec = team_spec[team_spec["chat_volume"] + team_spec["email_volume"] > 0]
if team_spec.empty:
    st.info(f"No data for {team_pick} in the current filter.")
else:
    st.markdown(
        _scorecard_html(team_spec, "specialization", f"{team_pick} — Specialization"),
        unsafe_allow_html=True,
    )

st.download_button(
    "Download specialization scorecard (CSV)",
    spec.to_csv(index=False).encode("utf-8"),
    file_name="specialization_scorecard.csv",
    mime="text/csv",
)
