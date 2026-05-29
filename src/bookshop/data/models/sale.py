"""Sale and SaleItem models.

A :class:`Sale` is the receipt header (customer, total, who/when); each
:class:`SaleItem` is a line. Capturing ``unit_price_cents`` on the line means a
later price change on a :class:`Book` never rewrites historical sales — the
legacy schema (a flat ``purchased`` table with no quantity or price) could not
do this.
"""

from __future__ import annotations

from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from ..base import Base, id_type, utcnow


class Sale(Base):
    __tablename__ = "sales"

    id = Column(id_type(), primary_key=True, autoincrement=True)
    customer_name = Column(String(255), nullable=True)
    customer_phone = Column(String(32), nullable=True)
    total_cents = Column(Integer, nullable=False, default=0)
    sold_by_user_id = Column(id_type(), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, nullable=False, default=utcnow, index=True)

    items = relationship(
        "SaleItem",
        back_populates="sale",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    sold_by = relationship("User", lazy="joined")

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"<Sale id={self.id} total_cents={self.total_cents} items={len(self.items)}>"


class SaleItem(Base):
    __tablename__ = "sale_items"
    __table_args__ = (CheckConstraint("quantity > 0", name="quantity_positive"),)

    id = Column(id_type(), primary_key=True, autoincrement=True)
    sale_id = Column(id_type(), ForeignKey("sales.id"), nullable=False, index=True)
    book_id = Column(id_type(), ForeignKey("books.id"), nullable=False, index=True)
    quantity = Column(Integer, nullable=False)
    unit_price_cents = Column(Integer, nullable=False)
    line_total_cents = Column(Integer, nullable=False)

    sale = relationship("Sale", back_populates="items")
    book = relationship("Book", lazy="joined")

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"<SaleItem book_id={self.book_id} qty={self.quantity}>"
