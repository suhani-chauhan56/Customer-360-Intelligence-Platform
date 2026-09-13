"""CustomerAtlas AI - Enterprise Customer 360 Intelligence Platform.

Production-grade analytics application covering:
- Executive Cockpit & Commercial Health
- Customer 360 Unified Profile Dossier
- RFM & Behavioral Cluster Hub
- Predictive AI Studio (What-If Churn & CLV Simulators)
- Experience & Voice of Customer (VoC) Sentiment Radar
- Next Best Offer & Merchandising Intelligence
- Enterprise SQL & Warehouse Console

Run locally:
    streamlit run streamlit_app/app.py
"""

from datetime import datetime
from io import BytesIO
from itertools import combinations
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


# ==============================================================================
# CONFIGURATION & CONSTANTS
# ==============================================================================

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
MODELS = ROOT / "models"
SQL_DIR = ROOT / "sql"

PLOT_CONFIG = {
    "displaylogo": False,
    "responsive": True,
    "scrollZoom": False,
    "modeBarButtonsToRemove": ["lasso2d", "select2d"],
}

MODEL_COLUMNS = [
    "recency_days",
    "frequency",
    "monetary",
    "avg_order_value",
    "number_of_products",
    "customer_age_days",
]

NAV_ITEMS = [
    ("Executive Cockpit", ":material/dashboard:"),
    ("Customer 360 Dossier", ":material/person_search:"),
    ("Audience & Segments", ":material/pie_chart:"),
    ("Predictive AI Studio", ":material/psychology:"),
    ("Experience & VoC Radar", ":material/forum:"),
    ("Next-Best-Offer & Catalog", ":material/auto_awesome:"),
    ("Data Warehouse & SQL", ":material/database:"),
]

PAGE_COPY = {
    "Executive Cockpit": (
        "Executive Cockpit",
        "Macro revenue velocity, customer retention health, and enterprise value distribution.",
    ),
    "Customer 360 Dossier": (
        "Customer 360 Dossier",
        "Deep 360-degree commercial profile, omnichannel journey, timeline, and recommended actions.",
    ),
    "Audience & Segments": (
        "Audience & Segmentation Hub",
        "Multidimensional RFM audiences, behavioral clustering, and targeted activation strategies.",
    ),
    "Predictive AI Studio": (
        "Predictive AI Studio",
        "Real-time What-If scenario simulation for calibrated churn propensity and forward CLV modeling.",
    ),
    "Experience & VoC Radar": (
        "Customer Experience & VoC Radar",
        "Live NLP review sentiment classifier, Voice of Customer trends, and campaign funnel ROI.",
    ),
    "Next-Best-Offer & Catalog": (
        "Next-Best-Offer & Merchandising",
        "Explainable cross-sell recommendations, basket co-occurrence rules, and catalog intelligence.",
    ),
    "Data Warehouse & SQL": (
        "Data Warehouse & SQL Console",
        "Governed dimensional star schema, live business query sandbox, and data contract audit.",
    ),
}

PAGE_GUIDE = {
    "Executive Cockpit": [
        "Track macro revenue & orders",
        "Inspect regional & segment Pareto breakdown",
        "Monitor churn exposure value in real time",
    ],
    "Customer 360 Dossier": [
        "Search 94k+ canonical profiles",
        "Evaluate churn risk & lifetime trajectory",
        "Export 1-click executive PDF / CSV dossier",
    ],
    "Audience & Segments": [
        "Analyze 6 RFM audiences & 5 behavior clusters",
        "Benchmark revenue contribution & average CLV",
        "Export segmented lists for marketing activation",
    ],
    "Predictive AI Studio": [
        "Simulate live What-If customer scenarios",
        "Inspect global XGBoost SHAP/feature importance",
        "Review held-out model comparison benchmarks",
    ],
    "Experience & VoC Radar": [
        "Test custom review text with live NLP pipeline",
        "Analyze sentiment trends & complaint/praise phrases",
        "Benchmark marketing campaign conversion & ROI",
    ],
    "Next-Best-Offer & Catalog": [
        "Generate explainable next-best-category offers",
        "Inspect frequently bought together basket rules",
        "Identify high-revenue & low-rated product categories",
    ],
    "Data Warehouse & SQL": [
        "Run predefined executive business queries",
        "Filter, search, and paginate warehouse extracts",
        "Inspect full SQL schema & business query library",
    ],
}

# Color palettes
BRAND_TEAL = "#0D9488"
BRAND_CYAN = "#06B6D4"
BRAND_INDIGO = "#6366F1"
BRAND_AMBER = "#F59E0B"
BRAND_CORAL = "#F43F5E"
BRAND_GREEN = "#10B981"
BRAND_SLATE = "#1E293B"


# ==============================================================================
# STREAMLIT PAGE SETUP
# ==============================================================================

st.set_page_config(
    page_title="CustomerAtlas AI | Customer 360 Intelligence Platform",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ==============================================================================
# DATA & MODEL LOADERS (CACHED)
# ==============================================================================

@st.cache_data(show_spinner=False)
def load_csv(name: str, parse_dates: tuple[str, ...] = ()) -> pd.DataFrame:
    path = PROCESSED / name
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path, parse_dates=list(parse_dates))


@st.cache_resource(show_spinner=False)
def load_model(name: str):
    path = MODELS / name
    if not path.exists():
        return None
    try:
        return joblib.load(path)
    except Exception:
        return None


# ==============================================================================
# UTILITY HELPERS
# ==============================================================================

def format_brl(value: float) -> str:
    if pd.isna(value):
        return "R$ 0"
    val = float(value)
    if abs(val) >= 1_000_000:
        return f"R$ {val / 1_000_000:.2f}M"
    if abs(val) >= 1_000:
        return f"R$ {val:,.0f}"
    return f"R$ {val:.2f}"


def format_pct(value: float) -> str:
    return "0.0%" if pd.isna(value) else f"{100 * float(value):.1f}%"


def format_num(value: float) -> str:
    if pd.isna(value):
        return "0"
    val = float(value)
    if abs(val) >= 1_000_000:
        return f"{val / 1_000_000:.2f}M"
    if abs(val) >= 1_000:
        return f"{val:,.0f}"
    return f"{val:.0f}"


def retention_action(probability: float, segment: str = "") -> dict:
    if probability >= 0.65:
        return {
            "tier": "Critical Priority",
            "badge_color": "#EF4444",
            "action": "Immediate VIP retention outreach. Review logistics friction and deploy a personalized win-back voucher.",
            "urgency": "High",
        }
    if probability >= 0.35:
        return {
            "tier": "Moderate Risk",
            "badge_color": "#F59E0B",
            "action": "Target with a tailored category re-engagement campaign. Highlight top-rated new arrivals in their favorite category.",
            "urgency": "Medium",
        }
    if segment in {"Champions", "Loyal Customers"}:
        return {
            "tier": "Advocate / Protect",
            "badge_color": "#10B981",
            "action": "Reward loyalty with exclusive early-access perks and cross-sell premium complementary categories.",
            "urgency": "Low (Growth)",
        }
    return {
        "tier": "Standard Growth",
        "badge_color": "#06B6D4",
        "action": "Encourage second purchase journey with streamlined discovery and first-repeat free shipping incentive.",
        "urgency": "Low",
    }


def model_input_frame(recency, frequency, monetary, avg_order_value, products, age) -> pd.DataFrame:
    return pd.DataFrame(
        [[recency, frequency, monetary, avg_order_value, products, age]],
        columns=MODEL_COLUMNS,
    )


# ==============================================================================
# ENTERPRISE DESIGN SYSTEM (CSS & THEME INJECTION)
# ==============================================================================

