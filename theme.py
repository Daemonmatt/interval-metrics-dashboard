"""Unified, muted 'executive' theme — one palette, consistent across every surface.

Design rules:
- Single primary color: navy (#1F3A5F). One accent: amber (#B7791F).
- Status tints are low-saturation; text stays dark for readability.
- No gradients, no loud chips. Whitespace does the work.
"""
from __future__ import annotations

import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st


COLORS = {
    "ink":        "#1C2B3A",
    "ink2":       "#3E4C5E",
    "ink3":       "#6B7785",
    "ink4":       "#98A2B0",
    "line":       "#E3E7EC",
    "line2":      "#EEF1F4",
    "surface":    "#FFFFFF",
    "canvas":     "#F7F8FA",
    "navy":       "#1F3A5F",
    "navy2":      "#2B5488",
    "navy3":      "#4A739E",
    "amber":      "#B7791F",
    "red":        "#A23B3B",
    "green":      "#3F7D4F",
    "ok_bg":      "#F1F5F2",
    "ok_text":    "#365E43",
    "warn_bg":    "#FAF3E3",
    "warn_text":  "#7A5614",
    "bad_bg":     "#F7E9E9",
    "bad_text":   "#7E2F2F",
    "neu_bg":     "#EEF1F4",
    "neu_text":   "#3E4C5E",
}

TABLEAU_10 = [
    "#1F3A5F", "#B7791F", "#4A739E", "#7E9CBF", "#3F7D4F",
    "#A23B3B", "#6B7785", "#8A6B3E", "#2B5488", "#5D7289",
]

SEQ_NAVY = [
    "#F4F7FB", "#DCE5F0", "#B9CBDF", "#8EAAC7", "#5E85AC",
    "#3E6691", "#254972", "#163558",
]
SEQ_AMBER = [
    "#FCF6E6", "#F5E2B4", "#EBCB83", "#D9B155", "#C1912E",
    "#9E731C", "#7A5614", "#5A3E0D",
]
SEQ_RED = [
    "#F7ECEC", "#ECCFCF", "#DDA9A9", "#C77F7F", "#A95858",
    "#883D3D", "#6B2A2A", "#511F1F",
]


def _register_template() -> None:
    t = go.layout.Template()
    t.layout.font = dict(
        family="Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
        size=12,
        color=COLORS["ink"],
    )
    t.layout.paper_bgcolor = COLORS["surface"]
    t.layout.plot_bgcolor = COLORS["surface"]
    t.layout.colorway = TABLEAU_10
    t.layout.title = dict(
        font=dict(size=14, color=COLORS["ink"], family="Inter, sans-serif"),
        x=0.01, xanchor="left",
        y=0.97, yanchor="top",
        pad=dict(t=0, b=10),
    )
    t.layout.margin = dict(l=56, r=24, t=56, b=80)
    t.layout.xaxis = dict(
        showgrid=False, zeroline=False, showline=True,
        linecolor=COLORS["line"], linewidth=1,
        ticks="outside", tickcolor=COLORS["line"], ticklen=4,
        tickfont=dict(size=11, color=COLORS["ink3"]),
        title=dict(font=dict(size=12, color=COLORS["ink3"])),
    )
    t.layout.yaxis = dict(
        showgrid=True, gridcolor=COLORS["line2"], gridwidth=1, zeroline=False,
        showline=False,
        tickfont=dict(size=11, color=COLORS["ink3"]),
        title=dict(font=dict(size=12, color=COLORS["ink3"])),
    )
    t.layout.legend = dict(
        orientation="h",
        yanchor="top", y=-0.18,
        xanchor="left", x=0,
        bgcolor="rgba(0,0,0,0)",
        font=dict(size=11, color=COLORS["ink2"]),
        title=dict(text=""),
        itemsizing="constant",
    )
    t.layout.hoverlabel = dict(
        bgcolor=COLORS["ink"], bordercolor=COLORS["ink"],
        font=dict(color="#FFFFFF", size=12, family="Inter, sans-serif"),
    )
    t.layout.coloraxis = dict(
        colorbar=dict(
            outlinewidth=0, thickness=10, len=0.7,
            tickfont=dict(size=10, color=COLORS["ink3"]),
            title=dict(font=dict(size=11, color=COLORS["ink3"])),
        )
    )
    pio.templates["cx_exec"] = t
    pio.templates.default = "cx_exec"


