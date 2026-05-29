"""Receipt rendering and cross-platform output.

The legacy code wrote a temp file and called the Windows-only
``startfile(path, 'print')``. Here we render the receipt as HTML/plain text
(pure, easily testable) and use Qt's portable printing for on-paper output and
PDF export. Qt is imported lazily so this module can be used (and unit-tested)
without a display.
"""

from __future__ import annotations

import html
from pathlib import Path

from ..core.config import get_settings
from .dto import SaleDTO


class ReceiptService:
    def __init__(self, shop_name: str | None = None) -> None:
        self.shop_name = shop_name or get_settings().app_name

    # -- Pure rendering ------------------------------------------------------

    def render_text(self, sale: SaleDTO) -> str:
        lines = [
            self.shop_name.center(40),
            "=" * 40,
            f"Receipt #{sale.id}",
            f"Date : {sale.created_at:%Y-%m-%d %H:%M}",
        ]
        # Truncate to keep the fixed-width plain-text receipt aligned even if a
        # very long customer name/phone was entered.
        if sale.customer_name:
            lines.append(f"Customer : {sale.customer_name[:30]}")
        if sale.customer_phone:
            lines.append(f"Phone : {sale.customer_phone[:30]}")
        if sale.sold_by:
            lines.append(f"Served by : {sale.sold_by[:30]}")
        lines.append("-" * 40)
        for item in sale.items:
            lines.append(f"{item.title[:24]:<24} {item.quantity:>2} x {item.unit_price_display}")
            lines.append(f"{'':<30}{item.line_total_display:>10}")
        lines.append("-" * 40)
        lines.append(f"{'TOTAL':<24}{sale.total_display:>16}")
        lines.append("=" * 40)
        lines.append("Thank you for your purchase!".center(40))
        return "\n".join(lines)

    def render_html(self, sale: SaleDTO) -> str:
        rows = "".join(
            f"<tr>"
            f"<td>{html.escape(item.title)}</td>"
            f"<td class='num'>{item.quantity}</td>"
            f"<td class='num'>{html.escape(item.unit_price_display)}</td>"
            f"<td class='num'>{html.escape(item.line_total_display)}</td>"
            f"</tr>"
            for item in sale.items
        )
        meta_bits = [f"<p><strong>Receipt #{sale.id}</strong> &middot; {sale.created_at:%Y-%m-%d %H:%M}</p>"]
        if sale.customer_name:
            meta_bits.append(f"<p>Customer: {html.escape(sale.customer_name)}</p>")
        if sale.customer_phone:
            meta_bits.append(f"<p>Phone: {html.escape(sale.customer_phone)}</p>")
        if sale.sold_by:
            meta_bits.append(f"<p>Served by: {html.escape(sale.sold_by)}</p>")
        meta = "".join(meta_bits)
        return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
  body {{ font-family: 'Segoe UI', Arial, sans-serif; color: #1a1a1a; }}
  h1 {{ font-size: 20px; margin: 0 0 4px; text-align: center; }}
  .meta p {{ margin: 2px 0; font-size: 12px; color: #444; word-break: break-word; }}
  td {{ word-break: break-word; max-width: 320px; }}
  table {{ width: 100%; border-collapse: collapse; margin-top: 12px; font-size: 13px; }}
  th, td {{ padding: 6px 8px; border-bottom: 1px solid #ddd; text-align: left; }}
  th.num, td.num {{ text-align: right; }}
  tfoot td {{ font-weight: bold; border-top: 2px solid #333; }}
  .thanks {{ text-align: center; margin-top: 16px; font-size: 12px; color: #666; }}
</style></head><body>
  <h1>{html.escape(self.shop_name)}</h1>
  <div class="meta">{meta}</div>
  <table>
    <thead><tr><th>Title</th><th class="num">Qty</th><th class="num">Unit</th><th class="num">Total</th></tr></thead>
    <tbody>{rows}</tbody>
    <tfoot><tr><td colspan="3">TOTAL</td><td class="num">{html.escape(sale.total_display)}</td></tr></tfoot>
  </table>
  <p class="thanks">Thank you for your purchase!</p>
</body></html>"""

    # -- Qt-backed output (lazy import) -------------------------------------

    def export_pdf(self, sale: SaleDTO, path: str | Path) -> Path:
        """Render the receipt to a PDF file.

        Uses :class:`QPdfWriter`, which writes PDF directly and does not touch
        the platform print subsystem — so it works reliably headless and on CI.
        """

        from PySide6.QtGui import QPageSize, QPdfWriter, QTextDocument

        path = Path(path)
        writer = QPdfWriter(str(path))
        writer.setPageSize(QPageSize(QPageSize.PageSizeId.A5))
        writer.setResolution(150)
        writer.setTitle(f"Receipt #{sale.id}")

        document = QTextDocument()
        document.setHtml(self.render_html(sale))
        document.print_(writer)
        return path

    def print_receipt(self, sale: SaleDTO, parent=None) -> bool:  # pragma: no cover - needs a printer/UI
        """Show the OS print dialog and print the receipt. Returns True if printed."""

        from PySide6.QtGui import QTextDocument
        from PySide6.QtPrintSupport import QPrintDialog, QPrinter

        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        dialog = QPrintDialog(printer, parent)
        if dialog.exec() != QPrintDialog.DialogCode.Accepted:
            return False
        document = QTextDocument()
        document.setHtml(self.render_html(sale))
        document.print_(printer)
        return True
