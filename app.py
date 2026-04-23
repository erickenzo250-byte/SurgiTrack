# �────────────────────────────────────────────────────────────────────────────
# orthotrack_pro.py  –  World‑Class Orthopedic Procedure Management System
# ────────────────────────────────────────────────────────────────────────
# 1️⃣  Imports & basic config
# 2️⃣  Design system (CSS + colour dict)
# 3️⃣  Data layer (JSON persistence – simple but portable)
# 4️⃣  Plotly theme helper
# 5️⃣  UI helpers (metric card, ag‑grid, dark‑mode)
# 6️⃣  Sidebar navigation
# 7️⃣  Pages: Dashboard • Add Procedure • Procedure Log • Analytics • Reports
# ────────────────────────────────────────────────────────────────────────
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json, os, io
from datetime import datetime, date
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph,
    Spacer, HRFlowable,
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import xlsxwriter

# Ag‑Grid for fast, paginated tables
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode

# ─────────────────────────────────────────────────────────────────────────────
# 1️⃣ PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="OrthoTrack Pro",
    page_icon="🦴",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# 2️⃣ DESIGN SYSTEM & COLOURS
# ─────────────────────────────────────────────────────────────────────────────
# --------─ colour dictionary – single source of truth ----------
COLOR = {
    # core palette (colour‑blind safe)
    "primary"   : "#0F4C75",   # deep navy – used for header background
    "accent"    : "#3282B8",   # sky‑blue – buttons, highlights
    "ink"       : "#1B262C",   # darkest text
    "soft_teal" : "#BBE1FA",
    "page_bg"   : "#F7F7FF",
    "warning"  : "#F08A5D",
    "error"    : "#B83B5E",
    "border"    : "#E5E5E5",
    "white"    : "#FFFFFF",
    "card_bg"   : "#F0F4FF",
    # Plotly sequential palettes (referenced by key)
    "seq_blue"   : "Blues",
    "seq_teal"   : "Tealgrn",
    "seq_orange" : "OrRd",
    "seq_green"  : "Greens",
    "seq_purple" : "Purples",
}

