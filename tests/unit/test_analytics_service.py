from __future__ import annotations

from datetime import datetime

import pytest

from bookshop.data.models import Sale
from bookshop.services.analytics_service import month_bounds
from bookshop.services.dto import CartLine


def _add(services, title, price_cents, qty):
    return services.inventory.add_book(title=title, price_cents=price_cents, initial_qty=qty)


def _set_sale_date(database, sale_id: int, when: datetime) -> None:
    with database.session_scope() as session:
        session.get(Sale, sale_id).created_at = when


def test_month_bounds_half_open():
    start, end = month_bounds(2026, 1)
    assert start == datetime(2026, 1, 1)
    assert end == datetime(2026, 2, 1)
    # December rolls over to next year.
    start, end = month_bounds(2026, 12)
    assert end == datetime(2027, 1, 1)
    with pytest.raises(ValueError):
        month_bounds(2026, 13)


def test_monthly_sales_are_period_scoped(services, database):
    """Regression for the legacy analytics that summed cumulative totals."""

    book = _add(services, "Seasonal", 1000, 100)

    jan = services.sales.create_sale([CartLine(book.id, 3)])
    feb = services.sales.create_sale([CartLine(book.id, 5)])
    _set_sale_date(database, jan.id, datetime(2026, 1, 10))
    _set_sale_date(database, feb.id, datetime(2026, 2, 10))

    jan_sales = services.analytics.monthly_sales(2026, 1)
    assert len(jan_sales) == 1
    assert jan_sales[0].quantity == 3
    assert jan_sales[0].revenue_cents == 3000

    feb_sales = services.analytics.monthly_sales(2026, 2)
    assert feb_sales[0].quantity == 5

    # A month with no sales is empty (not a cumulative carry-over).
    assert services.analytics.monthly_sales(2026, 3) == []


def test_month_boundary_is_exclusive_at_end(services, database):
    book = _add(services, "Edge", 1000, 100)
    s = services.sales.create_sale([CartLine(book.id, 1)])
    # Exactly the first instant of the *next* month must NOT count for January.
    _set_sale_date(database, s.id, datetime(2026, 2, 1, 0, 0, 0))
    assert services.analytics.monthly_sales(2026, 1) == []
    assert services.analytics.monthly_sales(2026, 2)[0].quantity == 1


def test_dashboard_summary(services, database):
    a = _add(services, "Stocked", 1000, 50)
    _add(services, "Low", 500, 2)  # below default threshold of 5
    _add(services, "OutOfStock", 500, 0)  # not counted as low stock

    sale = services.sales.create_sale([CartLine(a.id, 4)])
    _set_sale_date(database, sale.id, datetime(2026, 5, 29, 10, 0, 0))

    summary = services.analytics.dashboard_summary(now=datetime(2026, 5, 29, 12, 0, 0))
    assert summary.total_titles == 3
    assert summary.total_stock_units == 50 + 2 + 0 - 4  # one sold 4 of "Stocked"
    assert summary.low_stock_count == 1
    assert summary.today_revenue_cents == 4000
    assert summary.today_units_sold == 4
    assert summary.month_revenue_cents == 4000
