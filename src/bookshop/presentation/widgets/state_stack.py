"""A stacked container that switches between loading/content/empty/error."""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QStackedWidget, QWidget

from .skeleton import SkeletonList
from .states import EmptyState, ErrorState


class StateStack(QStackedWidget):
    """Holds the four canonical view states and exposes simple switchers."""

    retryClicked = Signal()

    def __init__(
        self,
        content: QWidget,
        parent: QWidget | None = None,
        *,
        loading: QWidget | None = None,
        empty: EmptyState | None = None,
        error: ErrorState | None = None,
        skeleton_rows: int = 6,
    ) -> None:
        super().__init__(parent)
        self.content = content
        self.loading = loading or SkeletonList(rows=skeleton_rows)
        self.empty = empty
        self.error = error or ErrorState()
        self.error.retryClicked.connect(self.retryClicked.emit)

        self.addWidget(self.content)
        self.addWidget(self.loading)
        if self.empty is not None:
            self.addWidget(self.empty)
        self.addWidget(self.error)

    def show_content(self) -> None:
        self.setCurrentWidget(self.content)

    def show_loading(self) -> None:
        self.setCurrentWidget(self.loading)

    def show_empty(self) -> None:
        self.setCurrentWidget(self.empty if self.empty is not None else self.content)

    def show_error(self, message: str = "") -> None:
        if message:
            self.error.set_message(message)
        self.setCurrentWidget(self.error)
