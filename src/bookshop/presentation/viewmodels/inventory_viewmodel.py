"""View-model for the inventory screen."""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import QObject, Signal

from ..context import AppContext
from ..errors import humanize_error


class InventoryViewModel(QObject):
    busyChanged = Signal(bool)
    booksLoaded = Signal(list)  # list[BookDTO]
    errorOccurred = Signal(str)
    actionSucceeded = Signal(str)

    def __init__(self, ctx: AppContext, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._ctx = ctx

    def load(self) -> None:
        self.busyChanged.emit(True)
        self._ctx.runner.run(
            self._ctx.services.inventory.list_books,
            on_result=self.booksLoaded.emit,
            on_error=lambda exc: self.errorOccurred.emit(humanize_error(exc)),
            on_finished=lambda: self.busyChanged.emit(False),
        )

    def add_book(self, values: dict[str, Any]) -> None:
        self._ctx.runner.run(
            lambda: self._ctx.services.inventory.add_book(**values),
            on_result=lambda book: self.actionSucceeded.emit(f"Added “{book.title}”."),
            on_error=lambda exc: self.errorOccurred.emit(humanize_error(exc)),
        )

    def update_book(self, book_id: int, values: dict[str, Any]) -> None:
        self._ctx.runner.run(
            lambda: self._ctx.services.inventory.update_book(book_id, **values),
            on_result=lambda book: self.actionSucceeded.emit(f"Updated “{book.title}”."),
            on_error=lambda exc: self.errorOccurred.emit(humanize_error(exc)),
        )

    def restock(self, book_id: int, quantity: int) -> None:
        self._ctx.runner.run(
            lambda: self._ctx.services.inventory.restock(book_id, quantity),
            on_result=lambda book: self.actionSucceeded.emit(
                f"Restocked “{book.title}” (now {book.stock_qty})."
            ),
            on_error=lambda exc: self.errorOccurred.emit(humanize_error(exc)),
        )
