"""Analytics: dashboard KPIs and correct, period-scoped sales aggregation."""

from __future__ import annotations

from datetime import datetime, timedelta

from ..core.clock import utcnow
from ..core.config import get_settings
from ..data.repositories import BookRepository, SaleRepository
from .base import BaseService
from .dto import BookSalesDTO, DashboardDTO


def month_bounds(year: int, month: int) -> tuple[datetime, datetime]:
    """Return the half-open ``[start, end)`` datetime range for a month.

    Using a half-open range avoids the off-by-one/last-day arithmetic the legacy
    code attempted with its ``last_month`` helper.
    """

    if not 1 <= month <= 12:
        raise ValueError("month must be between 1 and 12")
    start = datetime(year, month, 1)
    end = datetime(year + 1, 1, 1) if month == 12 else datetime(year, month + 1, 1)
    return start, end


def _day_bounds(moment: datetime) -> tuple[datetime, datetime]:
    start = datetime(moment.year, moment.month, moment.day)
    return start, start + timedelta(days=1)


class AnalyticsService(BaseService):
    def monthly_sales(self, year: int, month: int) -> list[BookSalesDTO]:
        start, end = month_bounds(year, month)
        return self._book_sales(start, end)

    def sales_for_period(self, start: datetime, end: datetime) -> list[BookSalesDTO]:
        return self._book_sales(start, end)

    def _book_sales(self, start: datetime, end: datetime) -> list[BookSalesDTO]:
        with self._unit_of_work() as session:
            rows = SaleRepository(session).book_sales_between(start, end)
            return [
                BookSalesDTO(book_id=bid, title=title, quantity=units, revenue_cents=revenue)
                for bid, title, units, revenue in rows
            ]

    def revenue_for_period(self, start: datetime, end: datetime) -> int:
        with self._unit_of_work() as session:
            return SaleRepository(session).revenue_between(start, end)

    def top_books(self, limit: int, start: datetime, end: datetime) -> list[BookSalesDTO]:
        return self._book_sales(start, end)[:limit]

    def dashboard_summary(self, *, now: datetime | None = None) -> DashboardDTO:
        now = now or utcnow()
        threshold = get_settings().low_stock_threshold
        today_start, today_end = _day_bounds(now)
        month_start, month_end = month_bounds(now.year, now.month)

        with self._unit_of_work() as session:
            book_repo = BookRepository(session)
            sale_repo = SaleRepository(session)
            return DashboardDTO(
                total_titles=book_repo.count(),
                total_stock_units=book_repo.total_stock_units(),
                # Scalar COUNT query — does not hydrate every low-stock row.
                low_stock_count=book_repo.count_low_stock(threshold),
                today_revenue_cents=sale_repo.revenue_between(today_start, today_end),
                today_units_sold=sale_repo.units_sold_between(today_start, today_end),
                month_revenue_cents=sale_repo.revenue_between(month_start, month_end),
            )
