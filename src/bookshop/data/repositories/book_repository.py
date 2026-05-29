"""Data access for :class:`~bookshop.data.models.book.Book`."""

from __future__ import annotations

from sqlalchemy import func, or_, select, update
from sqlalchemy.orm import Session

from ..models import Book

# Whitelisted sort columns (keys are the public API; values are ORM columns).
_SORT_COLUMNS = {
    "title": Book.title,
    "author": Book.author,
    "publisher": Book.publisher,
    "price": Book.price_cents,
    "stock": Book.stock_qty,
    "id": Book.id,
}


class BookRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get(self, book_id: int) -> Book | None:
        return self.session.get(Book, book_id)

    def get_by_isbn(self, isbn: str) -> Book | None:
        return self.session.execute(select(Book).where(Book.isbn == isbn)).scalar_one_or_none()

    def add(self, book: Book) -> Book:
        self.session.add(book)
        self.session.flush()
        return book

    def _base_query(self, search: str | None):
        stmt = select(Book)
        if search:
            like = f"%{search.strip()}%"
            stmt = stmt.where(
                or_(Book.title.ilike(like), Book.author.ilike(like), Book.isbn.ilike(like))
            )
        return stmt

    def list_all(
        self,
        *,
        search: str | None = None,
        sort_by: str = "title",
        order: str = "asc",
        limit: int | None = None,
        offset: int = 0,
    ) -> list[Book]:
        stmt = self._base_query(search)
        column = _SORT_COLUMNS.get(sort_by, Book.title)
        stmt = stmt.order_by(column.desc() if order == "desc" else column.asc())
        if limit is not None:
            stmt = stmt.limit(limit).offset(offset)
        return list(self.session.execute(stmt).scalars().all())

    def count(self, search: str | None = None) -> int:
        stmt = self._base_query(search).with_only_columns(func.count(Book.id)).order_by(None)
        return int(self.session.execute(stmt).scalar_one())

    def low_stock(self, threshold: int) -> list[Book]:
        stmt = (
            select(Book)
            .where(Book.stock_qty > 0, Book.stock_qty <= threshold)
            .order_by(Book.stock_qty.asc())
        )
        return list(self.session.execute(stmt).scalars().all())

    def count_low_stock(self, threshold: int) -> int:
        """Count low-stock books with a scalar query (no row hydration)."""

        stmt = select(func.count(Book.id)).where(
            Book.stock_qty > 0, Book.stock_qty <= threshold
        )
        return int(self.session.execute(stmt).scalar_one())

    def total_stock_units(self) -> int:
        stmt = select(func.coalesce(func.sum(Book.stock_qty), 0))
        return int(self.session.execute(stmt).scalar_one())

    def decrement_stock(self, book_id: int, quantity: int) -> int:
        """Atomically decrement stock, guarded so it can never go negative.

        Returns the number of rows affected: ``1`` on success, ``0`` if there
        was insufficient stock (the row is left untouched).
        """

        stmt = (
            update(Book)
            .where(Book.id == book_id, Book.stock_qty >= quantity)
            .values(stock_qty=Book.stock_qty - quantity)
            .execution_options(synchronize_session=False)
        )
        return self.session.execute(stmt).rowcount
