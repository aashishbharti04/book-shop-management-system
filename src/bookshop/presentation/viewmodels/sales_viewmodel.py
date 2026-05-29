"""View-model for the point-of-sale (sell) screen."""

from __future__ import annotations

from collections.abc import Sequence

from PySide6.QtCore import QObject, Signal

from ...services.dto import CartLine, SaleDTO
from ..context import AppContext
from ..errors import humanize_error


class SalesViewModel(QObject):
    busyChanged = Signal(bool)
    booksLoaded = Signal(list)  # list[BookDTO]
    saleCompleted = Signal(SaleDTO)
    errorOccurred = Signal(str)

    def __init__(self, ctx: AppContext, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._ctx = ctx

    def load_books(self) -> None:
        self.busyChanged.emit(True)
        self._ctx.runner.run(
            self._ctx.services.inventory.list_books,
            on_result=self.booksLoaded.emit,
            on_error=lambda exc: self.errorOccurred.emit(humanize_error(exc)),
            on_finished=lambda: self.busyChanged.emit(False),
        )

    def complete_sale(
        self,
        lines: Sequence[CartLine],
        customer_name: str | None,
        customer_phone: str | None,
    ) -> None:
        user = self._ctx.current_user
        user_id = user.id if user is not None else None
        self.busyChanged.emit(True)
        self._ctx.runner.run(
            lambda: self._ctx.services.sales.create_sale(
                lines,
                customer_name=customer_name,
                customer_phone=customer_phone,
                user_id=user_id,
            ),
            on_result=self.saleCompleted.emit,
            on_error=lambda exc: self.errorOccurred.emit(humanize_error(exc)),
            on_finished=lambda: self.busyChanged.emit(False),
        )