# --------─ global CSS (light theme) ----------
st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Bebas+Neue&display=swap');

    :root {{
        --c-primary   : {COLOR["primary"]};
        --c-accent    : {COLOR["accent"]};
        --c-ink       : {COLOR["ink"]};
        --c-soft-teal : {COLOR["soft_teal"]};
        --c-page-bg   : {COLOR["page_bg"]};
        --c-warning   : {COLOR["warning"]};
        --c-error     : {COLOR["error"]};
        --c-border    : {COLOR["border"]};
        --c-white     : {COLOR["white"]};
        --c-card-bg   : {COLOR["card_bg"]};
    }}

    html, body, [class*="css"] {{
        font-family: 'Inter',sans-serif !important;
        background: var(--c-page-bg) !important;
        color: var(--c-ink) !important;
    }}

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {{
        background: var(--c-primary) !important;
        border-right: 1px solid #1e2d3d !important;
    }}
    [data-testid="stSidebar"] * {{ color: #E0E7FF !important; }}
    [data-testid="stSidebar"] .sb-brand {{
        background: linear-gradient(135deg,var(--c-accent),var(--c-soft-teal));
        padding: 1.4rem 1.2rem 1.2rem;
        margin-bottom:.5rem;
        border-radius:8px;
    }}
    [data-testid="stSidebar"] .sb-brand h2 {{
        font-family:'Bebas Neue',sans-serif !important;
        font-size:1.9rem !important;
        letter-spacing:2px;
        color:white !important;
        margin:0;
    }}
    [data-testid="stSidebar"] .sb-brand p {{
        font-size:.75rem !important;
        color:rgba(255,255,255,.7);
        margin:0;
        letter-spacing:1.2px;
    }}

    /* ── Page Header ── */
    .ph {{
        background: linear-gradient(135deg,var(--c-primary),var(--c-accent));
        border-radius:16px;
        padding:2rem 2.5rem;
        margin-bottom:1.6rem;
        position:relative; overflow:hidden;
    }}
    .ph::after,.ph::before {{
        content:''; position:absolute; border-radius:50%;
        opacity:.13; pointer-events:none;
    }}
    .ph::after {{
        right:-60px; top:-60px;
        width:220px;height:220px;
        background:radial-gradient(circle,rgba(50,130,184,.3) 0%,transparent 70%);
    }}
    .ph::before {{
        right:40px; bottom:-40px;
        width:160px;height:160px;
        background:radial-gradient(circle,rgba(15,76,117,.25) 0%,transparent 70%);
    }}
    .ph h1 {{
        font-family:'Bebas Neue',sans-serif !important;
        font-size:2.7rem !important;
        letter-spacing:3px;
        color:white !important;
        margin:0 0 .3rem;
    }}
    .ph p {{
        color:rgba(255,255,255,.6);
        font-size:.88rem;
        margin:0;
    }}
    .ph-badge {{
        display:inline-block;
        background:rgba(255,255,255,.1);
        color:var(--c-accent);
        font-size:.75rem;
        font-weight:600;
        padding:.25rem .8rem;
        border-radius:20px;
        margin-bottom:.6rem;
    }}

    /* ── Section label ── */
    .sec-lbl {{
        font-size:.75rem; font-weight:700; text-transform:uppercase;
        letter-spacing:2px; color:var(--c-accent); margin-bottom:.6rem;
    }}

    /* ── Form sections ── */
    .fs {{
        background:var(--c-card-bg);
        border-left:4px solid var(--c-accent);
        border-radius:0 8px 8px 0;
        padding:.45rem .8rem .3rem;
        margin:1rem 0 .4rem;
        font-size:.75rem; font-weight:700;
        text-transform:uppercase;
        letter-spacing:1.5px;
        color:var(--c-accent);
    }}
    .fst{{background:var(--c-soft-teal);border-left-color:var(--c-accent);color:var(--c-accent);}}
    .fsa{{background:#FFFBEB;border-left-color:#F59E0B;color:#92400E;}}

    /* ── Record field ── */
    .rf{{margin-bottom:.5rem;padding:.6rem .9rem;background:#F8FAFC;border-radius:8px;}}
    .rf .rl{{font-size:.68rem;font-weight:700;text-transform:uppercase;letter-spacing:1px;color:var(--c-border);}}
    .rf .rv{{font-size:.92rem;color:var(--c-ink);font-weight:500;}}

    /* ── Chip ── */
    .chip{display:inline-block;background:linear-gradient(135deg,#EFF6FF,#DBEAFE);
          color:var(--c-accent);font-size:.72rem;font-weight:600;
          padding:.25rem .7rem;border-radius:20px;
          border:1px solid #BFDBFE;margin:.2rem .2rem .2rem 0;}

    /* ── Download card ── */
    .dlc{{background:var(--c-white);border:1.5px solid var(--c-border);
          border-radius:14px;padding:1.8rem;text-align:center;}}
    .dlc .di{{font-size:2.5rem;margin-bottom:.5rem;}}
    .dlc .dt{{font-weight:700;font-size:1rem;color:var(--c-ink);margin-bottom:.25rem;}}
    .dlc .dd{{font-size:.8rem;color:var(--c-border);}}

    /* ── Inputs ── */
    .stTextInput input,.stTextArea textarea{border-radius:8px !important;
        border:1.5px solid var(--c-border) !important;
        font-family:'Inter',sans-serif !important;font-size:.9rem !important;}
    .stTextInput input:focus,.stTextArea textarea:focus{border-color:var(--c-accent) !important;
        box-shadow:0 0 0 3px rgba(50,130,184,.12) !important;}
    .stTextInput label,.stTextArea label,.stSelectbox label,.stMultiSelect label,.stDateInput label{
        font-size:.78rem !important;font-weight:600 !important;
        color:var(--c-ink) !important;text-transform:uppercase !important;
        letter-spacing:.8px !important;}

    /* ── Buttons ── */
    .stButton>button{font-family:'Inter',sans-serif !important;
        font-weight:600 !important;border-radius:8px !important;
        transition:transform .15s,box-shadow .15s,background .15s !important;
        background:var(--c-accent);color:#fff;border:none;}
    .stButton>button:hover{transform:translateY(-1px);
        box-shadow:0 4px 12px rgba(50,130,184,.3);}
    .stButton>button[kind="secondary"]{background:var(--c-soft-teal);color:var(--c-ink);}

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"]{background:transparent !important;
        border-bottom:2px solid var(--c-border) !important;}
    .stTabs [data-baseweb="tab"]{font-family:'Inter',sans-serif !important;
        font-weight:600 !important;font-size:.85rem !important;
        padding:.7rem 1.2rem !important;color:var(--c-border) !important;}
    .stTabs [aria-selected="true"]{color:var(--c-accent) !important;
        border-bottom:2px solid var(--c-accent) !important;}

    /* ── Metric (fallback) ── */
    [data-testid="metric-container"] label{{font-family:'Inter',sans-serif !important;
        font-size:.72rem !important;font-weight:600 !important;
        text-transform:uppercase !important;letter-spacing:.8px !important;
        color:var(--c-border) !important;}}
    [data-testid="metric-container"] [data-testid="stMetricValue"]{{font-family:'Bebas Neue',sans-serif !important;
        font-size:2.2rem !important;color:var(--c-ink) !important;}}

    /* ── Dark‑mode toggle button ── */
    .dark-toggle{{position:fixed;top:0.9rem;right:0.9rem;background:var(--c-accent);
        color:#fff;border:none;border-radius:99px;padding:.35rem .9rem;
        font-weight:600;cursor:pointer;z-index:9999;}}
    .dark-toggle:hover{{opacity:.9;}}

    /* ── Scrollbar ── */
    ::-webkit-scrollbar{{width:6px;height:6px;}}
    ::-webkit-scrollbar-thumb{{background:#CBD5E1;border-radius:3px;}}
    </style>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────────────────────────────────────
# 3️⃣ DATA LAYER  (JSON file – simple, portable)
# ─────────────────────────────────────────────────────────────────────────────
DATA_FILE = "procedures.json"


def load_data() -> list:
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []


def save_data(data: list):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2, default=str)


@st.cache_data(ttl=2)
def get_df() -> pd.DataFrame:
    data = load_data()
    if not data:
        return pd.DataFrame()
    df = pd.DataFrame(data)
    df["date"] = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.to_period("M").astype(str)
    df["year"] = df["date"].dt.year
    df["quarter"] = df["date"].dt.to_period("Q").astype(str)
    return df


def bust():
    """Clear the cached DataFrame after a write operation."""
    get_df.clear()


def next_inv(data: list) -> str:
    """Create a sequential invoice number for the current year."""
    yr = datetime.now().year
    nums = []
    for r in data:
        inv = r.get("invoice", "")
        if str(yr) in inv:
            try:
                nums.append(int(inv.split("-")[-1]))
            except Exception:
                pass
    nxt = (max(nums) + 1) if nums else 1
    return f"INV-{yr}-{nxt:04d}"


# ─────────────────────────────────────────────────────────────────────────────
# 4️⃣ PLOTLY THEME HELPER
# ─────────────────────────────────────────────────────────────────────────────
BASE = dict(
    paper_bgcolor=COLOR["white"],
    plot_bgcolor="#F8FAFC",
    font=dict(family="Inter", color=COLOR["ink"]),
    title_font=dict(family="Inter", size=13, color=COLOR["border"]),
    margin=dict(t=44, b=28, l=20, r=16),
    legend=dict(font=dict(size=11, color=COLOR["ink"])),
)


def sc(fig: go.Figure, title: str = "", palette_key: str = "seq_blue") -> go.Figure:
    """
    Apply global theme and set a colour‑scale.
    palette_key must be a key from the COLOR dict that maps to a Plotly sequential scheme.
    """
    seq_name = COLOR.get(palette_key, "Blues")
    fig.update_layout(**BASE, title=dict(text=title, x=0.01, xanchor="left"))
    # If the trace uses a numerical colour field, give it the palette
    for tr in fig.data:
        if hasattr(tr, "marker") and hasattr(tr.marker, "color"):
            tr.marker.colorscale = seq_name
    fig.update_xaxes(
        showgrid=False, linecolor=COLOR["border"], tickfont=dict(size=10)
    )
    fig.update_yaxes(
        gridcolor="#F1F5F9", linecolor=COLOR["border"], tickfont=dict(size=10)
    )
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# 5️⃣ UI HELPERS (metric card, Ag‑Grid, dark‑mode)
# ─────────────────────────────────────────────────────────────────────────────
def metric_card(title: str, value, delta: str = None, help_msg: str = None):
    """Render a metric inside a subtle card with hover lift."""
    card_css = """
    <style>
    .metric-card{
        background:#FFF;
        border:1px solid #E5E5E5;
        border-radius:12px;
        padding:1rem 1.2rem;
        box-shadow:0 1px 4px rgba(0,0,0,.08);
        transition:transform .12s,box-shadow .12s;
    }
    .metric-card:hover{
        transform:translateY(-2px);
        box-shadow:0 4px 12px rgba(0,0,0,.12);
    }
    .metric-title{font-size:.75rem;color:#64748B;text-transform:uppercase;}
    .metric-value{font-family:'Bebas Neue',sans-serif;font-size:2.2rem;color:#0D1B2A;}
    .metric-delta{font-size:.78rem;color:#3282B8;}
    </style>
    """
    delta_html = f"<div class='metric-delta'>{delta}</div>" if delta else ""
    st.markdown(
        f"""{card_css}
        <div class="metric-card">
            <div class="metric-title">{title}</div>
            <div class="metric-value">{value}</div>
            {delta_html}
        </div>""",
        unsafe_allow_html=True,
    )


def ag_grid(df: pd.DataFrame, height: int = 420):
    """Paginated, sortable, filterable table using streamlit‑aggrid."""
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=20)
    gb.configure_default_column(filter=True, sortable=True, resizable=True)
    grid_options = gb.build()
    AgGrid(
        df,
        gridOptions=grid_options,
        height=height,
        fit_columns_on_grid_load=True,
        update_mode=GridUpdateMode.NO_UPDATE,
        allow_unsafe_jscode=True,
    )


# ------- Dark‑mode toggle (session state) -------
if "dark_mode" not in st.session_state:
    st.session_state["dark_mode"] = False


def toggle_dark():
    st.session_state["dark_mode"] = not st.session_state["dark_mode"]
    st.experimental_rerun()


# Show the tiny sun/moon button in the top‑right corner
toggle_label = "🌙" if not st.session_state["dark_mode"] else "☀️"
st.markdown(
    f"""<button class="dark-toggle" onClick="window.parent.postMessage({{'type':'toggle_dark'}}, '*');">{toggle_label}</button>""",
    unsafe_allow_html=True,
)

# Listen for the message (Streamlit >=1.27 forwards the message automatically)
if st.experimental_get_query_params().get("type") == ["toggle_dark"]:
    toggle_dark()


# If dark mode is active, inject an overwriting CSS block
if st.session_state["dark_mode"]:
    st.markdown(
        """
        <style>
        :root{
            --c-primary:#1a1a2e;   /* darker navy   */
            --c-accent:#5f0f40;    /* deep magenta */
            --c-ink:#f5f5f5;       /* light text   */
            --c-soft-teal:#16213e;
            --c-page-bg:#0f0f0f;
            --c-border:#2c2c2c;
        }
        html,body{background:var(--c-page-bg)!important;color:var(--c-ink)!important;}
        .ph,.sb-brand,.dlc{background:var(--c-soft-teal)!important;}
        .stButton>button{background:var(--c-accent)!important;}
        </style>
        """,
        unsafe_allow_html=True,
    )

# ─────────────────────────────────────────────────────────────────────────────
# 6️⃣ CONSTANT LISTS (Reps, Facilities, etc.)
# ─────────────────────────────────────────────────────────────────────────────
REPS = sorted(
    [
        "James Mwangi",
        "Faith Otieno",
        "Brian Koech",
        "Grace Auma",
        "Dennis Kiplangat",
        "Sharon Wanjiku",
        "Paul Mutua",
        "Lydia Chebet",
        "Moses Odhiambo",
        "Caroline Njeri",
    ]
)

FACILITIES = sorted(
    [
        "Moi Teaching & Referral Hospital",
        "Kenyatta National Hospital",
        "Aga Khan Hospital Nairobi",
        "MP Shah Hospital",
        "Nairobi Hospital",
        "AAR Hospital",
        "Coast General Hospital",
        "Eldoret Hospital",
        "Kisumu County Referral",
        "Nakuru Level 5 Hospital",
        "Thika Level 5 Hospital",
        "Mombasa Hospital",
        "Other",
    ]
)

REGIONS = [
    "East Africa",
    "West Africa",
    "North Africa",
    "Southern Africa",
    "Central Africa",
    "Middle East",
    "Europe",
    "Other",
]

SURGEONS = sorted(
    [
        "Dr. A. Kimani",
        "Dr. B. Otieno",
        "Dr. C. Waweru",
        "Dr. D. Mutai",
        "Dr. E. Achieng",
        "Dr. F. Njenga",
        "Dr. G. Kipchoge",
        "Dr. H. Omondi",
        "Dr. I. Wambua",
        "Dr. J. Chege",
        "Dr. K. Maina",
        "Dr. L. Rotich",
        "Dr. M. Abdi",
        "Dr. N. Kamau",
        "Dr. O. Simiyu",
        "Other",
    ]
)

PROCEDURES = sorted(
    [
        "Total Hip Replacement",
        "Total Knee Replacement",
        "Partial Knee Replacement",
        "Shoulder Arthroplasty",
        "Spinal Fusion L4-L5",
        "Spinal Fusion L5-S1",
        "Tibial Nail Fixation",
        "Femoral Nail Fixation",
        "DHS Plate Fixation",
        "Locking Plate Fixation",
        "ACL Reconstruction",
        "Revision Hip Replacement",
        "Revision Knee Replacement",
        "Humeral Nail Fixation",
        "Ankle Replacement",
        "External Fixator Application",
        "Proximal Femur Replacement",
        "Wrist Arthroplasty",
        "Other",
    ]
)

IMPLANTS = sorted(
    [
        "Total Hip Replacement System",
        "Total Knee Replacement System",
        "Partial Knee System",
        "Shoulder Arthroplasty System",
        "Spinal Fusion Cage",
        "Pedicle Screws",
        "Titanium Tibial Nail",
        "Femoral Intramedullary Nail",
        "DHS Plate & Screw",
        "Locking Compression Plate",
        "ACL Graft & Fixation",
        "Revision Hip Stem",
        "Revision Tibial Component",
        "Humeral Nail",
        "Total Ankle Replacement",
        "External Fixator Frame",
        "Proximal Femoral Prosthesis",
        "Bone Cement",
        "Augmentation Block",
        "Trial Components",
        "Other",
    ]
)


# ─────────────────────────────────────────────────────────────────────────────
# 7️⃣ SIDEBAR (navigation + live stats)
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        """
        <div class="sb-brand">
            <h2>🦴 ORTHOTRACK</h2>
            <p>Pro · Procedure Management</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    page = st.radio(
        "nav",
        [
            "📊  Dashboard",
            "➕  Add Procedure",
            "📋  Procedure Log",
            "📈  Analytics",
            "⬇️  Reports",
        ],
        label_visibility="collapsed",
    )

    # Live stats card (only if we have data)
    dfs = get_df()
    if not dfs.empty:
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div style='font-size:.65rem;color:#374151;letter-spacing:1.5px;padding:0 .2rem;margin-bottom:.3rem'>LIVE STATS</div>",
            unsafe_allow_html=True,
        )
        now_m = datetime.now()
        this_month = dfs[
            (dfs["date"].dt.month == now_m.month) & (dfs["date"].dt.year == now_m.year)
        ]

        stats = [
            (len(dfs), "Total Procedures"),
            (len(this_month), "This Month"),
            (dfs["rep"].nunique() if "rep" in dfs.columns else 0, "Active Reps"),
            (dfs["facility"].nunique() if "facility" in dfs.columns else 0, "Facilities"),
        ]
        for val, lbl in stats:
            st.markdown(
                f'<div class="sp"><div class="sv">{val}</div><div class="sl">{lbl}</div></div>',
                unsafe_allow_html=True,
            )
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    st.markdown(
        "<div style='font-size:.62rem;color:#374151;letter-spacing:1px;padding:0 .2rem'>v2.0 · OrthoTrack Pro</div>",
        unsafe_allow_html=True,
    )

# ─────────────────────────────────────────────────────────────────────────────
# 8️⃣ PAGE – DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────
if page == "📊  Dashboard":
    st.markdown(
        """
        <div class="ph">
            <div class="ph-badge">Live Dashboard</div>
            <h1>ORTHOTRACK PRO</h1>
            <p>Orthopedic Procedure Intelligence · Rep Performance · Regional Coverage</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    df = get_df()
    if df.empty:
        st.info("🦴 No procedures yet. Head to **Add Procedure** to get started!")
        st.stop()

    now = datetime.now()
    this_month = df[
        (df["date"].dt.month == now.month) & (df["date"].dt.year == now.year)
    ]

    # ---- top metrics (cards) ----
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Total Procedures", len(df), delta=str(len(this_month)))
    with c2:
        metric_card("Facilities", df["facility"].nunique())
    with c3:
        metric_card("Surgeons", df["surgeon"].nunique())
    with c4:
        metric_card("Active Reps", df["rep"].nunique())

    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

    # ---- Row 1 : Monthly bar + Region pie ----
    col1, col2 = st.columns([3, 2])
    with col1:
        monthly = df.groupby("month").size().reset_index(name="Count")
        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=monthly["month"],
                y=monthly["Count"],
                marker=dict(
                    color=monthly["Count"],
                    colorscale=COLOR["seq_teal"],
                    showscale=False,
                ),
                hovertemplate="%{x}<br><b>%{y} procedures</b><extra></extra>",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=monthly["month"],
                y=monthly["Count"],
                mode="lines",
                line=dict(color="#0D9488", width=2.5),
                hoverinfo="skip",
            )
        )
        sc(fig, "Monthly Procedure Volume", "seq_teal")
        fig.update_layout(showlegend=False, height=280)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        if "region" in df.columns:
            rc = df["region"].value_counts().reset_index()
            rc.columns = ["Region", "Count"]
            fig2 = px.pie(
                rc,
                values="Count",
                names="Region",
                color_discrete_sequence=px.colors.qualitative.Pastel,
                hole=0.4,
            )
            fig2.update_traces(textposition="inside", textinfo="percent+label")
            sc(fig2, "Coverage by Region")
            fig2.update_layout(showlegend=False, height=280)
            st.plotly_chart(fig2, use_container_width=True)

    # ---- Row 2 : Top reps / top procedures ----
    col3, col4 = st.columns(2)
    with col3:
        if "rep" in df.columns:
            rc2 = df["rep"].value_counts().head(10).reset_index()
            rc2.columns = ["Rep", "Count"]
            fig3 = px.bar(
                rc2,
                x="Count",
                y="Rep",
                orientation="h",
                color="Count",
                color_continuous_scale=COLOR["seq_blue"],
                text="Count",
            )
            fig3.update_traces(textposition="outside", textfont_size=10)
            sc(fig3, "Top Reps by Volume")
            fig3.update_layout(
                yaxis=dict(autorange="reversed"),
                showlegend=False,
                height=320,
                coloraxis_showscale=False,
            )
            st.plotly_chart(fig3, use_container_width=True)

    with col4:
        if "procedure" in df.columns:
            pc = df["procedure"].value_counts().head(8).reset_index()
            pc.columns = ["Procedure", "Count"]
            fig4 = px.bar(
                pc,
                x="Count",
                y="Procedure",
                orientation="h",
                color="Count",
                color_continuous_scale=["#CCFBF1", "#0D9488"],
                text="Count",
            )
            fig4.update_traces(textposition="outside", textfont_size=10)
            sc(fig4, "Top Procedure Types")
            fig4.update_layout(
                yaxis=dict(autorange="reversed"),
                showlegend=False,
                height=320,
                coloraxis_showscale=False,
            )
            st.plotly_chart(fig4, use_container_width=True)

    # ---- Row 3 : Top facilities + recent procedures table ----
    col5, col6 = st.columns([2, 3])
    with col5:
        if "facility" in df.columns:
            fc = df["facility"].value_counts().head(8).reset_index()
            fc.columns = ["Facility", "Count"]
            fig5 = px.bar(
                fc,
                x="Count",
                y="Facility",
                orientation="h",
                color="Count",
                color_continuous_scale=["#FEF3C7", "#F59E0B"],
                text="Count",
            )
            fig5.update_traces(textposition="outside")
            sc(fig5, "Top Facilities")
            fig5.update_layout(
                yaxis=dict(autorange="reversed"),
                showlegend=False,
                height=300,
                coloraxis_showscale=False,
            )
            st.plotly_chart(fig5, use_container_width=True)

    with col6:
        st.markdown("<div class='sec-lbl'>Recent Procedures</div>", unsafe_allow_html=True)
        rcols = [c for c in ["date", "invoice", "rep", "procedure", "facility", "surgeon"] if c in df.columns]
        rd = df.sort_values("date", ascending=False)[rcols].head(10).copy()
        if "date" in rd.columns:
            rd["date"] = rd["date"].dt.strftime("%d %b %Y")
        ag_grid(rd, height=300)

    # ---- Row 4 : Quarterly rep trend (if enough data) ----
    if "quarter" in df.columns and "rep" in df.columns:
        st.markdown("---")
        qr = df.groupby(["quarter", "rep"]).size().reset_index(name="Count")
        fig6 = px.line(
            qr,
            x="quarter",
            y="Count",
            color="rep",
            markers=True,
            color_discrete_sequence=px.colors.qualitative.Safe,
        )
        sc(fig6, "Quarterly Performance by Rep")
        fig6.update_layout(height=300, legend=dict(orientation="h", y=-0.25))
        st.plotly_chart(fig6, use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# 9️⃣ PAGE – ADD PROCEDURE
# ─────────────────────────────────────────────────────────────────────────────
elif page == "➕  Add Procedure":
    st.markdown(
        """
        <div class="ph">
            <div class="ph-badge">New Entry</div>
            <h1>ADD PROCEDURE</h1>
            <p>Log a new orthopedic procedure · All starred fields are required</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    raw = load_data()
    auto = next_inv(raw)

    # Card container for the whole form
    st.markdown(
        """
        <div style="background:#F0F4FF;border-left:4px solid #3282B8;
                    border-radius:8px;padding:1.6rem;margin-top:1rem;">
        """,
        unsafe_allow_html=True,
    )
    with st.form("add_form", clear_on_submit=True):
        # ---- Identification ----
        st.markdown("<div class='fs'>📋 Procedure Identification</div>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1:
            proc_date = st.date_input("📅 Date *", value=date.today())
        with c2:
            invoice = st.text_input("🧾 Invoice Number *", value=auto)
        with c3:
            rep_sel = st.selectbox("👤 Rep *", ["— Select —"] + REPS + ["Other"])
        rep_other = st.text_input("Rep full name *", key="rep_o") if rep_sel == "Other" else ""

        # ---- Location ----
        st.markdown("<div class='fs fst'>🏥 Location</div>", unsafe_allow_html=True)
        c4, c5 = st.columns(2)
        with c4:
            fac_sel = st.selectbox("🏥 Facility *", ["— Select —"] + FACILITIES)
        with c5:
            reg_sel = st.selectbox("🌍 Region *", ["— Select —"] + REGIONS)
        fac_other = st.text_input("Facility name *", key="fac_o") if fac_sel == "Other" else ""

        # ---- Clinical Details ----
        st.markdown("<div class='fs'>🔬 Clinical Details</div>", unsafe_allow_html=True)
        c6, c7 = st.columns(2)
        with c6:
            surg_sel = st.selectbox("👨‍⚕️ Surgeon *", ["— Select —"] + SURGEONS)
        with c7:
            proc_sel = st.selectbox("🔬 Procedure *", ["— Select —"] + PROCEDURES)
        surg_other = st.text_input("Surgeon full name *", key="surg_o") if surg_sel == "Other" else ""
        proc_other = st.text_input("Procedure name *", key="proc_o") if proc_sel == "Other" else ""

        implants_sel = st.multiselect("🦴 Implants Used *", IMPLANTS)

        # ---- Notes & Feedback ----
        st.markdown("<div class='fs fsa'>📝 Notes & Feedback</div>", unsafe_allow_html=True)
        c8, c9 = st.columns(2)
        with c8:
            challenges = st.text_area(
                "⚠️ Challenges Encountered",
                placeholder="Intra‑operative challenges, complications, delays…",
                height=110,
            )
        with c9:
            feedback = st.text_area(
                "💬 Surgeon / Outcome Feedback",
                placeholder="Post‑procedure feedback, surgeon comments, outcomes…",
                height=110,
            )

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        submitted = st.form_submit_button(
            "✅  Save Procedure", use_container_width=True, type="primary"
        )
    st.markdown("</div>", unsafe_allow_html=True)

    # ---- Validation & Save ----
    if submitted:
        # Resolve “Other” selections
        rep_f = rep_other.strip() if rep_sel == "Other" else rep_sel
        fac_f = fac_other.strip() if fac_sel == "Other" else fac_sel
        surg_f = surg_other.strip() if surg_sel == "Other" else surg_sel
        proc_f = proc_other.strip() if proc_sel == "Other" else proc_sel

        errs = []
        if not invoice.strip():
            errs.append("Invoice Number")
        if rep_sel == "— Select —":
            errs.append("Rep")
        if rep_sel == "Other" and not rep_f:
            errs.append("Rep Name")
        if fac_sel == "— Select —":
            errs.append("Facility")
        if fac_sel == "Other" and not fac_f:
            errs.append("Facility Name")
        if reg_sel == "— Select —":
            errs.append("Region")
        if surg_sel == "— Select —":
            errs.append("Surgeon")
        if surg_sel == "Other" and not surg_f:
            errs.append("Surgeon Name")
        if proc_sel == "— Select —":
            errs.append("Procedure")
        if proc_sel == "Other" and not proc_f:
            errs.append("Procedure Name")
        if not implants_sel:
            errs.append("Implants Used")
        if invoice.strip() in [r.get("invoice", "") for r in raw]:
            errs.append(f"Invoice {invoice.strip()} already exists")

        if errs:
            st.error(f"Please fix: **{' · '.join(errs)}**")
        else:
            rec = {
                "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
                "date": str(proc_date),
                "invoice": invoice.strip(),
                "rep": rep_f,
                "facility": fac_f,
                "region": reg_sel,
                "surgeon": surg_f,
                "procedure": proc_f,
                "implants": implants_sel,
                "challenges": challenges.strip() or "None",
                "feedback": feedback.strip() or "—",
                "logged_at": datetime.now().isoformat(),
            }
            raw.append(rec)
            save_data(raw)
            bust()
            st.success(f"✅ Saved — Invoice **{invoice.strip()}** · {proc_f} · {fac_f}")
            st.balloons()


# ─────────────────────────────────────────────────────────────────────────────
# 🔟 PAGE – PROCEDURE LOG
# ─────────────────────────────────────────────────────────────────────────────
elif page == "📋  Procedure Log":
    st.markdown(
        """
        <div class="ph">
            <div class="ph-badge">Records</div>
            <h1>PROCEDURE LOG</h1>
            <p>Search, filter, view, edit and manage all logged procedures</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    df = get_df()
    if df.empty:
        st.info("No procedures found. Add one to get started!")
        st.stop()

    # ---- Filters ------------------------------------------------------------
    with st.expander("🔍  Filters", expanded=True):
        fc1, fc2, fc3, fc4 = st.columns(4)
        with fc1:
            sr = st.selectbox(
                "Rep",
                ["All"] + sorted(df["rep"].dropna().unique().tolist())
                if "rep" in df.columns
                else ["All"],
            )
        with fc2:
            sg = st.selectbox(
                "Region",
                ["All"] + sorted(df["region"].dropna().unique().tolist())
                if "region" in df.columns
                else ["All"],
            )
        with fc3:
            sf = st.selectbox(
                "Facility",
                ["All"] + sorted(df["facility"].dropna().unique().tolist())
                if "facility" in df.columns
                else ["All"],
            )
        with fc4:
            sp = st.selectbox(
                "Procedure",
                ["All"] + sorted(df["procedure"].dropna().unique().tolist())
                if "procedure" in df.columns
                else ["All"],
            )
        dc1, dc2, dc3 = st.columns([2, 2, 3])
        with dc1:
            d_from = st.date_input("From", value=df["date"].min().date())
        with dc2:
            d_to = st.date_input("To", value=df["date"].max().date())
        with dc3:
            q = st.text_input(
                "🔎 Search invoice / surgeon / facility / rep",
                placeholder="Type to search…",
            )

    # ---- Apply filters ------------------------------------------------------
    flt = df.copy()
    if sr != "All":
        flt = flt[flt["rep"] == sr]
    if sg != "All":
        flt = flt[flt["region"] == sg]
    if sf != "All":
        flt = flt[flt["facility"] == sf]
    if sp != "All":
        flt = flt[flt["procedure"] == sp]
    flt = flt[(flt["date"].dt.date >= d_from) & (flt["date"].dt.date <= d_to)]

    if q.strip():
        qx = q.strip().lower()
        mask = pd.Series(False, index=flt.index)
        for col in ["invoice", "surgeon", "facility", "rep", "procedure"]:
            if col in flt.columns:
                mask |= flt[col].astype(str).str.lower().str.contains(qx, na=False)
        flt = flt[mask]

    # ---- Sorting ------------------------------------------------------------
    ch1, ch2 = st.columns([3, 1])
    with ch1:
        st.markdown(
            f"<div class='sec-lbl'>Showing {len(flt)} of {len(df)} procedures</div>",
            unsafe_allow_html=True,
        )
    with ch2:
        srt = st.selectbox(
            "Sort",
            ["Date ↓", "Date ↑", "Rep", "Facility", "Invoice"],
            label_visibility="collapsed",
        )
    sort_map = {
        "Date ↓": ("date", False),
        "Date ↑": ("date", True),
        "Rep": ("rep", True),
        "Facility": ("facility", True),
        "Invoice": ("invoice", True),
    }
    sort_col, asc = sort_map[srt]
    flt = flt.sort_values(sort_col, ascending=asc)

    # ---- Grid view -----------------------------------------------------------
    disp_cols = [
        c
        for c in ["date", "invoice", "rep", "procedure", "facility", "region", "surgeon"]
        if c in flt.columns
    ]
    disp = flt[disp_cols].copy()
    if "date" in disp.columns:
        disp["date"] = disp["date"].dt.strftime("%d %b %Y")
    ag_grid(disp, height=380)

    # ---- Detail view ---------------------------------------------------------
    st.markdown("---")
    st.markdown("### 🔍 Record Detail")
    if flt.empty:
        st.info("No records match your filters.")
    else:
        invoice_list = flt.sort_values("date", ascending=False)["invoice"].tolist()
        selected_invoice = st.selectbox("Select Invoice", invoice_list, key="detail")
        rec = flt[flt["invoice"] == selected_invoice].iloc[0]

        # split into three columns
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            for lbl, val in [
                ("Date", rec["date"].strftime("%d %b %Y")),
                ("Invoice", rec["invoice"]),
                ("Rep", rec["rep"]),
            ]:
                st.markdown(
                    f'<div class="rf"><div class="rl">{lbl}</div><div class="rv">{val}</div></div>',
                    unsafe_allow_html=True,
                )
        with col_b:
            for lbl, val in [
                ("Facility", rec["facility"]),
                ("Region", rec["region"]),
                ("Surgeon", rec["surgeon"]),
            ]:
                st.markdown(
                    f'<div class="rf"><div class="rl">{lbl}</div><div class="rv">{val}</div></div>',
                    unsafe_allow_html=True,
                )
        with col_c:
            for lbl, val in [
                ("Procedure", rec["procedure"]),
                ("Logged At", str(rec.get("logged_at", ""))[:16]),
            ]:
                st.markdown(
                    f'<div class="rf"><div class="rl">{lbl}</div><div class="rv">{val}</div></div>',
                    unsafe_allow_html=True,
                )

        # Implants (chips)
        impl = rec.get("implants", [])
        if isinstance(impl, list) and impl:
            chips = " ".join([f'<span class="chip">{i}</span>' for i in impl])
            st.markdown(
                f'<div class="rf"><div class="rl">Implants Used</div><div class="rv">{chips}</div></div>',
                unsafe_allow_html=True,
            )

        # Challenges & Feedback
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            st.markdown(
                f'<div class="rf"><div class="rl">⚠️ Challenges</div><div class="rv">{rec.get("challenges","—")}</div></div>',
                unsafe_allow_html=True,
            )
        with col_c2:
            st.markdown(
                f'<div class="rf"><div class="rl">💬 Feedback</div><div class="rv">{rec.get("feedback","—")}</div></div>',
                unsafe_allow_html=True,
            )

    # ---- Edit a record ------------------------------------------------------
    st.markdown("---")
    with st.expander("✏️  Edit a Record"):
        edit_inv = st.text_input("Invoice number to edit", key="edit_inv")
        raw = load_data()
        match = [r for r in raw if r.get("invoice") == edit_inv.strip()]
        if edit_inv.strip() and match:
            rec = match[0]
            with st.form("edit_form"):
                ec1, ec2, ec3 = st.columns(3)
                with ec1:
                    e_date = st.date_input(
                        "Date", value=date.fromisoformat(str(rec["date"])[:10])
                    )
                with ec2:
                    e_rep = st.selectbox("Rep", REPS, index=REPS.index(rec["rep"]))
                with ec3:
                    e_fac = st.selectbox(
                        "Facility", FACILITIES, index=FACILITIES.index(rec["facility"])
                    )
                ec4, ec5 = st.columns(2)
                with ec4:
                    e_region = st.selectbox(
                        "Region", REGIONS, index=REGIONS.index(rec["region"])
                    )
                with ec5:
                    e_surg = st.selectbox(
                        "Surgeon", SURGEONS, index=SURGEONS.index(rec["surgeon"])
                    )
                e_proc = st.text_input("Procedure", value=rec.get("procedure", ""))
                e_impl = st.multiselect("Implants Used", IMPLANTS, default=rec.get("implants", []))
                e_chal = st.text_area("Challenges", value=rec.get("challenges", ""), height=80)
                e_fb = st.text_area("Feedback", value=rec.get("feedback", ""), height=80)

                if st.form_submit_button("💾 Save Changes", type="primary"):
                    rec.update(
                        {
                            "date": str(e_date),
                            "rep": e_rep,
                            "facility": e_fac,
                            "region": e_region,
                            "surgeon": e_surg,
                            "procedure": e_proc,
                            "implants": e_impl,
                            "challenges": e_chal,
                            "feedback": e_fb,
                        }
                    )
                    save_data(raw)
                    bust()
                    st.success("Record updated!")
                    st.rerun()
        elif edit_inv.strip():
            st.warning("Invoice not found.")

    # ---- Delete a record ----------------------------------------------------
    with st.expander("🗑️  Delete a Record"):
        del_inv = st.text_input("Invoice number to delete", key="del_inv")
        if st.button("🗑️  Delete Record", type="primary"):
            raw = load_data()
            new_raw = [r for r in raw if r.get("invoice") != del_inv.strip()]
            if len(new_raw) < len(raw):
                save_data(new_raw)
                bust()
                st.success(f"Deleted `{del_inv}`")
                st.rerun()
            else:
                st.warning("Invoice not found.")


# ─────────────────────────────────────────────────────────────────────────────
# 1️⃣1️⃣ PAGE – ANALYTICS
# ─────────────────────────────────────────────────────────────────────────────
elif page == "📈  Analytics":
    st.markdown(
        """
        <div class="ph">
            <div class="ph-badge">Insights</div>
            <h1>ANALYTICS</h1>
            <p>Deep‑dive into rep performance, facility coverage, procedure trends and implant usage</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    df = get_df()
    if df.empty:
        st.info("No data available. Add procedures to unlock analytics.")
        st.stop()

    with st.expander("⚙️  Filter Analytics", expanded=False):
        f1, f2 = st.columns(2)
        with f1:
            sel_year = st.selectbox(
                "Year",
                ["All"] + sorted(df["year"].dropna().astype(str).unique().tolist(), reverse=True),
            )
        with f2:
            sel_rep = st.selectbox(
                "Rep",
                ["All"] + sorted(df["rep"].dropna().unique().tolist()) if "rep" in df.columns else ["All"],
            )
    adf = df.copy()
    if sel_year != "All":
        adf = adf[adf["year"].astype(str) == sel_year]
    if sel_rep != "All":
        adf = adf[adf["rep"] == sel_rep]

    tab1, tab2, tab3, tab4 = st.tabs(["📅  Trends", "🏥  Facility & Region", "👤  Rep Performance", "🦴  Implants"])

    # ────────── Trends ──────────
    with tab1:
        # Monthly volume (area)
        mo = adf.groupby("month").size().reset_index(name="Count")
        fig = px.area(
            mo,
            x="month",
            y="Count",
            color_discrete_sequence=[COLOR["accent"]],
        )
        fig.update_traces(fill="tozeroy", fillcolor="rgba(50,130,184,.12)", line=dict(width=2.5, color="#0D9488"))
        sc(fig, "Monthly Procedure Volume", "seq_teal")
        fig.update_layout(height=280)
        st.plotly_chart(fig, use_container_width=True)

        # Day‑of‑week bar
        dow_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        dow = adf["date"].dt.day_name().value_counts().reindex(dow_order, fill_value=0).reset_index()
        dow.columns = ["Day", "Count"]
        fig2 = px.bar(
            dow,
            x="Day",
            y="Count",
            color="Count",
            color_continuous_scale=COLOR["seq_orange"],
        )
        fig2.update_traces(text=dow["Count"], textposition="outside")
        sc(fig2, "Volume by Day of Week")
        fig2.update_layout(height=280, showlegend=False, coloraxis_showscale=False)
        st.plotly_chart(fig2, use_container_width=True)

        # Quarterly‑by‑rep (if present)
        if "quarter" in adf.columns and "rep" in adf.columns:
            qr = adf.groupby(["quarter", "rep"]).size().reset_index(name="Count")
            fig3 = px.line(
                qr,
                x="quarter",
                y="Count",
                color="rep",
                markers=True,
                color_discrete_sequence=px.colors.qualitative.Safe,
            )
            sc(fig3, "Quarterly Trends by Rep")
            fig3.update_layout(height=300, legend=dict(orientation="h", y=-0.25))
            st.plotly_chart(fig3, use_container_width=True)

        # Top procedures over time
        if "procedure" in adf.columns:
            top6 = adf["procedure"].value_counts().head(6).index.tolist()
            sub = adf[adf["procedure"].isin(top6)].groupby(["month", "procedure"]).size().reset_index(name="Count")
            fig4 = px.line(
                sub,
                x="month",
                y="Count",
                color="procedure",
                markers=True,
                color_discrete_sequence=px.colors.qualitative.Pastel,
            )
            sc(fig4, "Top Procedure Types Over Time")
            fig4.update_layout(height=300, legend=dict(orientation="h", y=-0.25))
            st.plotly_chart(fig4, use_container_width=True)

    # ────────── Facility & Region ──────────
    with tab2:
        c1, c2 = st.columns(2)
        with c1:
            if "facility" in adf.columns:
                fc = adf["facility"].value_counts().reset_index()
                fc.columns = ["Facility", "Count"]
                fig = px.bar(
                    fc,
                    x="Count",
                    y="Facility",
                    orientation="h",
                    color="Count",
                    color_continuous_scale=[COLOR["soft_teal"], COLOR["accent"]],
                )
                fig.update_traces(text=fc["Count"], textposition="outside")
                sc(fig, "Procedures by Facility")
                fig.update_layout(yaxis=dict(autorange="reversed"), height=380, showlegend=False, coloraxis_showscale=False)
                st.plotly_chart(fig, use_container_width=True)

        with c2:
            if "region" in adf.columns:
                rg = adf["region"].value_counts().reset_index()
                rg.columns = ["Region", "Count"]
                fig = px.pie(
                    rg,
                    values="Count",
                    names="Region",
                    hole=0.45,
                    color_discrete_sequence=px.colors.qualitative.Vivid,
                )
                fig.update_traces(textposition="inside", textinfo="percent+label")
                sc(fig, "Regional Distribution")
                fig.update_layout(height=380, showlegend=True)
                st.plotly_chart(fig, use_container_width=True)

        # Heatmap Region × Procedure
        if "region" in adf.columns and "procedure" in adf.columns:
            hm = adf.groupby(["region", "procedure"]).size().unstack(fill_value=0)
            fig = px.imshow(
                hm,
                color_continuous_scale="Blues",
                aspect="auto",
                text_auto=True,
            )
            sc(fig, "Region × Procedure Heatmap")
            fig.update_layout(height=380, coloraxis_showscale=False)
            st.plotly_chart(fig, use_container_width=True)

    # ────────── Rep Performance ──────────
    with tab3:
        if "rep" in adf.columns:
            # Summary table
            rs = (
                adf.groupby("rep")
                .agg(
                    Procedures=("id", "count"),
                    Facilities=("facility", "nunique"),
                    Surgeons=("surgeon", "nunique"),
                    Regions=("region", "nunique"),
                )
                .reset_index()
                .sort_values("Procedures", ascending=False)
            )
            st.markdown("#### Rep Performance Summary")
            st.dataframe(rs, use_container_width=True, hide_index=True)

            c1, c2 = st.columns(2)
            with c1:
                fig = px.bar(
                    rs.head(10),
                    x="Procedures",
                    y="rep",
                    orientation="h",
                    color="Procedures",
                    color_continuous_scale=[COLOR["soft_teal"], COLOR["accent"]],
                    text="Procedures",
                )
                fig.update_traces(textposition="outside")
                sc(fig, "Total Procedures per Rep")
                fig.update_layout(yaxis=dict(autorange="reversed"), height=340, showlegend=False, coloraxis_showscale=False)
                st.plotly_chart(fig, use_container_width=True)

            with c2:
                fig = px.scatter(
                    rs,
                    x="Facilities",
                    y="Procedures",
                    hover_name="rep",
                    size="Procedures",
                    color="Regions",
                    color_continuous_scale=COLOR["seq_blue"],
                )
                sc(fig, "Reach: Procedures vs Facilities")
                fig.update_traces(textposition="top center", textfont_size=9)
                fig.update_layout(height=340, showlegend=False, coloraxis_showscale=False)
                st.plotly_chart(fig, use_container_width=True)

            # Heatmap (rep × month)
            rm = adf.groupby(["rep", "month"]).size().unstack(fill_value=0)
            fig = px.imshow(
                rm,
                color_continuous_scale="Blues",
                aspect="auto",
                text_auto=True,
            )
            sc(fig, "Rep Activity Heatmap (Monthly)")
            fig.update_layout(height=360, coloraxis_showscale=False)
            st.plotly_chart(fig, use_container_width=True)

    # ────────── Implants ──────────
    with tab4:
        if "implants" in adf.columns:
            imp = adf["implants"].dropna().explode().value_counts().reset_index()
            imp.columns = ["Implant", "Count"]

            c1, c2 = st.columns(2)
            with c1:
                fig = px.bar(
                    imp.head(12),
                    x="Count",
                    y="Implant",
                    orientation="h",
                    color="Count",
                    color_continuous_scale=[COLOR["soft_teal"], COLOR["accent"]],
                    text="Count",
                )
                fig.update_traces(textposition="outside")
                sc(fig, "Most Used Implants")
                fig.update_layout(yaxis=dict(autorange="reversed"), height=380, showlegend=False, coloraxis_showscale=False)
                st.plotly_chart(fig, use_container_width=True)

            with c2:
                fig = px.pie(
                    imp.head(10),
                    values="Count",
                    names="Implant",
                    hole=0.4,
                    color_discrete_sequence=px.colors.qualitative.Pastel,
                )
                fig.update_traces(textposition="inside", textinfo="percent+label")
                sc(fig, "Implant Mix (Top 10)")
                fig.update_layout(height=380, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)

            # Implant trend over time (top 6)
            adf2 = adf.copy()
            adf2 = adf2.explode("implants")
            top6 = adf2["implants"].value_counts().head(6).index.tolist()
            sub = adf2[adf2["implants"].isin(top6)].groupby(["month", "implants"]).size().reset_index(name="Count")
            fig = px.line(
                sub,
                x="month",
                y="Count",
                color="implants",
                markers=True,
                color_discrete_sequence=px.colors.qualitative.Vivid,
            )
            sc(fig, "Top Implant Usage Over Time")
            fig.update_layout(height=300, legend=dict(orientation="h", y=-0.25))
            st.plotly_chart(fig, use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# 1️⃣2️⃣ PAGE – REPORTS
# ─────────────────────────────────────────────────────────────────────────────
elif page == "⬇️  Reports":
    st.markdown(
        """
        <div class="ph">
            <div class="ph-badge">Export</div>
            <h1>REPORTS</h1>
            <p>Generate and download professional procedure reports in PDF, Excel or CSV</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    df = get_df()
    if df.empty:
        st.info("No procedures to report on yet.")
        st.stop()

    st.markdown("### ⚙️ Configure Report")
    rb1, rb2 = st.columns(2)
    with rb1:
        scope = st.selectbox(
            "Report Scope",
            [
                "All Procedures",
                "By Rep",
                "By Region",
                "By Facility",
                "By Procedure Type",
                "Date Range",
            ],
        )
    with rb2:
        fmt = st.selectbox("Export Format", ["📄 PDF (Branded)", "📊 Excel Workbook (.xlsx)", "📑 CSV"])

    # ---- Filter according to chosen scope ----
    filtered = df.copy()
    label = "All Procedures"

    if scope == "By Rep" and "rep" in df.columns:
        pick = st.selectbox("Select Rep", sorted(df["rep"].dropna().unique().tolist()))
        filtered = df[df["rep"] == pick]
        label = f"Rep: {pick}"
    elif scope == "By Region" and "region" in df.columns:
        pick = st.selectbox("Select Region", sorted(df["region"].dropna().unique().tolist()))
        filtered = df[df["region"] == pick]
        label = f"Region: {pick}"
    elif scope == "By Facility" and "facility" in df.columns:
        pick = st.selectbox("Select Facility", sorted(df["facility"].dropna().unique().tolist()))
        filtered = df[df["facility"] == pick]
        label = f"Facility: {pick}"
    elif scope == "By Procedure Type" and "procedure" in df.columns:
        pick = st.selectbox("Select Procedure", sorted(df["procedure"].dropna().unique().tolist()))
        filtered = df[df["procedure"] == pick]
        label = f"Procedure: {pick}"
    elif scope == "Date Range":
        dr1, dr2 = st.columns(2)
        with dr1:
            d_from = st.date_input("From", value=df["date"].min().date())
        with dr2:
            d_to = st.date_input("To", value=df["date"].max().date())
        filtered = df[(df["date"].dt.date >= d_from) & (df["date"].dt.date <= d_to)]
        label = f"{d_from.strftime('%d %b %Y')} – {d_to.strftime('%d %b %Y')}"

    # ---- Summary cards ----
    st.markdown("---")
    st.markdown("### 📋 Report Preview")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Procedures", len(filtered))
    with c2:
        metric_card("Facilities", filtered["facility"].nunique() if "facility" in filtered.columns else 0)
    with c3:
        metric_card("Surgeons", filtered["surgeon"].nunique() if "surgeon" in filtered.columns else 0)
    with c4:
        metric_card("Reps", filtered["rep"].nunique() if "rep" in filtered.columns else 0)

    if not filtered.empty:
        preview_cols = [c for c in ["date", "invoice", "rep", "procedure", "facility", "surgeon"] if c in filtered.columns]
        preview = filtered.sort_values("date", ascending=False)[preview_cols].head(6).copy()
        if "date" in preview.columns:
            preview["date"] = preview["date"].dt.strftime("%d %b %Y")
        st.dataframe(preview, use_container_width=True, hide_index=True)

    # ---- Download section ----
    st.markdown("---")
    st.markdown("### ⬇️ Download")
    report_title = f"OrthoTrack Pro — {label}"
    ts = datetime.now().strftime("%Y%m%d_%H%M")

    if "PDF" in fmt:
        st.markdown(
            """
            <div class="dlc">
                <div class="di">📄</div>
                <div class="dt">Branded PDF Report</div>
                <div class="dd">Professional report with branding, summary stats & procedure log</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("📄 Generate PDF", type="primary", use_container_width=True):
            with st.spinner("Building PDF…"):
                pdf_buf = build_pdf(filtered, report_title, label)
            st.download_button(
                "⬇️ Download PDF",
                data=pdf_buf,
                file_name=f"orthotrack_{ts}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

    elif "Excel" in fmt:
        st.markdown(
            """
            <div class="dlc">
                <div class="di">📊</div>
                <div class="dt">Excel Workbook</div>
                <div class="dd">3‑sheet workbook: Procedures · Summary Statistics · Regional Breakdown</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("📊 Generate Excel", type="primary", use_container_width=True):
            with st.spinner("Building Excel workbook…"):
                excel_buf = build_excel(filtered, report_title)
            st.download_button(
                "⬇️ Download Excel",
                data=excel_buf,
                file_name=f"orthotrack_{ts}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )

    elif "CSV" in fmt:
        st.markdown(
            """
            <div class="dlc">
                <div class="di">📑</div>
                <div class="dt">CSV Export</div>
                <div class="dd">Raw data – all columns, all rows, ready for BI tools</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        csv_df = filtered.copy()
        if "date" in csv_df.columns:
            csv_df["date"] = csv_df["date"].dt.strftime("%Y-%m-%d")
        if "implants" in csv_df.columns:
            csv_df["implants"] = csv_df["implants"].apply(
                lambda x: ", ".join(x) if isinstance(x, list) else str(x)
            )
        for drop_col in ["month", "year", "quarter"]:
            if drop_col in csv_df.columns:
                csv_df.drop(columns=drop_col, inplace=True)
        csv_bytes = csv_df.to_csv(index=False).encode()
        st.download_button(
            "⬇️ Download CSV",
            data=csv_bytes,
            file_name=f"orthotrack_{ts}.csv",
            mime="text/csv",
            use_container_width=True,
        )


# ─────────────────────────────────────────────────────────────────────────────
# 13️⃣ PDF & EXCEL BUILDERS (unchanged, just reused)
# ─────────────────────────────────────────────────────────────────────────────
def build_pdf(df: pd.DataFrame, title: str, subtitle: str = "") -> io.BytesIO:
    """Create a branded PDF using ReportLab."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=1.8 * cm,
        rightMargin=1.8 * cm,
        topMargin=2 * cm,
        bottomMargin=1.8 * cm,
    )
    S = getSampleStyleSheet()
    ink = colors.HexColor(COLOR["ink"])
    cobalt = colors.HexColor(COLOR["accent"])
    border = colors.HexColor(COLOR["border"])
    muted = colors.HexColor(COLOR["border"])
    story = []

    # Header
    story.append(
        Paragraph(
            "ORTHOTRACK PRO",
            ParagraphStyle(
                "Header",
                fontName="Helvetica-Bold",
                fontSize=20,
                textColor=cobalt,
                spaceAfter=2,
                letterSpacing=4,
            ),
        )
    )
    story.append(Paragraph(title, ParagraphStyle("Title", fontName="Helvetica-Bold", fontSize=14, textColor=ink, spaceAfter=4)))
    if subtitle:
        story.append(Paragraph(subtitle, ParagraphStyle("Sub", fontName="Helvetica", fontSize=9, textColor=muted, spaceAfter=2)))
    story.append(
        Paragraph(
            f"Generated {datetime.now().strftime('%d %B %Y  ·  %H:%M')}   ·   {len(df)} record(s)",
            ParagraphStyle("Meta", fontName="Helvetica", fontSize=8, textColor=muted, spaceAfter=8),
        )
    )
    story.append(HRFlowable(width="100%", thickness=2, color=cobalt, spaceAfter=12))

    # Summary stats table
    nf = df["facility"].nunique() if "facility" in df.columns else 0
    ns = df["surgeon"].nunique() if "surgeon" in df.columns else 0
    nr = df["rep"].nunique() if "rep" in df.columns else 0
    ng = df["region"].nunique() if "region" in df.columns else 0
    sum_table = [
        ["PROCEDURES", "FACILITIES", "SURGEONS", "REPS", "REGIONS"],
        [str(len(df)), str(nf), str(ns), str(nr), str(ng)],
    ]
    t = Table(sum_table, colWidths=[2.8 * cm] * 5)
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), ink),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 7),
                ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor(COLOR["page_bg"])),
                ("FONTNAME", (0, 1), (-1, 1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 1), (-1, 1), 14),
                ("TEXTCOLOR", (0, 1), (-1, 1), ink),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                ("BOX", (0, 0), (-1, -1), 0.5, border),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, border),
            ]
        )
    )
    story.append(t)
    story.append(Spacer(1, 14))

    # Procedure log table (first 200 rows)
    story.append(Paragraph("PROCEDURE LOG", ParagraphStyle("TableTitle", fontName="Helvetica-Bold", fontSize=7, textColor=cobalt, spaceBefore=4, spaceAfter=6, letterSpacing=2)))
    wanted = ["date", "invoice", "rep", "facility", "region", "surgeon", "procedure", "implants"]
    present = [c for c in wanted if c in df.columns]
    cw_map = {
        "date": 10 * mm,
        "invoice": 18 * mm,
        "rep": 22 * mm,
        "facility": 27 * mm,
        "region": 17 * mm,
        "surgeon": 22 * mm,
        "procedure": 26 * mm,
        "implants": 28 * mm,
    }
    cwidths = [cw_map.get(c, 20 * mm) for c in present]
    rows = [[c.upper() for c in present]]
    for _, row in df.sort_values("date", ascending=False).head(200).iterrows():
        r = []
        for c in present:
            v = row.get(c, "")
            if c == "date":
                try:
                    v = pd.to_datetime(v).strftime("%d %b %Y")
                except Exception:
                    pass
            elif c == "implants" and isinstance(v, list):
                v = ", ".join(v)
            v = str(v)
            if len(v) > 26:
                v = v[:24] + "…"
            r.append(v)
        rows.append(r)

    t = Table(rows, colWidths=cwidths, repeatRows=1)
    # zebra striping
    bg = []
    for i in range(1, len(rows)):
        bg.append(("BACKGROUND", (0, i), (-1, i), colors.white if i % 2 else colors.HexColor("#F8FAFC")))
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), ink),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 7),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("TEXTCOLOR", (0, 1), (-1, -1), ink),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("BOX", (0, 0), (-1, -1), 0.5, border),
                ("INNERGRID", (0, 0), (-1, -1), 0.3, border),
                *bg,
            ]
        )
    )
    story.append(t)
    if len(df) > 200:
        story.append(Spacer(1, 8))
        story.append(
            Paragraph(
                f"… and {len(df)-200} more. Download Excel/CSV for full dataset.",
                ParagraphStyle("Note", fontName="Helvetica-Oblique", fontSize=8, textColor=muted),
            )
        )
    doc.build(story)
    buf.seek(0)
    return buf


