"""
OrthoTrack Pro v3.0 — Enhanced Orthopedic Procedure Management System
✦ Excel/CSV Import ✦ Rankings ✦ Leaderboards ✦ Goal Tracking ✦ Enhanced UI
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json, os, io
from datetime import datetime, date, timedelta
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm, mm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph,
    Spacer, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import xlsxwriter

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="OrthoTrack Pro",
    page_icon="🦴",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# DESIGN SYSTEM & CSS — Obsidian Dark × Electric Emerald × Bone White
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Syne:wght@700;800&family=DM+Mono:wght@400;500&display=swap');

:root {
    --bg:       #080C12;
    --surface:  #0E1520;
    --card:     #131C2B;
    --card2:    #192234;
    --border:   #1E2D42;
    --border2:  #263650;
    --emerald:  #00E5A0;
    --emerald2: #00C488;
    --sky:      #38BDF8;
    --amber:    #FFBE0B;
    --coral:    #FF6B6B;
    --violet:   #A78BFA;
    --text:     #E8F0F8;
    --muted:    #5A7291;
    --muted2:   #7A9AB8;
    --gold:     #FFD166;
    --silver:   #B0C4DE;
    --bronze:   #CD9B6A;
}

html, body, [class*="css"] {
    font-family: 'Space Grotesk', sans-serif !important;
    background: var(--bg) !important;
    color: var(--text) !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: var(--surface); }
::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 2px; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { color: var(--muted2) !important; }

.sb-logo-wrap {
    padding: 1.6rem 1.4rem 1.2rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 0.75rem;
}
.sb-logo {
    font-family: 'Syne', sans-serif !important;
    font-size: 1.6rem;
    font-weight: 800;
    letter-spacing: 2px;
    background: linear-gradient(135deg, var(--emerald), var(--sky));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1;
    margin-bottom: 2px;
}
.sb-sub {
    font-size: 0.65rem;
    color: var(--muted) !important;
    letter-spacing: 2px;
    text-transform: uppercase;
    font-family: 'DM Mono', monospace !important;
}

.stat-pill {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 0.65rem 1rem;
    margin: 0.3rem 0;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.stat-pill .sv {
    font-family: 'Syne', sans-serif !important;
    font-size: 1.5rem;
    font-weight: 800;
    color: var(--emerald) !important;
    line-height: 1;
}
.stat-pill .sl {
    font-size: 0.64rem;
    color: var(--muted) !important;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    font-family: 'DM Mono', monospace !important;
    text-align: right;
    max-width: 90px;
}

[data-testid="stSidebar"] .stRadio label {
    font-size: 0.85rem !important;
    font-weight: 600 !important;
    padding: 0.45rem 0.3rem !important;
    color: var(--muted2) !important;
    font-family: 'Space Grotesk', sans-serif !important;
}

/* ── Main background texture ── */
.main .block-container {
    background: var(--bg) !important;
    padding-top: 1.5rem !important;
}

/* ── Page header ── */
.ph {
    background: linear-gradient(135deg, var(--surface) 0%, #0B1829 60%, #060E18 100%);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 2.2rem 2.8rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}
.ph::after {
    content: '';
    position: absolute;
    right: -80px; top: -80px;
    width: 300px; height: 300px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(0,229,160,0.08) 0%, transparent 65%);
    pointer-events: none;
}
.ph::before {
    content: '';
    position: absolute;
    left: 0; bottom: 0; right: 0; top: 0;
    background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%2300E5A0' fill-opacity='0.02'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
    pointer-events: none;
}
.ph-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(0,229,160,0.1);
    border: 1px solid rgba(0,229,160,0.3);
    color: var(--emerald) !important;
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    padding: 0.3rem 0.9rem;
    border-radius: 20px;
    margin-bottom: 0.8rem;
    font-family: 'DM Mono', monospace;
    position: relative;
    z-index: 1;
}
.ph h1 {
    font-family: 'Syne', sans-serif !important;
    font-size: 2.8rem !important;
    font-weight: 800 !important;
    letter-spacing: 2px !important;
    background: linear-gradient(135deg, #ffffff 0%, var(--emerald) 100%);
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
    margin: 0 0 0.4rem !important;
    position: relative;
    z-index: 1;
}
.ph p {
    color: var(--muted2) !important;
    font-size: 0.88rem !important;
    margin: 0 !important;
    position: relative;
    z-index: 1;
}

/* ── Cards ── */
.kpi-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 1.4rem 1.6rem;
    position: relative;
    overflow: hidden;
    transition: border-color 0.2s;
}
.kpi-card:hover { border-color: var(--border2); }
.kpi-card .kv {
    font-family: 'Syne', sans-serif;
    font-size: 2.4rem;
    font-weight: 800;
    color: var(--text);
    line-height: 1;
    margin-bottom: 4px;
}
.kpi-card .kl {
    font-size: 0.7rem;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 1.5px;
    font-family: 'DM Mono', monospace;
}
.kpi-card .kdelta {
    font-size: 0.75rem;
    font-weight: 600;
    margin-top: 6px;
}
.kpi-card .accent-bar {
    position: absolute;
    top: 0; left: 0;
    width: 100%; height: 3px;
    border-radius: 16px 16px 0 0;
}

/* ── Rankings / Leaderboard ── */
.rank-row {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 0.75rem 1rem;
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px;
    margin-bottom: 0.5rem;
    transition: border-color 0.2s, transform 0.15s;
}
.rank-row:hover { border-color: var(--border2); transform: translateX(2px); }
.rank-num {
    font-family: 'Syne', sans-serif;
    font-size: 1.1rem;
    font-weight: 800;
    min-width: 28px;
    text-align: center;
}
.rank-name { font-weight: 600; font-size: 0.92rem; flex: 1; }
.rank-val {
    font-family: 'DM Mono', monospace;
    font-size: 0.88rem;
    font-weight: 500;
    color: var(--emerald);
}
.rank-bar-wrap { flex: 1; background: var(--surface); border-radius: 4px; height: 6px; }
.rank-bar { height: 6px; border-radius: 4px; }

/* ── Goal progress ── */
.goal-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 0.75rem;
}
.goal-title { font-weight: 700; font-size: 0.95rem; margin-bottom: 6px; }
.goal-sub { font-size: 0.72rem; color: var(--muted); font-family: 'DM Mono', monospace; margin-bottom: 10px; }
.goal-track-wrap { background: var(--surface); border-radius: 6px; height: 10px; margin-bottom: 6px; }
.goal-track { height: 10px; border-radius: 6px; }
.goal-pct { font-family: 'Syne', sans-serif; font-size: 1.3rem; font-weight: 800; }

/* ── Record field ── */
.rf {
    margin-bottom: 0.5rem;
    padding: 0.75rem 1rem;
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 10px;
}
.rf .rl {
    font-size: 0.64rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    color: var(--muted);
    margin-bottom: 4px;
    font-family: 'DM Mono', monospace;
}
.rf .rv { font-size: 0.9rem; color: var(--text); font-weight: 500; }

/* ── Chip ── */
.chip {
    display: inline-block;
    background: rgba(0,229,160,0.1);
    color: var(--emerald);
    font-size: 0.7rem;
    font-weight: 600;
    padding: 0.22rem 0.65rem;
    border-radius: 20px;
    border: 1px solid rgba(0,229,160,0.25);
    margin: 0.2rem 0.15rem 0.2rem 0;
}

/* ── Section label ── */
.sec-lbl {
    font-size: 0.65rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 2.5px;
    color: var(--emerald);
    margin-bottom: 0.75rem;
    font-family: 'DM Mono', monospace;
}

/* ── Form sections ── */
.fs {
    background: rgba(0,229,160,0.05);
    border-left: 3px solid var(--emerald);
    border-radius: 0 8px 8px 0;
    padding: 0.5rem 0.9rem 0.35rem;
    margin: 1.2rem 0 0.5rem;
    font-size: 0.65rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: var(--emerald);
    font-family: 'DM Mono', monospace;
}
.fs.fst { border-left-color: var(--sky); color: var(--sky); background: rgba(56,189,248,0.05); }
.fs.fsa { border-left-color: var(--amber); color: var(--amber); background: rgba(255,190,11,0.05); }

/* ── Download card ── */
.dlc {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 2rem;
    text-align: center;
}
.dlc .di { font-size: 2.8rem; margin-bottom: 0.5rem; }
.dlc .dt { font-weight: 700; font-size: 1rem; color: var(--text); margin-bottom: 0.3rem; }
.dlc .dd { font-size: 0.8rem; color: var(--muted); }

/* ── Upload zone ── */
.upload-zone {
    background: var(--card);
    border: 2px dashed var(--border2);
    border-radius: 20px;
    padding: 2.5rem;
    text-align: center;
    transition: border-color 0.2s;
}
.upload-zone:hover { border-color: var(--emerald); }

/* ── Import status ── */
.import-success {
    background: rgba(0,229,160,0.08);
    border: 1px solid rgba(0,229,160,0.3);
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 1rem;
}
.import-warn {
    background: rgba(255,190,11,0.08);
    border: 1px solid rgba(255,190,11,0.3);
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 1rem;
}

/* ── Streamlit input overrides ── */
.stTextInput input, .stTextArea textarea, .stNumberInput input {
    background: var(--card) !important;
    border: 1px solid var(--border2) !important;
    border-radius: 10px !important;
    color: var(--text) !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 0.9rem !important;
}
.stTextInput input:focus, .stTextArea textarea:focus, .stNumberInput input:focus {
    border-color: var(--emerald) !important;
    box-shadow: 0 0 0 3px rgba(0,229,160,0.12) !important;
}
.stTextInput label, .stTextArea label, .stSelectbox label,
.stMultiSelect label, .stDateInput label, .stNumberInput label {
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    color: var(--muted2) !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
    font-family: 'DM Mono', monospace !important;
}
div[data-baseweb="select"] > div {
    background: var(--card) !important;
    border-color: var(--border2) !important;
    border-radius: 10px !important;
}
div[data-baseweb="select"] span { color: var(--text) !important; }

/* ── Buttons ── */
.stButton > button {
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 700 !important;
    border-radius: 10px !important;
    transition: all 0.2s !important;
    font-size: 0.88rem !important;
}
.stButton > button:hover { transform: translateY(-2px) !important; }
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, var(--emerald), var(--emerald2)) !important;
    color: #080C12 !important;
    border: none !important;
    box-shadow: 0 4px 20px rgba(0,229,160,0.3) !important;
}
.stButton > button[kind="primary"]:hover {
    box-shadow: 0 6px 28px rgba(0,229,160,0.45) !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid var(--border) !important;
    gap: 0.5rem !important;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    padding: 0.75rem 1.2rem !important;
    color: var(--muted) !important;
    border-radius: 8px 8px 0 0 !important;
}
.stTabs [aria-selected="true"] {
    color: var(--emerald) !important;
    border-bottom: 2px solid var(--emerald) !important;
    background: rgba(0,229,160,0.05) !important;
}

/* ── Metrics ── */
[data-testid="metric-container"] {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    padding: 1rem 1.2rem !important;
}
[data-testid="metric-container"] label {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.65rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 1.5px !important;
    color: var(--muted) !important;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-family: 'Syne', sans-serif !important;
    font-size: 2rem !important;
    font-weight: 800 !important;
    color: var(--text) !important;
}
[data-testid="stMetricDelta"] { font-size: 0.78rem !important; }

/* ── Dataframe ── */
[data-testid="stDataFrame"] {
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    overflow: hidden !important;
}

/* ── Expander ── */
details {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    padding: 0.2rem 0.8rem !important;
}
summary {
    font-size: 0.88rem !important;
    font-weight: 600 !important;
    color: var(--text) !important;
}

/* ── Info / Success / Warning ── */
.stSuccess, .stInfo, .stWarning, .stError {
    border-radius: 10px !important;
}

/* ── Trophy rows ── */
.trophy-1 { color: var(--gold) !important; }
.trophy-2 { color: var(--silver) !important; }
.trophy-3 { color: var(--bronze) !important; }

/* ── Divider ── */
hr { border-color: var(--border) !important; margin: 1.5rem 0 !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────
DATA_FILE   = "procedures.json"
GOALS_FILE  = "rep_goals.json"

REPS = sorted([
    "James Mwangi","Faith Otieno","Brian Koech","Grace Auma","Dennis Kiplangat",
    "Sharon Wanjiku","Paul Mutua","Lydia Chebet","Moses Odhiambo","Caroline Njeri"
])
FACILITIES = sorted([
    "Moi Teaching & Referral Hospital","Kenyatta National Hospital","Aga Khan Hospital Nairobi",
    "MP Shah Hospital","Nairobi Hospital","AAR Hospital","Coast General Hospital",
    "Eldoret Hospital","Kisumu County Referral","Nakuru Level 5 Hospital",
    "Thika Level 5 Hospital","Mombasa Hospital","Other"
])
REGIONS = ["East Africa","West Africa","North Africa","Southern Africa","Central Africa","Middle East","Europe","Other"]
SURGEONS = sorted([
    "Dr. A. Kimani","Dr. B. Otieno","Dr. C. Waweru","Dr. D. Mutai","Dr. E. Achieng",
    "Dr. F. Njenga","Dr. G. Kipchoge","Dr. H. Omondi","Dr. I. Wambua","Dr. J. Chege",
    "Dr. K. Maina","Dr. L. Rotich","Dr. M. Abdi","Dr. N. Kamau","Dr. O. Simiyu","Other"
])
PROCEDURES = sorted([
    "Total Hip Replacement","Total Knee Replacement","Partial Knee Replacement",
    "Shoulder Arthroplasty","Spinal Fusion L4-L5","Spinal Fusion L5-S1","Tibial Nail Fixation",
    "Femoral Nail Fixation","DHS Plate Fixation","Locking Plate Fixation","ACL Reconstruction",
    "Revision Hip Replacement","Revision Knee Replacement","Humeral Nail Fixation",
    "Ankle Replacement","External Fixator Application","Proximal Femur Replacement",
    "Wrist Arthroplasty","Other"
])
IMPLANTS = sorted([
    "Total Hip Replacement System","Total Knee Replacement System","Partial Knee System",
    "Shoulder Arthroplasty System","Spinal Fusion Cage","Pedicle Screws","Titanium Tibial Nail",
    "Femoral Intramedullary Nail","DHS Plate & Screw","Locking Compression Plate",
    "ACL Graft & Fixation","Revision Hip Stem","Revision Tibial Component","Humeral Nail",
    "Total Ankle Replacement","External Fixator Frame","Proximal Femoral Prosthesis",
    "Bone Cement","Augmentation Block","Trial Components","Other"
])
COLORS = ["#00E5A0","#38BDF8","#FFBE0B","#FF6B6B","#A78BFA","#06B6D4","#10B981","#F97316","#EC4899","#6366F1"]

# Chart paper/plot bg for dark theme
CHART_BASE = dict(
    paper_bgcolor="#0E1520",
    plot_bgcolor="#080C12",
    font=dict(family="Space Grotesk", color="#E8F0F8"),
    title_font=dict(family="Space Grotesk", size=12, color="#5A7291"),
    margin=dict(t=44, b=28, l=20, r=16),
    legend=dict(font=dict(size=11), bgcolor="rgba(0,0,0,0)"),
)

# ─────────────────────────────────────────────────────────────────────────────
# DATA LAYER
# ─────────────────────────────────────────────────────────────────────────────
def load_data() -> list:
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f: return json.load(f)
    return []

def save_data(data: list):
    with open(DATA_FILE, "w") as f: json.dump(data, f, indent=2, default=str)

def load_goals() -> dict:
    if os.path.exists(GOALS_FILE):
        with open(GOALS_FILE, "r") as f: return json.load(f)
    return {}

def save_goals(goals: dict):
    with open(GOALS_FILE, "w") as f: json.dump(goals, f, indent=2)

@st.cache_data(ttl=2)
def get_df() -> pd.DataFrame:
    data = load_data()
    if not data: return pd.DataFrame()
    df = pd.DataFrame(data)
    df["date"]    = pd.to_datetime(df["date"])
    df["month"]   = df["date"].dt.to_period("M").astype(str)
    df["year"]    = df["date"].dt.year
    df["quarter"] = df["date"].dt.to_period("Q").astype(str)
    df["week"]    = df["date"].dt.isocalendar().week.astype(int)
    return df

def bust(): get_df.clear()

def next_inv(data: list) -> str:
    yr = datetime.now().year
    nums = []
    for r in data:
        inv = r.get("invoice", "")
        if str(yr) in inv:
            try: nums.append(int(inv.split("-")[-1]))
            except: pass
    return f"INV-{yr}-{(max(nums)+1 if nums else 1):04d}"

def sc(fig, title=""):
    fig.update_layout(**CHART_BASE, title=dict(text=title))
    fig.update_xaxes(showgrid=False, linecolor="#1E2D42", tickfont=dict(size=10), color="#5A7291")
    fig.update_yaxes(gridcolor="#0E1520", linecolor="#1E2D42", tickfont=dict(size=10), color="#5A7291")
    return fig

def rank_icon(i):
    if i == 0: return "🥇"
    if i == 1: return "🥈"
    if i == 2: return "🥉"
    return f"#{i+1}"

def rank_color(i):
    if i == 0: return "var(--gold)"
    if i == 1: return "var(--silver)"
    if i == 2: return "var(--bronze)"
    return "var(--muted2)"

# ─────────────────────────────────────────────────────────────────────────────
# EXCEL IMPORT ENGINE
# ─────────────────────────────────────────────────────────────────────────────
IMPORT_COLUMN_MAP = {
    # Common aliases → canonical field names
    "date": "date", "procedure date": "date", "surgery date": "date",
    "invoice": "invoice", "invoice number": "invoice", "invoice #": "invoice", "inv no": "invoice",
    "rep": "rep", "sales rep": "rep", "representative": "rep", "rep name": "rep",
    "facility": "facility", "hospital": "facility", "institution": "facility",
    "region": "region", "territory": "region", "area": "region",
    "surgeon": "surgeon", "doctor": "surgeon", "physician": "surgeon",
    "procedure": "procedure", "surgery": "procedure", "procedure type": "procedure",
    "implant": "implants", "implants": "implants", "implants used": "implants",
    "device": "implants", "devices": "implants",
    "challenges": "challenges", "challenge": "challenges", "complications": "challenges",
    "feedback": "feedback", "notes": "feedback", "comments": "feedback", "outcome": "feedback",
}

def parse_import_file(uploaded_file) -> tuple[pd.DataFrame, list]:
    """Parse uploaded Excel/CSV, auto-map columns, return (df, warnings)."""
    warnings = []
    fname = uploaded_file.name.lower()
    try:
        if fname.endswith(".csv"):
            raw = pd.read_csv(uploaded_file)
        elif fname.endswith((".xlsx", ".xls")):
            # Try to find the right sheet
            xf = pd.ExcelFile(uploaded_file)
            sheet = xf.sheet_names[0]
            for s in xf.sheet_names:
                if any(k in s.lower() for k in ["procedure","log","data","main"]):
                    sheet = s; break
            raw = pd.read_excel(uploaded_file, sheet_name=sheet)
            if len(xf.sheet_names) > 1:
                warnings.append(f"Multiple sheets detected — imported from '{sheet}'.")
        else:
            return None, ["Unsupported file type. Upload .xlsx, .xls, or .csv"]
    except Exception as e:
        return None, [f"Failed to read file: {e}"]

    # Normalise column names
    raw.columns = [str(c).strip().lower() for c in raw.columns]
    mapped = {}
    for col in raw.columns:
        canon = IMPORT_COLUMN_MAP.get(col)
        if canon:
            mapped[col] = canon

    if not mapped:
        return None, ["Could not match any columns. Expected headers like: date, invoice, rep, facility, region, surgeon, procedure, implants."]

    df = raw.rename(columns=mapped)
    missing_required = [f for f in ["date","rep","procedure"] if f not in df.columns]
    if missing_required:
        warnings.append(f"Missing recommended columns: {', '.join(missing_required)}")

    # Coerce date
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        bad_dates = df["date"].isna().sum()
        if bad_dates: warnings.append(f"{bad_dates} rows had unparseable dates and were set to today.")
        df["date"] = df["date"].fillna(pd.Timestamp.now())

    # Fill missing optionals
    for col in ["invoice","rep","facility","region","surgeon","procedure","challenges","feedback"]:
        if col not in df.columns: df[col] = ""

    # Implants — ensure it's a string (will be converted to list on ingest)
    if "implants" not in df.columns:
        df["implants"] = ""

    df = df.dropna(how="all")
    return df, warnings


def import_records(import_df: pd.DataFrame, existing: list, overwrite_dup: bool = False) -> tuple[int, int, int]:
    """Merge imported df into existing records. Returns (added, skipped, updated)."""
    existing_invs = {r.get("invoice","").strip(): i for i, r in enumerate(existing)}
    added = skipped = updated = 0

    for _, row in import_df.iterrows():
        inv = str(row.get("invoice","")).strip()
        if not inv or inv == "nan":
            inv = next_inv(existing)

        implants_raw = row.get("implants","")
        if isinstance(implants_raw, list):
            implants = implants_raw
        else:
            implants = [x.strip() for x in str(implants_raw).split(",") if x.strip() and x.strip() != "nan"]

        dt = row.get("date", pd.Timestamp.now())
        if hasattr(dt, "strftime"): dt = dt.strftime("%Y-%m-%d")

        rec = {
            "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
            "date": str(dt)[:10],
            "invoice": inv,
            "rep": str(row.get("rep","")).strip() or "Unknown",
            "facility": str(row.get("facility","")).strip() or "Unknown",
            "region": str(row.get("region","")).strip() or "Other",
            "surgeon": str(row.get("surgeon","")).strip() or "Unknown",
            "procedure": str(row.get("procedure","")).strip() or "Unknown",
            "implants": implants,
            "challenges": str(row.get("challenges","")).strip() or "None",
            "feedback": str(row.get("feedback","")).strip() or "—",
            "logged_at": datetime.now().isoformat(),
            "source": "import",
        }

        if inv in existing_invs:
            if overwrite_dup:
                existing[existing_invs[inv]] = rec
                updated += 1
            else:
                skipped += 1
        else:
            existing.append(rec)
            existing_invs[inv] = len(existing) - 1
            added += 1

    return added, skipped, updated

# ─────────────────────────────────────────────────────────────────────────────
# PDF
# ─────────────────────────────────────────────────────────────────────────────
def build_pdf(df: pd.DataFrame, title: str, subtitle: str = "") -> io.BytesIO:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            leftMargin=1.8*cm, rightMargin=1.8*cm,
                            topMargin=2*cm, bottomMargin=1.8*cm)
    S = getSampleStyleSheet()
    ink    = colors.HexColor("#0D1B2A")
    emerald= colors.HexColor("#00E5A0")
    navy   = colors.HexColor("#0E1520")
    cream  = colors.HexColor("#F8F6F1")
    border = colors.HexColor("#E2E8F0")
    muted  = colors.HexColor("#64748B")
    story  = []
    story.append(Paragraph("ORTHOTRACK PRO",
        ParagraphStyle("Br", fontName="Helvetica-Bold", fontSize=20,
                       textColor=emerald, spaceAfter=2, letterSpacing=4)))
    story.append(Paragraph(title,
        ParagraphStyle("Ti", fontName="Helvetica-Bold", fontSize=14,
                       textColor=ink, spaceAfter=4)))
    if subtitle:
        story.append(Paragraph(subtitle,
            ParagraphStyle("Su", fontName="Helvetica", fontSize=9, textColor=muted, spaceAfter=2)))
    story.append(Paragraph(
        f"Generated {datetime.now().strftime('%d %B %Y  ·  %H:%M')}   ·   {len(df)} record(s)",
        ParagraphStyle("Me", fontName="Helvetica", fontSize=8, textColor=muted, spaceAfter=8)))
    story.append(HRFlowable(width="100%", thickness=2, color=emerald, spaceAfter=12))
    story.append(Paragraph("SUMMARY",
        ParagraphStyle("SH", fontName="Helvetica-Bold", fontSize=7,
                       textColor=emerald, spaceBefore=2, spaceAfter=6, letterSpacing=2)))
    nf = df["facility"].nunique() if "facility" in df.columns else 0
    ns = df["surgeon"].nunique()  if "surgeon"  in df.columns else 0
    nr = df["rep"].nunique()      if "rep"      in df.columns else 0
    ng = df["region"].nunique()   if "region"   in df.columns else 0
    sd = [["PROCEDURES","FACILITIES","SURGEONS","REPS","REGIONS"],
          [str(len(df)), str(nf), str(ns), str(nr), str(ng)]]
    st_ = Table(sd, colWidths=[2.8*cm]*5)
    st_.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),ink),("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,0),7),
        ("BACKGROUND",(0,1),(-1,1),cream),
        ("FONTNAME",(0,1),(-1,1),"Helvetica-Bold"),("FONTSIZE",(0,1),(-1,1),14),
        ("TEXTCOLOR",(0,1),(-1,1),ink),
        ("ALIGN",(0,0),(-1,-1),"CENTER"),("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ("TOPPADDING",(0,0),(-1,-1),7),("BOTTOMPADDING",(0,0),(-1,-1),7),
        ("BOX",(0,0),(-1,-1),.5,border),("INNERGRID",(0,0),(-1,-1),.5,border),
    ]))
    story.append(st_)
    story.append(Spacer(1,14))
    story.append(Paragraph("PROCEDURE LOG",
        ParagraphStyle("SH2", fontName="Helvetica-Bold", fontSize=7,
                       textColor=emerald, spaceBefore=4, spaceAfter=6, letterSpacing=2)))
    wanted  = ["date","invoice","rep","facility","region","surgeon","procedure","implants"]
    present = [c for c in wanted if c in df.columns]
    cw_map  = {"date":10*mm,"invoice":18*mm,"rep":22*mm,"facility":27*mm,
               "region":17*mm,"surgeon":22*mm,"procedure":26*mm,"implants":28*mm}
    cwidths  = [cw_map.get(c,20*mm) for c in present]
    rows    = [[c.upper() for c in present]]
    for _, row in df.sort_values("date", ascending=False).head(200).iterrows():
        r = []
        for c in present:
            v = row.get(c,"")
            if c == "date":
                try: v = pd.to_datetime(v).strftime("%d %b %Y")
                except: pass
            elif c == "implants" and isinstance(v, list): v = ", ".join(v)
            v = str(v)
            if len(v) > 26: v = v[:24]+"…"
            r.append(v)
        rows.append(r)
    t = Table(rows, colWidths=cwidths, repeatRows=1)
    rbgs = []
    for i in range(1, len(rows)):
        bg = colors.white if i%2 else colors.HexColor("#F8FAFC")
        rbgs.append(("BACKGROUND",(0,i),(-1,i),bg))
    t.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),navy),("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,-1),7),
        ("FONTNAME",(0,1),(-1,-1),"Helvetica"),("TEXTCOLOR",(0,1),(-1,-1),ink),
        ("ALIGN",(0,0),(-1,-1),"LEFT"),("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),
        ("LEFTPADDING",(0,0),(-1,-1),5),
        ("BOX",(0,0),(-1,-1),.5,border),("INNERGRID",(0,0),(-1,-1),.3,border),
        *rbgs,
    ]))
    story.append(t)
    if len(df) > 200:
        story.append(Spacer(1,8))
        story.append(Paragraph(f"… and {len(df)-200} more. Download Excel/CSV for full dataset.",
            ParagraphStyle("N", fontName="Helvetica-Oblique", fontSize=8, textColor=muted)))
    doc.build(story)
    buf.seek(0)
    return buf

# ─────────────────────────────────────────────────────────────────────────────
# EXCEL EXPORT
# ─────────────────────────────────────────────────────────────────────────────
def build_excel(df: pd.DataFrame, title: str) -> io.BytesIO:
    buf = io.BytesIO()
    wb  = xlsxwriter.Workbook(buf, {"in_memory": True})
    def f(**kw): return wb.add_format({**kw, "font_name": "Calibri"})
    f_title = f(bold=True, font_size=16, font_color="#0D1B2A")
    f_sub   = f(font_size=9, font_color="#64748B", italic=True)
    f_hdr   = f(bold=True, font_size=9, font_color="white", bg_color="#0E1520",
                border=1, border_color="#CBD5E1", align="center", valign="vcenter", text_wrap=True)
    f_cell  = f(font_size=9, border=1, border_color="#E2E8F0", valign="vcenter")
    f_alt   = f(font_size=9, border=1, border_color="#E2E8F0", bg_color="#F8F6F1", valign="vcenter")
    f_sv    = f(bold=True, font_size=9, font_color="white", bg_color="#0D1B2A",
                border=1, border_color="#CBD5E1", align="center", valign="vcenter")
    f_val   = f(bold=True, font_size=18, font_color="#00C488", bg_color="#F0FDF9",
                border=1, border_color="#6EE7B7", align="center", valign="vcenter")
    f_dt    = f(font_size=9, border=1, border_color="#E2E8F0", num_format="dd mmm yyyy", valign="vcenter")
    f_dta   = f(font_size=9, border=1, border_color="#E2E8F0", bg_color="#F8F6F1",
                num_format="dd mmm yyyy", valign="vcenter")

    ws = wb.add_worksheet("Procedures")
    ws.set_zoom(90); ws.freeze_panes(5,0)
    ws.merge_range("A1:J1", "OrthoTrack Pro — "+title, f_title)
    ws.write("A2", f"Exported {datetime.now().strftime('%d %B %Y  ·  %H:%M')}   ·   {len(df)} records", f_sub)
    ws.set_row(0,26); ws.set_row(1,14); ws.set_row(2,6); ws.set_row(3,20)
    cols  = [c for c in ["date","invoice","rep","facility","region","surgeon","procedure","implants","challenges","feedback"] if c in df.columns]
    cw    = {"date":13,"invoice":16,"rep":22,"facility":30,"region":16,"surgeon":22,
             "procedure":28,"implants":35,"challenges":40,"feedback":40}
    for ci,col in enumerate(cols):
        ws.write(3, ci, col.upper(), f_hdr); ws.set_column(ci, ci, cw.get(col,18))
    for ri,(_, row) in enumerate(df.sort_values("date", ascending=False).iterrows()):
        alt = ri%2==1; ws.set_row(ri+4, 16)
        for ci,col in enumerate(cols):
            v = row.get(col,"")
            if isinstance(v,list): v = ", ".join(v)
            if not isinstance(v,str) and pd.isna(v): v=""
            cf = f_alt if alt else f_cell
            if col == "date":
                try:
                    ws.write_datetime(ri+4, ci, pd.to_datetime(v).to_pydatetime(), f_dta if alt else f_dt); continue
                except: pass
            ws.write(ri+4, ci, str(v), cf)

    ws2 = wb.add_worksheet("Summary")
    ws2.set_column("A:A",28); ws2.set_column("B:B",16); ws2.set_zoom(95)
    ws2.merge_range("A1:B1","OrthoTrack Pro — Summary Statistics", f_title)
    ws2.merge_range("A2:B2", f"Generated {datetime.now().strftime('%d %B %Y')}", f_sub)
    ws2.set_row(0,26); ws2.set_row(1,14); ws2.set_row(2,6)
    stats=[("Total Procedures", len(df)),
           ("Unique Facilities", df["facility"].nunique() if "facility" in df.columns else 0),
           ("Unique Surgeons",   df["surgeon"].nunique()  if "surgeon"  in df.columns else 0),
           ("Unique Reps",       df["rep"].nunique()       if "rep"      in df.columns else 0),
           ("Regions Covered",   df["region"].nunique()    if "region"   in df.columns else 0)]
    for i,(k,v) in enumerate(stats):
        ws2.set_row(i+3,26); ws2.write(i+3,0,k,f_sv); ws2.write(i+3,1,v,f_val)
    ro = len(stats)+5
    f_sec = f(bold=True, font_size=8, font_color="#00C488", bg_color="#F0FDF9", border=1, border_color="#6EE7B7")
    ws2.merge_range(ro,0,ro,1,"PROCEDURES BY REP", f_sec)
    if "rep" in df.columns:
        for i,(rep,cnt) in enumerate(df["rep"].value_counts().items()):
            ws2.set_row(ro+1+i,16)
            ws2.write(ro+1+i,0,rep, f_alt if i%2 else f_cell)
            ws2.write(ro+1+i,1,cnt, f_alt if i%2 else f_cell)

    ws3 = wb.add_worksheet("By Region")
    ws3.set_column("A:A",24); ws3.set_column("B:B",14); ws3.set_zoom(95)
    ws3.merge_range("A1:B1","Procedures by Region", f_title)
    ws3.set_row(0,24); ws3.set_row(1,6); ws3.set_row(2,20)
    ws3.write(2,0,"REGION",f_sv); ws3.write(2,1,"PROCEDURES",f_sv)
    if "region" in df.columns:
        for i,(reg,cnt) in enumerate(df["region"].value_counts().items()):
            ws3.set_row(i+3,16)
            ws3.write(i+3,0,reg, f_alt if i%2 else f_cell)
            ws3.write(i+3,1,cnt, f_alt if i%2 else f_cell)

    wb.close(); buf.seek(0)
    return buf

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sb-logo-wrap">
        <div class="sb-logo">🦴 ORTHOTRACK</div>
        <div class="sb-sub">Pro · v3.0 · Procedure Intelligence</div>
    </div>""", unsafe_allow_html=True)

    page = st.radio("nav", [
        "📊  Dashboard",
        "➕  Add Procedure",
        "📥  Import Data",
        "📋  Procedure Log",
        "🏆  Rankings",
        "📈  Analytics",
        "⬇️  Reports"
    ], label_visibility="collapsed")

    dfs = get_df()
    if not dfs.empty:
        st.markdown("<div style='margin:12px 0 6px;font-size:.6rem;color:#1E2D42;letter-spacing:2px;padding:0 .2rem'>LIVE STATS</div>",
                    unsafe_allow_html=True)
        now_m = datetime.now()
        this_mo = dfs[(dfs["date"].dt.month==now_m.month)&(dfs["date"].dt.year==now_m.year)]
        last_mo_start = (now_m.replace(day=1) - timedelta(days=1)).replace(day=1)
        last_mo = dfs[(dfs["date"].dt.month==last_mo_start.month)&(dfs["date"].dt.year==last_mo_start.year)]
        mo_delta = len(this_mo) - len(last_mo)
        delta_sym = "▲" if mo_delta >= 0 else "▼"
        for val, lbl in [
            (len(dfs),  "Total Procedures"),
            (f"{len(this_mo)} ({delta_sym}{abs(mo_delta)})", "This Month"),
            (dfs["rep"].nunique() if "rep" in dfs.columns else 0, "Active Reps"),
            (dfs["facility"].nunique() if "facility" in dfs.columns else 0, "Facilities"),
        ]:
            st.markdown(f'<div class="stat-pill"><div class="sv">{val}</div><div class="sl">{lbl}</div></div>',
                        unsafe_allow_html=True)

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:.58rem;color:#1E2D42;letter-spacing:1px;padding:0 .2rem;text-align:center'>OrthoTrack Pro · v3.0</div>",
                unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# ██  DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────
