"""Transaction Repository for customer order history and revenue analysis."""

from typing import List, Optional
from sqlalchemy import desc
from sqlalchemy.orm import Session

from database.models import Transaction
from database.repositories.base_repository import BaseRepository


class TransactionRepository(BaseRepository[Transaction]):
    """Data access repository for order transactions."""

    def __init__(self, session: Session):
        super().__init__(Transaction, session)

    def get_by_customer(self, customer_id: str, limit: int = 50) -> List[Transaction]:
        """Fetch all completed order transactions for a given customer."""
        return (
            self.session.query(Transaction)
            .filter(Transaction.customer_id == customer_id)
            .order_by(desc(Transaction.purchase_date))
            .limit(limit)
            .all()
        )