def build_excel(df: pd.DataFrame, title: str) -> io.BytesIO:
    """Create a formatted Excel workbook (Procedures + Summary sheets)."""
    buf = io.BytesIO()
    wb = xlsxwriter.Workbook(buf, {"in_memory": True})

    def fmt(**kw):
        return wb.add_format({**kw, "font_name": "Calibri"})

    # Common formats
    f_title = fmt(bold=True, font_size=16, font_color=COLOR["ink"])
    f_sub = fmt(font_size=9, font_color=COLOR["border"], italic=True)
    f_hdr = fmt(
        bold=True,
        font_size=9,
        font_color="white",
        bg_color=COLOR["primary"],
        border=1,
        border_color=COLOR["border"],
        align="center",
        valign="vcenter",
        text_wrap=True,
    )
    f_cell = fmt(font_size=9, border=1, border_color=COLOR["border"], valign="vcenter")
    f_alt = fmt(
        font_size=9,
        border=1,
        border_color=COLOR["border"],
        bg_color=COLOR["card_bg"],
        valign="vcenter",
    )
    f_date = fmt(font_size=9, border=1, border_color=COLOR["border"], num_format="dd mmm yyyy", valign="vcenter")
    f_date_alt = fmt(
        font_size=9,
        border=1,
        border_color=COLOR["border"],
        bg_color=COLOR["card_bg"],
        num_format="dd mmm yyyy",
        valign="vcenter",
    )
    f_stat_key = fmt(bold=True, font_size=9, font_color=COLOR["primary"], bg_color="#EFF6FF", border=1, border_color=COLOR["border"])
    f_stat_val = fmt(bold=True, font_size=18, font_color=COLOR["accent"], bg_color="#EFF6FF", border=1, border_color=COLOR["border"])

    # ---------- Sheet 1 – Procedures ----------
    ws = wb.add_worksheet("Procedures")
    ws.set_zoom(90)
    ws.freeze_panes(5, 0)
    ws.merge_range("A1:J1", "OrthoTrack Pro — " + title, f_title)
    ws.write("A2", f"Exported {datetime.now().strftime('%d %B %Y  ·  %H:%M')}   ·   {len(df)} records", f_sub)
    ws.set_row(0, 26)
    ws.set_row(1, 14)
    ws.set_row(2, 6)
    ws.set_row(3, 20)

    cols = [c for c in ["date", "invoice", "rep", "facility", "region", "surgeon", "procedure", "implants", "challenges", "feedback"] if c in df.columns]
    col_widths = {
        "date": 13,
        "invoice": 16,
        "rep": 22,
        "facility": 30,
        "region": 16,
        "surgeon": 22,
        "procedure": 28,
        "implants": 35,
        "challenges": 40,
        "feedback": 40,
    }
    for ci, col in enumerate(cols):
        ws.write(3, ci, col.upper(), f_hdr)
        ws.set_column(ci, ci, col_widths.get(col, 18))

    for ri, (_, row) in enumerate(df.sort_values("date", ascending=False).iterrows()):
        alt = ri % 2 == 1
        ws.set_row(ri + 4, 16)
        for ci, col in enumerate(cols):
            v = row.get(col, "")
            if isinstance(v, list):
                v = ", ".join(v)
            if col == "date":
                try:
                    dt = pd.to_datetime(v).to_pydatetime()
                except Exception:
                    dt = None
                if dt:
                    ws.write_datetime(ri + 4, ci, dt, f_date_alt if alt else f_date)
                    continue
            if not isinstance(v, str) and pd.isna(v):
                v = ""
            cf = f_alt if alt else f_cell
            ws.write(ri + 4, ci, str(v), cf)

    # ---------- Sheet 2 – Summary ----------
    ws2 = wb.add_worksheet("Summary")
    ws2.set_column("A:A", 28)
    ws2.set_column("B:B", 16)
    ws2.set_zoom(95)
    ws2.merge_range("A1:B1", "OrthoTrack Pro — Summary Statistics", f_title)
    ws2.merge_range("A2:B2", f"Generated {datetime.now().strftime('%d %B %Y')}", f_sub)
    ws2.set_row(0, 26)
    ws2.set_row(1, 14)
    ws2.set_row(2, 6)

    stats = [
        ("Total Procedures", len(df)),
        ("Unique Facilities", df["facility"].nunique() if "facility" in df.columns else 0),
        ("Unique Surgeons", df["surgeon"].nunique() if "surgeon" in df.columns else 0),
        ("Unique Reps", df["rep"].nunique() if "rep" in df.columns else 0),
        ("Regions Covered", df["region"].nunique() if "region" in df.columns else 0),
    ]
    for i, (k, v) in enumerate(stats):
        ws2.set_row(i + 3, 26)
        ws2.write(i + 3, 0, k, f_stat_key)
        ws2.write(i + 3, 1, v, f_stat_val)

    # Rep breakdown
    start = len(stats) + 5
    ws2.merge_range(start, 0, start, 1, "PROCEDURES BY REP", f_stat_key)
    if "rep" in df.columns:
        for i, (rep, cnt) in enumerate(df["rep"].value_counts().items()):
            ws2.set_row(start + 1 + i, 16)
            fmt_row = f_alt if i % 2 else f_cell
            ws2.write(start + 1 + i, 0, rep, fmt_row)
            ws2.write(start + 1 + i, 1, cnt, fmt_row)

    # ---------- Sheet 3 – By Region ----------
    ws3 = wb.add_worksheet("By Region")
    ws3.set_column("A:A", 24)
    ws3.set_column("B:B", 14)
    ws3.set_zoom(95)
    ws3.merge_range("A1:B1", "Procedures by Region", f_title)
    ws3.set_row(0, 24)
    ws3.set_row(1, 6)
    ws3.set_row(2, 20)
    ws3.write(2, 0, "REGION", f_stat_key)
    ws3.write(2, 1, "PROCEDURES", f_stat_key)
    if "region" in df.columns:
        for i, (reg, cnt) in enumerate(df["region"].value_counts().items()):
            ws3.set_row(i + 3, 16)
            fmt_row = f_alt if i % 2 else f_cell
            ws3.write(i + 3, 0, reg, fmt_row)
            ws3.write(i + 3, 1, cnt, fmt_row)

    wb.close()
    buf.seek(0)
    return buf
