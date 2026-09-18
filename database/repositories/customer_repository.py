"""Customer Repository for database-backed profile querying and filtering."""

from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy import func, desc, asc, or_
from sqlalchemy.orm import Session

from database.models import Customer, Transaction, Recommendation
from database.repositories.base_repository import BaseRepository


class CustomerRepository(BaseRepository[Customer]):
    """Data access repository for customer profiles and associated intelligence."""

    def __init__(self, session: Session):
        super().__init__(Customer, session)

    def get_by_customer_id(self, customer_id: str, org_id: str = "default_org") -> Optional[Customer]:
        """Fetch canonical customer profile by customer_id and org_id."""
        return (
            self.session.query(Customer)
            .filter(Customer.customer_id == customer_id, Customer.org_id == org_id)
            .first()
        )

    def search_and_filter(
        self,
        org_id: str = "default_org",
        search_query: Optional[str] = None,
        segment: Optional[str] = None,
        risk_level: Optional[str] = None,
        state: Optional[str] = None,
        clv_band: Optional[str] = None,
        sort_by: str = "total_spend",
        sort_desc: bool = True,
        limit: int = 25,
        offset: int = 0,
    ) -> Tuple[List[Customer], int]:
        """Execute parameterized multi-criteria customer queries with pagination."""
        query = self.session.query(Customer).filter(Customer.org_id == org_id)

        if search_query and search_query.strip():
            sq = f"%{search_query.strip()}%"
            query = query.filter(or_(Customer.customer_id.ilike(sq), Customer.city.ilike(sq)))

        if segment and segment != "All":
            query = query.filter(Customer.rfm_segment == segment)

        if risk_level and risk_level != "All":
            if "High" in risk_level:
                query = query.filter(Customer.churn_probability >= 0.65)
            elif "Medium" in risk_level:
                query = query.filter(Customer.churn_probability >= 0.35, Customer.churn_probability < 0.65)
            elif "Low" in risk_level:
                query = query.filter(Customer.churn_probability < 0.35)

        if state and state != "All":
            query = query.filter(Customer.state == state)

        if clv_band and clv_band != "All":
            query = query.filter(Customer.clv_band == clv_band)

        total_count = query.count()

        # Sorting
        sort_column = getattr(Customer, sort_by, Customer.total_spend)
        order_clause = desc(sort_column) if sort_desc else asc(sort_column)
        query = query.order_by(order_clause)

        results = query.offset(offset).limit(limit).all()
        return results, total_count

    def get_top_prioritized_customers(self, org_id: str = "default_org", limit: int = 50) -> List[Customer]:
        """Fetch top retention priority customers (high churn probability and high CLV)."""
        return (
            self.session.query(Customer)
            .filter(Customer.org_id == org_id, Customer.churn_probability >= 0.50)
            .order_by(desc(Customer.churn_probability * Customer.predicted_clv))
            .limit(limit)
            .all()
        )
