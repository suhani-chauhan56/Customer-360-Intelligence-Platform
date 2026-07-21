"""Compact Customer 360 Streamlit workspace.

Run from the project root:
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


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
MODELS = ROOT / "models"
PLOT_CONFIG = {"displaylogo": False, "responsive": True, "scrollZoom": False}
MODEL_COLUMNS = [
    "recency_days",
    "frequency",
    "monetary",
    "avg_order_value",
    "number_of_products",
    "customer_age_days",
]
NAV_ITEMS = [
    ("Executive Overview", ":material/space_dashboard:"),
    ("Customer Explorer", ":material/person_search:"),
    ("Segments", ":material/donut_large:"),
    ("Predictions", ":material/query_stats:"),
    ("Experience", ":material/reviews:"),
    ("Recommendations", ":material/recommend:"),
    ("Data & SQL", ":material/database:"),
]
PAGE_COPY = {
    "Executive Overview": ("Executive overview", "Revenue, retention, and customer value at a glance."),
    "Customer Explorer": ("Customer explorer", "Find one customer and see the complete commercial story."),
    "Segments": ("Customer segments", "Compare audiences and identify where to focus next."),
    "Predictions": ("Predictive intelligence", "Explore calibrated churn and forward-value scenarios."),
    "Experience": ("Customer experience", "Review sentiment and campaign response in one focused view."),
    "Recommendations": ("Next best category", "Turn purchase history into a simple, explainable offer."),
    "Data & SQL": ("Data and SQL", "Understand the sources, limitations, and reusable query library."),
}
PAGE_GUIDE = {
    "Executive Overview": ["Track commercial health", "Find valuable audiences", "Spot retention pressure"],
    "Customer Explorer": ["Search a unified profile", "Review engagement and history", "Choose the next action"],
    "Segments": ["Compare RFM audiences", "Measure revenue contribution", "Drill into behavior clusters"],
    "Predictions": ["Estimate churn propensity", "Model forward customer value", "Understand global model drivers"],
    "Experience": ["Classify review sentiment", "Explore complaints and praise", "Compare campaign performance"],
    "Recommendations": ["Select the next offer", "Explain recommendation logic", "Review product performance"],
    "Data & SQL": ["Check artifact readiness", "Run predefined analyses", "Download query results"],
}

st.set_page_config(
    page_title="CustomerAtlas AI | Customer 360 Intelligence",
    page_icon=":material/hub:",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data(show_spinner=False)
def load_csv(name: str, parse_dates: tuple[str, ...] = ()) -> pd.DataFrame:
    path = PROCESSED / name
    return pd.read_csv(path, parse_dates=list(parse_dates)) if path.exists() else pd.DataFrame()


@st.cache_resource(show_spinner=False)
def load_model(name: str):
    path = MODELS / name
    return joblib.load(path) if path.exists() else None


def format_brl(value: float) -> str:
    return "R$ 0" if pd.isna(value) else f"R$ {float(value):,.0f}"


def format_pct(value: float) -> str:
    return "0.0%" if pd.isna(value) else f"{100 * float(value):.1f}%"


def chart(figure, height: int = 300, legend: str = "bottom") -> None:
    """Render a compact chart while reserving separate title and legend space."""
    dark_mode = st.session_state.get("dark_mode", False)
    text_color = "#dce7eb" if dark_mode else "#263942"
    title_color = "#f5f8f9" if dark_mode else "#162a33"
    has_multi_item_legend = len(figure.data) > 1 or any(
        getattr(trace, "type", "") in {"pie", "funnelarea"} for trace in figure.data
    )
    show_legend = legend != "hidden" and has_multi_item_legend
    bottom_margin = 72 if show_legend and legend == "bottom" else 34
    legend_layout = (
        dict(
            orientation="h",
            yanchor="top",
            y=-0.16,
            xanchor="center",
            x=0.5,
            font=dict(size=11),
            itemclick="toggleothers",
            itemdoubleclick="toggle",
        )
        if legend == "bottom"
        else dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.02,
            font=dict(size=11),
        )
    )
    figure.update_layout(
        height=height,
        margin=dict(l=14, r=14, t=58, b=bottom_margin),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=text_color, size=12),
        title=dict(
            font=dict(size=16, color=title_color),
            x=0.02,
            xanchor="left",
            y=0.97,
            yanchor="top",
        ),
        showlegend=show_legend,
        legend_title_text="",
        legend=legend_layout,
        hoverlabel=dict(bgcolor="white", font_size=12),
    )
    st.plotly_chart(figure, width="stretch", config=PLOT_CONFIG)


def page_header(page: str) -> None:
    title, description = PAGE_COPY[page]
    guide_items = "".join(f"<li>{item}</li>" for item in PAGE_GUIDE[page])
    st.markdown(
        f"""
        <div class="page-head">
          <div class="page-title-block">
            <p class="eyebrow">CUSTOMERATLAS AI / CUSTOMER 360 INTELLIGENCE</p>
            <h1>{title}</h1>
            <p>{description}</p>
          </div>
          <div class="head-aside">
            <div class="signal-bars" aria-hidden="true"><b></b><b></b><b></b><b></b><b></b></div>
            <div class="status-row">
              <span class="status"><i></i>Data ready</span>
              <span class="status">BRL</span>
              <span class="status">Portfolio model</span>
            </div>
          </div>
          <div class="flow-line"><span></span></div>
        </div>
        <div class="page-guide"><strong>This page helps you:</strong><ul>{guide_items}</ul></div>
        """,
        unsafe_allow_html=True,
    )


def section_intro(title: str, note: str) -> None:
    st.markdown(f'<div class="section-title"><h2>{title}</h2><p>{note}</p></div>', unsafe_allow_html=True)


def require_release_data(frame: pd.DataFrame) -> None:
    if frame.empty:
        st.error("App data is missing. Run notebooks 01 through 06 in order.")
        st.code("jupyter notebook\nstreamlit run streamlit_app/app.py", language="bash")
        st.stop()
    required = {"customer_id", "total_spend", "total_orders", "rfm_segment", "predicted_clv", "churn_probability"}
    missing = sorted(required - set(frame.columns))
    if missing:
        st.error(f"Customer output is missing: {missing}. Rerun notebooks 05 and 06.")
        st.stop()


def retention_action(probability: float, segment: str = "") -> str:
    if probability >= 0.65:
        return "Priority recovery: contact the customer, review friction, and use a controlled win-back offer."
    if probability >= 0.35:
        return "Nurture: send a category-specific reminder and review campaign frequency."
    if segment in {"Champions", "Loyal Customers"}:
        return "Protect value: recognize loyalty and offer a relevant cross-sell."
    return "Develop value: simplify product discovery and encourage a second purchase."


def model_input_frame(recency, frequency, monetary, avg_order_value, products, age) -> pd.DataFrame:
    return pd.DataFrame(
        [[recency, frequency, monetary, avg_order_value, products, age]],
        columns=MODEL_COLUMNS,
    )


def animated_kpis(items: list[dict]) -> None:
    """Render responsive KPI counters with a real requestAnimationFrame count-up."""
    dark_mode = st.session_state.get("dark_mode", False)
    cards = "".join(
        f'''<div class="metric-card">
              <div class="metric-label">{item["label"]}</div>
              <div class="metric-value" data-value="{float(item["value"])}" data-format="{item["format"]}">0</div>
              <div class="metric-note">{item["note"]}</div>
            </div>'''
        for item in items
    )
    background = "#172d37" if dark_mode else "#ffffff"
    ink = "#f4f8f9" if dark_mode else "#1b3039"
    muted = "#a9bbc2" if dark_mode else "#647780"
    line = "#34505c" if dark_mode else "#dbe4e7"
    st.iframe(
        f"""
        <style>
          * {{ box-sizing: border-box; font-family: Inter, ui-sans-serif, system-ui, sans-serif; }}
          body {{ margin: 0; background: transparent; overflow: hidden; }}
          .metric-grid {{ display: grid; grid-template-columns: repeat(6, minmax(0, 1fr)); gap: 10px; padding: 1px; }}
          .metric-card {{
            min-width: 0; height: 96px; padding: 13px 14px; background: {background};
            border: 1px solid {line}; border-radius: 5px; position: relative; overflow: hidden;
            animation: rise .45s ease-out both; transition: transform .18s ease, box-shadow .18s ease;
          }}
          .metric-card::before {{ content: ""; position: absolute; left: 0; top: 0; bottom: 0; width: 3px; background: #117a72; }}
          .metric-card:hover {{ transform: translateY(-3px); box-shadow: 0 9px 22px rgba(16, 52, 63, .12); }}
          .metric-label {{ color: {muted}; font-size: 11px; font-weight: 650; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
          .metric-value {{ color: {ink}; font-size: 22px; line-height: 1.2; font-weight: 760; margin-top: 7px; white-space: nowrap; }}
          .metric-note {{ color: {muted}; font-size: 9px; margin-top: 3px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
          @keyframes rise {{ from {{ opacity: 0; transform: translateY(8px); }} to {{ opacity: 1; transform: none; }} }}
          @media (max-width: 1000px) {{ .metric-grid {{ grid-template-columns: repeat(3, 1fr); }} body {{ overflow: auto; }} }}
          @media (max-width: 560px) {{ .metric-grid {{ grid-template-columns: repeat(2, 1fr); }} }}
        </style>
        <div class="metric-grid">{cards}</div>
        <script>
          const duration = 850;
          const formatValue = (value, format) => {{
            if (format === "currency") return "R$ " + Math.round(value).toLocaleString("en-US");
            if (format === "percent") return value.toFixed(1) + "%";
            if (format === "rating") return value.toFixed(1) + " / 5";
            return Math.round(value).toLocaleString("en-US");
          }};
          document.querySelectorAll(".metric-value").forEach((element, index) => {{
            const target = Number(element.dataset.value);
            const startAt = performance.now() + index * 55;
            const tick = (now) => {{
              const progress = Math.min(Math.max((now - startAt) / duration, 0), 1);
              const eased = 1 - Math.pow(1 - progress, 3);
              element.textContent = formatValue(target * eased, element.dataset.format);
              if (progress < 1) requestAnimationFrame(tick);
            }};
            requestAnimationFrame(tick);
          }});
        </script>
        """,
        width="stretch",
        height=108 if len(items) <= 6 else 216,
    )


def build_profile_pdf(profile: pd.Series) -> bytes:
    """Create a compact customer profile report without storing temporary files."""
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
    from reportlab.lib import colors

    buffer = BytesIO()
    document = SimpleDocTemplate(buffer, pagesize=A4, title="Customer 360 Profile")
    styles = getSampleStyleSheet()
    fields = [
        ("Customer ID", profile.get("customer_id", "")),
        ("Location", f"{profile.get('city', '')}, {profile.get('state', '')}"),
        ("RFM Segment", profile.get("rfm_segment", "")),
        ("Behavior Cluster", profile.get("cluster_segment", "")),
        ("Favorite Category", profile.get("favorite_category", "")),
        ("Total Spend", format_brl(profile.get("total_spend", 0))),
        ("Orders", int(profile.get("total_orders", 0))),
        ("CLV Proxy", format_brl(profile.get("predicted_clv", 0))),
        ("Churn Propensity", format_pct(profile.get("churn_probability", 0))),
        ("Recommended Action", retention_action(float(profile.get("churn_probability", 0)), str(profile.get("rfm_segment", "")))),
    ]
    table = Table([["Attribute", "Value"], *fields], colWidths=[130, 360])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#117a72")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#dbe4e7")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("PADDING", (0, 0), (-1, -1), 7),
    ]))
    document.build([
        Paragraph("CustomerAtlas AI - Customer 360 Profile", styles["Title"]),
        Paragraph("Unified customer profile report", styles["Heading2"]),
        Spacer(1, 12),
        table,
    ])
    return buffer.getvalue()


def predefined_analysis(name: str) -> pd.DataFrame:
    """Run recruiter-friendly analytical queries on processed warehouse extracts."""
    valid_orders = fact_orders.loc[~fact_orders["order_status"].isin(["canceled", "unavailable"])].copy()
    if name == "Revenue by state":
        return (
            customer_features[["customer_id", "state"]]
            .merge(valid_orders[["customer_id", "order_id", "revenue"]], on="customer_id", how="inner")
            .groupby("state", as_index=False)
            .agg(customers=("customer_id", "nunique"), orders=("order_id", "nunique"), revenue=("revenue", "sum"))
            .sort_values("revenue", ascending=False)
        )
    if name == "Top customer segments":
        return segment_summary.sort_values("revenue", ascending=False).copy()
    if name == "High-risk customers":
        columns = ["customer_id", "state", "rfm_segment", "total_spend", "predicted_clv", "churn_probability"]
        return customer_features.loc[customer_features["churn_probability"].ge(0.65), columns].sort_values("churn_probability", ascending=False).head(500)
    columns = ["customer_id", "state", "rfm_segment", "total_spend", "predicted_clv", "clv_band"]
    return customer_features.nlargest(500, "predicted_clv")[columns]


@st.cache_data(show_spinner=False)
def extract_review_terms(label: str, limit: int = 8) -> pd.DataFrame:
    """Extract understandable complaint or praise phrases from review text."""
    from sklearn.feature_extraction.text import CountVectorizer

    reviews = product_reviews.loc[
        product_reviews["sentiment_label"].eq(label), "review_text"
    ].dropna().astype(str)
    if reviews.empty:
        return pd.DataFrame(columns=["phrase", "mentions"])
    vectorizer = CountVectorizer(stop_words="english", ngram_range=(1, 2), min_df=3, max_features=500)
    matrix = vectorizer.fit_transform(reviews)
    totals = np.asarray(matrix.sum(axis=0)).ravel()
    terms = pd.DataFrame({"phrase": vectorizer.get_feature_names_out(), "mentions": totals})
    return terms.nlargest(limit, "mentions").reset_index(drop=True)


@st.cache_data(show_spinner=False)
def product_intelligence_tables() -> tuple[pd.DataFrame, pd.DataFrame]:
    order_products = fact_orders.merge(
        dim_product[["product_id", "category_name_english"]], on="product_id", how="left"
    )
    category_performance = (
        order_products.groupby("category_name_english", as_index=False)
        .agg(revenue=("revenue", "sum"), orders=("order_id", "nunique"), products=("product_id", "nunique"))
        .sort_values("revenue", ascending=False)
    )
    baskets = order_products.groupby("order_id")["category_name_english"].apply(
        lambda values: sorted(set(values.dropna()))
    )
    pair_counts: dict[tuple[str, str], int] = {}
    for basket in baskets:
        for pair in combinations(basket, 2):
            pair_counts[pair] = pair_counts.get(pair, 0) + 1
    pairs = pd.DataFrame(
        [{"category_a": pair[0], "category_b": pair[1], "orders_together": count} for pair, count in pair_counts.items()]
    )
    if not pairs.empty:
        pairs = pairs.sort_values("orders_together", ascending=False).head(25)
    return category_performance, pairs


def add_css() -> None:
    st.markdown(
        """
        <style>
        :root {
            --navy: #132a35;
            --ink: #1b3039;
            --muted: #647780;
            --line: #dbe4e7;
            --canvas: #f5f7f8;
            --surface: #ffffff;
            --teal: #117a72;
            --coral: #c45849;
            --amber: #aa741e;
            --green: #247a52;
        }
        .stApp { background: var(--canvas); }
        .main .block-container { max-width: 1420px; padding: .55rem 1.6rem 2.5rem; }
        header[data-testid="stHeader"] { height: 0; background: transparent; }
        div[data-testid="stToolbar"] { visibility: hidden; height: 0; }
        div[data-testid="stDecoration"] { display: none; }

        /* Keep desktop navigation visible and readable. */
        section[data-testid="stSidebar"] {
            width: 268px !important;
            min-width: 268px !important;
            background: var(--navy);
            border-right: 1px solid #29434e;
        }
        section[data-testid="stSidebar"] > div { width: 268px !important; }
        section[data-testid="stSidebar"] [data-testid="stSidebarContent"] { padding: 1.1rem .8rem; }
        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3,
        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] label { color: #f5f8f9 !important; }
        section[data-testid="stSidebar"] .stCaptionContainer p { color: #b9c8ce !important; }
        section[data-testid="stSidebar"] div[data-baseweb="select"] * { color: #172a34 !important; }
        section[data-testid="stSidebar"] div[data-testid="stExpander"] {
            background: #f8fafb !important; border: 1px solid #9eb0b8 !important; overflow: hidden;
        }
        section[data-testid="stSidebar"] div[data-testid="stExpander"] summary,
        section[data-testid="stSidebar"] div[data-testid="stExpander"] summary * {
            color: #17313d !important; font-weight: 700 !important;
        }
        section[data-testid="stSidebar"] div[data-testid="stExpander"] label,
        section[data-testid="stSidebar"] div[data-testid="stExpander"] label p,
        section[data-testid="stSidebar"] div[data-testid="stExpander"] [data-testid="stWidgetLabel"] p {
            color: #405761 !important; opacity: 1 !important;
        }
        section[data-testid="stSidebar"] div[data-testid="stExpander"] input,
        section[data-testid="stSidebar"] div[data-testid="stExpander"] [data-baseweb="select"] > div {
            background: #ffffff !important; color: #172a34 !important;
        }
        section[data-testid="stSidebar"] div[data-testid="stButton"] button {
            width: 100%;
            min-height: 42px;
            justify-content: flex-start;
            border-radius: 5px;
            border: 1px solid transparent;
            padding: .55rem .7rem;
            font-weight: 600;
            transition: background .18s ease, border-color .18s ease, transform .18s ease;
        }
        section[data-testid="stSidebar"] div[data-testid="stButton"] button[kind="secondary"] {
            background: transparent;
            color: #dce7eb;
        }
        section[data-testid="stSidebar"] div[data-testid="stButton"] button[kind="secondary"]:hover {
            background: #203c48;
            border-color: #3b5965;
            transform: translateX(2px);
        }
        section[data-testid="stSidebar"] div[data-testid="stButton"] button[kind="primary"] {
            background: #e7f3f1;
            color: #105e59;
            border-color: #b7d8d3;
        }
        .brand-lockup {
            display: flex; align-items: center; gap: 12px; margin: 2px 3px 18px; padding: 13px 11px;
            border: 1px solid #34515d; border-radius: 6px; background: #193541; position: relative; overflow: hidden;
        }
        .brand-lockup::after { content: "PLATFORM"; position: absolute; right: 8px; top: 6px; color: #78939e; font-size: 8px; font-weight: 800; }
        .brand-mark {
            width: 43px; height: 43px; display: flex; align-items: flex-end; justify-content: center; gap: 3px;
            background: #e7f3f1; border-radius: 6px; padding: 9px 8px;
        }
        .brand-mark b { display: block; width: 4px; background: #117a72; border-radius: 1px; animation: brand-bars 1.6s ease-in-out infinite; }
        .brand-mark b:nth-child(1) { height: 9px; animation-delay: 0s; }
        .brand-mark b:nth-child(2) { height: 18px; animation-delay: .14s; }
        .brand-mark b:nth-child(3) { height: 13px; animation-delay: .28s; }
        .brand-mark b:nth-child(4) { height: 22px; animation-delay: .42s; }
        .brand-copy strong { color: #fff; display: block; font-size: 15px; line-height: 1.15; }
        .brand-copy span { color: #afc2c9; display: block; font-size: 10px; margin-top: 4px; }
        .nav-label { color: #8fa6af; font-size: 10px; font-weight: 700; margin: 4px 5px 7px; letter-spacing: 0; }
        .sidebar-foot { border-top: 1px solid #2b4652; margin-top: 12px; padding: 13px 5px 0; }
        .sidebar-foot p { font-size: 11px; color: #9db0b8 !important; margin: 0 0 5px; }

        .page-head {
            min-height: 124px; display: flex; align-items: center; justify-content: space-between;
            gap: 20px; padding: 18px 20px 20px; margin: 0 0 13px;
            background: #173641; border-left: 5px solid #20a096; border-bottom: 1px solid #294c57;
            position: relative; overflow: hidden; animation: slide-in .32s ease-out both;
        }
        .page-title-block { position: relative; z-index: 2; }
        .page-head .eyebrow { color: #60c8be; font-size: 10px; font-weight: 800; margin: 0 0 6px; }
        .page-head h1 { color: #f7fbfc; font-size: 29px; line-height: 1.15; margin: 0 0 6px; letter-spacing: 0; }
        .page-head p { color: #bdd0d6; font-size: 13px; margin: 0; }
        .head-aside { display: flex; align-items: center; gap: 18px; position: relative; z-index: 2; }
        .status-row { display: flex; gap: 6px; flex-wrap: wrap; justify-content: flex-end; }
        .status {
            color: #dce8eb; background: #204752; border: 1px solid #3b626d; border-radius: 4px;
            padding: 5px 8px; font-size: 11px; white-space: nowrap;
        }
        .status i {
            display: inline-block; width: 7px; height: 7px; background: var(--green);
            border-radius: 50%; margin-right: 6px; animation: pulse 1.8s infinite;
        }
        .signal-bars { height: 45px; display: flex; align-items: flex-end; gap: 4px; padding: 0 4px; }
        .signal-bars b { width: 5px; background: #45b5aa; border-radius: 1px; animation: signal 1.45s ease-in-out infinite; }
        .signal-bars b:nth-child(1) { height: 14px; animation-delay: 0s; }
        .signal-bars b:nth-child(2) { height: 29px; animation-delay: .12s; }
        .signal-bars b:nth-child(3) { height: 20px; animation-delay: .24s; }
        .signal-bars b:nth-child(4) { height: 38px; animation-delay: .36s; }
        .signal-bars b:nth-child(5) { height: 24px; animation-delay: .48s; }
        .flow-line { position: absolute; left: 0; right: 0; bottom: 0; height: 3px; background: #234955; overflow: hidden; }
        .flow-line span { display: block; width: 24%; height: 100%; background: #31a99e; animation: data-flow 2.4s ease-in-out infinite; }
        .page-guide {
            display: flex; align-items: center; gap: 14px; margin: -5px 0 14px;
            padding: 8px 10px; background: #edf5f4; border-left: 3px solid var(--teal);
            color: #4e626b; font-size: 11px;
        }
        .page-guide strong { color: var(--ink); white-space: nowrap; }
        .page-guide ul { display: flex; flex-wrap: wrap; gap: 8px 22px; margin: 0; padding-left: 18px; }
        .section-title { margin: 2px 0 10px; }
        .section-title h2 { color: var(--ink); font-size: 17px; margin: 0 0 2px; letter-spacing: 0; }
        .section-title p { color: var(--muted); font-size: 12px; margin: 0; }
        .insight-strip {
            display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; margin: 10px 0 14px;
        }
        .insight {
            background: #fff; border-left: 3px solid var(--teal); padding: 9px 11px;
            color: #52666f; font-size: 12px; min-height: 50px;
        }
        .insight strong { display: block; color: var(--ink); font-size: 13px; margin-bottom: 2px; }
        .proxy-note { border-left: 3px solid var(--amber); background: #fff9ed; padding: 9px 11px; color: #6e5627; font-size: 12px; margin-bottom: 12px; }
        .recommendation-item {
            background: #fff; border: 1px solid var(--line); border-radius: 5px; padding: 12px;
            min-height: 92px; transition: transform .18s ease, box-shadow .18s ease;
        }
        .recommendation-item:hover { transform: translateY(-2px); box-shadow: 0 7px 18px rgba(24, 51, 62, .08); }
        .recommendation-item small { color: var(--teal); font-weight: 700; }
        .recommendation-item strong { display: block; color: var(--ink); font-size: 14px; margin: 5px 0 3px; }
        .recommendation-item p { color: var(--muted); font-size: 11px; margin: 0; }

        div[data-testid="stMetric"] {
            min-height: 92px; background: var(--surface); padding: 12px 14px;
            border: 1px solid var(--line); border-radius: 5px;
            transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease;
        }
        div[data-testid="stMetric"]:hover { transform: translateY(-2px); border-color: #a9c4c2; box-shadow: 0 7px 18px rgba(24, 51, 62, .07); }
        div[data-testid="stMetricLabel"] { color: var(--muted); font-size: 12px; }
        div[data-testid="stMetricValue"] { color: var(--ink); font-size: 23px; }
        div[data-testid="stMetric"] { animation: metric-in .38s ease-out both; }
        div[data-testid="stMetric"]:nth-of-type(2) { animation-delay: .04s; }
        div[data-testid="stMetric"]:nth-of-type(3) { animation-delay: .08s; }
        div[data-testid="stDataFrame"] { border: 1px solid var(--line); border-radius: 5px; }
        div[data-testid="stPlotlyChart"] { background: #fff; border: 1px solid var(--line); border-radius: 5px; }
        div[data-testid="stExpander"] { background: #fff; border-color: var(--line); border-radius: 5px; }
        div[data-testid="stForm"] { background: #fff; border: 1px solid var(--line); border-radius: 5px; padding: 14px; }
        button[kind="primaryFormSubmit"], .main button[kind="primary"] { background: var(--teal); border-color: var(--teal); }

        @keyframes slide-in { from { opacity: 0; transform: translateY(5px); } to { opacity: 1; transform: none; } }
        @keyframes metric-in { from { opacity: 0; transform: translateY(7px); } to { opacity: 1; transform: none; } }
        @keyframes signal { 0%, 100% { transform: scaleY(.55); opacity: .65; } 50% { transform: scaleY(1); opacity: 1; } }
        @keyframes brand-bars { 0%, 100% { transform: scaleY(.65); } 50% { transform: scaleY(1); } }
        @keyframes data-flow { 0% { transform: translateX(-110%); } 55%, 100% { transform: translateX(430%); } }
        @keyframes pulse { 0%, 100% { opacity: 1; box-shadow: 0 0 0 0 rgba(36,122,82,.35); } 50% { opacity: .75; box-shadow: 0 0 0 4px rgba(36,122,82,0); } }

        @media (min-width: 769px) {
            section[data-testid="stSidebar"][aria-expanded="false"] { transform: none !important; margin-left: 0 !important; }
            button[data-testid="stSidebarCollapseButton"] { display: none; }
        }
        @media (max-width: 768px) {
            .main .block-container { padding: 1rem; }
            .page-head { align-items: flex-start; flex-direction: column; }
            .page-head h1 { font-size: 24px; }
            .head-aside { width: 100%; justify-content: space-between; }
            .status-row { justify-content: flex-start; }
            .page-guide { align-items: flex-start; flex-direction: column; gap: 5px; }
            .page-guide ul { display: block; }
            .insight-strip { grid-template-columns: 1fr; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def apply_dark_theme(enabled: bool) -> None:
    if not enabled:
        return
    st.markdown(
        """
        <style>
        :root {
            --ink: #eff5f6;
            --muted: #a9bbc2;
            --line: #34505c;
            --canvas: #10212a;
            --surface: #172d37;
        }
        .stApp { background: var(--canvas); color: #e6eef1; }
        .page-head, .page-head h1, .section-title h2 { color: var(--ink); }
        .status, .insight, .recommendation-item,
        div[data-testid="stMetric"], div[data-testid="stPlotlyChart"],
        div[data-testid="stExpander"], div[data-testid="stForm"] { background: var(--surface); }
        .status, .insight, .recommendation-item p, .page-guide { color: #b7c7cd; }
        .page-guide { background: #17343a; }
        .proxy-note { background: #3a3020; color: #e4ca92; }
        div[data-testid="stMetricValue"], .recommendation-item strong { color: #f5f8f9; }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.fragment(run_every=1)
def live_system_status() -> None:
    st.caption(f"System online | {datetime.now().strftime('%d %b %Y, %I:%M:%S %p')}")


add_css()

customer_features = load_csv("customer_360_features.csv", ("first_purchase_date", "last_purchase_date"))
require_release_data(customer_features)

if "active_page" not in st.session_state:
    st.session_state.active_page = "Executive Overview"

with st.sidebar:
    st.markdown(
        '<div class="brand-lockup"><div class="brand-mark"><b></b><b></b><b></b><b></b></div><div class="brand-copy"><strong>CustomerAtlas AI</strong><span>Customer 360 Intelligence</span></div></div>',
        unsafe_allow_html=True,
    )
    st.markdown('<p class="nav-label">WORKSPACE</p>', unsafe_allow_html=True)
    for label, icon in NAV_ITEMS:
        if st.button(
            label,
            key=f"nav_{label}",
            icon=icon,
            type="primary" if st.session_state.active_page == label else "secondary",
            width="stretch",
        ):
            st.session_state.active_page = label
            st.rerun()

    segment_values = sorted(customer_features["rfm_segment"].dropna().astype(str).unique())
    state_values = sorted(customer_features.get("state", pd.Series(dtype=str)).dropna().astype(str).unique())
    with st.expander("Filters", expanded=False, icon=":material/filter_alt:"):
        selected_segment = st.selectbox("RFM segment", ["All", *segment_values])
        selected_state = st.selectbox("State", ["All", *state_values])
        category_values = sorted(customer_features.get("favorite_category", pd.Series(dtype=str)).dropna().astype(str).unique())
        selected_category = st.selectbox("Favorite category", ["All", *category_values])
        min_date = customer_features["last_purchase_date"].min().date()
        max_date = customer_features["last_purchase_date"].max().date()
        selected_dates = st.date_input("Last purchase window", value=(min_date, max_date), min_value=min_date, max_value=max_date)

    st.toggle("Dark mode", key="dark_mode")
    live_system_status()

    st.markdown(
        f'<div class="sidebar-foot"><p>{len(customer_features):,} customer profiles</p><p>Currency: BRL</p><p>Updated from notebook outputs</p></div>',
        unsafe_allow_html=True,
    )

page = st.session_state.active_page
apply_dark_theme(st.session_state.dark_mode)

# Large extracts are loaded only for pages that use them. This keeps the
# executive dashboard responsive without removing any analytical detail.
segment_summary = pd.DataFrame()
sentiment = pd.DataFrame()
recommendations = pd.DataFrame()
feature_importance = pd.DataFrame()
model_evaluation = pd.DataFrame()
fact_orders = pd.DataFrame()
fact_campaign = pd.DataFrame()
dim_campaign = pd.DataFrame()
product_reviews = pd.DataFrame()
dim_product = pd.DataFrame()

if page == "Customer Explorer":
    fact_orders = load_csv("fact_orders.csv", ("purchase_date",))
    recommendations = load_csv("recommendations.csv")
elif page == "Segments":
    segment_summary = load_csv("segment_summary.csv")
elif page == "Predictions":
    feature_importance = load_csv("model_feature_importance.csv")
    model_evaluation = load_csv("model_evaluation.csv")
elif page == "Experience":
    sentiment = load_csv("product_sentiment.csv")
    product_reviews = load_csv("fact_product_reviews.csv", ("review_date",))
    fact_campaign = load_csv("fact_campaign.csv")
    dim_campaign = load_csv("dim_campaign.csv")
elif page == "Recommendations":
    recommendations = load_csv("recommendations.csv")
    fact_orders = load_csv("fact_orders.csv", ("purchase_date",))
    dim_product = load_csv("dim_product.csv")
    sentiment = load_csv("product_sentiment.csv")
elif page == "Data & SQL":
    segment_summary = load_csv("segment_summary.csv")
    sentiment = load_csv("product_sentiment.csv")
    recommendations = load_csv("recommendations.csv")
    model_evaluation = load_csv("model_evaluation.csv")
    fact_orders = load_csv("fact_orders.csv", ("purchase_date",))

if not product_reviews.empty:
    product_reviews["review_date"] = pd.to_datetime(product_reviews["review_date"], errors="coerce", format="mixed")

filtered = customer_features.copy()
if selected_segment != "All":
    filtered = filtered.loc[filtered["rfm_segment"].astype(str).eq(selected_segment)]
if selected_state != "All" and "state" in filtered.columns:
    filtered = filtered.loc[filtered["state"].astype(str).eq(selected_state)]
if selected_category != "All":
    filtered = filtered.loc[filtered["favorite_category"].astype(str).eq(selected_category)]
if isinstance(selected_dates, (tuple, list)) and len(selected_dates) == 2:
    start_date, end_date = pd.Timestamp(selected_dates[0]), pd.Timestamp(selected_dates[1])
    filtered = filtered.loc[filtered["last_purchase_date"].between(start_date, end_date)]

page_header(page)
if filtered.empty:
    st.warning("No customers match these filters. Open Filters in the sidebar and broaden the selection.")
    st.stop()


if page == "Executive Overview":
    total_customers = filtered["customer_id"].nunique()
    total_revenue = filtered["total_spend"].sum()
    total_orders = filtered["total_orders"].sum()
    repeat_rate = filtered["total_orders"].gt(1).mean()
    avg_churn = filtered["churn_probability"].mean()
    avg_clv = filtered["predicted_clv"].mean()
    avg_rating = filtered.get("avg_review_score", pd.Series(dtype=float)).mean()

    animated_kpis([
        {"label": "Total customers", "value": total_customers, "format": "integer", "note": "Canonical customer profiles"},
        {"label": "Revenue", "value": total_revenue, "format": "currency", "note": "Merchandise value"},
        {"label": "Orders", "value": total_orders, "format": "integer", "note": "Distinct customer orders"},
        {"label": "Average CLV", "value": avg_clv, "format": "currency", "note": "12-month proxy"},
        {"label": "Churn propensity", "value": 100 * avg_churn, "format": "percent", "note": "Calibrated portfolio proxy"},
        {"label": "Average rating", "value": avg_rating, "format": "rating", "note": "Olist customer feedback"},
    ])

    top_segment = filtered.groupby("rfm_segment", observed=False)["total_spend"].sum().idxmax()
    top_state = filtered.groupby("state")["total_spend"].sum().idxmax()
    high_risk_count = filtered["churn_probability"].ge(0.65).sum()
    st.markdown(
        f"""
        <div class="insight-strip">
          <div class="insight"><strong>{top_segment}</strong>Largest revenue-contributing segment</div>
          <div class="insight"><strong>{top_state}</strong>Highest-revenue state in this view</div>
          <div class="insight"><strong>{high_risk_count:,} customers</strong>High proxy risk; repeat rate is {repeat_rate:.1%}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns(2)
    with left:
        revenue_by_segment = filtered.groupby("rfm_segment", as_index=False, observed=False)["total_spend"].sum()
        figure = px.bar(
            revenue_by_segment.sort_values("total_spend"),
            x="total_spend", y="rfm_segment", orientation="h", color="rfm_segment",
            title="Revenue by segment", color_discrete_sequence=px.colors.qualitative.Safe,
        )
        figure.update_xaxes(title="Revenue (BRL)")
        figure.update_yaxes(title=None)
        chart(figure, 300)
        st.download_button(
            "Download segment revenue", revenue_by_segment.to_csv(index=False).encode("utf-8"),
            "revenue_by_segment.csv", "text/csv", icon=":material/download:", key="download_overview_segments",
        )
    with right:
        state_revenue = filtered.groupby("state", as_index=False)["total_spend"].sum().nlargest(10, "total_spend")
        figure = px.bar(
            state_revenue, x="state", y="total_spend", title="Top states",
            color="total_spend", color_continuous_scale="Tealgrn",
        )
        figure.update_yaxes(title="Revenue (BRL)")
        figure.update_xaxes(title=None)
        figure.update_layout(coloraxis_showscale=False)
        chart(figure, 300)
        st.download_button(
            "Download state revenue", state_revenue.to_csv(index=False).encode("utf-8"),
            "revenue_by_state.csv", "text/csv", icon=":material/download:", key="download_overview_states",
        )

    with st.expander("Explore customer value and recency", icon=":material/scatter_plot:"):
        sample = filtered.sample(min(len(filtered), 2_500), random_state=42)
        figure = px.scatter(
            sample, x="recency_days", y="total_spend", color="rfm_segment", size="total_orders",
            hover_data=["customer_id", "state", "predicted_clv", "churn_probability"],
            title="Customer value versus recency", color_discrete_sequence=px.colors.qualitative.Safe,
        )
        chart(figure, 320)

    st.download_button(
        "Download filtered customers", filtered.to_csv(index=False).encode("utf-8"),
        "customer_360_filtered.csv", "text/csv", icon=":material/download:",
    )

elif page == "Customer Explorer":
    customer_ids = sorted(filtered["customer_id"].dropna().astype(str).unique())
    selected_customer = st.selectbox("Find customer", customer_ids, placeholder="Select a customer ID")
    profile = filtered.loc[filtered["customer_id"].astype(str).eq(selected_customer)].iloc[0]

    metrics = st.columns(5)
    metrics[0].metric("Total spend", format_brl(profile["total_spend"]))
    metrics[1].metric("Orders", f"{profile['total_orders']:,.0f}")
    metrics[2].metric("Average order", format_brl(profile["avg_order_value"]))
    metrics[3].metric("CLV proxy", format_brl(profile["predicted_clv"]))
    metrics[4].metric("Churn proxy", format_pct(profile["churn_probability"]))

    profile_tab, journey_tab, history_tab, offers_tab = st.tabs(["Profile", "Journey & engagement", "Timeline", "Recommended offers"])
    with profile_tab:
        left, right = st.columns([1.45, 0.55])
        summary_fields = {
            "Customer ID": profile.get("customer_id", ""),
            "Location": f"{profile.get('city', '')}, {profile.get('state', '')}",
            "Favorite category": profile.get("favorite_category", ""),
            "RFM segment": profile.get("rfm_segment", ""),
            "Behavior cluster": profile.get("cluster_segment", ""),
            "Days since purchase": profile.get("recency_days", ""),
            "Unique products": profile.get("number_of_products", ""),
            "Review sentiment": "Positive" if float(profile.get("avg_review_score", 0)) >= 4 else "Neutral" if float(profile.get("avg_review_score", 0)) >= 3 else "Negative",
        }
        left.dataframe(
            pd.DataFrame({"Attribute": summary_fields.keys(), "Value": [str(value) for value in summary_fields.values()]}),
            width="stretch", hide_index=True, height=315,
        )
        churn_value = float(profile["churn_probability"])
        color = "#c45849" if churn_value >= 0.65 else "#aa741e" if churn_value >= 0.35 else "#247a52"
        gauge = go.Figure(go.Indicator(
            mode="gauge+number", value=100 * churn_value, number={"suffix": "%"},
            title={"text": "Churn propensity"},
            gauge={"axis": {"range": [0, 100]}, "bar": {"color": color}, "bgcolor": "#edf1f2"},
        ))
        gauge.update_layout(height=230, margin=dict(l=15, r=15, t=45, b=5))
        right.plotly_chart(gauge, width="stretch", config=PLOT_CONFIG)
        right.info(retention_action(churn_value, str(profile["rfm_segment"])))

    with journey_tab:
        journey_metrics = st.columns(5)
        journey_metrics[0].metric("Web sessions", f"{profile.get('sessions', 0):,.0f}")
        journey_metrics[1].metric("Page views", f"{profile.get('views', 0):,.0f}")
        journey_metrics[2].metric("Cart additions", f"{profile.get('cart_additions', 0):,.0f}")
        journey_metrics[3].metric("Campaign clicks", f"{profile.get('campaign_clicks', 0):,.0f}")
        journey_metrics[4].metric("Campaign conversions", f"{profile.get('campaign_conversions', 0):,.0f}")
        journey_details = pd.DataFrame([
            {"Area": "Website", "Signal": "Engagement score", "Value": profile.get("web_engagement_score", 0)},
            {"Area": "Marketing", "Signal": "Conversion rate", "Value": format_pct(profile.get("campaign_conversion_rate", 0))},
            {"Area": "Feedback", "Signal": "Average rating", "Value": f"{profile.get('avg_review_score', 0):.1f} / 5"},
            {"Area": "Support", "Signal": "Ticket history", "Value": "Not available in source data"},
        ])
        journey_details["Value"] = journey_details["Value"].astype(str)
        st.dataframe(journey_details, width="stretch", hide_index=True, height=180)

    with history_tab:
        history = fact_orders.loc[fact_orders["customer_id"].astype(str).eq(selected_customer)].copy()
        columns = ["purchase_date", "order_id", "order_status", "item_price", "freight_value"]
        st.dataframe(history.sort_values("purchase_date", ascending=False)[columns].head(50), width="stretch", hide_index=True, height=315)

    with offers_tab:
        customer_recs = recommendations.loc[recommendations["customer_id"].astype(str).eq(selected_customer)].sort_values("rank")
        if customer_recs.empty:
            st.info("No recommendation is available for this customer.")
        else:
            columns = st.columns(min(len(customer_recs), 5))
            for column, (_, rec) in zip(columns, customer_recs.head(5).iterrows()):
                column.markdown(
                    f'<div class="recommendation-item"><small>CHOICE {int(rec["rank"])}</small><strong>{rec["recommended_category"]}</strong><p>{rec["reason"]}</p></div>',
                    unsafe_allow_html=True,
                )

    export_columns = st.columns([0.22, 0.22, 0.56])
    export_columns[0].download_button(
        "Download CSV", pd.DataFrame([profile]).to_csv(index=False).encode("utf-8"),
        f"customer_{selected_customer}.csv", "text/csv", icon=":material/download:", width="stretch",
    )
    export_columns[1].download_button(
        "Download PDF", build_profile_pdf(profile), f"customer_{selected_customer}.pdf",
        "application/pdf", icon=":material/picture_as_pdf:", width="stretch",
    )

elif page == "Segments":
    segment_counts = filtered["rfm_segment"].value_counts().rename_axis("segment").reset_index(name="customers")
    cluster_value = filtered.groupby("cluster_segment", as_index=False)["total_spend"].sum()

    left, right = st.columns(2)
    with left:
        figure = px.pie(
            segment_counts, names="segment", values="customers", hole=0.52,
            title="RFM audience mix", color_discrete_sequence=px.colors.qualitative.Safe,
        )
        chart(figure, 330, legend="bottom")
    with right:
        figure = px.bar(
            cluster_value.sort_values("total_spend"), x="total_spend", y="cluster_segment",
            orientation="h", title="Revenue by behavior cluster", color="cluster_segment",
            color_discrete_sequence=px.colors.qualitative.Bold,
        )
        figure.update_yaxes(title=None)
        figure.update_xaxes(title="Revenue (BRL)")
        chart(figure, 330, legend="hidden")

    segment_downloads = st.columns(2)
    segment_downloads[0].download_button(
        "Download RFM distribution", segment_counts.to_csv(index=False).encode("utf-8"),
        "rfm_distribution.csv", "text/csv", icon=":material/download:", width="stretch",
    )
    segment_downloads[1].download_button(
        "Download cluster revenue", cluster_value.to_csv(index=False).encode("utf-8"),
        "cluster_revenue.csv", "text/csv", icon=":material/download:", width="stretch",
    )

    section_intro("Segment action table", "Use this short view to choose loyalty, growth, or win-back actions.")
    summary = segment_summary.copy()
    if not summary.empty:
        summary["avg_churn_probability"] = summary["avg_churn_probability"].map(format_pct)
        summary["revenue"] = summary["revenue"].map(format_brl)
        summary["avg_clv"] = summary["avg_clv"].map(format_brl)
        st.dataframe(summary, width="stretch", hide_index=True, height=265)

    with st.expander("Open detailed segment map", icon=":material/bubble_chart:"):
        sample = filtered.sample(min(len(filtered), 3_000), random_state=42)
        figure = px.scatter(
            sample, x="frequency", y="monetary", color="rfm_segment", size="recency_days",
            hover_data=["customer_id", "cluster_segment"], title="Frequency and value map",
            color_discrete_sequence=px.colors.qualitative.Safe,
        )
        chart(figure, 320)

elif page == "Predictions":
    st.markdown(
        '<div class="proxy-note"><strong>Portfolio note:</strong> Olist has no observed churn or CLV label. These calibrated proxy models demonstrate the workflow and must be replaced before production use.</div>',
        unsafe_allow_html=True,
    )
    churn_tab, clv_tab = st.tabs(["Churn propensity", "Customer value"])

    with churn_tab:
        churn_model = load_model("churn_model.pkl")
        left, right = st.columns([0.52, 0.48])
        with left:
            with st.form("churn_form"):
                first = st.columns(3)
                recency = first[0].number_input("Days inactive", min_value=0, value=120)
                frequency = first[1].number_input("Orders", min_value=1, value=2)
                products = first[2].number_input("Products", min_value=1, value=2)
                second = st.columns(3)
                monetary = second[0].number_input("Revenue (BRL)", min_value=0.0, value=250.0)
                aov = second[1].number_input("Avg order (BRL)", min_value=0.0, value=125.0)
                age = second[2].number_input("Purchase span", min_value=1, value=30)
                submitted = st.form_submit_button("Estimate churn propensity", icon=":material/query_stats:")
            if churn_model is None:
                st.info("Run Notebook 05 to create the churn model.")
            elif submitted:
                probability = float(churn_model.predict_proba(model_input_frame(recency, frequency, monetary, aov, products, age))[0, 1])
                band = "High" if probability >= 0.65 else "Medium" if probability >= 0.35 else "Low"
                result_cols = st.columns(2)
                result_cols[0].metric("Churn propensity", format_pct(probability))
                result_cols[1].metric("Risk band", band)
                st.info(retention_action(probability))
                gauge_color = "#c45849" if band == "High" else "#aa741e" if band == "Medium" else "#247a52"
                gauge = go.Figure(go.Indicator(
                    mode="gauge+number", value=100 * probability, number={"suffix": "%"},
                    gauge={
                        "axis": {"range": [0, 100]}, "bar": {"color": gauge_color},
                        "steps": [
                            {"range": [0, 35], "color": "#dceee6"},
                            {"range": [35, 65], "color": "#f3ead5"},
                            {"range": [65, 100], "color": "#f2deda"},
                        ],
                    },
                ))
                chart(gauge, 225)
                st.toast("Churn estimate is ready", icon=":material/check_circle:")
        with right:
            if not feature_importance.empty:
                importance = feature_importance.sort_values("churn_importance")
                figure = px.bar(
                    importance, x="churn_importance", y="feature", orientation="h",
                    title="What drives the proxy", color="churn_importance", color_continuous_scale="OrRd",
                )
                figure.update_layout(coloraxis_showscale=False)
                chart(figure, 300)

    with clv_tab:
        clv_model = load_model("clv_model.pkl")
        left, right = st.columns([0.48, 0.52])
        with left:
            with st.form("clv_form"):
                first = st.columns(2)
                recency = first[0].number_input("Days inactive", min_value=0, value=60, key="clv_recency")
                frequency = first[1].number_input("Orders", min_value=1, value=3, key="clv_frequency")
                second = st.columns(2)
                monetary = second[0].number_input("Revenue (BRL)", min_value=0.0, value=400.0, key="clv_monetary")
                aov = second[1].number_input("Avg order (BRL)", min_value=0.0, value=133.33, key="clv_aov")
                third = st.columns(2)
                products = third[0].number_input("Products", min_value=1, value=3, key="clv_products")
                age = third[1].number_input("Purchase span", min_value=1, value=120, key="clv_age")
                submitted = st.form_submit_button("Estimate forward value", icon=":material/paid:")
            if clv_model is None:
                st.info("Run Notebook 05 to create the CLV model.")
            elif submitted:
                input_frame = model_input_frame(recency, frequency, monetary, aov, products, age)
                value = max(float(clv_model.predict(input_frame)[0]), 0)
                if hasattr(clv_model, "estimators_"):
                    tree_values = np.array([tree.predict(input_frame.to_numpy())[0] for tree in clv_model.estimators_])
                    interval_low, interval_high = np.percentile(tree_values, [10, 90])
                else:
                    interval_low, interval_high = value * 0.85, value * 1.15
                q25, q50, q75 = filtered["predicted_clv"].quantile([0.25, 0.50, 0.75])
                value_band = "Platinum" if value >= q75 else "Gold" if value >= q50 else "Silver" if value >= q25 else "Bronze"
                result_cols = st.columns(3)
                result_cols[0].metric("12-month CLV proxy", format_brl(value))
                result_cols[1].metric("Value band", value_band)
                result_cols[2].metric("Planning range", f"{format_brl(interval_low)} - {format_brl(interval_high)}")
                recommendation = "Prioritize loyalty recognition and premium cross-sell." if value_band in {"Platinum", "Gold"} else "Build purchase frequency with a relevant next-best-category offer."
                st.info(recommendation)
                st.toast("Customer value estimate is ready", icon=":material/check_circle:")
        with right:
            figure = px.histogram(
                filtered, x="predicted_clv", nbins=36, title="Customer value distribution",
                color_discrete_sequence=["#117a72"],
            )
            figure.update_xaxes(title="12-month CLV proxy (BRL)")
            figure.update_yaxes(title="Customers")
            chart(figure, 300)

    section_intro("Model evaluation", "Held-out results from Notebook 05; proxy targets are not production outcomes.")
    if model_evaluation.empty:
        st.info("Run Notebook 05 to generate the model comparison table.")
    else:
        display_columns = [
            column for column in ["task", "model", "selected", "accuracy", "precision", "recall", "f1", "roc_auc", "mae", "r2"]
            if column in model_evaluation.columns
        ]
        st.dataframe(model_evaluation[display_columns], width="stretch", hide_index=True, height=245)
        st.download_button(
            "Download model evaluation",
            model_evaluation.to_csv(index=False).encode("utf-8"),
            "model_evaluation.csv",
            "text/csv",
            icon=":material/download:",
        )

elif page == "Experience":
    sentiment_tab, marketing_tab = st.tabs(["Review intelligence", "Campaign performance"])

    with sentiment_tab:
        if sentiment.empty:
            st.info("Run Notebook 05 to create sentiment outputs.")
        else:
            left, right = st.columns([0.42, 0.58])
            with left:
                section_intro("Test a review", "Use the saved TF-IDF model for a quick text classification.")
                review_text = st.text_area("Review text", placeholder="The delivery was fast and the product works well...", height=100)
                if st.button("Analyze sentiment", icon=":material/sentiment_satisfied:") and review_text.strip():
                    model = load_model("sentiment_model.pkl")
                    if model is None:
                        st.info("Run Notebook 05 to create the sentiment model.")
                    else:
                        label = model.predict([review_text])[0]
                        confidence = model.predict_proba([review_text])[0].max()
                        st.metric("Result", label, f"{confidence:.1%} confidence")
            with right:
                mix = sentiment.groupby("sentiment_label", as_index=False)["review_count"].sum()
                figure = px.pie(
                    mix, names="sentiment_label", values="review_count", hole=0.52,
                    title="Review-weighted sentiment", color="sentiment_label",
                    color_discrete_map={"Positive": "#247a52", "Neutral": "#aa741e", "Negative": "#c45849"},
                )
                chart(figure, 285)
            with st.expander("View category sentiment table"):
                st.dataframe(sentiment.sort_values("review_count", ascending=False), width="stretch", hide_index=True, height=280)

            if not product_reviews.empty:
                with st.expander("Sentiment trend and review explorer", icon=":material/trending_up:"):
                    trend_data = product_reviews.dropna(subset=["review_date"]).copy()
                    trend_data["month"] = trend_data["review_date"].dt.to_period("M").astype(str)
                    trend = trend_data.groupby(["month", "sentiment_label"], as_index=False).size()
                    figure = px.line(
                        trend, x="month", y="size", color="sentiment_label", markers=True,
                        title="Review sentiment over time",
                        color_discrete_map={"Positive": "#247a52", "Neutral": "#aa741e", "Negative": "#c45849"},
                    )
                    figure.update_yaxes(title="Reviews")
                    chart(figure, 270)

                    filter_columns = st.columns(2)
                    review_sentiment = filter_columns[0].selectbox("Sentiment", ["All", "Positive", "Neutral", "Negative"], key="review_sentiment")
                    review_categories = sorted(product_reviews["category_name"].dropna().astype(str).unique())
                    review_category = filter_columns[1].selectbox("Category", ["All", *review_categories], key="review_category")
                    review_sample = product_reviews.copy()
                    if review_sentiment != "All":
                        review_sample = review_sample.loc[review_sample["sentiment_label"].eq(review_sentiment)]
                    if review_category != "All":
                        review_sample = review_sample.loc[review_sample["category_name"].eq(review_category)]
                    st.dataframe(
                        review_sample[["review_date", "category_name", "rating", "sentiment_label", "review_text"]].head(100),
                        width="stretch", hide_index=True, height=260,
                    )

                with st.expander("Complaints, praise, and word cloud", icon=":material/cloud:"):
                    complaint_col, praise_col = st.columns(2)
                    complaint_col.markdown("**Common complaint phrases**")
                    complaint_col.dataframe(extract_review_terms("Negative"), width="stretch", hide_index=True, height=245)
                    praise_col.markdown("**Common praised phrases**")
                    praise_col.dataframe(extract_review_terms("Positive"), width="stretch", hide_index=True, height=245)

                    if st.button("Generate word cloud", icon=":material/auto_awesome:"):
                        from wordcloud import WordCloud
                        import matplotlib.pyplot as plt

                        with st.spinner("Building the review cloud..."):
                            cloud_text = " ".join(product_reviews["review_text"].dropna().astype(str).sample(
                                min(5_000, product_reviews["review_text"].notna().sum()), random_state=42
                            ))
                            word_cloud = WordCloud(width=1200, height=300, background_color="white", colormap="viridis").generate(cloud_text)
                            figure, axis = plt.subplots(figsize=(12, 3))
                            axis.imshow(word_cloud, interpolation="bilinear")
                            axis.axis("off")
                            st.pyplot(figure, width="stretch")
                            plt.close(figure)
                        st.toast("Word cloud generated", icon=":material/check_circle:")

    with marketing_tab:
        st.markdown('<div class="proxy-note">Campaign records are synthetic demonstration data, not observed Olist performance.</div>', unsafe_allow_html=True)
        if fact_campaign.empty or dim_campaign.empty:
            st.info("Run Notebook 02 to create campaign outputs.")
        else:
            campaign = (
                fact_campaign.groupby("campaign_id", as_index=False)
                .agg(sent=("email_sent", "sum"), opened=("opened", "sum"), clicked=("clicked", "sum"), converted=("converted", "sum"), revenue=("revenue_generated", "sum"))
                .merge(dim_campaign[["campaign_id", "campaign_type", "campaign_cost"]], on="campaign_id", how="left")
            )
            campaign["open_rate"] = campaign["opened"] / campaign["sent"].replace(0, np.nan)
            campaign["ctr"] = campaign["clicked"] / campaign["sent"].replace(0, np.nan)
            campaign["roi"] = (campaign["revenue"] - campaign["campaign_cost"]) / campaign["campaign_cost"]
            totals = campaign[["sent", "opened", "clicked", "converted"]].sum()
            funnel = pd.DataFrame({"stage": ["Sent", "Opened", "Clicked", "Converted"], "customers": totals.values})
            left, right = st.columns(2)
            with left:
                chart(px.funnel(funnel, x="customers", y="stage", title="Response funnel", color_discrete_sequence=["#117a72"]), 285)
            with right:
                chart(px.bar(campaign.sort_values("roi"), x="roi", y="campaign_type", orientation="h", title="Campaign ROI", color="roi", color_continuous_scale="RdYlGn"), 285)
            with st.expander("View campaign details"):
                st.dataframe(campaign.sort_values("roi", ascending=False), width="stretch", hide_index=True, height=270)

elif page == "Recommendations":
    offer_tab, product_tab = st.tabs(["Next best offer", "Product intelligence"])
    with offer_tab:
        if recommendations.empty:
            st.info("Run Notebook 05 to create recommendations.")
        else:
            recommendation_customer = st.selectbox(
                "Find customer", sorted(recommendations["customer_id"].dropna().astype(str).unique()),
                key="recommendation_customer",
            )
            result = recommendations.loc[recommendations["customer_id"].astype(str).eq(recommendation_customer)].sort_values("rank")
            section_intro("Recommended categories", "Each choice includes a simple reason a client can understand.")
            columns = st.columns(min(len(result), 5))
            for column, (_, rec) in zip(columns, result.head(5).iterrows()):
                column.markdown(
                    f'<div class="recommendation-item"><small>RANK {int(rec["rank"])}</small><strong>{rec["recommended_category"]}</strong><p>{rec["reason"]}</p></div>',
                    unsafe_allow_html=True,
                )
            method_mix = recommendations["method"].value_counts().rename_axis("method").reset_index(name="recommendations")
            with st.expander("How recommendations were created", icon=":material/info:"):
                st.write("Basket associations are used when available. Popular categories not yet purchased provide the fallback.")
                chart(px.bar(method_mix, x="method", y="recommendations", title="Method coverage", color="method", color_discrete_sequence=["#117a72", "#c45849"]), 250)

    with product_tab:
        if fact_orders.empty or dim_product.empty:
            st.info("Run Notebook 02 to create product intelligence outputs.")
        else:
            category_performance, product_pairs = product_intelligence_tables()
            left, right = st.columns(2)
            with left:
                top_categories = category_performance.head(12).sort_values("revenue")
                figure = px.bar(
                    top_categories, x="revenue", y="category_name_english", orientation="h",
                    title="Top categories by revenue", color="revenue", color_continuous_scale="Tealgrn",
                )
                figure.update_layout(coloraxis_showscale=False)
                figure.update_yaxes(title=None)
                chart(figure, 300)
            with right:
                low_rated = sentiment.loc[sentiment["review_count"].ge(20)].nsmallest(12, "avg_rating").sort_values("avg_rating", ascending=False)
                figure = px.bar(
                    low_rated, x="avg_rating", y="category_name", orientation="h",
                    title="Lowest-rated external categories", color="avg_rating", color_continuous_scale="RdYlGn",
                )
                figure.update_layout(coloraxis_showscale=False)
                figure.update_yaxes(title=None)
                chart(figure, 300)
            details_left, details_right = st.columns(2)
            details_left.markdown("**Frequently bought together**")
            details_left.dataframe(product_pairs.head(15), width="stretch", hide_index=True, height=280)
            details_right.markdown("**Category performance**")
            details_right.dataframe(category_performance.head(30), width="stretch", hide_index=True, height=280)

elif page == "Data & SQL":
    source_rows = [
        {"Source": "Olist", "Purpose": "Customers and transactions", "Rule": "Canonical customer source"},
        {"Source": "Cosmetics clickstream", "Purpose": "Behavior demonstration", "Rule": "Simulated identity mapping"},
        {"Source": "Datafiniti reviews", "Purpose": "Product sentiment", "Rule": "No Olist customer join"},
        {"Source": "Synthetic campaigns", "Purpose": "Marketing demonstration", "Rule": "Not observed performance"},
    ]
    st.dataframe(pd.DataFrame(source_rows), width="stretch", hide_index=True, height=180)

    left, right = st.columns(2)
    with left:
        section_intro("Data status", "Core artifacts required by the application.")
        artifact_status = pd.DataFrame([
            {"Artifact": "Customer profiles", "Rows": len(customer_features), "Status": "Ready"},
            {"Artifact": "Recommendations", "Rows": len(recommendations), "Status": "Ready" if not recommendations.empty else "Missing"},
            {"Artifact": "Sentiment summary", "Rows": len(sentiment), "Status": "Ready" if not sentiment.empty else "Missing"},
            {"Artifact": "Transactions", "Rows": len(fact_orders), "Status": "Ready" if not fact_orders.empty else "Missing"},
            {"Artifact": "Model evaluation", "Rows": len(model_evaluation), "Status": "Ready" if not model_evaluation.empty else "Missing"},
        ])
        st.dataframe(artifact_status, width="stretch", hide_index=True, height=205)
    with right:
        section_intro("Important limitations", "Use these notes when presenting the project.")
        st.info("Churn and CLV are calibrated portfolio proxies. Clickstream identities and campaign events are simulated. External reviews are never linked to Olist customers.")

    section_intro("Analytics console", "Choose a predefined business analysis and download the result.")
    query_controls = st.columns([0.55, 0.20, 0.25])
    analysis_name = query_controls[0].selectbox(
        "Business analysis",
        ["Revenue by state", "Top customer segments", "High-risk customers", "Highest-CLV customers"],
        label_visibility="collapsed",
    )
    if query_controls[1].button("Run analysis", icon=":material/play_arrow:", width="stretch"):
        st.toast(f"{analysis_name} is ready", icon=":material/check_circle:")
    analysis_result = predefined_analysis(analysis_name)
    query_controls[2].download_button(
        "Download result", analysis_result.to_csv(index=False).encode("utf-8"),
        f"{analysis_name.lower().replace(' ', '_')}.csv", "text/csv",
        icon=":material/download:", width="stretch",
    )
    table_controls = st.columns([0.5, 0.25, 0.25])
    table_search = table_controls[0].text_input("Search results", placeholder="Search any visible value...")
    page_size = table_controls[1].selectbox("Rows per page", [10, 25, 50, 100], index=1)
    searched_result = analysis_result.copy()
    if table_search:
        search_mask = searched_result.astype(str).apply(
            lambda column: column.str.contains(table_search, case=False, na=False)
        ).any(axis=1)
        searched_result = searched_result.loc[search_mask]
    total_pages = max(1, int(np.ceil(len(searched_result) / page_size)))
    page_number = table_controls[2].number_input("Page", min_value=1, max_value=total_pages, value=1)
    page_start = (page_number - 1) * page_size
    st.dataframe(
        searched_result.iloc[page_start:page_start + page_size],
        width="stretch", hide_index=True, height=275,
    )
    st.caption(f"Showing page {page_number} of {total_pages} | {len(searched_result):,} matching rows | Click a column header to sort")

    section_intro("Reports", "Export the most useful app-ready datasets.")
    report_columns = st.columns(3)
    report_columns[0].download_button(
        "Filtered customers", filtered.to_csv(index=False).encode("utf-8"),
        "filtered_customers.csv", "text/csv", icon=":material/download:", width="stretch",
    )
    report_columns[1].download_button(
        "Model predictions", customer_features[["customer_id", "churn_probability", "predicted_clv", "churn_risk_band", "clv_band"]].to_csv(index=False).encode("utf-8"),
        "model_predictions.csv", "text/csv", icon=":material/download:", width="stretch",
    )
    report_columns[2].download_button(
        "Recommendations", recommendations.to_csv(index=False).encode("utf-8"),
        "recommendations.csv", "text/csv", icon=":material/download:", width="stretch",
    )

    query_path = ROOT / "sql" / "business_queries.sql"
    with st.expander("Open SQL business-query library", icon=":material/code:"):
        if query_path.exists():
            sql_text = query_path.read_text(encoding="utf-8")
            st.code(sql_text, language="sql")
            st.download_button("Download SQL", sql_text.encode("utf-8"), "business_queries.sql", "text/sql", icon=":material/download:")
        else:
            st.error("sql/business_queries.sql was not found.")
