from __future__ import annotations

import pytest

from bookshop.core.exceptions import NotFoundError, ValidationError


def _add(services, title="A Book", price_cents=1000, qty=5, **kw):
    return services.inventory.add_book(title=title, price_cents=price_cents, initial_qty=qty, **kw)


def test_add_book_returns_dto(services):
    book = _add(services, title="Dune", price_cents=1599, qty=3, author="Frank Herbert")
    assert book.id is not None
    assert book.title == "Dune"
    assert book.price_cents == 1599
    assert book.stock_qty == 3
    assert book.in_stock is True


def test_add_book_validations(services):
    with pytest.raises(ValidationError):
        _add(services, title="   ")
    with pytest.raises(ValidationError):
        _add(services, price_cents=-1)
    with pytest.raises(ValidationError):
        _add(services, qty=-2)


def test_duplicate_isbn_rejected(services):
    _add(services, title="One", isbn="111")
    with pytest.raises(ValidationError):
        _add(services, title="Two", isbn="111")


def test_update_book_is_scoped_to_one_row(services):
    """Regression test for the legacy no-WHERE mass update bug."""

    a = _add(services, title="Alpha", price_cents=1000, qty=10)
    b = _add(services, title="Beta", price_cents=2000, qty=20)
    c = _add(services, title="Gamma", price_cents=3000, qty=30)

    services.inventory.update_book(b.id, price_cents=2500, title="Beta II")

    assert services.inventory.get_book(a.id).price_cents == 1000
    assert services.inventory.get_book(a.id).stock_qty == 10
    updated = services.inventory.get_book(b.id)
    assert updated.price_cents == 2500
    assert updated.title == "Beta II"
    assert services.inventory.get_book(c.id).price_cents == 3000


def test_update_missing_book_raises(services):
    with pytest.raises(NotFoundError):
        services.inventory.update_book(9999, price_cents=100)


def test_restock_only_target_and_rejects_nonpositive(services):
    a = _add(services, title="Alpha", qty=10)
    b = _add(services, title="Beta", qty=20)
    services.inventory.restock(a.id, 5)
    assert services.inventory.get_book(a.id).stock_qty == 15
    assert services.inventory.get_book(b.id).stock_qty == 20
    with pytest.raises(ValidationError):
        services.inventory.restock(a.id, 0)


def test_list_search_and_sort(services):
    _add(services, title="Python Crash Course", price_cents=3000)
    _add(services, title="Automate the Boring Stuff", price_cents=2000)
    _add(services, title="Learning SQL", price_cents=2500)

    found = services.inventory.list_books(search="python")
    assert [b.title for b in found] == ["Python Crash Course"]

    by_price_desc = services.inventory.list_books(sort_by="price", order="desc")
    prices = [b.price_cents for b in by_price_desc]
    assert prices == sorted(prices, reverse=True)
    assert services.inventory.count_books() == 3
