"""Enterprise Data and Machine Learning Service for CustomerAtlas.

Provides cached access to processed warehouse facts, customer feature store,
dimensional tables, precomputed recommendations, and ML model inference artifacts.
Guarantees analytical fidelity, configuration-driven paths, and calculation consistency.
"""

from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import joblib
import pandas as pd
import streamlit as st

from config.settings import DATA_DIR, MODELS_DIR, SQL_DIR, CACHE_TTL_SECONDS
from utils.formatting import format_brl, format_pct
from utils.logging_config import logger


MODEL_COLUMNS = [
    "recency_days",
    "frequency",
    "monetary",
    "avg_order_value",
    "number_of_products",
    "customer_age_days",
]


@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner=False)
def load_csv(name: str, parse_dates: Tuple[str, ...] = ()) -> pd.DataFrame:
    """Load and cache CSV datasets from the processed data directory."""
    path = DATA_DIR / name
    if not path.exists():
        logger.warning(f"Dataset file not found at {path}")
        return pd.DataFrame()
    try:
        df = pd.read_csv(path, parse_dates=list(parse_dates))
        logger.info(f"Loaded dataset {name}: {len(df):,} rows, {len(df.columns)} cols")
        return df
    except Exception as e:
        logger.error(f"Error loading {name}: {e}", exc_info=True)
        st.warning(f"Error loading {name}: {e}")
        return pd.DataFrame()


@st.cache_resource(show_spinner=False)
def load_model(name: str) -> Optional[Any]:
    """Load and cache serialized machine learning models from the models directory."""
    path = MODELS_DIR / name
    if not path.exists():
        logger.warning(f"Model file not found at {path}")
        return None
    try:
        model = joblib.load(path)
        logger.info(f"Loaded ML model: {name}")
        return model
    except Exception as e:
        logger.error(f"Error loading model {name}: {e}", exc_info=True)
        return None


def model_input_frame(
    recency: float,
    frequency: float,
    monetary: float,
    avg_order_value: float,
    products: float,
    age: float,
) -> pd.DataFrame:
    """Construct an inference feature frame conforming to the XGBoost schema contract."""
    return pd.DataFrame(
        [[recency, frequency, monetary, avg_order_value, products, age]],
        columns=MODEL_COLUMNS,
    )


def retention_action(probability: float, segment: str = "") -> Dict[str, str]:
    """Derive automated retention playbook actions based on churn propensity and segment."""
    from config.business_rules import get_retention_playbook
    return get_retention_playbook(probability, segment)


def build_customer_pdf(profile: pd.Series) -> bytes:
    """Generate executive Customer 360 PDF dossier conforming to enterprise report standards."""
    try:
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
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4F46E5")),
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
            Paragraph("CustomerAtlas — Unified Customer 360 Dossier", title_style),
            Paragraph(f"Generated on {datetime.now().strftime('%B %d, %Y - %I:%M %p')} | Confidential Business Intelligence", sub_style),
            Spacer(1, 10),
            HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#4F46E5"), spaceAfter=14),
            table,
        ]

        doc.build(elements)
        return buffer.getvalue()
    except Exception as e:
        logger.error(f"Error generating PDF dossier: {e}", exc_info=True)
        return f"PDF generation error: {e}".encode("utf-8")
