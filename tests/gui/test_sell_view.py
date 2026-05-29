from __future__ import annotations

import pytest

from bookshop.presentation.views.sell_view import SellView


@pytest.fixture
def stocked_context(app_context):
    app_context.services.inventory.add_book(title="Alpha", price_cents=1000, initial_qty=5)
    app_context.services.inventory.add_book(title="Beta", price_cents=250, initial_qty=3)
    return app_context


@pytest.mark.gui
def test_add_to_cart_updates_total(stocked_context):
    view = SellView(stocked_context)
    view.on_show()
    books = stocked_context.services.inventory.list_books()
    alpha = next(b for b in books if b.title == "Alpha")

    view._add_book(alpha)
    assert alpha.id in view._rows
    assert view.complete_button.isEnabled()
    assert "10.00" in view.total_label.text()

    # Adding the same book again increments quantity, not a new row.
    view._add_book(alpha)
    assert len(view._rows) == 1
    assert view._rows[alpha.id].quantity() == 2
    assert "20.00" in view.total_label.text()


@pytest.mark.gui
def test_complete_sale_decrements_stock_and_clears_cart(stocked_context):
    view = SellView(stocked_context)
    view.on_show()
    books = stocked_context.services.inventory.list_books()
    alpha = next(b for b in books if b.title == "Alpha")

    view._add_book(alpha)
    view._rows[alpha.id].spin.setValue(2)
    view._show_receipt = lambda sale: None  # avoid opening the modal dialog in tests
    view._complete()  # SyncTaskRunner runs inline

    # Cart cleared after completion.
    assert view._rows == {}
    assert not view.complete_button.isEnabled()
    # Stock decremented from 5 to 3.
    refreshed = next(b for b in stocked_context.services.inventory.list_books() if b.title == "Alpha")
    assert refreshed.stock_qty == 3


@pytest.mark.gui
def test_out_of_stock_book_not_added(app_context):
    app_context.services.inventory.add_book(title="Empty", price_cents=500, initial_qty=0)
    view = SellView(app_context)
    view.on_show()
    empty_book = app_context.services.inventory.list_books()[0]
    view._add_book(empty_book)
    assert view._rows == {}
