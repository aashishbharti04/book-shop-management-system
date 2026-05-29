from __future__ import annotations

from datetime import datetime

import pytest

from bookshop.services.dto import SaleDTO, SaleItemDTO
from bookshop.services.receipt_service import ReceiptService


@pytest.mark.gui
def test_export_pdf_writes_valid_file(qapp, tmp_path):
    items = (SaleItemDTO(1, "Clean Code", 2, 3899, 7798),)
    sale = SaleDTO(id=1, total_cents=7798, created_at=datetime(2026, 5, 29, 10, 30), items=items)

    out = tmp_path / "receipt.pdf"
    ReceiptService("Shop").export_pdf(sale, out)

    assert out.exists()
    data = out.read_bytes()
    assert len(data) > 0
    assert data[:4] == b"%PDF"  # valid PDF magic number