if page == "📊  Dashboard":
    st.markdown("""
    <div class="ph">
        <div class="ph-badge">● LIVE DASHBOARD</div>
        <h1>PROCEDURE INTELLIGENCE</h1>
        <p>Real-time orthopedic procedure tracking · Rep performance · Regional coverage · Implant analytics</p>
    </div>""", unsafe_allow_html=True)

    df = get_df()
    if df.empty:
        st.info("🦴 No procedures yet. Head to **Add Procedure** or **Import Data** to get started!")
        st.stop()

    now = datetime.now()
    this_mo = df[(df["date"].dt.month==now.month)&(df["date"].dt.year==now.year)]
    last_mo_s = (now.replace(day=1) - timedelta(days=1)).replace(day=1)
    last_mo = df[(df["date"].dt.month==last_mo_s.month)&(df["date"].dt.year==last_mo_s.year)]

    # KPI cards
    c1,c2,c3,c4,c5 = st.columns(5)
    kpis = [
        (c1, len(df), "Total Procedures", f"+{len(this_mo)} this month", "var(--emerald)"),
        (c2, len(this_mo), "This Month", f"{len(this_mo)-len(last_mo):+d} vs last month", "var(--sky)"),
        (c3, df["facility"].nunique() if "facility" in df.columns else 0, "Facilities", "covered", "var(--amber)"),
        (c4, df["surgeon"].nunique() if "surgeon" in df.columns else 0, "Surgeons", "engaged", "var(--violet)"),
        (c5, df["rep"].nunique() if "rep" in df.columns else 0, "Active Reps", "in field", "var(--coral)"),
    ]
    for col, val, lbl, delta, color in kpis:
        with col:
            st.markdown(f"""<div class="kpi-card">
                <div class="accent-bar" style="background:{color}"></div>
                <div class="kv">{val}</div>
                <div class="kl">{lbl}</div>
                <div class="kdelta" style="color:{color}">{delta}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # Row 1: Volume + Top Rep spotlight
    col1, col2 = st.columns([3,2])
    with col1:
        monthly = df.groupby("month").size().reset_index(name="Count")
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=monthly["month"], y=monthly["Count"],
            marker=dict(color=monthly["Count"],
                        colorscale=[[0,"#0E2D1A"],[0.5,"#00A870"],[1,"#00E5A0"]],
                        showscale=False, line=dict(width=0)),
            hovertemplate="%{x}<br><b>%{y} procedures</b><extra></extra>",
            name="Volume"
        ))
        fig.add_trace(go.Scatter(
            x=monthly["month"], y=monthly["Count"], mode="lines",
            line=dict(color="#38BDF8", width=2, dash="dot"),
            hoverinfo="skip", name="Trend"
        ))
        sc(fig, "Monthly Procedure Volume"); fig.update_layout(showlegend=False, height=280, bargap=0.25)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("<div class='sec-lbl'>Top Rep Spotlight</div>", unsafe_allow_html=True)
        if "rep" in df.columns:
            top_rep = df["rep"].value_counts().index[0]
            top_rep_count = df["rep"].value_counts().iloc[0]
            rep_fac = df[df["rep"]==top_rep]["facility"].nunique() if "facility" in df.columns else 0
            rep_reg = df[df["rep"]==top_rep]["region"].nunique() if "region" in df.columns else 0
            rep_surg = df[df["rep"]==top_rep]["surgeon"].nunique() if "surgeon" in df.columns else 0
            st.markdown(f"""<div style="background:linear-gradient(135deg,rgba(0,229,160,0.08),rgba(56,189,248,0.05));
                border:1px solid rgba(0,229,160,0.2);border-radius:16px;padding:1.5rem;text-align:center;margin-bottom:1rem">
                <div style="font-size:2rem">🥇</div>
                <div style="font-family:'Syne',sans-serif;font-size:1.3rem;font-weight:800;color:var(--emerald);margin-bottom:4px">{top_rep}</div>
                <div style="font-size:2.2rem;font-family:'Syne',sans-serif;font-weight:800;color:white">{top_rep_count}</div>
                <div style="font-size:0.7rem;color:var(--muted);letter-spacing:1px;text-transform:uppercase;font-family:'DM Mono',monospace">procedures all-time</div>
                <div style="display:flex;justify-content:center;gap:20px;margin-top:12px">
                    <div><div style="font-size:1.2rem;font-family:'Syne',sans-serif;font-weight:800;color:var(--sky)">{rep_fac}</div><div style="font-size:0.6rem;color:var(--muted);text-transform:uppercase">facilities</div></div>
                    <div><div style="font-size:1.2rem;font-family:'Syne',sans-serif;font-weight:800;color:var(--amber)">{rep_reg}</div><div style="font-size:0.6rem;color:var(--muted);text-transform:uppercase">regions</div></div>
                    <div><div style="font-size:1.2rem;font-family:'Syne',sans-serif;font-weight:800;color:var(--violet)">{rep_surg}</div><div style="font-size:0.6rem;color:var(--muted);text-transform:uppercase">surgeons</div></div>
                </div>
            </div>""", unsafe_allow_html=True)

        if "region" in df.columns:
            rc = df["region"].value_counts().reset_index(); rc.columns = ["Region","Count"]
            fig2 = px.pie(rc, values="Count", names="Region", color_discrete_sequence=COLORS, hole=.5)
            fig2.update_traces(textposition="inside", textinfo="percent", textfont_size=10,
                               marker=dict(line=dict(color="#080C12",width=2)))
            sc(fig2, "Regional Coverage"); fig2.update_layout(showlegend=False, height=200)
            st.plotly_chart(fig2, use_container_width=True)

    # Row 2
    col3, col4 = st.columns(2)
    with col3:
        if "rep" in df.columns:
            rc2 = df["rep"].value_counts().head(8).reset_index(); rc2.columns = ["Rep","Count"]
            fig3 = px.bar(rc2, x="Count", y="Rep", orientation="h",
                color="Count", color_continuous_scale=[[0,"#0E2D1A"],[1,"#00E5A0"]], text="Count")
            fig3.update_traces(textposition="outside", textfont_size=10, marker_line_width=0)
            sc(fig3, "Procedures by Rep")
            fig3.update_layout(yaxis=dict(autorange="reversed"), showlegend=False, height=300, coloraxis_showscale=False)
            st.plotly_chart(fig3, use_container_width=True)
    with col4:
        if "procedure" in df.columns:
            pc = df["procedure"].value_counts().head(8).reset_index(); pc.columns = ["Procedure","Count"]
            fig4 = px.bar(pc, x="Count", y="Procedure", orientation="h",
                color="Count", color_continuous_scale=[[0,"#0D2030"],[1,"#38BDF8"]], text="Count")
            fig4.update_traces(textposition="outside", textfont_size=10, marker_line_width=0)
            sc(fig4, "Top Procedure Types")
            fig4.update_layout(yaxis=dict(autorange="reversed"), showlegend=False, height=300, coloraxis_showscale=False)
            st.plotly_chart(fig4, use_container_width=True)

    # Row 3: Facility + Recent
    col5, col6 = st.columns([2,3])
    with col5:
        if "facility" in df.columns:
            fc = df["facility"].value_counts().head(7).reset_index(); fc.columns = ["Facility","Count"]
            fig5 = px.bar(fc, x="Count", y="Facility", orientation="h",
                color="Count", color_continuous_scale=[[0,"#2D1A00"],[1,"#FFBE0B"]], text="Count")
            fig5.update_traces(textposition="outside", textfont_size=10, marker_line_width=0)
            sc(fig5, "Top Facilities")
            fig5.update_layout(yaxis=dict(autorange="reversed"), showlegend=False, height=280, coloraxis_showscale=False)
            st.plotly_chart(fig5, use_container_width=True)
    with col6:
        st.markdown("<div class='sec-lbl'>Recent Procedures</div>", unsafe_allow_html=True)
        rcols = [c for c in ["date","invoice","rep","procedure","facility","surgeon"] if c in df.columns]
        rd = df.sort_values("date", ascending=False)[rcols].head(10).copy()
        if "date" in rd.columns: rd["date"] = rd["date"].dt.strftime("%d %b %Y")
        st.dataframe(rd, use_container_width=True, hide_index=True, height=290)

    # Row 4: quarterly
    if "quarter" in df.columns and "rep" in df.columns:
        st.markdown("<hr>", unsafe_allow_html=True)
        qr = df.groupby(["quarter","rep"]).size().reset_index(name="Count")
        fig6 = px.line(qr, x="quarter", y="Count", color="rep", markers=True,
            color_discrete_sequence=COLORS)
        sc(fig6, "Quarterly Performance by Rep")
        fig6.update_layout(height=280, legend=dict(orientation="h", y=-0.28))
        fig6.update_traces(line_width=2)
        st.plotly_chart(fig6, use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# ██  ADD PROCEDURE
# ─────────────────────────────────────────────────────────────────────────────
elif page == "➕  Add Procedure":
    st.markdown("""
    <div class="ph">
        <div class="ph-badge">✦ NEW ENTRY</div>
        <h1>ADD PROCEDURE</h1>
        <p>Log a new orthopedic procedure · All starred fields are required</p>
    </div>""", unsafe_allow_html=True)

    raw = load_data()
    auto = next_inv(raw)

    with st.form("add_form", clear_on_submit=True):
        st.markdown("<div class='fs'>📋 Procedure Identification</div>", unsafe_allow_html=True)
        c1,c2,c3 = st.columns(3)
        with c1: proc_date = st.date_input("📅 Date *", value=date.today())
        with c2: invoice   = st.text_input("🧾 Invoice Number *", value=auto)
        with c3: rep_sel   = st.selectbox("👤 Rep *", ["— Select —"]+REPS+["Other"])
        rep_other = st.text_input("Rep full name *", key="rep_o") if rep_sel=="Other" else ""

        st.markdown("<div class='fs fst'>🏥 Location</div>", unsafe_allow_html=True)
        c4,c5 = st.columns(2)
        with c4: fac_sel = st.selectbox("🏥 Facility *", ["— Select —"]+FACILITIES)
        with c5: reg_sel = st.selectbox("🌍 Region *",   ["— Select —"]+REGIONS)
        fac_other = st.text_input("Facility name *", key="fac_o") if fac_sel=="Other" else ""

        st.markdown("<div class='fs'>🔬 Clinical Details</div>", unsafe_allow_html=True)
        c6,c7 = st.columns(2)
        with c6: surg_sel  = st.selectbox("👨‍⚕️ Surgeon *",   ["— Select —"]+SURGEONS)
        with c7: proc_sel  = st.selectbox("🔬 Procedure *", ["— Select —"]+PROCEDURES)
        surg_other = st.text_input("Surgeon full name *", key="surg_o") if surg_sel=="Other" else ""
        proc_other = st.text_input("Procedure name *",    key="proc_o") if proc_sel=="Other" else ""
        implants_sel = st.multiselect("🦴 Implants Used *", IMPLANTS)

        st.markdown("<div class='fs fsa'>📝 Notes & Feedback</div>", unsafe_allow_html=True)
        c8,c9 = st.columns(2)
        with c8: challenges = st.text_area("⚠️ Challenges Encountered", placeholder="Intraoperative challenges, complications, delays…", height=110)
        with c9: feedback   = st.text_area("💬 Surgeon / Outcome Feedback", placeholder="Post-procedure feedback, surgeon comments, outcomes…", height=110)

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        submitted = st.form_submit_button("✅  Save Procedure", use_container_width=True, type="primary")

    if submitted:
        rep_f  = rep_other.strip()  if rep_sel  =="Other" else rep_sel
        fac_f  = fac_other.strip()  if fac_sel  =="Other" else fac_sel
        surg_f = surg_other.strip() if surg_sel =="Other" else surg_sel
        proc_f = proc_other.strip() if proc_sel =="Other" else proc_sel
        errs   = []
        if not invoice.strip():              errs.append("Invoice Number")
        if rep_sel  =="— Select —":          errs.append("Rep")
        if rep_sel  =="Other" and not rep_f: errs.append("Rep Name")
        if fac_sel  =="— Select —":          errs.append("Facility")
        if fac_sel  =="Other" and not fac_f: errs.append("Facility Name")
        if reg_sel  =="— Select —":          errs.append("Region")
        if surg_sel =="— Select —":          errs.append("Surgeon")
        if surg_sel =="Other" and not surg_f:errs.append("Surgeon Name")
        if proc_sel =="— Select —":          errs.append("Procedure")
        if proc_sel =="Other" and not proc_f:errs.append("Procedure Name")
        if not implants_sel:                 errs.append("Implants Used")
        if invoice.strip() in [r.get("invoice","") for r in raw]:
            errs.append(f"Invoice {invoice.strip()} already exists")
        if errs:
            st.error(f"Please fix: **{' · '.join(errs)}**")
        else:
            rec = {"id":datetime.now().strftime("%Y%m%d%H%M%S%f"),"date":str(proc_date),
                   "invoice":invoice.strip(),"rep":rep_f,"facility":fac_f,"region":reg_sel,
                   "surgeon":surg_f,"procedure":proc_f,"implants":implants_sel,
                   "challenges":challenges.strip() or "None",
                   "feedback":feedback.strip() or "—",
                   "logged_at":datetime.now().isoformat()}
            raw.append(rec); save_data(raw); bust()
            st.success(f"✅ Saved — Invoice **{invoice.strip()}** · {proc_f} · {fac_f}")
            st.balloons()


# ─────────────────────────────────────────────────────────────────────────────
# ██  IMPORT DATA
# ─────────────────────────────────────────────────────────────────────────────
elif page == "📥  Import Data":
    st.markdown("""
    <div class="ph">
        <div class="ph-badge">📥 BULK IMPORT</div>
        <h1>IMPORT DATA</h1>
        <p>Upload Excel (.xlsx / .xls) or CSV files to bulk-import procedure records</p>
    </div>""", unsafe_allow_html=True)

    # Template download
    st.markdown("### 📋 Step 1 — Download Template")
    st.markdown("Use this template to format your data correctly before importing.")

    col_t1, col_t2 = st.columns([2,3])
    with col_t1:
        buf_tpl = io.BytesIO()
        wb_tpl  = xlsxwriter.Workbook(buf_tpl, {"in_memory": True})
        def ft(**kw): return wb_tpl.add_format({**kw, "font_name":"Calibri"})
        fh = ft(bold=True, font_size=10, font_color="white", bg_color="#0E1520", border=1, border_color="#555", valign="vcenter", text_wrap=True)
        fd = ft(font_size=9, border=1, border_color="#DDD", italic=True, font_color="#888")
        fn = ft(font_size=8, border=1, border_color="#DDD", font_color="#AAA", italic=True)
        ws_tpl = wb_tpl.add_worksheet("Procedures")
        headers = ["date","invoice","rep","facility","region","surgeon","procedure","implants","challenges","feedback"]
        widths  = [14,  16,    22,  30,      16,      22,       28,          35,        40,         40]
        sample  = ["2024-06-15","INV-2024-0001","James Mwangi","Moi Teaching & Referral Hospital",
                   "East Africa","Dr. A. Kimani","Total Knee Replacement",
                   "Total Knee Replacement System, Bone Cement","None","Good outcome, surgeon satisfied"]
        notes   = ["YYYY-MM-DD","Auto-generated or manual","Sales Rep full name","Hospital name",
                   "Geographic region","Dr. Surname","Procedure performed",
                   "Comma-separated implants","Optional","Optional surgeon feedback"]
        ws_tpl.set_row(0, 24); ws_tpl.set_row(1, 18); ws_tpl.set_row(2, 36)
        for ci, (h, w, s, n) in enumerate(zip(headers, widths, sample, notes)):
            ws_tpl.set_column(ci, ci, w)
            ws_tpl.write(0, ci, h.upper(), fh)
            ws_tpl.write(1, ci, s, fd)
            ws_tpl.write(2, ci, f"ℹ️ {n}", fn)
        wb_tpl.close(); buf_tpl.seek(0)
        st.download_button("⬇️ Download Excel Template", data=buf_tpl,
            file_name="orthotrack_import_template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True, type="primary")

    with col_t2:
        st.markdown("""<div class="import-success">
        <div style="font-weight:700;margin-bottom:6px;color:#00E5A0">✓ Supported Column Names</div>
        <div style="font-size:0.8rem;color:#7A9AB8;line-height:1.8">
        <b style="color:#E8F0F8">date</b> — date, procedure date, surgery date<br>
        <b style="color:#E8F0F8">invoice</b> — invoice, invoice number, invoice #, inv no<br>
        <b style="color:#E8F0F8">rep</b> — rep, sales rep, representative, rep name<br>
        <b style="color:#E8F0F8">facility</b> — facility, hospital, institution<br>
        <b style="color:#E8F0F8">region</b> — region, territory, area<br>
        <b style="color:#E8F0F8">surgeon</b> — surgeon, doctor, physician<br>
        <b style="color:#E8F0F8">procedure</b> — procedure, surgery, procedure type<br>
        <b style="color:#E8F0F8">implants</b> — implant, implants, implants used, device, devices<br>
        <b style="color:#E8F0F8">challenges</b> — challenges, complications<br>
        <b style="color:#E8F0F8">feedback</b> — feedback, notes, comments, outcome
        </div></div>""", unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("### 📤 Step 2 — Upload Your File")

    uploaded = st.file_uploader(
        "Drop your Excel or CSV file here",
        type=["xlsx","xls","csv"],
        help="Supported: .xlsx, .xls, .csv — column names are auto-detected"
    )

    if uploaded:
        with st.spinner("Parsing file…"):
            import_df, parse_warnings = parse_import_file(uploaded)

        if import_df is None:
            for w in parse_warnings:
                st.error(f"❌ {w}")
        else:
            if parse_warnings:
                for w in parse_warnings:
                    st.warning(f"⚠️ {w}")

            st.markdown(f"""<div class="import-success">
            <div style="font-weight:700;color:#00E5A0;margin-bottom:4px">✓ File parsed successfully</div>
            <div style="font-size:0.82rem;color:#7A9AB8">{len(import_df)} rows detected · {len(import_df.columns)} columns mapped</div>
            </div>""", unsafe_allow_html=True)

            st.markdown("**Preview (first 10 rows)**")
            prev = import_df.copy()
            if "date" in prev.columns:
                prev["date"] = prev["date"].dt.strftime("%d %b %Y")
            if "implants" in prev.columns:
                prev["implants"] = prev["implants"].apply(
                    lambda x: ", ".join(x) if isinstance(x,list) else str(x))
            st.dataframe(prev.head(10), use_container_width=True, hide_index=True)

            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown("### ⚙️ Step 3 — Import Options")
            ic1, ic2 = st.columns(2)
            with ic1:
                overwrite = st.checkbox(
                    "Overwrite duplicate invoices",
                    value=False,
                    help="If unchecked, rows with existing invoice numbers are skipped"
                )
            with ic2:
                st.markdown("<div style='padding-top:0.3rem;font-size:0.8rem;color:var(--muted)'>Duplicate detection is based on Invoice Number. Rows without invoice numbers get auto-generated IDs.</div>",
                            unsafe_allow_html=True)

            if st.button("📥  Import Records", type="primary", use_container_width=True):
                raw = load_data()
                with st.spinner("Importing…"):
                    added, skipped, updated = import_records(import_df, raw, overwrite)
                    save_data(raw); bust()

                if added > 0 or updated > 0:
                    st.success(f"✅ Import complete — **{added} added**, **{updated} updated**, **{skipped} skipped**")
                    st.balloons()
                else:
                    st.warning(f"No new records added. {skipped} skipped (duplicate invoices). Enable 'Overwrite duplicates' to update them.")

                # Show import summary
                if added > 0:
                    st.markdown(f"""<div class="import-success">
                    <div style="font-weight:700;color:#00E5A0;margin-bottom:8px">Import Summary</div>
                    <div style="display:flex;gap:30px">
                        <div><div style="font-family:'Syne',sans-serif;font-size:1.8rem;font-weight:800;color:white">{added}</div><div style="font-size:0.65rem;color:var(--muted);text-transform:uppercase;letter-spacing:1px">Records Added</div></div>
                        <div><div style="font-family:'Syne',sans-serif;font-size:1.8rem;font-weight:800;color:var(--amber)">{updated}</div><div style="font-size:0.65rem;color:var(--muted);text-transform:uppercase;letter-spacing:1px">Updated</div></div>
                        <div><div style="font-family:'Syne',sans-serif;font-size:1.8rem;font-weight:800;color:var(--muted2)">{skipped}</div><div style="font-size:0.65rem;color:var(--muted);text-transform:uppercase;letter-spacing:1px">Skipped</div></div>
                    </div></div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# ██  PROCEDURE LOG
# ─────────────────────────────────────────────────────────────────────────────
elif page == "📋  Procedure Log":
    st.markdown("""
    <div class="ph">
        <div class="ph-badge">📋 RECORDS</div>
        <h1>PROCEDURE LOG</h1>
        <p>Search, filter, view, edit and manage all logged procedures</p>
    </div>""", unsafe_allow_html=True)

    df = get_df()
    if df.empty:
        st.info("No procedures found. Add one or import data to get started!"); st.stop()

    with st.expander("🔍  Filters", expanded=True):
        fc1,fc2,fc3,fc4 = st.columns(4)
        with fc1: sr = st.selectbox("Rep",       ["All"]+sorted(df["rep"].dropna().unique().tolist())       if "rep"       in df.columns else ["All"])
        with fc2: sg = st.selectbox("Region",    ["All"]+sorted(df["region"].dropna().unique().tolist())    if "region"    in df.columns else ["All"])
        with fc3: sf = st.selectbox("Facility",  ["All"]+sorted(df["facility"].dropna().unique().tolist())  if "facility"  in df.columns else ["All"])
        with fc4: sp = st.selectbox("Procedure", ["All"]+sorted(df["procedure"].dropna().unique().tolist()) if "procedure" in df.columns else ["All"])
        dc1,dc2,dc3 = st.columns([2,2,3])
        with dc1: d_from = st.date_input("From", value=df["date"].min().date())
        with dc2: d_to   = st.date_input("To",   value=df["date"].max().date())
        with dc3: q = st.text_input("🔎 Search", placeholder="Invoice · surgeon · facility · rep…")

    flt = df.copy()
    if sr!="All": flt = flt[flt["rep"]==sr]
    if sg!="All": flt = flt[flt["region"]==sg]
    if sf!="All": flt = flt[flt["facility"]==sf]
    if sp!="All": flt = flt[flt["procedure"]==sp]
    flt = flt[(flt["date"].dt.date>=d_from)&(flt["date"].dt.date<=d_to)]
    if q.strip():
        qx = q.strip().lower(); mk = pd.Series(False, index=flt.index)
        for c in ["invoice","surgeon","facility","rep","procedure"]:
            if c in flt.columns: mk |= flt[c].astype(str).str.lower().str.contains(qx, na=False)
        flt = flt[mk]

    ch1,ch2 = st.columns([3,1])
    with ch1: st.markdown(f"<div class='sec-lbl'>Showing {len(flt)} of {len(df)} procedures</div>", unsafe_allow_html=True)
    with ch2: srt = st.selectbox("Sort",["Date ↓","Date ↑","Rep","Facility","Invoice"], label_visibility="collapsed")
    sm = {"Date ↓":("date",False),"Date ↑":("date",True),"Rep":("rep",True),"Facility":("facility",True),"Invoice":("invoice",True)}
    sc_col, sa = sm[srt]; flt = flt.sort_values(sc_col, ascending=sa)

    sc_cols = [c for c in ["date","invoice","rep","procedure","facility","region","surgeon"] if c in flt.columns]
    disp = flt[sc_cols].copy()
    if "date" in disp.columns: disp["date"] = disp["date"].dt.strftime("%d %b %Y")
    st.dataframe(disp, use_container_width=True, hide_index=True, height=360)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("### 🔍 Record Detail")
    if not flt.empty:
        il = flt.sort_values("date", ascending=False)["invoice"].tolist()
        si = st.selectbox("Select Invoice", il, key="det")
        rec = flt[flt["invoice"]==si].iloc[0]
        dv = rec.get("date","")
        dstr = dv.strftime("%d %b %Y") if hasattr(dv,"strftime") else str(dv)[:10]
        ca,cb,cc = st.columns(3)
        with ca:
            for lbl,val in [("Date",dstr),("Invoice",rec.get("invoice","")),("Rep",rec.get("rep",""))]:
                st.markdown(f'<div class="rf"><div class="rl">{lbl}</div><div class="rv">{val}</div></div>',unsafe_allow_html=True)
        with cb:
            for lbl,val in [("Facility",rec.get("facility","")),("Region",rec.get("region","")),("Surgeon",rec.get("surgeon",""))]:
                st.markdown(f'<div class="rf"><div class="rl">{lbl}</div><div class="rv">{val}</div></div>',unsafe_allow_html=True)
        with cc:
            for lbl,val in [("Procedure",rec.get("procedure","")),("Source",rec.get("source","manual")),("Logged At",str(rec.get("logged_at",""))[:16])]:
                st.markdown(f'<div class="rf"><div class="rl">{lbl}</div><div class="rv">{val}</div></div>',unsafe_allow_html=True)
        impl = rec.get("implants",[])
        if isinstance(impl,list) and impl:
            chips = " ".join([f'<span class="chip">{i}</span>' for i in impl])
            st.markdown(f'<div class="rf"><div class="rl">Implants Used</div><div class="rv">{chips}</div></div>',unsafe_allow_html=True)
        cn1,cn2 = st.columns(2)
        with cn1: st.markdown(f'<div class="rf"><div class="rl">⚠️ Challenges</div><div class="rv">{rec.get("challenges","—")}</div></div>',unsafe_allow_html=True)
        with cn2: st.markdown(f'<div class="rf"><div class="rl">💬 Feedback</div><div class="rv">{rec.get("feedback","—")}</div></div>',unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    with st.expander("✏️  Edit a Record"):
        ei = st.text_input("Invoice number to edit", key="ei")
        raw2 = load_data()
        er_list = [r for r in raw2 if r.get("invoice")==ei.strip()]
        if ei.strip() and er_list:
            er = er_list[0]
            with st.form("edit_form"):
                ec1,ec2,ec3 = st.columns(3)
                with ec1: e_d = st.date_input("Date", value=date.fromisoformat(str(er["date"])[:10]))
                with ec2: e_r = st.selectbox("Rep", REPS, index=REPS.index(er["rep"]) if er["rep"] in REPS else 0)
                with ec3: e_f = st.selectbox("Facility", FACILITIES, index=FACILITIES.index(er["facility"]) if er["facility"] in FACILITIES else 0)
                ec4,ec5 = st.columns(2)
                with ec4: e_g = st.selectbox("Region", REGIONS, index=REGIONS.index(er["region"]) if er["region"] in REGIONS else 0)
                with ec5: e_s = st.selectbox("Surgeon", SURGEONS, index=SURGEONS.index(er["surgeon"]) if er["surgeon"] in SURGEONS else 0)
                e_p  = st.text_input("Procedure", value=er.get("procedure",""))
                e_c  = st.text_area("Challenges", value=er.get("challenges",""), height=80)
                e_fb = st.text_area("Feedback",   value=er.get("feedback",""),   height=80)
                if st.form_submit_button("💾 Save Changes", type="primary"):
                    for r in raw2:
                        if r.get("invoice")==ei.strip():
                            r.update({"date":str(e_d),"rep":e_r,"facility":e_f,"region":e_g,
                                      "surgeon":e_s,"procedure":e_p,"challenges":e_c,"feedback":e_fb})
                    save_data(raw2); bust()
                    st.success("Record updated!"); st.rerun()
        elif ei.strip(): st.warning("Invoice not found.")

    with st.expander("🗑️  Delete a Record"):
        di = st.text_input("Invoice number to delete", key="di")
        if st.button("🗑️  Delete Record", type="primary"):
            raw3 = load_data(); before = len(raw3)
            raw3 = [r for r in raw3 if r.get("invoice")!=di.strip()]
            if len(raw3)<before:
                save_data(raw3); bust(); st.success(f"Deleted `{di}`"); st.rerun()
            else: st.warning("Invoice not found.")


# ─────────────────────────────────────────────────────────────────────────────
# ██  RANKINGS & LEADERBOARD
# ─────────────────────────────────────────────────────────────────────────────
elif page == "🏆  Rankings":
    st.markdown("""
    <div class="ph">
        <div class="ph-badge">🏆 LEADERBOARD</div>
        <h1>RANKINGS</h1>
        <p>Rep leaderboards · Facility rankings · Surgeon activity · Goal tracking</p>
    </div>""", unsafe_allow_html=True)

    df = get_df()
    if df.empty:
        st.info("No data available."); st.stop()

    # Period filter
    pf1, pf2, pf3 = st.columns(3)
    with pf1:
        period = st.selectbox("Time Period", ["All Time","This Month","This Quarter","This Year","Last 30 Days","Last 90 Days"])
    with pf2:
        rank_by = st.selectbox("Rank By", ["Procedures","Facilities Covered","Surgeons Engaged","Regions Covered"])
    with pf3:
        show_goals = st.checkbox("Show Goal Progress", value=True)

    now = datetime.now()
    rdf = df.copy()
    if period == "This Month":
        rdf = rdf[(rdf["date"].dt.month==now.month)&(rdf["date"].dt.year==now.year)]
    elif period == "This Quarter":
        rdf = rdf[rdf["quarter"]==df["quarter"].max()]
    elif period == "This Year":
        rdf = rdf[rdf["year"]==now.year]
    elif period == "Last 30 Days":
        rdf = rdf[rdf["date"]>=pd.Timestamp.now()-pd.Timedelta(days=30)]
    elif period == "Last 90 Days":
        rdf = rdf[rdf["date"]>=pd.Timestamp.now()-pd.Timedelta(days=90)]

    period_label = period.lower()

    # Rep leaderboard
    tab_r, tab_f, tab_s, tab_g = st.tabs(["👤  Rep Rankings","🏥  Facility Rankings","🔬  Procedure Rankings","🎯  Goal Tracker"])

    with tab_r:
        if "rep" in rdf.columns and not rdf.empty:
            if rank_by == "Procedures":
                rs = rdf.groupby("rep").size().reset_index(name="score").sort_values("score", ascending=False)
                metric_label = "procedures"
            elif rank_by == "Facilities Covered":
                rs = rdf.groupby("rep")["facility"].nunique().reset_index(name="score").sort_values("score", ascending=False) if "facility" in rdf.columns else pd.DataFrame()
                metric_label = "facilities"
            elif rank_by == "Surgeons Engaged":
                rs = rdf.groupby("rep")["surgeon"].nunique().reset_index(name="score").sort_values("score", ascending=False) if "surgeon" in rdf.columns else pd.DataFrame()
                metric_label = "surgeons"
            else:
                rs = rdf.groupby("rep")["region"].nunique().reset_index(name="score").sort_values("score", ascending=False) if "region" in rdf.columns else pd.DataFrame()
                metric_label = "regions"

            if not rs.empty:
                max_score = rs["score"].max()
                st.markdown(f"<div class='sec-lbl'>Rep rankings · {rank_by.lower()} · {period_label}</div>", unsafe_allow_html=True)
                lc1, lc2 = st.columns([3,2])
                with lc1:
                    for i, row in rs.reset_index(drop=True).iterrows():
                        pct = int((row["score"]/max_score)*100)
                        color = rank_color(i)
                        bar_color = ["#FFD166","#B0C4DE","#CD9B6A"][i] if i < 3 else "#00E5A0"
                        st.markdown(f"""<div class="rank-row">
                            <div class="rank-num" style="color:{color}">{rank_icon(i)}</div>
                            <div class="rank-name">{row['rep']}</div>
                            <div class="rank-bar-wrap"><div class="rank-bar" style="width:{pct}%;background:{bar_color}"></div></div>
                            <div class="rank-val">{row['score']} {metric_label}</div>
                        </div>""", unsafe_allow_html=True)

                with lc2:
                    # Rep trend chart
                    if rank_by == "Procedures" and "month" in rdf.columns:
                        top5 = rs.head(5)["rep"].tolist()
                        rt = rdf[rdf["rep"].isin(top5)].groupby(["month","rep"]).size().reset_index(name="Count")
                        fig_rt = px.line(rt, x="month", y="Count", color="rep", markers=True,
                            color_discrete_sequence=["#FFD166","#B0C4DE","#CD9B6A","#00E5A0","#38BDF8"])
                        sc(fig_rt, "Top 5 Reps Trend")
                        fig_rt.update_layout(height=320, legend=dict(orientation="h", y=-0.3, font=dict(size=10)))
                        fig_rt.update_traces(line_width=2.5)
                        st.plotly_chart(fig_rt, use_container_width=True)

    with tab_f:
        if "facility" in rdf.columns and not rdf.empty:
            fs = rdf.groupby("facility").agg(
                Procedures=("id","count"),
                Reps=("rep","nunique"),
                Surgeons=("surgeon","nunique") if "surgeon" in rdf.columns else ("id","count")
            ).reset_index().sort_values("Procedures", ascending=False)

            st.markdown(f"<div class='sec-lbl'>Facility rankings by procedure volume · {period_label}</div>", unsafe_allow_html=True)
            max_f = fs["Procedures"].max()
            fc1, fc2 = st.columns([3,2])
            with fc1:
                for i, row in fs.head(10).reset_index(drop=True).iterrows():
                    pct = int((row["Procedures"]/max_f)*100)
                    color = rank_color(i); bar_c = ["#FFBE0B","#B0C4DE","#CD9B6A"][i] if i<3 else "#38BDF8"
                    st.markdown(f"""<div class="rank-row">
                        <div class="rank-num" style="color:{color}">{rank_icon(i)}</div>
                        <div class="rank-name" style="max-width:220px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{row['facility']}</div>
                        <div class="rank-bar-wrap"><div class="rank-bar" style="width:{pct}%;background:{bar_c}"></div></div>
                        <div class="rank-val">{row['Procedures']}</div>
                    </div>""", unsafe_allow_html=True)
            with fc2:
                fig_fp = px.pie(fs.head(8), values="Procedures", names="facility",
                    color_discrete_sequence=COLORS, hole=.45)
                fig_fp.update_traces(textposition="inside", textinfo="percent", textfont_size=10,
                    marker=dict(line=dict(color="#080C12",width=2)))
                sc(fig_fp, "Facility Share"); fig_fp.update_layout(showlegend=False, height=320)
                st.plotly_chart(fig_fp, use_container_width=True)

    with tab_s:
        if "procedure" in rdf.columns and not rdf.empty:
            ps = rdf["procedure"].value_counts().reset_index()
            ps.columns = ["Procedure","Count"]
            st.markdown(f"<div class='sec-lbl'>Procedure type rankings · {period_label}</div>", unsafe_allow_html=True)
            max_p = ps["Count"].max()
            for i, row in ps.head(12).reset_index(drop=True).iterrows():
                pct = int((row["Count"]/max_p)*100)
                bar_c = COLORS[i % len(COLORS)]
                st.markdown(f"""<div class="rank-row">
                    <div class="rank-num" style="color:{rank_color(i)}">{rank_icon(i)}</div>
                    <div class="rank-name">{row['Procedure']}</div>
                    <div class="rank-bar-wrap"><div class="rank-bar" style="width:{pct}%;background:{bar_c}"></div></div>
                    <div class="rank-val">{row['Count']}</div>
                </div>""", unsafe_allow_html=True)

    with tab_g:
        st.markdown("#### 🎯 Monthly Rep Goal Tracker")
        goals = load_goals()
        now_m = datetime.now()
        this_mo_key = f"{now_m.year}-{now_m.month:02d}"
        this_mo_df = df[(df["date"].dt.month==now_m.month)&(df["date"].dt.year==now_m.year)]
        rep_actual  = this_mo_df["rep"].value_counts().to_dict() if "rep" in this_mo_df.columns else {}

        st.markdown(f"<div class='sec-lbl'>Month: {now_m.strftime('%B %Y')}</div>", unsafe_allow_html=True)

        # Goal setting form
        with st.expander("⚙️  Set Monthly Goals"):
            with st.form("goals_form"):
                gcols = st.columns(3)
                new_goals = {}
                for i, rep in enumerate(REPS):
                    with gcols[i % 3]:
                        current_goal = goals.get(rep, {}).get("monthly", 10)
                        new_goals[rep] = st.number_input(
                            rep, min_value=0, max_value=500,
                            value=int(current_goal), key=f"g_{rep}"
                        )
                if st.form_submit_button("💾 Save Goals", type="primary"):
                    for rep, goal in new_goals.items():
                        if rep not in goals: goals[rep] = {}
                        goals[rep]["monthly"] = goal
                    save_goals(goals)
                    st.success("Goals saved!"); st.rerun()

        # Goal progress display
        reps_with_data = set(list(rep_actual.keys()) + list(goals.keys()))
        if reps_with_data:
            gc1, gc2 = st.columns(2)
            for i, rep in enumerate(sorted(reps_with_data)):
                actual = rep_actual.get(rep, 0)
                goal   = goals.get(rep, {}).get("monthly", 0)
                if goal == 0: continue
                pct    = min(int((actual/goal)*100), 100)
                remaining = max(goal - actual, 0)
                if pct >= 100:
                    bar_color = "linear-gradient(90deg,#00E5A0,#00C488)"
                    status = "🎯 Goal Achieved!"
                    status_color = "var(--emerald)"
                elif pct >= 75:
                    bar_color = "linear-gradient(90deg,#38BDF8,#0284C7)"
                    status = f"🔥 {remaining} to go"
                    status_color = "var(--sky)"
                elif pct >= 50:
                    bar_color = "linear-gradient(90deg,#FFBE0B,#D97706)"
                    status = f"📈 {remaining} to go"
                    status_color = "var(--amber)"
                else:
                    bar_color = "linear-gradient(90deg,#FF6B6B,#DC2626)"
                    status = f"⚡ {remaining} to go"
                    status_color = "var(--coral)"

                with gc1 if i%2==0 else gc2:
                    st.markdown(f"""<div class="goal-card">
                        <div class="goal-title">{rep}</div>
                        <div class="goal-sub">{actual} of {goal} procedures this month</div>
                        <div class="goal-track-wrap">
                            <div class="goal-track" style="width:{pct}%;background:{bar_color}"></div>
                        </div>
                        <div style="display:flex;align-items:center;justify-content:space-between">
                            <div class="goal-pct" style="color:{status_color}">{pct}%</div>
                            <div style="font-size:0.75rem;color:{status_color};font-weight:600">{status}</div>
                        </div>
                    </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# ██  ANALYTICS
# ─────────────────────────────────────────────────────────────────────────────
elif page == "📈  Analytics":
    st.markdown("""
    <div class="ph">
        <div class="ph-badge">📈 INSIGHTS</div>
        <h1>ANALYTICS</h1>
        <p>Deep-dive into trends · facility coverage · procedure patterns · implant usage</p>
    </div>""", unsafe_allow_html=True)

    df = get_df()
    if df.empty:
        st.info("No data available. Add procedures to unlock analytics."); st.stop()

    with st.expander("⚙️  Filter Analytics", expanded=False):
        fa1,fa2 = st.columns(2)
        with fa1: sy  = st.selectbox("Year", ["All"]+sorted(df["year"].dropna().unique().astype(str).tolist(), reverse=True))
        with fa2: sa2 = st.selectbox("Rep",  ["All"]+sorted(df["rep"].dropna().unique().tolist()) if "rep" in df.columns else ["All"])
    adf = df.copy()
    if sy !="All": adf = adf[adf["year"].astype(str)==sy]
    if sa2!="All": adf = adf[adf["rep"]==sa2]

    tab1,tab2,tab3,tab4 = st.tabs(["📅  Trends","🏥  Facility & Region","👤  Rep Performance","🦴  Implants"])

    with tab1:
        c1,c2 = st.columns(2)
        with c1:
            mo = adf.groupby("month").size().reset_index(name="Count")
            fig = px.area(mo, x="month", y="Count", color_discrete_sequence=["#00E5A0"])
            fig.update_traces(fill="tozeroy", fillcolor="rgba(0,229,160,0.08)", line=dict(width=2.5))
            sc(fig, "Monthly Procedure Volume"); fig.update_layout(height=280)
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            ord_ = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
            dow = adf["date"].dt.day_name().value_counts().reindex(ord_, fill_value=0).reset_index()
            dow.columns = ["Day","Count"]
            fig2 = px.bar(dow, x="Day", y="Count", color="Count",
                color_continuous_scale=[[0,"#0D2030"],[1,"#00E5A0"]])
            fig2.update_traces(text=dow["Count"], textposition="outside", marker_line_width=0)
            sc(fig2, "Volume by Day of Week"); fig2.update_layout(height=280, showlegend=False, coloraxis_showscale=False)
            st.plotly_chart(fig2, use_container_width=True)

        if "quarter" in adf.columns and "rep" in adf.columns:
            qr = adf.groupby(["quarter","rep"]).size().reset_index(name="Count")
            fig3 = px.line(qr, x="quarter", y="Count", color="rep", markers=True, color_discrete_sequence=COLORS)
            sc(fig3, "Quarterly Trends by Rep"); fig3.update_layout(height=300, legend=dict(orientation="h",y=-0.28))
            fig3.update_traces(line_width=2)
            st.plotly_chart(fig3, use_container_width=True)

        if "procedure" in adf.columns:
            tp = adf["procedure"].value_counts().head(6).index.tolist()
            pt = adf[adf["procedure"].isin(tp)].groupby(["month","procedure"]).size().reset_index(name="Count")
            fig4 = px.line(pt, x="month", y="Count", color="procedure", markers=True, color_discrete_sequence=COLORS)
            sc(fig4, "Top Procedure Types Over Time"); fig4.update_layout(height=300, legend=dict(orientation="h",y=-0.28))
            fig4.update_traces(line_width=2)
            st.plotly_chart(fig4, use_container_width=True)

    with tab2:
        c1,c2 = st.columns(2)
        with c1:
            if "facility" in adf.columns:
                fc2 = adf["facility"].value_counts().reset_index(); fc2.columns = ["Facility","Count"]
                fig5 = px.bar(fc2, x="Count", y="Facility", orientation="h",
                    color="Count", color_continuous_scale=[[0,"#2D1A00"],[1,"#FFBE0B"]], text="Count")
                fig5.update_traces(textposition="outside", marker_line_width=0)
                sc(fig5, "Procedures by Facility")
                fig5.update_layout(yaxis=dict(autorange="reversed"), height=380, showlegend=False, coloraxis_showscale=False)
                st.plotly_chart(fig5, use_container_width=True)
        with c2:
            if "region" in adf.columns:
                rg = adf["region"].value_counts().reset_index(); rg.columns = ["Region","Count"]
                fig6 = px.pie(rg, values="Count", names="Region", hole=.45, color_discrete_sequence=COLORS)
                fig6.update_traces(textposition="inside", textinfo="percent+label", textfont_size=11,
                    marker=dict(line=dict(color="#080C12",width=2)))
                sc(fig6, "Regional Distribution")
                fig6.update_layout(height=380, showlegend=True, legend=dict(orientation="v",x=1.02))
                st.plotly_chart(fig6, use_container_width=True)

        if "region" in adf.columns and "procedure" in adf.columns:
            hm = adf.groupby(["region","procedure"]).size().unstack(fill_value=0)
            fig7 = px.imshow(hm, color_continuous_scale=[[0,"#0E1520"],[0.5,"#006644"],[1,"#00E5A0"]], aspect="auto", text_auto=True)
            sc(fig7, "Region × Procedure Heatmap"); fig7.update_layout(height=400, coloraxis_showscale=False)
            st.plotly_chart(fig7, use_container_width=True)

    with tab3:
        if "rep" in adf.columns:
            rs = adf.groupby("rep").agg(
                Procedures=("id","count"),
                Facilities=("facility","nunique"),
                Surgeons=("surgeon","nunique"),
                Regions=("region","nunique")
            ).reset_index().sort_values("Procedures", ascending=False)
            st.markdown("#### Rep Performance Table")
            st.dataframe(rs, use_container_width=True, hide_index=True)

            c1,c2 = st.columns(2)
            with c1:
                fig8 = px.bar(rs.head(10), x="Procedures", y="rep", orientation="h",
                    color="Procedures", color_continuous_scale=[[0,"#0E2D1A"],[1,"#00E5A0"]], text="Procedures")
                fig8.update_traces(textposition="outside", marker_line_width=0)
                sc(fig8, "Total Procedures per Rep")
                fig8.update_layout(yaxis=dict(autorange="reversed"), height=340, showlegend=False, coloraxis_showscale=False)
                st.plotly_chart(fig8, use_container_width=True)
            with c2:
                fig9 = px.scatter(rs, x="Facilities", y="Procedures", text="rep",
                    color="Regions", size="Procedures", size_max=40,
                    color_continuous_scale=[[0,"#0E2D1A"],[1,"#00E5A0"]])
                sc(fig9, "Reach: Procedures vs Facilities")
                fig9.update_traces(textposition="top center", textfont_size=9)
                fig9.update_layout(height=340, showlegend=False, coloraxis_showscale=False)
                st.plotly_chart(fig9, use_container_width=True)

            rm = adf.groupby(["rep","month"]).size().unstack(fill_value=0)
            fig10 = px.imshow(rm, color_continuous_scale=[[0,"#0E1520"],[0.5,"#006644"],[1,"#00E5A0"]], aspect="auto", text_auto=True)
            sc(fig10, "Rep Activity Heatmap (Monthly)"); fig10.update_layout(height=360, coloraxis_showscale=False)
            st.plotly_chart(fig10, use_container_width=True)

    with tab4:
        if "implants" in adf.columns:
            imp = adf["implants"].dropna().explode().value_counts().reset_index()
            imp.columns = ["Implant","Count"]
            c1,c2 = st.columns(2)
            with c1:
                fig11 = px.bar(imp.head(12), x="Count", y="Implant", orientation="h",
                    color="Count", color_continuous_scale=[[0,"#0D2030"],[1,"#38BDF8"]], text="Count")
                fig11.update_traces(textposition="outside", marker_line_width=0)
                sc(fig11, "Most Used Implants")
                fig11.update_layout(yaxis=dict(autorange="reversed"), height=380, showlegend=False, coloraxis_showscale=False)
                st.plotly_chart(fig11, use_container_width=True)
            with c2:
                fig12 = px.pie(imp.head(10), values="Count", names="Implant", hole=.4, color_discrete_sequence=COLORS)
                fig12.update_traces(textposition="inside", textinfo="percent+label", textfont_size=10,
                    marker=dict(line=dict(color="#080C12",width=2)))
                sc(fig12, "Implant Mix (Top 10)"); fig12.update_layout(height=380, showlegend=False)
                st.plotly_chart(fig12, use_container_width=True)

            adf2 = adf.copy().explode("implants")
            ti   = adf2["implants"].value_counts().head(6).index.tolist()
            it   = adf2[adf2["implants"].isin(ti)].groupby(["month","implants"]).size().reset_index(name="Count")
            fig13 = px.line(it, x="month", y="Count", color="implants", markers=True, color_discrete_sequence=COLORS)
            sc(fig13, "Top Implant Usage Over Time"); fig13.update_layout(height=300, legend=dict(orientation="h",y=-0.28))
            fig13.update_traces(line_width=2)
            st.plotly_chart(fig13, use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# ██  REPORTS
# ─────────────────────────────────────────────────────────────────────────────
elif page == "⬇️  Reports":
    st.markdown("""
    <div class="ph">
        <div class="ph-badge">⬇️ EXPORT</div>
        <h1>REPORTS</h1>
        <p>Generate and download professional procedure reports in PDF, Excel or CSV</p>
    </div>""", unsafe_allow_html=True)

    df = get_df()
    if df.empty:
        st.info("No procedures to report on yet."); st.stop()

    st.markdown("### ⚙️ Configure Report")
    rb1,rb2 = st.columns(2)
    with rb1: scope = st.selectbox("Report Scope",["All Procedures","By Rep","By Region","By Facility","By Procedure Type","Date Range"])
    with rb2: fmt   = st.selectbox("Export Format",["📄 PDF (Branded)","📊 Excel Workbook (.xlsx)","📑 CSV"])

    flt_r = df.copy(); lbl = "All Procedures"
    if scope=="By Rep" and "rep" in df.columns:
        sr2   = st.selectbox("Select Rep", sorted(df["rep"].dropna().unique().tolist()))
        flt_r = df[df["rep"]==sr2]; lbl = f"Rep: {sr2}"
    elif scope=="By Region" and "region" in df.columns:
        sg2   = st.selectbox("Select Region", sorted(df["region"].dropna().unique().tolist()))
        flt_r = df[df["region"]==sg2]; lbl = f"Region: {sg2}"
    elif scope=="By Facility" and "facility" in df.columns:
        sf2   = st.selectbox("Select Facility", sorted(df["facility"].dropna().unique().tolist()))
        flt_r = df[df["facility"]==sf2]; lbl = f"Facility: {sf2}"
    elif scope=="By Procedure Type" and "procedure" in df.columns:
        sp2   = st.selectbox("Select Procedure", sorted(df["procedure"].dropna().unique().tolist()))
        flt_r = df[df["procedure"]==sp2]; lbl = f"Procedure: {sp2}"
    elif scope=="Date Range":
        dr1,dr2 = st.columns(2)
        with dr1: df_from2 = st.date_input("From", value=df["date"].min().date())
        with dr2: df_to2   = st.date_input("To",   value=df["date"].max().date())
        flt_r = df[(df["date"].dt.date>=df_from2)&(df["date"].dt.date<=df_to2)]
        lbl   = f"{df_from2.strftime('%d %b %Y')} – {df_to2.strftime('%d %b %Y')}"

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("### 📋 Report Preview")
    rp1,rp2,rp3,rp4 = st.columns(4)
    with rp1: st.metric("Procedures", len(flt_r))
    with rp2: st.metric("Facilities", flt_r["facility"].nunique() if "facility" in flt_r.columns else 0)
    with rp3: st.metric("Surgeons",   flt_r["surgeon"].nunique()  if "surgeon"  in flt_r.columns else 0)
    with rp4: st.metric("Reps",       flt_r["rep"].nunique()       if "rep"      in flt_r.columns else 0)

    if not flt_r.empty:
        pc  = [c for c in ["date","invoice","rep","procedure","facility","surgeon"] if c in flt_r.columns]
        pd2 = flt_r.sort_values("date", ascending=False)[pc].head(6).copy()
        if "date" in pd2.columns: pd2["date"] = pd2["date"].dt.strftime("%d %b %Y")
        st.dataframe(pd2, use_container_width=True, hide_index=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("### ⬇️ Download")
    rt = f"OrthoTrack Pro — {lbl}"
    ts = datetime.now().strftime("%Y%m%d_%H%M")

    if "PDF" in fmt:
        st.markdown("""<div class="dlc"><div class="di">📄</div>
        <div class="dt">Branded PDF Report</div>
        <div class="dd">Professional report with summary stats, procedure log and OrthoTrack branding</div></div>""",
        unsafe_allow_html=True)
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        if st.button("📄  Generate PDF Report", type="primary", use_container_width=True):
            with st.spinner("Building PDF…"):
                pb = build_pdf(flt_r, rt, lbl)
            st.download_button("⬇️  Download PDF", data=pb,
                file_name=f"orthotrack_{ts}.pdf", mime="application/pdf", use_container_width=True)

    elif "Excel" in fmt:
        st.markdown("""<div class="dlc"><div class="di">📊</div>
        <div class="dt">Excel Workbook</div>
        <div class="dd">3-sheet workbook: Procedures · Summary Statistics · Regional Breakdown</div></div>""",
        unsafe_allow_html=True)
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        if st.button("📊  Generate Excel Workbook", type="primary", use_container_width=True):
            with st.spinner("Building Excel workbook…"):
                xb = build_excel(flt_r, rt)
            st.download_button("⬇️  Download Excel", data=xb,
                file_name=f"orthotrack_{ts}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True)

    elif "CSV" in fmt:
        st.markdown("""<div class="dlc"><div class="di">📑</div>
        <div class="dt">CSV Export</div>
        <div class="dd">Raw data export — all columns, all records, comma-separated</div></div>""",
        unsafe_allow_html=True)
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        cd = flt_r.copy()
        if "date" in cd.columns: cd["date"] = cd["date"].dt.strftime("%Y-%m-%d")
        if "implants" in cd.columns: cd["implants"] = cd["implants"].apply(lambda x:", ".join(x) if isinstance(x,list) else str(x))
        for c in ["month","year","quarter","week"]:
            if c in cd.columns: cd.drop(columns=c, inplace=True)
        st.download_button("⬇️  Download CSV", data=cd.to_csv(index=False).encode(),
            file_name=f"orthotrack_{ts}.csv", mime="text/csv", use_container_width=True)
