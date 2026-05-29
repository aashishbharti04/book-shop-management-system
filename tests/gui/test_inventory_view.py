from __future__ import annotations

import pytest

from bookshop.presentation.views.inventory_view import InventoryView


@pytest.mark.gui
def test_empty_inventory_shows_empty_state(app_context):
    view = InventoryView(app_context)
    view.on_show()
    assert view.stack.currentWidget() is view.empty


@pytest.mark.gui
def test_inventory_lists_books(app_context):
    app_context.services.inventory.add_book(title="Test Book", price_cents=1000, initial_qty=3)
    view = InventoryView(app_context)
    view.on_show()
    assert view.table._model.rowCount() == 1
    assert view.stack.currentWidget() is view.table


@pytest.mark.gui
def test_add_book_through_viewmodel_reloads(app_context):
    view = InventoryView(app_context)
    view.on_show()
    view.vm.add_book(
        {
            "title": "Added Book",
            "author": None,
            "publisher": None,
            "isbn": None,
            "price_cents": 1500,
            "initial_qty": 5,
        }
    )
    assert view.table._model.rowCount() == 1
    assert view.stack.currentWidget() is view.table


@pytest.mark.gui
def test_edit_buttons_enable_on_selection(app_context):
    app_context.services.inventory.add_book(title="Selectable", price_cents=1000, initial_qty=1)
    view = InventoryView(app_context)
    view.on_show()
    assert not view.edit_button.isEnabled()
    view.table.view.selectRow(0)
    assert view.edit_button.isEnabled()
    assert view.restock_button.isEnabled()
