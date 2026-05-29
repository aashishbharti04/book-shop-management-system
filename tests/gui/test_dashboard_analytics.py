from __future__ import annotations

import pytest

from bookshop.presentation.views.analytics_view import AnalyticsView
from bookshop.presentation.views.dashboard_view import DashboardView
from bookshop.services.dto import CartLine


@pytest.mark.gui
def test_dashboard_summary_and_recent(app_context):
    book = app_context.services.inventory.add_book(title="X", price_cents=1000, initial_qty=10)
    app_context.services.sales.create_sale([CartLine(book.id, 2)], customer_name="Ada")

    view = DashboardView(app_context)
    view.on_show()

    assert view.cards["titles"]._value.text() == "1"
    assert view.cards["today_units"]._value.text() == "2"
    assert "20.00" in view.cards["today_revenue"]._value.text()
    assert view.recent_table._model.rowCount() == 1
    assert view.recent_stack.currentWidget() is view.recent_table


@pytest.mark.gui
def test_dashboard_empty_recent(app_context):
    view = DashboardView(app_context)
    view.on_show()
    assert view.recent_stack.currentWidget() is view.recent_stack.empty


@pytest.mark.gui
def test_analytics_current_month_has_data(app_context):
    book = app_context.services.inventory.add_book(title="Seller", price_cents=500, initial_qty=10)
    app_context.services.sales.create_sale([CartLine(book.id, 3)])

    view = AnalyticsView(app_context)
    view.on_show()  # defaults to the current month/year

    assert view.table._model.rowCount() == 1
    assert view.stack.currentWidget() is not view.empty


@pytest.mark.gui
def test_analytics_empty_for_past_month(app_context):
    view = AnalyticsView(app_context)
    view.month_combo.setCurrentIndex(0)  # January
    view.year_spin.setValue(2000)
    view.on_show()
    assert view.stack.currentWidget() is view.empty
