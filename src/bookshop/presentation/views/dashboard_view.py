"""Dashboard: KPI cards and recent sales."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGridLayout, QLabel, QVBoxLayout, QWidget

from ...services.dto import DashboardDTO, SaleDTO
from ..context import AppContext
from ..viewmodels.dashboard_viewmodel import DashboardViewModel
from ..widgets import Card, Column, DataTable, EmptyState, StateStack
from .base_view import BaseView

_RIGHT = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter


class _MetricCard(Card):
    def __init__(self, caption: str, parent: QWidget | None = None) -> None:
        super().__init__(parent, padding=18, spacing=4)
        self._caption = QLabel(caption)
        self._caption.setProperty("role", "caption")
        self._value = QLabel("—")
        self._value.setProperty("role", "metric")
        self.body().addWidget(self._caption)
        self.body().addWidget(self._value)

    def set_value(self, text: str) -> None:
        self._value.setText(text)


class DashboardView(BaseView):
    def __init__(self, ctx: AppContext, parent: QWidget | None = None) -> None:
        super().__init__(ctx, parent)
        self.vm = DashboardViewModel(ctx, self)
        self._build_ui()
        self._connect()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(16)

        title = QLabel("Dashboard")
        title.setProperty("role", "h1")
        root.addWidget(title)

        # KPI cards in a responsive grid (3 per row).
        self.cards = {
            "today_revenue": _MetricCard("Revenue today"),
            "today_units": _MetricCard("Units sold today"),
            "month_revenue": _MetricCard("Revenue this month"),
            "titles": _MetricCard("Titles in catalogue"),
            "stock": _MetricCard("Units in stock"),
            "low_stock": _MetricCard("Low-stock titles"),
        }
        grid = QGridLayout()
        grid.setSpacing(16)
        for index, card in enumerate(self.cards.values()):
            grid.addWidget(card, index // 3, index % 3)
        root.addLayout(grid)

        recent_heading = QLabel("Recent sales")
        recent_heading.setProperty("role", "h2")
        root.addWidget(recent_heading)

        columns = [
            Column(
                "Date",
                lambda s: s.created_at.strftime("%Y-%m-%d %H:%M"),
                sort_key=lambda s: s.created_at,
            ),
            Column("Customer", lambda s: s.customer_name or "—", stretch=True),
            Column("Items", lambda s: s.item_count, align=_RIGHT, sort_key=lambda s: s.item_count),
            Column(
                "Total", lambda s: s.total_display, align=_RIGHT, sort_key=lambda s: s.total_cents
            ),
        ]
        self.recent_table = DataTable(columns, searchable=False)
        empty = EmptyState(
            "No sales yet",
            "Completed sales will show up here.",
            icon="🧾",
        )
        self.recent_stack = StateStack(self.recent_table, empty=empty, skeleton_rows=4)
        root.addWidget(self.recent_stack, 1)

    def _connect(self) -> None:
        self.vm.summaryLoaded.connect(self._on_summary)
        self.vm.recentLoaded.connect(self._on_recent)
        self.vm.errorOccurred.connect(self.recent_stack.show_error)
        self.recent_stack.retryClicked.connect(self.vm.load)

    def on_show(self) -> None:
        self.vm.load()

    def _on_summary(self, summary: DashboardDTO) -> None:
        self.cards["today_revenue"].set_value(summary.today_revenue_display)
        self.cards["today_units"].set_value(str(summary.today_units_sold))
        self.cards["month_revenue"].set_value(summary.month_revenue_display)
        self.cards["titles"].set_value(str(summary.total_titles))
        self.cards["stock"].set_value(str(summary.total_stock_units))
        self.cards["low_stock"].set_value(str(summary.low_stock_count))

    def _on_recent(self, sales: list[SaleDTO]) -> None:
        self.recent_table.set_rows(sales)
        if sales:
            self.recent_stack.show_content()
        else:
            self.recent_stack.show_empty()