def inject_enterprise_styles(dark_mode: bool) -> None:
    # Palette definition based on mode
    if dark_mode:
        bg_canvas = "#0A0F1D"
        bg_surface = "#111827"
        bg_surface_elevated = "#1F2937"
        bg_card = "#162032"
        border_color = "rgba(255, 255, 255, 0.08)"
        border_glow = "rgba(13, 148, 136, 0.35)"
        text_primary = "#F9FAFB"
        text_secondary = "#9CA3AF"
        text_muted = "#6B7280"
        sidebar_bg = "#0B1120"
        sidebar_border = "rgba(255, 255, 255, 0.06)"
        table_stripe = "#131C2E"
    else:
        bg_canvas = "#F4F7FB"
        bg_surface = "#FFFFFF"
        bg_surface_elevated = "#F8FAFC"
        bg_card = "#FFFFFF"
        border_color = "#E2E8F0"
        border_glow = "rgba(13, 148, 136, 0.25)"
        text_primary = "#0F172A"
        text_secondary = "#475569"
        text_muted = "#64748B"
        sidebar_bg = "#0F172A"
        sidebar_border = "#1E293B"
        table_stripe = "#F8FAFC"

    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

        :root {{
            --bg-canvas: {bg_canvas};
            --bg-surface: {bg_surface};
            --bg-surface-elevated: {bg_surface_elevated};
            --bg-card: {bg_card};
            --border-color: {border_color};
            --border-glow: {border_glow};
            --text-primary: {text_primary};
            --text-secondary: {text_secondary};
            --text-muted: {text_muted};
            --teal: #0D9488;
            --teal-light: #14B8A6;
            --cyan: #06B6D4;
            --indigo: #6366F1;
            --amber: #F59E0B;
            --coral: #F43F5E;
            --green: #10B981;
        }}

        * {{
            font-family: 'Plus Jakarta Sans', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            letter-spacing: -0.01em;
        }}

        .stApp {{
            background: var(--bg-canvas);
            color: var(--text-primary);
        }}

        /* Clean Streamlit Default UI Noise */
        header[data-testid="stHeader"] {{ height: 0; background: transparent; }}
        div[data-testid="stToolbar"] {{ visibility: hidden; height: 0; }}
        div[data-testid="stDecoration"] {{ display: none; }}
        [data-testid="stMainBlockContainer"] {{
            max-width: 1440px;
            padding: 0.8rem 2rem 3rem;
        }}

        /* Modern Sidebar */
        section[data-testid="stSidebar"] {{
            width: 290px !important;
            min-width: 290px !important;
            background: {sidebar_bg} !important;
            border-right: 1px solid {sidebar_border} !important;
        }}
        section[data-testid="stSidebar"] [data-testid="stSidebarContent"] {{
            padding: 1.2rem 1rem;
        }}
        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3,
        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] label {{
            color: #F8FAFC !important;
        }}
        section[data-testid="stSidebar"] .stCaptionContainer p {{
            color: #94A3B8 !important;
        }}

        /* Brand Header in Sidebar */
        .brand-container {{
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 12px 14px;
            margin-bottom: 20px;
            background: linear-gradient(135deg, rgba(13,148,136,0.15) 0%, rgba(99,102,241,0.15) 100%);
            border: 1px solid rgba(255,255,255,0.12);
            border-radius: 10px;
        }}
        .brand-icon {{
            width: 40px;
            height: 40px;
            background: linear-gradient(135deg, #0D9488 0%, #06B6D4 100%);
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #FFFFFF;
            font-size: 20px;
            font-weight: 800;
            box-shadow: 0 4px 12px rgba(13,148,136,0.4);
        }}
        .brand-title {{
            font-size: 15px;
            font-weight: 800;
            color: #FFFFFF;
            line-height: 1.1;
        }}
        .brand-subtitle {{
            font-size: 10.5px;
            font-weight: 500;
            color: #94A3B8;
            margin-top: 3px;
            text-transform: uppercase;
            letter-spacing: 0.06em;
        }}

        /* Navigation Buttons in Sidebar */
        .nav-category-header {{
            font-size: 10px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: #64748B !important;
            margin: 16px 6px 8px;
        }}
        section[data-testid="stSidebar"] div[data-testid="stButton"] button {{
            width: 100%;
            min-height: 40px;
            justify-content: flex-start;
            border-radius: 8px;
            border: 1px solid transparent;
            padding: 8px 12px;
            font-weight: 600;
            font-size: 13.5px;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        }}
        section[data-testid="stSidebar"] div[data-testid="stButton"] button[kind="secondary"] {{
            background: transparent;
            color: #CBD5E1;
        }}
        section[data-testid="stSidebar"] div[data-testid="stButton"] button[kind="secondary"]:hover {{
            background: rgba(255,255,255,0.06);
            color: #FFFFFF;
            transform: translateX(3px);
        }}
        section[data-testid="stSidebar"] div[data-testid="stButton"] button[kind="primary"] {{
            background: linear-gradient(90deg, #0D9488 0%, #0F766E 100%);
            color: #FFFFFF;
            border-color: rgba(20,184,166,0.4);
            box-shadow: 0 4px 14px rgba(13,148,136,0.35);
        }}
        section[data-testid="stSidebar"] div[data-testid="stButton"] button p,
        section[data-testid="stSidebar"] div[data-testid="stButton"] button span {{
            color: inherit !important;
        }}

        /* Executive Page Header */
        .page-header-card {{
            background: linear-gradient(135deg, rgba(13,148,136,0.08) 0%, rgba(99,102,241,0.05) 50%, var(--bg-surface) 100%);
            border: 1px solid var(--border-color);
            border-left: 4px solid var(--teal);
            border-radius: 12px;
            padding: 20px 24px;
            margin-bottom: 18px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.03);
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 16px;
        }}
        .page-badge {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            font-size: 10.5px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: var(--teal);
            margin-bottom: 6px;
        }}
        .page-title {{
            font-size: 26px;
            font-weight: 800;
            color: var(--text-primary);
            line-height: 1.2;
            margin: 0 0 6px 0;
            letter-spacing: -0.02em;
        }}
        .page-subtitle {{
            font-size: 13.5px;
            color: var(--text-secondary);
            margin: 0;
            max-width: 750px;
        }}
        .page-status-pill {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: var(--bg-surface-elevated);
            border: 1px solid var(--border-color);
            border-radius: 20px;
            padding: 6px 14px;
            font-size: 11.5px;
            font-weight: 600;
            color: var(--text-secondary);
        }}
        .status-dot {{
            width: 8px;
            height: 8px;
            background: var(--green);
            border-radius: 50%;
            box-shadow: 0 0 8px rgba(16,185,129,0.7);
            animation: pulse-green 2s infinite;
        }}

        /* Executive Guide Bar */
        .guide-bar {{
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 10px 16px;
            margin-bottom: 20px;
            background: var(--bg-surface);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            font-size: 12px;
            color: var(--text-secondary);
            flex-wrap: wrap;
        }}
        .guide-bar strong {{
            color: var(--text-primary);
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }}
        .guide-pill {{
            background: var(--bg-surface-elevated);
            border: 1px solid var(--border-color);
            border-radius: 6px;
            padding: 3px 9px;
            font-size: 11px;
            color: var(--text-secondary);
        }}

        /* Section Headings */
        .section-header {{
            display: flex;
            align-items: baseline;
            justify-content: space-between;
            margin: 22px 0 12px 0;
            padding-bottom: 6px;
            border-bottom: 1px solid var(--border-color);
        }}
        .section-header h3 {{
            font-size: 17px;
            font-weight: 700;
            color: var(--text-primary);
            margin: 0;
            letter-spacing: -0.01em;
        }}
        .section-header span {{
            font-size: 12px;
            color: var(--text-muted);
        }}

        /* Metric Cards */
        div[data-testid="stMetric"] {{
            background: var(--bg-surface);
            border: 1px solid var(--border-color);
            border-radius: 10px;
            padding: 14px 16px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.02);
            transition: all 0.2s ease;
        }}
        div[data-testid="stMetric"]:hover {{
            border-color: var(--border-glow);
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(0,0,0,0.06);
        }}
        div[data-testid="stMetricLabel"] {{
            font-size: 12px !important;
            font-weight: 600 !important;
            color: var(--text-secondary) !important;
        }}
        div[data-testid="stMetricValue"] {{
            font-family: 'JetBrains Mono', 'Plus Jakarta Sans', monospace !important;
            font-size: 24px !important;
            font-weight: 800 !important;
            color: var(--text-primary) !important;
            letter-spacing: -0.02em !important;
        }}

        /* Insight Cards */
        .insight-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 12px;
            margin: 14px 0 20px;
        }}
        .insight-card {{
            background: var(--bg-surface);
            border: 1px solid var(--border-color);
            border-left: 3px solid var(--teal);
            border-radius: 8px;
            padding: 14px 16px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.02);
        }}
        .insight-card.warning {{
            border-left-color: var(--amber);
        }}
        .insight-card.alert {{
            border-left-color: var(--coral);
        }}
        .insight-title {{
            font-size: 14.5px;
            font-weight: 700;
            color: var(--text-primary);
            margin-bottom: 4px;
        }}
        .insight-desc {{
            font-size: 12px;
            color: var(--text-secondary);
            line-height: 1.4;
            margin: 0;
        }}

        /* Recommendation Cards */
        .rec-card {{
            background: var(--bg-surface);
            border: 1px solid var(--border-color);
            border-radius: 10px;
            padding: 16px;
            margin-bottom: 10px;
            transition: all 0.2s ease;
            position: relative;
            overflow: hidden;
        }}
        .rec-card:hover {{
            border-color: var(--teal);
            transform: translateY(-2px);
            box-shadow: 0 6px 18px rgba(13,148,136,0.12);
        }}
        .rec-card-rank {{
            position: absolute;
            top: 12px;
            right: 14px;
            font-size: 11px;
            font-weight: 800;
            color: var(--teal);
            background: rgba(13,148,136,0.1);
            padding: 3px 8px;
            border-radius: 4px;
        }}
        .rec-card-title {{
            font-size: 15px;
            font-weight: 700;
            color: var(--text-primary);
            margin: 0 0 6px 0;
        }}
        .rec-card-reason {{
            font-size: 12px;
            color: var(--text-secondary);
            margin: 0;
            line-height: 1.4;
        }}

        /* Forms, Buttons & Tabs */
        div[data-testid="stForm"] {{
            background: var(--bg-surface);
            border: 1px solid var(--border-color);
            border-radius: 10px;
            padding: 18px;
        }}
        div[data-testid="stExpander"] {{
            background: var(--bg-surface) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 8px !important;
        }}
        div[data-testid="stDataFrame"] {{
            border: 1px solid var(--border-color);
            border-radius: 8px;
            overflow: hidden;
        }}
        div[data-testid="stPlotlyChart"] {{
            background: var(--bg-surface);
            border: 1px solid var(--border-color);
            border-radius: 10px;
            padding: 8px;
        }}
        button[kind="primary"] {{
            background: linear-gradient(90deg, #0D9488 0%, #0F766E 100%) !important;
            border-color: #0D9488 !important;
            color: #FFFFFF !important;
            font-weight: 600 !important;
            border-radius: 6px !important;
        }}

        /* Keyframe Animations */
        @keyframes pulse-green {{
            0%, 100% {{ transform: scale(1); opacity: 1; }}
            50% {{ transform: scale(1.3); opacity: 0.6; }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def chart(figure, height: int = 320, legend: str = "bottom", dark_mode: bool = False) -> None:
    """Standardized enterprise styling for Plotly charts."""
    text_color = "#E2E8F0" if dark_mode else "#334155"
    title_color = "#F8FAFC" if dark_mode else "#0F172A"
    grid_color = "rgba(255,255,255,0.06)" if dark_mode else "rgba(0,0,0,0.06)"
    hover_bg = "#1E293B" if dark_mode else "#FFFFFF"
    hover_text = "#F8FAFC" if dark_mode else "#0F172A"

    has_multi_item_legend = len(figure.data) > 1 or any(
        getattr(trace, "type", "") in {"pie", "funnelarea", "sunburst"} for trace in figure.data
    )
    show_legend = legend != "hidden" and has_multi_item_legend

    legend_layout = (
        dict(
            orientation="h",
            yanchor="top",
            y=-0.18,
            xanchor="center",
            x=0.5,
            font=dict(size=11, color=text_color),
        )
        if legend == "bottom"
        else dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.02,
            font=dict(size=11, color=text_color),
        )
    )

    figure.update_layout(
        height=height,
        margin=dict(l=14, r=14, t=48, b=56 if show_legend and legend == "bottom" else 28),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Plus Jakarta Sans, Inter, sans-serif", color=text_color, size=12),
        title=dict(
            font=dict(size=15, color=title_color),
            x=0.01,
            xanchor="left",
            y=0.97,
            yanchor="top",
        ),
        showlegend=show_legend,
        legend=legend_layout,
        hoverlabel=dict(
            bgcolor=hover_bg,
            font_color=hover_text,
            bordercolor=text_color,
            font_size=12,
        ),
    )
    figure.update_xaxes(gridcolor=grid_color, zerolinecolor=grid_color)
    figure.update_yaxes(gridcolor=grid_color, zerolinecolor=grid_color)
    st.plotly_chart(figure, use_container_width=True, config=PLOT_CONFIG)


def render_page_header(page_name: str) -> None:
    title, subtitle = PAGE_COPY[page_name]
    guides = PAGE_GUIDE.get(page_name, [])
    guide_pills = "".join(f'<span class="guide-pill">✓ {g}</span>' for g in guides)

    st.markdown(
        f"""
        <div class="page-header-card">
            <div>
                <div class="page-badge">⚡ CUSTOMERATLAS AI / CUSTOMER 360 PLATFORM</div>
                <h1 class="page-title">{title}</h1>
                <p class="page-subtitle">{subtitle}</p>
            </div>
            <div class="page-status-pill">
                <span class="status-dot"></span>
                <span>Live Intelligence Engine</span>
                <span style="opacity: 0.4;">|</span>
                <span>Currency: BRL</span>
            </div>
        </div>
        <div class="guide-bar">
            <strong>Key Capabilities:</strong>
            {guide_pills}
        </div>
        """,
        unsafe_allow_html=True,
    )


def build_customer_pdf(profile: pd.Series) -> bytes:
    """Generate professional executive Customer 360 PDF dossier."""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Heading1"],
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#0F172A"),
    )
    sub_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#475569"),
    )

    action_info = retention_action(float(profile.get("churn_probability", 0)), str(profile.get("rfm_segment", "")))

    fields = [
        ["Attribute", "Metric / Intelligence Value"],
        ["Customer ID", str(profile.get("customer_id", ""))],
        ["Location", f"{str(profile.get('city', '')).title()}, {str(profile.get('state', '')).upper()}"],
        ["RFM Segment", str(profile.get("rfm_segment", ""))],
        ["Behavior Cluster", str(profile.get("cluster_segment", ""))],
        ["Favorite Category", str(profile.get("favorite_category", ""))],
        ["Total Lifetime Spend", format_brl(profile.get("total_spend", 0))],
        ["Total Orders Placed", str(int(profile.get("total_orders", 1)))],
        ["Average Order Value", format_brl(profile.get("avg_order_value", 0))],
        ["Recency (Days Inactive)", f"{int(profile.get('recency_days', 0))} days"],
        ["12-Month CLV Proxy", format_brl(profile.get("predicted_clv", 0))],
        ["Churn Propensity", format_pct(profile.get("churn_probability", 0))],
        ["Retention Playbook Tier", action_info["tier"]],
        ["Recommended Commercial Action", action_info["action"]],
    ]

    table = Table(fields, colWidths=[150, 370])
    table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0D9488")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("PADDING", (0, 0), (-1, -1), 6),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#F8FAFC"), colors.white]),
        ])
    )

    elements = [
        Paragraph("CustomerAtlas AI - Unified Customer 360 Dossier", title_style),
        Paragraph(f"Generated on {datetime.now().strftime('%B %d, %Y - %I:%M %p')} | Confidential Executive Report", sub_style),
        Spacer(1, 10),
        HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0D9488"), spaceAfter=14),
        table,
    ]

    doc.build(elements)
    return buffer.getvalue()


