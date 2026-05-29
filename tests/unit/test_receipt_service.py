from __future__ import annotations

from datetime import datetime

from bookshop.services.dto import SaleDTO, SaleItemDTO
from bookshop.services.receipt_service import ReceiptService


def _sample_sale() -> SaleDTO:
    items = (
        SaleItemDTO(
            book_id=1, title="Clean Code", quantity=2, unit_price_cents=3899, line_total_cents=7798
        ),
        SaleItemDTO(
            book_id=2, title="Refactoring", quantity=1, unit_price_cents=5999, line_total_cents=5999
        ),
    )
    return SaleDTO(
        id=7,
        total_cents=13797,
        created_at=datetime(2026, 5, 29, 10, 30),
        items=items,
        customer_name="Ada Lovelace",
        customer_phone="555-0100",
        sold_by="demo",
    )


def test_render_html_contains_key_fields():
    html = ReceiptService("My Book Shop").render_html(_sample_sale())
    assert "My Book Shop" in html
    assert "Receipt #7" in html
    assert "Clean Code" in html
    assert "Refactoring" in html
    assert "Ada Lovelace" in html
    assert "$137.97" in html  # total, default $ symbol


def test_render_text_is_plain_and_complete():
    text = ReceiptService("My Book Shop").render_text(_sample_sale())
    assert "My Book Shop" in text
    assert "TOTAL" in text
    assert "Clean Code" in text


def test_render_html_escapes_user_content():
    items = (SaleItemDTO(1, "<script>alert(1)</script>", 1, 100, 100),)
    sale = SaleDTO(id=1, total_cents=100, created_at=datetime(2026, 1, 1), items=items)
    html = ReceiptService("Shop").render_html(sale)
    assert "<script>" not in html
    assert "&lt;script&gt;" in html
