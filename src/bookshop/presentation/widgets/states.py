"""Empty-state and error-state placeholder widgets."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from .buttons import PrimaryButton, SecondaryButton


class _StatePanel(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._layout = QVBoxLayout(self)
        self._layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._layout.setSpacing(8)

        self.icon = QLabel()
        self.icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon.setStyleSheet("font-size: 40px;")
        self.title = QLabel()
        self.title.setProperty("role", "h2")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.subtitle = QLabel()
        self.subtitle.setProperty("role", "muted")
        self.subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.subtitle.setWordWrap(True)

        self._layout.addStretch(1)
        self._layout.addWidget(self.icon)
        self._layout.addWidget(self.title)
        self._layout.addWidget(self.subtitle)


class EmptyState(_StatePanel):
    actionClicked = Signal()

    def __init__(
        self,
        title: str,
        subtitle: str = "",
        *,
        icon: str = "\U0001f4ed",  # 📭
        action_text: str | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.icon.setText(icon)
        self.title.setText(title)
        self.subtitle.setText(subtitle)
        self.setAccessibleName(f"Empty: {title}")
        if action_text:
            self.action = PrimaryButton(action_text)
            self.action.clicked.connect(self.actionClicked.emit)
            self._layout.addSpacing(8)
            self._layout.addWidget(self.action, alignment=Qt.AlignmentFlag.AlignCenter)
        self._layout.addStretch(1)


class ErrorState(_StatePanel):
    retryClicked = Signal()

    def __init__(
        self,
        title: str = "Something went wrong",
        subtitle: str = "",
        *,
        icon: str = "⚠️",  # ⚠️
        retry_text: str = "Try again",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.icon.setText(icon)
        self.title.setText(title)
        self.subtitle.setText(subtitle)
        self.setAccessibleName(f"Error: {title}")
        self.retry = SecondaryButton(retry_text)
        self.retry.clicked.connect(self.retryClicked.emit)
        self._layout.addSpacing(8)
        self._layout.addWidget(self.retry, alignment=Qt.AlignmentFlag.AlignCenter)
        self._layout.addStretch(1)

    def set_message(self, subtitle: str) -> None:
        self.subtitle.setText(subtitle)
