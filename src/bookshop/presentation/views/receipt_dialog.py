"""Receipt preview dialog with print and PDF-export actions."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from ...services.dto import SaleDTO
from ...services.receipt_service import ReceiptService
from ..widgets import PrimaryButton, SecondaryButton


class ReceiptDialog(QDialog):
    def __init__(
        self,
        sale: SaleDTO,
        receipts: ReceiptService,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._sale = sale
        self._receipts = receipts
        self.setWindowTitle(f"Receipt #{sale.id}")
        self.setModal(True)
        self.setMinimumSize(420, 520)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        preview = QTextBrowser()
        preview.setHtml(receipts.render_html(sale))
        layout.addWidget(preview, 1)

        self.status = QLabel("")
        self.status.setProperty("role", "muted")
        layout.addWidget(self.status)

        buttons = QHBoxLayout()
        self.print_button = SecondaryButton("Print…")
        self.pdf_button = SecondaryButton("Save as PDF…")
        self.close_button = PrimaryButton("Done")
        buttons.addStretch(1)
        buttons.addWidget(self.print_button)
        buttons.addWidget(self.pdf_button)
        buttons.addWidget(self.close_button)
        layout.addLayout(buttons)

        self.print_button.clicked.connect(self._print)
        self.pdf_button.clicked.connect(self._save_pdf)
        self.close_button.clicked.connect(self.accept)

    def _print(self) -> None:
        printed = self._receipts.print_receipt(self._sale, self)
        if printed:
            self.status.setText("Sent to printer.")

    def _save_pdf(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self, "Save receipt as PDF", f"receipt_{self._sale.id}.pdf", "PDF files (*.pdf)"
        )
        if not path:
            return
        self._receipts.export_pdf(self._sale, path)
        self.status.setText(f"Saved to {path}")
