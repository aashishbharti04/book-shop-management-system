"""Card container with an optional soft drop shadow."""

from __future__ import annotations

from PySide6.QtGui import QColor
from PySide6.QtWidgets import QFrame, QGraphicsDropShadowEffect, QVBoxLayout, QWidget

from ..theme import tokens as T


class Card(QFrame):
    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        object_name: str = "Card",
        shadow: bool = True,
        padding: int = T.SPACE_LG,
        spacing: int = T.SPACE_MD,
    ) -> None:
        super().__init__(parent)
        self.setObjectName(object_name)
        self._body = QVBoxLayout(self)
        self._body.setContentsMargins(padding, padding, padding, padding)
        self._body.setSpacing(spacing)
        if shadow:
            effect = QGraphicsDropShadowEffect(self)
            effect.setBlurRadius(28)
            effect.setOffset(0, 6)
            effect.setColor(QColor(0, 0, 0, 55))
            self.setGraphicsEffect(effect)

    def body(self) -> QVBoxLayout:
        return self._body

    def add(self, widget: QWidget) -> None:
        self._body.addWidget(widget)
