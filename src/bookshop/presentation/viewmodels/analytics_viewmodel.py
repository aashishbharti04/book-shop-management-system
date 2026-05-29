"""View-model for the analytics screen."""

from __future__ import annotations

from PySide6.QtCore import QObject, Signal

from ..context import AppContext
from ..errors import humanize_error


class AnalyticsViewModel(QObject):
    busyChanged = Signal(bool)
    salesLoaded = Signal(list)  # list[BookSalesDTO]
    errorOccurred = Signal(str)

    def __init__(self, ctx: AppContext, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._ctx = ctx

    def load(self, year: int, month: int) -> None:
        self.busyChanged.emit(True)
        self._ctx.runner.run(
            lambda: self._ctx.services.analytics.monthly_sales(year, month),
            on_result=self.salesLoaded.emit,
            on_error=lambda exc: self.errorOccurred.emit(humanize_error(exc)),
            on_finished=lambda: self.busyChanged.emit(False),
        )