_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    color: {COLORS['ink']};
}}
.stApp {{ background-color: {COLORS['canvas']}; }}

#MainMenu, footer {{ visibility: hidden; }}
header[data-testid="stHeader"] {{ background: transparent; height: 0; }}

.block-container {{
    padding-top: 1.25rem;
    padding-bottom: 3rem;
    max-width: 1480px;
}}

h1, h2, h3, h4, h5, h6, p, span, div, label, li {{
    color: {COLORS['ink']};
}}
h1 {{ font-weight: 700 !important; font-size: 1.55rem !important; letter-spacing: -0.01em; }}
h2 {{ font-weight: 600 !important; font-size: 1.1rem  !important; }}
h3 {{ font-weight: 600 !important; font-size: 1.0rem  !important; }}

/* Sidebar */
section[data-testid="stSidebar"] {{
    background-color: {COLORS['surface']};
    border-right: 1px solid {COLORS['line']};
}}
section[data-testid="stSidebar"] .block-container {{ padding-top: 1.5rem; }}
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] h4 {{
    font-size: .72rem !important;
    text-transform: uppercase; letter-spacing: .10em;
    color: {COLORS['ink3']} !important;
    font-weight: 600 !important;
    margin-top: 1.2rem;
}}
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] div {{
    color: {COLORS['ink2']} !important;
    font-size: 0.85rem;
}}

/* Sidebar nav (multi-page) — force visible link color on both themes */
[data-testid="stSidebarNav"] a,
[data-testid="stSidebarNav"] a span,
[data-testid="stSidebarNav"] a p {{
    color: {COLORS['ink2']} !important;
    font-weight: 500 !important;
    font-size: .88rem !important;
}}
[data-testid="stSidebarNav"] a:hover,
[data-testid="stSidebarNav"] a:hover span {{
    color: {COLORS['navy']} !important;
    background: {COLORS['canvas']};
    border-radius: 4px;
}}
[data-testid="stSidebarNav"] a[aria-current="page"],
[data-testid="stSidebarNav"] a[aria-current="page"] span {{
    color: {COLORS['navy']} !important;
    font-weight: 600 !important;
    background: {COLORS['canvas']};
    border-radius: 4px;
}}

/* File uploader — force light styling */
[data-testid="stFileUploader"] section,
[data-testid="stFileUploaderDropzone"] {{
    background: {COLORS['canvas']} !important;
    border: 1px dashed {COLORS['line']} !important;
    border-radius: 6px !important;
    color: {COLORS['ink2']} !important;
}}
[data-testid="stFileUploader"] section *,
[data-testid="stFileUploaderDropzone"] * {{
    color: {COLORS['ink2']} !important;
}}
[data-testid="stFileUploader"] button,
[data-testid="stFileUploaderDropzone"] button {{
    background: {COLORS['surface']} !important;
    color: {COLORS['ink']} !important;
    border: 1px solid {COLORS['line']} !important;
    border-radius: 4px !important;
    font-weight: 500 !important;
}}
[data-testid="stFileUploader"] button:hover {{
    border-color: {COLORS['navy2']} !important;
    color: {COLORS['navy']} !important;
}}

/* Date input, text input, select, slider — keep clean & light */
[data-testid="stDateInput"] input,
[data-testid="stDateInputField"] input,
[data-baseweb="input"] input,
[data-baseweb="select"] > div,
[data-baseweb="select"] input {{
    background: {COLORS['surface']} !important;
    color: {COLORS['ink']} !important;
    border-color: {COLORS['line']} !important;
    border-radius: 4px !important;
}}
[data-baseweb="select"] div[role="button"] {{
    background: {COLORS['surface']} !important;
    color: {COLORS['ink']} !important;
    border-color: {COLORS['line']} !important;
}}
[data-baseweb="tag"] {{
    background: {COLORS['canvas']} !important;
    color: {COLORS['ink']} !important;
    border: 1px solid {COLORS['line']} !important;
}}

/* Checkbox label color */
[data-testid="stCheckbox"] label,
[data-testid="stCheckbox"] p {{
    color: {COLORS['ink']} !important;
}}