# ==============================================================================
# STATE INITIALIZATION & SIDEBAR NAVIGATION
# ==============================================================================

if "active_page" not in st.session_state:
    st.session_state.active_page = "Executive Cockpit"

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

inject_enterprise_styles(st.session_state.dark_mode)

# Load primary customer 360 feature store
customer_features = load_csv("customer_360_features.csv", ("first_purchase_date", "last_purchase_date"))

if customer_features.empty:
    st.error("⚠️ App artifacts are missing in `data/processed/`. Please run notebooks 01 through 06.")
    st.code("python -m venv .venv\nstreamlit run streamlit_app/app.py", language="bash")
    st.stop()


# Sidebar Navigation
with st.sidebar:
    st.markdown(
        """
        <div class="brand-container">
            <div class="brand-icon">⚡</div>
            <div>
                <div class="brand-title">CustomerAtlas AI</div>
                <div class="brand-subtitle">Enterprise Customer 360</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="nav-category-header">ANALYTICS WORKSPACES</div>', unsafe_allow_html=True)
    for label, icon in NAV_ITEMS:
        is_active = st.session_state.active_page == label
        if st.button(
            label,
            key=f"nav_{label}",
            icon=icon,
            type="primary" if is_active else "secondary",
            use_container_width=True,
        ):
            st.session_state.active_page = label
            st.rerun()

    st.markdown('<div class="nav-category-header">GLOBAL AUDIENCE FILTERS</div>', unsafe_allow_html=True)
    with st.expander("Filter Criteria", expanded=False, icon=":material/filter_list:"):
        segment_options = ["All", *sorted(customer_features["rfm_segment"].dropna().unique())]
        selected_segment = st.selectbox("RFM Segment", segment_options)

        state_options = ["All", *sorted(customer_features["state"].dropna().unique())]
        selected_state = st.selectbox("State / Region", state_options)

        cat_options = ["All", *sorted(customer_features["favorite_category"].dropna().unique())]
        selected_category = st.selectbox("Favorite Category", cat_options)

        min_date = customer_features["last_purchase_date"].min().date()
        max_date = customer_features["last_purchase_date"].max().date()
        date_range = st.date_input(
            "Purchase Date Window",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
        )

    st.markdown('<div class="nav-category-header">PREFERENCES & HEALTH</div>', unsafe_allow_html=True)
    dark_mode_toggle = st.toggle("Dark Mode Theme", value=st.session_state.dark_mode)
    if dark_mode_toggle != st.session_state.dark_mode:
        st.session_state.dark_mode = dark_mode_toggle
        st.rerun()

    st.caption(f"🟢 Warehouse Active | {len(customer_features):,} Canonical Profiles")
    st.caption(f"🕒 {datetime.now().strftime('%d %b %Y, %I:%M %p')}")


# Filter Customer Features
filtered = customer_features.copy()
if selected_segment != "All":
    filtered = filtered[filtered["rfm_segment"] == selected_segment]
if selected_state != "All" and "state" in filtered.columns:
    filtered = filtered[filtered["state"] == selected_state]
if selected_category != "All":
    filtered = filtered[filtered["favorite_category"] == selected_category]
if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start_dt, end_dt = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
    filtered = filtered[filtered["last_purchase_date"].between(start_dt, end_dt)]


# Page Router
current_page = st.session_state.active_page
render_page_header(current_page)

if filtered.empty:
    st.warning("⚠️ No customer profiles match your filter criteria. Open 'Global Audience Filters' in the sidebar to broaden selections.")
    st.stop()


# ==============================================================================
# WORKSPACE 1: EXECUTIVE COCKPIT
# ==============================================================================

if current_page == "Executive Cockpit":
    total_profiles = filtered["customer_id"].nunique()
    total_rev = filtered["total_spend"].sum()
    total_ord = filtered["total_orders"].sum()
    avg_clv_val = filtered["predicted_clv"].mean()
    churn_rate = filtered["churn_probability"].mean()
    avg_satisfaction = filtered["avg_review_score"].mean()
    repeat_customers = (filtered["total_orders"] > 1).sum()
    repeat_rate = repeat_customers / max(1, total_profiles)
    at_risk_rev = filtered[filtered["churn_probability"] >= 0.65]["total_spend"].sum()

    # Executive KPI Grid
    kpi_cols = st.columns(6)
    kpi_cols[0].metric("Total Customers", f"{total_profiles:,}", "Profiles in view")
    kpi_cols[1].metric("Merchandise GMV", format_brl(total_rev), "Total Spend")
    kpi_cols[2].metric("Total Orders", f"{total_ord:,}", f"{(total_ord/total_profiles):.2f} orders/cust")
    kpi_cols[3].metric("Avg 12M CLV", format_brl(avg_clv_val), "Forward value")
    kpi_cols[4].metric("Churn Propensity", format_pct(churn_rate), f"{format_brl(at_risk_rev)} at risk")
    kpi_cols[5].metric("Avg CSAT Score", f"{avg_satisfaction:.2f} / 5", "Olist Reviews")

    # Executive Insight Strip
    top_seg = filtered.groupby("rfm_segment")["total_spend"].sum().idxmax()
    top_seg_rev = filtered.groupby("rfm_segment")["total_spend"].sum().max()
    top_state_name = filtered.groupby("state")["total_spend"].sum().idxmax()
    top_state_rev = filtered.groupby("state")["total_spend"].sum().max()

    st.markdown(
        f"""
        <div class="insight-grid">
            <div class="insight-card">
                <div class="insight-title">🏆 Top Revenue Segment: {top_seg}</div>
                <p class="insight-desc">Generates <strong>{format_brl(top_seg_rev)}</strong> ({top_seg_rev/total_rev:.1%} of filtered GMV). Priority audience for retention.</p>
            </div>
            <div class="insight-card">
                <div class="insight-title">📍 Top Geographic Hub: {top_state_name}</div>
                <p class="insight-desc">Leads regional demand with <strong>{format_brl(top_state_rev)}</strong> in sales. Recommended for logistics fulfillment priority.</p>
            </div>
            <div class="insight-card alert">
                <div class="insight-title">⚠️ Churn Risk Exposure: {format_brl(at_risk_rev)}</div>
                <p class="insight-desc">{(filtered['churn_probability'] >= 0.65).sum():,} customers show high churn propensity. Repeat buyer rate is <strong>{repeat_rate:.1%}</strong>.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Executive Charts Row 1
    col_chart_1, col_chart_2 = st.columns(2)
    with col_chart_1:
        seg_rev = filtered.groupby("rfm_segment", as_index=False)["total_spend"].sum().sort_values("total_spend", ascending=True)
        fig_seg = px.bar(
            seg_rev,
            x="total_spend",
            y="rfm_segment",
            orientation="h",
            color="rfm_segment",
            title="Revenue Contribution by RFM Segment",
            color_discrete_sequence=[BRAND_TEAL, BRAND_CYAN, BRAND_INDIGO, BRAND_AMBER, BRAND_CORAL, "#8B5CF6"],
        )
        fig_seg.update_xaxes(title="Total Spend (BRL)")
        fig_seg.update_yaxes(title=None)
        chart(fig_seg, 320, legend="hidden", dark_mode=st.session_state.dark_mode)

    with col_chart_2:
        state_rev = filtered.groupby("state", as_index=False)["total_spend"].sum().nlargest(10, "total_spend").sort_values("total_spend", ascending=True)
        fig_state = px.bar(
            state_rev,
            x="total_spend",
            y="state",
            orientation="h",
            title="Top 10 States by Merchandise Revenue",
            color="total_spend",
            color_continuous_scale="Teal",
        )
        fig_state.update_xaxes(title="Revenue (BRL)")
        fig_state.update_yaxes(title="State")
        fig_state.update_layout(coloraxis_showscale=False)
        chart(fig_state, 320, legend="hidden", dark_mode=st.session_state.dark_mode)

    # Customer Scatter & Value Matrix
    with st.expander("Customer Lifetime Value vs Recency Scatter Matrix", expanded=True, icon=":material/scatter_plot:"):
        sample_size = min(len(filtered), 2500)
        scatter_sample = filtered.sample(sample_size, random_state=42)
        fig_scatter = px.scatter(
            scatter_sample,
            x="recency_days",
            y="total_spend",
            color="rfm_segment",
            size="total_orders",
            hover_data=["customer_id", "state", "predicted_clv", "churn_probability"],
            title=f"Recency vs Spend Density (Sample of {sample_size:,} Profiles)",
            color_discrete_sequence=[BRAND_TEAL, BRAND_CYAN, BRAND_INDIGO, BRAND_AMBER, BRAND_CORAL, "#8B5CF6"],
        )
        fig_scatter.update_xaxes(title="Days Inactive (Recency)")
        fig_scatter.update_yaxes(title="Total Spend (BRL)")
        chart(fig_scatter, 340, legend="bottom", dark_mode=st.session_state.dark_mode)

    # Export Row
    exp_col1, exp_col2 = st.columns([0.3, 0.7])
    with exp_col1:
        st.download_button(
            "Download Filtered Customer Profiles (CSV)",
            filtered.to_csv(index=False).encode("utf-8"),
            "customer_360_executive_view.csv",
            "text/csv",
            icon=":material/download:",
            use_container_width=True,
        )


# ==============================================================================
# WORKSPACE 2: CUSTOMER 360 DOSSIER
# ==============================================================================

elif current_page == "Customer 360 Dossier":
    fact_orders = load_csv("fact_orders.csv", ("purchase_date",))
    recommendations = load_csv("recommendations.csv")

    # Search & Presets
    search_col1, search_col2 = st.columns([0.4, 0.6])
    with search_col1:
        preset = st.selectbox(
            "Quick Filter Presets",
            [
                "All Available Customers",
                "High Value Champions (VIP)",
                "At Risk High Spenders",
                "Growth Potential (Engaged)",
                "Recent First-Time Buyers",
            ],
        )

    preset_subset = filtered.copy()
    if preset == "High Value Champions (VIP)":
        preset_subset = preset_subset[preset_subset["rfm_segment"] == "Champions"]
    elif preset == "At Risk High Spenders":
        preset_subset = preset_subset[(preset_subset["churn_probability"] >= 0.65) & (preset_subset["total_spend"] >= 200)]
    elif preset == "Growth Potential (Engaged)":
        preset_subset = preset_subset[preset_subset["cluster_segment"] == "Growth Potential"]
    elif preset == "Recent First-Time Buyers":
        preset_subset = preset_subset[(preset_subset["recency_days"] <= 60) & (preset_subset["total_orders"] == 1)]

    if preset_subset.empty:
        preset_subset = filtered

    customer_id_list = sorted(preset_subset["customer_id"].dropna().unique())
    with search_col2:
        selected_cust = st.selectbox("Search / Select Customer ID", customer_id_list, index=0)

    profile = filtered[filtered["customer_id"] == selected_cust].iloc[0]

    # Customer Hero Card
    churn_val = float(profile.get("churn_probability", 0))
    action_info = retention_action(churn_val, str(profile.get("rfm_segment", "")))

    st.markdown(
        f"""
        <div class="page-header-card" style="margin-top: 12px; background: linear-gradient(135deg, rgba(13,148,136,0.12) 0%, var(--bg-surface) 100%);">
            <div style="display: flex; align-items: center; gap: 16px;">
                <div style="width: 52px; height: 52px; border-radius: 12px; background: #0D9488; display: flex; align-items: center; justify-content: center; color: white; font-size: 24px; font-weight: 800;">
                    {str(profile.get('rfm_segment', 'C'))[0]}
                </div>
                <div>
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span style="font-size: 18px; font-weight: 800; color: var(--text-primary);">{profile.get('customer_id')}</span>
                        <span style="background: rgba(13,148,136,0.15); color: #0D9488; font-size: 11px; font-weight: 700; padding: 2px 8px; border-radius: 4px;">{profile.get('rfm_segment')}</span>
                        <span style="background: rgba(99,102,241,0.15); color: #6366F1; font-size: 11px; font-weight: 700; padding: 2px 8px; border-radius: 4px;">{profile.get('cluster_segment')}</span>
                    </div>
                    <p style="margin: 4px 0 0; font-size: 13px; color: var(--text-secondary);">
                        📍 {str(profile.get('city', 'Unknown')).title()}, {str(profile.get('state', 'SP')).upper()} &nbsp;|&nbsp;
                        Category Affinity: <strong>{profile.get('favorite_category')}</strong> &nbsp;|&nbsp;
                        Customer Tier: <strong>{profile.get('clv_band', 'Standard')}</strong>
                    </p>
                </div>
            </div>
            <div>
                <span style="background: {action_info['badge_color']}; color: white; padding: 6px 14px; border-radius: 20px; font-size: 12px; font-weight: 700;">
                    {action_info['tier']}
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Dossier Quick Metrics
    metric_cols = st.columns(5)
    metric_cols[0].metric("Total Lifetime Spend", format_brl(profile["total_spend"]))
    metric_cols[1].metric("Total Orders", f"{profile['total_orders']:.0f}")
    metric_cols[2].metric("Average Order Value", format_brl(profile["avg_order_value"]))
    metric_cols[3].metric("12M CLV Proxy", format_brl(profile["predicted_clv"]))
    metric_cols[4].metric("Churn Propensity", format_pct(profile["churn_probability"]))

    # 4-Tab Unified Dossier
    tab_profile, tab_journey, tab_orders, tab_offers = st.tabs([
        "📋 Unified Profile",
        "🌐 Omnichannel & Engagement",
        "📦 Order History Timeline",
        "🎁 AI Next-Best-Offers",
    ])

    with tab_profile:
        col_prof_left, col_prof_right = st.columns([1.3, 0.7])
        with col_prof_left:
            summary_dict = {
                "Canonical Customer ID": profile.get("customer_id"),
                "Geographic Location": f"{str(profile.get('city', '')).title()}, {str(profile.get('state', '')).upper()}",
                "RFM Audience Segment": profile.get("rfm_segment"),
                "Behavioral Cluster": profile.get("cluster_segment"),
                "Primary Affinity Category": profile.get("favorite_category"),
                "Days Since Last Order": f"{int(profile.get('recency_days', 0))} days",
                "Distinct Items Purchased": int(profile.get("number_of_products", 1)),
                "Average Review Score": f"{profile.get('avg_review_score', 5.0):.1f} / 5.0",
                "Estimated 90-Day Revenue": format_brl(profile.get("predicted_90d_revenue", 0)),
            }
            summary_df = pd.DataFrame({"Attribute": summary_dict.keys(), "Intelligence Metric": summary_dict.values()})
            st.dataframe(summary_df, hide_index=True, use_container_width=True, height=330)

        with col_prof_right:
            gauge_fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=100 * churn_val,
                number={"suffix": "%", "font": {"family": "JetBrains Mono", "size": 28}},
                title={"text": "<b>Churn Propensity</b>", "font": {"size": 15}},
                gauge={
                    "axis": {"range": [0, 100]},
                    "bar": {"color": action_info["badge_color"]},
                    "steps": [
                        {"range": [0, 35], "color": "rgba(16,185,129,0.15)"},
                        {"range": [35, 65], "color": "rgba(245,158,11,0.15)"},
                        {"range": [65, 100], "color": "rgba(239,68,68,0.15)"},
                    ],
                },
            ))
            gauge_fig.update_layout(height=210, margin=dict(l=15, r=15, t=35, b=5), paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(gauge_fig, use_container_width=True, config=PLOT_CONFIG)
            st.info(f"**Recommended Playbook:** {action_info['action']}")

    with tab_journey:
        j_col1, j_col2, j_col3, j_col4, j_col5 = st.columns(5)
        j_col1.metric("Web Sessions", f"{profile.get('sessions', 0):,.0f}")
        j_col2.metric("Page Views", f"{profile.get('views', 0):,.0f}")
        j_col3.metric("Cart Additions", f"{profile.get('cart_additions', 0):,.0f}")
        j_col4.metric("Campaign Clicks", f"{profile.get('campaign_clicks', 0):,.0f}")
        j_col5.metric("Campaign Conversions", f"{profile.get('campaign_conversions', 0):,.0f}")

        journey_table = pd.DataFrame([
            {"Touchpoint Channel": "Digital Web Activity", "Signal / Metric": "Web Engagement Score", "Score / Value": f"{profile.get('web_engagement_score', 0):.1f} pts"},
            {"Touchpoint Channel": "Digital Conversion", "Signal / Metric": "Web Conversion Rate", "Score / Value": format_pct(profile.get("web_conversion_rate", 0))},
            {"Touchpoint Channel": "Marketing Campaigns", "Signal / Metric": "Campaign Open Rate", "Score / Value": format_pct(profile.get("campaign_open_rate", 0))},
            {"Touchpoint Channel": "Marketing Campaigns", "Signal / Metric": "Attributed Campaign Revenue", "Score / Value": format_brl(profile.get("campaign_revenue", 0))},
            {"Touchpoint Channel": "Customer Feedback (VoC)", "Signal / Metric": "Average Review Rating", "Score / Value": f"{profile.get('avg_review_score', 0):.1f} / 5.0"},
        ])
        st.dataframe(journey_table, hide_index=True, use_container_width=True)

    with tab_orders:
        if not fact_orders.empty:
            cust_orders = fact_orders[fact_orders["customer_id"] == selected_cust].copy()
            if cust_orders.empty:
                st.info("No detailed transaction line items found for this customer.")
            else:
                cust_orders = cust_orders.sort_values("purchase_date", ascending=False)
                display_cols = [
                    c for c in ["order_id", "purchase_date", "order_status", "item_price", "freight_value", "revenue"]
                    if c in cust_orders.columns
                ]
                st.dataframe(cust_orders[display_cols], hide_index=True, use_container_width=True)
        else:
            st.info("Transaction history fact table is currently loading.")

    with tab_offers:
        if not recommendations.empty:
            cust_recs = recommendations[recommendations["customer_id"] == selected_cust].sort_values("rank")
            if cust_recs.empty:
                st.info("No precomputed recommendations found for this customer.")
            else:
                st.markdown("**Explainable Next-Best-Category Recommendations for this Profile:**")
                rec_cols = st.columns(min(len(cust_recs), 5))
                for col_idx, (_, rec) in enumerate(cust_recs.head(5).iterrows()):
                    with rec_cols[col_idx]:
                        st.markdown(
                            f"""
                            <div class="rec-card">
                                <span class="rec-card-rank">#{int(rec['rank'])}</span>
                                <div class="rec-card-title">{rec['recommended_category']}</div>
                                <p class="rec-card-reason"><strong>Reason:</strong> {rec['reason']}</p>
                                <div style="margin-top: 8px; font-size: 11px; color: var(--teal); font-weight: 600;">
                                    Method: {rec.get('method', 'Basket Co-occurrence')}
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
        else:
            st.info("Recommendations dataset is loading.")

    # Export Dossier Row
    dossier_exp1, dossier_exp2 = st.columns([0.25, 0.25])
    with dossier_exp1:
        st.download_button(
            "Download Executive PDF Dossier",
            build_customer_pdf(profile),
            f"customer_360_{selected_cust}.pdf",
            "application/pdf",
            icon=":material/picture_as_pdf:",
            use_container_width=True,
        )
    with dossier_exp2:
        st.download_button(
            "Download Customer Record (CSV)",
            pd.DataFrame([profile]).to_csv(index=False).encode("utf-8"),
            f"customer_360_{selected_cust}.csv",
            "text/csv",
            icon=":material/download:",
            use_container_width=True,
        )


# ==============================================================================
# WORKSPACE 3: AUDIENCE & SEGMENTS HUB
# ==============================================================================

elif current_page == "Audience & Segments":
    segment_summary = load_csv("segment_summary.csv")

    seg_counts = filtered["rfm_segment"].value_counts().reset_index()
    seg_counts.columns = ["Segment", "Customers"]

    cluster_rev = filtered.groupby("cluster_segment", as_index=False)["total_spend"].sum().sort_values("total_spend", ascending=True)

    col_seg_1, col_seg_2 = st.columns(2)
    with col_seg_1:
        fig_rfm_pie = px.pie(
            seg_counts,
            names="Segment",
            values="Customers",
            hole=0.55,
            title="RFM Audience Distribution",
            color_discrete_sequence=[BRAND_TEAL, BRAND_CYAN, BRAND_INDIGO, BRAND_AMBER, BRAND_CORAL, "#8B5CF6"],
        )
        chart(fig_rfm_pie, 330, legend="bottom", dark_mode=st.session_state.dark_mode)

    with col_seg_2:
        fig_clust_bar = px.bar(
            cluster_rev,
            x="total_spend",
            y="cluster_segment",
            orientation="h",
            title="Revenue Contribution by Behavioral Cluster",
            color="cluster_segment",
            color_discrete_sequence=px.colors.qualitative.Bold,
        )
        fig_clust_bar.update_xaxes(title="Revenue (BRL)")
        fig_clust_bar.update_yaxes(title=None)
        chart(fig_clust_bar, 330, legend="hidden", dark_mode=st.session_state.dark_mode)

    # Segment Strategy Action Table
    st.markdown('<div class="section-header"><h3>Strategic Segment Action Playbook</h3><span>Audience Activation Matrix</span></div>', unsafe_allow_html=True)
    if not segment_summary.empty:
        summary_display = segment_summary.copy()
        summary_display["revenue"] = summary_display["revenue"].map(format_brl)
        summary_display["avg_clv"] = summary_display["avg_clv"].map(format_brl)
        summary_display["avg_churn_probability"] = summary_display["avg_churn_probability"].map(format_pct)
        st.dataframe(summary_display, hide_index=True, use_container_width=True)

    # Multidimensional Bubble Map
    with st.expander("Multidimensional Frequency vs Monetary Value Map", expanded=False, icon=":material/bubble_chart:"):
        sample_seg = filtered.sample(min(len(filtered), 3000), random_state=42)
        fig_bubble = px.scatter(
            sample_seg,
            x="frequency",
            y="monetary",
            color="rfm_segment",
            size="recency_days",
            hover_data=["customer_id", "cluster_segment", "predicted_clv"],
            title="Audience Clustering (Frequency vs Monetary vs Recency)",
            color_discrete_sequence=[BRAND_TEAL, BRAND_CYAN, BRAND_INDIGO, BRAND_AMBER, BRAND_CORAL, "#8B5CF6"],
        )
        fig_bubble.update_xaxes(title="Order Frequency")
        fig_bubble.update_yaxes(title="Monetary Value (BRL)")
        chart(fig_bubble, 340, legend="bottom", dark_mode=st.session_state.dark_mode)

    # Segment Download Row
    seg_d1, seg_d2 = st.columns(2)
    with seg_d1:
        st.download_button(
            "Export RFM Audience Breakdown (CSV)",
            seg_counts.to_csv(index=False).encode("utf-8"),
            "rfm_audience_summary.csv",
            "text/csv",
            icon=":material/download:",
            use_container_width=True,
        )
    with seg_d2:
        st.download_button(
            "Export Cluster Revenue Breakdown (CSV)",
            cluster_rev.to_csv(index=False).encode("utf-8"),
            "behavior_cluster_revenue.csv",
            "text/csv",
            icon=":material/download:",
            use_container_width=True,
        )


# ==============================================================================
# WORKSPACE 4: PREDICTIVE AI STUDIO
# ==============================================================================

elif current_page == "Predictive AI Studio":
    st.markdown(
        """
        <div class="insight-card warning" style="margin-bottom: 16px;">
            <div class="insight-title">📌 Governance & Calibration Transparency</div>
            <p class="insight-desc">Olist transactions do not contain native subscription churn logs. Machine learning models in this platform are trained on calibrated portfolio proxy targets using XGBoost to demonstrate enterprise analytics, propensity scoring, and automated decision playbooks.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    feature_importance = load_csv("model_feature_importance.csv")
    model_evaluation = load_csv("model_evaluation.csv")

    pred_tab_churn, pred_tab_clv = st.tabs([
        "🔮 Churn Propensity What-If Simulator",
        "💎 12-Month CLV Scenario Estimator",
    ])

    with pred_tab_churn:
        churn_model = load_model("churn_model.pkl")
        sim_col_l, sim_col_r = st.columns([0.5, 0.5])

        with sim_col_l:
            with st.form("churn_sim_form"):
                st.markdown("**Simulate Customer Scenario Parameters:**")
                c1, c2 = st.columns(2)
                sim_recency = c1.number_input("Days Inactive (Recency)", min_value=0, max_value=800, value=90, step=5)
                sim_frequency = c2.number_input("Total Orders (Frequency)", min_value=1, max_value=50, value=2, step=1)

                c3, c4 = st.columns(2)
                sim_monetary = c3.number_input("Total Spend (BRL)", min_value=5.0, max_value=50000.0, value=280.0, step=10.0)
                sim_aov = c4.number_input("Average Order Value (BRL)", min_value=5.0, max_value=25000.0, value=140.0, step=10.0)

                c5, c6 = st.columns(2)
                sim_products = c5.number_input("Distinct Products", min_value=1, max_value=50, value=2, step=1)
                sim_age = c6.number_input("Customer Purchase Span (Days)", min_value=1, max_value=800, value=45, step=5)

                churn_submit = st.form_submit_button("Run Live Churn Propensity Inference", type="primary", use_container_width=True)

            if churn_model is not None:
                input_df = model_input_frame(sim_recency, sim_frequency, sim_monetary, sim_aov, sim_products, sim_age)
                prob = float(churn_model.predict_proba(input_df)[0, 1])
                band = "High Risk" if prob >= 0.65 else "Medium Risk" if prob >= 0.35 else "Low Risk"
                band_color = "#EF4444" if prob >= 0.65 else "#F59E0B" if prob >= 0.35 else "#10B981"

                with sim_col_r:
                    st.markdown("**Live Scenario Prediction Output:**")
                    res_c1, res_c2 = st.columns(2)
                    res_c1.metric("Predicted Churn Risk", format_pct(prob))
                    res_c2.metric("Risk Classification", band)

                    act = retention_action(prob)
                    st.info(f"**Automated Retention Playbook:** {act['action']}")

                    g_fig = go.Figure(go.Indicator(
                        mode="gauge+number",
                        value=100 * prob,
                        number={"suffix": "%", "font": {"family": "JetBrains Mono"}},
                        title={"text": "<b>Churn Propensity Meter</b>"},
                        gauge={
                            "axis": {"range": [0, 100]},
                            "bar": {"color": band_color},
                            "steps": [
                                {"range": [0, 35], "color": "rgba(16,185,129,0.15)"},
                                {"range": [35, 65], "color": "rgba(245,158,11,0.15)"},
                                {"range": [65, 100], "color": "rgba(239,68,68,0.15)"},
                            ],
                        },
                    ))
                    g_fig.update_layout(height=200, margin=dict(l=15, r=15, t=30, b=5), paper_bgcolor="rgba(0,0,0,0)")
                    st.plotly_chart(g_fig, use_container_width=True, config=PLOT_CONFIG)
            else:
                st.info("Churn pipeline model (`churn_model.pkl`) is ready to load.")

        # Feature Importance
        if not feature_importance.empty:
            st.markdown('<div class="section-header"><h3>Global Feature Drivers (XGBoost Churn Classifier)</h3></div>', unsafe_allow_html=True)
            sorted_imp = feature_importance.sort_values("churn_importance", ascending=True)
            fig_imp = px.bar(
                sorted_imp,
                x="churn_importance",
                y="feature",
                orientation="h",
                title="Relative Feature Importance for Churn Prediction",
                color="churn_importance",
                color_continuous_scale="Reds",
            )
            fig_imp.update_layout(coloraxis_showscale=False)
            fig_imp.update_xaxes(title="Relative Importance Weight")
            fig_imp.update_yaxes(title=None)
            chart(fig_imp, 280, legend="hidden", dark_mode=st.session_state.dark_mode)

    with pred_tab_clv:
        clv_model = load_model("clv_model.pkl")
        clv_l, clv_r = st.columns([0.5, 0.5])

        with clv_l:
            with st.form("clv_sim_form"):
                st.markdown("**Simulate Forward Customer Value Parameters:**")
                k1, k2 = st.columns(2)
                clv_rec = k1.number_input("Days Inactive", min_value=0, max_value=800, value=30, step=5, key="c_rec")
                clv_freq = k2.number_input("Orders Placed", min_value=1, max_value=50, value=3, step=1, key="c_freq")

                k3, k4 = st.columns(2)
                clv_mon = k3.number_input("Historical Spend (BRL)", min_value=5.0, max_value=50000.0, value=450.0, step=10.0, key="c_mon")
                clv_aov = k4.number_input("Average Order Value (BRL)", min_value=5.0, max_value=25000.0, value=150.0, step=10.0, key="c_aov")

                k5, k6 = st.columns(2)
                clv_prod = k5.number_input("Products Purchased", min_value=1, max_value=50, value=3, step=1, key="c_prod")
                clv_span = k6.number_input("Purchase Span (Days)", min_value=1, max_value=800, value=90, step=5, key="c_span")

                clv_submit = st.form_submit_button("Run Live 12-Month CLV Estimation", type="primary", use_container_width=True)

            if clv_model is not None:
                clv_input = model_input_frame(clv_rec, clv_freq, clv_mon, clv_aov, clv_prod, clv_span)
                est_clv = max(float(clv_model.predict(clv_input)[0]), 0.0)
                interval_low = est_clv * 0.85
                interval_high = est_clv * 1.15

                q25, q50, q75 = filtered["predicted_clv"].quantile([0.25, 0.50, 0.75])
                val_tier = "Platinum VIP" if est_clv >= q75 else "Gold Tier" if est_clv >= q50 else "Silver Tier" if est_clv >= q25 else "Bronze Tier"

                with clv_r:
                    st.markdown("**12-Month Forward Value Forecast:**")
                    clv_c1, clv_c2 = st.columns(2)
                    clv_c1.metric("Predicted 12M CLV", format_brl(est_clv))
                    clv_c2.metric("Customer Value Tier", val_tier)

                    st.markdown(f"**80% Planning Range:** `{format_brl(interval_low)}` — `{format_brl(interval_high)}`")
                    st.info("💡 **Commercial Strategy:** Prioritize premium VIP loyalty recognition, dedicated concierge support, and early access cross-sell." if "Platinum" in val_tier or "Gold" in val_tier else "💡 **Commercial Strategy:** Target with category cross-sell discounts to build order frequency.")
            else:
                st.info("CLV regression model (`clv_model.pkl`) is ready.")

        # CLV Distribution
        fig_clv_dist = px.histogram(
            filtered,
            x="predicted_clv",
            nbins=40,
            title="Distribution of 12-Month Predicted CLV Across Customer Base",
            color_discrete_sequence=[BRAND_TEAL],
        )
        fig_clv_dist.update_xaxes(title="Predicted CLV (BRL)")
        fig_clv_dist.update_yaxes(title="Customer Count")
        chart(fig_clv_dist, 280, legend="hidden", dark_mode=st.session_state.dark_mode)

    # Model Evaluation Benchmarks
    st.markdown('<div class="section-header"><h3>Held-Out Model Benchmark Leaderboard</h3><span>Notebook 05 Cross-Validation Results</span></div>', unsafe_allow_html=True)
    if not model_evaluation.empty:
        st.dataframe(model_evaluation, hide_index=True, use_container_width=True)


# ==============================================================================
# WORKSPACE 5: EXPERIENCE & VOC RADAR
# ==============================================================================

elif current_page == "Experience & VoC Radar":
    sentiment = load_csv("product_sentiment.csv")
    product_reviews = load_csv("fact_product_reviews.csv", ("review_date",))
    fact_campaign = load_csv("fact_campaign.csv")
    dim_campaign = load_csv("dim_campaign.csv")

    exp_tab1, exp_tab2 = st.tabs([
        "💬 Voice of Customer & NLP Classifier",
        "🎯 Marketing Campaign Funnel & ROI",
    ])

    with exp_tab1:
        nlp_col1, nlp_col2 = st.columns([0.45, 0.55])
        with nlp_col1:
            st.markdown("**Live Review Text NLP Classifier:**")
            sample_text = st.text_area(
                "Customer Review / Feedback",
                value="The product arrived two days early, packaged securely, and exceeded my expectations!",
                height=110,
            )
            nlp_btn = st.button("Classify Sentiment", icon=":material/sentiment_satisfied:", type="primary", use_container_width=True)

            sentiment_model = load_model("sentiment_model.pkl")
            if nlp_btn and sample_text.strip():
                if sentiment_model is not None:
                    pred_label = sentiment_model.predict([sample_text])[0]
                    pred_prob = sentiment_model.predict_proba([sample_text])[0].max()
                    pill_color = "#10B981" if pred_label == "Positive" else "#F59E0B" if pred_label == "Neutral" else "#EF4444"
                    st.markdown(
                        f"""
                        <div style="background: var(--bg-surface-elevated); border: 1px solid var(--border-color); border-radius: 8px; padding: 14px; margin-top: 10px;">
                            <div style="font-size: 12px; color: var(--text-muted); text-transform: uppercase; font-weight: 700;">Classification Result</div>
                            <div style="font-size: 22px; font-weight: 800; color: {pill_color}; margin-top: 4px;">{pred_label} ({pred_prob:.1%} Confidence)</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                else:
                    st.info("Sentiment classification model (`sentiment_model.pkl`) is ready.")

        with nlp_col2:
            if not sentiment.empty:
                sent_mix = sentiment.groupby("sentiment_label", as_index=False)["review_count"].sum()
                fig_sent_pie = px.pie(
                    sent_mix,
                    names="sentiment_label",
                    values="review_count",
                    hole=0.52,
                    title="Overall Review Sentiment Distribution",
                    color="sentiment_label",
                    color_discrete_map={"Positive": BRAND_GREEN, "Neutral": BRAND_AMBER, "Negative": BRAND_CORAL},
                )
                chart(fig_sent_pie, 260, legend="bottom", dark_mode=st.session_state.dark_mode)

        # Sentiment Trends & Explorer
        if not product_reviews.empty:
            with st.expander("Monthly Sentiment Trends & Review Explorer", expanded=True, icon=":material/trending_up:"):
                trend_df = product_reviews.dropna(subset=["review_date"]).copy()
                trend_df["review_date"] = pd.to_datetime(trend_df["review_date"], errors="coerce")
                trend_df = trend_df.dropna(subset=["review_date"])
                trend_df["month"] = trend_df["review_date"].dt.to_period("M").astype(str)
                monthly_trend = trend_df.groupby(["month", "sentiment_label"], as_index=False).size()

                fig_trend = px.line(
                    monthly_trend,
                    x="month",
                    y="size",
                    color="sentiment_label",
                    markers=True,
                    title="Review Volume by Sentiment Over Time",
                    color_discrete_map={"Positive": BRAND_GREEN, "Neutral": BRAND_AMBER, "Negative": BRAND_CORAL},
                )
                fig_trend.update_xaxes(title="Month")
                fig_trend.update_yaxes(title="Reviews")
                chart(fig_trend, 280, legend="bottom", dark_mode=st.session_state.dark_mode)

                st.markdown("**Sample Review Feedback Database:**")
                st.dataframe(
                    product_reviews[["review_date", "category_name", "rating", "sentiment_label", "review_text"]].head(50),
                    hide_index=True,
                    use_container_width=True,
                    height=240,
                )

    with exp_tab2:
        st.markdown('<div class="insight-card"><p class="insight-desc">Marketing campaign logs represent synthetic event simulation to illustrate funnel stages, conversion drop-offs, and multi-channel ROI analysis.</p></div>', unsafe_allow_html=True)
        if not fact_campaign.empty and not dim_campaign.empty:
            camp_agg = (
                fact_campaign.groupby("campaign_id", as_index=False)
                .agg(
                    sent=("email_sent", "sum"),
                    opened=("opened", "sum"),
                    clicked=("clicked", "sum"),
                    converted=("converted", "sum"),
                    revenue=("revenue_generated", "sum"),
                )
                .merge(dim_campaign[["campaign_id", "campaign_type", "campaign_cost"]], on="campaign_id", how="left")
            )
            camp_agg["roi"] = (camp_agg["revenue"] - camp_agg["campaign_cost"]) / camp_agg["campaign_cost"]

            funnel_totals = camp_agg[["sent", "opened", "clicked", "converted"]].sum()
            funnel_df = pd.DataFrame({"Stage": ["Sent", "Opened", "Clicked", "Converted"], "Audience": funnel_totals.values})

            f_col1, f_col2 = st.columns(2)
            with f_col1:
                fig_funnel = px.funnel(funnel_df, x="Audience", y="Stage", title="Omnichannel Campaign Conversion Funnel", color_discrete_sequence=[BRAND_TEAL])
                chart(fig_funnel, 300, legend="hidden", dark_mode=st.session_state.dark_mode)

            with f_col2:
                fig_roi = px.bar(
                    camp_agg.sort_values("roi", ascending=True),
                    x="roi",
                    y="campaign_type",
                    orientation="h",
                    title="Campaign Return on Investment (ROI)",
                    color="roi",
                    color_continuous_scale="Teal",
                )
                fig_roi.update_xaxes(title="ROI Multiplier")
                fig_roi.update_yaxes(title=None)
                chart(fig_roi, 300, legend="hidden", dark_mode=st.session_state.dark_mode)


# ==============================================================================
# WORKSPACE 6: NEXT-BEST-OFFER & CATALOG
# ==============================================================================

elif current_page == "Next-Best-Offer & Catalog":
    recommendations = load_csv("recommendations.csv")
    fact_orders = load_csv("fact_orders.csv", ("purchase_date",))
    dim_product = load_csv("dim_product.csv")
    sentiment = load_csv("product_sentiment.csv")

    rec_tab1, rec_tab2 = st.tabs([
        "🎯 Customer Recommendation Lookup",
        "📊 Merchandising & Basket Associations",
    ])

    with rec_tab1:
        if not recommendations.empty:
            cust_options = sorted(recommendations["customer_id"].dropna().unique())
            sel_rec_cust = st.selectbox("Find Recommendations for Customer", cust_options, index=0)
            rec_results = recommendations[recommendations["customer_id"] == sel_rec_cust].sort_values("rank")

            st.markdown(f"**Top Ranked Next-Best-Category Offers for Customer `{sel_rec_cust}`:**")
            r_cols = st.columns(min(len(rec_results), 5))
            for i, (_, rec_row) in enumerate(rec_results.head(5).iterrows()):
                with r_cols[i]:
                    st.markdown(
                        f"""
                        <div class="rec-card">
                            <span class="rec-card-rank">#{int(rec_row['rank'])}</span>
                            <div class="rec-card-title">{rec_row['recommended_category']}</div>
                            <p class="rec-card-reason"><strong>Logic:</strong> {rec_row['reason']}</p>
                            <div style="margin-top: 8px; font-size: 11px; color: var(--teal); font-weight: 600;">
                                Engine: {rec_row.get('method', 'Basket Association')}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            # Recommendation Methodology Breakdown
            method_counts = recommendations["method"].value_counts().reset_index()
            method_counts.columns = ["Recommendation Method", "Volume"]
            fig_method = px.bar(
                method_counts,
                x="Recommendation Method",
                y="Volume",
                title="Recommendation Engine Logic Distribution",
                color="Recommendation Method",
                color_discrete_sequence=[BRAND_TEAL, BRAND_CORAL],
            )
            chart(fig_method, 260, legend="hidden", dark_mode=st.session_state.dark_mode)
        else:
            st.info("Recommendations dataset is loading.")

    with rec_tab2:
        if not fact_orders.empty and not dim_product.empty:
            order_prod = fact_orders.merge(dim_product[["product_id", "category_name_english"]], on="product_id", how="left")
            cat_perf = (
                order_prod.groupby("category_name_english", as_index=False)
                .agg(revenue=("revenue", "sum"), orders=("order_id", "nunique"), products=("product_id", "nunique"))
                .sort_values("revenue", ascending=False)
            )

            baskets = order_prod.groupby("order_id")["category_name_english"].apply(lambda vals: sorted(set(vals.dropna())))
            pair_dict = {}
            for b in baskets:
                for p in combinations(b, 2):
                    pair_dict[p] = pair_dict.get(p, 0) + 1
            pairs_df = pd.DataFrame([{"Category A": p[0], "Category B": p[1], "Co-occurrences": c} for p, c in pair_dict.items()])
            if not pairs_df.empty:
                pairs_df = pairs_df.sort_values("Co-occurrences", ascending=False).head(20)

            c_left, c_right = st.columns(2)
            with c_left:
                top_cats = cat_perf.head(10).sort_values("revenue", ascending=True)
                fig_top_cats = px.bar(
                    top_cats,
                    x="revenue",
                    y="category_name_english",
                    orientation="h",
                    title="Top 10 Product Categories by Merchandise GMV",
                    color="revenue",
                    color_continuous_scale="Teal",
                )
                fig_top_cats.update_layout(coloraxis_showscale=False)
                fig_top_cats.update_xaxes(title="Revenue (BRL)")
                fig_top_cats.update_yaxes(title=None)
                chart(fig_top_cats, 320, legend="hidden", dark_mode=st.session_state.dark_mode)

            with c_right:
                if not sentiment.empty:
                    low_cats = sentiment[sentiment["review_count"] >= 20].nsmallest(10, "avg_rating").sort_values("avg_rating", ascending=True)
                    fig_low_cats = px.bar(
                        low_cats,
                        x="avg_rating",
                        y="category_name",
                        orientation="h",
                        title="Categories Requiring Quality / Supplier Review",
                        color="avg_rating",
                        color_continuous_scale="Reds",
                    )
                    fig_low_cats.update_layout(coloraxis_showscale=False)
                    fig_low_cats.update_xaxes(title="Average CSAT Rating (1-5)")
                    fig_low_cats.update_yaxes(title=None)
                    chart(fig_low_cats, 320, legend="hidden", dark_mode=st.session_state.dark_mode)

            st.markdown('<div class="section-header"><h3>Frequently Bought Together (Cross-Category Basket Rules)</h3></div>', unsafe_allow_html=True)
            st.dataframe(pairs_df, hide_index=True, use_container_width=True)


# ==============================================================================
# WORKSPACE 7: DATA WAREHOUSE & SQL CONSOLE
# ==============================================================================

elif current_page == "Data Warehouse & SQL":
    fact_orders = load_csv("fact_orders.csv", ("purchase_date",))
    segment_summary = load_csv("segment_summary.csv")
    model_evaluation = load_csv("model_evaluation.csv")
    recommendations = load_csv("recommendations.csv")

    st.markdown('<div class="section-header"><h3>Data Warehouse Architecture & Source Governance</h3></div>', unsafe_allow_html=True)
    sources = [
        {"Source Domain": "Olist E-Commerce", "Role in Customer 360": "Canonical customer identities, order items, payments, reviews", "Governance Rule": "Truth layer for all transactions & RFM"},
        {"Source Domain": "Clickstream Events", "Role in Customer 360": "Digital web activity, sessions, views, cart additions", "Governance Rule": "Simulated identity map for behavioral enrichment"},
        {"Source Domain": "Amazon Datafiniti Reviews", "Role in Customer 360": "Product-level NLP sentiment & Voice of Customer benchmarks", "Governance Rule": "Independent benchmark; no customer joins"},
        {"Source Domain": "Synthetic Marketing Campaigns", "Role in Customer 360": "Omnichannel campaign logs, open/click rates, ROI metrics", "Governance Rule": "Synthetic demonstration of marketing attribution"},
    ]
    st.dataframe(pd.DataFrame(sources), hide_index=True, use_container_width=True)

    # Readiness checklist
    art_col1, art_col2 = st.columns(2)
    with art_col1:
        st.markdown("**Warehouse Artifact Readiness:**")
        status_table = pd.DataFrame([
            {"Artifact": "Canonical Customer Features", "Rows": f"{len(customer_features):,}", "Status": "Ready 🟢"},
            {"Artifact": "Dimensional Order Transactions", "Rows": f"{len(fact_orders):,}" if not fact_orders.empty else "0", "Status": "Ready 🟢" if not fact_orders.empty else "Missing 🔴"},
            {"Artifact": "AI Next-Best-Offer Catalog", "Rows": f"{len(recommendations):,}" if not recommendations.empty else "0", "Status": "Ready 🟢" if not recommendations.empty else "Missing 🔴"},
            {"Artifact": "Model Evaluation Benchmarks", "Rows": f"{len(model_evaluation):,}" if not model_evaluation.empty else "0", "Status": "Ready 🟢" if not model_evaluation.empty else "Missing 🔴"},
        ])
        st.dataframe(status_table, hide_index=True, use_container_width=True)

    with art_col2:
        st.markdown("**Enterprise Data Contracts & Limitations:**")
        st.info("• Churn and 12-Month CLV are calibrated portfolio proxy models.\n• Monetary units use Brazilian Reais (BRL, R$).\n• All outputs comply with the Release Validation checks in Notebook 06.")

    # Business Query Sandbox Runner
    st.markdown('<div class="section-header"><h3>Predefined Business Analytics Query Engine</h3><span>Instant SQL Analysis</span></div>', unsafe_allow_html=True)

    q_controls = st.columns([0.5, 0.25, 0.25])
    query_choice = q_controls[0].selectbox(
        "Select Analytical Query",
        [
            "Revenue by State & Region",
            "Top Customer Segments by GMV",
            "High-Risk Churn Customers",
            "Highest-CLV VIP Customers",
        ],
    )

    valid_orders = fact_orders[~fact_orders["order_status"].isin(["canceled", "unavailable"])].copy() if not fact_orders.empty else pd.DataFrame()

    if query_choice == "Revenue by State & Region":
        if not valid_orders.empty:
            q_result = (
                customer_features[["customer_id", "state"]]
                .merge(valid_orders[["customer_id", "order_id", "revenue"]], on="customer_id", how="inner")
                .groupby("state", as_index=False)
                .agg(customers=("customer_id", "nunique"), orders=("order_id", "nunique"), revenue=("revenue", "sum"))
                .sort_values("revenue", ascending=False)
            )
        else:
            q_result = customer_features.groupby("state", as_index=False)["total_spend"].sum().rename(columns={"total_spend": "revenue"}).sort_values("revenue", ascending=False)
    elif query_choice == "Top Customer Segments by GMV":
        q_result = segment_summary.sort_values("revenue", ascending=False) if not segment_summary.empty else pd.DataFrame()
    elif query_choice == "High-Risk Churn Customers":
        q_result = customer_features[customer_features["churn_probability"] >= 0.65][["customer_id", "state", "rfm_segment", "total_spend", "predicted_clv", "churn_probability"]].sort_values("churn_probability", ascending=False).head(500)
    else:
        q_result = customer_features.nlargest(500, "predicted_clv")[["customer_id", "state", "rfm_segment", "total_spend", "predicted_clv", "clv_band"]]

    q_controls[1].download_button(
        "Download Query Result (CSV)",
        q_result.to_csv(index=False).encode("utf-8"),
        f"{query_choice.lower().replace(' ', '_')}.csv",
        "text/csv",
        icon=":material/download:",
        use_container_width=True,
    )

    # Search & Pagination
    s_col1, s_col2 = st.columns([0.7, 0.3])
    table_search = s_col1.text_input("Filter / Search Query Rows", placeholder="Type any keyword, state, or ID...")
    page_size = s_col2.selectbox("Page Size", [10, 25, 50, 100], index=1)

    filtered_q = q_result.copy()
    if table_search:
        mask = filtered_q.astype(str).apply(lambda col: col.str.contains(table_search, case=False, na=False)).any(axis=1)
        filtered_q = filtered_q[mask]

    tot_pages = max(1, int(np.ceil(len(filtered_q) / page_size)))
    page_no = st.number_input("Page", min_value=1, max_value=tot_pages, value=1)
    start_idx = (page_no - 1) * page_size

    st.dataframe(filtered_q.iloc[start_idx : start_idx + page_size], hide_index=True, use_container_width=True)
    st.caption(f"Showing page {page_no} of {tot_pages} | {len(filtered_q):,} total records")

    # SQL Library Viewer
    sql_file = SQL_DIR / "business_queries.sql"
    with st.expander("Inspect Business SQL Query Catalog (`sql/business_queries.sql`)", expanded=False, icon=":material/code:"):
        if sql_file.exists():
            sql_code = sql_file.read_text(encoding="utf-8")
            st.code(sql_code, language="sql")
            st.download_button(
                "Download SQL Catalog",
                sql_code.encode("utf-8"),
                "business_queries.sql",
                "text/sql",
                icon=":material/download:",
            )
        else:
            st.warning("SQL business query catalog not found at `sql/business_queries.sql`.")
