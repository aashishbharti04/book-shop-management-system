"""Modal dialog for adding or editing a book."""

from __future__ import annotations

from typing import Any

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from ...core.exceptions import ValidationError
from ...core.money import cents_to_decimal_str, parse_money_to_cents
from ...services.dto import BookDTO
from ..widgets import FormField


class BookFormDialog(QDialog):
    def __init__(self, parent: QWidget | None = None, *, book: BookDTO | None = None) -> None:
        super().__init__(parent)
        self._book = book
        self._values: dict[str, Any] | None = None
        self.setWindowTitle("Edit book" if book else "Add book")
        self.setModal(True)
        self.setMinimumWidth(440)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        self.title_field = FormField("Title", placeholder="Book title")
        self.author_field = FormField("Author", placeholder="Author (optional)")
        self.publisher_field = FormField("Publisher", placeholder="Publisher (optional)")
        self.isbn_field = FormField("ISBN", placeholder="ISBN (optional)")
        self.price_field = FormField("Price", placeholder="e.g. 12.99")
        for field in (
            self.title_field,
            self.author_field,
            self.publisher_field,
            self.isbn_field,
            self.price_field,
        ):
            layout.addWidget(field)

        self.qty_spin = QSpinBox()
        self.qty_spin.setRange(0, 1_000_000)
        self.qty_field = FormField("Initial quantity", widget=self.qty_spin)
        if book is None:
            layout.addWidget(self.qty_field)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        save_button = buttons.button(QDialogButtonBox.StandardButton.Save)
        save_button.setProperty("variant", "primary")
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        if book is not None:
            self._populate(book)

    def _populate(self, book: BookDTO) -> None:
        self.title_field.set_text(book.title)
        self.author_field.set_text(book.author or "")
        self.publisher_field.set_text(book.publisher or "")
        self.isbn_field.set_text(book.isbn or "")
        self.price_field.set_text(cents_to_decimal_str(book.price_cents))

    def _on_accept(self) -> None:
        title = self.title_field.text().strip()
        if not title:
            self.title_field.set_error("Title is required.")
            return
        try:
            price_cents = parse_money_to_cents(self.price_field.text())
        except ValidationError as exc:
            self.price_field.set_error(str(exc))
            return

        values: dict[str, Any] = {
            "title": title,
            "author": self.author_field.text().strip() or None,
            "publisher": self.publisher_field.text().strip() or None,
            "isbn": self.isbn_field.text().strip() or None,
            "price_cents": price_cents,
        }
        if self._book is None:
            values["initial_qty"] = self.qty_spin.value()
        self._values = values
        self.accept()

    def values(self) -> dict[str, Any] | None:
        return self._values
