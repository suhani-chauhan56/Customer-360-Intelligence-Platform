"""Customer Sentiment and CSAT Intelligence Service for CustomerAtlas.

Provides real-time and cached sentiment analytics derived from customer review
data, CSAT satisfaction ratings, longitudinal sentiment trends, segment breakdowns,
product category satisfaction, and empirical negative feedback theme extraction.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
import streamlit as st

from config.settings import DATA_DIR, RAW_DATA_DIR, CACHE_TTL_SECONDS
from utils.formatting import format_pct
from utils.logging_config import logger


@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner=False)
def load_sentiment_dataset() -> pd.DataFrame:
    """Load and process customer review data with sentiment polarity classification."""
    # Attempt to load raw reviews dataset
    raw_path = RAW_DATA_DIR / "olist_order_reviews_dataset.csv"
    if not raw_path.exists():
        raw_path = DATA_DIR.parent / "raw" / "olist_order_reviews_dataset.csv"

    if not raw_path.exists():
        logger.warning(f"Raw reviews dataset not found at {raw_path}")
        return pd.DataFrame()

    try:
        df = pd.read_csv(raw_path, parse_dates=["review_creation_date", "review_answer_timestamp"])
        
        # Ensure score is numeric
        df["review_score"] = pd.to_numeric(df["review_score"], errors="coerce").fillna(5.0).astype(int)
        
        # Sentiment categorization based on standard CSAT scale
        # Positive: 4-5 stars | Neutral: 3 stars | Negative: 1-2 stars
        conditions = [
            df["review_score"] >= 4,
            df["review_score"] == 3,
            df["review_score"] <= 2,
        ]
        choices = ["Positive", "Neutral", "Negative"]
        df["sentiment_category"] = np.select(conditions, choices, default="Neutral")
        
        # Sentiment score normalization (-1.0 to +1.0)
        # 5 -> +1.0, 4 -> +0.5, 3 -> 0.0, 2 -> -0.5, 1 -> -1.0
        score_map = {5: 1.0, 4: 0.5, 3: 0.0, 2: -0.5, 1: -1.0}
        df["sentiment_polarity"] = df["review_score"].map(score_map).fillna(0.0)
        
        # Extract month-year for time series
        df["review_month"] = df["review_creation_date"].dt.to_period("M").astype(str)
        
        logger.info(f"Loaded {len(df):,} review records for sentiment analysis.")
        return df
    except Exception as e:
        logger.error(f"Error processing sentiment reviews dataset: {e}", exc_info=True)
        return pd.DataFrame()


def compute_sentiment_overview(reviews_df: pd.DataFrame) -> Dict[str, Any]:
    """Calculate macro CSAT and sentiment distribution benchmarks."""
    if reviews_df is None or reviews_df.empty:
        return {
            "total_reviews": 0,
            "avg_review_score": 0.0,
            "positive_pct": 0.0,
            "neutral_pct": 0.0,
            "negative_pct": 0.0,
            "positive_count": 0,
            "neutral_count": 0,
            "negative_count": 0,
            "comments_count": 0,
            "comment_rate": 0.0,
        }

    total = len(reviews_df)
    score_counts = reviews_df["sentiment_category"].value_counts()
    pos_count = int(score_counts.get("Positive", 0))
    neu_count = int(score_counts.get("Neutral", 0))
    neg_count = int(score_counts.get("Negative", 0))

    has_comment = reviews_df["review_comment_message"].dropna().str.strip() != ""
    comments_count = int(has_comment.sum())

    return {
        "total_reviews": total,
        "avg_review_score": float(reviews_df["review_score"].mean()),
        "positive_pct": pos_count / max(1, total),
        "neutral_pct": neu_count / max(1, total),
        "negative_pct": neg_count / max(1, total),
        "positive_count": pos_count,
        "neutral_count": neu_count,
        "negative_count": neg_count,
        "comments_count": comments_count,
        "comment_rate": comments_count / max(1, total),
    }


def compute_sentiment_trend(reviews_df: pd.DataFrame) -> pd.DataFrame:
    """Compute monthly longitudinal CSAT and sentiment proportion trends."""
    if reviews_df is None or reviews_df.empty:
        return pd.DataFrame()

    valid_df = reviews_df[reviews_df["review_month"].str.match(r"^201[6-8]-\d{2}$")].copy()
    
    monthly = (
        valid_df.groupby("review_month")
        .agg(
            total_reviews=("review_score", "count"),
            avg_score=("review_score", "mean"),
            pos_reviews=("sentiment_category", lambda s: (s == "Positive").sum()),
            neg_reviews=("sentiment_category", lambda s: (s == "Negative").sum()),
            neu_reviews=("sentiment_category", lambda s: (s == "Neutral").sum()),
        )
        .reset_index()
        .sort_values("review_month")
    )

    monthly["positive_pct"] = monthly["pos_reviews"] / monthly["total_reviews"]
    monthly["negative_pct"] = monthly["neg_reviews"] / monthly["total_reviews"]
    monthly["neutral_pct"] = monthly["neu_reviews"] / monthly["total_reviews"]

    return monthly


def compute_sentiment_by_segment(
    customer_df: pd.DataFrame,
    reviews_df: pd.DataFrame,
    orders_df: pd.DataFrame,
) -> pd.DataFrame:
    """Aggregate customer satisfaction metrics across RFM segments."""
    if customer_df is None or customer_df.empty or "avg_review_score" not in customer_df.columns:
        return pd.DataFrame()

    seg_sent = (
        customer_df.groupby("rfm_segment", as_index=False)
        .agg(
            customers=("customer_id", "count"),
            avg_csat=("avg_review_score", "mean"),
            low_rating_customers=("low_rating_count", lambda s: (s > 0).sum() if s is not None else 0),
            total_spend=("total_spend", "sum"),
        )
    )

    seg_sent["low_rating_pct"] = seg_sent["low_rating_customers"] / seg_sent["customers"]
    return seg_sent.sort_values("avg_csat", ascending=False)


def extract_negative_themes(reviews_df: pd.DataFrame, top_n: int = 5) -> List[Dict[str, Any]]:
    """Extract factual negative root-cause themes from verified low-rating review text.

    Classifies real Portuguese review text into operational themes:
    - Delivery Delay / Atraso
    - Product Discrepancy / Diferente / Errado
    - Defect / Quality / Quebrado / Defeito
    - Missing Item / Faltou
    - Customer Service / Atendimento
    """
    if reviews_df is None or reviews_df.empty:
        return []

    neg_reviews = reviews_df[
        (reviews_df["review_score"] <= 2) & reviews_df["review_comment_message"].notna()
    ].copy()

    if neg_reviews.empty:
        return []

    texts = neg_reviews["review_comment_message"].astype(str).str.lower()

    # Rule-based theme keyword patterns derived from customer feedback
    themes_def = [
        {
            "theme": "Delivery Delay & Logistics Friction",
            "keywords": ["atraso", "atrasou", "demora", "demorou", "nao recebi", "não recebi", "prazo", "entrega", "esperando", "nunca chegou"],
            "description": "Shipment arrived past promised estimated delivery date or is currently delayed in transit.",
            "action": "Audit carrier performance, adjust delivery promise algorithms, and trigger proactive delay notifications.",
            "badge_color": "#DC2626",
            "icon": "🚚",
        },
        {
            "theme": "Product Quality & Physical Defect",
            "keywords": ["defeito", "quebrado", "danificado", "qualidade", "estragado", "pessimo", "péssimo", "ruim", "fraco", "material"],
            "description": "Received merchandise was broken, defective, or of lower manufacturing quality than expected.",
            "action": "Enforce vendor quality control standards and streamline automated replacement returns.",
            "badge_color": "#EA580C",
            "icon": "⚠️",
        },
        {
            "theme": "Product Discrepancy & Catalog Inaccuracy",
            "keywords": ["diferente", "errado", "foto", "veio errado", "outro produto", "tamanho", "cor errada", "modelo diferente"],
            "description": "Delivered item did not match catalog listing photos, size description, or specifications.",
            "action": "Audit marketplace seller listings, update product images, and verify SKU dimension specifications.",
            "badge_color": "#F59E0B",
            "icon": "📦",
        },
        {
            "theme": "Missing Items & Incomplete Shipments",
            "keywords": ["faltou", "incompleto", "veio faltando", "nao veio", "não veio", "metade", "falta", "peca faltando"],
            "description": "Customer received a multi-item package where one or more line items were omitted.",
            "action": "Improve warehouse pick-and-pack scanning verification and barcode audit checkpoints.",
            "badge_color": "#8B5CF6",
            "icon": "🔍",
        },
        {
            "theme": "Customer Support & Communication Responsiveness",
            "keywords": ["contato", "atendimento", "resposta", "nao responde", "não responde", "ninguem", "sac", "ignorado"],
            "description": "Customer experienced unresponsiveness when seeking assistance or order status updates.",
            "action": "Deploy omni-channel automated ticketing and establish an SLA of < 4 business hours for issue resolution.",
            "badge_color": "#0284C7",
            "icon": "💬",
        },
    ]

    total_with_comments = len(neg_reviews)
    results = []

    for t in themes_def:
        pattern = "|".join(t["keywords"])
        matches = texts.str.contains(pattern, regex=True, na=False)
        matched_count = int(matches.sum())
        matched_pct = matched_count / max(1, total_with_comments)

        sample_comments = neg_reviews[matches]["review_comment_message"].dropna().head(3).tolist()

        results.append({
            "theme": t["theme"],
            "matched_count": matched_count,
            "share_of_negative_comments": matched_pct,
            "description": t["description"],
            "action": t["action"],
            "badge_color": t["badge_color"],
            "icon": t["icon"],
            "sample_feedback": sample_comments,
        })

    # Sort by frequency
    results.sort(key=lambda x: x["matched_count"], reverse=True)
    return results[:top_n]


def compute_category_satisfaction(
    fact_orders: pd.DataFrame,
    reviews_df: pd.DataFrame,
    customer_df: pd.DataFrame,
) -> pd.DataFrame:
    """Calculate average customer satisfaction rating across primary product categories."""
    if customer_df is None or customer_df.empty or "favorite_category" not in customer_df.columns:
        return pd.DataFrame()

    cat_stats = (
        customer_df.groupby("favorite_category")
        .agg(
            customers=("customer_id", "count"),
            avg_review_score=("avg_review_score", "mean"),
            total_revenue=("total_spend", "sum"),
            avg_spend=("total_spend", "mean"),
        )
        .reset_index()
    )

    # Filter categories with meaningful sample size (>= 50 customers)
    cat_stats = cat_stats[cat_stats["customers"] >= 50].sort_values("avg_review_score", ascending=False)
    return cat_stats