/* Slider track + handle */
[data-testid="stSlider"] [role="slider"] {{
    background: {COLORS['navy']} !important;
    border-color: {COLORS['navy']} !important;
}}
[data-testid="stSlider"] [data-baseweb="slider"] div[style*="background"] {{
    background: {COLORS['line']} !important;
}}

/* Plotly chart frames */
.stPlotlyChart, div[data-testid="stPlotlyChart"] {{
    border: 1px solid {COLORS['line']};
    border-radius: 4px;
    background: {COLORS['surface']};
    padding: 2px;
}}

/* Dataframe frame */
div[data-testid="stDataFrame"] {{
    border: 1px solid {COLORS['line']};
    border-radius: 4px;
    overflow: hidden;
    background: {COLORS['surface']};
}}

/* ---------- Banner ---------- */
.cx-banner {{
    background: {COLORS['surface']};
    border: 1px solid {COLORS['line']};
    border-top: 3px solid {COLORS['navy']};
    padding: 20px 26px 18px 26px;
    border-radius: 4px;
    margin-bottom: 16px;
}}
.cx-banner .cx-eyebrow {{
    font-size: .68rem;
    letter-spacing: .16em;
    text-transform: uppercase;
    color: {COLORS['ink3']};
    font-weight: 600;
}}
.cx-banner .cx-title {{
    font-size: 1.5rem;
    font-weight: 700;
    color: {COLORS['ink']};
    margin-top: 4px;
    line-height: 1.2;
    letter-spacing: -0.01em;
}}
.cx-banner .cx-sub {{
    font-size: .85rem;
    color: {COLORS['ink2']};
    margin-top: 6px;
}}

/* ---------- Filter chips ---------- */
.cx-filter-chip {{
    display: inline-block;
    background: {COLORS['surface']};
    color: {COLORS['ink2']};
    font-size: .72rem;
    padding: 3px 10px;
    border: 1px solid {COLORS['line']};
    border-radius: 999px;
    margin: 0 6px 6px 0;
    font-weight: 500;
}}

/* ---------- KPI cards ---------- */
.cx-kpi-grid {{
    display: grid;
    grid-template-columns: repeat(7, minmax(0, 1fr));
    gap: 10px;
    margin-bottom: 4px;
}}
@media (max-width: 1200px) {{
    .cx-kpi-grid {{ grid-template-columns: repeat(4, 1fr); }}
}}
.cx-kpi {{
    background: {COLORS['surface']};
    border: 1px solid {COLORS['line']};
    border-top: 2px solid var(--accent, {COLORS['navy3']});
    border-radius: 4px;
    padding: 14px 14px 12px 14px;
    min-height: 118px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    transition: border-color .15s ease;
}}
.cx-kpi .cx-label {{
    color: {COLORS['ink3']};
    font-size: .68rem;
    font-weight: 600;
    letter-spacing: .10em;
    text-transform: uppercase;
}}
.cx-kpi .cx-value {{
    color: {COLORS['ink']};
    font-size: 1.65rem;
    font-weight: 700;
    line-height: 1.15;
    font-variant-numeric: tabular-nums;
    letter-spacing: -0.01em;
    margin-top: 2px;
}}
.cx-kpi .cx-sub {{
    color: {COLORS['ink3']};
    font-size: .72rem;
    font-weight: 500;
    font-variant-numeric: tabular-nums;
    margin-top: 4px;
    line-height: 1.35;
}}
.cx-kpi .cx-status {{
    display: inline-flex; align-items: center; gap: 5px;
    font-size: .65rem; font-weight: 600; letter-spacing: .04em;
    color: {COLORS['ink3']};
    margin-right: 8px;
}}
.cx-kpi .cx-dot {{
    width: 7px; height: 7px; border-radius: 50%;
    background: {COLORS['ink4']};
    display: inline-block;
}}
.cx-kpi.status-ok .cx-dot   {{ background: {COLORS['green']}; }}
.cx-kpi.status-warn .cx-dot {{ background: {COLORS['amber']}; }}
.cx-kpi.status-bad .cx-dot  {{ background: {COLORS['red']}; }}
.cx-kpi.status-ok .cx-status   {{ color: {COLORS['green']}; }}
.cx-kpi.status-warn .cx-status {{ color: {COLORS['amber']}; }}
.cx-kpi.status-bad .cx-status  {{ color: {COLORS['red']}; }}

