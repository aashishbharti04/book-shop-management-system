"""View-model for the dashboard screen."""

from __future__ import annotations

from PySide6.QtCore import QObject, Signal

from ...services.dto import DashboardDTO
from ..context import AppContext
from ..errors import humanize_error


class DashboardViewModel(QObject):
    busyChanged = Signal(bool)
    summaryLoaded = Signal(DashboardDTO)
    recentLoaded = Signal(list)  # list[SaleDTO]
    errorOccurred = Signal(str)

    def __init__(self, ctx: AppContext, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._ctx = ctx

    def load(self) -> None:
        self.busyChanged.emit(True)
        self._ctx.runner.run(
            self._ctx.services.analytics.dashboard_summary,
            on_result=self.summaryLoaded.emit,
            on_error=lambda exc: self.errorOccurred.emit(humanize_error(exc)),
            on_finished=lambda: self.busyChanged.emit(False),
        )
        self._ctx.runner.run(
            lambda: self._ctx.services.sales.recent_sales(8),
            on_result=self.recentLoaded.emit,
            on_error=lambda exc: self.errorOccurred.emit(humanize_error(exc)),
        )
