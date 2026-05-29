"""Point-of-sale screen: build a cart and complete a sale."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from ...core.money import format_money
from ...services.dto import BookDTO, CartLine, SaleDTO
from ..context import AppContext
from ..viewmodels.sales_viewmodel import SalesViewModel
from ..widgets import (
    Card,
    Column,
    DataTable,
    FormField,
    GhostButton,
    PrimaryButton,
    SecondaryButton,
)
from .base_view import BaseView
from .receipt_dialog import ReceiptDialog

_RIGHT = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter


class CartRow(QFrame):
    qtyChanged = Signal()
    removed = Signal(int)  # book_id

    def __init__(self, book: BookDTO, quantity: int = 1, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.book = book
        self.setObjectName("CardAlt")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(10)

        title = QLabel(book.title)
        title.setWordWrap(True)
        self.spin = QSpinBox()
        self.spin.setRange(1, max(book.stock_qty, 1))
        self.spin.setValue(min(quantity, max(book.stock_qty, 1)))
        self.spin.setAccessibleName(f"Quantity for {book.title}")
        self.line_total = QLabel(format_money(self.current_total()))
        self.line_total.setAlignment(_RIGHT)
        self.line_total.setMinimumWidth(80)
        remove = GhostButton("✕")
        remove.setFixedWidth(34)
        remove.setAccessibleName(f"Remove {book.title}")

        layout.addWidget(title, 1)
        layout.addWidget(self.spin)
        layout.addWidget(self.line_total)
        layout.addWidget(remove)

        self.spin.valueChanged.connect(self._on_qty)
        remove.clicked.connect(lambda: self.removed.emit(book.id))

    def quantity(self) -> int:
        return self.spin.value()

    def current_total(self) -> int:
        return self.book.price_cents * self.spin.value()

    def increment(self) -> None:
        self.spin.setValue(min(self.spin.value() + 1, self.spin.maximum()))

    def _on_qty(self) -> None:
        self.line_total.setText(format_money(self.current_total()))
        self.qtyChanged.emit()


class SellView(BaseView):
    def __init__(self, ctx: AppContext, parent: QWidget | None = None) -> None:
        super().__init__(ctx, parent)
        self.vm = SalesViewModel(ctx, self)
        self._rows: dict[int, CartRow] = {}
        self._build_ui()
        self._connect()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(16)

        title = QLabel("Sell")
        title.setProperty("role", "h1")
        root.addWidget(title)

        body = QHBoxLayout()
        body.setSpacing(16)
        body.addWidget(self._build_catalog(), 3)
        body.addWidget(self._build_order(), 2)
        root.addLayout(body, 1)

    def _build_catalog(self) -> QWidget:
        card = Card()
        heading = QLabel("Catalogue")
        heading.setProperty("role", "h2")
        columns = [
            Column("Title", lambda b: b.title, stretch=True),
            Column(
                "Price", lambda b: b.price_display, align=_RIGHT, sort_key=lambda b: b.price_cents
            ),
            Column("Stock", lambda b: b.stock_qty, align=_RIGHT, sort_key=lambda b: b.stock_qty),
        ]
        self.catalog = DataTable(columns, search_placeholder="Search the catalogue…")
        self.add_button = SecondaryButton("Add to order →")
        self.add_button.setEnabled(False)
        card.body().addWidget(heading)
        card.body().addWidget(self.catalog, 1)
        card.body().addWidget(self.add_button, alignment=Qt.AlignmentFlag.AlignRight)
        return card

    def _build_order(self) -> QWidget:
        card = Card()
        heading = QLabel("Current order")
        heading.setProperty("role", "h2")

        self.cart_area = QScrollArea()
        self.cart_area.setWidgetResizable(True)
        self.cart_area.setFrameShape(QFrame.Shape.NoFrame)
        cart_container = QWidget()
        self.cart_layout = QVBoxLayout(cart_container)
        self.cart_layout.setContentsMargins(0, 0, 0, 0)
        self.cart_layout.setSpacing(8)
        self.empty_hint = QLabel("Your order is empty.\nAdd books from the catalogue.")
        self.empty_hint.setProperty("role", "muted")
        self.empty_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cart_layout.addWidget(self.empty_hint)
        self.cart_layout.addStretch(1)
        self.cart_area.setWidget(cart_container)

        self.customer_name = FormField("Customer name", placeholder="optional")
        self.customer_phone = FormField("Phone", placeholder="optional")

        self.total_label = QLabel(format_money(0))
        self.total_label.setProperty("role", "metric")
        total_row = QHBoxLayout()
        total_caption = QLabel("Total")
        total_caption.setProperty("role", "h2")
        total_row.addWidget(total_caption)
        total_row.addStretch(1)
        total_row.addWidget(self.total_label)

        self.complete_button = PrimaryButton("Complete sale")
        self.complete_button.setEnabled(False)
        self.clear_button = GhostButton("Clear")
        action_row = QHBoxLayout()
        action_row.addWidget(self.clear_button)
        action_row.addStretch(1)
        action_row.addWidget(self.complete_button)

        card.body().addWidget(heading)
        card.body().addWidget(self.cart_area, 1)
        card.body().addWidget(self.customer_name)
        card.body().addWidget(self.customer_phone)
        card.body().addLayout(total_row)
        card.body().addLayout(action_row)
        return card

    def _connect(self) -> None:
        self.catalog.selectionChanged.connect(
            lambda book: self.add_button.setEnabled(book is not None)
        )
        self.catalog.rowActivated.connect(self._add_book)
        self.add_button.clicked.connect(self._add_selected)
        self.clear_button.clicked.connect(self._clear_cart)
        self.complete_button.clicked.connect(self._complete)

        self.vm.booksLoaded.connect(self.catalog.set_rows)
        self.vm.saleCompleted.connect(self._on_sale_completed)
        self.vm.errorOccurred.connect(lambda msg: self.ctx.notify(msg, "error"))
        self.vm.busyChanged.connect(
            lambda busy: self.complete_button.setEnabled(not busy and bool(self._rows))
        )

    def on_show(self) -> None:
        self.vm.load_books()

    # -- Cart management -----------------------------------------------------
    def _add_selected(self) -> None:
        book = self.catalog.current_object()
        if book is not None:
            self._add_book(book)

    def _add_book(self, book: BookDTO) -> None:
        if book.stock_qty <= 0:
            self.ctx.notify(f"“{book.title}” is out of stock.", "error")
            return
        if book.id in self._rows:
            self._rows[book.id].increment()
            return
        row = CartRow(book)
        row.qtyChanged.connect(self._update_total)
        row.removed.connect(self._remove_row)
        self._rows[book.id] = row
        self.cart_layout.insertWidget(self.cart_layout.count() - 2, row)
        self.empty_hint.setVisible(False)
        self._update_total()

    def _remove_row(self, book_id: int) -> None:
        row = self._rows.pop(book_id, None)
        if row is not None:
            row.setParent(None)
            row.deleteLater()
        self.empty_hint.setVisible(not self._rows)
        self._update_total()

    def _clear_cart(self) -> None:
        for book_id in list(self._rows):
            self._remove_row(book_id)

    def _update_total(self) -> None:
        total = sum(row.current_total() for row in self._rows.values())
        self.total_label.setText(format_money(total))
        self.complete_button.setEnabled(bool(self._rows))

    def _complete(self) -> None:
        if not self._rows:
            return
        lines = [CartLine(book_id, row.quantity()) for book_id, row in self._rows.items()]
        name = self.customer_name.text().strip() or None
        phone = self.customer_phone.text().strip() or None
        self.vm.complete_sale(lines, name, phone)

    def _on_sale_completed(self, sale: SaleDTO) -> None:
        self._clear_cart()
        self.customer_name.set_text("")
        self.customer_phone.set_text("")
        self.ctx.notify("Sale completed.", "success")
        self.vm.load_books()  # refresh stock
        self._show_receipt(sale)

    def _show_receipt(self, sale: SaleDTO) -> None:
        ReceiptDialog(sale, self.ctx.services.receipts, self).exec()
