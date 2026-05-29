"""Analytics: monthly sales chart (matplotlib embedded in Qt) and top sellers."""

from __future__ import annotations

import calendar
import os

os.environ.setdefault("QT_API", "pyside6")

import matplotlib

matplotlib.use("QtAgg")

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from ...core.clock import utcnow
from ...services.dto import BookSalesDTO
from ..context import AppContext
from ..theme.tokens import ThemeTokens
from ..viewmodels.analytics_viewmodel import AnalyticsViewModel
from ..widgets import Card, Column, DataTable, EmptyState, StateStack
from .base_view import BaseView

_RIGHT = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter


class SalesChartCanvas(FigureCanvasQTAgg):
    """A matplotlib bar chart embedded as a Qt widget (no separate window)."""

    def __init__(self) -> None:
        self.figure = Figure(figsize=(6, 3.2), tight_layout=True)
        super().__init__(self.figure)
        self.ax = self.figure.add_subplot(111)

    def render_data(self, data: list[BookSalesDTO], tokens: ThemeTokens, title: str) -> None:
        self.ax.clear()
        self.figure.patch.set_facecolor(tokens.surface)
        self.ax.set_facecolor(tokens.surface)

        labels = [d.title for d in data]
        values = [d.quantity for d in data]
        positions = range(len(values))
        self.ax.bar(positions, values, color=tokens.primary, width=0.6)
        self.ax.set_xticks(list(positions))
        self.ax.set_xticklabels(
            [label[:16] for label in labels], rotation=30, ha="right", fontsize=8, color=tokens.text
        )
        self.ax.set_ylabel("Units sold", color=tokens.text)
        self.ax.set_title(title, color=tokens.text, fontsize=11, loc="left")
        self.ax.tick_params(colors=tokens.text_muted)
        for spine in self.ax.spines.values():
            spine.set_color(tokens.border)
        if values:
            self.ax.set_ylim(0, max(values) * 1.2 + 1)
        self.draw_idle()


class AnalyticsView(BaseView):
    def __init__(self, ctx: AppContext, parent: QWidget | None = None) -> None:
        super().__init__(ctx, parent)
        self.vm = AnalyticsViewModel(ctx, self)
        self._last_data: list[BookSalesDTO] = []
        now = utcnow()
        self._build_ui(now.year, now.month)
        self._connect()

    def _build_ui(self, year: int, month: int) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(16)

        header = QHBoxLayout()
        title = QLabel("Analytics")
        title.setProperty("role", "h1")
        self.month_combo = QComboBox()
        for index in range(1, 13):
            self.month_combo.addItem(calendar.month_name[index], index)
        self.month_combo.setCurrentIndex(month - 1)
        self.month_combo.setAccessibleName("Month")
        self.year_spin = QSpinBox()
        self.year_spin.setRange(2000, 2100)
        self.year_spin.setValue(year)
        self.year_spin.setAccessibleName("Year")
        header.addWidget(title)
        header.addStretch(1)
        header.addWidget(QLabel("Period:"))
        header.addWidget(self.month_combo)
        header.addWidget(self.year_spin)
        root.addLayout(header)

        # Content: chart card + top-sellers table.
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(16)

        chart_card = Card()
        self.canvas = SalesChartCanvas()
        chart_card.body().addWidget(self.canvas)
        content_layout.addWidget(chart_card, 3)

        top_heading = QLabel("Top sellers")
        top_heading.setProperty("role", "h2")
        content_layout.addWidget(top_heading)
        columns = [
            Column("Title", lambda d: d.title, stretch=True),
            Column("Units", lambda d: d.quantity, align=_RIGHT, sort_key=lambda d: d.quantity),
            Column("Revenue", lambda d: d.revenue_display, align=_RIGHT,
                   sort_key=lambda d: d.revenue_cents),
        ]
        self.table = DataTable(columns, searchable=False)
        content_layout.addWidget(self.table, 2)

        self.empty = EmptyState(
            "No sales for this period",
            "Try a different month, or record some sales first.",
            icon="📈",
        )
        self.stack = StateStack(content, empty=self.empty, skeleton_rows=5)
        root.addWidget(self.stack, 1)

    def _connect(self) -> None:
        self.month_combo.currentIndexChanged.connect(self._reload)
        self.year_spin.valueChanged.connect(self._reload)
        self.stack.retryClicked.connect(self._reload)
        self.vm.busyChanged.connect(self._on_busy)
        self.vm.salesLoaded.connect(self._on_loaded)
        self.vm.errorOccurred.connect(self.stack.show_error)
        # Connect a bound method (not a lambda) so Qt auto-disconnects this when
        # the view is destroyed, preventing it firing on a deleted widget.
        self.ctx.theme.themeChanged.connect(self._on_theme_changed)

    def on_show(self) -> None:
        self._reload()

    def _selected_period(self) -> tuple[int, int]:
        return self.year_spin.value(), self.month_combo.currentData()

    def _reload(self) -> None:
        year, month = self._selected_period()
        self.vm.load(year, month)

    def _on_busy(self, busy: bool) -> None:
        if busy:
            self.stack.show_loading()

    def _on_loaded(self, data: list[BookSalesDTO]) -> None:
        self._last_data = data
        if not data:
            self.stack.show_empty()
            return
        self.table.set_rows(data)
        self._render_chart()
        self.stack.show_content()

    def _on_theme_changed(self, *_: object) -> None:
        # Only re-style the chart if it's actually on screen — avoids redrawing
        # a hidden analytics view every time the theme is toggled elsewhere.
        if self._last_data and self.isVisible():
            self._render_chart()

    def _render_chart(self) -> None:
        year, month = self._selected_period()
        title = f"{calendar.month_name[month]} {year}"
        self.canvas.render_data(self._last_data, self.ctx.theme.tokens, title)
