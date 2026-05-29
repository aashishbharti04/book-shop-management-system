"""Book (inventory) model.

Replaces the legacy ``stock`` table. Money is stored as integer **cents**
(`price_cents`) to avoid floating-point rounding errors. A check constraint
guarantees stock can never go negative — the database itself backs up the
atomic decrement performed when selling.
"""

from __future__ import annotations

from sqlalchemy import CheckConstraint, Column, DateTime, Integer, String

from ..base import Base, id_type, utcnow


class Book(Base):
    __tablename__ = "books"
    __table_args__ = (
        CheckConstraint("stock_qty >= 0", name="stock_qty_non_negative"),
        CheckConstraint("price_cents >= 0", name="price_cents_non_negative"),
    )

    id = Column(id_type(), primary_key=True, autoincrement=True)
    isbn = Column(String(20), unique=True, nullable=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    author = Column(String(255), nullable=True)
    publisher = Column(String(255), nullable=True)
    price_cents = Column(Integer, nullable=False, default=0)
    stock_qty = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=utcnow)
    updated_at = Column(DateTime, nullable=False, default=utcnow, onupdate=utcnow)

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"<Book id={self.id} title={self.title!r} stock={self.stock_qty}>"
