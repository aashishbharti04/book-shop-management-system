"""Data access for :class:`~bookshop.data.models.sale.Sale`."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..models import Book, Sale, SaleItem


class SaleRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get(self, sale_id: int) -> Sale | None:
        return self.session.get(Sale, sale_id)

    def add(self, sale: Sale) -> Sale:
        self.session.add(sale)
        self.session.flush()
        return sale

    def recent(self, limit: int = 10) -> list[Sale]:
        stmt = select(Sale).order_by(Sale.created_at.desc()).limit(limit)
        return list(self.session.execute(stmt).scalars().all())

    def revenue_between(self, start: datetime, end: datetime) -> int:
        """Total revenue (cents) for sales in the half-open range [start, end)."""

        stmt = select(func.coalesce(func.sum(Sale.total_cents), 0)).where(
            Sale.created_at >= start, Sale.created_at < end
        )
        return int(self.session.execute(stmt).scalar_one())

    def units_sold_between(self, start: datetime, end: datetime) -> int:
        stmt = (
            select(func.coalesce(func.sum(SaleItem.quantity), 0))
            .select_from(SaleItem)
            .join(Sale, Sale.id == SaleItem.sale_id)
            .where(Sale.created_at >= start, Sale.created_at < end)
        )
        return int(self.session.execute(stmt).scalar_one())

    def book_sales_between(self, start: datetime, end: datetime) -> list[tuple[int, str, int, int]]:
        """Per-book (id, title, units, revenue_cents) for the half-open range.

        This is the correct, period-scoped aggregation that the legacy
        ``view_sales`` got wrong (it summed a cumulative lifetime counter).
        """

        stmt = (
            select(
                Book.id,
                Book.title,
                func.sum(SaleItem.quantity),
                func.sum(SaleItem.line_total_cents),
            )
            .select_from(SaleItem)
            .join(Sale, Sale.id == SaleItem.sale_id)
            .join(Book, Book.id == SaleItem.book_id)
            .where(Sale.created_at >= start, Sale.created_at < end)
            .group_by(Book.id, Book.title)
            .order_by(func.sum(SaleItem.quantity).desc(), Book.title.asc())
        )
        return [
            (int(bid), title, int(units), int(revenue))
            for bid, title, units, revenue in self.session.execute(stmt).all()
        ]
