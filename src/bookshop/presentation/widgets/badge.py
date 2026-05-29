"""Small status badge (pill)."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QSizePolicy, QWidget

from .utils import set_property


class Badge(QLabel):
    def __init__(
        self, text: str = "", level: str = "success", parent: QWidget | None = None
    ) -> None:
        super().__init__(text, parent)
        self.setProperty("badge", level)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        if text:
            self.setAccessibleName(f"{text} ({level})")

    def set_level(self, level: str) -> None:
        set_property(self, "badge", level)

    def set_text(self, text: str, level: str | None = None) -> None:
        self.setText(text)
        if level is not None:
            self.set_level(level)
        self.setAccessibleName(f"{text} ({self.property('badge')})")
