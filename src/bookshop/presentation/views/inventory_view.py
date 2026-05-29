"""Inventory screen: searchable/sortable book list with add/edit/restock."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from ...core.config import get_settings
from ...services.dto import BookDTO
from ..context import AppContext
from ..viewmodels.inventory_viewmodel import InventoryViewModel
from ..widgets import Column, DataTable, EmptyState, PrimaryButton, SecondaryButton, StateStack
from .base_view import BaseView
from .book_form_dialog import BookFormDialog

_RIGHT = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter


class InventoryView(BaseView):
    def __init__(self, ctx: AppContext, parent: QWidget | None = None) -> None:
        super().__init__(ctx, parent)
        self.vm = InventoryViewModel(ctx, self)
        self._threshold = get_settings().low_stock_threshold
        self._selected: BookDTO | None = None
        self._build_ui()
        self._connect()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(16)

        header = QHBoxLayout()
        title = QLabel("Inventory")
        title.setProperty("role", "h1")
        self.restock_button = SecondaryButton("Restock")
        self.edit_button = SecondaryButton("Edit")
        self.add_button = PrimaryButton("＋  Add book")
        self.restock_button.setEnabled(False)
        self.edit_button.setEnabled(False)
        header.addWidget(title)
        header.addStretch(1)
        header.addWidget(self.restock_button)
        header.addWidget(self.edit_button)
        header.addWidget(self.add_button)

        columns = [
            Column("Title", lambda b: b.title, stretch=True),
            Column("Author", lambda b: b.author or "—"),
            Column("ISBN", lambda b: b.isbn or "—"),
            Column("Price", lambda b: b.price_display, align=_RIGHT, sort_key=lambda b: b.price_cents),
            Column("Stock", lambda b: b.stock_qty, align=_RIGHT, sort_key=lambda b: b.stock_qty),
            Column("Status", lambda b: b.status(self._threshold), sort_key=lambda b: b.stock_qty),
        ]
        self.table = DataTable(columns, search_placeholder="Search by title, author or ISBN…")
        self.empty = EmptyState(
            "No books in your inventory",
            "Add your first book to start tracking stock and sales.",
            icon="📚",
            action_text="＋  Add book",
        )
        self.stack = StateStack(self.table, empty=self.empty)

        root.addLayout(header)
        root.addWidget(self.stack, 1)

    def _connect(self) -> None:
        self.add_button.clicked.connect(self._add)
        self.edit_button.clicked.connect(self._edit_selected)
        self.restock_button.clicked.connect(self._restock_selected)
        self.table.selectionChanged.connect(self._on_selection)
        self.table.rowActivated.connect(self._edit_book)
        self.empty.actionClicked.connect(self._add)
        self.stack.retryClicked.connect(self.vm.load)

        self.vm.busyChanged.connect(self._on_busy)
        self.vm.booksLoaded.connect(self._on_loaded)
        self.vm.errorOccurred.connect(self.stack.show_error)
        self.vm.actionSucceeded.connect(self._on_action_success)

    # -- Lifecycle -----------------------------------------------------------
    def on_show(self) -> None:
        self.vm.load()

    def _on_busy(self, busy: bool) -> None:
        if busy:
            self.stack.show_loading()

    def _on_loaded(self, books: list[BookDTO]) -> None:
        self.table.set_rows(books)
        self._selected = None
        self._update_actions()
        if books:
            self.stack.show_content()
        else:
            self.stack.show_empty()

    def _on_action_success(self, message: str) -> None:
        self.ctx.notify(message, "success")
        self.vm.load()

    # -- Selection -----------------------------------------------------------
    def _on_selection(self, book: BookDTO | None) -> None:
        self._selected = book
        self._update_actions()

    def _update_actions(self) -> None:
        has_selection = self._selected is not None
        self.edit_button.setEnabled(has_selection)
        self.restock_button.setEnabled(has_selection)

    # -- Actions -------------------------------------------------------------
    def _add(self) -> None:
        dialog = BookFormDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            values = dialog.values()
            if values:
                self.vm.add_book(values)

    def _edit_selected(self) -> None:
        if self._selected is not None:
            self._edit_book(self._selected)

    def _edit_book(self, book: BookDTO) -> None:
        dialog = BookFormDialog(self, book=book)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            values = dialog.values()
            if values:
                self.vm.update_book(book.id, values)

    def _restock_selected(self) -> None:
        if self._selected is None:
            return
        quantity, ok = QInputDialog.getInt(
            self,
            "Restock",
            f"Units to add to “{self._selected.title}”:",
            1,
            1,
            1_000_000,
        )
        if ok:
            self.vm.restock(self._selected.id, quantity)
