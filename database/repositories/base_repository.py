"""Generic Base Repository providing standardized CRUD operations."""

from typing import Any, Generic, List, Optional, Type, TypeVar
from sqlalchemy.orm import Session

T = TypeVar("T")


class BaseRepository(Generic[T]):
    """Generic repository encapsulating common database interactions."""

    def __init__(self, model_cls: Type[T], session: Session):
        self.model_cls = model_cls
        self.session = session

    def get_by_id(self, entity_id: Any) -> Optional[T]:
        """Fetch single entity by its primary key using SQLAlchemy 2.0 pattern."""
        return self.session.get(self.model_cls, entity_id)

    def list_all(self, limit: int = 100, offset: int = 0) -> List[T]:
        """Retrieve paginated list of entities."""
        return self.session.query(self.model_cls).offset(offset).limit(limit).all()

    def count(self) -> int:
        """Count total entities."""
        return self.session.query(self.model_cls).count()

    def add(self, entity: T) -> T:
        """Add new entity to session."""
        self.session.add(entity)
        return entity

    def delete(self, entity: T) -> None:
        """Delete entity from session."""
        self.session.delete(entity)

    def commit(self) -> None:
        """Commit current transaction."""
        self.session.commit()
