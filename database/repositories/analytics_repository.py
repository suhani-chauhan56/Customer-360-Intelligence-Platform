"""Analytics Repository for macro portfolio aggregates and segment metrics."""

from typing import Any, Dict, List
from sqlalchemy import func, desc
from sqlalchemy.orm import Session

from database.models import Customer, Transaction


class AnalyticsRepository:
    """Database aggregation queries for portfolio-level analytics."""

    def __init__(self, session: Session):
        self.session = session

    def get_portfolio_overview(self, org_id: str = "default_org") -> Dict[str, Any]:
        """Aggregate total customers, GMV, orders, and averages."""
        res = (
            self.session.query(
                func.count(Customer.customer_id).label("total_customers"),
                func.sum(Customer.total_spend).label("total_gmv"),
                func.sum(Customer.total_orders).label("total_orders"),
                func.avg(Customer.predicted_clv).label("avg_clv"),
                func.avg(Customer.churn_probability).label("avg_churn_prob"),
            )
            .filter(Customer.org_id == org_id)
            .first()
        )

        return {
            "total_customers": res.total_customers or 0,
            "total_gmv": float(res.total_gmv or 0.0),
            "total_orders": int(res.total_orders or 0),
            "avg_clv": float(res.avg_clv or 0.0),
            "avg_churn_prob": float(res.avg_churn_prob or 0.0),
        }

    def get_segment_aggregates(self, org_id: str = "default_org") -> List[Dict[str, Any]]:
        """Compute customer count and gross spend grouped by RFM segment."""
        results = (
            self.session.query(
                Customer.rfm_segment,
                func.count(Customer.customer_id).label("customers"),
                func.sum(Customer.total_spend).label("revenue"),
                func.avg(Customer.predicted_clv).label("avg_clv"),
                func.avg(Customer.churn_probability).label("avg_churn_probability"),
            )
            .filter(Customer.org_id == org_id)
            .group_by(Customer.rfm_segment)
            .order_by(desc("revenue"))
            .all()
        )

        return [
            {
                "rfm_segment": r.rfm_segment or "Unknown",
                "customers": r.customers,
                "revenue": float(r.revenue or 0.0),
                "avg_clv": float(r.avg_clv or 0.0),
                "avg_churn_probability": float(r.avg_churn_probability or 0.0),
            }
            for r in results
        ]
