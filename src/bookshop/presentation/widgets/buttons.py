"""Themeable button variants with accessible defaults."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QPushButton, QWidget


class _BaseButton(QPushButton):
    def __init__(
        self, text: str = "", parent: QWidget | None = None, *, variant: str = "secondary"
    ) -> None:
        super().__init__(text, parent)
        self.setProperty("variant", variant)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setMinimumHeight(34)
        if text:
            self.setAccessibleName(text)


class PrimaryButton(_BaseButton):
    def __init__(self, text: str = "", parent: QWidget | None = None) -> None:
        super().__init__(text, parent, variant="primary")
        self.setDefault(True)


class SecondaryButton(_BaseButton):
    def __init__(self, text: str = "", parent: QWidget | None = None) -> None:
        super().__init__(text, parent, variant="secondary")


class GhostButton(_BaseButton):
    def __init__(self, text: str = "", parent: QWidget | None = None) -> None:
        super().__init__(text, parent, variant="ghost")


class DangerButton(_BaseButton):
    def __init__(self, text: str = "", parent: QWidget | None = None) -> None:
        super().__init__(text, parent, variant="danger")
