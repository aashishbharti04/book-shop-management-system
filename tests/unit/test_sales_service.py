from __future__ import annotations

import pytest
from sqlalchemy import func, select

from bookshop.core.exceptions import OutOfStockError, ValidationError
from bookshop.data.models import Sale, SaleItem
from bookshop.services.dto import CartLine


def _add(services, title, price_cents, qty):
    return services.inventory.add_book(title=title, price_cents=price_cents, initial_qty=qty)


def _sale_count(database) -> int:
    with database.session_scope() as session:
        return int(session.execute(select(func.count(Sale.id))).scalar_one())


def test_create_sale_decrements_stock_and_totals(services):
    a = _add(services, "Alpha", 1000, 10)
    b = _add(services, "Beta", 250, 5)

    sale = services.sales.create_sale(
        [CartLine(a.id, 3), CartLine(b.id, 2)],
        customer_name="Grace Hopper",
        customer_phone="555-0199",
    )

    assert sale.total_cents == 3 * 1000 + 2 * 250
    assert sale.item_count == 5
    assert services.inventory.get_book(a.id).stock_qty == 7
    assert services.inventory.get_book(b.id).stock_qty == 3


def test_oversell_raises_and_rolls_back(services, database):
    book = _add(services, "Scarce", 500, 2)
    with pytest.raises(OutOfStockError):
        services.sales.create_sale([CartLine(book.id, 5)])

    # Stock unchanged and NO sale/sale_item rows were written.
    assert services.inventory.get_book(book.id).stock_qty == 2
    assert _sale_count(database) == 0
    with database.session_scope() as session:
        assert int(session.execute(select(func.count(SaleItem.id))).scalar_one()) == 0


def test_multiline_partial_failure_rolls_back_everything(services, database):
    ok = _add(services, "Plenty", 1000, 10)
    scarce = _add(services, "Scarce", 1000, 1)

    with pytest.raises(OutOfStockError):
        services.sales.create_sale([CartLine(ok.id, 2), CartLine(scarce.id, 5)])

    # The first line must NOT have been decremented; whole transaction rolled back.
    assert services.inventory.get_book(ok.id).stock_qty == 10
    assert services.inventory.get_book(scarce.id).stock_qty == 1
    assert _sale_count(database) == 0


def test_unit_price_captured_at_sale_time(services):
    book = _add(services, "Priced", 1000, 10)
    services.sales.create_sale([CartLine(book.id, 1)])

    # Change the price AFTER the sale; the historical line must not change.
    services.inventory.update_book(book.id, price_cents=9999)

    sale = services.sales.recent_sales(limit=1)[0]
    assert sale.items[0].unit_price_cents == 1000
    assert sale.total_cents == 1000


def test_duplicate_lines_are_consolidated(services):
    book = _add(services, "Same", 100, 10)
    sale = services.sales.create_sale([CartLine(book.id, 2), CartLine(book.id, 3)])
    assert services.inventory.get_book(book.id).stock_qty == 5
    assert len(sale.items) == 1
    assert sale.items[0].quantity == 5


def test_empty_cart_rejected(services):
    with pytest.raises(ValidationError):
        services.sales.create_sale([])


def test_nonpositive_quantity_rejected(services):
    book = _add(services, "X", 100, 10)
    with pytest.raises(ValidationError):
        services.sales.create_sale([CartLine(book.id, 0)])