/* ---------- Sections ---------- */
.cx-section-title {{
    color: {COLORS['ink']};
    font-weight: 600;
    font-size: 1.02rem;
    margin: 22px 0 4px 0;
    letter-spacing: -.005em;
}}
.cx-section-sub {{
    color: {COLORS['ink3']};
    font-size: .82rem;
    margin-bottom: 12px;
}}

/* ---------- Custom scorecard table ---------- */
.cx-score {{
    width: 100%;
    border-collapse: collapse;
    background: {COLORS['surface']};
    border: 1px solid {COLORS['line']};
    border-radius: 4px;
    overflow: hidden;
    font-family: 'Inter', sans-serif;
    font-size: .88rem;
    color: {COLORS['ink']};
}}
.cx-score thead th {{
    background: {COLORS['canvas']};
    color: {COLORS['ink3']};
    font-weight: 600;
    font-size: .70rem;
    letter-spacing: .08em;
    text-transform: uppercase;
    padding: 11px 14px;
    border-bottom: 1px solid {COLORS['line']};
    text-align: left;
    white-space: nowrap;
}}
.cx-score tbody td {{
    padding: 11px 14px;
    border-bottom: 1px solid {COLORS['line2']};
    color: {COLORS['ink']};
    font-variant-numeric: tabular-nums;
}}
.cx-score tbody tr:last-child td {{ border-bottom: none; }}
.cx-score tbody tr:hover td {{ background: {COLORS['canvas']}; }}
.cx-score td.team-name {{ font-weight: 600; color: {COLORS['ink']}; }}
.cx-score td.num {{ text-align: right; }}
.cx-score td.tint-ok   {{ background: {COLORS['ok_bg']};   color: {COLORS['ok_text']};   font-weight: 600; }}
.cx-score td.tint-warn {{ background: {COLORS['warn_bg']}; color: {COLORS['warn_text']}; font-weight: 600; }}
.cx-score td.tint-bad  {{ background: {COLORS['bad_bg']};  color: {COLORS['bad_text']};  font-weight: 600; }}

/* ---------- Findings / action plan ---------- */
.cx-finding {{
    border: 1px solid {COLORS['line']};
    border-left: 3px solid {COLORS['ink4']};
    border-radius: 4px;
    background: {COLORS['surface']};
    padding: 12px 14px;
    margin-bottom: 10px;
}}
.cx-finding.high   {{ border-left-color: {COLORS['red']};   }}
.cx-finding.medium {{ border-left-color: {COLORS['amber']}; }}
.cx-finding.low    {{ border-left-color: {COLORS['navy2']}; }}
.cx-finding.win    {{ border-left-color: {COLORS['green']}; }}
.cx-finding .cx-ftitle {{
    font-weight: 600; color: {COLORS['ink']}; font-size: .92rem;
    display: flex; align-items: center; gap: 10px;
}}
.cx-finding .cx-fchip {{
    display: inline-block;
    font-size: .63rem; font-weight: 700; letter-spacing: .08em;
    padding: 2px 7px; border-radius: 3px;
    background: {COLORS['neu_bg']}; color: {COLORS['neu_text']};
}}
.cx-finding.high   .cx-fchip {{ background: {COLORS['bad_bg']};  color: {COLORS['bad_text']}; }}
.cx-finding.medium .cx-fchip {{ background: {COLORS['warn_bg']}; color: {COLORS['warn_text']}; }}
.cx-finding.win    .cx-fchip {{ background: {COLORS['ok_bg']};   color: {COLORS['ok_text']}; }}
.cx-finding .cx-fdetail {{
    color: {COLORS['ink2']}; font-size: .82rem; margin-top: 6px;
}}
.cx-finding .cx-frec {{
    color: {COLORS['ink']}; font-size: .82rem; margin-top: 8px;
    background: {COLORS['canvas']}; padding: 8px 10px; border-radius: 3px;
    border-left: 2px solid {COLORS['navy2']};
}}
.cx-finding .cx-frec b {{ color: {COLORS['navy']}; font-weight: 600; }}

hr {{ border-color: {COLORS['line']}; }}
</style>
"""


def apply_theme() -> None:
    _register_template()
    st.markdown(_CSS, unsafe_allow_html=True)
